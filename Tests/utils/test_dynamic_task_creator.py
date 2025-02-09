import unittest
from typing import Any
from background_workflows.utils.dynamic_task_creator import DynamicTaskCreator
from background_workflows.utils.activity_registry import ActivityRegistry
from background_workflows.tasks.base_task import BaseTask

class FakeStore:
    """
    A fake task store used solely for testing DynamicTaskCreator.
    """
    pass

class FakeTask(BaseTask):
    def execute_single(self, msg: Any) -> None:
        """
        A dummy implementation of execute_single for testing purposes.
        """
        pass

class Msg:
    """
    A simple message class with a task_type attribute for testing.
    """
    task_type: str = "FAKE_TASK"

class TestDynamicTaskCreator(unittest.TestCase):
    def setUp(self) -> None:
        """
        Set up the test by initializing a fake store and a DynamicTaskCreator instance.
        """
        self.store = FakeStore()
        self.creator = DynamicTaskCreator(self.store)

    def test_create_task_found(self) -> None:
        """
        Test that the DynamicTaskCreator returns an instance of the task class
        when the task_type is registered.
        """
        ActivityRegistry.register("FAKE_TASK", FakeTask)
        task = self.creator.create_task(Msg())
        self.assertIsInstance(task, FakeTask)
        self.assertEqual(task.task_store, self.store)

    def test_create_task_not_found(self) -> None:
        """
        Test that the DynamicTaskCreator returns None if the task_type is not registered.
        """
        class Msg2:
            task_type: str = "UNKNOWN_TASK"

        task = self.creator.create_task(Msg2())
        self.assertIsNone(task)

if __name__ == "__main__":
    unittest.main()
