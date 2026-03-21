# -*- coding: utf-8 -*-
"""Tests for Mapa KM ``n_kms`` parsing."""

from src.reports.mapa_km.kms_value import parse_n_kms_value


def test_parse_integer() -> None:
    assert parse_n_kms_value(363) == 363.0


def test_parse_string_decimal_comma_three_places() -> None:
    """363,000 = 363 with 3 decimal places (PT), not 363 thousand."""

    assert parse_n_kms_value("363,000") == 363.0


def test_parse_string_decimal_comma() -> None:
    assert parse_n_kms_value("12,5") == 12.5


def test_parse_string_thousands_dot_then_decimal_comma() -> None:
    assert parse_n_kms_value("1.234,56") == 1234.56


def test_parse_string_plain() -> None:
    assert parse_n_kms_value("42") == 42.0


def test_parse_dot_thousands_no_comma() -> None:
    """Sem vírgula: pontos como milhares (ex.: modelo europeu só com pontos)."""

    assert parse_n_kms_value("1.234.567") == 1234567.0


def test_parse_none_and_bool() -> None:
    assert parse_n_kms_value(None) is None
    assert parse_n_kms_value(True) is None
