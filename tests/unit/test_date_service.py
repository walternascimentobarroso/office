# -*- coding: utf-8 -*-
"""Unit tests for DateService"""

import pytest
from datetime import date

from src.services.date_service import DateService


class TestDateService:
    """Test cases for DateService"""

    def test_get_weekend_days_march_2026(self):
        """Test weekend calculation for March 2026"""
        weekends = DateService.get_weekend_days(3, 2026)
        expected = {1, 7, 8, 14, 15, 21, 22, 28, 29}  # Saturdays and Sundays
        assert weekends == expected

    def test_get_weekend_days_february_2026(self):
        """Test weekend calculation for February 2026 (28 days)"""
        weekends = DateService.get_weekend_days(2, 2026)
        # Feb 2026: 1=Sun, 2=Mon, ..., 28=Sat
        expected = {1, 7, 8, 14, 15, 21, 22, 28}  # Saturdays and Sundays
        assert weekends == expected

    def test_get_weekend_days_january_2026(self):
        """Test weekend calculation for January 2026"""
        weekends = DateService.get_weekend_days(1, 2026)
        expected = {3, 4, 10, 11, 17, 18, 24, 25, 31}  # Saturdays and Sundays
        assert weekends == expected

    def test_get_weekend_days_december_2025(self):
        """Test weekend calculation for December 2025"""
        weekends = DateService.get_weekend_days(12, 2025)
        expected = {6, 7, 13, 14, 20, 21, 27, 28}  # Saturdays and Sundays
        assert weekends == expected

    def test_get_weekend_days_leap_year_february(self):
        """Test weekend calculation for February in leap year"""
        weekends = DateService.get_weekend_days(2, 2024)  # 2024 is leap year
        # Feb 2024: 1=Thu, 2=Fri, 3=Sat, ..., 29=Thu
        expected = {3, 4, 10, 11, 17, 18, 24, 25}  # Saturdays and Sundays
        assert weekends == expected

    def test_resolve_month_int(self) -> None:
        assert DateService.resolve_month(7) == 7

    def test_resolve_month_portuguese_name(self) -> None:
        assert DateService.resolve_month("Março") == 3

    def test_resolve_month_invalid_int(self) -> None:
        with pytest.raises(ValueError):
            DateService.resolve_month(13)

    def test_resolve_month_unknown_name(self) -> None:
        with pytest.raises(ValueError):
            DateService.resolve_month("NotAMonth")