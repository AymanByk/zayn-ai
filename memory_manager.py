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

    def get_memory(self, categorie:str):
        return self.memory[categorie]
    
    def get_saved_memory(self, key):
        return self.memory["memories"].get(key) 
    
    def history_add(self, a: str):
            self.memory["history"].append(a)
            self.save_memory()

    def load_memory(self):
        if os.path.exists("memory.json"):
            try:
                with open("memory.json", "r") as file:
                    return json.load(file)
            except json.JSONDecodeError:
                print("memory.json is empty or corrupted. Creating new memory.")

        return {
            "name": "",
            "history": [],
            "memories": {}
        }
    
    def save_memory(self):
        with open("memory.json", "w") as file:
            json.dump(self.memory, file, indent=4)

    def remember(self,key:str,value:str)-> bool:
        try:
            self.memory["memories"][key] = value
            self.history_add("remember")
            return True
        except KeyError:
            return False

    def forget(self, key: str) -> bool:
        if key in self.memory["memories"]:
            del self.memory["memories"][key]
            self.history_add("forget")
            return True

        return False
        
           

    def show_memory(self):
        for key, value in self.memory.items():
            print(key, ":", value)