import unittest
import json
from typing import Any
from background_workflows.tasks.process_single_queue import ProcessSingleQueue
from background_workflows.storage.tables.sqlite_task_store import SqliteTaskStore
from background_workflows.storage.schemas.task_entity import TaskEntity


class MockProcessSingleQueue(ProcessSingleQueue):
    def do_work_on_single(self, payload: dict) -> str:
        """
        A dummy implementation that simply returns a JSON string indicating success.

        :param payload: The parsed input payload.
        :return: A JSON string with the result.
        """
        return json.dumps({"status": "worked"})


class TestProcessSingleQueue(unittest.TestCase):
    def setUp(self) -> None:
        """
        Set up an in-memory SQLite task store and initialize the MockProcessSingleQueue task.
        """
        self.store = SqliteTaskStore(":memory:")
        self.store.create_if_not_exists()
        self.task = MockProcessSingleQueue(self.store)

    def test_execute_single(self) -> None:
        """
        Test that executing a single message properly marks the task as COMPLETED.

        This test manually inserts a TaskEntity into the store and then simulates
        processing of a message. After execution, the task status should be COMPLETED.
        """
        # Create and upsert a new TaskEntity in the active store.
        entity = TaskEntity(
            PartitionKey="res",
            RowKey="123",
            TaskType="TEST",
            InputPayload='{"test": true}',
            OutputPayload="",
            Status="CREATED",
        )
        self.store.upsert_task(entity)

        # Define a mock message with required attributes.
        class Msg:
            resource_id: str = "res"
            row_key: str = "123"

        # Execute the task processing using the mock message.
        self.task.execute_single(Msg())

        # Retrieve the task from the store and verify that its status is now COMPLETED.
        finished: Any = self.store.get_task("res", "123")
        self.assertIsNotNone(finished, "Task should be found in the store after execution.")
        self.assertEqual(finished.Status, "COMPLETED", "Task should be marked as COMPLETED.")

if __name__ == "__main__":
    unittest.main()
