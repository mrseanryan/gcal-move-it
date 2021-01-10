from datetime import date
from parameterized import parameterized
import unittest

import date_utils
import target_date_calculator
import todays


class TestTargetDateCalculator(unittest.TestCase):
    @parameterized.expand([
        # Dec to Jan
        ('Dec to Jan', 2020, 12, date(2020, 12, 31), None, date(2021, 1, 31)),
        ('Dec to Jan', 2020, 12, date(2020, 12, 1), None, date(2021, 1, 1)),
        ('Dec to Jan', 2021, 1, date(2020, 12, 1), None, date(2021, 1, 1)),

        # Dec to Jan - pinned
        ('Dec to Jan - pinned to 1st Tuesday', 2020, 12,
         date(2020, 12, 1), None, date(2021, 1, 5), True),
        ('Dec to Jan - pinned to 1st Tuesday', 2021, 1,
         date(2020, 12, 1), None, date(2021, 1, 5), True),

        ('Dec to Jan - pinned to last Wednesday', 2020, 12,
         date(2020, 12, 30), None, date(2021, 1, 27), True),
        ('Dec to Jan - pinned to last Wednesday', 2021, 1,
         date(2020, 12, 30), None, date(2021, 1, 27), True),

        # Dec to Jan - NOT pinned
        ('Dec to Jan - not pinned', 2020, 12,
         date(2020, 12, 1), None, date(2021, 1, 1), False),
        ('Dec to Jan - not pinned', 2021, 1,
         date(2020, 12, 1), None, date(2021, 1, 1), False),
        ('Dec to Jan - not pinned', 2020, 12,
         date(2020, 12, 30), None, date(2021, 1, 30), False),
        ('Dec to Jan - not pinned', 2021, 1,
         date(2020, 12, 30), None, date(2021, 1, 30), False),

        # End Jan to Feb - overflow
        ('End Jan to Feb - overflow', 2021, 1,
         date(2021, 1, 30), None, date(2021, 2, 28)),
        ('End Jan to Feb - overflow', 2021, 2,
         date(2021, 1, 30), None, date(2021, 2, 28)),
        # End Jan to Feb - no overflow
        ('End Jan to Feb - no overflow', 2021, 1,
         date(2021, 1, 28), None, date(2021, 2, 28)),
        ('End Jan to Feb - no overflow', 2021, 2,
         date(2021, 1, 28), None, date(2021, 2, 28)),
        ('End Jan to Feb - no overflow', 2021, 1,
         date(2021, 1, 27), None, date(2021, 2, 27)),
        ('End Jan to Feb - no overflow', 2021, 2,
         date(2021, 1, 27), None, date(2021, 2, 27)),

        # Jan to Feb - pinned
        ('Jan to Feb - pinned - last Sat', 2021, 1,
         date(2021, 1, 30), None, date(2021, 2, 27), True),
        ('Jan to Feb - pinned - last Sat', 2021, 2,
         date(2021, 1, 30), None, date(2021, 2, 27), True),
        ('Jan to Feb - pinned - 2nd Mon', 2021, 1,
         date(2021, 1, 11), None, date(2021, 2, 8), True),
        ('Jan to Feb - pinned - 2nd Mon', 2021, 2,
         date(2021, 1, 11), None, date(2021, 2, 8), True),

        ('Jan to Feb - pinned - 4th Mon', 2021, 1,
         date(2021, 1, 25), None, date(2021, 2, 22), True),

        ('Jan to Feb - pinned - 4th Mon', 2021, 2,
         date(2021, 1, 25), None, date(2021, 2, 22), True),

        # Jan to Feb - NOT pinned
        ('Jan to Feb - pinned - last Sat', 2021, 1,
         date(2021, 1, 30), None, date(2021, 2, 28), False),
        ('Jan to Feb - pinned - last Sat', 2021, 2,
         date(2021, 1, 30), None, date(2021, 2, 28), False),
        ('Jan to Feb - pinned - 2nd Mon', 2021, 1,
         date(2021, 1, 11), None, date(2021, 2, 11), False),
        ('Jan to Feb - pinned - 2nd Mon', 2021, 2,
         date(2021, 1, 11), None, date(2021, 2, 11), False),
        ('Jan to Feb - pinned - 4th Mon', 2021, 1,
         date(2021, 1, 25), None, date(2021, 2, 25), False),
        ('Jan to Feb - pinned - 4th Mon', 2021, 2,
         date(2021, 1, 25), None, date(2021, 2, 25), False),

        # xxx tests for target_date_option
    ])
    def test_calculate_target_date(self, msg, this_year, this_month, source_date, target_date_option, expected_target_date, is_pinned_to_day=False):
        # Act
        today = todays.TodayMock(this_year, this_month)
        date_context = date_utils.DateContext(today, source_date.month)

        actual_target_date = target_date_calculator.calculate_target_date(
            date_context, source_date, is_pinned_to_day, target_date_option)
        self.assertEqual(expected_target_date, actual_target_date, msg)
