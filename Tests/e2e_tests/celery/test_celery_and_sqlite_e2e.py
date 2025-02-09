import os
import shutil
import time
import unittest
from typing import Any, Optional

from dotenv import load_dotenv

# Celery testing tools
from celery.contrib.testing.worker import start_worker
from celery import Celery
from celery.contrib.testing.tasks import ping
from unittest.mock import patch

from Tests.sample_tasks.sample_task import SampleTask
from Tests.tests_suites_helpers.test_helper import TestHelper
from background_workflows.constants.app_constants import AppConstants
from background_workflows.storage.queue.celery_queue_backend import CeleryQueueBackend
from background_workflows.storage.tables.azure_task_store import AzureTaskStore
from background_workflows.storage.tables.sqlite_task_store import SqliteTaskStore
from background_workflows.utils.workflow_client import WorkflowClient
from background_workflows.storage.blobs.local_blob_store import LocalBlobStore

# Ensure that the SampleTask and ping class is registered (side-effect of import)
SampleTask
ping

# Generate a unique SQLite database path for testing.
db_path: str = f"TestCeleryE2E_{TestHelper.generate_guid_for_local_db()}.db"


class TestCeleryWithSqliteE2E(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        """
        Create a dedicated Celery app for end-to-end testing.

        The Celery app is configured using the broker and backend URLs defined in AppConstants.
        Required task modules are included and task routing is set up.
        """
        cls.celery_app: Celery = Celery(
            "test_celery_e2e",
            broker=AppConstants.Celery.get_celery_broker_url(),
            backend=AppConstants.Celery.get_celery_backend_url(),
        )
        cls.celery_app.conf.include = [
            "celery.contrib.testing.tasks",
            "background_workflows.tasks.celery.celery_task",
        ]
        cls.celery_app.conf.task_routes = {
            "background_workflows.tasks.celery_task.celery_task_handler": {
                "queue": "test_queue_test_celery_and_sqlite_e2e"
            }
        }
        cls.celery_app.conf.update(
            task_always_eager=False,
            worker_concurrency=1,
        )

    def setUp(self) -> None:
        """
        Set up the testing environment for each test:
          - Remove any existing test database.
          - Initialize the Celery queue backend and local SQLite task store.
          - Create a WorkflowClient for starting and querying tasks.
        """
        if os.path.exists(db_path):
            os.remove(db_path)

        # Initialize the Celery Queue Backend
        self.queue_backend: CeleryQueueBackend = CeleryQueueBackend(
            celery_app=self.celery_app,
            task_name=AppConstants.Celery.TASK_NAME_BACKGROUND,
        )

        # Initialize the SQLite Task Store
        self.task_store: SqliteTaskStore = SqliteTaskStore(db_path=db_path)
        self.task_store.create_if_not_exists()

        # Initialize a local Blob Store (could be AzureBlobStore in production)
        self.unique_root = f"test_blobs_celery_sqlite_{TestHelper.generate_guid_for_blob()}"
        self.blob_store = LocalBlobStore( root_dir = self.unique_root )  # Using local blob store for testing

        # Initialize the WorkflowClient with the blob store
        self.client: WorkflowClient = WorkflowClient(self.task_store, self.queue_backend, self.blob_store)

    def tearDown(self) -> None:
        """
        Tear down the test environment by closing the task store and removing the test database file.
        """
        self.task_store.close()
        if os.path.exists(db_path):
            os.remove(db_path)

        if os.path.exists( self.unique_root ):
            try:
                # Remove directory and all its contents
                shutil.rmtree( self.unique_root )
                print( f"Successfully deleted {self.unique_root}" )
            except Exception as e:
                print( f"Failed to delete {self.unique_root}: {e}" )

    def test_sample_task_e2e(self) -> None:
        """
        End-to-end test for SAMPLE_TASK using Celery with a local SQLite task store.

        Steps:
          1. Enqueue a task with activity type "SAMPLE_TASK" and input parameters.
          2. Run a single pass of the controller to process the task.
          3. Poll until the task status is updated to COMPLETED.
          4. Retrieve and validate the task result.
        """
        with start_worker(self.celery_app, pool="solo") as worker:
            # 1) Prepare the blob content to pass
            blob_content = "This is some blob content"

            # 2) Start an activity by enqueuing a task.
            row_key: str = self.client.start_activity(
                activity_type="SAMPLE_TASK",
                resource_id="TestRes",
                store_mode=AppConstants.TaskStoreFactory.StoreModes.SQLITE,
                database_name=db_path,
                container_name="test_container",  # Add blob container
                blob_name="test_blob",  # Add blob name
                blob_content=blob_content,  # Pass the blob content here
                x = 21,
                y = "HelloE2E",
            )
            print("Enqueued Celery-based task with row_key =", row_key)

            # 3) Wait (poll) for the task to complete (up to 15 seconds).
            status: Optional[str] = None
            for _ in range(15):
                status = self.client.get_status(row_key, "TestRes")
                if status == "COMPLETED":
                    break
                time.sleep(1)

            # 4) Verify the final status.
            final_status: Optional[str] = self.client.get_status(row_key, "TestRes")
            self.assertEqual(
                final_status,
                "COMPLETED",
                f"Task should be COMPLETED, got {final_status}",
            )

            # 5) Retrieve and validate the task result.
            result: Optional[Any] = self.client.get_result(row_key, "TestRes")
            self.assertIsNotNone(result, "Should have a result payload after completion.")
            self.assertIn("answer", result, "Result should include 'answer'.")
            self.assertIn("echo", result, "Result should include 'echo'.")
            self.assertEqual(result["answer"], 42, "Expected answer to be 42 (21 * 2).")
            self.assertEqual(result["echo"], "HelloE2E", "Expected echo to be 'HelloE2E'.")

            # Validate that container_name and blob_name are part of the result
            self.assertEqual( result[ "ContainerName" ], "test_container","Expected 'ContainerName' to be 'test_container'." )
            self.assertEqual( result[ "BlobName" ], "test_blob", "Expected 'BlobName' to be 'test_blob'." )