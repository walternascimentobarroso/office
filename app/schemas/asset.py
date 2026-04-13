"""Asset (equipment) schemas."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field, model_validator

from app.models.asset import AssetCategory, AssetStatus
from app.schemas.common import AuditReadModel


class AssetCreate(BaseModel):
    """Payload to create an asset."""

    name: str = Field(min_length=1, max_length=512)
    description: str | None = Field(default=None, max_length=4096)
    price: Decimal = Field(ge=0)
    category: AssetCategory
    status: AssetStatus
    location: str | None = Field(default=None, max_length=1024)
    purchase_date: date | None = None
    warranty_until: date | None = None
    serial_number: str | None = Field(default=None, max_length=256)
    brand: str | None = Field(default=None, max_length=256)
    notes: str | None = Field(default=None, max_length=8192)

    @model_validator(mode="after")
    def warranty_after_purchase(self) -> AssetCreate:
        if (
            self.purchase_date is not None
            and self.warranty_until is not None
            and self.warranty_until < self.purchase_date
        ):
            msg = "warranty_until must be on or after purchase_date"
            raise ValueError(msg)
        return self


class AssetUpdate(BaseModel):
    """Partial update for an asset."""

    name: str | None = Field(default=None, min_length=1, max_length=512)
    description: str | None = Field(default=None, max_length=4096)
    price: Decimal | None = Field(default=None, ge=0)
    category: AssetCategory | None = None
    status: AssetStatus | None = None
    location: str | None = Field(default=None, max_length=1024)
    purchase_date: date | None = None
    warranty_until: date | None = None
    serial_number: str | None = Field(default=None, max_length=256)
    brand: str | None = Field(default=None, max_length=256)
    notes: str | None = Field(default=None, max_length=8192)

    @model_validator(mode="after")
    def warranty_after_purchase(self) -> AssetUpdate:
        if (
            self.purchase_date is not None
            and self.warranty_until is not None
            and self.warranty_until < self.purchase_date
        ):
            msg = "warranty_until must be on or after purchase_date"
            raise ValueError(msg)
        return self


class AssetRead(AuditReadModel):
    """Asset response."""

    company_id: UUID
    name: str
    description: str | None = None
    price: Decimal
    category: AssetCategory
    status: AssetStatus
    location: str | None = None
    purchase_date: date | None = None
    warranty_until: date | None = None
    serial_number: str | None = None
    brand: str | None = None
    notes: str | None = None
    invoice_storage_key: str | None = None
    invoice_file_url: str | None = None
