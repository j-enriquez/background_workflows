# background_workflows/tasks/celery/celery_task.py

from celery import shared_task
from typing import Any, Dict
import logging

from background_workflows.constants.app_constants import AppConstants
from background_workflows.storage.schemas.task_message import TaskMessage
from background_workflows.storage.tables.task_store_factory import TaskStoreFactory
from background_workflows.utils.dynamic_task_creator import DynamicTaskCreator

logger = logging.getLogger( __name__ )


@shared_task( name = AppConstants.Celery.TASK_NAME_BACKGROUND )
def celery_task_handler(msg_str: str) -> None:
    """
    Celery worker entry point.

    This function receives a JSON string (msg_str) representing a task message,
    wraps it to simulate a standard queue message, and then processes it using
    dynamic task creation. The processing steps are as follows:

      1. Wrap the JSON string in a dictionary with the key "content" and parse
         it into a TaskMessage instance.
      2. Instantiate a TaskStoreFactory using configuration from the TaskMessage.
      3. Obtain the underlying task store (either Azure or SQLite) via the factory.
      4. Use DynamicTaskCreator to instantiate the corresponding task object.
      5. If a valid task object is created, execute it; otherwise, log an error.

    :param msg_str: A JSON string representing the task message.
    """
    try:
        # Wrap the message to mimic a standard queue message structure.
        wrapped: Dict[ str, Any ] = {"content": msg_str}
        tmsg: TaskMessage = TaskMessage( wrapped )

        # Instantiate the factory using configuration extracted from the TaskMessage.
        factory: TaskStoreFactory = TaskStoreFactory(
            store_mode = tmsg.store_mode,
            active_table_name = tmsg.active_table_name,
            finished_table_name = tmsg.finished_table_name,
            sqlite_db_path = tmsg.database_name,
        )
        # Obtain the task store (Azure or SQLite, depending on configuration).
        store = factory.get_task_store()

        # Dynamically create the task instance.
        creator: DynamicTaskCreator = DynamicTaskCreator( store )
        task_obj = creator.create_task( tmsg )

        if not task_obj:
            logger.error( f"Unknown task type: {tmsg.task_type}" )
            return

        # Execute the task.
        task_obj.execute_single( tmsg )

    except Exception as e:
        logger.exception( f"Exception occurred in celery_task_handler: {e}" )
