# -*- coding: utf-8 -*-
"""Unit tests for asset Pydantic schemas."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.models.asset import AssetCategory, AssetStatus
from app.schemas.asset import AssetCreate, AssetUpdate


def test_asset_create_minimal() -> None:
    payload = AssetCreate(
        name="Laptop",
        price=Decimal("0.00"),
        category=AssetCategory.mine,
        status=AssetStatus.active,
    )
    assert payload.name == "Laptop"


def test_asset_create_rejects_warranty_before_purchase() -> None:
    with pytest.raises(ValidationError):
        AssetCreate(
            name="X",
            price=Decimal("1.00"),
            category=AssetCategory.mine,
            status=AssetStatus.active,
            purchase_date=date(2025, 6, 1),
            warranty_until=date(2025, 1, 1),
        )


def test_asset_update_rejects_warranty_before_purchase() -> None:
    with pytest.raises(ValidationError):
        AssetUpdate(
            purchase_date=date(2025, 6, 1),
            warranty_until=date(2025, 1, 1),
        )


def test_asset_create_rejects_negative_price() -> None:
    with pytest.raises(ValidationError):
        AssetCreate(
            name="X",
            price=Decimal("-1.00"),
            category=AssetCategory.mine,
            status=AssetStatus.active,
        )
