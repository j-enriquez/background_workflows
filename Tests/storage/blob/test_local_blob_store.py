import os
import shutil
import unittest
import uuid
from typing import Final

from background_workflows.storage.blobs.local_blob_store import LocalBlobStore


class TestLocalBlobStore( unittest.TestCase ):
    def setUp(self) -> None:
        """
        Set up a unique root directory for blob storage tests and initialize a LocalBlobStore.
        """
        self.unique_root: str = f"test_blobs_TestLocalBlobStore_{uuid.uuid4().hex[ :6 ]}"
        self.store: LocalBlobStore = LocalBlobStore( root_dir = self.unique_root )

    def tearDown(self) -> None:
        """
        Clean up the unique root directory after each test.
        """
        if os.path.exists( self.unique_root ):
            try:
                # Remove directory and all its contents
                shutil.rmtree( self.unique_root )
                print( f"Successfully deleted {self.unique_root}" )
            except Exception as e:
                print( f"Failed to delete {self.unique_root}: {e}" )

    def test_create_container(self) -> None:
        """
        Test that creating a container results in a corresponding directory within the root.
        """
        container_name: str = "test_container_" + uuid.uuid4().hex[ :4 ]
        self.store.create_container_if_not_exists( container_name )
        container_path: str = os.path.join( self.unique_root, container_name )
        self.assertTrue(
            os.path.exists( container_path ),
            f"Container directory '{container_path}' should exist after creation."
        )

    def test_upload_download_blob(self) -> None:
        """
        Test uploading and downloading a blob in a container.

        The test verifies that the uploaded content is exactly retrieved.
        """
        container_name: str = "test_container_" + uuid.uuid4().hex[ :4 ]
        self.store.create_container_if_not_exists( container_name )
        blob_name: Final[ str ] = "test_blob.txt"
        data: bytes = b"hello"

        # Upload the blob
        self.store.upload_blob( container_name, blob_name, data )
        # Download the blob and verify its content
        content: bytes = self.store.download_blob( container_name, blob_name )
        self.assertEqual( content, data, "Downloaded blob content should match the uploaded data." )

    def test_delete_blob(self) -> None:
        """
        Test that deleting a blob successfully removes the file from storage.
        """
        container_name: str = "test_container_" + uuid.uuid4().hex[ :4 ]
        self.store.create_container_if_not_exists( container_name )
        blob_name: Final[ str ] = "test_blob.txt"
        data: bytes = b"hello"

        # Upload the blob
        self.store.upload_blob( container_name, blob_name, data )
        # Delete the blob
        self.store.delete_blob( container_name, blob_name )
        # Construct the expected blob file path
        blob_path: str = os.path.join( self.unique_root, container_name, blob_name )
        self.assertFalse(
            os.path.exists( blob_path ),
            f"Blob file '{blob_path}' should not exist after deletion."
        )


if __name__ == "__main__":
    unittest.main()
