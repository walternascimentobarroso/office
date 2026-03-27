"""Role schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.schemas.common import AuditReadModel


class RoleCreate(BaseModel):
    """Payload to create a role."""

    name: str = Field(min_length=1, max_length=128)
    description: str | None = Field(default=None, max_length=1024)


class RoleUpdate(BaseModel):
    """Payload to update a role."""

    name: str | None = Field(default=None, min_length=1, max_length=128)
    description: str | None = Field(default=None, max_length=1024)


class RoleRead(AuditReadModel):
    """Role response model."""

    name: str
    description: str | None = None
