from View.View import View
import datetime

import pygame
import dateutil
from dateutil import parser

import calendar


class MonthView(View):
    def __init__(self, screen, settings, font):
        super().__init__(screen=screen, settings=settings, font=font)
        self.month_days = []
        self.day_events = None

    #####################################################################

    def draw(self, day_in_focus):
        self.screen.fill(self.settings.background_colour)
        self.draw_eekdays()
        self.draw_days(day_in_focus)

    def draw_day_event(self, event, line, font, x1, y1):
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

    def draw_day(self, day, column, row, height, font):
        weekday_length = self.settings.width / 7
        x1 = weekday_length * column
        y1 = height * row + self.settings.height - self.grid_height
        if day.day == datetime.date.today().day and day.month == datetime.date.today().month and day.year == datetime.date.today().year:
            column_colour = self.settings.today_colour
        elif (column % 2) == 0:
            column_colour = self.settings.column_colours[0].foreground
        else:
            column_colour = self.settings.column_colours[1].foreground
        # Draw rectangle.
        day_box = pygame.Rect((x1 + 1, y1 + 1), (weekday_length - 1, height - 1))
        pygame.draw.rect(surface=self.screen.surface, rect=day_box, color=column_colour, border_radius=15)

        self.draw_day_of_month_number(day=day.day, day_box=day_box)
        # Put events.
        day_events = self.month_days[day.day - 1]
        line = 0
        for event in day_events.events:
            self.draw_day_event(event=event, line=line, font=font, x1=x1, y1=y1)
            line = line + 1

    def draw_days(self, day_in_focus):
        font = self.font
        font.set_point_size(48)
        month_text = font.render(calendar.month_name[day_in_focus.month], antialias=True,
                                 color=self.settings.text_colour)
        month_rect = month_text.get_rect()
        month_rect.center = (self.settings.width / 2, 50)
        self.screen.blit(month_text, month_rect)

        font = self.font
        weekday_of_1st, day_count = calendar.monthrange(day_in_focus.year, day_in_focus.month)
        row_count = 5
        if weekday_of_1st == calendar.SUNDAY and day_count == 28:
            row_count = 4
        elif (weekday_of_1st == calendar.FRIDAY and day_count == 31) or (
                weekday_of_1st == calendar.SATURDAY and day_count >= 30):
            row_count = 6

        column = (weekday_of_1st + 1) % 7
        row = 0
        height = self.grid_height / row_count
        for d0 in range(day_count):
            self.draw_day(
                datetime.datetime(year=day_in_focus.year, month=day_in_focus.month, day=d0 + 1),
                column=column,
                row=row,
                height=height,
                font=font
            )
            column = column + 1
            if column == 7:
                column = 0
                row = row + 1

    def refresh_calendar(self, day_in_focus, super_calendar):
        # Get calendar events.
        self.month_days = []
        self.day_events = None
        cursor = pygame.mouse.get_cursor()
        pygame.mouse.set_cursor(pygame.cursors.ball)
        print("Getting the events of this month")
        weekday_of_1st, day_count = calendar.monthrange(day_in_focus.year, day_in_focus.month)
        for day in range(day_count):
            day_events = super_calendar.get_events(day + 1, day_in_focus)
            self.month_days.append(day_events)
        pygame.mouse.set_cursor(cursor)

    def skip(self, amount, day_in_focus):
        return day_in_focus + dateutil.relativedelta.relativedelta(months=amount)
