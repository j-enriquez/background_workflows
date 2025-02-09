"""
AppConstants Module

This module centralizes application-wide constants.
"""

import logging
import os
from typing import Final


class AppConstants:
    """
    Centralized container for application-wide constants.
    Constants are grouped by domain in nested classes.
    """

    class TaskStoreFactory:
        class StoreModes:
            AZURE: Final[str] = "azure"
            SQLITE: Final[str] = "sqlite"

        # Environment keys and their default values for store configuration
        STORE_MODE_ENV_KEY: Final[str] = "STORE_MODE"
        STORE_MODE_DEFAULT: Final[str] = StoreModes.SQLITE

        AZURE_STORAGE_CONNECTION_STRING_ENV_KEY: Final[str] = "AZURE_STORAGE_CONNECTION_STRING"
        # Default connection string intended for local Azurite usage.
        AZURE_STORAGE_CONNECTION_STRING_DEFAULT: Final[str] = "DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;QueueEndpoint=http://127.0.0.1:10001/devstoreaccount1;TableEndpoint=http://127.0.0.1:10002/devstoreaccount1;"


        SQLITE_DB_PATH_ENV_KEY: Final[str] = "SQLITE_DB_PATH"
        SQLITE_DB_PATH_DEFAULT: Final[str] = "local_tasks.db"

        ACTIVE_TABLE_NAME_ENV_KEY: Final[str] = "ACTIVE_TABLE_NAME"
        ACTIVE_TABLE_NAME_DEFAULT: Final[str] = "ActiveTasks"
        FINISHED_TABLE_NAME_ENV_KEY: Final[str] = "FINISHED_TABLE_NAME"
        FINISHED_TABLE_NAME_DEFAULT: Final[str] = "FinishedTasks"

        @classmethod
        def get_active_store_mode(cls) -> str:
            """
            Retrieves the store mode from the environment.

            :return: The store mode, either "azure" or "sqlite".
            """
            return os.getenv(cls.STORE_MODE_ENV_KEY, cls.STORE_MODE_DEFAULT)

        @classmethod
        def get_azure_storage_connection_string(cls) -> str:
            """
            Retrieves the Azure storage connection string from the environment.

            :return: The Azure storage connection string.
            """
            return os.getenv(
                cls.AZURE_STORAGE_CONNECTION_STRING_ENV_KEY,
                cls.AZURE_STORAGE_CONNECTION_STRING_DEFAULT,
            )

        @classmethod
        def get_active_table_name(cls) -> str:
            """
            Retrieves the active table name from the environment.

            :return: The active table name.
            """
            return os.getenv(cls.ACTIVE_TABLE_NAME_ENV_KEY, cls.ACTIVE_TABLE_NAME_DEFAULT)

        @classmethod
        def get_finished_table_name(cls) -> str:
            """
            Retrieves the finished table name from the environment.

            :return: The finished table name.
            """
            return os.getenv(cls.FINISHED_TABLE_NAME_ENV_KEY, cls.FINISHED_TABLE_NAME_DEFAULT)

        @classmethod
        def get_sqlite_db_path(cls) -> str:
            """
            Retrieves the SQLite database path from the environment.

            :return: The SQLite database path.
            """
            return os.getenv(cls.SQLITE_DB_PATH_ENV_KEY, cls.SQLITE_DB_PATH_DEFAULT)

    class Logging:
        # Logging configuration constants
        FORMAT: Final[str] = "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
        LEVEL: Final[int] = logging.DEBUG
        LOGGER_NAME: Final[str] = "bgworkflows"

    class TaskStatus:
        CREATED: Final[str] = "CREATED"
        RUNNING: Final[str] = "RUNNING"
        COMPLETED: Final[str] = "COMPLETED"
        ERROR: Final[str] = "ERROR"

    class MainController:
        DEFAULT_MAX_THREADS: Final[int] = 10
        DEFAULT_CPU_THRESHOLD: Final[float] = 0.80
        MAIN_LOOP_SLEEP_SECS: Final[int] = 10
        MAIN_LOOP_CPU_RECHECK_SECS: Final[int] = 2
        RUN_ONCE_MAX_MESSAGES_DEFAULT: Final[int] = 10
        POLL_AND_HANDLE_DEFAULT_MESSAGES: Final[int] = 10
        DEFAULT_VISIBILITY_TIMEOUT: Final[int] = 1800
        VISIBILITY_TIMEOUT_FOR_DEFER: Final[int] = 60

    class ThreadPoolManager:
        DEFAULT_MAX: Final[int] = 10

    class Celery:
        CELERY_BROKER_URL_ENV_KEY: Final[str] = "CELERY_BROKER_URL"
        CELERY_BROKER_URL_DEFAULT: Final[str] = "redis://localhost:6379/0"
        CELERY_BACKEND_URL_ENV_KEY: Final[str] = "CELERY_BACKEND_URL"
        CELERY_BACKEND_URL_DEFAULT: Final[str] = "redis://localhost:6379/1"

        TASK_NAME_BACKGROUND: Final[str] = "background_workflows.tasks.celery_task"

        @classmethod
        def get_celery_broker_url(cls) -> str:
            """
            Retrieves the Celery broker URL from the environment.

            :return: The Celery broker URL.
            """
            return os.getenv(cls.CELERY_BROKER_URL_ENV_KEY, cls.CELERY_BROKER_URL_DEFAULT)

        @classmethod
        def get_celery_backend_url(cls) -> str:
            """
            Retrieves the Celery backend URL from the environment.

            :return: The Celery backend URL.
            """
            return os.getenv(cls.CELERY_BACKEND_URL_ENV_KEY, cls.CELERY_BACKEND_URL_DEFAULT)

    class LocalBlob:
        ROOT_DIR: Final[str] = "local_blobs"

    class ClassNames:
        TASK_ENTITY: Final[str] = "TaskEntity"

    class TaskTableFields:
        PARTITION_KEY: Final[str] = "PartitionKey"
        ROW_KEY: Final[str] = "RowKey"
        TASK_TYPE: Final[str] = "TaskType"
        STATUS: Final[str] = "Status"
        INPUT_PAYLOAD: Final[str] = "InputPayload"
        OUTPUT_PAYLOAD: Final[str] = "OutputPayload"
        START_TIME: Final[str] = "StartTime"
        END_TIME: Final[str] = "EndTime"
        BATCH_ID: Final[str] = "BatchID"
        ERROR_MESSAGE: Final[str] = "ErrorMessage"
        CONTAINER_NAME: Final[str] = "ContainerName"
        BLOB_NAME: Final[str] = "BlobName"

    class MessageKeys:
        CONTENT: Final[str] = "content"
        RESOURCE_ID: Final[str] = "resource_id"
        ROW_KEY: Final[str] = "row_key"
        TASK_TYPE: Final[str] = "task_type"
        PAYLOAD: Final[str] = "payload"
        STORE_MODE: Final[str] = "store_mode"
        ACTIVE_TABLE_NAME: Final[str] = "active_table_name"
        FINISHED_TABLE_NAME: Final[str] = "finished_table_name"
        DATABASE_NAME: Final[str] = "database_name"
