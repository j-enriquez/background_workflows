import unittest
import json
from typing import Any, Optional
from background_workflows.controller.main.main_controller import MainController
from background_workflows.storage.tables.sqlite_task_store import SqliteTaskStore
from background_workflows.storage.queue.local_queue_backend import LocalQueueBackend

class TestMainController(unittest.TestCase):
    def setUp(self) -> None:
        """
        Set up an in-memory SQLite task store and a local queue backend.
        Initialize the MainController with a single thread and a high CPU threshold.
        """
        self.store: SqliteTaskStore = SqliteTaskStore(":memory:")
        self.store.create_if_not_exists()
        self.queue: LocalQueueBackend = LocalQueueBackend()
        self.controller: MainController = MainController(
            task_store=self.store,
            queue_backend=self.queue,
            max_threads=1,
            cpu_threshold=0.99,
        )
        self.controller.initialize_infrastructure()

    def test_run_once_with_messages(self) -> None:
        """
        Test that running a single pass of the controller processes messages correctly.

        In this test, we enqueue a message with an unknown task_type to trigger a warning.
        The log output should indicate that the message was removed.
        """
        # Enqueue a message with an unknown task type.
        test_message: str = json.dumps({
            "resource_id": "res",
            "row_key": "123",
            "task_type": "UNKNOWN",
            "payload": {}
        })
        self.queue.send_message(test_message)

        # Capture log output at the WARNING level.
        with self.assertLogs("background_workflows.controller.main.main_controller", level="WARNING") as cm:
            self.controller.run_once()

        # Verify that a warning log containing "Unknown task_type=UNKNOWN" was captured.
        log_found: bool = any(
            "Unknown task_type=UNKNOWN" in message for message in cm.output
        )
        self.assertTrue(log_found, f"Expected warning log not found. Captured logs: {cm.output}")

if __name__ == "__main__":
    unittest.main()
