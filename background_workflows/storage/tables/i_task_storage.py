# background_workflows/storage/tables/i_task_store.py

from abc import ABC, abstractmethod
from typing import Optional
from background_workflows.storage.schemas.task_entity import TaskEntity


class ITaskStore(ABC):
    """
    Interface for storing and retrieving tasks in an 'active' area,
    and eventually moving them to a 'finished' area.
    """

    @abstractmethod
    def create_if_not_exists(self) -> None:
        """
        Create or ensure the storage is ready (e.g., tables, schema, etc.).

        This method should create the necessary storage structures if they do not exist.
        """
        raise NotImplementedError("create_if_not_exists() must be implemented by subclasses.")

    @abstractmethod
    def get_task(self, resource_id: str, row_key: str) -> Optional[TaskEntity]:
        """
        Fetch a single task from the active store.

        :param resource_id: The partition key associated with the task.
        :param row_key: The unique row identifier for the task.
        :return: A TaskEntity if the task is found; otherwise, None.
        """
        raise NotImplementedError("get_task() must be implemented by subclasses.")

    @abstractmethod
    def upsert_task(self, entity: TaskEntity) -> None:
        """
        Insert or update a task in the active store.

        :param entity: The TaskEntity to insert or update.
        """
        raise NotImplementedError("upsert_task() must be implemented by subclasses.")

    @abstractmethod
    def delete_task(self, resource_id: str, row_key: str) -> None:
        """
        Remove the task from the active store.

        :param resource_id: The partition key of the task.
        :param row_key: The unique identifier of the task.
        """
        raise NotImplementedError("delete_task() must be implemented by subclasses.")

    @abstractmethod
    def move_to_finished(self, entity: TaskEntity) -> None:
        """
        Insert the task entity into the finished store for historical record.

        :param entity: The TaskEntity to move to the finished store.
        """
        raise NotImplementedError("move_to_finished() must be implemented by subclasses.")
