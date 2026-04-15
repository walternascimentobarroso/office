"""Supplier schemas."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.schemas.common import AuditReadModel


class SupplierCreate(BaseModel):
    """Payload to create a supplier."""

    name: str = Field(min_length=1, max_length=512)
    contact_name: str | None = Field(default=None, max_length=512)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=64)
    address: str | None = Field(default=None, max_length=1024)
    tax_id: str | None = Field(default=None, max_length=256)
    notes: str | None = Field(default=None, max_length=8192)


class SupplierUpdate(BaseModel):
    """Partial update for a supplier."""

    name: str | None = Field(default=None, min_length=1, max_length=512)
    contact_name: str | None = Field(default=None, max_length=512)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=64)
    address: str | None = Field(default=None, max_length=1024)
    tax_id: str | None = Field(default=None, max_length=256)
    notes: str | None = Field(default=None, max_length=8192)


class SupplierRead(AuditReadModel):
    """Supplier response."""

    company_id: UUID
    name: str
    contact_name: str | None = None
    email: str | None = None
    phone: str | None = None
    address: str | None = None
    tax_id: str | None = None
    notes: str | None = None
