# -*- coding: utf-8 -*-
"""Base Excel service with template method pattern for report generation"""

import logging
from abc import ABC, abstractmethod
from io import BytesIO
from pathlib import Path
from typing import Dict, Any, List

from openpyxl import load_workbook
from openpyxl.styles import PatternFill

from src.services.style_service import StyleService


logger = logging.getLogger(__name__)


class BaseExcelService(ABC):
    """Base service for Excel report generation using template method pattern"""

    def __init__(self, template_path: str, style_service: StyleService):
        self.template_path = Path(template_path)
        self.style_service = style_service

    def generate(self, data: Dict[str, Any], mappings: Dict[str, Any]) -> BytesIO:
        """Template method for Excel generation"""
        logger.info(f"Generating Excel report from template: {self.template_path}")

        # Load template
        wb = load_workbook(self.template_path)
        ws = wb.active

        # Fill data
        self.fill_header(ws, data.get('meta', {}), mappings.get('header', {}))
        self.fill_rows(ws, data.get('entries', []), mappings.get('rows', {}))
        self.fill_footer(ws, data, mappings.get('footer', {}))

        # Apply styles
        self.apply_styles(ws, data)

        # Save to BytesIO
        output = BytesIO()
        wb.save(output)
        output.seek(0)

        logger.info("Excel report generated successfully")
        return output

    @abstractmethod
    def fill_header(self, ws, meta: Dict[str, Any], header_mappings: Dict[str, str]) -> None:
        """Fill header cells from meta data"""
        pass

    @abstractmethod
    def fill_rows(self, ws, entries: List[Dict[str, Any]], row_mappings: Dict[str, Any]) -> None:
        """Fill data rows from entries"""
        pass

    @abstractmethod
    def fill_footer(self, ws, data: Dict[str, Any], footer_mappings: Dict[str, str]) -> None:
        """Fill footer cells from additional data"""
        pass

    def apply_styles(self, ws, data: Dict[str, Any]) -> None:
        """Apply conditional styling for weekends and holidays"""
        month = data['meta']['mes']
        holidays = set(data.get('holidays', []))

        # Apply to column A (days)
        for row in range(8, 39):  # Assuming rows 8-38 for days
            cell = ws[f'A{row}']
            if cell.value and isinstance(cell.value, int):
                day = cell.value
                if self.style_service.is_weekend(month, day):
                    cell.fill = PatternFill(start_color="F0F0F0", end_color="F0F0F0", fill_type="solid")
                elif day in holidays:
                    cell.fill = PatternFill(start_color="FFFFE0", end_color="FFFFE0", fill_type="solid")