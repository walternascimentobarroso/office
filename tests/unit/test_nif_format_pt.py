# -*- coding: utf-8 -*-
"""Unit tests for Portuguese NIF display formatting."""

import pytest

from src.reports.mapa_km.nif_format import format_nif_pt


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("123456789", "123.456.789"),
        ("333333333", "333.333.333"),
        ("231423345", "231.423.345"),
        ("123.456.789", "123.456.789"),
        (123456789, "123.456.789"),
        (None, None),
    ],
)
def test_format_nif_pt_groups_of_three(raw: object, expected: object) -> None:
    assert format_nif_pt(raw) == expected


def test_format_nif_pt_no_digits_returns_original() -> None:
    assert format_nif_pt("abc") == "abc"
