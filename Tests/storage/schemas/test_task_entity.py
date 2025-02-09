import unittest
from typing import Any, Dict
from background_workflows.storage.schemas.task_entity import TaskEntity


class TestTaskEntity( unittest.TestCase ):
    def test_default_init(self) -> None:
        """
        Test that TaskEntity initializes correctly with default values.

        Expected behavior:
          - ResourceId is set equal to PartitionKey.
          - RowKey is set as provided.
          - Status defaults to "CREATED".
        """
        entity: TaskEntity = TaskEntity( PartitionKey = "res", RowKey = "123" )
        self.assertEqual( entity.ResourceId, "res" )
        self.assertEqual( entity.RowKey, "123" )
        self.assertEqual( entity.Status, "CREATED" )

    def test_status_changes(self) -> None:
        """
        Test that marking the task as running, completed, or error updates the Status accordingly.
        """
        entity: TaskEntity = TaskEntity( PartitionKey = "res", RowKey = "123" )
        entity.mark_running()
        self.assertEqual( entity.Status, "RUNNING" )
        entity.mark_completed()
        self.assertEqual( entity.Status, "COMPLETED" )
        entity.mark_error()
        self.assertEqual( entity.Status, "ERROR" )

    def test_dict_method(self) -> None:
        """
        Test that the to_dict method returns a dictionary containing the expected keys.
        """
        entity: TaskEntity = TaskEntity( PartitionKey = "res", RowKey = "123", InputPayload = "inp" )
        d: Dict[ str, Any ] = entity.to_dict()
        self.assertIn( "PartitionKey", d )
        self.assertIn( "InputPayload", d )


if __name__ == "__main__":
    unittest.main()
