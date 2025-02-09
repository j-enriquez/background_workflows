# background_workflows/utils/activity_registry.py

from typing import Type, Optional, Dict, TypeVar
from background_workflows.tasks.base_task import BaseTask

# Define a type variable for task classes (subclasses of BaseTask)
T = TypeVar("T", bound=BaseTask)

class ActivityRegistry:
    """
    Global registry mapping activity types (strings) to task classes (subclasses of BaseTask).

    This registry allows for the dynamic instantiation of tasks based on their activity type.
    """

    _registry: Dict[str, Type[BaseTask]] = {}

    @classmethod
    def register(cls, activity_type: str, task_class: Type[T]) -> None:
        """
        Registers a task class under the provided activity_type.

        :param activity_type: A string representing the activity type.
        :param task_class: A task class (subclass of BaseTask) to register.
        """
        cls._registry[activity_type] = task_class

    @classmethod
    def get(cls, activity_type: str) -> Optional[Type[BaseTask]]:
        """
        Retrieves the registered task class for the given activity_type.

        :param activity_type: A string representing the activity type.
        :return: The task class registered under the activity_type, or None if not found.
        """
        return cls._registry.get(activity_type)
