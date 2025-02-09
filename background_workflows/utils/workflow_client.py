from typing import Optional, Any
from background_workflows.storage.blobs.i_blob_store import IBlobStore
from background_workflows.saga.task_creation_saga import TaskCreationSaga, SagaFailure
from background_workflows.constants.app_constants import AppConstants
import json

from background_workflows.storage.queue.i_queue_backend import IQueueBackend
from background_workflows.storage.schemas.task_entity import TaskEntity
from background_workflows.storage.tables.i_task_storage import ITaskStore
from background_workflows.utils.task_logger import logger


class WorkflowClient:
    """
    A high-level client that abstracts away the underlying queue and storage mechanics
    to manage background task workflows.
    """

    def __init__(self, task_store: ITaskStore, queue_backend: IQueueBackend, blob_store: IBlobStore) -> None:
        """
        Initialize the WorkflowClient with a given task store, queue backend, and blob storage instance.

        :param task_store: An ITaskStore implementation (e.g. AzureTaskStore, SqliteTaskStore) for persisting task data.
        :param queue_backend: An IQueueBackend implementation (e.g. AzureQueueBackend, LocalQueueBackend) for messaging.
        :param blob_store: An IBlobStore implementation (e.g. AzureBlobStore, LocalBlobStore) for blob storage operations.
        """
        self.task_store: ITaskStore = task_store
        self.queue_backend: IQueueBackend = queue_backend
        self.blob_store: IBlobStore = blob_store

    def start_activity(
        self,
        activity_type: str,
        resource_id: Optional[str] = None,
        store_mode: Optional[str] = AppConstants.TaskStoreFactory.get_active_store_mode(),
        active_table_name: Optional[str] = AppConstants.TaskStoreFactory.get_active_table_name(),
        finished_table_name: Optional[str] = AppConstants.TaskStoreFactory.get_finished_table_name(),
        database_name: Optional[str] = AppConstants.TaskStoreFactory.get_sqlite_db_path(),
        container_name: Optional[str] = None,
        blob_name: Optional[str] = None,
        blob_content: Optional[str] = None,  # Added blob_content parameter
        **kwargs: Any,
    ) -> str:
        """
        Create a new task and enqueue a message using a SAGA pattern, where blob handling (upload and delete) is included.
        If the SAGA fails, the blob will be deleted but the container will remain intact.

        :param activity_type: A string identifier for the task type.
        :param resource_id: Optional resource (partition) identifier for grouping tasks.
        :param store_mode: The storage mode ("azure" or "sqlite"). Defaults from AppConstants.
        :param active_table_name: The active tasks table name. Defaults from AppConstants.
        :param finished_table_name: The finished tasks table name. Defaults from AppConstants.
        :param database_name: The SQLite database path. Defaults from AppConstants.
        :param container_name: The Azure Blob container name.
        :param blob_name: The name of the blob to upload.
        :param blob_content: The content to be uploaded as a blob.
        :param kwargs: Additional keyword arguments to include in the task payload.
        :return: The unique row_key of the successfully created task.
        :raises SagaFailure: If the task creation saga fails.
        """
        # Initialize the TaskCreationSaga and pass the blob store, task store, and queue backend
        saga = TaskCreationSaga(
            activity_type=activity_type,
            task_store=self.task_store,
            queue_backend=self.queue_backend,
            blob_store=self.blob_store,
            resource_id=resource_id,
            store_mode=store_mode,
            active_table_name=active_table_name,
            finished_table_name=finished_table_name,
            database_name=database_name,
            container_name=container_name,
            blob_name=blob_name,
            blob_content=blob_content,  # Pass the blob content here
            **kwargs
        )

        try:
            row_key = saga.run_saga()
            logger.info(f"Started activity '{activity_type}' with row_key={row_key} (SAGA OK).")
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