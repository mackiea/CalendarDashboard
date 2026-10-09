from View.View import View
import datetime

import pygame
import dateutil
from dateutil import parser

class WeekView(View):
    def __init__(self, screen, settings, font):
        super().__init__(screen=screen, settings=settings, font=font)
        self.weekday_name_text = []

        self.week_days = []
        self.day_events = None

        self.day_in_focus = datetime.date.today()
        self.service = None
        self.family_calendar_id = None

    def draw(self, day_in_focus):
            self.draw_days(day_in_focus)

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
        rect.left = x1 + 50
        rect.top = y1 + 5 + line * 20
        if is_all_day:
            back_rect = rect
            back_rect.left = rect.left - 60
            back_rect.right = rect.right + 60
            pygame.draw.rect(surface=self.screen.surface,
                             rect=pygame.Rect((rect.left - 10, rect.top), (rect.width + 20, rect.height)),
                             color=self.settings.allday_colour, border_radius=6)
        self.screen.blit(event_line, rect)

    def draw_day_of_week(self, day, column, font, day_in_focus):
        weekday_length = self.settings.width / 7
        x1 = weekday_length * column
        y1 = self.settings.height - self.grid_height
        if day.day == datetime.date.today().day and day.month == datetime.date.today().month and day.year == datetime.date.today().year:
            column_colour = self.settings.today_colour
        elif (column % 2) == 0:
            column_colour = self.settings.column_colours[0].foreground
        else:
            column_colour = self.settings.column_colours[1].foreground
        # Draw rectangle.
        day_box = pygame.Rect((x1 + 1, y1 + 1), (weekday_length - 1, self.grid_height - 1))
        pygame.draw.rect(surface=self.screen.surface, rect=day_box, color=column_colour, border_radius=15)

        self.draw_day_of_month_number(day=day.day, day_box=day_box)
        # Put events.
        day_events = self.week_days[column]
        line = 0
        for event in day_events.events:
            self.draw_day_of_month_event(event=event, line=line, font=font, x1=x1, y1=y1)
            line = line + 1

    def draw_days(self, day_in_focus):
        font = self.font
        font.set_point_size(48)
        week_number = int(day_in_focus.strftime("%U"))

        title = font.render("Week " + str(week_number), antialias=True,
                                 color=self.settings.text_colour)
        rect = title.get_rect()
        rect.center = (self.settings.width / 2, 50)
        self.screen.blit(title, rect)

        font = self.font
        column = 0
        week_number = int(day_in_focus.strftime("%U"))
        weekday = datetime.date.fromisocalendar(year=day_in_focus.year, week=week_number, day=7)
        for d0 in range(7):
            self.draw_day_of_week(weekday, column=column, font=font, day_in_focus=day_in_focus)
            weekday = weekday + dateutil.relativedelta.relativedelta(days=1)
            column = column + 1

    def refresh_calendar(self, day_in_focus, super_calendar):
        # Get calendar events.
        self.week_days = []
        self.day_events = None
        cursor = pygame.mouse.get_cursor()
        pygame.mouse.set_cursor(pygame.cursors.ball)
        week_number = int(day_in_focus.strftime("%U"))
        weekday = datetime.date.fromisocalendar(year=day_in_focus.year, week=week_number, day=7)
        for count in range(7):
            day_events = super_calendar.get_events_for_day(weekday)
            self.week_days.append(day_events)
            weekday = weekday + dateutil.relativedelta.relativedelta(days=1)
        pygame.mouse.set_cursor(cursor)

    def skip(self, day_in_focus, amount):
        return day_in_focus + dateutil.relativedelta.relativedelta(weeks=amount)
