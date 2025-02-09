# Background Workflows

A pluggable framework for managing background tasks in Python. Supports both local task execution with threading and distributed task execution using Celery.

## Features

- Task orchestration with support for Azure Table Storage or SQLite for task persistence.
- Queue management for local in-memory queues or Celery for distributed task processing.
- Dynamic task creation and registration for extensible workflow management.

## Additional Documentation

For more detailed documentation, please refer to the following sections:
- **Summary**: [summary.md](docs/summary.md) – A brief summary of the framework and its key components.
- **Controller Documentation**: [controller.md](docs/controller.md) – Detailed information about the controller components and how they work.
- **Storage Documentation**: [storage.md](docs/storage.md) – Information on task storage options, including Azure and SQLite.
- **Task Documentation**: [tasks.md](docs/tasks.md) – Overview of task management, including how to define and run tasks.
- **Utils Documentation**: [utils.md](docs/utils.md) – A guide to the utility functions and classes used in the framework.
- **Overall Framework Diagram**: [overal_diagram.md](docs/overal_diagram.md) – A high-level diagram illustrating the components and their relationships.

## Installation

You can install the `background_workflows` library via pip:

```bash
pip install background_workflows
```

## Usage

### 1. Initialize Task Store and Queue Backend

```python
from background_workflows.storage.tables.task_store_factory import TaskStoreFactory
from background_workflows.storage.queue.local_queue_backend import LocalQueueBackend

# Initialize task store and queue backend
factory = TaskStoreFactory(store_mode="sqlite")
task_store = factory.get_task_store()
queue_backend = LocalQueueBackend()
```

### 2. Start a Background Activity

```python
from background_workflows.utils.workflow_client import WorkflowClient

workflow_client = WorkflowClient(task_store, queue_backend)
workflow_client.start_activity("MY_CUSTOM_TASK", resource_id="1234", payload={"data": "value"})
```

### 3. Monitor Task Status

```python
status = workflow_client.get_status(row_key="unique-row-id", resource_id="1234")
print(f"Task Status: {status}")
```

## Configuration

### Environment Variables

To configure the library, set the following environment variables:

- **`STORE_MODE`**: Choose between `"azure"` or `"sqlite"` for task storage.
- **`AZURE_STORAGE_CONNECTION_STRING`**: Required for Azure storage mode.
- **`SQLITE_DB_PATH`**: Path to the SQLite database (default is `local_tasks.db`).
- **`CELERY_BROKER_URL`**: The URL for the Celery message broker (e.g., Redis).
- **`CELERY_BACKEND_URL`**: The URL for the Celery result backend (e.g., Redis).

Example:

```bash
export STORE_MODE=azure
export AZURE_STORAGE_CONNECTION_STRING="your_connection_string_here"
```

## Controllers

The framework provides two key controllers for managing task execution: 

### 1. **MainController**
- **Purpose**: Polls queues and executes tasks in a local thread pool.
- **Configuration**: Can be configured to use a specific number of threads and CPU usage threshold.
- **Usage**:

```python
from background_workflows.controller.main.main_controller import MainController

controller = MainController(task_store, queue_backend)
controller.run()  # Starts the continuous polling and task execution loop
```

### 1. **CeleryController**
- **Purpose**: Delegates task processing to Celery workers, removing the need for local polling.
- **Configuration**: Requires a Celery setup and message broker.
- **Usage**:

```python
from background_workflows.controller.celery.celery_controller import CeleryController

controller = CeleryController(task_store, celery_queue_backend)
controller.run_once()  # Executes a single pass of task handling
```

## Contributing

We welcome contributions to the **background_workflows** library! To contribute:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Make your changes.
4. Run tests to ensure everything works.
5. Submit a pull request with a description of the changes you’ve made.

### Running Tests

To run the tests, you can use `pytest`:

```bash
pytest tests/
```


## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
