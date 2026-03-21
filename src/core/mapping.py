# -*- coding: utf-8 -*-
"""Mapping loader for Excel cell and row configuration"""

import json
import re
from typing import Dict, Any
from src.core.exceptions import MappingError


class MappingLoader:
    """Loads and validates mapping configuration from JSON files"""

    @staticmethod
    def load_header_mapping(path: str) -> Dict[str, str]:
        """
        Load header field to cell mapping from JSON file

        Expected format:
        {
            "empresa": "B1",
            "nif": "D4",
            "mes": "J4"
        }
        """
        return MappingLoader._load_field_cell_mapping(path, "Header")

    @staticmethod
    def load_footer_mapping(path: str) -> Dict[str, str]:
        """
        Load footer field to cell mapping from JSON file

        Keys are API field names; ``ultimo_dia_util_mes`` is filled automatically
        (last Mon–Fri of the current month). Other keys map to ``funcionario``.
        """
        return MappingLoader._load_field_cell_mapping(path, "Footer")

    @staticmethod
    def _load_field_cell_mapping(path: str, kind: str) -> Dict[str, str]:
        try:
            with open(path, "r", encoding="utf-8") as f:
                mapping = json.load(f)

            if not isinstance(mapping, dict):
                raise MappingError(
                    f"{kind} mapping must be a dict, got {type(mapping).__name__}"
                )

            for field, cell in mapping.items():
                if not isinstance(cell, str):
                    raise MappingError(
                        f"Cell address for '{field}' must be string, got {type(cell).__name__}"
                    )
                if not _is_valid_cell_address(cell):
                    raise MappingError(f"Invalid cell address: {cell}")

            return mapping

        except json.JSONDecodeError as e:
            raise MappingError(f"Invalid JSON in {kind.lower()} mapping file: {e}")
        except FileNotFoundError:
            raise MappingError(f"{kind} mapping file not found: {path}")

    @staticmethod
    def load_rows_mapping(path: str) -> Dict[str, Any]:
        """
        Load rows configuration from JSON file

        Expected format:
        {
            "start_row": 8,
            "columns": {
                "day": "A",
                "description": "B",
                "location": "D",
                "start_time": "E",
                "end_time": "J"
            }
        }
        """
        try:
            with open(path, "r", encoding="utf-8") as f:
                mapping = json.load(f)

            if not isinstance(mapping, dict):
                raise MappingError(
                    f"Rows mapping must be a dict, got {type(mapping).__name__}"
                )

            # Validate required keys
            if "start_row" not in mapping:
                raise MappingError("Rows mapping must have 'start_row' key")
            if "columns" not in mapping:
                raise MappingError("Rows mapping must have 'columns' key")

            # Validate start_row
            if not isinstance(mapping["start_row"], int):
                raise MappingError(
                    f"start_row must be int, got {type(mapping['start_row']).__name__}"
                )
            if mapping["start_row"] < 1:
                raise MappingError(f"start_row must be >= 1, got {mapping['start_row']}")

            # Validate columns
            columns = mapping["columns"]
            if not isinstance(columns, dict):
                raise MappingError(
                    f"columns must be a dict, got {type(columns).__name__}"
                )

            for field, cell in columns.items():
                if not isinstance(cell, str):
                    raise MappingError(
                        f"Column address for '{field}' must be string, got {type(cell).__name__}"
                    )
                if not _is_valid_cell_address(cell):
                    raise MappingError(f"Invalid column address: {cell}")

            return mapping

        except json.JSONDecodeError as e:
            raise MappingError(f"Invalid JSON in rows mapping file: {e}")
        except FileNotFoundError:
            raise MappingError(f"Rows mapping file not found: {path}")


def _is_valid_cell_address(cell: str) -> bool:
    """Validate that a cell address is in correct Excel format (e.g., A1, B10, J4, or A)"""

    if not isinstance(cell, str) or len(cell) < 1:
        return False

    return bool(re.match(r"^[A-Z]+(?:[0-9]+)?$", cell))
