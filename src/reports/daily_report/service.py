# -*- coding: utf-8 -*-
"""Daily report Excel generation service."""

import logging
from datetime import date
from typing import Any, Dict, List

from openpyxl.worksheet.worksheet import Worksheet

from src.core.business_calendar import last_weekday_of_month
from src.core.excel_cells import set_cell_value
from src.core.tax_id_format_pt import format_pt_tax_id
from src.core.utils import load_json_mapping
from src.services.base_excel_service import (
    BaseExcelService,
    fill_entry_row_cells,
    row_for_calendar_entry,
)
from src.services.date_service import DateService

logger = logging.getLogger(__name__)


class DailyReportService(BaseExcelService):
    """Service for generating daily report Excel files."""

    def __init__(self) -> None:
        template_path = "src/reports/daily_report/template.xlsx"
        super().__init__(template_path)
        self.mappings = load_json_mapping("src/reports/daily_report/mapping.json")

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
            if field == "tax_id":
                value = format_pt_tax_id(value)
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
            row_num = row_for_calendar_entry(start_row, entry, i)
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
        """Fill footer cells from employee data and computed last business day."""

        month = DateService.resolve_month(
            data.get("month") or (data.get("meta") or {}).get("month"),
        )
        year = date.today().year
        employee = data.get("employee") or {}

        footer_values = {
            "full_name": employee.get("name"),
            "address": employee.get("address"),
            "tax_id": employee.get("tax_id"),
            "vehicle_plate": employee.get("vehicle_plate"),
        }

        for field, cell in footer_mappings.items():
            if field == "last_business_day_of_month":
                set_cell_value(ws, cell, last_weekday_of_month(year, month))
                logger.debug("Filled footer %s with last_business_day_of_month", cell)
                continue
            value = footer_values.get(field)
            if value is not None:
                if field == "tax_id":
                    value = format_pt_tax_id(value)
                set_cell_value(ws, cell, value)
                logger.debug("Filled footer %s with %s: %s", cell, field, value)
