# `controller` Component Documentation

## Purpose

The controller layer is responsible for coordinating the retrieval of tasks from queues and executing them. Controllers act as the orchestrator between the storage (task store) and the messaging layer (queue backend), ensuring tasks are processed according to the desired strategy.

## Components

### 1. BaseController (abstract)

- **Responsibilities:**
  - Defines the core interface for controllers.
  - Declares abstract methods `run()` and `run_once()` which must be implemented by subclasses.
  - Maintains references to a task store (`ITaskStore`) and a queue backend (`IQueueBackend`).

### 2. MainController

- **Responsibilities:**
  - Implements a **polling loop** for processing tasks:
    1. Waits until CPU usage is below a predefined threshold.
    2. Retrieves a batch of messages from the queue.
    3. For each message, uses `DynamicTaskCreator` to determine and instantiate the correct task class.
    4. Executes tasks in parallel using a `ThreadPoolManager`.
  - Moves tasks from the "active" store to the "finished" store upon successful completion or failure.

### 3. CeleryController

- **Responsibilities:**
  - Acts as a no-op controller when using Celery.
  - Delegates task execution entirely to Celery workers, so no local polling or thread management is required.

## Key Points

- **MainController:**  
  Used when running in a single-process mode that actively polls for tasks. It manages its own concurrency through a thread pool.
  
- **CeleryController:**  
  Used in distributed or asynchronous environments where Celery workers handle task execution, eliminating the need for local polling loops.

## Mermaid Diagram

The diagram below illustrates the relationships between the different controller classes and their supporting components:

```mermaid
flowchart TB
    subgraph Controller
      A[BaseController<br> abstract]
      B[MainController]
      C[CeleryController]
    end

    A --> B
    A --> C

    B -->|manages| T[ThreadPoolManager]
    B -->|creates tasks| DC[DynamicTaskCreator]

    style A fill:#ffeedb,stroke:#999,stroke-width:1px
    style B fill:#fff9c0,stroke:#999,stroke-width:1px
    style C fill:#fff9c0,stroke:#999,stroke-width:1px
    style T fill:#c0fff9,stroke:#999,stroke-width:1px
    style DC fill:#c0fff9,stroke:#999,stroke-width:1px
