"""Asset (equipment) ORM model."""

from __future__ import annotations

import enum
import uuid
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Date, Enum as SAEnum, ForeignKey, Index, Numeric, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.company import Company


class AssetCategory(str, enum.Enum):
    """Who owns or supplies the asset."""

    mine = "mine"
    landlord = "landlord"
    supplier = "supplier"


class AssetStatus(str, enum.Enum):
    """Operational state of the asset."""

    active = "active"
    maintenance = "maintenance"
    broken = "broken"
    disposed = "disposed"


class Asset(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Company equipment / fixed asset."""

    __tablename__ = "assets"
    __table_args__ = (
        Index(
            "ix_assets_company_id_active",
            "company_id",
            postgresql_where=text("deleted_at IS NULL"),
        ),
        Index(
            "ix_assets_company_category_status",
            "company_id",
            "category",
            "status",
            postgresql_where=text("deleted_at IS NULL"),
        ),
    )

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="RESTRICT"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    price: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    category: Mapped[AssetCategory] = mapped_column(
        SAEnum(AssetCategory, native_enum=False, length=32),
        nullable=False,
    )
    status: Mapped[AssetStatus] = mapped_column(
        SAEnum(AssetStatus, native_enum=False, length=32),
        nullable=False,
    )
    location: Mapped[str | None] = mapped_column(Text, nullable=True)
    purchase_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    warranty_until: Mapped[date | None] = mapped_column(Date, nullable=True)
    serial_number: Mapped[str | None] = mapped_column(Text, nullable=True)
    brand: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    invoice_storage_key: Mapped[str | None] = mapped_column(Text, nullable=True)

    company: Mapped["Company"] = relationship(back_populates="assets", lazy="selectin")
