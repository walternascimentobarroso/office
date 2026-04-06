"""Invoice email log ORM model."""

from __future__ import annotations

import enum
from datetime import datetime
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, Enum, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class InvoiceEmailStatus(str, enum.Enum):
    """Outcome of an invoice email send attempt."""

    sent = "sent"
    failed = "failed"


class InvoiceEmailLog(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Audit log for monthly invoice request emails."""

    __tablename__ = "invoice_email_logs"
    __table_args__ = (
        CheckConstraint("month >= 1 AND month <= 12", name="ck_invoice_email_logs_month_range"),
        CheckConstraint("year >= 2000", name="ck_invoice_email_logs_year_min"),
    )

    _status_enum = Enum(
        InvoiceEmailStatus,
        name="invoice_email_status",
        create_type=False,
        values_callable=lambda enum_cls: [item.value for item in enum_cls],
    )

    company_id: Mapped[UUID] = mapped_column(
        ForeignKey("companies.id", ondelete="RESTRICT"),
        nullable=False,
    )
    month: Mapped[int] = mapped_column(Integer, nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    to_email: Mapped[str] = mapped_column(Text, nullable=False)
    subject: Mapped[str] = mapped_column(Text, nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[InvoiceEmailStatus] = mapped_column(
        _status_enum,
        nullable=False,
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
