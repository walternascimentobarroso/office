"""Supplier ORM model."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.company import Company


class Supplier(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Company supplier / vendor."""

    __tablename__ = "suppliers"
    __table_args__ = (
        Index(
            "ix_suppliers_company_id_active",
            "company_id",
            postgresql_where=text("deleted_at IS NULL"),
        ),
    )

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="RESTRICT"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    contact_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    email: Mapped[str | None] = mapped_column(Text, nullable=True)
    phone: Mapped[str | None] = mapped_column(Text, nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    tax_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    company: Mapped["Company"] = relationship(back_populates="suppliers", lazy="selectin")
