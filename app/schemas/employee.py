"""Employee schemas."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import AuditReadModel


class EmployeeCreate(BaseModel):
    """Payload to create an employee."""

    name: str = Field(min_length=1, max_length=255)
    tax_id: str = Field(min_length=1, max_length=64)
    address: str | None = Field(default=None, max_length=1024)
    vehicle_plate: str | None = Field(default=None, max_length=32)


class EmployeeUpdate(BaseModel):
    """Payload to update an employee."""

    name: str | None = Field(default=None, min_length=1, max_length=255)
    tax_id: str | None = Field(default=None, min_length=1, max_length=64)
    address: str | None = Field(default=None, max_length=1024)
    vehicle_plate: str | None = Field(default=None, max_length=32)


class EmployeeRead(AuditReadModel):
    """Employee response model."""

    company_id: UUID
    name: str
    tax_id: str
    address: str | None = None
    vehicle_plate: str | None = None
