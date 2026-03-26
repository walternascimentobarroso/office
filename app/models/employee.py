"""Employee ORM model."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.company import Company
    from app.models.report import Report


class Employee(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Represents an employee in a company."""

    __tablename__ = "employees"
    __table_args__ = (
        UniqueConstraint("company_id", "tax_id", name="uq_employees_company_tax_id"),
        Index(
            "ix_employees_company_id_active",
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
    tax_id: Mapped[str] = mapped_column(Text, nullable=False)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    vehicle_plate: Mapped[str | None] = mapped_column(Text, nullable=True)

    company: Mapped["Company"] = relationship(back_populates="employees", lazy="selectin")
    reports: Mapped[list["Report"]] = relationship(
        back_populates="employee",
        cascade="save-update, merge",
        lazy="selectin",
    )
