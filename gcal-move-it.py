"""
gcal-move-it.py
Author: Sean Ryan
Version: 1.0

Uses the Google Calendar API to move non-recurring events from one month to the next month.

Only events that occurred before today are moved.

Usage: gcal-move-it.py <source month 1..12> [options]

The options are:
[-d dryrun Perform a dry run, without actually modifying the calendar]
[-h help]

Example: gcal-move-it.py 1 -d
"""

from __future__ import print_function
from calendar import monthrange
from optparse import OptionParser
import getopt
import datetime
from datetime import date
import pickle
import os.path
import sys
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar.events']

# usage() - prints out the usage text, from the top of this file :-)


def usage():
    print (__doc__)


# optparse - parse the args
parser = OptionParser(
    usage='%prog <source month 1..12> [options]')
parser.add_option('-d', '--dryrun', dest='is_dry_run', action='store_const',
                  const=True, default=False,
                  help='Perform a dry run: do not modify the calendar')

(options, args) = parser.parse_args()
if (len(args) != 1):
    usage()
    sys.exit(2)

is_dry_run = options.is_dry_run
sourceMonthIndex = int(args[0])

"""
# Filter the events
# - not starting with "k " or "done "
# - all-day, for 1 day (so start.date == end.date)
# - not recurring
# - not default (blue) color
"""


def filter_event(event):
    if (not 'start' in event):
        return False
    summary = event['summary'].lower()
    # import pdb
    # pdb.set_trace()
    return (('start' in event) and  # else is multi-day event, which we skip
            not ('recurrance' in event) and
            not summary.startswith("k ") and
            not summary.startswith("done ") and
            not summary.startswith("n/a") and
            summary != "hol"
            )


def main():
    print('here!!! 1')

    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    # Call the Calendar API
    #
    # Get the events for the source month, that could be moved
    # - only past events (not from today)

    # xxx
    thisYear = date.today().year
    startOfMonth = date(thisYear, sourceMonthIndex, 1)
    daysInMonth = monthrange(thisYear, sourceMonthIndex)[1]

    # The end of the month is the very start of the following day
    endOfMonth = date(thisYear, sourceMonthIndex,
                      daysInMonth) + datetime.timedelta(days=1)

    timeMin = datetime.datetime.combine(
        startOfMonth, datetime.time()).isoformat() + 'Z'

    startOfToday = date.today()
    dateMax = min(endOfMonth, startOfToday)
    # 'Z' indicates UTC time
    timeMax = datetime.datetime.combine(
        dateMax, datetime.time()).isoformat() + 'Z'

    # xxx
    # import pdb
    # pdb.set_trace()

    print('Getting events than can be moved')
    events_result = service.events().list(calendarId='primary',
                                          maxResults=1000,
                                          timeMin=timeMin, timeMax=timeMax,
                                          timeZone='utc'
                                          # orderBy='startTime'
                                          ).execute()
    events = events_result.get('items', [])

    # xxx
    if not events:
        print('No upcoming events found.')

    filtered_events = filter(filter_event, events)

    for event in filtered_events:
        if ('start' in event):
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start, event['summary'])

    # xxx
    # move the events:
    # Xx always to following month
    # Xx following month could be next year!
    # Xx if dest month less days, then use the last day


print('here!!! 0')

if __name__ == '__main__':
    main()
