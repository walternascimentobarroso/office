# -*- coding: utf-8 -*-
"""Configuration for Excel API"""

import os
from pathlib import Path
from src.core.exceptions import TemplateLoadError


class Config:
    """Configuration management for the Excel API service"""

    # Weekend highlighting — openpyxl expects aRGB hex (AARRGGBB), no '#'
    WEEKEND_FILL = "FFFFFF00"
    # Holiday highlighting — #f6b26b
    HOLIDAY_FILL = "FFF6B26B"
    # Percentagem < 100% — cell background (#fbd4b4)
    PERCENTAGE_UNDER_100_FILL = "FFFBD4B4"

    def __init__(self):
        # Get paths from environment or use defaults
        self.template_path = os.getenv(
            "TEMPLATE_PATH", "templates/excel_template.xlsx"
        )
        self.header_mapping_path = os.getenv(
            "HEADER_MAPPING_PATH", "templates/mappings/header_mapping.json"
        )
        self.rows_mapping_path = os.getenv(
            "ROWS_MAPPING_PATH", "templates/mappings/rows_mapping.json"
        )
        self.footer_mapping_path = os.getenv(
            "FOOTER_MAPPING_PATH", "templates/mappings/footer_mapping.json"
        )

        # Validate paths exist
        self._validate_paths()

    def _validate_paths(self) -> None:
        """Validate that all required files exist and are accessible"""

        paths_to_check = [
            (self.template_path, "Template file"),
            (self.header_mapping_path, "Header mapping file"),
            (self.rows_mapping_path, "Rows mapping file"),
            (self.footer_mapping_path, "Footer mapping file"),
        ]

        for path_str, name in paths_to_check:
            path = Path(path_str)
            if not path.exists():
                raise TemplateLoadError(f"{name} not found: {path_str}")
            if not path.is_file():
                raise TemplateLoadError(f"{name} is not a file: {path_str}")


# Global config instance
_config = None


def get_config() -> Config:
    """Get or create global config instance (singleton)"""

    global _config
    if _config is None:
        _config = Config()
    return _config
