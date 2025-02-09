# Overall Framework Mermaid Diagram

```mermaid
flowchart TD
    A[WorkflowClient] -->|start_activity| B[QueueBackend]
    A --> D[TaskStore]

    B -->|send_message| Q[(Queue)]
    Q -->|receive_messages| C[MainController<br/>or CeleryController]

    C -->|fetch TaskEntity| D
    C -->|create Task object<br/> via DynamicTaskCreator| E[BaseTask<br/>ProcessSingleQueue etc.]

    E -->|mark RUNNING, set StartTime| D
    E -->|task executes user logic| E
    E -->|mark COMPLETED, move to finished| D

    classDef storeFill fill:#f9f9f9,stroke:#999,stroke-width:1px
    classDef queueFill fill:#d1f1ff,stroke:#999,stroke-width:1px

    class D storeFill
    class Q queueFill
    style C fill:#f0fff0,stroke:#999,stroke-width:1px,stroke-dasharray: 5 5

```


### Explanation

- **WorkflowClient:**  
  Initiates task creation by calling `start_activity`, which interacts with both the QueueBackend and TaskStore.

- **QueueBackend:**  
  Handles sending messages (to a queue) that are then received by the controller (either `MainController` or `CeleryController`).

- **TaskStore:**  
  Stores task entities, including both active and finished tasks.

- **MainController / CeleryController:**  
  Receives messages from the queue.  
  - `MainController` polls, retrieves the task entity from the store, and uses `DynamicTaskCreator` to create the appropriate task instance (a subclass of `BaseTask` such as `ProcessSingleQueue`).  
  - `CeleryController` delegates task execution to Celery workers.

- **BaseTask / ProcessSingleQueue:**  
  Implements task-specific logic (e.g., marking tasks as RUNNING, COMPLETED, or ERROR) and updates the task store accordingly.

The diagram uses custom class styles to visually distinguish the TaskStore (`storeFill`) and the Queue (`queueFill`), while the Controller is highlighted with a dashed outline.

This diagram provides an overall view of the task processing flow within the system.
