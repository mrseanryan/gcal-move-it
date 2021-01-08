"""
For a given event, calculate the target day of month, for the target month and year.
"""

from datetime import date

import date_utils


def calculate_day_of_month_for_source_date(source_date, target_year, target_month):
    target_day = source_date.day

    target_month_days = date_utils.days_in_month(target_year, target_month)

    # If target month has less days, then use the last day
    if (target_day > target_month_days):
        target_day = target_month_days
    return target_day


def calculate_target_date(date_context, source_date, target_date_option):
    target_month_value = date_utils.target_month(
        date_context, target_date_option)
    target_day = calculate_day_of_month_for_source_date(
        source_date, date_utils.target_year(date_context), target_month_value.month)

    target_date = date(target_month_value.year,
                       target_month_value.month, target_day)

    if (target_date_option != None):
        target_date = target_date_option

    return target_date
