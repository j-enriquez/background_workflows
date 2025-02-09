import json
import uuid
from typing import Optional, Any, Dict

from background_workflows.constants.app_constants import AppConstants
from background_workflows.storage.blobs.i_blob_store import IBlobStore
from background_workflows.storage.queue.i_queue_backend import IQueueBackend
from background_workflows.storage.tables.i_task_storage import ITaskStore
from background_workflows.storage.schemas.task_entity import TaskEntity
from background_workflows.storage.schemas.task_message import TaskMessage
from background_workflows.utils.task_logger import logger


class SagaFailure(Exception):
    """
    Custom exception to indicate a SAGA step failure.
    """
    pass


class TaskCreationSaga:
    """
    SAGA for creating a new task entity and sending it to the queue.

    Steps:
      1) Upload a blob to Azure Blob Storage.
      2) Prepare a new TaskEntity (CREATED).
      3) Insert/Upsert it in the DB (active store).
      4) Enqueue the message in the queue backend.
      5) If any step fails, revert or mark the DB record so we don't have 'orphan' tasks.
      6) If the blob was created, delete it in case of failure.
    """

    def __init__(
        self,
        activity_type: str,
        task_store: ITaskStore,
        queue_backend: IQueueBackend,
        blob_store: IBlobStore,
        resource_id: Optional[str],
        store_mode: Optional[str],
        active_table_name: Optional[str],
        finished_table_name: Optional[str],
        database_name: Optional[str],
        container_name: Optional[str] = None,
        blob_name: Optional[str] = None,
        blob_content: Optional[str] = None,
        **kwargs: Any,
    ):
        self.activity_type = activity_type
        self.task_store = task_store
        self.queue_backend = queue_backend
        self.blob_store = blob_store
        self.resource_id = resource_id
        self.store_mode = store_mode
        self.active_table_name = active_table_name
        self.finished_table_name = finished_table_name
        self.database_name = database_name
        self.container_name = container_name
        self.blob_name = blob_name
        self.blob_content = blob_content
        self.kwargs = kwargs

        # Generate a unique RowKey for the new task
        self.row_key: str = str(uuid.uuid4())

        # Prepare the new TaskEntity with basic fields
        self.entity = TaskEntity(
            PartitionKey=self.resource_id,
            RowKey=self.row_key,
            TaskType=self.activity_type,
            InputPayload=json.dumps(kwargs),
            OutputPayload="",
            Status=AppConstants.TaskStatus.CREATED,
            ContainerName = self.container_name,
            BlobName = self.blob_name
        )

    def run_saga(self) -> str:
        """
        Orchestrates the entire creation + enqueue steps.
        Returns the row_key if successful, or raises SagaFailure on error.
        """

        # Step 1: Upload the blob if container and blob names are provided
        if self.container_name and self.blob_name and self.blob_content:
            try:
                self.blob_store.upload_blob(self.container_name, self.blob_name, self.blob_content.encode('utf-8'))
                logger.info(f"[TaskCreationSaga] Blob {self.blob_name} uploaded to container {self.container_name}.")
            except Exception as ex:
                logger.error(f"[TaskCreationSaga] Failed to upload blob: {ex}")
                raise SagaFailure(f"Failed to upload blob: {ex}")

        # Step 2: Upsert the task entity into the store
        try:
            self._step_upsert_task()
        except Exception as ex:
            self._delete_blob_if_exists()
            raise SagaFailure( f"Failed to upsert row: {ex}" ) from ex

        # Step 3: Enqueue the task message
        try:
            self._step_enqueue_message()
        except Exception as ex:
            logger.error(f"[TaskCreationSaga] Step 3 failed => {ex}")
            # Step 3 Failure: Compensation
            self._compensate_upsert_task_failure()
            self._delete_blob_if_exists()
            raise SagaFailure(f"Failed to enqueue task message: {ex}") from ex

        logger.info(f"[TaskCreationSaga] Completed successfully (row_key={self.row_key}).")
        return self.row_key

    def _step_upsert_task(self) -> None:
        """
        Insert (or update) the task record in the 'active' store.
        """
        logger.debug(f"[TaskCreationSaga] Upserting TaskEntity with RowKey={self.row_key}")
        self.task_store.upsert_task(self.entity)

    def _step_enqueue_message(self) -> None:
        """
        Build the task message and send it to the queue.
        If this fails, we do a compensation in _compensate_upsert_task_failure.
        """
        message_data = {
            AppConstants.MessageKeys.RESOURCE_ID: self.resource_id,
            AppConstants.MessageKeys.ROW_KEY: self.row_key,
            AppConstants.MessageKeys.TASK_TYPE: self.activity_type,
            AppConstants.MessageKeys.PAYLOAD: self.kwargs,
            AppConstants.MessageKeys.STORE_MODE: self.store_mode,
            AppConstants.MessageKeys.ACTIVE_TABLE_NAME: self.active_table_name,
            AppConstants.MessageKeys.FINISHED_TABLE_NAME: self.finished_table_name,
            AppConstants.MessageKeys.DATABASE_NAME: self.database_name,
        }
        wrapped_for_schema = {
            AppConstants.MessageKeys.CONTENT: json.dumps(message_data)
        }
        task_message = TaskMessage(wrapped_for_schema)

        logger.debug(f"[TaskCreationSaga] Enqueuing message for RowKey={self.row_key}")
        # If this raises an exception, it is caught in run_saga
        self.queue_backend.send_message(task_message.to_json())

    def _compensate_upsert_task_failure(self) -> None:
        """
        Compensation logic: If the queue step fails, we remove or mark the DB record
        so that we don't leave an orphaned task that will never be executed.
        Here we do a simple deletion. Alternatively, you could set status=ERROR or something else.
        """
        logger.warning(f"[TaskCreationSaga] Compensation => Deleting the partially created task {self.row_key}")
        try:
            self.task_store.delete_task(self.resource_id or "", self.row_key)
        except Exception as ex:
            logger.error(f"[TaskCreationSaga] Compensation failed => {ex}")
            # For a real system, you might log/alert if compensation also fails.

    def _delete_blob_if_exists(self) -> None:
        """
        Deletes the blob from the Azure Blob Storage if it was created.
        """
        if self.container_name and self.blob_name:
            try:
                logger.info(f"[TaskCreationSaga] Deleting blob {self.blob_name} in container {self.container_name}.")
                self.blob_store.delete_blob(self.container_name, self.blob_name)
            except Exception as ex:
                logger.error(f"[TaskCreationSaga] Failed to delete blob {self.blob_name}: {ex}")
