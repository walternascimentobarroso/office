# -*- coding: utf-8 -*-
"""Parse ``n_kms`` from JSON (strings with thousands/decimals) to a float for Excel."""

import re


def parse_n_kms_value(value: object) -> float | None:
    """
    Convert API ``n_kms`` to float.

    **Portuguese-style input:** a vírgula é sempre o separador **decimal**.
    Ex.: ``12,5`` → 12.5; ``363,000`` → 363.0 (três casas decimais, não 363 mil).

    Parte inteira pode usar ponto como milhares: ``1.234,56`` → 1234.56.

    Sem vírgula: ``1.234.567`` (grupos de 3) → milhares; caso contrário ``float(s)``.
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
