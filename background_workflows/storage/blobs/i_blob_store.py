# background_workflows/storage/blobs/i_blob_store.py

from abc import ABC, abstractmethod

class IBlobStore(ABC):
    """
    Interface for a blob store that supports file uploads and downloads.
    """

    @abstractmethod
    def create_container_if_not_exists(self, container_name: str) -> None:
        """
        Create a container if it does not already exist.

        :param container_name: The name of the container to create.
        """
        raise NotImplementedError

    @abstractmethod
    def upload_blob(self, container_name: str, blob_name: str, data: bytes) -> None:
        """
        Uploads a blob of data to the specified container.

        :param container_name: The container in which to upload the blob.
        :param blob_name: The name of the blob.
        :param data: The binary data to upload.
        """
        raise NotImplementedError

    @abstractmethod
    def download_blob(self, container_name: str, blob_name: str) -> bytes:
        """
        Downloads the specified blob as bytes.

        :param container_name: The container from which to download the blob.
        :param blob_name: The name of the blob.
        :return: The blob's data as a bytes object.
        """
        raise NotImplementedError

    @abstractmethod
    def delete_blob(self, container_name: str, blob_name: str) -> None:
        """
        Deletes the specified blob from the given container.

        :param container_name: The container from which to delete the blob.
        :param blob_name: The name of the blob to delete.
        """
        raise NotImplementedError
