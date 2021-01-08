"""
Utils for processing date fields of events.
"""

import datetime

from calendar import monthrange
from dateutil import relativedelta
from datetime import date


class DateContext:
    # today is instance of TodayAuto or TodayMock
    def __init__(self, today, source_month_index):
        self.today = today
        self.source_month_index = source_month_index


def days_in_month(year, month_index):
    return monthrange(year, month_index)[1]


def event_start_date(event):
    return parse_year_month_day(event['start']['date'])


def parse_year_month_day(date_string):
    return datetime.datetime.strptime(date_string, '%Y-%m-%d')


def target_year(date_context):
    # If source is December, then target is following year:
    if (date_context.source_month_index == 12):
        return source_year(date_context) + 1
    return source_year(date_context)


def source_year(date_context):
    # If source is December, then is from previous year:
    if (date_context.source_month_index == 12):
        if (date_context.today.this_month() == 12):
            return date_context.today.this_year()
        return date_context.today.this_year() - 1
    return date_context.today.this_year()


def days_source_month(date_context):
    daysInMonth = days_in_month(source_year(
        date_context), date_context.source_month_index)
    return daysInMonth


def target_month(date_context, target_date_option):
    if (target_date_option != None):
        return target_date_option

    return start_of_source_month(date_context) + relativedelta.relativedelta(months=1)


def start_of_source_month(date_context):
    return date(source_year(date_context), date_context.source_month_index, 1)
