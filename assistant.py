from tools.tool_definitions import ToolDefinitions
from tools.project_context import ProjectContext
from tools.file_system import FileSystemTool
from approval_manager import ApprovalManager
from tools.calculator import CalculatorTool
from memory_manager import MemoryManager
from system_prompt import SYSTEM_PROMPT
from tools.time_tool import TimeTool
from llm_client import LLMClient
from pathlib import Path
import binascii
import base64
import json

class Assistant:
    def __init__(self):
        self.llm = LLMClient()
        self.messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            }
        ]
        
        self.calculator = CalculatorTool()
        self.timer = TimeTool()
        self.manager = MemoryManager()
        self.approval_manager = ApprovalManager()

        #path is current working directory
        self.project_context = ProjectContext(str(Path.cwd()))
        self.file_system = FileSystemTool(self.project_context)

        self.tools= ToolDefinitions().tools
        self.max_tool_iterations= 20
                
           
    def greet(self):
        name = self.manager.get_name().strip()
        
        if name:
            print(f"Hello, {name}")
        else:
            self.name()

    def name(self):
        name = input("What is your Name? ")
        print(f"Nice to meet you, {name}. Your Name has been saved.")
        self.manager.set_name(name)

    def calc(self,operation:str,a,b)->str:
        result="Error occured"
        try:
            match operation:
                case "add":
                    result =self.calculator.add( a, b) 

                case "subtract":
                    result =self.calculator.subtract( a, b) 
                   
                case "multiply":
                    result =self.calculator.multiply( a, b)

                case "divide":
                    result =self.calculator.divide( a, b)
                case _:
                    return str(result)
                    

        except ValueError:
            return "Only numbers are accepted."
        except ZeroDivisionError:
            return "ERROR: Cannot divide by zero."
        return str(result)

    def chat(self) -> bool:
        tmp = input("> ")

        if tmp.strip().lower() == "exit":
            print("Exit Program")
            return False

        self.messages.append({
            "role": "user",
            "content": tmp
        })

        message = self.llm.chat(self.messages, self.tools)

        # Erst Fehler prüfen
        if "error" in message:
            print(f"\nZayn error: {message['error']}")
            return True

        # Dann speichern
        self.messages.append(message)

        if not message.get("tool_calls"):
            return True

        tool_iteration = 0

        while message.get("tool_calls"):
            # Task-loop limit
            if tool_iteration >= self.max_tool_iterations:
                print("\nZayn error: Maximum tool iterations reached.")
                return True

            tool_calls = message["tool_calls"]
            cancelled = False

            for tool_call in tool_calls:
                function = tool_call["function"]

                if cancelled:
                    # skip tasks if cancelled
                    result = {
                        "success": False,
                        "cancelled": True,
                        "error": "Skipped because the user cancelled this round."
                    }
                else:
                    print(
                        "\n[TOOL]",
                        function["name"],
                        function.get("arguments", {})
                    )

                    result = self.execute_tool(tool_call)

                    if result.get("cancelled"):
                        cancelled = True

                self.messages.append({
                    "role": "tool",
                    "tool_name": function["name"],
                    "content": json.dumps(result)
                })

            
            if cancelled:
                # Give the LLM a final response without tool access
                final_instruction = {
                    "role": "system",
                    "content": (
                        "The user rejected a tool operation. "
                        "The rejected operation was not executed. "
                        "Remaining tool calls in this round were skipped. "
                        "Respect the user's decision. "
                        "Do not claim that the rejected changes were made. "
                        "Explain the outcome based on the actual tool results. "
                        "Respond naturally to the user."
                    )
                }

                final_message = self.llm.chat(
                    self.messages + [final_instruction],
                    []
                )

                if "error" in final_message:
                    print(f"\nZayn error: {final_message['error']}")
                    return True

                self.messages.append(final_message)

                return True


            tool_iteration += 1

            # Reminding about the actual task
            reminder = {
                "role": "system",
                "content": (
                    f"The user's current request is: {tmp}\n"
                    "Continue solving that request. "
                    "If requested files have not been read, read them now. "
                    "Follow relevant references before answering. "
                    "Do not replace the task with a summary of the last tool result. "
                    "Base project-specific claims only on inspected code."
                )
            }

            message = self.llm.chat(
                self.messages + [reminder],
                self.tools
            )

            if "error" in message:
                print(f"\nZayn error: {message['error']}")
                return True

            self.messages.append(message)

        return True
    
    # execute the Tools and returns the result
    def execute_tool(self, tool_call):
        try:
            function = tool_call.get("function")

            if not function:
                return {
                    "success": False,
                    "error": "Invalid tool call: missing function."
                }

            name = function.get("name")

            if not name:
                return {
                    "success": False,
                    "error": "Invalid tool call: missing tool name."
                }

            arguments = function.get("arguments", {})

            # Invalid arguments?
            if isinstance(arguments, str):
                arguments = json.loads(arguments)

            if not isinstance(arguments, dict):
                return {
                    "success": False,
                    "error": "Invalid tool arguments."
                }
            # TIME
            if name == "time":
                result = self.timer.get_time()

                return {
                    "success": True,
                    "result": result
                }

            # CALCULATOR
            elif name == "calculator":
                operation = arguments.get("operation")
                a = arguments.get("a")
                b = arguments.get("b")

                if operation is None or a is None or b is None:
                    return {
                        "success": False,
                        "error": "Missing calculator arguments."
                    }

                result = self.calc(operation, a, b)

                return {
                    "success": True,
                    "result": result
                }

            # REMEMBER
            elif name == "remember":
                key = arguments.get("key")
                value = arguments.get("value")

                if key is None or value is None:
                    return {
                        "success": False,
                        "error": "Missing remember arguments."
                    }

                self.manager.remember(key, value)

                return {
                    "success": True,
                    "result": f"Memory '{key}' has been saved."
                }

            # FORGET
            elif name == "forget":
                key = arguments.get("key")

                if key is None:
                    return {
                        "success": False,
                        "error": "Missing forget argument: key."
                    }

                deleted = self.manager.forget(key)

                if not deleted:
                    return {
                        "success": False,
                        "error": f"No memory found for '{key}'."
                    }

                return {
                    "success": True,
                    "result": f"Memory '{key}' has been deleted."
                }

            # SWAP / UPDATE MEMORY VALUE
            elif name == "swap_value":
                key = arguments.get("key")
                value = arguments.get("value")

                if key is None or value is None:
                    return {
                        "success": False,
                        "error": "Missing swap_value arguments."
                    }

                result = self.manager.swap_value(key, value)

                return {
                    "success": True,
                    "result": result
                }

            # GET MEMORY
            elif name == "get_memory":
                key = arguments.get("key")

                if key is None:
                    return {
                        "success": False,
                        "error": "Missing get_memory argument: key."
                    }

                result = self.manager.get_memory(key)

                if result is None:
                    return {
                        "success": False,
                        "error": f"No memory found for '{key}'."
                    }

                return {
                    "success": True,
                    "result": result
                }

            # LIST MEMORIES
            elif name == "list_memories":
                result = self.manager.list_memories()

                return {
                    "success": True,
                    "result": result
                }

            # LIST DIRECTORY
            elif name == "list_directory":
                return self.file_system.list_directory(
                    arguments.get("path", ".")
                )

            # READ_FILE
            elif name == "read_file":
                return self.file_system.read_file(
                    path=arguments["path"],
                    include_line_numbers=arguments.get(
                        "include_line_numbers",False
                    ),
                    start_line=arguments.get("start_line"),
                    end_line=arguments.get("end_line")
                )
            
            # SEARCH FILE
            elif name == "search_files":
                return self.file_system.search_files(
                    query=arguments.get("query",""),
                    extension=arguments.get("extension"),
                    content=arguments.get("content"),
                    max_results=arguments.get("max_results",50)
                )

            #GET PROJECT INFO
            elif name == "get_project_info":
                return self.project_context.get_project_info()  

            # CREATE FILE
            elif name == "create_file":
                path = arguments.get("path")
                content = arguments.get("content", "")
                encoding = arguments.get("encoding", "utf-8")

                # validate path
                if not isinstance(path, str) or not path.strip() or Path(path).is_absolute():
                    return {
                        "success": False,
                        "error": "Use a relative project path."
                    }
                 # validate content
                if not isinstance(content, str):
                    return {
                        "success": False,
                        "error": "Content must be a string."
                    }
                
                # validate encoding
                if encoding not in ("utf-8", "base64"):
                    return {
                        "success": False,
                        "error": "Unsupported encoding."
                    }

                try:
                    if encoding == "utf-8":
                        data = content.encode("utf-8")
                    else:
                        data = base64.b64decode(content, validate=True)
                except (UnicodeError, ValueError, binascii.Error):
                    return {
                        "success": False,
                        "error": "Invalid file content."
                    }

                # data limit
                if len(data) > 5 * 1024 * 1024:
                    return {
                        "success": False,
                        "error": "File exceeds the 5 MB limit."
                    }

                target = self.project_context.resolve_path(path)
                relative = target.relative_to(
                    self.project_context.get_project_root()
                )

                if not relative.parts or any(
                    part in self.file_system.ignored_directories
                    for part in relative.parts
                ):
                    return {
                        "success": False,
                        "error": "This project path is not writable."
                    }

                # File already exists
                if target.exists():
                    return {
                        "success": False,
                        "error": "File already exists."
                    }
                # wrong directory
                if not target.parent.is_dir():
                    return {
                        "success": False,
                        "error": "Parent directory does not exist."
                    }

                # User's appoval
                if not self.approval_manager.file_creation(
                    str(relative), content, encoding, data
                ):
                    return {
                        "success": False,
                        "cancelled": True,
                        "error": "Cancelled by user."
                    }

                return self.file_system.create_file(
                    str(relative),
                    content,
                    encoding
                )
            
            # REPLACE TEXT
            elif name == "replace_text":
                path = arguments.get("path")
                old_text = arguments.get("old_text")
                new_text = arguments.get("new_text")
                # validating parameters
                if not isinstance(path, str) or not path.strip() or Path(path).is_absolute():
                    return {
                        "success": False,
                        "error": "Use a relative project path."
                    }
                if not isinstance(old_text, str) or not old_text:
                    return {
                        "success": False,
                        "error": "old_text must be non-empty."
                    }
                if not isinstance(new_text, str):
                    return {
                        "success": False,
                        "error": "new_text must be a string."
                    }

                # relative path creation & validation
                target = self.project_context.resolve_path(path)
                relative = target.relative_to(
                    self.project_context.get_project_root()
                )

                if any(
                    part in self.file_system.ignored_directories
                    for part in relative.parts
                ):
                    return {
                        "success": False,
                        "error": "This project path is not writable."
                    }

                if not target.is_file():
                    return {
                        "success": False,
                        "error": "File does not exist."
                    }

                if target.stat().st_size > self.file_system.max_file_size:
                    return {
                        "success": False,
                        "error": "File is too large."
                    }

                with target.open("r", encoding="utf-8", newline="") as file:
                    original = file.read()

                matches = original.count(old_text)

                if matches != 1:
                    return {
                        "success": False,
                        "error": f"Expected exactly one match, found {matches}."
                    }
                
                # USER approval
                if not self.approval_manager.text_replacement(
                    str(relative), old_text, new_text
                ):
                    return {
                        "success": False,
                        "cancelled": True,
                        "error": "Cancelled by user."
                    }

                return self.file_system.replace_text(
                    path=str(relative),
                    old_text=old_text,
                    new_text=new_text,
                    expected_content=original
                )
            
            # UNKNOWN TOOL
            else:
                return {
                    "success": False,
                    "error": f"Unknown tool: {name}"
                }
        except json.JSONDecodeError:
            return {
                "success": False,
                "error": "Tool arguments contained invalid JSON."
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"Tool execution failed: {e}"
            }