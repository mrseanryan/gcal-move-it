"""
For a given event, calculate the target day of month, for the target month and year.
"""

import date_utils


def calculate_day_of_month_for_event(event, this_year, target_month):
    source_date = date_utils.event_start_date(event)

    target_day = source_date.day

    dest_month_days = date_utils.days_in_month(this_year, target_month)

    # If target month has less days, then use the last day
    if (source_date.day > dest_month_days):
        dest_day = dest_month_days
    return target_day
