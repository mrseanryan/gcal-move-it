from parameterized import parameterized

import unittest
import date_utils
import todays


class TestDateUtils(unittest.TestCase):

    def check_source_year(self, this_year, this_month, source_month, expected_source_year):
        today = todays.TodayMock(this_year, this_month)

        context = date_utils.DateContext(today, source_month)

        # Act
        actual_source_year = date_utils.source_year(context)

        self.assertEqual(expected_source_year, actual_source_year)

    @parameterized.expand([
        (2020, 12, 12, 2020),
        (2021, 1, 12, 2020),
        (2021, 1, 1, 2021),
    ])
    def test_source_year(self, this_year, this_month, source_month, expected_source_year):
        # Act
        self.check_source_year(this_year, this_month,
                               source_month, expected_source_year)

    def check_target_year(self, this_year, this_month, source_month, expected_target_year):
        today = todays.TodayMock(this_year, this_month)

        context = date_utils.DateContext(today, source_month)

        # Act
        actual_target_year = date_utils.target_year(context)

        self.assertEqual(expected_target_year, actual_target_year)

    @parameterized.expand([
        (2020, 12, 12, 2021),
        (2021, 1, 12, 2021),
        (2021, 1, 11, 2021),
    ])
    def test_target_year(self, this_year, this_month, source_month, expected_target_year):
        # Act
        self.check_target_year(this_year, this_month,
                               source_month, expected_target_year)


if __name__ == '__main__':
    unittest.main()
