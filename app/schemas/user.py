"""User schemas."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import AuditReadModel


class UserRoleRead(BaseModel):
    """Role information embedded in user responses."""

    id: UUID
    name: str
    description: str | None = None


class UserCreate(BaseModel):
    """Payload to create a user."""

    name: str = Field(min_length=1, max_length=255)
    email: str = Field(min_length=1, max_length=320)
    role_ids: list[UUID] = Field(default_factory=list)


class UserUpdate(BaseModel):
    """Payload to update a user."""

    name: str | None = Field(default=None, min_length=1, max_length=255)
    email: str | None = Field(default=None, min_length=1, max_length=320)
    role_ids: list[UUID] | None = None


class UserRead(AuditReadModel):
    """User response model."""

    company_id: UUID
    name: str
    email: str
    roles: list[UserRoleRead] = Field(default_factory=list)
