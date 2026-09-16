import os.path
import datetime
from dateutil.tz import tzlocal

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

import SuperCalendar
from Day import Day

class GoogleCalendar(SuperCalendar.SuperCalendar):

    family_calendar_id = None
    service = None
    def __init__(self, calendar_name):
        super().__init__()
        scopes = ["https://www.googleapis.com/auth/calendar.readonly"]
        # Load in Google API credentials.
        creds = None
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", scopes)
        # If there are no (valid) credentials available, let the user log in.
        if not creds:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", scopes)
            creds = flow.run_local_server(port=0)
        if creds.expired and creds.refresh_token:
                creds.refresh(Request())
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

        self.service = build("calendar", "v3", credentials=creds)

        # Call the Calendar API.
        # Get available calendars.
        calendar_list = self.service.calendarList().list().execute()
        calendars = calendar_list.get("items", [])

        if not calendars:
            print("No calendars found.")
            return

        print("Calendars:")
        # Prints the start and name of the next 10 events
        for cal in calendars:
            print(cal)
            if cal["summary"] == calendar_name:
                self.family_calendar_id = cal["id"]

        if not self.family_calendar_id:
            print("No family calendar found")

    def get_events(self, day, day_in_focus) -> Day:
        day_dt = datetime.datetime(tzinfo=tzlocal(), year=day_in_focus.year, month=day_in_focus.month, day=day)
        day_iso = day_dt.isoformat()
        tomorrow_iso = (day_dt + datetime.timedelta(hours=23, minutes=59)).isoformat()
        events_result = (
            self.service.events()
            .list(
                calendarId=self.family_calendar_id,
                timeMin=day_iso,
                timeMax=tomorrow_iso,
                maxResults=10,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        return Day(events=events_result.get("items", []), day=day)