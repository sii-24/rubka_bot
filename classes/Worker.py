class Worker:
    id: str
    name: str
    events: int

    def __init__(self, id="0", name="", events=0):
        self.id = id
        self.name = name
        self.events = events
