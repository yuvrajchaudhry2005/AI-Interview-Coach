import os
import tempfile
import unittest

import auth_store


class AuthStoreTests(unittest.TestCase):
    def setUp(self):
        self.database_file = tempfile.NamedTemporaryFile(delete=False)
        self.database_file.close()
        self.original_database_path = auth_store.DATABASE_PATH
        auth_store.DATABASE_PATH = self.database_file.name
        auth_store.init_database()

    def tearDown(self):
        auth_store.DATABASE_PATH = self.original_database_path
        os.unlink(self.database_file.name)

    def test_passwords_and_history_are_user_specific(self):
        first_user = auth_store.create_user("First User", "FIRST@example.com", "password-123")
        second_user = auth_store.create_user("Second User", "second@example.com", "password-456")

        self.assertIsNotNone(auth_store.authenticate_user("first@example.com", "password-123"))
        self.assertIsNone(auth_store.authenticate_user("first@example.com", "wrong-password"))

        auth_store.save_interview_history(first_user["id"], "session-1", "Backend Developer", "Technical", 8.0, 3)
        auth_store.save_interview_history(second_user["id"], "session-2", "Data Scientist", "Mixed", 6.0, 4)

        self.assertEqual(len(auth_store.get_interview_history(first_user["id"])), 1)
        self.assertEqual(auth_store.get_interview_history(first_user["id"])[0]["score"], 8.0)

    def test_delete_user_removes_account_and_history(self):
        user = auth_store.create_user("Delete Me", "delete@example.com", "password-123")
        auth_store.save_interview_history(user["id"], "session-delete", "Tester", "HR", 7.0, 3)

        auth_store.delete_user(user["id"])

        self.assertIsNone(auth_store.authenticate_user("delete@example.com", "password-123"))
        self.assertEqual(auth_store.get_interview_history(user["id"]), [])


if __name__ == "__main__":
    unittest.main()