# background_workflows/controller/base_controller.py

import abc
from typing import Any


class BaseController( abc.ABC ):
    """
    A base class for all controllers. Subclasses must implement
    the run() and run_once() methods.
    """

    def __init__(self, task_store: Any, queue_backend: Any) -> None:
        """
        Initialize the controller.

        :param task_store: An ITaskStore implementation (e.g., AzureTaskStore, SqliteTaskStore).
        :param queue_backend: An IQueueBackend implementation (e.g., AzureQueueBackend, LocalQueueBackend, CeleryQueueBackend).
        """
        self.task_store: Any = task_store
        self.queue_backend: Any = queue_backend

    def initialize_infrastructure(self) -> None:
        """
        Creates or verifies any underlying tables, queues, or containers.

        This method can be overridden if additional initialization logic is needed.
        """
        self.task_store.create_if_not_exists()
        self.queue_backend.create_queue()

    @abc.abstractmethod
    def run(self) -> None:
        """
        Run the controller indefinitely or as required.

        Subclasses must implement this method.

        :raises NotImplementedError: Always, unless overridden.
        """
        raise NotImplementedError( "Subclasses must implement run()" )

    @abc.abstractmethod
    def run_once(self, max_messages: int = 10) -> None:
        """
        Process a single pass of tasks.

        This method is useful for testing or ad-hoc execution.

        :param max_messages: Maximum number of messages to process during this pass.
        :raises NotImplementedError: Always, unless overridden.
        """
        raise NotImplementedError( "Subclasses must implement run_once()" )
