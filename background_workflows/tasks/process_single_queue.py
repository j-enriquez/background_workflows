# background_workflows/tasks/process_single_queue.py

import abc
import json
from typing import Any, Dict, Optional

from background_workflows.constants.app_constants import AppConstants
from background_workflows.tasks.base_task import BaseTask
from background_workflows.utils.task_logger import logger


class ProcessSingleQueue(BaseTask):
    """
    A subclass of BaseTask that handles single messages in a straightforward manner.

    Subclasses should implement the `do_work_on_single` method to provide the
    specific logic for processing a single message payload.
    """

    @abc.abstractmethod
    def do_work_on_single(self, msg: Dict[str, Any]) -> str:
        """
        Process a single message payload.

        This abstract method must be implemented by the subclass to define the
        task-specific business logic. The method receives a dictionary (parsed
        from the input JSON) and should return a string (typically a JSON string
        representing the output payload).

        :param msg: The parsed input message as a dictionary.
        :return: A string representing the output payload.
        """
        logger.info(f"[ProcessSingleQueue] Handling single message: {msg}")
        raise NotImplementedError("Subclasses must implement do_work_on_single()")

    def execute_single(self, msg: Any) -> None:
        """
        Public entry point for processing a single queued message.

        This method performs the following steps:
          1. Retrieves the task entity from storage using the resource_id and row_key.
          2. Parses the input payload from JSON into a dictionary.
          3. Invokes the subclass-implemented `do_work_on_single` method to process the payload.
          4. On success, marks the task as complete; on failure, marks it as error.

        :param msg: The raw message, which should have attributes (or keys) for resource_id and row_key
                    as defined in AppConstants.MessageKeys.
        """
        # Extract core fields from the message.
        resource_id: Optional[str] = getattr(msg, AppConstants.MessageKeys.RESOURCE_ID, None)
        row_key: Optional[str] = getattr(msg, AppConstants.MessageKeys.ROW_KEY, None)

        # Initialize the task entity (mark as RUNNING, set start time, etc.).
        entity: Optional[Any] = self._initialize_single(resource_id, row_key)
        if not entity:
            return  # Abort processing if initialization fails.

        unique_key: str = f"{resource_id}||{row_key}"
        try:
            # Parse the input payload (assumed to be a JSON string) into a dictionary.
            input_payload: Dict[str, Any] = json.loads(entity.InputPayload)
            # Execute the task-specific logic.
            output_payload: str = self.do_work_on_single(input_payload)
            # Save the output payload to the entity.
            entity.OutputPayload = output_payload
            # Mark the task as completed.
            self._complete_single(unique_key, entity)
        except Exception as ex:
            logger.exception(f"[BaseTask] single => FAIL => {ex}")
            self._fail_single(unique_key, error_message=str(ex))
