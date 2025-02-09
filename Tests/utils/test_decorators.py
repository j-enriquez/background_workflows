import unittest
from typing import Type
from background_workflows.utils.decorators import register_activity
from background_workflows.tasks.base_task import BaseTask
from background_workflows.utils.activity_registry import ActivityRegistry

class MockBaseTask(BaseTask):
    def execute_single(self, msg: any) -> None:
        """
        A dummy implementation of execute_single for testing purposes.
        """
        pass

class TestRegisterActivityDecorator(unittest.TestCase):
    def test_decorator_success(self) -> None:
        """
        Test that the register_activity decorator successfully registers a subclass
        of BaseTask in the ActivityRegistry.
        """
        @register_activity("MOCK_TASK")
        class MyTask(MockBaseTask):
            pass

        registered_class: Type[BaseTask] = ActivityRegistry.get("MOCK_TASK")
        self.assertEqual(registered_class, MyTask)

    def test_decorator_wrong_class(self) -> None:
        """
        Test that the register_activity decorator raises a TypeError if applied
        to a class that is not a subclass of BaseTask.
        """
        with self.assertRaises(TypeError):
            @register_activity("WRONG")
            class NotBaseTask:
                pass

if __name__ == "__main__":
    unittest.main()
