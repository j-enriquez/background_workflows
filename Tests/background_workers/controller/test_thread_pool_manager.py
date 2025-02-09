import unittest
from typing import Any
from background_workflows.controller.main.thread_pool_manager import ThreadPoolManager

class TestThreadPoolManager(unittest.TestCase):
    def test_init(self) -> None:
        """
        Test that the ThreadPoolManager initializes with the correct max_threads value.
        """
        tpm: ThreadPoolManager = ThreadPoolManager(max_threads=5)
        self.assertEqual(tpm.max_threads, 5)

    def test_cpu_usage(self) -> None:
        """
        Test that the get_cpu_usage method returns a value between 0.0 and 1.0.
        """
        tpm: ThreadPoolManager = ThreadPoolManager()
        usage: float = tpm.get_cpu_usage()
        self.assertGreaterEqual(usage, 0.0, "CPU usage should be at least 0.0")
        self.assertLessEqual(usage, 1.0, "CPU usage should be at most 1.0")

    def test_current_thread_count(self) -> None:
        """
        Test that the current_thread_count returns 0 when no tasks have been submitted.
        """
        tpm: ThreadPoolManager = ThreadPoolManager()
        count: int = tpm.current_thread_count()
        self.assertEqual(count, 0, "There should be no active threads initially.")

if __name__ == "__main__":
    unittest.main()
