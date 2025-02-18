# tests/test_http_fetch_async.py

import os
import shutil
import asyncio
import unittest
from typing import Optional, Any

from Tests.sample_tasks.async_http_fetcher import AsyncHttpFetcher
from Tests.tests_suites_helpers.test_helper import TestHelper

from background_workflows.controller.async_controller.main_async_controller import MainAsyncController
from background_workflows.storage.tables.sqlite_task_store import SqliteTaskStore
from background_workflows.storage.queue.local_queue_backend import LocalQueueBackend
from background_workflows.storage.blobs.local_blob_store import LocalBlobStore
from background_workflows.utils.workflow_client import WorkflowClient

AsyncHttpFetcher

class TestHttpFetch_Async(unittest.IsolatedAsyncioTestCase):
    """
    Test suite verifying multiple async HTTP fetch tasks run concurrently in MainAsyncController.
    """

    async def asyncSetUp(self) -> None:
        self.db_path: str = f"test_tasks_{TestHelper.generate_guid_for_local_db()}.db"
        self.task_store = SqliteTaskStore(db_path=self.db_path)
        self.task_store.create_if_not_exists()

        self.queue_backend = LocalQueueBackend()
        self.unique_root = f"test_blobs_http_fetch_{TestHelper.generate_guid_for_blob()}"
        self.blob_store = LocalBlobStore(root_dir=self.unique_root)

        # Create the async controller
        self.controller = MainAsyncController(
            task_store=self.task_store,
            queue_backend=self.queue_backend,
            max_concurrent_tasks=100,   # Let 3 tasks run in parallel
            poll_interval_secs=.1,
            cpu_threshold=1.0
        )

        self.client = WorkflowClient(
            self.task_store, self.queue_backend, self.blob_store
        )

        # Start controller in background
        self.controller_task = asyncio.create_task(self.controller.run())

    async def asyncTearDown(self) -> None:
        # Stop the controller
        await self.controller.shutdown()
        await self.controller_task

        self.task_store.close()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        if os.path.exists(self.unique_root):
            try:
                shutil.rmtree(self.unique_root)
            except Exception as e:
                print(f"Failed to delete {self.unique_root}: {e}")

    async def test_http_fetch_tasks(self):
        """
        Enqueue several ASYNC_HTTP_FETCH tasks, each retrieving a URL,
        then verify concurrency and results.
        """

        urls = [
            "https://httpbin.org/get?test=1",
            "https://httpbin.org/delay/1",
            "https://httpbin.org/delay/2",
            "https://httpbin.org/get?test=4",
            "https://httpbin.org/get?test=5",
        ]
        job_ids = []

        for i, url in enumerate(urls):
            job_id = self.client.start_activity(
                activity_type="ASYNC_HTTP_FETCH",
                resource_id="HttpFetcherGroup",
                url=url
            )
            job_ids.append(job_id)

        # Wait a bit for tasks to be processed
        # The controller is running concurrently in self.controller_task
        await asyncio.sleep(10)

        # Check statuses and results
        for i, job_id in enumerate(job_ids):
            status = self.client.get_status(job_id, "HttpFetcherGroup")
            self.assertEqual(status, "COMPLETED", f"Task {i} not completed")

            result: Optional[Any] = self.client.get_result(job_id, resource_id="HttpFetcherGroup")
            self.assertIsNotNone(result, f"No result for job_id={job_id}")
            self.assertIn("status_code", result)
            self.assertIn("content_length", result)
            self.assertIn("first_50_chars", result)

            # Example assertion: status_code == 200
            self.assertEqual(result["status_code"], 200, "HTTP fetch should return 200 status")
            print(f"Task {i}, status={result['status_code']}, length={result['content_length']}")
