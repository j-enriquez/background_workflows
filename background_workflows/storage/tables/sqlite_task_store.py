# background_workflows/storage/tables/sqlite_task_store.py

import sqlite3
import os
from datetime import datetime
from typing import Optional, List, Any

from background_workflows.constants.app_constants import AppConstants
from background_workflows.storage.schemas.task_entity import TaskEntity
from background_workflows.storage.tables.i_task_storage import ITaskStore
from background_workflows.utils.task_logger import logger


class SqliteTaskStore(ITaskStore):
    """
    SQLite-based ITaskStore implementation using dynamic table names for 'active'
    and 'finished' tasks. This class creates the necessary tables (if they do not exist)
    and provides methods for upserting, retrieving, deleting, and moving tasks.
    """

    def __init__(
        self,
        db_path: str = AppConstants.TaskStoreFactory.get_sqlite_db_path(),
        active_table_name: str = AppConstants.TaskStoreFactory.get_active_table_name(),
        finished_table_name: str = AppConstants.TaskStoreFactory.get_finished_table_name(),
    ) -> None:
        """
        Initialize the SQLite task store.

        :param db_path: Path to the SQLite database file (use ":memory:" for tests).
        :param active_table_name: Name of the table that stores active tasks.
        :param finished_table_name: Name of the table that stores finished tasks.
        """
        self.db_path: str = db_path
        self.active_table_name: str = active_table_name
        self.finished_table_name: str = finished_table_name
        self._conn: Optional[sqlite3.Connection] = None

    def create_if_not_exists(self) -> None:
        """
        Creates the required tables in the SQLite database if they do not already exist.
        Uses "IF NOT EXISTS" in the CREATE TABLE statements.
        """
        # Determine if initialization is needed by checking if the database file exists.
        needs_init: bool = not os.path.exists(self.db_path)
        self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        if needs_init:
            with self._conn:
                # Create the "active" table if it doesn't exist.
                self._conn.execute(
                    f"""
                    CREATE TABLE IF NOT EXISTS {self.active_table_name} (
                        resource_id TEXT,
                        row_key TEXT,
                        task_type TEXT,
                        status TEXT,
                        input_payload TEXT,
                        output_payload TEXT,
                        start_time TEXT,
                        end_time TEXT,
                        batch_id TEXT,
                        error_message TEXT,
                        PRIMARY KEY(resource_id, row_key)
                    );
                    """
                )
                # Create the "finished" table if it doesn't exist.
                self._conn.execute(
                    f"""
                    CREATE TABLE IF NOT EXISTS {self.finished_table_name} (
                        resource_id TEXT,
                        row_key TEXT,
                        task_type TEXT,
                        status TEXT,
                        input_payload TEXT,
                        output_payload TEXT,
                        start_time TEXT,
                        end_time TEXT,
                        batch_id TEXT,
                        error_message TEXT,
                        PRIMARY KEY(resource_id, row_key)
                    );
                    """
                )
            logger.info("SQLite tables created or verified.")

    def _row_to_entity(self, row: List[Any]) -> TaskEntity:
        """
        Converts a row from SQLite into a TaskEntity.

        :param row: List of column values from the query.
        :return: A TaskEntity instance populated with the row data.
        """
        return TaskEntity(
            PartitionKey=row[0],
            RowKey=row[1],
            TaskType=row[2],
            Status=row[3],
            InputPayload=row[4],
            OutputPayload=row[5],
            StartTime=row[6],
            EndTime=row[7],
            BatchID=row[8],
            ErrorMessage=row[9],
        )

    def get_task(self, resource_id: str, row_key: str) -> Optional[TaskEntity]:
        """
        Retrieves a task by its resource_id and row_key from the active table,
        or, if not found, from the finished table.

        :param resource_id: The partition key.
        :param row_key: The unique task identifier.
        :return: A TaskEntity instance if found; otherwise, None.
        """
        with self._conn:
            cursor = self._conn.execute(
                f"SELECT * FROM {self.active_table_name} WHERE resource_id=? AND row_key=?",
                (resource_id, row_key),
            )
            row = cursor.fetchone()
            if row:
                logger.debug(f"Row found (active): {row}")
                return self._row_to_entity(row)

            cursor = self._conn.execute(
                f"SELECT * FROM {self.finished_table_name} WHERE resource_id=? AND row_key=?",
                (resource_id, row_key),
            )
            row = cursor.fetchone()
            if row:
                logger.debug(f"Row found (finished): {row}")
                return self._row_to_entity(row)
        return None

    def upsert_task(self, entity: TaskEntity) -> bool:
        """
        Inserts or updates the given task entity in the active table.
        Converts any datetime fields to ISO format if necessary.

        :param entity: The TaskEntity instance to upsert.
        :return: True if the upsert is successful, False otherwise.
        """
        try:
            data = entity.to_dict()
            # Convert datetime fields to ISO format if they are datetime objects.
            data["StartTime"] = data["StartTime"].isoformat() if isinstance(data["StartTime"], datetime) else None
            data["EndTime"] = data["EndTime"].isoformat() if isinstance(data["EndTime"], datetime) else None

            logger.debug(f"Upserting task: {data}")
            with self._conn:
                self._conn.execute(
                    f"""
                    INSERT INTO {self.active_table_name} (
                        resource_id,
                        row_key,
                        task_type,
                        status,
                        input_payload,
                        output_payload,
                        start_time,
                        end_time,
                        batch_id,
                        error_message
                    )
                    VALUES (
                        :PartitionKey,
                        :RowKey,
                        :TaskType,
                        :Status,
                        :InputPayload,
                        :OutputPayload,
                        :StartTime,
                        :EndTime,
                        :BatchID,
                        :ErrorMessage
                    )
                    ON CONFLICT(resource_id, row_key) DO UPDATE SET
                        task_type = COALESCE(excluded.task_type, {self.active_table_name}.task_type),
                        status = COALESCE(excluded.status, {self.active_table_name}.status),
                        input_payload = COALESCE(excluded.input_payload, {self.active_table_name}.input_payload),
                        output_payload = COALESCE(excluded.output_payload, {self.active_table_name}.output_payload),
                        start_time = COALESCE(excluded.start_time, {self.active_table_name}.start_time),
                        end_time = COALESCE(excluded.end_time, {self.active_table_name}.end_time),
                        batch_id = COALESCE(excluded.batch_id, {self.active_table_name}.batch_id),
                        error_message = COALESCE(excluded.error_message, {self.active_table_name}.error_message)
                    """,
                    data,
                )
            logger.debug(f"Task {data['RowKey']} upserted successfully.")
            return True

        except Exception as e:
            logger.exception(f"Error while upserting task: {e}")
            return False

    def delete_task(self, resource_id: str, row_key: str) -> None:
        """
        Deletes a task from the active table.

        :param resource_id: The partition key.
        :param row_key: The unique task identifier.
        """
        with self._conn:
            self._conn.execute(
                f"DELETE FROM {self.active_table_name} WHERE resource_id=? AND row_key=?",
                (resource_id, row_key),
            )
        logger.debug(f"Deleted task with resource_id={resource_id}, row_key={row_key}")

    def move_to_finished(self, entity: TaskEntity) -> None:
        """
        Inserts the given task entity into the finished table.

        :param entity: The TaskEntity instance to move.
        """
        data = entity.to_dict()
        with self._conn:
            self._conn.execute(
                f"""
                INSERT INTO {self.finished_table_name} (
                    resource_id,
                    row_key,
                    task_type,
                    status,
                    input_payload,
                    output_payload,
                    start_time,
                    end_time,
                    batch_id,
                    error_message
                )
                VALUES (
                    :PartitionKey,
                    :RowKey,
                    :TaskType,
                    :Status,
                    :InputPayload,
                    :OutputPayload,
                    :StartTime,
                    :EndTime,
                    :BatchID,
                    :ErrorMessage
                )
                """,
                data,
            )
        logger.debug(f"Moved task {data['RowKey']} to finished table.")

    def get_all_active_tasks(self, resource_id: str) -> List[TaskEntity]:
        """
        Retrieves all active tasks for the specified resource.

        :param resource_id: The partition key to filter tasks.
        :return: A list of TaskEntity instances.
        """
        with self._conn:
            cursor = self._conn.execute(
                f"""
                SELECT resource_id,
                       row_key,
                       task_type,
                       status,
                       input_payload,
                       output_payload,
                       start_time,
                       end_time,
                       batch_id,
                       error_message
                FROM {self.active_table_name}
                WHERE resource_id=?
                """,
                (resource_id,),
            )
            rows = cursor.fetchall()
        return [self._row_to_entity(row) for row in rows] if rows else []

    def close(self) -> None:
        """
        Closes the SQLite database connection.
        """
        if self._conn:
            self._conn.close()
            self._conn = None
            logger.debug("SQLite connection closed.")
