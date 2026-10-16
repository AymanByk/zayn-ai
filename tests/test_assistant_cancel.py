"""Integration tests for cancellation in Assistant.chat(), without Ollama or file writes."""
import json
import sys
import types
import unittest
from unittest.mock import Mock, patch
from typing import cast

if "system_prompt" not in sys.modules:
    system_prompt = types.ModuleType("system_prompt")
    setattr(system_prompt, "SYSTEM_PROMPT", "Test-only system prompt")
    sys.modules["system_prompt"] = system_prompt

from assistant import Assistant


def tool(name, **arguments):
    return {"function": {"name": name, "arguments": arguments}}


class TestAssistantCancel(unittest.TestCase):
    def setUp(self):
        # Skip __init__: avoid Ollama, filesystem and persistent memory dependencies.
        self.assistant = Assistant.__new__(Assistant)
        self.assistant.messages = [{"role": "system", "content": "Test"}]
        self.assistant.tools = [{"type": "function", "function": {"name": "test"}}]
        self.assistant.max_tool_iterations = 20
        self.assistant.llm = Mock()
        # Pylance sees LLMClient.chat as a method, but the test uses a Mock.
        self.mock_chat = cast(Mock, self.assistant.llm.chat)

    def test_rejection_skips_remaining_calls_and_gets_ai_response_without_tools(self):
        calls = [tool("create_file", path="a.txt"), tool("replace_text", path="b.txt")]
        final = {"role": "assistant", "content": "I did not make that change."}
        self.mock_chat.side_effect = [
            {"role": "assistant", "content": "", "tool_calls": calls},
            final,
        ]
        self.assistant.execute_tool = Mock(return_value={
            "success": False, "cancelled": True, "error": "Cancelled by user."
        })
        with patch("builtins.input", return_value="Change my files"):
            self.assertTrue(self.assistant.chat())

        self.assertEqual(self.assistant.execute_tool.call_count, 1)
        self.assertEqual(self.mock_chat.call_count, 2)
        args, _ = self.mock_chat.call_args
        self.assertEqual(args[1], [])
        self.assertIn("rejected", args[0][-1]["content"])
        results = [json.loads(m["content"]) for m in self.assistant.messages if m["role"] == "tool"]
        self.assertEqual(len(results), 2)
        self.assertTrue(all(r["cancelled"] for r in results))
        self.assertEqual(self.assistant.messages[-1], final)

    def test_successful_first_call_is_not_undone_when_second_rejected(self):
        calls = [tool("read_file", path="a.txt"), tool("create_file", path="b.txt")]
        self.mock_chat.side_effect = [
            {"role": "assistant", "content": "", "tool_calls": calls},
            {"role": "assistant", "content": "The second action was cancelled."},
        ]
        self.assistant.execute_tool = Mock(side_effect=[
            {"success": True, "result": "read"},
            {"success": False, "cancelled": True, "error": "Cancelled by user."},
        ])
        with patch("builtins.input", return_value="Do both"):
            self.assistant.chat()
        self.assertEqual(self.assistant.execute_tool.call_count, 2)
        results = [json.loads(m["content"]) for m in self.assistant.messages if m["role"] == "tool"]
        self.assertTrue(results[0]["success"])
        self.assertTrue(results[1]["cancelled"])
        self.assertEqual(self.mock_chat.call_args.args[1], [])

    def test_approval_uses_normal_tools_and_continues(self):
        calls = [tool("create_file", path="a.txt")]
        self.mock_chat.side_effect = [
            {"role": "assistant", "content": "", "tool_calls": calls},
            {"role": "assistant", "content": "File created."},
        ]
        self.assistant.execute_tool = Mock(return_value={"success": True})
        with patch("builtins.input", return_value="Create file"):
            self.assertTrue(self.assistant.chat())
        self.assertEqual(self.assistant.execute_tool.call_count, 1)
        self.assertEqual(self.mock_chat.call_args.args[1], self.assistant.tools)

    def test_unexpected_final_tool_calls_are_not_saved_or_executed(self):
        self.mock_chat.side_effect = [
            {"role": "assistant", "content": "", "tool_calls": [tool("create_file", path="a.txt")]},
            {"role": "assistant", "content": "", "tool_calls": [tool("delete_file", path="b.txt")]},
        ]
        self.assistant.execute_tool = Mock(return_value={"success": False, "cancelled": True})
        with patch("builtins.input", return_value="Create file"):
            self.assertTrue(self.assistant.chat())
        self.assertEqual(self.assistant.execute_tool.call_count, 1)
        self.assertEqual(self.mock_chat.call_count, 2)
        self.assertNotIn("tool_calls", self.assistant.messages[-1])

    def test_final_llm_failure_does_not_restart_tools(self):
        self.mock_chat.side_effect = [
            {"role": "assistant", "content": "", "tool_calls": [tool("delete_file", path="a.txt")]},
            {"error": "Could not connect to Ollama."},
        ]
        self.assistant.execute_tool = Mock(return_value={"success": False, "cancelled": True})
        with patch("builtins.input", return_value="Delete file"):
            self.assertTrue(self.assistant.chat())
        self.assertEqual(self.mock_chat.call_count, 2)
        self.assertEqual(self.assistant.execute_tool.call_count, 1)


if __name__ == "__main__":
    unittest.main()
