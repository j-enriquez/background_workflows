import os
import shutil
import time
import unittest
from typing import Any, Optional

from Tests.sample_tasks.multiply_x_by_2 import MultiplyXBy2
from Tests.tests_suites_helpers.test_helper import TestHelper
from background_workflows.controller.main.main_controller import MainController
from background_workflows.storage.queue.local_queue_backend import LocalQueueBackend
from background_workflows.storage.tables.sqlite_task_store import SqliteTaskStore
from background_workflows.utils.workflow_client import WorkflowClient
from background_workflows.storage.blobs.local_blob_store import LocalBlobStore

# Ensure that the MultiplyXBy2 class is registered (side-effect of import)
MultiplyXBy2


class TestCompleteSingleTask(unittest.TestCase):
    def setUp(self) -> None:
        """
        Set up the test environment for a complete single task execution.

        This includes:
          - Creating a temporary SQLite database.
          - Initializing the task store and local queue backend.
          - Creating the required tables.
          - Setting up a MainController and a WorkflowClient.
        """
        # Generate a unique SQLite database path.
        self.db_path: str = f"test_tasks_{TestHelper.generate_guid_for_local_db()}.db"

        # Initialize the SQLite task store.
        self.task_store: SqliteTaskStore = SqliteTaskStore(db_path=self.db_path)
        self.task_store.create_if_not_exists()

        # Initialize the local in-memory queue backend.
        self.queue_backend: LocalQueueBackend = LocalQueueBackend()

        # Initialize a local Blob Store for the test.
        self.unique_root = f"test_blobs_e2e_single_queue_{TestHelper.generate_guid_for_blob()}"
        self.blob_store = LocalBlobStore(root_dir=self.unique_root)

        # Initialize the MainController with a single thread and high CPU threshold to allow task execution.
        self.controller: MainController = MainController(
            task_store=self.task_store,
            queue_backend=self.queue_backend,
            max_threads=1,
            cpu_threshold=0.99,
        )
        self.controller.initialize_infrastructure()

        # Create the WorkflowClient to abstract the task start and query operations.
        self.client: WorkflowClient = WorkflowClient(
            self.task_store, self.queue_backend, self.blob_store
        )

    def tearDown(self) -> None:
        """
        Clean up the test environment by closing the task store connection and
        removing the temporary SQLite database file.
        """
        self.task_store.close()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

        if os.path.exists( self.unique_root ):
            try:
                # Remove directory and all its contents
                shutil.rmtree( self.unique_root )
                print( f"Successfully deleted {self.unique_root}" )
            except Exception as e:
                print( f"Failed to delete {self.unique_root}: {e}" )

    def test_sample_task_sync(self) -> None:
        """
        Test the synchronous execution of a sample task.

        The test performs the following steps:
          1. Enqueues a task with activity type "MULTIPLY_X_BY_2" and input parameters.
          2. Runs a single pass of the controller to process the queued message.
          3. Verifies that the task status is updated to COMPLETED.
          4. Retrieves and validates the task result, ensuring that 'x' has been doubled
             and that the echoed message is correct.
        """
        # 1) Enqueue a task of type "MULTIPLY_X_BY_2".
        job_id: str = self.client.start_activity(
            activity_type="MULTIPLY_X_BY_2",
            resource_id="TestCustomer",
            x=10,
            y="hello test",
            container_name="test_container",  # Add blob container
            blob_name="test_blob",  # Add blob name
            blob_content="This is the blob content",  # Add blob content
        )

        # 2) Run the controller in a single pass to process tasks.
        self.controller.run_once()
        time.sleep(5)  # Allow some time for task processing.

        # 3) Check the status of the task.
        status: Optional[str] = self.client.get_status(job_id, "TestCustomer")
        self.assertEqual(
            status,
            "COMPLETED",
            f"Task should be COMPLETED but is {status}"
        )

        # 4) Retrieve and validate the output result.
        result: Optional[Any] = self.client.get_result(job_id, resource_id="TestCustomer")
        self.assertIsNotNone(result, "Result should not be None after task completion.")
        self.assertIn("answer", result, "Result should contain the key 'answer'.")
        self.assertEqual(result["answer"], 20, "Expected answer to be 20 (2 * 10).")
        self.assertIn("details", result, "Result should contain the key 'details'.")
        self.assertIn("hello test", result["details"], "Result details should echo 'hello test'.")

        # Validate that container_name and blob_name are part of the result
        self.assertEqual(result["ContainerName"], "test_container", "Expected 'ContainerName' to be 'test_container'.")
        self.assertEqual(result["BlobName"], "test_blob", "Expected 'BlobName' to be 'test_blob'.")
