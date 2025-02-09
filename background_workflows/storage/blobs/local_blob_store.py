# background_workflows/storage/blobs/local_blob_store.py

import os
from typing import Any
from .i_blob_store import IBlobStore
from ...constants.app_constants import AppConstants


class LocalBlobStore(IBlobStore):
    """
    LocalBlobStore is a filesystem-based implementation of IBlobStore,
    intended for testing and local development. Blobs are stored in a
    directory structure under a root directory, with each container represented
    as a subdirectory.
    """

    def __init__(self, root_dir: str = AppConstants.LocalBlob.ROOT_DIR) -> None:
        """
        Initialize the LocalBlobStore with the specified root directory.

        :param root_dir: Directory to store all containers and blobs.
                         Defaults to AppConstants.LocalBlob.ROOT_DIR.
        """
        self.root_dir: str = root_dir
        if not os.path.exists(self.root_dir):
            os.makedirs(self.root_dir, exist_ok=True)

    def create_container_if_not_exists(self, container_name: str) -> None:
        """
        Creates a container directory if it does not already exist.

        :param container_name: The name of the container to create.
        """
        container_path: str = os.path.join(self.root_dir, container_name)
        os.makedirs(container_path, exist_ok=True)

    def upload_blob(self, container_name: str, blob_name: str, data: bytes) -> None:
        """
        Uploads binary data to a blob file within the specified container.
        The container directory is created if it does not exist.

        :param container_name: The name of the container.
        :param blob_name: The name of the blob file.
        :param data: The binary data to upload.
        """
        container_path: str = os.path.join(self.root_dir, container_name)
        os.makedirs(container_path, exist_ok=True)
        blob_path: str = os.path.join(container_path, blob_name)
        with open(blob_path, "wb") as f:
            f.write(data)

    def download_blob(self, container_name: str, blob_name: str) -> bytes:
        """
        Downloads the blob from the specified container.

        :param container_name: The name of the container.
        :param blob_name: The name of the blob file.
        :return: The binary data read from the blob.
        :raises FileNotFoundError: If the blob file does not exist.
        """
        blob_path: str = os.path.join(self.root_dir, container_name, blob_name)
        with open(blob_path, "rb") as f:
            return f.read()

    def delete_blob(self, container_name: str, blob_name: str) -> None:
        """
        Deletes the specified blob from the given container.

        :param container_name: The name of the container.
        :param blob_name: The name of the blob file to delete.
        """
        blob_path: str = os.path.join(self.root_dir, container_name, blob_name)
        if os.path.isfile(blob_path):
            os.remove(blob_path)
