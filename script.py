import datetime
from enum import Enum

import pgzrun
import pygame
from dateutil import parser
import dateutil

import Settings
from GoogleCalendar import GoogleCalendar

settings = Settings.Settings()
super_calendar = GoogleCalendar(settings.source_name)

# Default heights.
WIDTH=1920
HEIGHT=1200

GRIDHEIGHT = HEIGHT-120

_weekday_length = WIDTH / 7
import calendar

_initialized = False
_monthText = None

_weekday_name_text = []

_days = []

class Mode(Enum):
    Month=1
    Week=2
    Day=3
_mode = Mode.Month
_day_in_focus = datetime.date.today()
_service = None
_family_calendar_id = None
_status = ""

def draw():
    global settings
    screen.fill(settings.background_colour)
    if _monthText:
        month_rect = _monthText.get_rect()
        month_rect.center = (WIDTH/2, 50)
        screen.blit(_monthText, month_rect)

    draw_eekdays()
    draw_days_of_month()

    if _status is not None:
        font = pygame.font.Font(filename='freesansbold.ttf', size=24)
        status_line = font.render(_status, antialias=True, color=settings.text_colour)
        rect = status_line.get_rect()
        rect.center = (WIDTH/2, HEIGHT/2)
        screen.blit(status_line, rect)

def update():
    if not _initialized:
        initialize()

    global _monthText
    font = pygame.font.Font(filename='freesansbold.ttf', size=32)
    _monthText = font.render(calendar.month_name[_day_in_focus.month], antialias=True, color=settings.text_colour)

def on_key_down(key):
    global _day_in_focus, _status
    if key == keys.RIGHT:
        _status = "Loading month " + calendar.month_name[(_day_in_focus.month + 1) % 12]
        draw()
        _day_in_focus = _day_in_focus + dateutil.relativedelta.relativedelta( months=1)
        refresh_calendar()
    elif key == keys.LEFT:
        _status = "Loading month " + calendar.month_name[(_day_in_focus.month + 1) % 12]
        draw()
        _day_in_focus = _day_in_focus + dateutil.relativedelta.relativedelta(months=-1)
        refresh_calendar()
    _status = ""


#####################################################################

def draw_eekdays():
    i=_weekday_length/2
    column = 0
    for weekday_name_text in _weekday_name_text:
        if (column % 2) == 0:
            column_colour = settings.column_colours[0].background
        else:
            column_colour = settings.column_colours[1].background
        pygame.draw.rect(surface=screen.surface,
                         rect=pygame.Rect((_weekday_length * column, 80), (_weekday_length, GRIDHEIGHT+40)),
                         color=column_colour,
                         border_radius=15
        )
        rect = weekday_name_text.get_rect()
        rect.center = (i, 100)
        screen.blit(weekday_name_text, rect)
        i+=_weekday_length
        column = column + 1

def draw_day_of_month_number(day, day_box, colour, font):
    day_number = font.render(str(day), antialias=True, color=settings.text_colour)
    rect = day_number.get_rect()
    rect.left = day_box.left + 11
    rect.top = day_box.top + 8
    pygame.draw.circle(surface=screen.surface, color=colour,
                       center=(rect.left + rect.width / 2, rect.top + rect.height / 2), radius=14)
    screen.blit(day_number, rect)


def draw_day_of_month(day, column, row, height, font):
    global settings
    x1 = _weekday_length * column
    y1 = height * row + HEIGHT - GRIDHEIGHT
    if day == datetime.date.today().day:
        column_colour = settings.today_colour
    elif (column % 2) == 0:
        column_colour = settings.column_colours[0].foreground
    else:
        column_colour = settings.column_colours[1].foreground
    # Draw rectangle.
    day_box = pygame.Rect((x1 + 1, y1 + 1), (_weekday_length - 1, height - 1))
    pygame.draw.rect(surface=screen.surface, rect=day_box, color=column_colour, border_radius=15)

    def draw_day_of_month_event(event, line):
        is_all_day = False
        start = event["start"].get("dateTime")
        if start is None:
            start = event["start"].get("date")
            is_all_day = True

        start_dt = parser.parse(start).astimezone()
        font.set_point_size(14)
        if is_all_day:
            event_line = font.render(str(event["summary"]), antialias=True, color=settings.text_colour)
        else:
            event_line = font.render(str(start_dt.hour) + ":{:02d}".format(start_dt.minute) + " " + str(event["summary"]),
                                antialias=True, color=settings.text_colour)
        rect = event_line.get_rect()
        rect.left = x1 + 40
        rect.top = y1 + 5 + line * 20
        if is_all_day:
            back_rect = rect
            back_rect.left = rect.left-60
            back_rect.right = rect.right+60
            pygame.draw.rect(surface=screen.surface, rect=pygame.Rect((rect.left-10, rect.top), (rect.width+20, rect.height)), color=settings.allday_colour, border_radius=6)
        screen.blit(event_line, rect)


    draw_day_of_month_number(day=day, day_box=day_box, colour=(255, 255, 255), font=font)
    # Put events.
    day_events = _days[day-1]
    line = 0
    for event in day_events.events:
        draw_day_of_month_event(event=event, line=line)
        line = line + 1



def draw_days_of_month():
    font = pygame.font.Font(filename='freesansbold.ttf', size=24)
    weekday_of_1st, day_count = calendar.monthrange(_day_in_focus.year, _day_in_focus.month)
    row_count = 5
    if weekday_of_1st == calendar.SUNDAY and day_count == 28:
        row_count = 4
    elif (weekday_of_1st == calendar.FRIDAY and day_count == 31) or (weekday_of_1st == calendar.SATURDAY and day_count >= 30):
        row_count = 6

    column = (weekday_of_1st + 1) % 7
    row = 0
    height = GRIDHEIGHT / row_count
    for d0 in range(day_count):
        draw_day_of_month(day=d0+1, column=column, row=row, height=height, font=font)
        column = column + 1
        if column == 7:
            column = 0
            row = row + 1

def initialize():
  print("C A L E N D A R  D A S H B O A R D")
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  global _initialized, WIDTH, HEIGHT, GRIDHEIGHT, _weekday_length
  _initialized = True

  WIDTH = settings.width
  HEIGHT = settings.height

  GRIDHEIGHT = HEIGHT - 120

  _weekday_length = WIDTH / 7

  screen.surface = pygame.display.set_mode(size=(WIDTH, HEIGHT), flags=pygame.constants.FULLSCREEN)

  # Set weekday headers.
  rectified_list = list(calendar.day_name)
  rectified_list.insert(0, rectified_list.pop(calendar.SUNDAY))
  for weekday in rectified_list:
      font = pygame.font.Font(filename='freesansbold.ttf', size=24)
      global _weekday_name_text
      print(settings.text_colour)
      _weekday_name_text.append(font.render(weekday, antialias=True, color=settings.text_colour))
  refresh_calendar()
  clock.schedule_interval(refresh_calendar, 60)

def refresh_calendar():
    # Get calendar events.
    global _days
    _days = []
    cursor = pygame.mouse.get_cursor()
    pygame.mouse.set_cursor(pygame.cursors.ball)
    print("Getting the events of this month")
    weekday_of_1st, day_count = calendar.monthrange(_day_in_focus.year, _day_in_focus.month)
    for day in range(day_count):
        day_events = super_calendar.get_events(day+1, _day_in_focus)
        _days.append(day_events)
    pygame.mouse.set_cursor(cursor)


pgzrun.go()
