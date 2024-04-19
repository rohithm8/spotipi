import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
dir = os.path.join(os.path.dirname(__file__), '../config')
coloridLUT = ("#ffffff", "#a4bdfc", "#7ae7bf", "#dbadff", "#ff887c", "#fbd75b", "#ffb878", "#46d6db", "#e1e1e1", "#5484ed", "#51b749", "#dc2127")


def getCalendarInfo():
    """
    Returns the next calendar event
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(os.path.join(dir, 'token.json')):
        creds = Credentials.from_authorized_user_file(os.path.join(dir, 'token.json'), SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f'Error refreshing credentials: {e}')
                return None
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                os.path.join(dir, 'credentials.json'), SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(os.path.join(dir, 'token.json'), 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('calendar', 'v3', credentials=creds)

        # Call the Calendar API
        now = datetime.datetime.utcnow()  # 'Z' indicates UTC time
        later = now + datetime.timedelta(days=1)
        events_result = service.events().list(calendarId='primary', timeMin=now.isoformat() + 'Z',
                                              timeMax=later.isoformat() + 'Z',
                                              maxResults=3, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])
        summarisedEvents = []
        
        # Prints the start and name of the next 10 events, if found
        if events:
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))
                color = coloridLUT[int(event.get('colorId', 0))]
                summarisedEvents.append((start, end, event['summary'], color))
        # return summarisedEvents
        return None
    except HttpError as error:
        print('An error occurred: %s' % error)
        return None



if __name__ == '__main__':
    print(getCalendarInfo())
