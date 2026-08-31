from memory_manager import MemoryManager
from tools.calculator import CalculatorTool
from tools.time_tool import TimeTool
from llm_client import LLMClient

class Assistant:
    def __init__(self):
        self.calculator = CalculatorTool()
        self.timer = TimeTool()
        self.manager = MemoryManager()
        self.llm = LLMClient()
        self.messages=[]
        self.time_tool={
            "type": "function",
            "function": {
                "name": "time",
                "description": "Returns the current Date including year month day hour minute and seconds",
                "parameters": {
                
                },
                "required": []
            }
        }
        self.calculator_tool = {
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
        self.tools=[self.calculator_tool,self.time_tool]
                
           
    def greet(self):
        name= self.manager.get_name().strip()
        if  name!= "":
            print(f"Hello, {name}")
            self.manager.history_add("hello")
        else:
            self.name()

    def name(self):
        name = input("What is your Name? ")
        print(f"Nice to meet you, {name}. I saved your Name in the DataBase.")
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
                    
            self.manager.history_add("calc")

        except ValueError:
            return "Only numbers are accepted."
        except ZeroDivisionError:
            return "ERROR: Cannot divide by zero."
        return str(result)

    def chat(self) -> bool:
        tmp = input("> ")

        if tmp.strip().lower() == "exit":
            print("Exit Programm")
            return False

        # 1. User-Nachricht speichern
        self.messages.append({
            "role": "user",
            "content": tmp
        })

        # 2. Erste Antwort vom LLM
        message = self.llm.chat(self.messages, self.tools)

        # 3. Assistant-Message IMMER speichern
        self.messages.append(message)

        # 4. Prüfen, ob ein Tool verlangt wurde
        if "tool_calls" in message:
            tool_call = message["tool_calls"][0]
            self.execute_tool(tool_call)            
        else:
            print(message["content"])
        return True
    
    def execute_tool(self, tool_call):
        function = tool_call["function"]
        arguments = function.get("arguments", {})

        if function["name"] == "time":
            result = self.timer.get_time()

        elif function["name"] == "calculator":
            result = self.calc(
                arguments["operation"],
                arguments["a"],
                arguments["b"]
            )

        else:
            result = "Unknown tool."

        self.messages.append({
            "role": "tool",
            "content": result
        })

        final_message = self.llm.chat(self.messages, self.tools)
        self.messages.append(final_message)

        print(final_message["content"])
            
    def show_history(self):
        # Foreach
        for item in self.manager.get_memory("history"):
            print(item)

    def remember(self):
        key = input("Key: ")
        value = input("Value: ")
        if(self.manager.remember(key,value)):
            print("Saved")
        else:
            print("Error")

    def forget(self):
        key = input("What should I forget: ")
        
        if self.manager.forget(key):
            print(f"Forgot {key}")
        else:
            print("Key was not in Memories.")

    def show_memory(self):
        self.manager.show_memory()

    def time(self):
        print(f"Current time: {self.timer.get_time()}")
        self.manager.history_add("time")
