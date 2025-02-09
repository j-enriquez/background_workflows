# background_workflows/storage/queue/azure_queue_backend.py

from azure.storage.queue import QueueClient, QueueMessage
from typing import Any, Iterable
from .i_queue_backend import IQueueBackend


class AzureQueueBackend( IQueueBackend ):
    """
    An implementation of IQueueBackend that uses Azure Storage Queues.

    This class encapsulates all queue operations such as creating a queue,
    sending messages, receiving messages, deleting messages, and updating messages.
    """

    def __init__(self, connection_string: str, queue_name: str) -> None:
        """
        Initialize the AzureQueueBackend with the given connection string and queue name.

        :param connection_string: The Azure Storage connection string.
        :param queue_name: The name of the Azure queue.
        """
        self.connection_string: str = connection_string
        self.queue_name: str = queue_name
        self.queue_client: Any = None

    def create_queue(self) -> None:
        """
        Creates the queue if it doesn't already exist.

        Initializes the queue client using the provided connection string and queue name.
        """
        self.queue_client = QueueClient.from_connection_string(
            conn_str = self.connection_string, queue_name = self.queue_name
        )
        self.queue_client.create_queue()

    def send_message(self, msg_str: str) -> None:
        """
        Sends a message string to the Azure queue.

        :param msg_str: The message content to send.
        """
        self.queue_client.send_message( msg_str )

    def receive_messages(self, max_messages: int = 1, visibility_timeout: int = 60) -> Iterable[ QueueMessage ]:
        """
        Receives messages from the queue.

        :param max_messages: Maximum number of messages to retrieve.
        :param visibility_timeout: The visibility timeout (in seconds) for the messages.
        :return: An iterable of QueueMessage objects.
        """
        return self.queue_client.receive_messages(
            max_messages = max_messages, visibility_timeout = visibility_timeout
        )

    def delete_message(self, msg: QueueMessage) -> None:
        """
        Deletes the specified message from the queue.

        :param msg: The QueueMessage object to delete.
        """
        self.queue_client.delete_message( msg )

    def update_message(self, msg: QueueMessage, visibility_timeout: int = 60) -> None:
        """
        Updates the visibility timeout of the specified message.

        :param msg: The QueueMessage object to update.
        :param visibility_timeout: The new visibility timeout (in seconds).
        """
        self.queue_client.update_message(
            msg.id, msg.pop_receipt, visibility_timeout = visibility_timeout
        )
