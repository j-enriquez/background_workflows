import unittest
import os

from dotenv import load_dotenv

from Tests.tests_suites_helpers.test_helper import TestHelper
from background_workflows.saga.task_creation_saga import TaskCreationSaga, SagaFailure
from background_workflows.storage.schemas.task_entity import TaskEntity
from background_workflows.constants.app_constants import AppConstants
from background_workflows.storage.tables.task_store_factory import TaskStoreFactory
from background_workflows.storage.queue.azure_queue_backend import AzureQueueBackend
from background_workflows.storage.blobs.azure_blob_store import AzureBlobStore
from background_workflows.storage.tables.azure_task_store import AzureTaskStore
from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError


class TestTaskCreationSaga( unittest.TestCase ):

    def setUp(self):
        load_dotenv()
        """
        Set up the test environment by initializing necessary components.
        This test uses Azure services, and the connection strings are expected to be in the environment variables.
        """
        self.resource_id = 'test_resource_id'
        self.activity_type = 'test_activity'
        self.row_key = 'test_row_key'
        self.container_name = 'testcontainer' + TestHelper.generate_guid_for_blob()
        self.blob_name = 'testblob' + TestHelper.generate_guid_for_blob()
        self.blob_content = 'test_blob_content'
        self.store_mode = 'azure'
        self.queue_name = "testqueue" + TestHelper.generate_guid_for_queue()

        # Blob
        self.blob_store = AzureBlobStore( connection_string = AppConstants.TaskStoreFactory.get_azure_storage_connection_string() )
        self.blob_store.create_container_if_not_exists( self.container_name )

        # Queue
        self.queue_backend = AzureQueueBackend( connection_string = AppConstants.TaskStoreFactory.get_azure_storage_connection_string(), queue_name = self.queue_name )
        self.queue_backend.create_queue()

        # Initialize the Task Store using the factory method
        factory = TaskStoreFactory( store_mode = AppConstants.TaskStoreFactory.StoreModes.AZURE,azure_connection_string = AppConstants.TaskStoreFactory.get_azure_storage_connection_string() )
        self.task_store = factory.get_task_store()

    def test_run_saga_successful(self):
        """
        Test that the TaskCreationSaga runs successfully with valid inputs.
        """
        saga = TaskCreationSaga(
            activity_type = self.activity_type,
            task_store = self.task_store,
            queue_backend = self.queue_backend,
            blob_store = self.blob_store,
            resource_id = self.resource_id,
            store_mode = self.store_mode,
            active_table_name = AppConstants.TaskStoreFactory.get_active_table_name(),
            finished_table_name = AppConstants.TaskStoreFactory.get_finished_table_name(),
            database_name = "",
            container_name = self.container_name,
            blob_name = self.blob_name,
            blob_content = self.blob_content
        )

        # Run saga and assert row key is returned
        row_key = saga.run_saga()
        self.assertIsNotNone( row_key )

        # Ensure blob was uploaded and the task was inserted into the store
        downloaded_blob = self.blob_store.download_blob( self.container_name, self.blob_name )
        self.assertEqual( downloaded_blob.decode( 'utf-8' ), self.blob_content )

        task_entity = self.task_store.get_task( self.resource_id, row_key )
        self.assertIsNotNone( task_entity )
        self.assertEqual( task_entity.RowKey, row_key )

    def test_run_saga_failure_due_to_task_store_upsert(self):
        """
        Test that the TaskCreationSaga fails gracefully if task store upsert fails.
        """
        # Simulate failure by introducing an issue in the Azure task store (e.g., corrupt data)
        self.task_store.active_client = None  # Break connection to simulate failure

        saga = TaskCreationSaga(
            activity_type = self.activity_type,
            task_store = self.task_store,
            queue_backend = self.queue_backend,
            blob_store = self.blob_store,
            resource_id = self.resource_id,
            store_mode = self.store_mode,
            active_table_name = AppConstants.TaskStoreFactory.get_active_table_name(),
            finished_table_name = AppConstants.TaskStoreFactory.get_finished_table_name(),
            database_name = "",
            container_name = self.container_name,
            blob_name = self.blob_name,
            blob_content = self.blob_content
        )

        with self.assertRaises( SagaFailure ):
            saga.run_saga()

    def tearDown(self):
        """
        Clean up any resources used in the tests.
        """
        # Remove the blob container and any blobs
        try:
            self.blob_store.delete_blob( self.container_name, self.blob_name )
        except ResourceExistsError:
            pass  # Ignore if the blob doesn't exist
        except ResourceNotFoundError:
            pass


if __name__ == '__main__':
    unittest.main()
