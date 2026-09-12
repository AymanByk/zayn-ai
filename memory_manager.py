import os
import json

class MemoryManager:
    def __init__(self) -> None:
        self.memory= self.load_memory()

    def set_name(self,name: str):
        self.memory["name"] = name
        self.save_memory()

    def get_name(self)-> str:
        return self.memory["name"]

    def get_memory(self, key: str):
        memory_val = self.memory["memories"].get(key)

        if memory_val is not None:
            return f"Memory found: {memory_val}"

        return f"No memory found for '{key}'."

    def swap_value(self, key, value):
        if key in self.memory["memories"]:
            self.memory["memories"][key] = value
            self.save_memory()
            return "Memory updated."

        return "Memory not found."

    def list_memories(self):
        return self.memory["memories"]

    def load_memory(self):
        if os.path.exists("memory.json"):
            try:
                with open("memory.json", "r") as file:
                    return json.load(file)
            except json.JSONDecodeError:
                print("memory.json is empty or corrupted. Creating new memory.")

        return {
            "name": "",
            "memories": {}
        }
    
    def save_memory(self):
        with open("memory.json", "w") as file:
            json.dump(self.memory, file, indent=4)

    def remember(self, key: str, value: str) -> bool:
        try:
            self.memory["memories"][key] = value
            self.save_memory()
            return True
        except KeyError:
            return False

    def forget(self, key: str) -> bool:
        if key in self.memory["memories"]:
            del self.memory["memories"][key]
            self.save_memory()
            return True

        return False
