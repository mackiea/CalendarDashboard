from abc import ABC, abstractmethod

from Day import Day

class SuperCalendar(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def get_events(self, day, day_in_focus)->Day:
        pass
