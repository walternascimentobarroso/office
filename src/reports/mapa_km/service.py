# -*- coding: utf-8 -*-
"""Mapa KM report service"""

import logging
from typing import Dict, Any, List

from openpyxl.worksheet.worksheet import Worksheet

from src.services.base_excel_service import BaseExcelService
from src.services.style_service import StyleService
from src.core.utils import load_json_mapping


logger = logging.getLogger(__name__)


class MapaKmService(BaseExcelService):
    """Service for generating Mapa KM Excel reports"""

    def __init__(self, style_service: StyleService):
        template_path = "src/reports/mapa_km/template.xlsx"
        super().__init__(template_path, style_service)
        self.mappings = load_json_mapping("src/reports/mapa_km/mapping.json")

    def fill_header(self, ws: Worksheet, meta: Dict[str, Any], header_mappings: Dict[str, str]) -> None:
        """Fill header cells from meta data"""
        for field, cell in header_mappings.items():
            value = meta.get(field)
            if value is not None:
                ws[cell] = value
                logger.debug(f"Filled header {cell} with {field}: {value}")

    def fill_rows(self, ws: Worksheet, entries: List[Dict[str, Any]], row_mappings: Dict[str, Any]) -> None:
        """Fill data rows from entries"""
        start_row = row_mappings.get('start_row', 8)
        columns = row_mappings.get('columns', {})

        for i, entry in enumerate(entries):
            row_num = start_row + i
            for field, col in columns.items():
                value = entry.get(field)
                if value is not None:
                    cell = f"{col}{row_num}"
                    ws[cell] = value
                    logger.debug(f"Filled row {cell} with {field}: {value}")

    def fill_footer(self, ws: Worksheet, data: Dict[str, Any], footer_mappings: Dict[str, str]) -> None:
        """Fill footer cells from vehicle data"""
        vehicle = data.get('vehicle', {})
        if vehicle:
            for field, cell in footer_mappings.items():
                value = vehicle.get(field)
                if value is not None:
                    ws[cell] = value
                    logger.debug(f"Filled footer {cell} with {field}: {value}")

        # Calculate and fill ultimo_dia_util_mes if mapping exists
        if 'ultimo_dia_util_mes' in footer_mappings:
            # TODO: implement last business day calculation
            pass