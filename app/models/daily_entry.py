"""Daily entry ORM model."""

from __future__ import annotations

import uuid
from datetime import time
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Index, Integer, Text, Time, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.report import Report


class DailyEntry(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Describes daily work done in a report."""

    __tablename__ = "daily_entries"
    __table_args__ = (
        CheckConstraint("day >= 1 AND day <= 31", name="ck_daily_entries_day_range"),
        CheckConstraint("percentage >= 0 AND percentage <= 100", name="ck_daily_entries_percentage_range"),
        Index(
            "ix_daily_entries_report_id_active",
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
    description: Mapped[str] = mapped_column(Text, nullable=False)
    location: Mapped[str | None] = mapped_column(Text, nullable=True)
    start_time: Mapped[time | None] = mapped_column(Time(timezone=False), nullable=True)
    end_time: Mapped[time | None] = mapped_column(Time(timezone=False), nullable=True)
    percentage: Mapped[int] = mapped_column(Integer, nullable=False, server_default="100")

    report: Mapped["Report"] = relationship(back_populates="daily_entries", lazy="selectin")
