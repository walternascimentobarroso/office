# -*- coding: utf-8 -*-
"""Helpers for writing openpyxl worksheets with merged cell ranges."""

from __future__ import annotations

from typing import Any, cast

from openpyxl.cell.cell import Cell, MergedCell
from openpyxl.worksheet.worksheet import Worksheet


def resolve_writable_cell(ws: Worksheet, cell_ref: str) -> Cell:
    """Return the anchor cell for ``cell_ref`` (top-left if inside a merge)."""

    cell = ws[cell_ref]
    if not isinstance(cell, MergedCell):
        return cast("Cell", cell)
    for merged in ws.merged_cells.ranges:
        if cell.coordinate in merged:
            return cast(
                "Cell",
                ws.cell(row=merged.min_row, column=merged.min_col),
            )
    return cast("Cell", cell)


def set_cell_value(ws: Worksheet, cell_ref: str, value: Any) -> None:
    """Assign ``value`` to a cell, respecting merged ranges."""

    resolve_writable_cell(ws, cell_ref).value = value
