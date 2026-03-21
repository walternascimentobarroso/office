# -*- coding: utf-8 -*-
"""Configuration for Excel API (styling constants)."""

_config = None


class Config:
    """Shared Excel styling constants used by report generators."""

    # Weekend highlighting — openpyxl expects aRGB hex (AARRGGBB), no '#'
    WEEKEND_FILL = "FFFFFF00"
    # Holiday highlighting — #f6b26b
    HOLIDAY_FILL = "FFF6B26B"
    # Percentagem < 100% — cell background (#fbd4b4)
    PERCENTAGE_UNDER_100_FILL = "FFFBD4B4"


def get_config() -> Config:
    """Return the global configuration singleton."""

    global _config
    if _config is None:
        _config = Config()
    return _config
