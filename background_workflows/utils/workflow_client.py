# background_workflows/utils/workflow_client.py

import uuid
import json
from typing import Any, Optional

from background_workflows.constants.app_constants import AppConstants
from background_workflows.storage.tables.i_task_storage import ITaskStore
from background_workflows.storage.schemas.task_entity import TaskEntity
from background_workflows.storage.queue.i_queue_backend import IQueueBackend
from background_workflows.utils.task_logger import logger
from background_workflows.saga.task_creation_saga import TaskCreationSaga, SagaFailure


class WorkflowClient:
    """
    A high-level client that abstracts away the underlying queue and storage mechanics
    to manage background task workflows.

    This client creates tasks and enqueues messages using a SAGA pattern. If the message
    enqueuing fails, the saga will automatically roll back any partially created task
    in the task store.
    """

    def __init__(self, task_store: ITaskStore, queue_backend: IQueueBackend) -> None:
        """
        Initialize the WorkflowClient with a given task store and queue backend.

        :param task_store: An ITaskStore implementation (e.g. AzureTaskStore, SqliteTaskStore)
                           for persisting task data.
        :param queue_backend: An IQueueBackend implementation (e.g. AzureQueueBackend, LocalQueueBackend)
                              for messaging.
        """
        self.task_store: ITaskStore = task_store
        self.queue_backend: IQueueBackend = queue_backend

    def start_activity(
        self,
        activity_type: str,
        resource_id: Optional[str] = None,
        store_mode: Optional[str] = AppConstants.TaskStoreFactory.get_active_store_mode(),
        active_table_name: Optional[str] = AppConstants.TaskStoreFactory.get_active_table_name(),
        finished_table_name: Optional[str] = AppConstants.TaskStoreFactory.get_finished_table_name(),
        database_name: Optional[str] = AppConstants.TaskStoreFactory.get_sqlite_db_path(),
        **kwargs: Any,
    ) -> str:
        """
        Create a new task and enqueue a message using a SAGA pattern.

        This method instantiates a TaskCreationSaga with the given parameters. The saga is
        responsible for ensuring that a task is created in the task store and a corresponding
        message is enqueued. If the saga fails, it automatically cleans up any partially created
        task from the database.

        :param activity_type: A string identifier for the task type.
        :param resource_id: Optional resource (partition) identifier for grouping tasks.
        :param store_mode: The storage mode ("azure" or "sqlite"). Defaults from AppConstants.
        :param active_table_name: The active tasks table name. Defaults from AppConstants.
        :param finished_table_name: The finished tasks table name. Defaults from AppConstants.
        :param database_name: The SQLite database path. Defaults from AppConstants.
        :param kwargs: Additional keyword arguments to include in the task payload.
        :return: The unique row_key of the successfully created task.
        :raises SagaFailure: If the task creation saga fails.
        """
        saga = TaskCreationSaga(
            activity_type=activity_type,
            task_store=self.task_store,
            queue_backend=self.queue_backend,
            resource_id=resource_id,
            store_mode=store_mode,
            active_table_name=active_table_name,
            finished_table_name=finished_table_name,
            database_name=database_name,
            **kwargs
        )

        try:
            row_key = saga.run_saga()
            logger.info(
                f"Started activity '{activity_type}' with row_key={row_key} (SAGA OK)."
            )
            return row_key
        except SagaFailure as ex:
            logger.error(f"SAGA failed for activity '{activity_type}': {ex}")
            raise

    def get_status(self, row_key: str, resource_id: str) -> Optional[str]:
        """
        Retrieve the status of a task.

        :param row_key: The unique row key of the task.
        :param resource_id: The resource (partition) identifier for the task.
        :return: The status of the task (e.g., CREATED, RUNNING, COMPLETED, ERROR) if found; otherwise, None.
        """
        task_entity: Optional[TaskEntity] = self.task_store.get_task(resource_id, row_key)
        return task_entity.Status if task_entity is not None else None

    def get_result(self, row_key: str, resource_id: Optional[str] = None) -> Optional[Any]:
        """
        Retrieve the final result of a completed task.

        This method fetches the TaskEntity from the task store and, if the task is marked as COMPLETED
        with a non-empty output payload, deserializes and returns the JSON result.

        :param row_key: The unique row key of the task.
        :param resource_id: The resource (partition) identifier for the task.
        :return: The deserialized output payload if the task is completed; otherwise, None.
        """
        task_entity: Optional[TaskEntity] = self.task_store.get_task(resource_id, row_key)
        if task_entity is None:
            return None

        if (
            task_entity.Status == AppConstants.TaskStatus.COMPLETED
            and task_entity.OutputPayload
        ):
            return json.loads(task_entity.OutputPayload)
        return None
