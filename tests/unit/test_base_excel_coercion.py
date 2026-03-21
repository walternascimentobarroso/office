# -*- coding: utf-8 -*-
"""Tests for day-of-month coercion (Excel float cells)."""

from src.services.base_excel_service import (
    _coerce_day_of_month,
    coerce_entry_day,
    row_for_calendar_entry,
)


def test_coerce_int() -> None:
    assert _coerce_day_of_month(15) == 15


def test_coerce_float_from_template() -> None:
    assert _coerce_day_of_month(1.0) == 1
    assert _coerce_day_of_month(31.0) == 31


def test_coerce_rejects_non_integer_float() -> None:
    assert _coerce_day_of_month(1.5) is None


def test_coerce_rejects_bool() -> None:
    assert _coerce_day_of_month(True) is None


def test_coerce_none() -> None:
    assert _coerce_day_of_month(None) is None


def test_coerce_entry_day_string() -> None:
    assert coerce_entry_day("4") == 4
    assert coerce_entry_day(" 15 ") == 15


def test_coerce_entry_day_invalid_string() -> None:
    assert coerce_entry_day("x") is None
    assert coerce_entry_day("") is None


def test_row_for_calendar_entry_uses_day() -> None:
    assert row_for_calendar_entry(8, {"day": 4}, 0) == 11


def test_row_for_calendar_entry_fallback_without_day() -> None:
    assert row_for_calendar_entry(8, {}, 2) == 10
