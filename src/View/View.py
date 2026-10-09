from abc import abstractmethod, ABC

import pygame
import calendar

class View(ABC):
    def __init__(self, screen, settings, font):
        self.screen = screen
        self.settings = settings
        self.font = font
        self.grid_height = self.settings.height - 120

        # Set weekday headers.
        rectified_list = list(calendar.day_name)
        rectified_list.insert(0, rectified_list.pop(calendar.SUNDAY))
        self.weekday_name_text = []
        for weekday in rectified_list:
            self.weekday_name_text.append(
                self.font.render(weekday, antialias=True, color=self.settings.text_colour))

    @abstractmethod
    def draw(self, day_in_focus):
        pass

    @abstractmethod
    def refresh_calendar(self, day_in_focus, super_calendar):
        pass

    @abstractmethod
    def skip(self, day_in_focus, amount):
        pass

    def draw_eekdays(self):
        weekday_name_text = []
        rectified_list = list(calendar.day_name)
        rectified_list.insert(0, rectified_list.pop(calendar.SUNDAY))
        for weekday in rectified_list:
            weekday_name_text.append(
                self.font.render(weekday, antialias=True, color=self.settings.text_colour))

        weekday_length = self.settings.width / 7

        i = weekday_length / 2
        column = 0
        for weekday_name_text in weekday_name_text:
            if (column % 2) == 0:
                column_colour = self.settings.column_colours[0].background
            else:
                column_colour = self.settings.column_colours[1].background
            pygame.draw.rect(surface=self.screen.surface,
                             rect=pygame.Rect((weekday_length * column, 80),
                                              (weekday_length, self.grid_height + 40)),
                             color=column_colour,
                             border_radius=15
                             )
            rect = weekday_name_text.get_rect()
            rect.center = (i, 100)
            self.screen.blit(weekday_name_text, rect)
            i += weekday_length
            column = column + 1

    def draw_day_of_month_number(self, day, day_box):
        self.font.set_point_size(24)
        day_number = self.font.render(str(day), antialias=True, color=self.settings.text_colour)
        rect = day_number.get_rect()
        rect.left = day_box.left + 11
        rect.top = day_box.top + 8
        pygame.draw.circle(surface=self.screen.surface, color=(255, 255, 255),
                           center=(rect.left + rect.width / 2, rect.top + rect.height / 2), radius=14)
        self.screen.blit(day_number, rect)
