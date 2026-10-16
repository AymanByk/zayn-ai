import unittest

from tools.tool_policy import ToolPolicy


class TestToolPolicy(unittest.TestCase):

    def setUp(self):
        self.policy = ToolPolicy()

    def test_auto_tools(self):
        # All current automatic tools must be allowed without confirmation.
        for tool_name in self.policy.AUTO:
            with self.subTest(tool=tool_name):
                self.assertEqual(self.policy.get_permission(tool_name), "auto")
                self.assertFalse(self.policy.requires_approval(tool_name))

    def test_approval_tools(self):
        # These tools require approval, including future write_file support.
        for tool_name in ("create_file", "replace_text", "delete_file", "write_file"):
            with self.subTest(tool=tool_name):
                self.assertIn(tool_name, self.policy.APPROVAL)
                self.assertEqual(self.policy.get_permission(tool_name), "approval")
                self.assertTrue(self.policy.requires_approval(tool_name))

    def test_unknown_tool(self):
        for tool_name in ("unknown_tool", "execute_code", ""):
            with self.subTest(tool=tool_name):
                self.assertEqual(self.policy.get_permission(tool_name), "deny")
                self.assertFalse(self.policy.requires_approval(tool_name))

    def test_no_overlap_between_auto_and_approval(self):
        # A tool must not belong to both permission groups.
        self.assertFalse(self.policy.AUTO & self.policy.APPROVAL)


if __name__ == "__main__":
    unittest.main()
