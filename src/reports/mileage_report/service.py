# -*- coding: utf-8 -*-
"""Mileage (KM) report Excel generation service."""

import logging
from datetime import date
from typing import Any, Dict, List

from openpyxl.worksheet.worksheet import Worksheet

from src.core.business_calendar import last_weekday_of_month
from src.core.excel_cells import set_cell_value
from src.core.tax_id_format_pt import format_pt_tax_id
from src.core.utils import load_json_mapping
from src.reports.mileage_report.distance_km_value import parse_distance_km_value
from src.services.base_excel_service import BaseExcelService, row_for_calendar_entry
from src.services.date_service import DateService

logger = logging.getLogger(__name__)


class MileageReportService(BaseExcelService):
    """Service for generating mileage report Excel files."""

    def _calendar_style_row_bounds(self) -> tuple[int, int]:
        """Template lists days 1–28 in column A (rows 9–36)."""

        return (9, 36)

    def __init__(self) -> None:
        template_path = "src/reports/mileage_report/template.xlsx"
        super().__init__(template_path)
        self.mappings = load_json_mapping("src/reports/mileage_report/mapping.json")

    def fill_header(
        self,
        ws: Worksheet,
        meta: Dict[str, Any],
        header_mappings: Dict[str, str],
    ) -> None:
        """Fill header cells; ``month`` (1–12) is written as Portuguese month name in the template."""

        for field, cell in header_mappings.items():
            value = meta.get(field)
            if value is None:
                continue
            if field == "month" and isinstance(value, int):
                value = DateService.month_name_portuguese(value)
            elif field == "tax_id":
                value = format_pt_tax_id(value)
            set_cell_value(ws, cell, value)
            logger.debug("Filled header %s with %s: %s", cell, field, value)

    def fill_rows(
        self,
        ws: Worksheet,
        entries: List[Dict[str, Any]],
        row_mappings: Dict[str, Any],
    ) -> None:
        """Fill data rows: ``distance_km`` parsed to numeric for column F."""

        start_row = row_mappings.get("start_row", 9)
        columns = row_mappings.get("columns", {})

        for i, entry in enumerate(entries):
            row_num = row_for_calendar_entry(start_row, entry, i)
            for field, col in columns.items():
                value = entry.get(field)
                if value is None:
                    continue
                addr = f"{col}{row_num}"
                if field == "distance_km":
                    parsed = parse_distance_km_value(value)
                    if parsed is not None:
                        set_cell_value(ws, addr, parsed)
                    continue
                set_cell_value(ws, addr, value)

    def fill_footer(
        self,
        ws: Worksheet,
        data: Dict[str, Any],
        footer_mappings: Dict[str, str],
    ) -> None:
        """Fill footer from employee data (incl. vehicle plate) and last business day."""

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
            fvalue = footer_values.get(field)
            if fvalue is not None:
                if field == "tax_id":
                    fvalue = format_pt_tax_id(fvalue)
                set_cell_value(ws, cell, fvalue)
                logger.debug("Filled footer %s with %s: %s", cell, field, fvalue)
