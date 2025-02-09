import os
import unittest
from typing import Any, Optional
from Tests.tests_suites_helpers.test_helper import TestHelper
from background_workflows.storage.tables.sqlite_task_store import SqliteTaskStore
from background_workflows.storage.schemas.task_entity import TaskEntity


class TestSqliteTaskStore( unittest.TestCase ):
    def setUp(self) -> None:
        """
        Set up an in-memory SQLite task store using a temporary file.
        If the file already exists, it is removed before starting.
        """
        self.db_path: str = f"test_tasks_{TestHelper.generate_guid_for_local_db()}.db"
        if os.path.exists( self.db_path ):
            os.remove( self.db_path )
        self.task_store: SqliteTaskStore = SqliteTaskStore( db_path = self.db_path )
        self.task_store.create_if_not_exists()

    def tearDown(self) -> None:
        """
        Close the SQLite connection and remove the temporary database file.
        """
        self.task_store.close()
        if os.path.exists( self.db_path ):
            os.remove( self.db_path )

    def test_upsert_and_get_task(self) -> None:
        """
        Test that a TaskEntity can be upserted into the store and then retrieved correctly.
        """
        entity: TaskEntity = TaskEntity(
            PartitionKey = "res",
            RowKey = "123",
            TaskType = "TEST"
        )
        self.task_store.upsert_task( entity )
        fetched: Any = self.task_store.get_task( "res", "123" )
        self.assertIsNotNone( fetched, "TaskEntity should be retrievable after upsert." )
        self.assertEqual( fetched.TaskType, "TEST", "TaskType should match the upserted value." )

    def test_delete_task(self) -> None:
        """
        Test that a TaskEntity can be deleted from the active store.
        """
        entity: TaskEntity = TaskEntity(
            PartitionKey = "res",
            RowKey = "123",
            TaskType = "TEST"
        )
        self.task_store.upsert_task( entity )
        self.task_store.delete_task( "res", "123" )
        fetched: Optional[ TaskEntity ] = self.task_store.get_task( "res", "123" )
        self.assertIsNone( fetched, "TaskEntity should be None after deletion." )

    def test_move_to_finished(self) -> None:
        """
        Test that a TaskEntity can be moved from the active store to the finished store.

        After moving, deleting the task from the active store should not remove it from finished.
        """
        entity: TaskEntity = TaskEntity(
            PartitionKey = "res",
            RowKey = "123"
        )
        self.task_store.upsert_task( entity )
        self.task_store.move_to_finished( entity )
        # Remove from active tasks.
        self.task_store.delete_task( "res", "123" )
        # Verify the task still exists in the finished store.
        still_exists: Optional[ TaskEntity ] = self.task_store.get_task( "res", "123" )
        self.assertIsNotNone( still_exists, "Task should exist in finished tasks after move." )


if __name__ == "__main__":
    unittest.main()
