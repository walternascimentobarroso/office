# -*- coding: utf-8 -*-
"""Business-day helpers (weekdays only; no public holiday calendar)."""

from calendar import monthrange
from datetime import date, timedelta


def last_weekday_of_month(year: int, month: int) -> date:
    """Last calendar day of month that falls on Monday–Friday."""

    last_cal = monthrange(year, month)[1]
    d = date(year, month, last_cal)
    while d.weekday() >= 5:
        d -= timedelta(days=1)
    return d


def last_weekday_of_current_month(*, today: date | None = None) -> date:
    """Last weekday of the month containing ``today`` (default: system date)."""

    ref = today or date.today()
    return last_weekday_of_month(ref.year, ref.month)
