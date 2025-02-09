import unittest
from typing import Type, Optional
from background_workflows.utils.activity_registry import ActivityRegistry

class MockTask:
    """
    A simple mock task class used for testing the ActivityRegistry.
    """
    pass

class TestActivityRegistry(unittest.TestCase):
    def test_register_and_get(self) -> None:
        """
        Test that a task class can be registered and then retrieved correctly.
        """
        # Register the mock task under the activity type "TEST"
        ActivityRegistry.register("TEST", MockTask)
        # Retrieve the task class using the same activity type
        retrieved_class: Optional[Type] = ActivityRegistry.get("TEST")
        self.assertEqual(retrieved_class, MockTask)

    def test_get_none(self) -> None:
        """
        Test that retrieving a non-existent activity type returns None.
        """
        retrieved_class: Optional[Type] = ActivityRegistry.get("NONEXISTENT")
        self.assertIsNone(retrieved_class)

if __name__ == "__main__":
    unittest.main()
