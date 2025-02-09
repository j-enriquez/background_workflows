# background_workflows/storage/queue/i_queue_backend.py

from abc import ABC, abstractmethod
from typing import Any, Iterable

class IQueueBackend(ABC):
    """
    Interface for basic queue operations.

    Implementations must provide methods to:
      - create_queue()
      - send_message(...)
      - receive_messages(...)
      - delete_message(...)
      - update_message(...)
    """

    @abstractmethod
    def create_queue(self) -> None:
        """
        Create the queue if it does not already exist.
        """
        raise NotImplementedError("create_queue() must be implemented by subclasses.")

    @abstractmethod
    def send_message(self, msg_str: str) -> None:
        """
        Send a message to the queue.

        :param msg_str: The message string to be sent.
        """
        raise NotImplementedError("send_message() must be implemented by subclasses.")

    @abstractmethod
    def receive_messages(self, max_messages: int = 1, visibility_timeout: int = 60) -> Iterable[Any]:
        """
        Receive messages from the queue.

        :param max_messages: Maximum number of messages to retrieve.
        :param visibility_timeout: The visibility timeout (in seconds) for the retrieved messages.
        :return: An iterable of message objects.
        """
        raise NotImplementedError("receive_messages() must be implemented by subclasses.")

    @abstractmethod
    def delete_message(self, msg: Any) -> None:
        """
        Delete the specified message from the queue.

        :param msg: The message object to delete.
        """
        raise NotImplementedError("delete_message() must be implemented by subclasses.")

    @abstractmethod
    def update_message(self, msg: Any, visibility_timeout: int = 60) -> None:
        """
        Update the visibility timeout of the specified message.

        :param msg: The message object to update.
        :param visibility_timeout: The new visibility timeout (in seconds).
        """
        raise NotImplementedError("update_message() must be implemented by subclasses.")
