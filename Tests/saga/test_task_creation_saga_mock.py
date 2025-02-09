import unittest
from unittest.mock import MagicMock, patch
from background_workflows.saga.task_creation_saga import TaskCreationSaga, SagaFailure
from background_workflows.storage.schemas.task_entity import TaskEntity
from background_workflows.constants.app_constants import AppConstants


class TestTaskCreationSaga( unittest.TestCase ):

    @patch( 'background_workflows.storage.blobs.i_blob_store.IBlobStore' )
    @patch( 'background_workflows.storage.queue.i_queue_backend.IQueueBackend' )
    @patch( 'background_workflows.storage.tables.i_task_storage.ITaskStore' )
    def test_run_saga_successful(self, mock_task_store, mock_queue_backend, mock_blob_store):
        # Mock input parameters
        resource_id = 'test_resource_id'
        activity_type = 'test_activity'
        row_key = 'test_row_key'
        store_mode = 'azure'
        container_name = 'test_container'
        blob_name = 'test_blob'
        blob_content = 'test_blob_content'

        # Setup mock TaskStore behavior
        mock_task_store.upsert_task = MagicMock()
        mock_task_store.get_task = MagicMock( return_value = None )

        # Setup mock BlobStore behavior
        mock_blob_store.upload_blob = MagicMock()
        mock_blob_store.delete_blob = MagicMock()

        # Setup mock QueueBackend behavior
        mock_queue_backend.send_message = MagicMock()

        # Initialize the saga
        saga = TaskCreationSaga(
            activity_type = activity_type,
            task_store = mock_task_store,
            queue_backend = mock_queue_backend,
            blob_store = mock_blob_store,
            resource_id = resource_id,
            store_mode = store_mode,
            active_table_name = AppConstants.TaskStoreFactory.get_active_table_name(),
            finished_table_name = AppConstants.TaskStoreFactory.get_finished_table_name(),
            database_name = AppConstants.TaskStoreFactory.get_sqlite_db_path(),
            container_name = container_name,
            blob_name = blob_name,
            blob_content = blob_content
        )

        # Run saga
        row_key = saga.run_saga()

        # Assertions to ensure the saga behaves as expected
        self.assertIsNotNone( row_key )
        mock_blob_store.upload_blob.assert_called_once_with( container_name, blob_name, blob_content.encode( 'utf-8' ) )
        mock_task_store.upsert_task.assert_called_once()
        mock_queue_backend.send_message.assert_called_once()

    @patch( 'background_workflows.storage.blobs.i_blob_store.IBlobStore' )
    @patch( 'background_workflows.storage.queue.i_queue_backend.IQueueBackend' )
    @patch( 'background_workflows.storage.tables.i_task_storage.ITaskStore' )
    def test_run_saga_failure_due_to_blob_upload(self, mock_task_store, mock_queue_backend, mock_blob_store):
        # Mock input parameters
        resource_id = 'test_resource_id'
        activity_type = 'test_activity'
        store_mode = 'azure'
        container_name = 'test_container'
        blob_name = 'test_blob'
        blob_content = 'test_blob_content'

        # Setup mock TaskStore behavior
        mock_task_store.upsert_task = MagicMock()

        # Setup mock BlobStore behavior to simulate a failure during upload
        mock_blob_store.upload_blob = MagicMock( side_effect = Exception( "Blob upload failed" ) )

        # Setup mock QueueBackend behavior
        mock_queue_backend.send_message = MagicMock()

        # Initialize the saga
        saga = TaskCreationSaga(
            activity_type = activity_type,
            task_store = mock_task_store,
            queue_backend = mock_queue_backend,
            blob_store = mock_blob_store,
            resource_id = resource_id,
            store_mode = store_mode,
            active_table_name = AppConstants.TaskStoreFactory.get_active_table_name(),
            finished_table_name = AppConstants.TaskStoreFactory.get_finished_table_name(),
            database_name = AppConstants.TaskStoreFactory.get_sqlite_db_path(),
            container_name = container_name,
            blob_name = blob_name,
            blob_content = blob_content
        )

        # Run saga and expect a failure due to blob upload error
        with self.assertRaises( SagaFailure ):
            saga.run_saga()

        mock_blob_store.upload_blob.assert_called_once_with( container_name, blob_name, blob_content.encode( 'utf-8' ) )
        mock_task_store.upsert_task.assert_not_called()
        mock_queue_backend.send_message.assert_not_called()

    @patch( 'background_workflows.storage.blobs.i_blob_store.IBlobStore' )
    @patch( 'background_workflows.storage.queue.i_queue_backend.IQueueBackend' )
    @patch( 'background_workflows.storage.tables.i_task_storage.ITaskStore' )
    def test_run_saga_failure_due_to_task_store_upsert(self, mock_task_store, mock_queue_backend, mock_blob_store):
        # Mock input parameters
        resource_id = 'test_resource_id'
        activity_type = 'test_activity'
        store_mode = 'azure'
        container_name = 'test_container'
        blob_name = 'test_blob'
        blob_content = 'test_blob_content'

        # Setup mock TaskStore behavior to simulate failure in upsert
        mock_task_store.upsert_task = MagicMock( side_effect = Exception( "Task upsert failed" ) )

        # Setup mock BlobStore behavior
        mock_blob_store.upload_blob = MagicMock()

        # Setup mock QueueBackend behavior
        mock_queue_backend.send_message = MagicMock()

        # Initialize the saga
        saga = TaskCreationSaga(
            activity_type = activity_type,
            task_store = mock_task_store,
            queue_backend = mock_queue_backend,
            blob_store = mock_blob_store,
            resource_id = resource_id,
            store_mode = store_mode,
            active_table_name = AppConstants.TaskStoreFactory.get_active_table_name(),
            finished_table_name = AppConstants.TaskStoreFactory.get_finished_table_name(),
            database_name = AppConstants.TaskStoreFactory.get_sqlite_db_path(),
            container_name = container_name,
            blob_name = blob_name,
            blob_content = blob_content
        )

        # Run saga and expect a failure due to task store upsert error
        with self.assertRaises( SagaFailure ):
            saga.run_saga()

        mock_blob_store.upload_blob.assert_called_once_with( container_name, blob_name, blob_content.encode( 'utf-8' ) )
        mock_task_store.upsert_task.assert_called_once()
        mock_queue_backend.send_message.assert_not_called()


if __name__ == '__main__':
    unittest.main()
