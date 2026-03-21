# -*- coding: utf-8 -*-
"""Unit tests for business day helpers"""

from datetime import date

from src.core.business_calendar import last_weekday_of_current_month, last_weekday_of_month


class TestLastWeekdayOfMonth:
    """Tests for last weekday of month"""

    def test_march_2026_last_day_is_weekday(self):
        """When month ends on a weekday, that day is returned."""
        assert last_weekday_of_month(2026, 3) == date(2026, 3, 31)

    def test_october_2026_month_ends_saturday(self):
        """When month ends on weekend, previous Friday is returned."""
        assert last_weekday_of_month(2026, 10) == date(2026, 10, 30)

    def test_last_weekday_of_current_month_with_reference(self):
        """last_weekday_of_current_month respects ``today`` override."""
        ref = date(2026, 10, 1)
        assert last_weekday_of_current_month(today=ref) == last_weekday_of_month(2026, 10)
