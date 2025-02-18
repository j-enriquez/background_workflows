import asyncio
import logging
from typing import Any, List

from background_workflows.storage.schemas.task_message import TaskMessage
from background_workflows.utils.dynamic_task_creator import DynamicTaskCreator

logger = logging.getLogger( __name__ )


class MainAsyncController:
    """
    An all-async controller for I/O-bound crawling tasks.

    Features:
      - Single event loop
      - A concurrency semaphore for controlling total tasks in flight
      - Periodic polling of a queue for new messages
      - Execution of tasks as async coroutines
    """

    def __init__(
            self,
            task_store: Any,
            queue_backend: Any,
            max_concurrent_tasks: int = 300,
            poll_interval_secs: float = 3.0,
            cpu_threshold: float = 1.0,  # 1.0 means 100%, effectively no CPU gating
    ) -> None:
        """
        :param task_store: The storage (ITaskStore) for persisting task states if needed.
        :param queue_backend: An async-friendly queue client or a wrapper for synchronous calls.
        :param max_concurrent_tasks: The max number of concurrent tasks allowed at once.
        :param poll_interval_secs: How often we poll the queue in seconds.
        :param cpu_threshold: Optional CPU usage fraction (0.0-1.0). If usage exceeds, we pause polling.
        """
        self.task_store = task_store
        self.queue_backend = queue_backend
        self.max_concurrent_tasks = max_concurrent_tasks
        self.poll_interval_secs = poll_interval_secs
        self.cpu_threshold = cpu_threshold

        # Semaphore to limit concurrency
        self.semaphore = asyncio.Semaphore( self.max_concurrent_tasks )

        # DynamicTaskCreator that knows how to instantiate tasks by type
        self.task_creator = DynamicTaskCreator( self.task_store )

        self._shutdown_flag = False

    async def run(self) -> None:
        """
        Continuously polls the queue for new messages and schedules them as async tasks,
        respecting the concurrency limit and optional CPU threshold.

        This method never returns unless an external condition calls `shutdown()`.
        """
        logger.info( "MainAsyncController starting the main loop." )
        while not self._shutdown_flag:
            # Optionally enforce CPU usage check if desired
            if not await self._check_cpu_usage():
                # If CPU usage is too high, skip this poll cycle
                await asyncio.sleep( 2.0 )
                continue

            # Poll the queue for messages
            msgs = await self._receive_messages_async(
                max_messages = 20,
                visibility_timeout = 60 * 60 * 6
            )

            if not msgs:
                # If no messages, sleep before next poll
                await asyncio.sleep( self.poll_interval_secs )
                continue

            # Process each message
            for raw_msg in msgs:
                # Convert raw_msg to a known format
                tmsg = TaskMessage( raw_msg )
                task_obj = self.task_creator.create_task( tmsg )

                if not task_obj:
                    logger.warning( f"Unknown task_type={tmsg.task_type}; deleting msg." )
                    await self._delete_message_async( raw_msg )
                    continue

                # Schedule the async task to run
                await self._schedule_task( task_obj, tmsg, raw_msg )

            # Short pause before next poll
            await asyncio.sleep( self.poll_interval_secs )

        logger.info( "MainAsyncController main loop exiting (shutdown requested)." )

    async def shutdown(self):
        """
        Signal the controller to stop after finishing current loop iteration.
        """
        logger.info( "Shutdown signal received; stopping main loop." )
        self._shutdown_flag = True

    async def _schedule_task(self, task_obj: Any, tmsg: TaskMessage, raw_msg: Any) -> None:
        """
        Schedule a single message as an async crawling job.
        We use a semaphore to limit concurrency.
        """

        # Create a coroutine that wraps the entire job
        async def job_wrapper():
            async with self.semaphore:
                logger.info( f"Starting async job for row_key={tmsg.row_key}" )
                try:
                    # The assumption: task_obj.execute_single_async(...) is truly async
                    await task_obj.execute_single_async( tmsg )
                    # On success, remove the message from the queue
                    await self._delete_message_async( raw_msg )
                except Exception as ex:
                    logger.exception(
                        f"Exception in async job (row_key={tmsg.row_key}): {ex}"
                    )

        # Spawn a background task to run the job
        asyncio.create_task( job_wrapper() )

    async def _check_cpu_usage(self) -> bool:
        """
        By default, we do a 0.5s sample; if usage > cpu_threshold, we return False.
        With I/O, this might not be critical.
        """
        usage = await self._cpu_percent_async( interval = 0.5 )
        if usage > self.cpu_threshold:
            logger.warning(
                f"CPU usage {usage:.2f} is above threshold {self.cpu_threshold:.2f}."
            )
            return False
        return True

    async def _cpu_percent_async(self, interval: float) -> float:
        """
        Because psutil.cpu_percent is synchronous, we run it in a threadpool
        to avoid blocking the async loop.
        """
        loop = asyncio.get_running_loop()
        import psutil

        def blocking_cpu():
            return psutil.cpu_percent( interval = interval ) / 100.0

        return await loop.run_in_executor( None, blocking_cpu )

    async def _receive_messages_async(self, max_messages: int, visibility_timeout: int) -> List[ Any ]:
        loop = asyncio.get_running_loop()

        def sync_receive():
            return self.queue_backend.receive_messages(
                max_messages = max_messages,
                visibility_timeout = visibility_timeout
            )

        msgs = await loop.run_in_executor( None, sync_receive )
        return msgs or [ ]

    async def _delete_message_async(self, raw_msg: Any) -> None:
        loop = asyncio.get_running_loop()

        def sync_delete():
            self.queue_backend.delete_message( raw_msg )

        await loop.run_in_executor( None, sync_delete )
