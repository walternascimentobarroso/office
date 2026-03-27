"""Company ORM model."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.employee import Employee
    from app.models.report import Report
    from app.models.user import User


class Company(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Represents a company."""

    __tablename__ = "companies"

    name: Mapped[str] = mapped_column(Text, nullable=False)
    tax_id: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)

    employees: Mapped[list["Employee"]] = relationship(
        back_populates="company",
        cascade="save-update, merge",
        lazy="selectin",
    )
    users: Mapped[list["User"]] = relationship(
        back_populates="company",
        cascade="save-update, merge",
        lazy="selectin",
    )
    reports: Mapped[list["Report"]] = relationship(
        back_populates="company",
        cascade="save-update, merge",
        lazy="selectin",
    )
