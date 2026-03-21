# -*- coding: utf-8 -*-
"""Tests for day-of-month coercion (Excel float cells)."""

from src.services.base_excel_service import _coerce_day_of_month


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
