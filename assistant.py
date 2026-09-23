from tools.tool_definitions import ToolDefinitions
from tools.project_context import ProjectContext
from tools.file_system import FileSystemTool
from tools.calculator import CalculatorTool
from memory_manager import MemoryManager
from system_prompt import SYSTEM_PROMPT
from tools.time_tool import TimeTool
from llm_client import LLMClient
from pathlib import Path
import binascii
import hashlib
import base64
import json
import sys
import os

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

            for tool_call in tool_calls:

                print(
                    "\n[TOOL]",
                    tool_call["function"]["name"],
                    tool_call["function"].get("arguments", {})
                )
                result = self.execute_tool(tool_call)

                self.messages.append({
                    "role": "tool",
                    "tool_name": tool_call["function"]["name"],
                    "content": json.dumps(result)
                })

            tool_iteration += 1
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
                if not self.approve_file_creation(
                    str(relative), content, encoding, data
                ):
                    return {
                        "success": False,
                        "error": "Cancelled by user."
                    }

                return self.file_system.create_file(
                    str(relative),
                    content,
                    encoding
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
        
    def approve_file_creation(
        self,
        path: str,
        content: str,
        encoding: str,
        data: bytes
    ) -> bool:
        
        print("Create file?  [y/N]: ", end="", flush=True)
        buffer = []

        while True:
            char = self.get_char()

            if char == "\x1b":  # Escape
                print()
                return False

            if char in ("\r", "\n"):
                answer = "".join(buffer).strip().lower()
                print()

                if answer in ("yes", "y"):
                    return True
                if answer in ("", "no", "n"):
                    return False

                print("Type yes to create or no to cancel: ", end="", flush=True)
                buffer.clear()

            elif char in ("\x08", "\x7f"):  # Backspace
                if buffer:
                    buffer.pop()
                    sys.stdout.write("\b \b")
                    sys.stdout.flush()

            elif char.isprintable():
                buffer.append(char)
                sys.stdout.write(char)
                sys.stdout.flush()

    #get key input        
    def get_char(self) -> str:
        if os.name == 'nt':  # Windows
            import msvcrt
            ch = msvcrt.getch()
            if ch in (b'\x00', b'\xe0'):  # Special key prefix (e.g., arrow keys)
                msvcrt.getch()
                return ''
            return ch.decode('utf-8', errors='ignore')
        else:  # Unix / Linux / macOS
            import tty
            import termios
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                ch = sys.stdin.read(1)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            return ch
