"""Company schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.schemas.common import AuditReadModel


class CompanyCreate(BaseModel):
    """Payload to create a company."""

    name: str = Field(min_length=1, max_length=255)
    tax_id: str = Field(min_length=1, max_length=64)
    address: str | None = Field(default=None, max_length=1024)


class CompanyUpdate(BaseModel):
    """Payload to update a company."""

    name: str | None = Field(default=None, min_length=1, max_length=255)
    tax_id: str | None = Field(default=None, min_length=1, max_length=64)
    address: str | None = Field(default=None, max_length=1024)


class CompanyRead(AuditReadModel):
    """Company response model."""

    name: str
    tax_id: str
    address: str | None = None
