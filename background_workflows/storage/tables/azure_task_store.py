# background_workflows/storage/tables/azure_task_store.py

from typing import Optional
from azure.data.tables import TableServiceClient
from azure.core.exceptions import ResourceNotFoundError
from background_workflows.constants.app_constants import AppConstants
from background_workflows.storage.schemas.task_entity import TaskEntity
from background_workflows.storage.tables.i_task_storage import ITaskStore


class AzureTaskStore( ITaskStore ):
    """
    An implementation of ITaskStore using Azure Table Storage.

    This class handles the creation of the active and finished tables, and provides
    methods for retrieving, upserting, deleting, and moving TaskEntity objects.
    """

    def __init__(
            self,
            connection_string: str,
            active_table_name: str = AppConstants.TaskStoreFactory.get_active_table_name(),
            finished_table_name: str = AppConstants.TaskStoreFactory.get_finished_table_name(),
    ) -> None:
        """
        Initialize the AzureTaskStore.

        :param connection_string: Azure Storage connection string.
        :param active_table_name: Name of the table for active tasks.
        :param finished_table_name: Name of the table for finished tasks.
        """
        self.connection_string: str = connection_string
        self.active_table_name: str = active_table_name
        self.finished_table_name: str = finished_table_name

        self.table_service_client: TableServiceClient = TableServiceClient.from_connection_string(
            self.connection_string
        )
        self.active_client = None
        self.finished_client = None

    def create_if_not_exists(self) -> None:
        """
        Ensures that the required tables exist.

        If the active or finished table does not exist, it will be created. Once created,
        the table clients are initialized.
        """
        self.table_service_client.create_table_if_not_exists( self.active_table_name )
        self.table_service_client.create_table_if_not_exists( self.finished_table_name )
        self.active_client = self.table_service_client.get_table_client( self.active_table_name )
        self.finished_client = self.table_service_client.get_table_client( self.finished_table_name )

    def get_task(self, resource_id: str, row_key: str) -> Optional[ TaskEntity ]:
        """
        Retrieves a task from the active table. If the task is not found in the active table,
        it attempts to retrieve it from the finished table.

        :param resource_id: The partition key for the task.
        :param row_key: The row key (unique identifier) for the task.
        :return: A TaskEntity instance if found, or None otherwise.
        """
        try:
            entity_data = self.active_client.get_entity( partition_key = resource_id, row_key = row_key )
            return TaskEntity( **entity_data )
        except ResourceNotFoundError:
            try:
                entity_data = self.finished_client.get_entity( partition_key = resource_id, row_key = row_key )
                return TaskEntity( **entity_data )
            except ResourceNotFoundError:
                return None

    def upsert_task(self, entity: TaskEntity) -> None:
        """
        Inserts or updates the provided task entity in the active table.

        :param entity: The TaskEntity to upsert.
        """
        data = entity.to_dict()
        self.active_client.upsert_entity( data )

    def delete_task(self, resource_id: str, row_key: str) -> None:
        """
        Deletes the task from the active table.

        :param resource_id: The partition key of the task.
        :param row_key: The row key of the task.
        """
        self.active_client.delete_entity( partition_key = resource_id, row_key = row_key )

    def move_to_finished(self, entity: TaskEntity) -> None:
        """
        Moves a task entity to the finished table by upserting it there.

        :param entity: The TaskEntity to move.
        """
        data = entity.to_dict()
        self.finished_client.upsert_entity( data )
