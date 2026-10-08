import datetime
from enum import Enum

import pygame
import dateutil
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

        self.weekday_name_text = []

        self.month_days = []
        self.week_days = []
        self.day_events = None

        self.mode = self.Mode.Day
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
        h = self.settings.adjusted_height if self.settings.adjusted_height else self.height
        self.screen.surface = pygame.display.set_mode(size=(self.width, h), flags=pygame.constants.FULLSCREEN)

        # Set weekday headers.
        rectified_list = list(calendar.day_name)
        rectified_list.insert(0, rectified_list.pop(calendar.SUNDAY))
        for weekday in rectified_list:
            self.weekday_name_text.append(self.get_font().render(weekday, antialias=True, color=self.settings.text_colour))
        self.refresh_calendar()
        self.clock.schedule_interval(self.refresh_calendar, 60)

    #####################################################################

    def next_mode(self):
        if self.mode == self.Mode.Month:
            self.mode = self.Mode.Week
        elif self.mode == self.Mode.Week:
            self.mode = self.Mode.Day
        elif self.mode == self.Mode.Day:
            self.mode = self.Mode.Month
        self.refresh_calendar()

    @staticmethod
    def get_font() -> pygame.font.Font:
        return pygame.font.Font(pygame.font.match_font("arial"), size=24)

    def draw(self):
        self.screen.fill(self.settings.background_colour)
        if self.mode != self.Mode.Day:
            self.draw_eekdays()
        if self.mode == self.Mode.Month:
            self.draw_days_of_month()
        elif self.mode == self.Mode.Week:
            self.draw_days_of_week()
        else:
            self.draw_day(self.day_in_focus)

        if self.status is not None:
            status_line = self.get_font().render(self.status, antialias=True, color=self.settings.text_colour)
            rect = status_line.get_rect()
            rect.center = (self.width / 2, self.height / 2)
            self.screen.blit(status_line, rect)

    def update(self):
        pass

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
        if day == datetime.date.today():
            column_colour = self.settings.today_colour
        elif (column % 2) == 0:
            column_colour = self.settings.column_colours[0].foreground
        else:
            column_colour = self.settings.column_colours[1].foreground
        # Draw rectangle.
        day_box = pygame.Rect((x1 + 1, y1 + 1), (self.weekday_length - 1, height - 1))
        pygame.draw.rect(surface=self.screen.surface, rect=day_box, color=column_colour, border_radius=15)

        self.draw_day_of_month_number(day=day.day, day_box=day_box, colour=(255, 255, 255), font=font)
        # Put events.
        day_events = self.month_days[day.day - 1]
        line = 0
        for event in day_events.events:
            self.draw_day_of_month_event(event=event, line=line, font=font, x1=x1, y1=y1)
            line = line + 1

    def draw_day(self, day):
        font = self.get_font()
        font.set_point_size(48)

        title = font.render(
            self.day_in_focus.strftime("%A, %B %d"),
            antialias=True,
            color=self.settings.text_colour
        )
        rect = title.get_rect()
        rect.center = (self.width / 2, 50)
        self.screen.blit(title, rect)

        if day == datetime.date.today():
            colour = self.settings.today_colour
        elif (day.day % 2) == 0:
            colour = self.settings.column_colours[0].foreground
        else:
            colour = self.settings.column_colours[1].foreground
        # Draw rectangle.
        y1 = self.height - self.gridheight
        day_box = pygame.Rect((1, y1), (self.width - 1, self.gridheight - 1))
        pygame.draw.rect(surface=self.screen.surface, rect=day_box, color=colour, border_radius=15)

        # Put events.
        line = 0
        for event in self.day_events.events:
            self.draw_day_of_month_event(event=event, line=line, font=self.get_font(), x1=0, y1=y1)
            line = line + 1

    def draw_day_of_week(self, day, column, font):
        x1 = self.weekday_length * column
        y1 = self.height - self.gridheight
        if day == datetime.date.today():
            column_colour = self.settings.today_colour
        elif (column % 2) == 0:
            column_colour = self.settings.column_colours[0].foreground
        else:
            column_colour = self.settings.column_colours[1].foreground
        # Draw rectangle.
        day_box = pygame.Rect((x1 + 1, y1 + 1), (self.weekday_length - 1, self.gridheight - 1))
        pygame.draw.rect(surface=self.screen.surface, rect=day_box, color=column_colour, border_radius=15)

        self.draw_day_of_month_number(day=day.day, day_box=day_box, colour=(255, 255, 255), font=font)
        # Put events.
        day_events = self.week_days[column]
        line = 0
        for event in day_events.events:
            self.draw_day_of_month_event(event=event, line=line, font=font, x1=x1, y1=y1)
            line = line + 1

    def draw_days_of_month(self):
        font = self.get_font()
        font.set_point_size(48)
        monthText = font.render(calendar.month_name[self.day_in_focus.month], antialias=True,
                                 color=self.settings.text_colour)
        month_rect = monthText.get_rect()
        month_rect.center = (self.width / 2, 50)
        self.screen.blit(monthText, month_rect)

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
            self.draw_day_of_month(
                datetime.datetime(year=self.day_in_focus.year, month=self.day_in_focus.month, day=d0 + 1),
                column=column,
                row=row,
                height=height,
                font=font
            )
            column = column + 1
            if column == 7:
                column = 0
                row = row + 1

    def draw_days_of_week(self):
        font = self.get_font()
        font.set_point_size(48)
        week_number = int(self.day_in_focus.strftime("%U"))

        title = font.render("Week " + str(week_number), antialias=True,
                                 color=self.settings.text_colour)
        rect = title.get_rect()
        rect.center = (self.width / 2, 50)
        self.screen.blit(title, rect)

        font = self.get_font()
        column = 0
        week_number = int(self.day_in_focus.strftime("%U"))
        weekday = datetime.date.fromisocalendar(year=self.day_in_focus.year, week=week_number, day=7)
        for d0 in range(7):
            self.draw_day_of_week(weekday, column=column, font=font)
            weekday = weekday + dateutil.relativedelta.relativedelta(days=1)
            column = column + 1

    def refresh_calendar(self):
        # Get calendar events.
        self.month_days = []
        self.week_days = []
        self.day_events = None
        cursor = pygame.mouse.get_cursor()
        pygame.mouse.set_cursor(pygame.cursors.ball)
        if self.mode == self.Mode.Month:
            print("Getting the events of this month")
            weekday_of_1st, day_count = calendar.monthrange(self.day_in_focus.year, self.day_in_focus.month)
            for day in range(day_count):
                day_events = self.super_calendar.get_events(day + 1, self.day_in_focus)
                self.month_days.append(day_events)

        elif self.mode == self.Mode.Week:
            week_number = int(self.day_in_focus.strftime("%U"))
            weekday = datetime.date.fromisocalendar(year=self.day_in_focus.year, week=week_number, day=7)
            for count in range(7):
                day_events = self.super_calendar.get_events_for_day(weekday)
                self.week_days.append(day_events)
                weekday = weekday + dateutil.relativedelta.relativedelta(days=1)
        elif self.mode == self.Mode.Day:
            self.day_events = self.super_calendar.get_events_for_day(self.day_in_focus)
        pygame.mouse.set_cursor(cursor)

    def skip(self, amount):
        if self.mode == self.mode.Month:
            self.day_in_focus = self.day_in_focus + dateutil.relativedelta.relativedelta(months=amount)
        elif self.mode == self.mode.Week:
            self.day_in_focus = self.day_in_focus + dateutil.relativedelta.relativedelta(weeks=amount)
        if self.mode == self.mode.Day:
            self.day_in_focus = self.day_in_focus + dateutil.relativedelta.relativedelta(days=amount)
