# -*- coding: utf-8 -*-
"""Portuguese-style NIF display: digits grouped by threes (e.g. 123.456.789)."""


def format_nif_pt(value: object) -> object:
    """Return NIF with a dot every three digits; non-digit characters are stripped first."""

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
