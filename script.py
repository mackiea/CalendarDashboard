import datetime
import os.path
from calendar import Calendar
from datetime import tzinfo
from enum import Enum

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pgzrun
import pygame
from dateutil import parser

WIDTH = 1920
HEIGHT = 1200
GRIDHEIGHT = 1100
_weekday_length = WIDTH / 7
import calendar

_white = (255, 255, 255)
_background_color = (200, 200, 255)
_text_colour = (0, 0, 0)
_green = (0, 255, 0)
_blue = (0, 0, 128)
BLACK = (0, 0, 0)
_initialized = False
_monthText = None

_weekday_name_text = []

class Day:
    events = []
    def __init__(self, events):
        self.events = events

_days = []

class Mode(Enum):
    Month=1
    Week=2
    Day=3
_mode = Mode.Month
_day_in_focus = datetime.date.today()
_service = None
_family_calendar_id = None

def draw():
    screen.fill(_background_color)
    if _monthText:
        month_rect = _monthText.get_rect()
        month_rect.center = (WIDTH/2, 50)
        screen.blit(_monthText, month_rect)

    i=_weekday_length/2
    for weekday_name_text in _weekday_name_text:
        rect = weekday_name_text.get_rect()
        rect.center = (i, 100)
        screen.blit(weekday_name_text, rect)
        i+=_weekday_length

    # Draw days.
    weekday_of_1st, day_count = calendar.monthrange(_day_in_focus.year, _day_in_focus.month)
    rowCount = 5
    if weekday_of_1st == calendar.SUNDAY and day_count == 28:
        rowCount = 4
    if (weekday_of_1st == calendar.FRIDAY and day_count == 31) or (weekday_of_1st == calendar.SATURDAY and day_count >= 30):
        rowCount = 6

    column = weekday_of_1st + 1
    row = 0
    width = WIDTH / 7
    height = GRIDHEIGHT / rowCount
    for d0 in range(day_count):
        day = d0 + 1
        x1 = width * column
        y1 = height * row + HEIGHT-GRIDHEIGHT
        screen.draw.rect(Rect((x1, y1),(width, height)), BLACK)

        # Put day number.
        font = pygame.font.Font(filename='freesansbold.ttf', size=24)
        day_number = font.render(str(day), antialias=True, bgcolor=_background_color, color=_text_colour)
        rect = day_number.get_rect()
        rect.left = x1 + 5
        rect.top = y1 + 5
        screen.blit(day_number, rect)

        # Put events.
        day_events = _days[d0]
        line = 0
        for event in day_events.events:
            print(str(event))
            is_all_day = False
            start = event["start"].get("dateTime")
            if start is None:
                start = event["start"].get("date")
                is_all_day = True

            print(str(start))

            start_dt = parser.parse(start).astimezone()
            font.set_point_size(18)
            if is_all_day:
                event = font.render(str(event["summary"]), antialias=True, bgcolor=_background_color, color=_text_colour)
            else:
                event = font.render(str(start_dt.hour) + ":{:02d}".format(start_dt.minute) + " " + str(event["summary"]),
                                    antialias=True, bgcolor=_background_color, color=_text_colour)
            rect = event.get_rect()
            rect.left = x1 + 40
            rect.top = y1 + 5 + line * 20
            screen.blit(event, rect)

            line = line + 1

        column = column + 1

        if (column == 7):
            column = 0
            row = row + 1


    # for days_of_month in calendar.monthrange(year=_day_in_focus.year, month=_day_in_focus.month):
    #    pygame.draw.

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

def update():
    if not _initialized:
        initialize()

    global _monthText
    font = pygame.font.Font(filename='freesansbold.ttf', size=32)
    _monthText = font.render(calendar.month_name[_day_in_focus.month], antialias=True, bgcolor=_background_color, color=_text_colour)

def initialize():
  print("C A L E N D A R  D A S H B O A R D")
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  global _initialized
  _initialized = True

  screen.surface = pygame.display.set_mode(size=(1920, 1200), flags=pygame.constants.FULLSCREEN)

  rectified_list = list(calendar.day_name)
  rectified_list.insert(0, rectified_list.pop(calendar.SUNDAY))
  for weekday in rectified_list:
      font = pygame.font.Font(filename='freesansbold.ttf', size=16)
      global _weekday_name_text
      _weekday_name_text.append(font.render(weekday, antialias=True, bgcolor=_background_color, color=_text_colour))

  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())

  try:
    global _service
    _service = build("calendar", "v3", credentials=creds)

    # Call the Calendar API.
    # Get available calendars.
    calendar_list = _service.calendarList().list().execute()
    calendars = calendar_list.get("items", [])

    if not calendars:
      print("No calendars found.")
      return

    print("Calendars:")
    # Prints the start and name of the next 10 events
    global _family_calendar_id
    for cal in calendars:
      print(cal)
      if cal["summary"] == "Family":
          _family_calendar_id = cal["id"]

    if not _family_calendar_id:
        print("No family calendar found")
        return

    refresh_calendar()
  except HttpError as error:
    print(f"An error occurred: {error}")

def refresh_calendar():
    # Get calendar events.
    print("Getting the events of this month")
    weekday_of_1st, day_count = calendar.monthrange(_day_in_focus.year, _day_in_focus.month)
    for day in range(day_count):
        day_dt = datetime.datetime(tzinfo=datetime.timezone.utc, year=_day_in_focus.year,
                                               month=_day_in_focus.month, day=day+1)
        day_iso = day_dt.isoformat()
        tomorrow_iso = (day_dt + datetime.timedelta(days=1)).isoformat()
        events_result = (
            _service.events()
            .list(
    #             calendarId="primary",
                calendarId=_family_calendar_id,
                timeMin=day_iso,
                timeMax=tomorrow_iso,
                maxResults=10,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        day_events = Day(events_result.get("items", []))
        _days.append(day_events)

pgzrun.go()
