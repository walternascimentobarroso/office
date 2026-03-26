"""Shared schema primitives."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ORMReadModel(BaseModel):
    """Base model for ORM -> API serialization."""

    model_config = ConfigDict(from_attributes=True)


class AuditReadModel(ORMReadModel):
    """Audit fields shared by read schemas."""

    id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None
