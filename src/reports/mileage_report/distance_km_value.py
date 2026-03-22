# -*- coding: utf-8 -*-
"""Parse ``distance_km`` from JSON (strings with thousands/decimals) to a float for Excel."""

import re


def parse_distance_km_value(value: object) -> float | None:
    """
    Convert API ``distance_km`` to float.

    **European-style input:** comma is always the **decimal** separator.
    E.g. ``12,5`` → 12.5; ``363,000`` → 363.0 (three decimal places, not 363 thousand).

    Integer part may use dot as thousands: ``1.234,56`` → 1234.56.

    Without comma: ``1.234.567`` (groups of 3) → thousands; otherwise ``float(s)``.
    """

    if value is None:
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return float(value)
    if isinstance(value, float):
        return value
    s = str(value).strip().replace(" ", "").replace("\u00a0", "")
    if not s:
        return None

    if "," in s:
        left, right = s.rsplit(",", 1)
        if not right.isdigit():
            return None
        left_clean = left.replace(".", "")
        if not re.fullmatch(r"-?\d+", left_clean):
            return None
        return float(f"{left_clean}.{right}")

    if re.fullmatch(r"\d{1,3}(\.\d{3})+", s):
        return float(s.replace(".", ""))
    try:
        return float(s)
    except ValueError:
        return None
