import datetime
import os.path
from enum import Enum

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pgzrun
import pygame
WIDTH = 1920
HEIGHT = 1200
_weekday_length = WIDTH / 7
import calendar

_white = (255, 255, 255)
_background_color = (200, 200, 255)
_text_colour = (0, 0, 0)
_green = (0, 255, 0)
_blue = (0, 0, 128)
_initialized = False
_monthText = None

_weekday_name_text = []

class Mode(Enum):
    Month=1
    Week=2
    Day=3
_mode = Mode.Month
_day_in_focus = datetime.date.today()

def draw():
    screen.fill(_background_color)
    screen.draw.circle((400, 300), 30, 'white')
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


    # for days_of_month in calendar.monthrange(year=_day_in_focus.year, month=_day_in_focus.month):
    #    pygame.draw.

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

def drawz(events):
    # Prints the start and name of the next 10 events
    for event in events:
      start = event["start"].get("dateTime", event["start"].get("date"))
      print(start, event["summary"])


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
    service = build("calendar", "v3", credentials=creds)

    # Call the Calendar API.
    # Get available calendars.
    calendar_list = service.calendarList().list().execute()
    calendars = calendar_list.get("items", [])

    if not calendars:
      print("No calendars found.")
      return

    print("Calendars:")
    # Prints the start and name of the next 10 events
    family_calendar_id = None
    for cal in calendars:
      print(cal)
      if cal["summary"] == "Family":
          family_calendar_id = cal["id"]

    if not family_calendar_id:
        print("No family calendar found")
        return

    # Get calendar events.
    now = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()
    print("Getting the upcoming 10 events")
    events_result = (
        service.events()
        .list(
#             calendarId="primary",
            calendarId=family_calendar_id,
            timeMin=now,
            maxResults=10,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    events = events_result.get("items", [])
    if not events:
      print("No upcoming events found.")
      return

  except HttpError as error:
    print(f"An error occurred: {error}")


pgzrun.go()
