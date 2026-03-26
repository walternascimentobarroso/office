"""Report service."""

from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.daily_entry import DailyEntry
from app.models.mileage_entry import MileageEntry
from app.models.report import Report, ReportType
from app.repositories.company import CompanyRepository
from app.repositories.employee import EmployeeRepository
from app.repositories.report import ReportRepository
from app.schemas.report import ReportCreate, ReportUpdate
from app.utils.soft_delete import mark_deleted


class ReportService:
    """Business operations for reports and nested entries."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.company_repository = CompanyRepository(session)
        self.employee_repository = EmployeeRepository(session)
        self.report_repository = ReportRepository(session)

    async def create(self, payload: ReportCreate) -> Report:
        company = await self.company_repository.get_by_id(payload.company_id)
        if company is None:
            msg = "Company not found."
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg)

        employee = await self.employee_repository.get_by_id(payload.employee_id)
        if employee is None:
            msg = "Employee not found."
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg)

        if employee.company_id != payload.company_id:
            msg = "Employee does not belong to the provided company."
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)

        existing = await self.report_repository.get_by_employee_period(
            employee_id=payload.employee_id,
            month=payload.month,
            year=payload.year,
            report_type=payload.report_type,
        )
        if existing is not None:
            msg = "Report already exists for employee and period."
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=msg)

        report = Report(
            company_id=payload.company_id,
            employee_id=payload.employee_id,
            month=payload.month,
            year=payload.year,
            holidays=payload.holidays,
            status=payload.status,
            report_type=payload.report_type,
        )
        report = await self.report_repository.add(report)

        daily_entries = [
            DailyEntry(
                report_id=report.id,
                day=item.day,
                description=item.description,
                location=item.location,
                start_time=item.start_time,
                end_time=item.end_time,
            )
            for item in payload.daily_entries
        ]
        mileage_entries = [
            MileageEntry(
                report_id=report.id,
                day=item.day,
                origin=item.origin,
                destination=item.destination,
                distance_km=item.distance_km,
            )
            for item in payload.mileage_entries
        ]

        await self.report_repository.add_daily_entries(report.id, daily_entries)
        await self.report_repository.add_mileage_entries(report.id, mileage_entries)
        await self.session.commit()
        full_report = await self.report_repository.get_full(report.id)
        if full_report is None:
            msg = "Failed to load newly created report."
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=msg)
        return full_report

    async def get(self, report_id: UUID) -> Report:
        report = await self.report_repository.get_full(report_id)
        if report is None:
            msg = "Report not found."
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg)
        return report

    async def list(self, limit: int = 50, offset: int = 0) -> tuple[list[Report], int]:
        reports = await self.report_repository.list(limit=limit, offset=offset)
        total = await self.report_repository.count()
        return list(reports), total

    async def soft_delete(self, report_id: UUID) -> None:
        report = await self.get(report_id)
        mark_deleted(report)
        for daily_entry in report.daily_entries:
            mark_deleted(daily_entry)
        for mileage_entry in report.mileage_entries:
            mark_deleted(mileage_entry)
        await self.session.commit()

    async def update(self, report_id: UUID, payload: ReportUpdate) -> Report:
        report = await self.get(report_id)
        update_data = payload.model_dump(exclude_unset=True)

        target_company_id = update_data.get("company_id", report.company_id)
        target_employee_id = update_data.get("employee_id", report.employee_id)
        target_month = update_data.get("month", report.month)
        target_year = update_data.get("year", report.year)
        target_report_type = update_data.get("report_type", report.report_type)

        if target_company_id != report.company_id:
            company = await self.company_repository.get_by_id(target_company_id)
            if company is None:
                msg = "Company not found."
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg)

        if target_employee_id != report.employee_id:
            employee = await self.employee_repository.get_by_id(target_employee_id)
            if employee is None:
                msg = "Employee not found."
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg)

        employee = await self.employee_repository.get_by_id(target_employee_id)
        if employee is None:
            msg = "Employee not found."
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg)
        if employee.company_id != target_company_id:
            msg = "Employee does not belong to the provided company."
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)

        unique_changed = (
            target_employee_id != report.employee_id
            or target_month != report.month
            or target_year != report.year
            or target_report_type != report.report_type
        )
        if unique_changed:
            existing = await self.report_repository.get_by_employee_period_excluding_id(
                employee_id=target_employee_id,
                month=target_month,
                year=target_year,
                report_type=target_report_type,
                report_id=report_id,
            )
            if existing is not None:
                msg = "Report already exists for employee and period."
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=msg)

        for field in (
            "company_id",
            "employee_id",
            "month",
            "year",
            "holidays",
            "status",
            "report_type",
        ):
            if field in update_data:
                setattr(report, field, update_data[field])

        if "daily_entries" in update_data:
            for entry in report.daily_entries:
                mark_deleted(entry)
            daily_entries = [
                DailyEntry(
                    report_id=report.id,
                    day=item.day,
                    description=item.description,
                    location=item.location,
                    start_time=item.start_time,
                    end_time=item.end_time,
                )
                for item in update_data["daily_entries"]
            ]
            await self.report_repository.add_daily_entries(report.id, daily_entries)

        if "mileage_entries" in update_data:
            for entry in report.mileage_entries:
                mark_deleted(entry)
            mileage_entries = [
                MileageEntry(
                    report_id=report.id,
                    day=item.day,
                    origin=item.origin,
                    destination=item.destination,
                    distance_km=item.distance_km,
                )
                for item in update_data["mileage_entries"]
            ]
            await self.report_repository.add_mileage_entries(report.id, mileage_entries)

        await self.session.commit()
        refreshed = await self.report_repository.get_full(report.id)
        if refreshed is None:
            msg = "Report not found."
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg)
        return refreshed

    async def list_by_type(
        self,
        *,
        report_type: ReportType,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[Report], int]:
        reports = await self.report_repository.list_by_type(
            report_type=report_type,
            limit=limit,
            offset=offset,
        )
        total = await self.report_repository.count_by_type(report_type=report_type)
        return reports, total
