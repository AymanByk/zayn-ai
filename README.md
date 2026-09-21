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
- Read-only file-system access
- Directory listing
- File search by name, extension and content
- Project-scoped file access
- Path traversal protection
- File size limits
- Active project context

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
- [x] Long-term memory
- [x] LLM-controlled memory
- [x] Calculator tool
- [x] Time tool
- [x] Function calling
- [x] Improve tool routing
- [x] Support multiple tool calls
- [x] Integrate additional tools
- [x] Improve error handling
- [x] File reading
- [x] Directory listing
- [x] File search by name, extension and content
- [x] Project-scoped file access
- [x] Project context
- [x] Path traversal protection
- [x] File size limits

### Planned

- [ ] Multi-file code analysis
- [ ] File writing and editing
- [ ] Approval system for file and system modifications
- [ ] Shell command execution
- [ ] Code execution
- [ ] Test execution
- [ ] Execution result analysis
- [ ] Additional security and stability hardening
- [ ] Git/GitHub integration
- [ ] Self-improvement suggestions with human approval
- [ ] Voice input and output
- [ ] Desktop or web interface

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
|   ├── project_context.py
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
ollama pull qwen3.5:9b
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

Zayn AI follows a tool-based permission model. The language model does not directly access the operating system.

Current file-system access is read-only and restricted to the active project root.

Implemented safeguards include:

- Project-root access restrictions
- Path traversal protection
- File size limits
- Ignored directories such as `.git`, `.venv`, `node_modules` and `__pycache__`
- No file modification or command execution capabilities yet

Future write, delete and shell operations will require dedicated tools and an approval system.

## Status

Zayn AI is an experimental personal project and is currently under active development.
