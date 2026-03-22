# -*- coding: utf-8 -*-
"""Unit tests for Portuguese tax ID display formatting."""

import pytest

from src.core.tax_id_format_pt import format_pt_tax_id


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
def test_format_pt_tax_id_groups_of_three(raw: object, expected: object) -> None:
    assert format_pt_tax_id(raw) == expected


def test_format_pt_tax_id_no_digits_returns_original() -> None:
    assert format_pt_tax_id("abc") == "abc"
