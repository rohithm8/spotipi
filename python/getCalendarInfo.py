import datetime
import os.path
import json

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
SERVICE_ACCOUNT_FILE = os.path.join(os.path.dirname(__file__), '../config/spotipi-sva-creds.json')
CALENDAR_NAME = os.path.join(os.path.dirname(__file__), '../config/calendar-name.json')
dir = os.path.join(os.path.dirname(__file__), '../config')
coloridLUT = ("#ffffff", "#a4bdfc", "#7ae7bf", "#dbadff", "#ff887c", "#fbd75b", "#ffb878", "#46d6db", "#e1e1e1", "#5484ed", "#51b749", "#dc2127")


def getCalendarInfo():
    """
    Returns the next calendar event
    """
    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    try:
        service = build('calendar', 'v3', credentials=creds)

        # Call the Calendar API
        now = datetime.datetime.utcnow()  # 'Z' indicates UTC time
        later = now + datetime.timedelta(days=1)
        calendarId = json.load(open(CALENDAR_NAME))["calendarId"]
        events_result = service.events().list(calendarId=calendarId, timeMin=now.isoformat() + 'Z',
                                              timeMax=later.isoformat() + 'Z',
                                              maxResults=3, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])
        summarisedEvents = []

        if events:
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))
                color = coloridLUT[int(event.get('colorId', 0))]
                summarisedEvents.append((start, end, event['summary'], color))
        return summarisedEvents
    except HttpError as error:
        print('An error occurred: %s' % error)
        return None



if __name__ == '__main__':
    print(getCalendarInfo())
