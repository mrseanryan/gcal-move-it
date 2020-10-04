#! python3
"""
gcal_move_it.py
Author: Sean Ryan
Version: 1.3

Uses the Google Calendar API to bulk process events:

# clean:
- clean descriptions that have doubled-up URLs

Usage: gcal_move_it.py clean <month 1..12> [options]

# move:
- Move non-recurring events from one month to the next month.
- Only events that occurred before today are moved.

Usage: gcal_move_it.py move <source month 1..12> [options]

The options are:
[-b blacklist - Specify a blacklist to exclude some events]
[-d dryrun - Perform a dry run, without actually modifying the calendar]
[-h help]
[-t targetdate - Specify an exact target date (instead of the default which is 'one month later')]
[-w whitelist - Specify a whitelist to include only some events]

Examples:
gcal_move_it.py clean 1
gcal_move_it.py move 1
gcal_move_it.py move 1 -w urgent;important
gcal_move_it.py move 1 -b "cancelled;^done" -d -w urgent;important
"""

from __future__ import print_function
from babel.dates import format_date
from calendar import monthrange
from optparse import OptionParser
from functools import reduce
import getopt
import datetime
from datetime import date
from dateutil import relativedelta
import pickle
import os.path
import sys
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

import description_cleaner

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar.events']

# usage() - prints out the usage text, from the top of this file :-)


def usage():
    print (__doc__)


def parse_year_month_day(date_string):
    return datetime.datetime.strptime(date_string, '%Y-%m-%d')


def split_exlude_empty(text, separator):
    return list(filter(None, text.split(separator)))


# optparse - parse the args
parser = OptionParser(
    usage='%prog <source month 1..12> [options]')
parser.add_option('-b', '--blacklist', dest='blacklist', default="",
                  help="Blacklist: pass only events that do not match any of these ; separated texts. ^ means 'starts with', '=x' means 'exactly matches x'")
parser.add_option('-d', '--dryrun', dest='is_dry_run', action='store_const',
                  const=True, default=False,
                  help='Perform a dry run: do not modify the calendar')
parser.add_option('-t', '--targetdate', dest='target_date', default='',
                  help='Move to this date (instead of adding 1 month). Format: yyyy-mm-dd')
parser.add_option('-w', '--whitelist', dest='whitelist', default="",
                  help='Whitelist: pass any events that contain one of these ; separated texts.')

(options, args) = parser.parse_args()
if (len(args) != 2):
    usage()
    sys.exit(2)

blacklist = split_exlude_empty(options.blacklist, ';')
is_dry_run = options.is_dry_run
command = args[0]
sourceMonthIndex = int(args[1])
target_date = None
if any(options.target_date):
    target_date = parse_year_month_day(options.target_date)
whitelist = split_exlude_empty(options.whitelist, ';')


def event_start_date(event):
    return parse_year_month_day(event['start']['date'])


def is_multi_day(event):
    if ('date' in event['start'] and
            'date' in event['end']
            ):
        start_date = event_start_date(event)
        end_date = parse_year_month_day(event['end']['date'])
        delta = end_date - start_date
        return delta.days > 1  # A whole-day event actually ends on the next day!

    return False


def is_in_source_month(event):
    if ('date' in event['start']):
        start_date = event_start_date(event)
        return start_date.month == sourceMonthIndex

    return False


def matches_blacklist_entry(summary, black):
    if(black.startswith('^')):
        return summary.startswith(black[1:])
    if(black.startswith('=')):
        return summary == black[1:]
    return black in summary


def summary_passes_blacklist(summary):
    if (not any(blacklist)):
        return True

    return all(not matches_blacklist_entry(summary, b) for b in blacklist)


def summary_passes_whitelist(summary):
    if (not any(whitelist)):
        return True

    return any(w in summary for w in whitelist)


def filter_event(event):
    """
    # Filter the events:
    # - following white and black lists
    # - all-day, for 1 day
    # - not a timed event (is all-day)
    # - not recurring
    """
    if (not 'start' in event):
        return False
    summary = event['summary'].lower()

    return (('start' in event) and  # else is multi-day event, which we skip
            # note: not checking for 'recurringEventId' since if the event was manually moved, then it probably got forgotten, and SHOULD be moved to next month
            not ('recurrence' in event) and
            summary_passes_blacklist(summary) and
            summary_passes_whitelist(summary) and
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


def days_in_month(year, month_index):
    return monthrange(year, month_index)[1]


def this_year():
    return date.today().year


def days_source_month():
    daysInMonth = days_in_month(this_year(), sourceMonthIndex)
    return daysInMonth


def dest_month():
    if (target_date != None):
        return target_date

    return start_of_source_month() + relativedelta.relativedelta(months=1)


def start_of_source_month():
    return date(this_year(), sourceMonthIndex, 1)


def get_events(service):
    # Call the Calendar API
    #
    # Get the events for the source month, that could be moved
    # - only past events (not from today)

    startOfMonth = start_of_source_month()
    daysInMonth = days_source_month()

    # The end of the month is the very start of the following day
    endOfMonth = date(this_year(), sourceMonthIndex,
                      daysInMonth) + datetime.timedelta(days=1)

    startOfToday = date.today()
    maxDate = min(endOfMonth, startOfToday)

    print('Getting events in range: ' +
          date_to_string(startOfMonth) + ' - ' + date_to_string(maxDate))

    return get_events_from_service(service, startOfMonth, maxDate)


def date_to_wire_format(dest_date):
    return dest_date.strftime('%Y-%m-%d')


def update_event_via_service(event, service):
    service.events().update(calendarId='primary',
                            eventId=event['id'],
                            body=event
                            ).execute()


def move_event_to_via_service(event, dest_date, service):
    startDate = {'date': date_to_wire_format(dest_date)}
    endDate = {'date': date_to_wire_format(
        dest_date + datetime.timedelta(days=1))}

    event['start'] = startDate
    event['end'] = endDate

    update_event_via_service(event, service)


def move_event_to(event, dest_date, service):
    print("--> " + date_to_string(dest_date))
    if not is_dry_run:
        move_event_to_via_service(event, dest_date, service)


def move_event(event, dest_month_value, dest_month_days, service):
    # If dest month has less days, then use the last day
    source_date = event_start_date(event)
    dest_day = source_date.day
    if (source_date.day > dest_month_days):
        dest_day = dest_month_days
    dest_date = date(dest_month_value.year, dest_month_value.month, dest_day)

    if (target_date != None):
        dest_date = target_date
    move_event_to(event, dest_date, service)


def ilen(iterable):
    return reduce(lambda sum, element: sum + 1, iterable, 0)


def list_size_as_text(events):
    return str(ilen(events))


def set_event_summary_via_service(event, clean_desc, service):
    event['description'] = clean_desc
    update_event_via_service(event, service)


def dump_desc(original_description, clean_desc):
    print (">>-- FROM --<<")
    print (original_description)
    print (">>--  TO  --<<")
    print(clean_desc)
    print (">>-- ---- --<<")
    print()


def clean_event(event, service):
    if(not('description' in event)):
        return False

    original_description = event['description']
    clean_desc = description_cleaner.clean_description(original_description)
    if(clean_desc != original_description):
        dump_desc(original_description, clean_desc)
        if not is_dry_run:
            set_event_summary_via_service(event, clean_desc, service)
        return True
    return False


def process_events_clean(filtered_events, service):
    events_cleaned = 0
    for event in filtered_events:
        # To debug, uncomment here:
        # import pdb
        # pdb.set_trace()
        #
        print(date_to_string(event_start_date(event)), event['summary'])
        if (clean_event(event, service)):
            events_cleaned += 1

    print (f"{events_cleaned} events have a 'dirty' description")

    if is_dry_run:
        print ("(dry run) No events were modified")
    else:
        print (f"{events_cleaned} events were updated to have a clean description")


def process_events_move(filtered_events, service):
    dest_month_value = dest_month()
    dest_month_days = days_in_month(
        dest_month_value.year, dest_month_value.month)

    for event in filtered_events:
        # To debug, uncomment here:
        # import pdb
        # pdb.set_trace()
        #
        print(date_to_string(event_start_date(event)), event['summary'])
        move_event(event, dest_month_value, dest_month_days, service)

    if is_dry_run:
        print ("(dry run) No events were modified")
    else:
        print (list_size_as_text(filtered_events) + " events were modified")


def main():
    service = connect_to_calendar_service()

    events = get_events(service)

    if not events:
        print('No upcoming events found.')

    filtered_events = list(filter(filter_event, events))

    sorted_and_filtered = sorted(
        filtered_events, key=lambda event: event_start_date(event))

    print ("Processing total of " + list_size_as_text(events) +
           " events filtered down to " + list_size_as_text(filtered_events) + "...")

    if (command == "clean"):
        process_events_clean(sorted_and_filtered, service)
    elif (command == "move"):
        process_events_move(sorted_and_filtered, service)
    else:
        print(f"Unknown command '{command}'")
        usage()


if __name__ == '__main__':
    main()