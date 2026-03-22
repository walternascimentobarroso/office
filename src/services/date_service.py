# -*- coding: utf-8 -*-
"""Date service for weekend calculations and month resolution."""

from datetime import date

_EN_MONTH_NAMES = {
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

_EN_MONTH_NAMES_BY_NUM = tuple(
    name for name, _ in sorted(_EN_MONTH_NAMES.items(), key=lambda x: x[1])
)


class DateService:
    """Service for date-related calculations."""

    @staticmethod
    def resolve_month(month: int | str) -> int:
        """Resolve month (1–12 or English month name) to month number."""

        if isinstance(month, int):
            if not 1 <= month <= 12:
                msg = "month must be an integer between 1 and 12"
                raise ValueError(msg)
            return month
        if isinstance(month, str):
            num = _EN_MONTH_NAMES.get(month)
            if num is None:
                msg = f"Unknown month name: {month}"
                raise ValueError(msg)
            return num
        msg = "month must be int (1–12) or an English month name"
        raise TypeError(msg)

    @staticmethod
    def month_name_english(month: int) -> str:
        """English month label for Excel (1 = January, …, 12 = December)."""

        if not 1 <= month <= 12:
            msg = "month must be an integer between 1 and 12"
            raise ValueError(msg)
        return _EN_MONTH_NAMES_BY_NUM[month - 1]

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
        weekends: set[int] = set()
        for day in range(1, 32):
            try:
                d = date(year, month, day)
            except ValueError:
                continue
            if d.weekday() >= 5:
                weekends.add(day)
        return weekends
