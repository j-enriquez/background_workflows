# background_workflows/storage/blobs/azure_blob_store.py

from azure.core.exceptions import ResourceExistsError
from azure.storage.blob import BlobServiceClient
from .i_blob_store import IBlobStore
from typing import Any

class AzureBlobStore(IBlobStore):
    """
    AzureBlobStore implements the IBlobStore interface using Azure Storage Blobs.

    It provides methods to:
      - Create a container if it does not exist.
      - Upload binary data (blobs) with overwrite enabled.
      - Download a blob's content as bytes.
      - Delete a blob.
    """

    def __init__(self, connection_string: str) -> None:
        """
        Initialize the AzureBlobStore with the provided Azure Storage connection string.

        :param connection_string: An Azure Storage connection string.
        """
        self.connection_string: str = connection_string
        self.blob_service_client: BlobServiceClient = BlobServiceClient.from_connection_string(connection_string)

    def create_container_if_not_exists(self, container_name: str) -> None:
        """
        Creates the specified container if it does not already exist.

        :param container_name: The name of the container to create.
        """
        container_client = self.blob_service_client.get_container_client(container_name)
        try:
            container_client.create_container()
        except ResourceExistsError:
            # The container already exists, so no further action is needed.
            pass

    def upload_blob(self, container_name: str, blob_name: str, data: bytes) -> None:
        """
        Uploads the provided data to a blob in the specified container,
        overwriting any existing blob with the same name.

        :param container_name: The name of the container.
        :param blob_name: The name of the blob.
        :param data: The binary data to upload.
        """
        container_client = self.blob_service_client.get_container_client(container_name)
        blob_client = container_client.get_blob_client(blob_name)
        blob_client.upload_blob(data, overwrite=True)

    def download_blob(self, container_name: str, blob_name: str) -> bytes:
        """
        Downloads the specified blob from the given container.

        :param container_name: The name of the container.
        :param blob_name: The name of the blob.
        :return: The blob's data as a bytes object.
        """
        container_client = self.blob_service_client.get_container_client(container_name)
        blob_client = container_client.get_blob_client(blob_name)
        downloader = blob_client.download_blob()
        return downloader.readall()

    def delete_blob(self, container_name: str, blob_name: str) -> None:
        """
        Deletes the specified blob from the given container.

        :param container_name: The name of the container.
        :param blob_name: The name of the blob.
        """
        container_client = self.blob_service_client.get_container_client(container_name)
        container_client.delete_blob(blob_name)
