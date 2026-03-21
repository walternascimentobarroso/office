# -*- coding: utf-8 -*-
"""Mapa KM report service."""

import logging
from datetime import date
from typing import Any, Dict, List

from openpyxl.worksheet.worksheet import Worksheet

from src.core.business_calendar import last_weekday_of_month
from src.core.excel_cells import set_cell_value
from src.core.utils import load_json_mapping
from src.services.base_excel_service import BaseExcelService, fill_entry_row_cells
from src.services.date_service import DateService

logger = logging.getLogger(__name__)


class MapaKmService(BaseExcelService):
    """Service for generating Mapa KM Excel reports."""

    def _calendar_style_row_bounds(self) -> tuple[int, int]:
        """Template lists days 1–28 in column A (rows 9–36)."""

        return (9, 36)

    def __init__(self) -> None:
        template_path = "src/reports/mapa_km/template.xlsx"
        super().__init__(template_path)
        self.mappings = load_json_mapping("src/reports/mapa_km/mapping.json")

    def fill_header(
        self,
        ws: Worksheet,
        meta: Dict[str, Any],
        header_mappings: Dict[str, str],
    ) -> None:
        """Fill header cells; ``meta.mes`` (1–12) is written as Portuguese month name in the template."""

        for field, cell in header_mappings.items():
            value = meta.get(field)
            if value is None:
                continue
            if field == "mes" and isinstance(value, int):
                value = DateService.month_name_portuguese(value)
            set_cell_value(ws, cell, value)
            logger.debug("Filled header %s with %s: %s", cell, field, value)

    def fill_rows(
        self,
        ws: Worksheet,
        entries: List[Dict[str, Any]],
        row_mappings: Dict[str, Any],
    ) -> None:
        """Fill data rows from entries."""

        start_row = row_mappings.get("start_row", 9)
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
        """Fill footer from funcionario (incl. vehicle_matricula) and último dia útil."""

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
                    set_cell_value(ws, cell, value)
                    logger.debug("Filled footer %s with %s: %s", cell, field, value)
