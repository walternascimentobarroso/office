# -*- coding: utf-8 -*-
"""Tests for mileage ``distance_km`` parsing."""

from src.reports.mileage_report.distance_km_value import parse_distance_km_value


def test_parse_integer() -> None:
    assert parse_distance_km_value(363) == 363.0


def test_parse_string_decimal_comma_three_places() -> None:
    """363,000 = 363 with 3 decimal places (EU style), not 363 thousand."""

    assert parse_distance_km_value("363,000") == 363.0


def test_parse_string_decimal_comma() -> None:
    assert parse_distance_km_value("12,5") == 12.5


def test_parse_string_thousands_dot_then_decimal_comma() -> None:
    assert parse_distance_km_value("1.234,56") == 1234.56


def test_parse_string_plain() -> None:
    assert parse_distance_km_value("42") == 42.0


def test_parse_dot_thousands_no_comma() -> None:
    """Without comma: dots as thousands (e.g. European-style with dots only)."""

    assert parse_distance_km_value("1.234.567") == 1234567.0


def test_parse_none_and_bool() -> None:
    assert parse_distance_km_value(None) is None
    assert parse_distance_km_value(True) is None
