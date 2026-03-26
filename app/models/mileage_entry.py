"""Mileage entry ORM model."""

from __future__ import annotations

import uuid
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Index, Integer, Numeric, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.report import Report


class MileageEntry(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Mileage details for a report day."""

    __tablename__ = "mileage_entries"
    __table_args__ = (
        CheckConstraint("day >= 1 AND day <= 31", name="ck_mileage_entries_day_range"),
        Index(
            "ix_mileage_entries_report_id_active",
            "report_id",
            postgresql_where=text("deleted_at IS NULL"),
        ),
    )

    report_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("reports.id", ondelete="CASCADE"),
        nullable=False,
    )
    day: Mapped[int] = mapped_column(Integer, nullable=False)
    origin: Mapped[str] = mapped_column(Text, nullable=False)
    destination: Mapped[str] = mapped_column(Text, nullable=False)
    distance_km: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    report: Mapped["Report"] = relationship(back_populates="mileage_entries", lazy="selectin")
