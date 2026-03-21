# -*- coding: utf-8 -*-
"""Service for month parsing and validation"""

from typing import Union


class MonthService:
    """Service for handling month conversions and validation"""

    MONTH_NAMES = {
        "Janeiro": 1, "Fevereiro": 2, "Março": 3, "Abril": 4, "Maio": 5, "Junho": 6,
        "Julho": 7, "Agosto": 8, "Setembro": 9, "Outubro": 10, "Novembro": 11, "Dezembro": 12
    }

    @staticmethod
    def parse_month(month: Union[int, str]) -> int:
        """Convert month to integer representation"""
        if isinstance(month, int):
            if 1 <= month <= 12:
                return month
            raise ValueError(f"Month must be between 1 and 12, got {month}")
        elif isinstance(month, str):
            month_num = MonthService.MONTH_NAMES.get(month)
            if month_num:
                return month_num
            raise ValueError(f"Invalid month name: {month}")
        else:
            raise ValueError(f"Month must be int or string, got {type(month)}")

    @staticmethod
    def get_month_name(month: int) -> str:
        """Get Portuguese month name from number"""
        for name, num in MonthService.MONTH_NAMES.items():
            if num == month:
                return name
        raise ValueError(f"Invalid month number: {month}")