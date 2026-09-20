class ToolDefinitions:
    def __init__(self) -> None:
        swap_value_tool = {
            "type": "function",
            "function": {
                "name": "swap_value",
                "description": "Replaces the value of an existing memory key with a new value.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "key": {
                            "type": "string"
                        },
                        "value": {
                            "type": "string"
                        }
                    },
                    "required": ["key", "value"]
                }
            }
        }
        time_tool={
                    "type": "function",
                    "function": {
                        "name": "time",
                        "description": "Returns the current Date including year month day hour minute and seconds",
                        "parameters": {
                            "type": "object",
                            "properties": {},
                            "required": []
                        }
                    }
                }
        calculator_tool = {
            "type": "function",
            "function": {
                "name": "calculator",
                "description": "Performs arithmetic calculations such as addition, subtraction, multiplication and division",
                "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["add", "subtract", "multiply", "divide"]
                    },
                    "a": {
                        "type": "number"
                    },
                    "b": {
                        "type": "number"
                    }
                    },
                    "required": ["operation", "a", "b"]
                }
            }
        }
        remember_tool = {
            "type": "function",
            "function": {
                "name": "remember",
                "description": (
                    "Stores information about the user that should persist across conversations. "
                    "Use this tool when the user explicitly asks to remember something or "
                    "when they provide stable information that is clearly useful in future conversations."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "key": {
                            "type": "string"
                        },
                        "value": {
                            "type": "string"
                        }
                    },
                    "required": ["key", "value"]
                }
            }
        }
        forget_tool={
            "type": "function",
                "function": {
                    "name": "forget",
                    "description": (
                        "Deletes a stored long-term memory using its exact internal key. "
                        "If the user asks to forget information but the exact key is unknown, "
                        "first use list_memories to find the relevant key, then call this tool."
                    ),
                    "parameters": {
                    "type": "object",
                    "properties": {
                        "key": {
                        "type": "string"
                        }
                    },
                    "required": ["key"]
                    }
                }
            }
        get_memory_tool= {
            "type": "function",
            "function": {
                "name": "get_memory",
                "description": "Retrieves a previously stored memory by its key.",
                "parameters": {
                "type": "object",
                "properties": {
                    "key": {
                    "type": "string"
                    }
                },
                "required": ["key"]
                }
            }
        }
        list_memories_tool={
            "type": "function",
            "function": {
                "name": "list_memories",
                "description": (
                    "Returns all stored long-term memories with their keys and values. "
                    "Use this when the relevant memory key is unknown."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                },
            }
        }
        list_directory_tool = {
            "type": "function",
            "function": {
                "name": "list_directory",
                "description": (
                    "Lists files and directories inside the current project. "
                    "Use this to inspect the structure of the project."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": (
                                "Relative directory path inside the project. "
                                "Use '.' for the project root."
                            )
                        }
                    },
                    "required": []
                }
            }
        }
        read_file_tool = {
            "type": "function",
            "function": {
                "name": "read_file",
                "description": (
                    "Reads the contents of a text file inside the current project. "
                    "Use this when you need to inspect source code or configuration files."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": (
                                "Relative path of the file inside the project."
                            )
                        }
                    },
                    "required": ["path"]
                }
            }
        }
        search_files_tool = {
            "type": "function",
            "function": {
                "name": "search_files",
                "description": (
                    "Searches files inside the current project. "
                    "Can search by filename, file extension, "
                    "or text contained inside files."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": (
                                "Optional filename search term. "
                                "Example: 'memory' finds files whose names contain memory."
                            )
                        },
                        "extension": {
                            "type": "string",
                            "description": (
                                "Optional file extension filter, "
                                "for example 'py', '.json' or 'md'."
                            )
                        },
                        "content": {
                            "type": "string",
                            "description": (
                                "Optional text that must appear inside the file."
                            )
                        },
                        "max_results": {
                            "type": "integer",
                            "description": (
                                "Maximum number of matching files to return."
                            )
                        }
                    },
                    "required": []
                }
            }
        }
        get_project_info_tool = {
            "type": "function",
            "function": {
                "name": "get_project_info",
                "description": (
                    "Returns information about the currently active project, "
                    "including its name and root directory."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        }
        
        self.tools = [
            calculator_tool,
            time_tool,
            remember_tool,
            forget_tool,
            swap_value_tool,
            get_memory_tool,
            list_memories_tool,
            list_directory_tool,
            read_file_tool,
            search_files_tool,
            get_project_info_tool 
        ]