"""User-role association ORM model."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.role import Role
    from app.models.user import User


class UserRole(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Represents an assignment of one role to one user."""

    __tablename__ = "user_roles"
    __table_args__ = (
        UniqueConstraint("user_id", "role_id", name="uq_user_roles_user_role"),
        Index(
            "ix_user_roles_user_id_active",
            "user_id",
            postgresql_where=text("deleted_at IS NULL"),
        ),
        Index(
            "ix_user_roles_role_id_active",
            "role_id",
            postgresql_where=text("deleted_at IS NULL"),
        ),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("roles.id", ondelete="RESTRICT"),
        nullable=False,
    )

    user: Mapped["User"] = relationship(back_populates="user_roles", lazy="selectin")
    role: Mapped["Role"] = relationship(back_populates="user_roles", lazy="selectin")
