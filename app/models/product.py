"""Product ORM model."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Index, Numeric, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.company import Company


class Product(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Company product / item for sale."""

    __tablename__ = "products"
    __table_args__ = (
        Index(
            "ix_products_company_id_active",
            "company_id",
            postgresql_where=text("deleted_at IS NULL"),
        ),
        Index(
            "ix_products_company_category",
            "company_id",
            "category",
            postgresql_where=text("deleted_at IS NULL"),
        ),
    )

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="RESTRICT"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    price: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    category: Mapped[str] = mapped_column(Text, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    image_storage_key: Mapped[str | None] = mapped_column(Text, nullable=True)

    company: Mapped["Company"] = relationship(back_populates="products", lazy="selectin")
