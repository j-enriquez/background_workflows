# background_workflows/utils/decorators.py

from typing import Callable, Type, TypeVar
from background_workflows.utils.activity_registry import ActivityRegistry
from background_workflows.tasks.base_task import BaseTask

# Define a type variable for classes that are subclasses of BaseTask.
T = TypeVar('T', bound=BaseTask)

def register_activity(activity_type: str) -> Callable[[Type[T]], Type[T]]:
    """
    Decorator to auto-register a BaseTask subclass under the provided activity_type.

    This decorator automatically registers the decorated class with the global ActivityRegistry.
    Usage:
        @register_activity("MY_TASK")
        class MyTask(BaseTask):
            ...

    :param activity_type: A string representing the activity type for which the task is registered.
    :return: A decorator function that registers the task class and returns it.
    """
    def decorator(cls: Type[T]) -> Type[T]:
        if not issubclass(cls, BaseTask):
            raise TypeError("@register_activity can only be used on BaseTask subclasses")
        ActivityRegistry.register(activity_type, cls)
        return cls
    return decorator
