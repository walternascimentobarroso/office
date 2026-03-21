# -*- coding: utf-8 -*-
"""Service for Excel styling operations"""

import calendar
from datetime import datetime
from typing import Union


class StyleService:
    """Service for handling Excel styling logic"""

    MONTH_NAMES = {
        "Janeiro": 1, "Fevereiro": 2, "Março": 3, "Abril": 4, "Maio": 5, "Junho": 6,
        "Julho": 7, "Agosto": 8, "Setembro": 9, "Outubro": 10, "Novembro": 11, "Dezembro": 12
    }

    def is_weekend(self, month: Union[int, str], day: int) -> bool:
        """Check if a day in the given month is a weekend"""
        if isinstance(month, str):
            month_num = self.MONTH_NAMES.get(month)
            if not month_num:
                return False
        else:
            month_num = month

        # Use current year for calculation
        year = datetime.now().year
        try:
            weekday = calendar.weekday(year, month_num, day)
            return weekday >= 5  # Saturday = 5, Sunday = 6
        except ValueError:
            return False

    def is_holiday(self, day: int, holidays: set) -> bool:
        """Check if a day is in the holidays set"""
        return day in holidays