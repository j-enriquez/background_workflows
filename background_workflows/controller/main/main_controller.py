# backgorund_workflows/controller/main/main_controller.py

import time
import logging
from typing import Any

from background_workflows.constants.app_constants import AppConstants
from background_workflows.controller.base_controller import BaseController
from background_workflows.controller.main.thread_pool_manager import ThreadPoolManager
from background_workflows.storage.schemas.task_message import TaskMessage
from background_workflows.utils.dynamic_task_creator import DynamicTaskCreator

logger = logging.getLogger(__name__)


class MainController(BaseController):
    """
    MainController orchestrates task processing by:
      - Polling messages from an IQueueBackend.
      - Delegating tasks to a ThreadPoolManager.
      - Instantiating the proper task via DynamicTaskCreator.

    It continuously monitors system CPU usage and dispatches tasks when safe.
    """

    def __init__(
        self,
        task_store: Any,
        queue_backend: Any,
        max_threads: int = AppConstants.MainController.DEFAULT_MAX_THREADS,
        cpu_threshold: float = AppConstants.MainController.DEFAULT_CPU_THRESHOLD,
    ) -> None:
        """
        Initialize the MainController with a task store, queue backend, and resource limits.

        :param task_store: An instance of ITaskStore for persisting task state.
        :param queue_backend: An instance of IQueueBackend for message operations.
        :param max_threads: Maximum number of concurrent worker tasks.
        :param cpu_threshold: Maximum CPU usage (as a fraction) at which new tasks are scheduled.
        """
        super().__init__(task_store, queue_backend)
        self.max_threads: int = max_threads
        self.cpu_threshold: float = cpu_threshold

        self.thread_pool: ThreadPoolManager = ThreadPoolManager(max_threads)
        self.task_creator: DynamicTaskCreator = DynamicTaskCreator(self.task_store)

    def run(self) -> None:
        """
        Continuously poll the queue and dispatch tasks when system resources allow.

        The loop performs the following steps:
          1. Wait until CPU usage is below the defined threshold.
          2. Poll the queue for messages.
          3. Dispatch each message to the thread pool for execution.
        """
        logger.info("MainController run loop started.")
        while True:
            self._wait_for_safe_cpu()
            self._poll_and_handle_messages(self.queue_backend)
            time.sleep(AppConstants.MainController.MAIN_LOOP_SLEEP_SECS)

    def run_once(self, max_messages: int = AppConstants.MainController.RUN_ONCE_MAX_MESSAGES_DEFAULT) -> None:
        """
        Executes a single pass to poll and dispatch tasks.

        Useful for testing or ad-hoc runs.

        :param max_messages: Maximum number of messages to process in this pass.
        """
        logger.info("MainController single-pass started.")
        self._wait_for_safe_cpu()
        self._poll_and_handle_messages(self.queue_backend, max_messages=max_messages)

    def _wait_for_safe_cpu(self) -> None:
        """
        Wait until the current CPU usage falls below the defined threshold.
        """
        while True:
            usage: float = self.thread_pool.get_cpu_usage()
            if usage < self.cpu_threshold:
                break
            logger.warning(
                f"CPU usage {usage:.2f} >= threshold {self.cpu_threshold:.2f}, sleeping."
            )
            time.sleep(AppConstants.MainController.MAIN_LOOP_CPU_RECHECK_SECS)

    def _poll_and_handle_messages(
        self, queue_backend: Any, max_messages: int = AppConstants.MainController.POLL_AND_HANDLE_DEFAULT_MESSAGES
    ) -> None:
        """
        Poll the queue for messages and dispatch each to the worker pool.

        :param queue_backend: The queue backend from which to receive messages.
        :param max_messages: Maximum number of messages to fetch from the queue.
        """
        msgs = queue_backend.receive_messages(
            max_messages=max_messages,
            visibility_timeout=AppConstants.MainController.DEFAULT_VISIBILITY_TIMEOUT,
        )
        if not msgs:
            return

        for raw_msg in msgs:
            self._handle_single(raw_msg, queue_backend)

    def _handle_single(self, raw_msg: Any, queue_backend: Any) -> None:
        """
        Handle a single queued message: parse the message, create the corresponding task,
        and submit the task for execution if resource constraints allow.

        :param raw_msg: The raw message from the queue.
        :param queue_backend: The queue backend for updating or deleting messages.
        """
        # Parse the message into a TaskMessage object
        tmsg = TaskMessage(raw_msg)
        task_obj = self.task_creator.create_task(tmsg)
        if not task_obj:
            logger.warning(f"Unknown task_type={tmsg.task_type}, removing message.")
            queue_backend.delete_message(raw_msg)
            return

        # Check current CPU usage and thread pool load
        cpu_usage: float = self.thread_pool.get_cpu_usage()
        active_count: int = self.thread_pool.current_thread_count()

        if cpu_usage < self.cpu_threshold and active_count < self.max_threads:
            logger.info(
                f"Scheduling task {tmsg.task_type} for resource_id={tmsg.resource_id}, row_key={tmsg.row_key}"
            )
            self.thread_pool.submit_task(task_obj, tmsg, raw_msg, queue_backend)
        else:
            # Defer processing if resources are limited
            queue_backend.update_message(
                raw_msg,
                visibility_timeout=AppConstants.MainController.VISIBILITY_TIMEOUT_FOR_DEFER,
            )
            logger.info(f"Deferring task; high CPU/threads for row_key={tmsg.row_key}")
