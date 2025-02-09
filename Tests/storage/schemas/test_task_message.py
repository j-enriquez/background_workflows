import unittest
import json
from background_workflows.storage.schemas.task_message import TaskMessage
from background_workflows.constants.app_constants import AppConstants


class TestTaskMessage(unittest.TestCase):
    def test_local_dict_msg(self):
        """
        Basic test to ensure TaskMessage correctly parses the minimal required fields.
        """
        local_msg = {
            "id": 123,
            "pop_receipt": "abc",
            "content": '{"resource_id":"res","row_key":"123","task_type":"T","payload":{"foo":"bar"}}',
        }
        tmsg = TaskMessage(local_msg)
        self.assertEqual(tmsg.resource_id, "res")
        self.assertEqual(tmsg.row_key, "123")
        self.assertEqual(tmsg.task_type, "T")
        self.assertIn("foo", tmsg.payload)

        # Confirm additional fields default to None if not provided
        self.assertIsNone(tmsg.store_mode)
        self.assertIsNone(tmsg.active_table_name)
        self.assertIsNone(tmsg.finished_table_name)
        self.assertIsNone(tmsg.database_name)

    def test_store_mode_fields(self):
        """
        Test that TaskMessage correctly parses the extended fields like store_mode,
        active_table_name, etc. when included in the JSON.
        """
        msg_json = json.dumps(
            {
                AppConstants.MessageKeys.RESOURCE_ID: "res",
                AppConstants.MessageKeys.ROW_KEY: "456",
                AppConstants.MessageKeys.TASK_TYPE: "SAMPLE",
                AppConstants.MessageKeys.PAYLOAD: {"hello": "world"},
                AppConstants.MessageKeys.STORE_MODE: "sqlite",
                AppConstants.MessageKeys.ACTIVE_TABLE_NAME: "myActiveTable",
                AppConstants.MessageKeys.FINISHED_TABLE_NAME: "myFinishedTable",
                AppConstants.MessageKeys.DATABASE_NAME: "myDatabase.db",
            }
        )
        local_msg = {"content": msg_json}

        tmsg = TaskMessage(local_msg)
        self.assertEqual(tmsg.resource_id, "res")
        self.assertEqual(tmsg.row_key, "456")
        self.assertEqual(tmsg.task_type, "SAMPLE")
        self.assertDictEqual(tmsg.payload, {"hello": "world"})

        self.assertEqual(tmsg.store_mode, "sqlite")
        self.assertEqual(tmsg.active_table_name, "myActiveTable")
        self.assertEqual(tmsg.finished_table_name, "myFinishedTable")
        self.assertEqual(tmsg.database_name, "myDatabase.db")

    def test_to_json(self):
        """
        Verify that to_json() includes all relevant fields.
        """
        local_msg = {
            "content": '{"resource_id":"res","row_key":"123","task_type":"T","payload":{}}'
        }
        tmsg = TaskMessage(local_msg)
        json_str = tmsg.to_json()

        # Check core fields
        self.assertIn('"resource_id": "res"', json_str)
        self.assertIn('"row_key": "123"', json_str)
        self.assertIn('"task_type": "T"', json_str)
        self.assertIn('"payload": {}', json_str)

        # Now give it some extended fields
        tmsg.store_mode = "azure"
        tmsg.active_table_name = "MyActive"
        tmsg.finished_table_name = "MyFinished"
        tmsg.database_name = "test.db"
        new_json = tmsg.to_json()
        self.assertIn('"store_mode": "azure"', new_json)
        self.assertIn('"active_table_name": "MyActive"', new_json)
        self.assertIn('"finished_table_name": "MyFinished"', new_json)
        self.assertIn('"database_name": "test.db"', new_json)


if __name__ == "__main__":
    unittest.main()
