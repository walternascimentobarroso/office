# -*- coding: utf-8 -*-
"""Portuguese tax ID (NIF) display: digits grouped in threes (e.g. 123.456.789)."""


def format_pt_tax_id(value: object) -> object:
    """Return tax ID with a dot every three digits; non-digit characters are stripped first."""

    if value is None:
        return None
    digits = "".join(c for c in str(value).strip() if c.isdigit())
    if not digits:
        return value
    groups: list[str] = []
    rest = digits
    while rest:
        groups.append(rest[-3:])
        rest = rest[:-3]
    return ".".join(reversed(groups))
