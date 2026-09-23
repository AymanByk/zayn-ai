import os
import json
from typing import Any
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
            "stream": True,
            "options": {
                "num_ctx": 16384
            }
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
            full_thinking = ""

            for line in response.iter_lines():

                if not line:
                    continue

                try:
                    chunk = json.loads(line)

                except json.JSONDecodeError:
                    return {
                        "error": "Ollama returned invalid JSON."
                    }

                # Response must be a dictionary
                if not isinstance(chunk, dict):
                    return {
                        "error": "Ollama returned an invalid response format."
                    }

                # Error directly returned by Ollama
                if chunk.get("error"):
                    return {
                        "error": f"Ollama error: {chunk['error']}"
                    }

                chunk_message = chunk.get("message")

                # Does stream chunks contain a message?
                if chunk_message is None:
                    continue

                if not isinstance(chunk_message, dict):
                    return {
                        "error": "Invalid message format from Ollama."
                    }

                thinking = chunk_message.get("thinking", "")
                if isinstance(thinking, str):
                    full_thinking += thinking

                # Normal streamed text
                content = chunk_message.get("content", "")

                if isinstance(content, str) and content:
                    print(content, end="", flush=True)
                    full_content += content

                # Tool calls
                current_tool_calls = chunk_message.get("tool_calls")

                if current_tool_calls:

                    if not isinstance(current_tool_calls, list):
                        return {
                            "error": "Ollama returned invalid tool calls."
                        }

                    tool_calls.extend(current_tool_calls)

            # format
            if full_content:
                print()

            # message can contain strings AND lists
            message: dict[str, Any] = {
                "role": "assistant",
                "content": full_content
            }

            if tool_calls:
                message["tool_calls"] = tool_calls

            if full_thinking:
                message["thinking"] = full_thinking
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

        except Exception as e:
            return {
                "error": f"Unexpected LLM client error: {e}"
            }