# background_workflows/storage/tables/task_store_factory.py

import os
from typing import Optional
from background_workflows.constants.app_constants import AppConstants
from background_workflows.storage.tables.i_task_storage import ITaskStore
from background_workflows.storage.tables.sqlite_task_store import SqliteTaskStore
from background_workflows.storage.tables.azure_task_store import AzureTaskStore
from background_workflows.tasks.base_task import logger


class TaskStoreFactory:
    """
    Factory for creating a task store (either AzureTaskStore or SqliteTaskStore)
    based on the provided store mode and configuration parameters.

    This factory instantiates the proper store implementation, ensures that the
    underlying storage (tables) is created, and returns an ITaskStore instance for use.
    """

    def __init__(
        self,
        store_mode: str,
        azure_connection_string: Optional[str] = None,
        active_table_name: Optional[str] = None,
        finished_table_name: Optional[str] = None,
        sqlite_db_path: Optional[str] = None,
    ) -> None:
        """
        Initialize the TaskStoreFactory with the desired configuration.

        :param store_mode: The storage mode to use ('azure' or 'sqlite').
        :param azure_connection_string: Connection string for Azure Table Storage.
                                        If not provided, the default from AppConstants is used.
        :param active_table_name: Name of the table for active tasks.
                                  Defaults to the AppConstants value if not provided.
        :param finished_table_name: Name of the table for finished tasks.
                                    Defaults to the AppConstants value if not provided.
        :param sqlite_db_path: Path to the SQLite database.
                               Defaults to the AppConstants value if not provided.
        """
        self.store_mode: str = store_mode.lower()
        self.azure_connection_string: Optional[str] = (
            azure_connection_string or AppConstants.TaskStoreFactory.get_azure_storage_connection_string()
        )
        self.active_table_name: str = active_table_name or AppConstants.TaskStoreFactory.get_active_table_name()
        self.finished_table_name: str = finished_table_name or AppConstants.TaskStoreFactory.get_finished_table_name()
        self.sqlite_db_path: str = sqlite_db_path or AppConstants.TaskStoreFactory.get_sqlite_db_path()

    def get_task_store(self) -> ITaskStore:
        """
        Create and return an ITaskStore instance based on the configured store mode.

        :return: An instance of AzureTaskStore if store_mode is 'azure', or SqliteTaskStore if store_mode is 'sqlite'.
        :raises ValueError: If store_mode is not recognized or required parameters are missing.
        """
        if self.store_mode == "azure":
            if not self.azure_connection_string:
                raise ValueError("Azure connection string is required for Azure store mode.")
            store: ITaskStore = AzureTaskStore(
                connection_string=self.azure_connection_string,
                active_table_name=self.active_table_name,
                finished_table_name=self.finished_table_name,
            )
        elif self.store_mode == "sqlite":
            store = SqliteTaskStore(
                db_path=self.sqlite_db_path,
                active_table_name=self.active_table_name,
                finished_table_name=self.finished_table_name,
            )
        else:
            raise ValueError(f"Unknown store_mode: {self.store_mode}")

        logger.info(f"Creating task store using {self.store_mode} mode.")
        store.create_if_not_exists()
        return store
