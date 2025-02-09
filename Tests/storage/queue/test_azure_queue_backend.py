import os
import unittest
from typing import Optional, List, Dict, Any
from azure.core.exceptions import ServiceRequestError, ResourceNotFoundError
from dotenv import load_dotenv
from azure.storage.queue import QueueClient, QueueMessage

from Tests.tests_suites_helpers.test_helper import TestHelper
from background_workflows.constants.app_constants import AppConstants
from background_workflows.storage.queue.azure_queue_backend import AzureQueueBackend


class TestAzureQueueBackend( unittest.TestCase ):
    def setUp(self) -> None:
        """
        Build a unique queue name and initialize the AzureQueueBackend.

        Loads environment variables and, if the required connection string is not set,
        skips the tests.
        """
        load_dotenv()
        conn_str: Optional[ str ] = AppConstants.TaskStoreFactory.get_azure_storage_connection_string()
        if not conn_str:
            self.skipTest( "AZURE_STORAGE_CONNECTION_STRING not set." )
        self.queue_name: str = f"testqueue{TestHelper.generate_guid_for_queue()}"
        self.backend: AzureQueueBackend = AzureQueueBackend( conn_str, self.queue_name )

        try:
            self.backend.create_queue()
        except ServiceRequestError as ex:
            self.fail( f"Could not connect to Azure/Azurite: {ex}" )

    def tearDown(self) -> None:
        """
        Clean up by deleting the queue created during setup.

        If the queue is not found (e.g., already deleted), the exception is caught and ignored.
        """
        from azure.storage.queue import QueueClient

        conn_str: Optional[ str ] = AppConstants.TaskStoreFactory.get_azure_storage_connection_string()
        if conn_str:
            try:
                qclient: QueueClient = QueueClient.from_connection_string( conn_str, self.queue_name )
                qclient.delete_queue()
            except ResourceNotFoundError:
                pass

    def test_send_receive_message(self) -> None:
        """
        Test that sending a message enqueues it correctly and that it can be received,
        then deleted, leaving the queue empty.
        """
        # 1) Send a message.
        test_msg: str = "Hello from AzureQueueBackend"
        self.backend.send_message( test_msg )

        # 2) Receive the message.
        messages: List[ QueueMessage ] = list(
            self.backend.receive_messages( max_messages = 1, visibility_timeout = 30 )
        )
        self.assertEqual( len( messages ), 1, "Expected exactly one message in the queue." )
        first: QueueMessage = messages[ 0 ]
        self.assertIn( "content", first, "Message should have a 'content' key." )
        self.assertEqual( first[ "content" ], test_msg, "Message content does not match expected value." )

        # 3) Delete the message.
        self.backend.delete_message( first )

        # 4) Confirm the queue is now empty.
        messages_empty: List[ QueueMessage ] = list(
            self.backend.receive_messages( max_messages = 1 )
        )
        self.assertEqual( len( messages_empty ), 0, "Expected the queue to be empty after deletion." )


if __name__ == "__main__":
    unittest.main()
