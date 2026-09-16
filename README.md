# Zayn AI

Zayn AI is a local AI assistant built in Python.

The goal is to develop a modular, privacy-focused assistant that can use tools, remember information and eventually assist with software development while keeping important actions under user control.

The project is currently under active development and is also used to learn about local LLMs, APIs, tool calling and AI assistant architecture.

## Current Features

- Local LLM integration with Ollama
- Qwen3 8B
- CLI-based chat
- Conversation history
- Persistent JSON memory
- Function / tool calling
- Task-loops
- Modular separation between assistant logic, LLM communication, memory and tools

## How It Works

```text
User
  ↓
Zayn AI
  ↓
Local LLM
  ↓
Normal response OR tool request
                    ↓
               Python Tool
                    ↓
               Tool Result
                    ↓
                  LLM
                    ↓
             Final Response
```

The LLM decides which tool should be used, while the Python application controls and executes the actual action.

## Roadmap

### Current Development

- [x] Local LLM integration
- [x] Conversation context
- [x] Basic persistent memory
- [x] Calculator tool
- [x] Function calling
- [x] Improve tool routing
- [x] Support multiple tool calls
- [x] Integrate additional tools
- [x] Improve error handling

### Planned

- [x] LLM-controlled memory
- [ ] File reading and writing
- [ ] Code execution
- [ ] Test execution
- [ ] Code analysis
- [ ] Approval system for system modifications
- [ ] Long-term memory
- [ ] Voice input and output
- [ ] Desktop or web interface
- [ ] Git/GitHub integration
- [ ] Self-improvement suggestions with human approval

## Tech Stack

- Python
- Ollama
- Qwen3 8B
- JSON
- HTTP APIs
- Git / GitHub

## Project Structure

```text
zayn-ai/
├── main.py
├── assistant.py
├── llm_client.py
├── memory_manager.py
├── system_prompt.py
│
├── tools/
│   ├── __init__.py
|   ├── tool_definitions.py
│   ├── calculator.py
|   ├── file_system.py
│   └── time_tool.py
│
├── .env.example
├── memory.example.json
├── requirements.txt
├── .gitignore
└── README.md
```

## Running the Project

Requirements:

- Python 3
- Ollama
- Qwen3 8B

Install the model:

```bash
ollama pull qwen3:8b
```

Install Python dependencies:

```bash
pip install -r requirements.txt
```

Run:

```bash
python main.py
```

## Security

Zayn AI is designed so that the LLM does not directly receive unrestricted access to the operating system.

Future actions such as modifying files or executing code should be controlled by dedicated tools and require user approval where appropriate.

## Status

Zayn AI is an experimental personal project and is currently under active development.
