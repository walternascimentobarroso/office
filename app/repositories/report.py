"""Report repository."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.models.daily_entry import DailyEntry
from app.models.mileage_entry import MileageEntry
from app.models.report import Report, ReportType
from app.repositories.base import BaseRepository


class ReportRepository(BaseRepository[Report]):
    """Persistence operations for reports."""

    model = Report

    async def get_full(self, report_id: UUID) -> Report | None:
        stmt = (
            self._active_stmt()
            .where(Report.id == report_id)
            .options(
                selectinload(Report.daily_entries),
                selectinload(Report.mileage_entries),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_employee_period(
        self,
        employee_id: UUID,
        month: int,
        year: int,
        report_type: ReportType,
    ) -> Report | None:
        stmt = self._active_stmt().where(
            Report.employee_id == employee_id,
            Report.month == month,
            Report.year == year,
            Report.report_type == report_type,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_employee_period_excluding_id(
        self,
        *,
        employee_id: UUID,
        month: int,
        year: int,
        report_type: ReportType,
        report_id: UUID,
    ) -> Report | None:
        stmt = self._active_stmt().where(
            Report.employee_id == employee_id,
            Report.month == month,
            Report.year == year,
            Report.report_type == report_type,
            Report.id != report_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_type(
        self,
        *,
        report_type: ReportType,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Report]:
        stmt = self._active_stmt().where(Report.report_type == report_type).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count_by_type(self, *, report_type: ReportType) -> int:
        stmt = (
            select(func.count())
            .select_from(Report)
            .where(Report.deleted_at.is_(None), Report.report_type == report_type)
        )
        result = await self.session.execute(stmt)
        return int(result.scalar_one())

    async def add_daily_entries(self, report_id: UUID, entries: list[DailyEntry]) -> None:
        for entry in entries:
            entry.report_id = report_id
            self.session.add(entry)
        await self.session.flush()

    async def add_mileage_entries(self, report_id: UUID, entries: list[MileageEntry]) -> None:
        for entry in entries:
            entry.report_id = report_id
            self.session.add(entry)
        await self.session.flush()
