"""
Mockable 'Today' interface
"""

from datetime import date


class TodayAuto:
    def this_year(self):
        return date.today().year

    def this_month(self):
        return date.today().month


class TodayMock:
    def __init__(self, this_year, this_month):
        self._this_year = this_year
        self._this_month = this_month

    def this_year(self):
        return self._this_year

    def this_month(self):
        return self._this_month
