# -*- coding: utf-8 -*-
"""Unit tests for configuration module."""

import pytest

from src.core.config import Config, get_config


class TestConfig:
    """Tests for styling configuration."""

    def test_get_config_singleton(self) -> None:
        """get_config returns the same instance."""

        c1 = get_config()
        c2 = get_config()
        assert c1 is c2
        assert isinstance(c1, Config)

    def test_fill_constants_are_argb_hex(self) -> None:
        """Styling constants use openpyxl aRGB form."""

        c = Config()
        assert len(c.WEEKEND_FILL) == 8
        assert len(c.HOLIDAY_FILL) == 8
        assert len(c.PERCENTAGE_UNDER_100_FILL) == 8
