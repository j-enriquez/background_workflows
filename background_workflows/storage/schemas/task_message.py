# background_workflows/storage/schemas/task_message.py

import json
from typing import Any, Dict, Optional, Union
from background_workflows.constants.app_constants import AppConstants


class TaskMessage:
    """
    Represents a task message extracted from a queue message.

    The initializer expects the input to be either:
      - A dictionary with a key "content" whose value is a JSON string, or
      - An Azure queue message object with a `content` attribute containing a JSON string.

    The JSON string must encode a dictionary that includes the core fields:
      - resource_id
      - row_key
      - task_type
      - payload (optional; defaults to an empty dict)

    It may also include additional fields such as:
      - store_mode
      - active_table_name
      - finished_table_name
      - database_name
    """

    def __init__(self, azure_or_local_msg: Union[ Dict[ str, Any ], Any ]) -> None:
        """
        Initialize a TaskMessage instance by parsing a JSON string from the input message.

        :param azure_or_local_msg: A dict with a "content" key containing a JSON string,
                                   or an object with a 'content' attribute that is a JSON string.
        """
        raw_str: str
        if isinstance( azure_or_local_msg, dict ):
            raw_str = azure_or_local_msg[ AppConstants.MessageKeys.CONTENT ]
        else:
            raw_str = azure_or_local_msg.content

        data: Dict[ str, Any ] = json.loads( raw_str )

        # Core fields
        self.resource_id: Optional[ str ] = data.get( AppConstants.MessageKeys.RESOURCE_ID )
        self.row_key: Optional[ str ] = data.get( AppConstants.MessageKeys.ROW_KEY )
        self.task_type: Optional[ str ] = data.get( AppConstants.MessageKeys.TASK_TYPE )
        self.payload: Dict[ str, Any ] = data.get( AppConstants.MessageKeys.PAYLOAD, {} )

        # Additional fields
        self.store_mode: Optional[ str ] = data.get( AppConstants.MessageKeys.STORE_MODE )
        self.active_table_name: Optional[ str ] = data.get( AppConstants.MessageKeys.ACTIVE_TABLE_NAME )
        self.finished_table_name: Optional[ str ] = data.get( AppConstants.MessageKeys.FINISHED_TABLE_NAME )
        self.database_name: Optional[ str ] = data.get( AppConstants.MessageKeys.DATABASE_NAME )

    def to_json(self) -> str:
        """
        Convert this TaskMessage instance to its JSON string representation.

        This method builds a dictionary mirroring the structure parsed during initialization,
        including both core and additional fields, and then serializes it to JSON.

        :return: A JSON string representing the task message.
        """
        data: Dict[ str, Any ] = {
            AppConstants.MessageKeys.RESOURCE_ID: self.resource_id,
            AppConstants.MessageKeys.ROW_KEY: self.row_key,
            AppConstants.MessageKeys.TASK_TYPE: self.task_type,
            AppConstants.MessageKeys.PAYLOAD: self.payload,
            AppConstants.MessageKeys.STORE_MODE: self.store_mode,
            AppConstants.MessageKeys.ACTIVE_TABLE_NAME: self.active_table_name,
            AppConstants.MessageKeys.FINISHED_TABLE_NAME: self.finished_table_name,
            AppConstants.MessageKeys.DATABASE_NAME: self.database_name,
        }
        return json.dumps( data )
