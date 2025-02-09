import os
import unittest
from typing import Optional
from dotenv import load_dotenv
from azure.core.exceptions import ServiceRequestError, ResourceNotFoundError
from azure.data.tables import TableServiceClient

from Tests.tests_suites_helpers.test_helper import TestHelper
from background_workflows.constants.app_constants import AppConstants
from background_workflows.storage.tables.azure_task_store import AzureTaskStore


class TestAzureTaskStore(unittest.TestCase):
    def setUp(self) -> None:
        """
        Set up the test environment for AzureTaskStore.

        This method loads environment variables, generates unique table names,
        initializes an AzureTaskStore instance, and creates the necessary tables.
        If the required connection string is not set, the test is skipped.
        """
        load_dotenv()
        conn_str: Optional[str] = AppConstants.TaskStoreFactory.get_azure_storage_connection_string()
        if not conn_str:
            self.skipTest("AZURE_STORAGE_CONNECTION_STRING not set.")

        # Generate unique random table names for active and finished tasks.
        self.active_table: str = "active" + TestHelper.generate_guid_for_table()[:8]
        self.finished_table: str = "finished" + TestHelper.generate_guid_for_table()[:8]

        # Initialize the AzureTaskStore with the generated table names.
        self.store: AzureTaskStore = AzureTaskStore(
            connection_string=conn_str,
            active_table_name=self.active_table,
            finished_table_name=self.finished_table,
        )

        try:
            self.store.create_if_not_exists()
        except ServiceRequestError as ex:
            self.fail(f"Cannot connect to Azure/Azurite: {ex}")

        # Create a TableServiceClient to help with table cleanup.
        self.table_svc: TableServiceClient = TableServiceClient.from_connection_string(conn_str)

    def tearDown(self) -> None:
        """
        Clean up by deleting the active and finished tables created during setup.

        If a table is not found (already deleted), the exception is caught and ignored.
        """
        try:
            self.table_svc.delete_table(self.active_table)
        except ResourceNotFoundError:
            pass

        try:
            self.table_svc.delete_table(self.finished_table)
        except ResourceNotFoundError:
            pass

    def test_create_if_not_exists(self) -> None:
        """
        A simple test to verify that the create_if_not_exists method executes without error.
        """
        # The creation is verified during setup. If no exception is raised, the test passes.
        self.assertTrue(True)


if __name__ == "__main__":
    unittest.main()
