"""
Utils for processing date fields of events.
"""

import datetime

from calendar import monthrange
from dateutil import relativedelta
from datetime import date


def days_in_month(year, month_index):
    return monthrange(year, month_index)[1]


def event_start_date(event):
    return parse_year_month_day(event['start']['date'])


def parse_year_month_day(date_string):
    return datetime.datetime.strptime(date_string, '%Y-%m-%d')


def target_year(today, sourceMonthIndex):
    # If source is December, then target is following year:
    if (sourceMonthIndex == 12):
        return source_year(today, sourceMonthIndex) + 1
    return source_year(today, sourceMonthIndex)


def source_year(today, sourceMonthIndex):
    # If source is December, then is from previous year:
    if (sourceMonthIndex == 12):
        if (today.this_month() == 12):
            return today.this_year()
        return today.this_year() - 1
    return today.this_year()


def days_source_month(today, sourceMonthIndex):
    daysInMonth = days_in_month(source_year(
        today, sourceMonthIndex), sourceMonthIndex)
    return daysInMonth


def target_month(today, target_date_option, sourceMonthIndex):
    if (target_date_option != None):
        return target_date_option

    return start_of_source_month(today, sourceMonthIndex) + relativedelta.relativedelta(months=1)


def start_of_source_month(today, sourceMonthIndex):
    return date(source_year(today, sourceMonthIndex), sourceMonthIndex, 1)
