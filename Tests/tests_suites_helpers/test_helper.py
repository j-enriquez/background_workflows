import uuid
from typing import Final


class TestHelper:
    """
    Utility class for generating unique identifiers for testing purposes.

    Provides static methods to generate GUIDs for blobs, tables, queues, and local databases.
    """

    @staticmethod
    def generate_guid_for_blob() -> str:
        """
        Generate a short GUID for naming blobs.

        :return: A string of 8 hexadecimal characters.
        """
        return str( uuid.uuid4() )[ :8 ]

    @staticmethod
    def generate_guid_for_table() -> str:
        """
        Generate a full GUID for naming tables.

        :return: A full GUID string.
        """
        return str( uuid.uuid4() )

    @staticmethod
    def generate_guid_for_queue() -> str:
        """
        Generate a short GUID for naming queues.

        :return: A string of 6 hexadecimal characters.
        """
        return str( uuid.uuid4().hex[ :6 ] )

    @staticmethod
    def generate_guid_for_local_db() -> str:
        """
        Generate a short GUID for naming local SQLite databases.

        :return: A string of 8 hexadecimal characters.
        """
        return str( uuid.uuid4().hex[ :8 ] )
