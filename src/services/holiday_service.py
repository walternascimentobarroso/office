# -*- coding: utf-8 -*-
"""Service for holiday processing"""

from typing import List, Set


class HolidayService:
    """Service for processing holiday data"""

    @staticmethod
    def process_holidays(holidays: List[int]) -> Set[int]:
        """Convert holidays list to validated set"""
        valid_holidays = set()
        for holiday in holidays:
            if isinstance(holiday, int) and 1 <= holiday <= 31:
                valid_holidays.add(holiday)
        return valid_holidays