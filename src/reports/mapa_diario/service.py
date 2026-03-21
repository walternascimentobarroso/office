# -*- coding: utf-8 -*-
"""Mapa Diário report service."""

import logging
from datetime import date
from typing import Any, Dict, List

from openpyxl.worksheet.worksheet import Worksheet

from src.core.business_calendar import last_weekday_of_month
from src.core.excel_cells import set_cell_value
from src.core.nif_format_pt import format_nif_pt
from src.core.utils import load_json_mapping
from src.services.base_excel_service import BaseExcelService, fill_entry_row_cells
from src.services.date_service import DateService

logger = logging.getLogger(__name__)


class MapaDiarioService(BaseExcelService):
    """Service for generating Mapa Diário Excel reports."""

    def __init__(self) -> None:
        template_path = "src/reports/mapa_diario/template.xlsx"
        super().__init__(template_path)
        self.mappings = load_json_mapping("src/reports/mapa_diario/mapping.json")

    def fill_header(
        self,
        ws: Worksheet,
        meta: Dict[str, Any],
        header_mappings: Dict[str, str],
    ) -> None:
        """Fill header cells from meta data."""

        for field, cell in header_mappings.items():
            value = meta.get(field)
            if value is None:
                continue
            if field == "nif":
                value = format_nif_pt(value)
            set_cell_value(ws, cell, value)
            logger.debug("Filled header %s with %s: %s", cell, field, value)

    def fill_rows(
        self,
        ws: Worksheet,
        entries: List[Dict[str, Any]],
        row_mappings: Dict[str, Any],
    ) -> None:
        """Fill data rows from entries."""

        start_row = row_mappings.get("start_row", 8)
        columns = row_mappings.get("columns", {})
        pct_fill = self._config.PERCENTAGE_UNDER_100_FILL

        for i, entry in enumerate(entries):
            row_num = start_row + i
            fill_entry_row_cells(
                ws,
                row_num,
                entry,
                columns,
                percentage_under_100_fill=pct_fill,
            )

    def fill_footer(
        self,
        ws: Worksheet,
        data: Dict[str, Any],
        footer_mappings: Dict[str, str],
    ) -> None:
        """Fill footer cells from funcionario data and computed last business day."""

        month = DateService.resolve_month(data["meta"]["mes"])
        year = date.today().year
        funcionario = data.get("funcionario") or {}

        for field, cell in footer_mappings.items():
            if field == "ultimo_dia_util_mes":
                set_cell_value(ws, cell, last_weekday_of_month(year, month))
                logger.debug("Filled footer %s with ultimo_dia_util_mes", cell)
                continue
            if isinstance(funcionario, dict):
                value = funcionario.get(field)
                if value is not None:
                    if field == "nif":
                        value = format_nif_pt(value)
                    set_cell_value(ws, cell, value)
                    logger.debug("Filled footer %s with %s: %s", cell, field, value)
