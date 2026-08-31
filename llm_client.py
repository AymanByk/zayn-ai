import os
import requests
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
            "stream": False
        }

        response = requests.post(
            self.url,
            json=data,
            timeout=60
        )

        response.raise_for_status()

        result = response.json()

        return result["message"]