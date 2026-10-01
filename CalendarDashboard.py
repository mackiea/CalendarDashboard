import datetime
from enum import Enum

import pygame
from dateutil import parser

import Settings
from GoogleCalendar import GoogleCalendar
import calendar


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

        self.monthText = None

        self.weekday_name_text = []

        self.days = []

        self.mode = self.Mode.Month
        self.day_in_focus = datetime.date.today()
        self.service = None
        self.family_calendar_id = None
        self.status = ""

        print("C A L E N D A R  D A S H B O A R D")
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.

        self.width = self.settings.width
        self.height = self.settings.height
        self.gridheight = self.height - 120
        self.weekday_length = self.width / 7
        self.screen.surface = pygame.display.set_mode(size=(self.width, self.height), flags=pygame.constants.FULLSCREEN)

        # Set weekday headers.
        rectified_list = list(calendar.day_name)
        rectified_list.insert(0, rectified_list.pop(calendar.SUNDAY))
        for weekday in rectified_list:
            self.weekday_name_text.append(self.get_font().render(weekday, antialias=True, color=self.settings.text_colour))
        self.refresh_calendar()
        self.clock.schedule_interval(self.refresh_calendar, 60)

    #####################################################################

    @staticmethod
    def get_font() -> pygame.font.Font:
        return pygame.font.Font(pygame.font.match_font("ubuntu"), size=24)

    def draw(self):
        self.screen.fill(self.settings.background_colour)
        if self.monthText:
            month_rect = self.monthText.get_rect()
            month_rect.center = (self.width / 2, 50)
            self.screen.blit(self.monthText, month_rect)

        self.draw_eekdays()
        self.draw_days_of_month()

        if self.status is not None:
            status_line = self.get_font().render(self.status, antialias=True, color=self.settings.text_colour)
            rect = status_line.get_rect()
            rect.center = (self.width / 2, self.height / 2)
            self.screen.blit(status_line, rect)

    def update(self):
        font = self.get_font()
        font.set_point_size(32)
        self.monthText = font.render(calendar.month_name[self.day_in_focus.month], antialias=True,
                                 color=self.settings.text_colour)

    def draw_eekdays(self):
        i = self.weekday_length / 2
        column = 0
        for weekday_name_text in self.weekday_name_text:
            if (column % 2) == 0:
                column_colour = self.settings.column_colours[0].background
            else:
                column_colour = self.settings.column_colours[1].background
            pygame.draw.rect(surface=self.screen.surface,
                             rect=pygame.Rect((self.weekday_length * column, 80), (self.weekday_length, self.gridheight + 40)),
                             color=column_colour,
                             border_radius=15
                             )
            rect = weekday_name_text.get_rect()
            rect.center = (i, 100)
            self.screen.blit(weekday_name_text, rect)
            i += self.weekday_length
            column = column + 1

    def draw_day_of_month_number(self, day, day_box, colour, font):
        day_number = font.render(str(day), antialias=True, color=self.settings.text_colour)
        rect = day_number.get_rect()
        rect.left = day_box.left + 11
        rect.top = day_box.top + 8
        pygame.draw.circle(surface=self.screen.surface, color=colour,
                           center=(rect.left + rect.width / 2, rect.top + rect.height / 2), radius=14)
        self.screen.blit(day_number, rect)

    def draw_day_of_month_event(self, event, line, font, x1, y1):
        is_all_day = False
        start = event["start"].get("dateTime")
        if start is None:
            start = event["start"].get("date")
            is_all_day = True

        start_dt = parser.parse(start).astimezone()
        font.set_point_size(14)
        if is_all_day:
            event_line = font.render(str(event["summary"]), antialias=True, color=self.settings.text_colour)
        else:
            event_line = font.render(
                str(start_dt.hour) + ":{:02d}".format(start_dt.minute) + " " + str(event["summary"]),
                antialias=True, color=self.settings.text_colour)
        rect = event_line.get_rect()
        rect.left = x1 + 40
        rect.top = y1 + 5 + line * 20
        if is_all_day:
            back_rect = rect
            back_rect.left = rect.left - 60
            back_rect.right = rect.right + 60
            pygame.draw.rect(surface=self.screen.surface,
                             rect=pygame.Rect((rect.left - 10, rect.top), (rect.width + 20, rect.height)),
                             color=self.settings.allday_colour, border_radius=6)
        self.screen.blit(event_line, rect)

    def draw_day_of_month(self, day, column, row, height, font):
        x1 = self.weekday_length * column
        y1 = height * row + self.height - self.gridheight
        if day == datetime.date.today().day:
            column_colour = self.settings.today_colour
        elif (column % 2) == 0:
            column_colour = self.settings.column_colours[0].foreground
        else:
            column_colour = self.settings.column_colours[1].foreground
        # Draw rectangle.
        day_box = pygame.Rect((x1 + 1, y1 + 1), (self.weekday_length - 1, height - 1))
        pygame.draw.rect(surface=self.screen.surface, rect=day_box, color=column_colour, border_radius=15)

        self.draw_day_of_month_number(day=day, day_box=day_box, colour=(255, 255, 255), font=font)
        # Put events.
        day_events = self.days[day - 1]
        line = 0
        for event in day_events.events:
            self.draw_day_of_month_event(event=event, line=line, font=font, x1=x1, y1=y1)
            line = line + 1

    def draw_days_of_month(self):
        # font = pygame.font.Font(filename='freesansbold.ttf', size=24)
        font = self.get_font()
        weekday_of_1st, day_count = calendar.monthrange(self.day_in_focus.year, self.day_in_focus.month)
        row_count = 5
        if weekday_of_1st == calendar.SUNDAY and day_count == 28:
            row_count = 4
        elif (weekday_of_1st == calendar.FRIDAY and day_count == 31) or (
                weekday_of_1st == calendar.SATURDAY and day_count >= 30):
            row_count = 6

        column = (weekday_of_1st + 1) % 7
        row = 0
        height = self.gridheight / row_count
        for d0 in range(day_count):
            self.draw_day_of_month(day=d0 + 1, column=column, row=row, height=height, font=font)
            column = column + 1
            if column == 7:
                column = 0
                row = row + 1

    def refresh_calendar(self):
        # Get calendar events.
        self.days = []
        cursor = pygame.mouse.get_cursor()
        pygame.mouse.set_cursor(pygame.cursors.ball)
        print("Getting the events of this month")
        weekday_of_1st, day_count = calendar.monthrange(self.day_in_focus.year, self.day_in_focus.month)
        for day in range(day_count):
            day_events = self.super_calendar.get_events(day + 1, self.day_in_focus)
            self.days.append(day_events)
        pygame.mouse.set_cursor(cursor)
