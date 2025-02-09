# background_workflows/storage/queue/local_queue_backend.py

import collections
from collections import deque
from typing import Any, Dict, List
from .i_queue_backend import IQueueBackend


class LocalQueueBackend(IQueueBackend):
    """
    A simple in-memory queue for local testing with manual "visibility" simulation.

    This implementation uses a deque to store messages. Each message is represented as a
    dictionary with the following keys:
      - 'id': a unique identifier (using Python's built-in id()).
      - 'pop_receipt': None (since no receipt management is required locally).
      - 'content': the original message string.
    """

    def __init__(self) -> None:
        """
        Initialize the local in-memory queue.
        """
        self.queue: deque[str] = deque()

    def create_queue(self) -> None:
        """
        Create the queue if necessary.

        For the local in-memory queue, this is a no-op.
        """
        pass

    def send_message(self, msg_str: str) -> None:
        """
        Append a message to the local in-memory queue.

        :param msg_str: The message content to enqueue.
        """
        self.queue.append(msg_str)

    def receive_messages(self, max_messages: int = 1, visibility_timeout: int = 60) -> List[Dict[str, Any]]:
        """
        Retrieve up to 'max_messages' messages from the in-memory queue.

        Each message is represented as a dictionary with keys:
          - 'id': a unique identifier generated using id(raw_message)
          - 'pop_receipt': Always None in this implementation.
          - 'content': The original message string.

        :param max_messages: The maximum number of messages to retrieve.
        :param visibility_timeout: Not used in this local implementation.
        :return: A list of message dictionaries.
        """
        msgs: List[Dict[str, Any]] = []
        while self.queue and len(msgs) < max_messages:
            raw: str = self.queue.popleft()
            msg_obj: Dict[str, Any] = {"id": id(raw), "pop_receipt": None, "content": raw}
            msgs.append(msg_obj)
        return msgs

    def delete_message(self, msg: Dict[str, Any]) -> None:
        """
        Delete the specified message from the queue.

        For the local in-memory queue, messages are removed during retrieval,
        so no further action is required.

        :param msg: The message dictionary to delete.
        """
        pass

    def update_message(self, msg: Dict[str, Any], visibility_timeout: int = 60) -> None:
        """
        Update the specified message's visibility timeout.

        This functionality is not implemented in the local approach.

        :param msg: The message dictionary to update.
        :param visibility_timeout: The new visibility timeout (unused locally).
        """
        pass
