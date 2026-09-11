import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()


class LLMClient:
    def __init__(self):
        self.model = os.getenv("OLLAMA_MODEL", "qwen3:8b")
        self.url = os.getenv("OLLAMA_URL",
            "http://localhost:11434/api/chat"
        )
    def chat(self, messages: list, tools: list):
        data = {
            "model": self.model,
            "messages": messages,
            "tools": tools,
            "stream": True
        }

        response = requests.post(
            self.url,
            json=data,
            timeout=60,
            stream=True
        )

        response.raise_for_status()

        full_content = ""
        tool_calls = []

        for line in response.iter_lines():
            if not line:
                continue

            chunk = json.loads(line)
            chunk_message = chunk.get("message", {})

            # Normaler Text
            content = chunk_message.get("content", "")

            if content:
                print(content, end="", flush=True)
                full_content += content

            # Tool Calls
            if chunk_message.get("tool_calls"):
                tool_calls.extend(chunk_message["tool_calls"])

        message = {
            "role": "assistant",
            "content": full_content
        }

        if tool_calls:
            message["tool_calls"] = tool_calls
        else:
            print()

        return message