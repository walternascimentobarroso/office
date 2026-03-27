"""Role ORM model."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.user_role import UserRole


class Role(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Represents a role that can be assigned to users."""

    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    user_roles: Mapped[list["UserRole"]] = relationship(
        back_populates="role",
        cascade="save-update, merge",
        lazy="selectin",
    )
