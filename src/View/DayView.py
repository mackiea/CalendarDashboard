from View.View import View

import datetime

import pygame
import dateutil
from dateutil import parser


class DayView(View):
    def __init__(self, screen, settings, font):
        super().__init__(screen, settings, font)
        self.screen = screen
        self.settings = settings
        self.day_events = None

    #####################################################################

    def draw(self, day_in_focus):
            self.draw_day(day_in_focus=day_in_focus)

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

    def draw_day(self, day_in_focus):
        font = self.font
        font.set_point_size(48)

        title = font.render(
            day_in_focus.strftime("%A, %B %d"),
            antialias=True,
            color=self.settings.text_colour
        )
        rect = title.get_rect()
        rect.center = (self.settings.width / 2, 50)
        self.screen.blit(title, rect)

        if day_in_focus.day == datetime.date.today().day and day_in_focus.month == datetime.date.today().month and day_in_focus.year == datetime.date.today().year:
            colour = self.settings.today_colour
        elif (day_in_focus.day % 2) == 0:
            colour = self.settings.column_colours[0].foreground
        else:
            colour = self.settings.column_colours[1].foreground
        # Draw rectangle.
        y1 = self.settings.height - self.grid_height
        day_box = pygame.Rect((1, y1), (self.settings.width - 1, self.grid_height - 1))
        pygame.draw.rect(surface=self.screen.surface, rect=day_box, color=colour, border_radius=15)

        # Put events.
        line = 0
        for event in self.day_events.events:
            self.draw_day_of_month_event(event=event, line=line, font=self.font, x1=0, y1=y1)
            line = line + 1

    def refresh_calendar(self, day_in_focus, super_calendar):
        # Get calendar events.
        self.day_events = None
        cursor = pygame.mouse.get_cursor()
        pygame.mouse.set_cursor(pygame.cursors.ball)
        self.day_events = super_calendar.get_events_for_day(day_in_focus)
        pygame.mouse.set_cursor(cursor)

    def skip(self, day_in_focus, amount):
        return day_in_focus + dateutil.relativedelta.relativedelta(days=amount)


