import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()


class LLMClient:
    def __init__(self):
        self.model = os.getenv("OLLAMA_MODEL", "qwen3:8b")
        self.url = os.getenv(
            "OLLAMA_URL",
            "http://localhost:11434/api/chat"
        )

        self.timeout = 60

    def chat(self, messages: list, tools: list) -> dict:
        data = {
            "model": self.model,
            "messages": messages,
            "tools": tools,
            "stream": True
        }

        try:
            response = requests.post(
                self.url,
                json=data,
                timeout=self.timeout,
                stream=True
            )

            response.raise_for_status()

            full_content = ""
            tool_calls = []

            for line in response.iter_lines():
                if not line:
                    continue

                try:
                    chunk = json.loads(line)

                except json.JSONDecodeError:
                    return {
                        "error": "Ollama returned invalid JSON."
                    }

                chunk_message = chunk.get("message")

                if not isinstance(chunk_message, dict):
                    continue

                # Normal streamed text
                content = chunk_message.get("content", "")

                if content:
                    print(content, end="", flush=True)
                    full_content += content

                # Tool calls
                current_tool_calls = chunk_message.get("tool_calls")

                if current_tool_calls:
                    tool_calls.extend(current_tool_calls)

            message = {
                "role": "assistant",
                "content": full_content
            }

            if tool_calls:
                message["tool_calls"] = tool_calls

            # Completely empty response
            if not full_content and not tool_calls:
                return {
                    "error": "Ollama returned an empty response."
                }

            return message

        except requests.exceptions.ConnectionError:
            return {
                "error": "Could not connect to Ollama."
            }

        except requests.exceptions.Timeout:
            return {
                "error": "The request to Ollama timed out."
            }

        except requests.exceptions.HTTPError as e:
            return {
                "error": f"Ollama returned an HTTP error: {e}"
            }

        except requests.exceptions.RequestException as e:
            return {
                "error": f"Request failed: {e}"
            }