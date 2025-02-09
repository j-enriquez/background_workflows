# background_workflows/storage/schemas/task_schemas.py

from datetime import datetime
from typing import Any, Dict, Optional
from background_workflows.constants.app_constants import AppConstants


class TaskEntity:
    """
    Represents a row in the 'active' and 'finished' storage tables.

    - PartitionKey corresponds to ResourceId.
    - RowKey is the unique identifier for the task.
    - Additional fields include task type, status, payloads, timestamps, and error details.
    """

    def __init__(self, **kwargs: Any) -> None:
        """
        Initialize a TaskEntity instance from keyword arguments.

        The keys in kwargs should match the constants defined in AppConstants.TaskTableFields.

        :param kwargs: Dictionary containing task fields.
        """
        self.PartitionKey: Optional[ str ] = kwargs.get( AppConstants.TaskTableFields.PARTITION_KEY )
        self.RowKey: Optional[ str ] = kwargs.get( AppConstants.TaskTableFields.ROW_KEY )
        # ResourceId is derived from PartitionKey.
        self.ResourceId: Optional[ str ] = self.PartitionKey

        self.TaskType: str = kwargs.get( AppConstants.TaskTableFields.TASK_TYPE, "" )
        self.Status: str = kwargs.get( AppConstants.TaskTableFields.STATUS, AppConstants.TaskStatus.CREATED )
        self.InputPayload: str = kwargs.get( AppConstants.TaskTableFields.INPUT_PAYLOAD, "" )
        self.OutputPayload: str = kwargs.get( AppConstants.TaskTableFields.OUTPUT_PAYLOAD, "" )

        # StartTime and EndTime can be datetime objects or None.
        self.StartTime: Optional[ Any ] = kwargs.get( AppConstants.TaskTableFields.START_TIME, None )
        self.EndTime: Optional[ Any ] = kwargs.get( AppConstants.TaskTableFields.END_TIME, None )

        self.BatchID: str = kwargs.get( AppConstants.TaskTableFields.BATCH_ID, "" )
        self.ErrorMessage: Optional[ str ] = kwargs.get( AppConstants.TaskTableFields.ERROR_MESSAGE, None )

    def to_dict(self) -> Dict[ str, Any ]:
        """
        Convert this TaskEntity to a dictionary suitable for storage upsert operations.

        Uses field names defined in AppConstants.TaskTableFields as dictionary keys.

        :return: A dictionary representation of the task entity.
        """
        return {
            AppConstants.TaskTableFields.PARTITION_KEY: self.ResourceId,
            AppConstants.TaskTableFields.ROW_KEY: self.RowKey,
            AppConstants.TaskTableFields.TASK_TYPE: self.TaskType,
            AppConstants.TaskTableFields.STATUS: self.Status,
            AppConstants.TaskTableFields.INPUT_PAYLOAD: self.InputPayload,
            AppConstants.TaskTableFields.OUTPUT_PAYLOAD: self.OutputPayload,
            AppConstants.TaskTableFields.START_TIME: self.StartTime,
            AppConstants.TaskTableFields.END_TIME: self.EndTime,
            AppConstants.TaskTableFields.BATCH_ID: self.BatchID,
            AppConstants.TaskTableFields.ERROR_MESSAGE: self.ErrorMessage,
        }

    def mark_running(self) -> None:
        """
        Mark the task status as RUNNING.
        """
        self.Status = AppConstants.TaskStatus.RUNNING

    def mark_completed(self) -> None:
        """
        Mark the task status as COMPLETED.
        """
        self.Status = AppConstants.TaskStatus.COMPLETED

    def mark_error(self) -> None:
        """
        Mark the task status as ERROR.
        """
        self.Status = AppConstants.TaskStatus.ERROR

    def __repr__(self) -> str:
        """
        Return a debug string representation of the TaskEntity.

        :return: A string including the ResourceId, RowKey, and current Status.
        """
        return (
            f"<{AppConstants.ClassNames.TASK_ENTITY} "
            f"{AppConstants.TaskTableFields.PARTITION_KEY}={self.ResourceId}, "
            f"{AppConstants.TaskTableFields.ROW_KEY}={self.RowKey}, "
            f"{AppConstants.TaskTableFields.STATUS}={self.Status}>"
        )
