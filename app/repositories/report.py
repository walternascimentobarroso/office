"""Report repository."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import selectinload

from app.models.daily_entry import DailyEntry
from app.models.mileage_entry import MileageEntry
from app.models.report import Report
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
    ) -> Report | None:
        stmt = self._active_stmt().where(
            Report.employee_id == employee_id,
            Report.month == month,
            Report.year == year,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_employee_period_excluding_id(
        self,
        *,
        employee_id: UUID,
        month: int,
        year: int,
        report_id: UUID,
    ) -> Report | None:
        stmt = self._active_stmt().where(
            Report.employee_id == employee_id,
            Report.month == month,
            Report.year == year,
            Report.id != report_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

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
