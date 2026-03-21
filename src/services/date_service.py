# -*- coding: utf-8 -*-
"""Date service for weekend calculations and month resolution."""

from datetime import date


_PT_MONTH_NAMES = {
    "Janeiro": 1,
    "Fevereiro": 2,
    "Março": 3,
    "Abril": 4,
    "Maio": 5,
    "Junho": 6,
    "Julho": 7,
    "Agosto": 8,
    "Setembro": 9,
    "Outubro": 10,
    "Novembro": 11,
    "Dezembro": 12,
}


class DateService:
    """Service for date-related calculations."""

    @staticmethod
    def resolve_month(mes: int | str) -> int:
        """Resolve meta.mes (1–12 or Portuguese month name) to month number."""

        if isinstance(mes, int):
            if not 1 <= mes <= 12:
                msg = "mes must be an integer between 1 and 12"
                raise ValueError(msg)
            return mes
        if isinstance(mes, str):
            num = _PT_MONTH_NAMES.get(mes)
            if num is None:
                msg = f"Unknown month name: {mes}"
                raise ValueError(msg)
            return num
        msg = "mes must be int (1–12) or a Portuguese month name"
        raise TypeError(msg)

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
