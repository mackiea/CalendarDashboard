import datetime
import os.path
from calendar import Calendar
from datetime import tzinfo
from enum import Enum

from dateutil.tz import tzlocal
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pgzrun
import pygame
from dateutil import parser
import dateutil

# WIDTH = 1920
# HEIGHT = 1200
# GRIDHEIGHT = 1080

# WIDTH = 1920
# HEIGHT = 1080
# GRIDHEIGHT = HEIGHT-120

WIDTH = 1280
HEIGHT = 720
GRIDHEIGHT = HEIGHT-120

_weekday_length = WIDTH / 7
import calendar

WHITE = (255, 255, 255)
BACKGROUND_COLOUR = (200, 200, 255)
TEXT_COLOUR = (0, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 128)
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
_status = ""

def draw():
    screen.fill(BACKGROUND_COLOUR)
    if _monthText:
        month_rect = _monthText.get_rect()
        month_rect.center = (WIDTH/2, 50)
        screen.blit(_monthText, month_rect)

    # Draw eekdays.
    width = WIDTH / 7
    i=_weekday_length/2
    column = 0
    for weekday_name_text in _weekday_name_text:
        if (column % 2) == 0:
            column_colour = (200, 200, 100)
        else:
            column_colour = (200, 100, 200)
        pygame.draw.rect(surface=screen.surface, rect=Rect((width * column, 80), (width, GRIDHEIGHT+40)),
                         color=column_colour,
                         border_radius=15
        )
        rect = weekday_name_text.get_rect()
        rect.center = (i, 100)
        screen.blit(weekday_name_text, rect)
        i+=_weekday_length
        column = column + 1

    # Draw days.
    weekday_of_1st, day_count = calendar.monthrange(_day_in_focus.year, _day_in_focus.month)
    rowCount = 5
    if weekday_of_1st == calendar.SUNDAY and day_count == 28:
        rowCount = 4
    elif (weekday_of_1st == calendar.FRIDAY and day_count == 31) or (weekday_of_1st == calendar.SATURDAY and day_count >= 30):
        rowCount = 6

    column = (weekday_of_1st + 1) % 7
    row = 0
    height = GRIDHEIGHT / rowCount
    for d0 in range(day_count):
        day = d0 + 1
        x1 = width * column
        y1 = height * row + HEIGHT-GRIDHEIGHT
        if day == datetime.date.today().day:
            column_colour = (255, 255, 255)
            column_colour_2 = (255, 255, 255)
        elif (column % 2) == 0:
            column_colour = (255, 255, 200)
            column_colour_2 = (255, 255, 255)
        else:
            column_colour = (255, 200, 255)
            column_colour_2 = (255, 255, 255)
        # Draw rectangle.
        pygame.draw.rect(surface=screen.surface, rect=Rect((x1 + 1, y1 + 1),(width-1, height-1)), color=column_colour, border_radius=15)

        # Put day number.
        font = pygame.font.Font(filename='freesansbold.ttf', size=24)
        day_number = font.render(str(day), antialias=True, color=TEXT_COLOUR)
        rect = day_number.get_rect()
        rect.left = x1 + 11
        rect.top = y1 + 8
        pygame.draw.circle(surface=screen.surface, color = column_colour_2, center=(rect.left+rect.width/2, rect.top+rect.height/2), radius=14)
        screen.blit(day_number, rect)

        # Put events.
        day_events = _days[d0]
        line = 0
        for event in day_events.events:
            # print(str(event))
            is_all_day = False
            start = event["start"].get("dateTime")
            if start is None:
                start = event["start"].get("date")
                is_all_day = True

            # print(str(start))

            start_dt = parser.parse(start).astimezone()
            font.set_point_size(14)
            if is_all_day:
                event = font.render(str(event["summary"]), antialias=True, color=TEXT_COLOUR)
            else:
                event = font.render(str(start_dt.hour) + ":{:02d}".format(start_dt.minute) + " " + str(event["summary"]),
                                    antialias=True, color=TEXT_COLOUR)
            rect = event.get_rect()
            rect.left = x1 + 40
            rect.top = y1 + 5 + line * 20
            screen.blit(event, rect)

            line = line + 1

        column = column + 1
        if (column == 7):
            column = 0
            row = row + 1

        if _status is not None:
            status_line = font.render(_status, antialias=True, color=TEXT_COLOUR)
            rect = status_line.get_rect()
            rect.center = (WIDTH/2, HEIGHT/2)
            screen.blit(status_line, rect)


# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

def update():
    if not _initialized:
        initialize()

    global _monthText
    font = pygame.font.Font(filename='freesansbold.ttf', size=32)
    _monthText = font.render(calendar.month_name[_day_in_focus.month], antialias=True, color=TEXT_COLOUR)

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

def initialize():
  print("C A L E N D A R  D A S H B O A R D")
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  global _initialized
  _initialized = True

  screen.surface = pygame.display.set_mode(size=(1920, 1200), flags=pygame.constants.FULLSCREEN)

  # Set weekday headers.
  rectified_list = list(calendar.day_name)
  rectified_list.insert(0, rectified_list.pop(calendar.SUNDAY))
  for weekday in rectified_list:
      font = pygame.font.Font(filename='freesansbold.ttf', size=24)
      global _weekday_name_text
      _weekday_name_text.append(font.render(weekday, antialias=True, color=TEXT_COLOUR))

  # Load in Google API credentials.
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
    clock.schedule_interval(refresh_calendar, 60)
  except HttpError as error:
    print(f"An error occurred: {error}")

def refresh_calendar():
    # Get calendar events.
    global _days
    _days = []
    cursor = pygame.mouse.get_cursor()
    pygame.mouse.set_cursor(pygame.cursors.ball)
    print("Getting the events of this month")
    weekday_of_1st, day_count = calendar.monthrange(_day_in_focus.year, _day_in_focus.month)
    for day in range(day_count):
        day_dt = datetime.datetime(tzinfo=tzlocal(), year=_day_in_focus.year, month=_day_in_focus.month, day=day+1)
        day_iso = day_dt.isoformat()
        print(day_iso)
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
    pygame.mouse.set_cursor(cursor)


pgzrun.go()
