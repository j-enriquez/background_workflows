import unittest
from typing import Any, Dict, List
from background_workflows.storage.queue.local_queue_backend import LocalQueueBackend

class TestLocalQueueBackend(unittest.TestCase):
    def setUp(self) -> None:
        """
        Initialize a new LocalQueueBackend instance for each test.
        """
        self.queue: LocalQueueBackend = LocalQueueBackend()

    def test_send_receive_single(self) -> None:
        """
        Test that sending a single message enqueues it properly and it is correctly retrieved.
        """
        self.queue.send_message("msg1")
        msgs: List[Dict[str, Any]] = self.queue.receive_messages()
        self.assertEqual(len(msgs), 1, "There should be exactly one message in the queue.")
        self.assertEqual(msgs[0]["content"], "msg1", "The message content should be 'msg1'.")

    def test_delete_message(self) -> None:
        """
        Test that calling delete_message results in an empty queue.

        Note:
          In this local in-memory implementation, messages are removed during retrieval.
          Hence, delete_message is effectively a no-op after a message has been received.
        """
        self.queue.send_message("msg1")
        # Retrieve the message, which also removes it from the queue.
        msg: Dict[str, Any] = self.queue.receive_messages()[0]
        # Call delete_message (should be a no-op for the local implementation).
        self.queue.delete_message(msg)
        # Subsequent calls should return an empty list.
        msgs: List[Dict[str, Any]] = self.queue.receive_messages()
        self.assertEqual(len(msgs), 0, "The queue should be empty after deletion.")

if __name__ == "__main__":
    unittest.main()
