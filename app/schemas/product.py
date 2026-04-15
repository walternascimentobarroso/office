"""Product schemas."""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import AuditReadModel


class ProductCreate(BaseModel):
    """Payload to create a product."""

    name: str = Field(min_length=1, max_length=512)
    price: Decimal = Field(ge=0)
    category: str = Field(min_length=1, max_length=256)
    active: bool = True


class ProductUpdate(BaseModel):
    """Partial update for a product."""

    name: str | None = Field(default=None, min_length=1, max_length=512)
    price: Decimal | None = Field(default=None, ge=0)
    category: str | None = Field(default=None, min_length=1, max_length=256)
    active: bool | None = None


class ProductRead(AuditReadModel):
    """Product response."""

    company_id: UUID
    name: str
    price: Decimal
    category: str
    active: bool
    image_storage_key: str | None = None
    image_url: str | None = None
