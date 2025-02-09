import unittest
from background_workflows.utils.workflow_client import WorkflowClient
from background_workflows.storage.tables.sqlite_task_store import SqliteTaskStore
from background_workflows.storage.queue.local_queue_backend import LocalQueueBackend

class TestWorkflowClient(unittest.TestCase):
    def setUp(self) -> None:
        """
        Set up an in-memory SQLite task store and a local queue backend.
        Initialize the WorkflowClient with these components.
        """
        self.store = SqliteTaskStore(":memory:")
        self.store.create_if_not_exists()
        self.queue = LocalQueueBackend()
        self.client = WorkflowClient(self.store, self.queue)

    def test_start_activity(self) -> None:
        """
        Test that starting an activity returns a valid row_key.
        """
        row_key = self.client.start_activity("TEST_ACTIVITY", "resource_123", x=1, y=2)
        self.assertIsInstance(row_key, str)

    def test_get_status_not_found(self) -> None:
        """
        Test that querying the status of a non-existent task returns None.
        """
        status = self.client.get_status("nonexistent_rowkey", "resource_123")
        self.assertIsNone(status)

    def test_get_result_not_found(self) -> None:
        """
        Test that querying the result of a non-existent task returns None.
        """
        result = self.client.get_result("nonexistent_rowkey", "resource_123")
        self.assertIsNone(result)

if __name__ == "__main__":
    unittest.main()
