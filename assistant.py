from memory_manager import MemoryManager
from tools.calculator import CalculatorTool
from tools.time_tool import TimeTool
from llm_client import LLMClient
from tools.tool_definitions import ToolDefinitions

class Assistant:
    def __init__(self):
        self.calculator = CalculatorTool()
        self.timer = TimeTool()
        self.manager = MemoryManager()
        self.llm = LLMClient()
        self.messages=[]
        self.tools= self.tools = ToolDefinitions().tools
                
           
    def greet(self):
        name= self.manager.get_name().strip()
        if  name!= "":
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
            print("Exit Programm")
            return False

        # save users input 
        self.messages.append({
            "role": "user",
            "content": tmp
        })

        # First Answer from LLM
        message = self.llm.chat(self.messages, self.tools)
        self.messages.append(message)

        if not message.get("tool_calls"):
            return True

        # Dispatcher
        while message.get("tool_calls"):
            tool_calls = message["tool_calls"]

            for tool_call in  tool_calls:

                result= self.execute_tool(tool_call)   
                self.messages.append({
                    "role": "tool",
                    "content": str(result)
                })

            message = self.llm.chat(self.messages, self.tools)
            self.messages.append(message)
          
        return True
    
    # execute the Tools and returns the result
    def execute_tool(self, tool_call):
        function = tool_call["function"]
        arguments = function.get("arguments", {})
        name = function["name"]

        if name == "time":
            result = self.timer.get_time()

        elif name == "calculator":
            result = self.calc(
                arguments["operation"],
                arguments["a"],
                arguments["b"]
            )

        elif name == "remember":
            key = arguments["key"]
            value = arguments["value"]
            self.manager.remember(key, value)

            result = "Saved Memory"

        elif name == "forget":
            result = f"Memory has been deleted"
            key= arguments["key"]
            if self.manager.forget(arguments["key"]) == False:
                result= f"No memory found for '{key}'."

        elif name == "swap_value":
            result = self.manager.swap_value(
                arguments["key"],
                arguments["value"]
            )

        elif name == "get_memory":
            key = arguments["key"]
            result = self.manager.get_memory(key)

        elif name== "list_memories":
            result= self.manager.list_memories()

        else:
            result = "Unknown tool."
        return result
            