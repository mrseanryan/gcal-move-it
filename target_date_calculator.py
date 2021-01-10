"""
For a given event, calculate the target day of month, for the target month and year.
"""

from calendar import weekday
from datetime import date

import date_utils


def calculate_day_of_month_for_source_date(source_date, target_year, target_month):
    target_day = source_date.day

    target_month_days = date_utils.days_in_month(target_year, target_month)

    # If target month has less days, then use the last day
    if (target_day > target_month_days):
        target_day = target_month_days
    return target_day


def adjust_target_to_pinned_day_first_of_month(target_date, source_day_of_week):
    target_day = 1
    day_of_week_target_month_1st = weekday(
        target_date.year, target_date.month, target_day)

    if (source_day_of_week >= day_of_week_target_month_1st):
        target_day = source_day_of_week - day_of_week_target_month_1st + 1
    else:
        target_day = target_day + 7 - (day_of_week_target_month_1st -
                                       source_day_of_week)
    return date(target_date.year, target_date.month, target_day)


def adjust_target_to_pinned_day_last_of_month(target_date, source_day_of_week):
    days_in_target_month = date_utils.days_in_month(
        target_date.year, target_date.month)
    target_day = days_in_target_month
    while (weekday(target_date.year, target_date.month, target_day) != source_day_of_week):
        target_day += -1
    return date(target_date.year, target_date.month, target_day)


def adjust_target_to_pinned_day_handling_month_bounds(target_date, source_day_of_week):
    days_in_target_month = date_utils.days_in_month(
        target_date.year, target_date.month)
    target_day_of_week = weekday(
        target_date.year, target_date.month, target_date.day)
    diff = target_day_of_week - source_day_of_week
    target_day = target_date.day
    if (diff > 0):
        if (diff < 4):
            target_day = target_date.day - diff
        else:
            target_day += 7 - diff
            if (target_day > days_in_target_month):
                target_day = target_date.day - diff
    else:
        target_day -= diff
        if (target_day > days_in_target_month):
            target_day = target_date.day + (7 + diff)

    return date(target_date.year, target_date.month, target_day)


def adjust_target_to_pinned_day(target_date, source_date):
    # 0-6 ~ Mon-Sun
    source_day_of_week = weekday(
        source_date.year, source_date.month, source_date.day)

    target_day_of_week = weekday(
        target_date.year, target_date.month, target_date.day)

    if (target_day_of_week == source_day_of_week):
        return target_date

    # special case: first for that day within the month
    is_first = source_date.day <= 7
    if (is_first):
        return adjust_target_to_pinned_day_first_of_month(target_date, source_day_of_week)

    # special case: last for that day within the month
    is_last = date_utils.days_in_month(
        source_date.year, source_date.month) - source_date.day < 7
    if (is_last):
        return adjust_target_to_pinned_day_last_of_month(target_date, source_day_of_week)

    return adjust_target_to_pinned_day_handling_month_bounds(target_date, source_day_of_week)


def calculate_target_date(date_context, source_date, is_pinned_to_day, target_date_option):
    if (target_date_option != None):
        return target_date_option

    target_month_value = date_utils.target_month(
        date_context, target_date_option)
    target_day = calculate_day_of_month_for_source_date(
        source_date, date_utils.target_year(date_context), target_month_value.month)

    target_date = date(target_month_value.year,
                       target_month_value.month, target_day)

    if (is_pinned_to_day):
        return adjust_target_to_pinned_day(target_date, source_date)

    return target_date
