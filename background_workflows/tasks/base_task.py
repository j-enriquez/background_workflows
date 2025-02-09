# background_workflows/tasks/base_task.py

import abc
import socket
import time
import logging
from datetime import datetime
from typing import Optional, Dict

from background_workflows.storage.tables.i_task_storage import ITaskStore
from background_workflows.storage.schemas.task_entity import TaskEntity

logger = logging.getLogger(__name__)


class BaseTask(abc.ABC):
    """
    Abstract base class for tasks providing common functionality for:
      - Single-message processing.
      - Updating task status (marking as running, completed, or error).
    """

    def __init__(self, task_store: ITaskStore) -> None:
        """
        Initialize the BaseTask.

        :param task_store: An ITaskStore implementation for reading/writing task entities.
        """
        self.task_store: ITaskStore = task_store
        # Mapping from "resource_id||row_key" to the corresponding TaskEntity
        self._active_items: Dict[str, TaskEntity] = {}

    def _initialize_single(self, resource_id: str, row_key: str) -> Optional[TaskEntity]:
        """
        Loads the TaskEntity, marks it as RUNNING, sets its start time,
        and caches it for further processing.

        :param resource_id: The resource identifier (PartitionKey).
        :param row_key: The unique task identifier (RowKey).
        :return: The updated TaskEntity if found; otherwise, None.
        """
        if not resource_id or not row_key:
            logger.error("[BaseTask] _initialize_single => Missing IDs in message.")
            return None

        # Retrieve the task from the store.
        task_entity: Optional[TaskEntity] = self.task_store.get_task(resource_id, row_key)
        if not task_entity:
            logger.error(f"[BaseTask] _initialize_single => No such task in store: {resource_id}/{row_key}")
            return None

        # Mark the task as running and update its start time.
        task_entity.mark_running()
        task_entity.StartTime = datetime.utcnow()
        self.task_store.upsert_task(task_entity)

        # Cache the task using a unique key composed of resource_id and row_key.
        unique_key: str = f"{resource_id}||{row_key}"
        self._active_items[unique_key] = task_entity
        return task_entity

    def _complete_single(self, unique_key: str, input_task_entity: Optional[TaskEntity] = None) -> None:
        """
        Marks the task as COMPLETED, sets its end time, moves it to the finished store,
        and removes it from the active cache.

        :param unique_key: The unique key in the format "resource_id||row_key".
        :param input_task_entity: Optionally, a TaskEntity to complete directly; if not provided,
                                  the cached task is used.
        """
        task_entity: Optional[TaskEntity] = input_task_entity or self._active_items.get(unique_key)
        if task_entity:
            task_entity.mark_completed()
            task_entity.EndTime = datetime.utcnow()
            self.task_store.upsert_task(task_entity)

            # Move the task to the finished store and remove it from active storage.
            self.task_store.move_to_finished(task_entity)
            self.task_store.delete_task(task_entity.ResourceId, task_entity.RowKey)
            self._active_items.pop(unique_key, None)

    def _fail_single(self, unique_key: str, error_message: str) -> None:
        """
        Marks the task as ERROR, sets its end time and error message, moves it to the finished store,
        and removes it from the active cache.

        :param unique_key: The unique key in the format "resource_id||row_key".
        :param error_message: The error message describing the failure.
        """
        task_entity: Optional[TaskEntity] = self._active_items.get(unique_key)
        if task_entity:
            task_entity.mark_error()
            task_entity.EndTime = datetime.utcnow()
            task_entity.ErrorMessage = error_message
            self.task_store.upsert_task(task_entity)

            # Move the task to the finished store and remove it from active storage.
            self.task_store.move_to_finished(task_entity)
            self.task_store.delete_task(task_entity.ResourceId, task_entity.RowKey)
            self._active_items.pop(unique_key, None)

    def _generate_batch_id(self) -> str:
        """
        Generates a unique batch ID using the hostname and the current timestamp.

        :return: A unique batch identifier string.
        """
        hostname: str = socket.gethostname()
        epoch: float = time.time()
        return f"{hostname}-{epoch:.6f}"
