# background_workflows/utils/dynamic_task_creator.py

from typing import Any, Optional, Type
from background_workflows.utils.activity_registry import ActivityRegistry
from background_workflows.storage.tables.i_task_storage import ITaskStore
from background_workflows.tasks.base_task import BaseTask


class DynamicTaskCreator:
    """
    Dynamically looks up the registered task class (via ActivityRegistry)
    and instantiates it with the provided ITaskStore.
    """

    def __init__(self, task_store: ITaskStore) -> None:
        """
        Initialize the DynamicTaskCreator with an ITaskStore.

        :param task_store: An instance of ITaskStore (e.g., AzureTaskStore or SqliteTaskStore)
                           to be injected into task instances.
        """
        self.task_store: ITaskStore = task_store

    def create_task(self, msg: Any) -> Optional[BaseTask]:
        """
        Dynamically creates an instance of the task class corresponding to the provided message.

        The message should have a 'task_type' attribute (or key) that is used to look up the
        corresponding task class in the ActivityRegistry.

        :param msg: A TaskMessage-like object that contains a 'task_type' attribute.
        :return: An instance of the corresponding task class initialized with the task_store,
                 or None if no matching task class is found.
        """
        task_class: Optional[Type[BaseTask]] = ActivityRegistry.get(msg.task_type)
        if not task_class:
            return None
        return task_class(self.task_store)
