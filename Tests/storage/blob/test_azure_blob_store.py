import os
import unittest
from typing import Optional
from azure.core.exceptions import ServiceRequestError, ResourceNotFoundError
from dotenv import load_dotenv

from Tests.tests_suites_helpers.test_helper import TestHelper
from background_workflows.constants.app_constants import AppConstants
from background_workflows.storage.blobs.azure_blob_store import AzureBlobStore


class TestAzureBlobStore(unittest.TestCase):
    def setUp(self) -> None:
        """
        Set up an instance of AzureBlobStore for testing.

        Loads environment variables, generates a unique container name, and attempts to
        create the container in Azure (or Azurite). If the required connection string is not set,
        the test is skipped.
        """
        load_dotenv()
        conn_str: Optional[str] = AppConstants.TaskStoreFactory.get_azure_storage_connection_string()
        if not conn_str:
            self.skipTest("AZURE_STORAGE_CONNECTION_STRING not set.")
        self.store: AzureBlobStore = AzureBlobStore(conn_str)
        self.container_name: str = "testcontainer" + TestHelper.generate_guid_for_blob()

        try:
            self.store.create_container_if_not_exists(self.container_name)
        except ServiceRequestError as ex:
            self.fail(f"Could not connect to Azure/Azurite: {ex}")

    def tearDown(self) -> None:
        """
        Clean up the test container created during setup.

        Attempts to delete the container. If the container is not found, the exception is caught and ignored.
        """
        try:
            blob_service = self.store.blob_service_client
            container_client = blob_service.get_container_client(self.container_name)
            container_client.delete_container()
        except ResourceNotFoundError:
            pass

    def test_upload_download_delete_blob(self) -> None:
        """
        Test that uploading, downloading, and deleting a blob works as expected.

        This test uploads a blob to the container, verifies that the downloaded content
        matches the uploaded content, then deletes the blob. Finally, it confirms that attempting
        to download the deleted blob raises a ResourceNotFoundError.
        """
        blob_name: str = "hello_world.txt"
        data: bytes = b"Hello from AzureBlobStore!"
        self.store.upload_blob(self.container_name, blob_name, data)

        # Now try downloading the blob.
        downloaded: bytes = self.store.download_blob(self.container_name, blob_name)
        self.assertEqual(downloaded, data, "Downloaded blob should match uploaded data.")

        # Delete the blob.
        self.store.delete_blob(self.container_name, blob_name)

        # Confirm the blob is no longer available.
        with self.assertRaises(ResourceNotFoundError):
            self.store.download_blob(self.container_name, blob_name)


if __name__ == "__main__":
    unittest.main()
