import unittest
from typing import Any
from background_workflows.tasks.base_task import BaseTask
from background_workflows.storage.tables.sqlite_task_store import SqliteTaskStore


class MockTask(BaseTask):
    def execute_single(self, msg: Any) -> None:
        """
        A dummy implementation of execute_single for testing purposes.
        No actual processing is performed.
        """
        pass  # This method is intentionally left blank for testing.


class TestBaseTask(unittest.TestCase):
    def setUp(self) -> None:
        """
        Set up an in-memory SQLite task store and initialize a MockTask instance.
        """
        self.store = SqliteTaskStore(":memory:")
        self.store.create_if_not_exists()
        self.task = MockTask(self.store)

    def test_generate_batch_id(self) -> None:
        """
        Test that _generate_batch_id returns a string containing a hyphen,
        indicating it is composed of the hostname and a timestamp.
        """
        batch_id: str = self.task._generate_batch_id()
        self.assertIsInstance(batch_id, str)
        self.assertIn("-", batch_id)  # Expect a format like "hostname-epoch"


if __name__ == "__main__":
    unittest.main()
