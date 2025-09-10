class Stat:
    all_events: int
    active_events: int
    archive_events: int

    def __init__(self, all_events=0, active_events=0, archive_events=0):
        self.all_events = all_events
        self.active_events = active_events
        self.archive_events = archive_events
    