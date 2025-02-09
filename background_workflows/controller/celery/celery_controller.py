# background_workflows/controller/celery/celery_controller.py

from typing import Any
from background_workflows.controller.base_controller import BaseController


class CeleryController(BaseController):
    """
    A controller for Celery-based task execution.

    Since Celery workers automatically consume tasks from the queue,
    this controller does not implement a polling loop.
    """

    def __init__(self, task_store: Any, celery_queue_backend: Any) -> None:
        """
        Initialize the CeleryController.

        :param task_store: An implementation of ITaskStore for persisting tasks.
        :param celery_queue_backend: An IQueueBackend implementation that enqueues tasks directly for Celery.
        """
        super().__init__(task_store, celery_queue_backend)

    def initialize_infrastructure(self) -> None:
        """
        Ensures the task store is created.

        For Celery-based processing, only the task store is needed.
        Queue initialization is managed by the Celery framework.
        """
        self.task_store.create_if_not_exists()

    def run(self) -> None:
        """
        No polling loop is implemented because Celery workers handle task processing automatically.

        This method intentionally does nothing.
        """
        pass

    def run_once(self, max_messages: int = 10) -> None:
        """
        No single-pass execution is required because Celery uses a push-based mechanism.

        :param max_messages: Not applicable for Celery; included for interface compatibility.
        """
        pass
