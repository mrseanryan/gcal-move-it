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
from babel.dates import format_date
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


def parse_year_month_day(date_string):
    return datetime.datetime.strptime(date_string, '%Y-%m-%d')


def is_multi_day(event):
    if ('date' in event['start'] and
        'date' in event['end']
        ):
        start_date = parse_year_month_day(event['start']['date'])
        end_date = parse_year_month_day(event['end']['date'])
        delta = end_date - start_date
        return delta.days > 1  # A whole-day event actually ends on the next day!

    return False


def is_in_source_month(event):
    if ('date' in event['start']):
        start_date = parse_year_month_day(event['start']['date'])
        return start_date.month == sourceMonthIndex

    return False


def filter_event(event):
    """
  1 Filter the events
    # - not starting with "k " or "done "
    # - all-day, for 1 day
    # - not recurring
    """
    if (not 'start' in event):
        return False
    summary = event['summary'].lower()
    return (('start' in event) and  # else is multi-day event, which we skip
            # note: not checking for 'recurringEventId' since if the event was manually moved, then it probably got forgotten, and SHOULD be moved to next month
            not ('recurrence' in event) and
            not summary.startswith("k ") and
            not summary.startswith("cancelled ") and
            not summary.startswith("done ") and
            not summary.startswith("n/a") and
            summary != "hol" and
            not is_multi_day(event) and
            not 'dateTime' in event['start'] and  # not a timed event
            # not in the next month (bug in http request?)
            is_in_source_month(event)
            )


def date_to_string(date):
    return format_date(date, locale='en')


def connect_to_calendar_service():
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

    return build('calendar', 'v3', credentials=creds)


def get_events_from_service(service, startOfMonth, maxDate):
    # 'Z' indicates UTC time
    timeMin = datetime.datetime.combine(
        startOfMonth, datetime.time()).isoformat() + 'Z'
    timeMax = datetime.datetime.combine(
        maxDate, datetime.time()).isoformat() + 'Z'

    events_result = service.events().list(calendarId='primary',
                                          maxResults=1000,
                                          timeMin=timeMin, timeMax=timeMax,
                                          timeZone='utc'
                                          # orderBy='startTime'
                                          ).execute()
    events = events_result.get('items', [])
    return events


def get_events(service):
    # Call the Calendar API
    #
    # Get the events for the source month, that could be moved
    # - only past events (not from today)

    thisYear = date.today().year
    startOfMonth = date(thisYear, sourceMonthIndex, 1)
    daysInMonth = monthrange(thisYear, sourceMonthIndex)[1]

    # The end of the month is the very start of the following day
    endOfMonth = date(thisYear, sourceMonthIndex,
                      daysInMonth) + datetime.timedelta(days=1)

    startOfToday = date.today()
    maxDate = min(endOfMonth, startOfToday)

    print('Getting events than can be moved and have date in range: ' +
          date_to_string(startOfMonth) + ' - ' + date_to_string(maxDate))

    return get_events_from_service(service, startOfMonth, maxDate)


def process_events(filtered_events):
    print ("Found " + str(len(filtered_events)) + " events to process")

    for event in filtered_events:
        # To debug, uncomment here:
        # import pdb
        # pdb.set_trace()
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'])

    # TODO xxx
    # move the events:
    # Xx always to following month
    # Xx following month could be next year!
    # Xx if dest month has less days, then use the last day


def main():
    service = connect_to_calendar_service()

    events = get_events(service)

    if not events:
        print('No upcoming events found.')

    filtered_events = filter(filter_event, events)

    process_events(filtered_events)


if __name__ == '__main__':
    main()
