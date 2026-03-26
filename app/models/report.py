"""Report ORM model."""

from __future__ import annotations

import enum
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Enum, ForeignKey, Index, Integer, text
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.company import Company
    from app.models.daily_entry import DailyEntry
    from app.models.employee import Employee
    from app.models.mileage_entry import MileageEntry


class ReportStatus(str, enum.Enum):
    """Allowed statuses for reports."""

    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"


class ReportType(str, enum.Enum):
    """Allowed types for reports."""

    DAILY = "daily"
    MILEAGE = "mileage"


class Report(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Monthly report for one employee."""

    __tablename__ = "reports"
    __table_args__ = (
        CheckConstraint("month >= 1 AND month <= 12", name="ck_reports_month_range"),
        CheckConstraint("year >= 2000", name="ck_reports_year_min"),
        Index(
            "ix_reports_company_month_year_active",
            "company_id",
            "month",
            "year",
            postgresql_where=text("deleted_at IS NULL"),
        ),
    )
    _status_enum = Enum(
        ReportStatus,
        name="report_status",
        values_callable=lambda enum_cls: [item.value for item in enum_cls],
    )
    _report_type_enum = Enum(
        ReportType,
        name="report_type",
        values_callable=lambda enum_cls: [item.value for item in enum_cls],
    )

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="RESTRICT"),
        nullable=False,
    )
    employee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employees.id", ondelete="RESTRICT"),
        nullable=False,
    )
    month: Mapped[int] = mapped_column(Integer, nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    holidays: Mapped[list[int]] = mapped_column(ARRAY(Integer), nullable=False, server_default="{}")
    status: Mapped[ReportStatus] = mapped_column(
        _status_enum,
        nullable=False,
        server_default=ReportStatus.DRAFT.value,
    )
    report_type: Mapped[ReportType] = mapped_column(
        _report_type_enum,
        nullable=False,
        server_default=ReportType.DAILY.value,
    )

    company: Mapped["Company"] = relationship(back_populates="reports", lazy="selectin")
    employee: Mapped["Employee"] = relationship(back_populates="reports", lazy="selectin")
    daily_entries: Mapped[list["DailyEntry"]] = relationship(
        back_populates="report",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    mileage_entries: Mapped[list["MileageEntry"]] = relationship(
        back_populates="report",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
