# Background Workflows – Two-Page Summary

## Overview

The **background_workflows** library provides a pluggable and extensible system for asynchronous task processing in Python. It solves the problem of enqueueing work items (tasks), storing their state, and running them in the background using either:

- Local polling and threading (the “MainController” pattern), or  
- A Celery-based push model.

### Core Use Cases

1. **Queue-based asynchronous tasks** (via Azure Queue, local in-memory queue, or CeleryQueueBackend).  
2. **Storing task states** in Azure Table Storage or SQLite for real-time tracking and historical records.  
3. **Automated concurrency** via a local thread pool (using MainController) or via Celery workers.  
4. **Dynamic registration** of tasks through an activity registry, allowing for flexible task instantiation.

The system is composed of loosely coupled modules:

1. **`constants`** – Centralized configuration (environment variables, default paths, logging settings, etc.).
2. **`controller`** – Orchestrators for task execution (MainController and CeleryController).
3. **`storage`** – Abstractions and implementations for persisting tasks, managing queues, and handling blobs.
4. **`tasks`** – Base task classes (BaseTask, ProcessSingleQueue) and Celery task definitions.
5. **`utils`** – Helper utilities for dynamic task creation, registration, logging, and client workflows.
6. **`scripts`** – Command-line scripts for code inspection, formatting, and environment setup.
7. **Tests** – Comprehensive unit and integration tests covering all aspects (local and cloud-based).

## High-Level Design

1. **Task:** A unit of work defined by a Python class (subclass of `BaseTask`).
2. **TaskStore:** A persistent store for `TaskEntity` records (using either Azure Table Storage or SQLite).
3. **QueueBackend:** An interface for enqueuing and dequeuing task messages.
4. **Controller:** The orchestrator that either polls (MainController) or defers to Celery (CeleryController) for task execution.
5. **DynamicTaskCreator:** Uses the task’s `activity_type` to dynamically instantiate the appropriate task class.

These components can be mixed and matched to suit your environment:
- **Storage:** Azure vs. SQLite.
- **Queue:** Azure Queue, local in-memory queue, or Celery.
- **Concurrency:** Local thread pool or distributed Celery workers.

### Typical Flow

1. A developer calls `WorkflowClient.start_activity(...)` with an `activity_type` and input parameters.
2. The client writes a new “active” `TaskEntity` to the task store and enqueues a corresponding JSON message.
3. The controller (or Celery) consumes the message, uses the DynamicTaskCreator to instantiate the correct task class, and executes the logic.
4. Upon completion or failure, the task is updated and moved to the finished store.

## Environment & Configuration

- **STORE_MODE:** "azure" or "sqlite" to determine the task store type.
- **Azure:** Uses `AZURE_STORAGE_CONNECTION_STRING` (and other endpoints).
- **SQLite:** Uses `SQLITE_DB_PATH`.
- **Celery:** Configured via `CELERY_BROKER_URL` and `CELERY_BACKEND_URL`.
- Logging is configured via `AppConstants.Logging`.

### Benefits

- **Modular:** Easily switch between storage and queue implementations.
- **Scalable:** Run locally with thread pools or scale out using Celery.
- **Testable:** In-memory queues and SQLite enable comprehensive local integration testing.

In summary, **background_workflows** provides a flexible, component-driven system for handling background tasks in Python, suitable for both local development and cloud-scale production scenarios.
