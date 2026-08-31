from datetime import datetime

class TimeTool:
    def __init__(self) -> None:
        self.time= datetime

    def get_time(self) ->str:
        now = str(datetime.now())
        return now