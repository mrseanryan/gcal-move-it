#! python3
"""
gcal_move_it.py
Author: Sean Ryan
Version: 1.4

Uses the Google Calendar API to bulk process events:

# clean:
- clean descriptions that have doubled-up URLs or email addresses

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
gcal_move_it.py move 1 -w subject_1;subject_2 -t 2021-01-13
"""

from __future__ import print_function
from babel.dates import format_date
from optparse import OptionParser
from functools import reduce

import calendar
import getopt
import datetime
import pickle
import os.path
import sys

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

import date_utils
import description_cleaner
import target_date_calculator
import todays

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar.events']

# usage() - prints out the usage text, from the top of this file :-)


def usage():
    print(__doc__)


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
source_month_index = int(args[1])
target_date_option = None
if any(options.target_date):
    target_date_option = date_utils.parse_year_month_day(options.target_date)
whitelist = split_exlude_empty(options.whitelist, ';')

today = todays.TodayAuto()
date_context = date_utils.DateContext(today, source_month_index)
is_move = command == 'move'


def is_multi_day(event):
    if ('date' in event['start'] and
            'date' in event['end']
            ):
        start_date = date_utils.event_start_date(event)
        end_date = date_utils.parse_year_month_day(event['end']['date'])
        delta = end_date - start_date
        return delta.days > 1  # A whole-day event actually ends on the next day!

    return False


def is_in_source_month(event):
    if ('date' in event['start']):
        start_date = date_utils.event_start_date(event)
        return start_date.month == source_month_index

    return False


def is_before_max_date(event, date_context):
    max_date = date_utils.calculate_max_date(date_context, is_move)
    start_date = date_utils.event_start_date(event)

    return start_date < max_date


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
            is_in_source_month(event) and
            # is before the max date [occurs with *manually moved* recurring events] (bug in http request?)
            is_before_max_date(event, date_context)
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


def get_events(service, maxDate):
    # Call the Calendar API
    #
    # Get the events for the source month, that could be moved

    startOfMonth = date_utils.start_of_source_month(date_context)

    print('Getting events in range: ' +
          date_to_string(startOfMonth) + ' - ' + date_to_string(maxDate))

    return get_events_from_service(service, startOfMonth, maxDate)


def date_to_wire_format(target_date):
    return target_date.strftime('%Y-%m-%d')


def update_event_via_service(event, service):
    service.events().update(calendarId='primary',
                            eventId=event['id'],
                            body=event
                            ).execute()


def move_event_to_via_service(event, target_date, service):
    startDate = {'date': date_to_wire_format(target_date)}
    endDate = {'date': date_to_wire_format(
        target_date + datetime.timedelta(days=1))}

    event['start'] = startDate
    event['end'] = endDate

    update_event_via_service(event, service)


def move_event_to(event, target_date, service, is_pinned_to_day):
    suffix = ""
    if (is_pinned_to_day):
        target_day_of_week = calendar.weekday(
            target_date.year, target_date.month, target_date.day)
        suffix = f" [pinned to {calendar.day_name[target_day_of_week]}]"

    print("--> " + date_to_string(target_date) + suffix)
    if not is_dry_run:
        move_event_to_via_service(event, target_date, service)


def move_event(event, date_context, target_date_option, service):
    source_date = date_utils.event_start_date(event)

    is_pinned_to_day = (event['summary'].startswith(
        '[p]') or event['summary'].startswith('[pinned]'))

    target_date = target_date_calculator.calculate_target_date(
        date_context, source_date, is_pinned_to_day, target_date_option)

    move_event_to(event, target_date, service, is_pinned_to_day)


def ilen(iterable):
    return reduce(lambda sum, element: sum + 1, iterable, 0)


def list_size_as_text(events):
    return str(ilen(events))


def set_event_summary_via_service(event, clean_desc, service):
    event['description'] = clean_desc
    update_event_via_service(event, service)


def dump_desc(original_description, clean_desc):
    print(">>-- FROM --<<")
    print(original_description)
    print(">>--  TO  --<<")
    print(clean_desc)
    print(">>-- ---- --<<")
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
        print(date_to_string(date_utils.event_start_date(event)),
              event['summary'])
        if (clean_event(event, service)):
            events_cleaned += 1

    print(f"{events_cleaned} events have a 'dirty' description")

    if is_dry_run:
        print("(dry run) No events were modified")
    else:
        print(f"{events_cleaned} events were updated to have a clean description")


def summarize_event(event):
    summary = event['summary']
    if ('recurringEventId' in event):
        summary += ' (recurring, but moved)'
    return summary


def process_events_move(filtered_events, service):
    for event in filtered_events:
        # To debug, uncomment here:
        # import pdb
        # pdb.set_trace()
        #
        print(date_to_string(date_utils.event_start_date(event)),
              summarize_event(event))
        move_event(event, date_context, target_date_option, service)

    if is_dry_run:
        print("(dry run) No events were modified")
    else:
        print(list_size_as_text(filtered_events) + " events were modified")


def main():
    service = connect_to_calendar_service()

    events = get_events(
        service, date_utils.calculate_max_date(date_context, is_move))

    if not events:
        print('No upcoming events found.')

    filtered_events = list(filter(filter_event, events))

    sorted_and_filtered = sorted(
        filtered_events, key=lambda event: date_utils.event_start_date(event))

    print("Processing total of " + list_size_as_text(events) +
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
