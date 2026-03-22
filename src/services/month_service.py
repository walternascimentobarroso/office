# -*- coding: utf-8 -*-
"""Service for month parsing and validation"""

from typing import Union


class MonthService:
    """Service for handling month conversions and validation"""

    MONTH_NAMES = {
        "January": 1,
        "February": 2,
        "March": 3,
        "April": 4,
        "May": 5,
        "June": 6,
        "July": 7,
        "August": 8,
        "September": 9,
        "October": 10,
        "November": 11,
        "December": 12,
    }

    @staticmethod
    def parse_month(month: Union[int, str]) -> int:
        """Convert month to integer representation"""
        if isinstance(month, int):
            if 1 <= month <= 12:
                return month
            raise ValueError(f"Month must be between 1 and 12, got {month}")
        if isinstance(month, str):
            month_num = MonthService.MONTH_NAMES.get(month)
            if month_num:
                return month_num
            raise ValueError(f"Invalid month name: {month}")
        raise ValueError(f"Month must be int or string, got {type(month)}")

    @staticmethod
    def get_month_name(month: int) -> str:
        """Get English month name from number"""
        for name, num in MonthService.MONTH_NAMES.items():
            if num == month:
                return name
        raise ValueError(f"Invalid month number: {month}")
