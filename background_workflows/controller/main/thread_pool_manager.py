# background_workflows/controller/main/thread_pool_manager.py

import psutil
import logging
from concurrent.futures import ThreadPoolExecutor, Future
from typing import List, Any
from background_workflows.constants.app_constants import AppConstants

logger = logging.getLogger(__name__)

class ThreadPoolManager:
    """
    Manages a pool of worker threads for executing tasks using a ThreadPoolExecutor.

    Features:
      - Monitors CPU usage via `get_cpu_usage()`.
      - Tracks the number of active (non-completed) tasks.
      - Submits tasks to a ThreadPoolExecutor instead of manually managing threads.
    """

    def __init__(self, max_threads: int = AppConstants.ThreadPoolManager.DEFAULT_MAX) -> None:
        """
        Initialize the ThreadPoolManager.

        :param max_threads: Maximum number of worker threads allowed.
        """
        self.max_threads: int = max_threads
        self.executor: ThreadPoolExecutor = ThreadPoolExecutor(max_workers=max_threads)
        self.futures: List[Future[Any]] = []

    def get_cpu_usage(self) -> float:
        """
        Returns the current CPU usage as a fraction between 0.0 and 1.0.

        Uses psutil.cpu_percent() with a one-second interval. Note that using interval=1
        will block for one second to measure CPU usage.

        :return: CPU usage fraction (e.g., 0.25 for 25% usage).
        """
        return psutil.cpu_percent(interval=1) / 100.0

    def current_thread_count(self) -> int:
        """
        Returns the current number of active (non-completed) futures.

        Cleans up the list of futures by filtering out completed tasks.

        :return: The number of active tasks.
        """
        self.futures = [f for f in self.futures if not f.done()]
        return len(self.futures)

    def submit_task(self, task_obj: Any, msg: Any, raw_msg: Any, queue_backend: Any) -> None:
        """
        Submits a task to the ThreadPoolExecutor.

        :param task_obj: The task object (must implement an `execute_single` method).
        :param msg: The parsed message to be processed.
        :param raw_msg: The original message object (used for deletion upon successful execution).
        :param queue_backend: The queue backend to interact with (e.g., for deleting or updating the message).
        """
        future: Future[Any] = self.executor.submit(self._task_runner, task_obj, msg, raw_msg, queue_backend)
        self.futures.append(future)

    def _task_runner(self, task_obj: Any, msg: Any, raw_msg: Any, queue_backend: Any) -> None:
        """
        Internal runner method that executes a single task and handles post-execution operations.

        If the task executes successfully, it deletes the message from the queue.
        Any exceptions are logged appropriately.

        :param task_obj: The task object.
        :param msg: The parsed message.
        :param raw_msg: The original message object.
        :param queue_backend: The queue backend used for message deletion or update.
        """
        try:
            logger.info("Task execution started.")
            task_obj.execute_single(msg)
            queue_backend.delete_message(raw_msg)
        except Exception as ex:
            logger.exception(f"Error in task execution: {ex}")

    def shutdown(self, wait: bool = True) -> None:
        """
        Shuts down the ThreadPoolExecutor, optionally waiting for running tasks to complete.

        :param wait: If True, block until all pending tasks are complete.
        """
        self.executor.shutdown(wait=wait)
