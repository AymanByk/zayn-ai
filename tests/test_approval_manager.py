import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from approval_manager import ApprovalManager


class TestApprovalManager(unittest.TestCase):

    def setUp(self):
        self.approval = ApprovalManager()

    def simulate_input(self, characters, question="Test?"):
        # Simulate keyboard input without waiting for a human.
        output = io.StringIO()
        with patch.object(self.approval, "get_char", side_effect=characters):
            with redirect_stdout(output):
                result = self.approval.request_approval(question)
        return result, output.getvalue()

    def test_accept_yes(self):
        for characters in (["y", "\r"], ["y", "e", "s", "\r"], ["Y", "\r"]):
            with self.subTest(characters=characters):
                result, _ = self.simulate_input(characters)
                self.assertTrue(result)

    def test_reject_no(self):
        for characters in (["n", "\r"], ["n", "o", "\r"]):
            with self.subTest(characters=characters):
                result, _ = self.simulate_input(characters)
                self.assertFalse(result)

    def test_reject_escape(self):
        result, _ = self.simulate_input(["\x1b"])
        self.assertFalse(result)

    def test_reject_enter(self):
        for key in ("\r", "\n"):
            with self.subTest(key=repr(key)):
                result, _ = self.simulate_input([key])
                self.assertFalse(result)

    def test_invalid_answer_can_be_corrected(self):
        result, output = self.simulate_input(["x", "\r", "y", "\r"])
        self.assertTrue(result)
        self.assertIn("Type yes to approve or no to cancel", output)

    def test_backspace(self):
        # Type 'n', erase it, then confirm with 'y'.
        result, _ = self.simulate_input(["n", "\x08", "y", "\r"])
        self.assertTrue(result)

    def test_text_replacement_uses_confirmation(self):
        with patch.object(self.approval, "request_approval", return_value=False) as mock_approval:
            with redirect_stdout(io.StringIO()):
                result = self.approval.text_replacement("example.py", "old", "new")
        self.assertFalse(result)
        mock_approval.assert_called_once_with("Apply this change?")

    def test_file_creation_uses_confirmation(self):
        with patch.object(self.approval, "request_approval", return_value=True) as mock_approval:
            with redirect_stdout(io.StringIO()):
                result = self.approval.file_creation("example.txt", "hello", "utf-8", b"hello")
        self.assertTrue(result)
        mock_approval.assert_called_once_with("Create file?")

    def test_file_deletion_uses_confirmation(self):
        with patch.object(self.approval, "request_approval", return_value=False) as mock_approval:
            with redirect_stdout(io.StringIO()):
                result = self.approval.file_deletion("example.txt", 5)
        self.assertFalse(result)
        mock_approval.assert_called_once_with("Delete this file?")


if __name__ == "__main__":
    unittest.main()
