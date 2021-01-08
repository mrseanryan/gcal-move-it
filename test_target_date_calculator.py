from datetime import date
from parameterized import parameterized
import unittest

import date_utils
import target_date_calculator
import todays


class TestTargetDateCalculator(unittest.TestCase):
    @parameterized.expand([
        # Dec to Jan
        (2020, 12, date(2020, 12, 31), None, date(2021, 1, 31)),
        (2020, 12, date(2020, 12, 1), None, date(2021, 1, 1)),
        (2021, 1, date(2020, 12, 1), None, date(2021, 1, 1)),
        # End Jan to Feb - overflow
        (2021, 1, date(2021, 1, 30), None, date(2021, 2, 28)),
        (2021, 2, date(2021, 1, 30), None, date(2021, 2, 28)),
        # End Jan to Feb - no overflow
        (2021, 1, date(2021, 1, 28), None, date(2021, 2, 28)),
        (2021, 2, date(2021, 1, 28), None, date(2021, 2, 28)),
        (2021, 1, date(2021, 1, 27), None, date(2021, 2, 27)),
        (2021, 2, date(2021, 1, 27), None, date(2021, 2, 27)),
        # xxx
    ])
    def test_source_year(self, this_year, this_month, source_date, target_date_option, expected_target_date):
        # Act
        today = todays.TodayMock(this_year, this_month)
        date_context = date_utils.DateContext(today, source_date.month)

        actual_target_date = target_date_calculator.calculate_target_date(
            date_context, source_date, target_date_option)
        self.assertEqual(expected_target_date, actual_target_date)
