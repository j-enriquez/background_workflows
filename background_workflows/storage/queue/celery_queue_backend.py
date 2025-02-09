# background_workflows/storage/queue/celery_queue_backend.py

from typing import Any, List
from .i_queue_backend import IQueueBackend
from ...constants.app_constants import AppConstants


class CeleryQueueBackend(IQueueBackend):
    """
    A queue backend that sends tasks directly to Celery workers (push-based).

    In this model, tasks are directly sent to Celery, and traditional queue
    operations like receiving, deleting, or updating messages are not used.
    """

    def __init__(self, celery_app: Any, task_name: str = AppConstants.Celery.TASK_NAME_BACKGROUND) -> None:
        """
        Initialize the CeleryQueueBackend.

        :param celery_app: The Celery application instance.
        :param task_name: The dotted path name of a Celery task function that will receive each message's payload.
        """
        self.app: Any = celery_app
        self.task_name: str = task_name

    def create_queue(self) -> None:
        """
        Creates the queue if needed.

        For Celery, broker structures are auto-created so this is a no-op.
        """
        pass

    def send_message(self, msg_str: str) -> None:
        """
        Enqueue a Celery task with the given message string.
        The Celery worker will automatically pick up the task.

        :param msg_str: The message payload as a JSON string.
        """
        self.app.send_task(self.task_name, args=[msg_str])

    def receive_messages(self, max_messages: int = 1, visibility_timeout: int = 60) -> List[Any]:
        """
        Not used in the Celery push-based model.

        :param max_messages: Not applicable for Celery.
        :param visibility_timeout: Not applicable for Celery.
        :return: An empty list.
        """
        return []

    def delete_message(self, msg: Any) -> None:
        """
        Deleting messages is not relevant in the Celery model.

        :param msg: The message to delete (ignored).
        """
        pass

    def update_message(self, msg: Any, visibility_timeout: int = 60) -> None:
        """
        Updating messages is not relevant in the Celery model.

        :param msg: The message to update (ignored).
        :param visibility_timeout: Not applicable.
        """
        pass
