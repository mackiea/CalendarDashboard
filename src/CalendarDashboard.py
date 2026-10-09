import datetime
from enum import Enum

import pygame

import Settings
from GoogleCalendar import GoogleCalendar

from View.MonthView import MonthView
from View.WeekView import WeekView
from View.DayView import DayView


class CalendarDashboard:

    class Mode(Enum):
        Month = 1
        Week = 2
        Day = 3

    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock

        self.settings = Settings.Settings()
        self.super_calendar = GoogleCalendar(self.settings.source_name)

        self.day_events = None

        self.mode = self.Mode.Month
        self.day_in_focus = datetime.date.today()
        self.family_calendar_id = None
        self.status = ""

        self.view = MonthView(screen=screen, settings=self.settings, font=self.get_font())

        print("C A L E N D A R  D A S H B O A R D")
        self.width = self.settings.width
        self.height = self.settings.height
        self.gridheight = self.height - 120
        self.weekday_length = self.width / 7
        h = self.settings.adjusted_height if self.settings.adjusted_height else self.height
        self.screen.surface = pygame.display.set_mode(size=(self.width, h), flags=pygame.constants.FULLSCREEN)

        self.refresh_calendar()
        self.clock.schedule_interval(self.refresh_calendar, 60)

    #####################################################################

    def next_mode(self):
        if self.mode == self.Mode.Month:
            self.mode = self.Mode.Week
            self.view = WeekView(self.screen, self.settings, self.get_font())
        elif self.mode == self.Mode.Week:
            self.mode = self.Mode.Day
            self.view = DayView(self.screen, self.settings, self.get_font())
            self.refresh_calendar()
        elif self.mode == self.Mode.Day:
            self.mode = self.Mode.Month
            self.view = MonthView(self.screen, self.settings, self.get_font())
        self.refresh_calendar()

    @staticmethod
    def get_font() -> pygame.font.Font:
        return pygame.font.Font(pygame.font.match_font("arial"), size=24)

    def draw(self):
        self.screen.fill(self.settings.background_colour)
        self.view.draw(day_in_focus=self.day_in_focus)

        if self.status is not None:
            status_line = self.get_font().render(self.status, antialias=True, color=self.settings.text_colour)
            rect = status_line.get_rect()
            rect.center = (self.width / 2, self.height / 2)
            self.screen.blit(status_line, rect)

    def update(self):
        pass

    def refresh_calendar(self):
        # Get calendar events.
        self.day_events = None
        cursor = pygame.mouse.get_cursor()
        pygame.mouse.set_cursor(pygame.cursors.ball)
        self.view.refresh_calendar(day_in_focus=self.day_in_focus, super_calendar=self.super_calendar)
        pygame.mouse.set_cursor(cursor)

    def skip(self, amount):
        self.day_in_focus = self.view.skip(day_in_focus=self.day_in_focus, amount=amount)


