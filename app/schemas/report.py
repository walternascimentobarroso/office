"""Report and entry schemas."""

from __future__ import annotations

from datetime import time
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.report import ReportStatus, ReportType
from app.schemas.common import AuditReadModel


class DailyEntryCreate(BaseModel):
    """Payload for one daily entry."""

    day: int = Field(ge=1, le=31)
    description: str = Field(min_length=1, max_length=2000)
    location: str | None = Field(default=None, max_length=512)
    start_time: time | None = None
    end_time: time | None = None
    percentage: int = Field(default=100, ge=0, le=100)


class MileageEntryCreate(BaseModel):
    """Payload for one mileage entry."""

    day: int = Field(ge=1, le=31)
    origin: str = Field(min_length=1, max_length=255)
    destination: str = Field(min_length=1, max_length=255)
    distance_km: Decimal = Field(gt=Decimal("0"), max_digits=10, decimal_places=2)


class ReportCreate(BaseModel):
    """Payload to create a report and entries."""

    company_id: UUID
    employee_id: UUID
    month: int = Field(ge=1, le=12)
    year: int = Field(ge=2000)
    holidays: list[int] = Field(default_factory=list)
    status: ReportStatus = ReportStatus.DRAFT
    report_type: ReportType = ReportType.DAILY
    daily_entries: list[DailyEntryCreate] = Field(default_factory=list)
    mileage_entries: list[MileageEntryCreate] = Field(default_factory=list)


class ReportUpdate(BaseModel):
    """Payload to update report fields and optional entry sets."""

    company_id: UUID | None = None
    employee_id: UUID | None = None
    month: int | None = Field(default=None, ge=1, le=12)
    year: int | None = Field(default=None, ge=2000)
    holidays: list[int] | None = None
    status: ReportStatus | None = None
    report_type: ReportType | None = None
    daily_entries: list[DailyEntryCreate] | None = None
    mileage_entries: list[MileageEntryCreate] | None = None


class DailyEntryRead(AuditReadModel):
    """Read model for daily entry."""

    report_id: UUID
    day: int
    description: str
    location: str | None
    start_time: time | None
    end_time: time | None
    percentage: int


class MileageEntryRead(AuditReadModel):
    """Read model for mileage entry."""

    report_id: UUID
    day: int
    origin: str
    destination: str
    distance_km: Decimal


class ReportRead(AuditReadModel):
    """Report response model."""

    company_id: UUID
    employee_id: UUID
    month: int
    year: int
    holidays: list[int]
    status: ReportStatus
    report_type: ReportType
    daily_entries: list[DailyEntryRead] = Field(default_factory=list)
    mileage_entries: list[MileageEntryRead] = Field(default_factory=list)
