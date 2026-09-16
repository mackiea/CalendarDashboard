import datetime


class Day:
    def __init__(self, events, day):
        self.events = []
        for event in events:
            if "date" in event["start"]:
                start = datetime.datetime.strptime(event["start"]["date"], "%Y-%m-%d")
                if start.day <= day:
                    self.events.append(event)
            else:
                self.events.append(event)

