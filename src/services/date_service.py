# -*- coding: utf-8 -*-
"""Date service for weekend calculations"""

from datetime import date


class DateService:
    """Service for date-related calculations"""

    @staticmethod
    def get_weekend_days(month: int, year: int) -> set[int]:
        """
        Calculate which days in the given month are weekends (Saturday/Sunday).

        Args:
            month: Month number (1-12)
            year: Year number

        Returns:
            Set of day numbers (1-31) that are weekends
        """
        weekends = set()
        for day in range(1, 32):
            try:
                d = date(year, month, day)
                if d.weekday() >= 5:  # 5=Saturday, 6=Sunday
                    weekends.add(day)
            except ValueError:
                # Invalid day for month (e.g., Feb 30)
                continue
        return weekends