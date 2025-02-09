# tests/test_task_store_factory.py

import os
import unittest
from unittest.mock import patch
from typing import Optional

from dotenv import load_dotenv

from background_workflows.constants.app_constants import AppConstants
from background_workflows.storage.tables.azure_task_store import AzureTaskStore
from background_workflows.storage.tables.sqlite_task_store import SqliteTaskStore
from background_workflows.storage.tables.task_store_factory import TaskStoreFactory

class TestTaskStoreFactory(unittest.TestCase):
    def test_forced_sqlite_mode(self) -> None:
        """
        Test that forcing the store mode to 'sqlite' returns an instance of SqliteTaskStore.
        """
        factory: TaskStoreFactory = TaskStoreFactory(
            store_mode=AppConstants.TaskStoreFactory.StoreModes.SQLITE
        )
        store = factory.get_task_store()
        self.assertIsInstance(store, SqliteTaskStore)

    @patch.dict(
        os.environ,
        {
            "STORE_MODE": "azure",
            "AZURE_STORAGE_CONNECTION_STRING": "DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;QueueEndpoint=http://127.0.0.1:10001/devstoreaccount1;TableEndpoint=http://127.0.0.1:10002/devstoreaccount1;",
        },
    )
    def test_env_vars_for_azure(self) -> None:
        """
        Test that when the environment variables force the store mode to 'azure',
        the factory returns an instance of AzureTaskStore.
        """
        factory: TaskStoreFactory = TaskStoreFactory(
            store_mode = AppConstants.TaskStoreFactory.StoreModes.AZURE
        )
        store = factory.get_task_store()
        self.assertIsInstance( store, AzureTaskStore )


if __name__ == "__main__":
    load_dotenv()  # Ensure environment variables are loaded before tests run.
    unittest.main()