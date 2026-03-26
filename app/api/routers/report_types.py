"""Typed report CRUD routes."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.models.report import Report, ReportType
from app.repositories.company import CompanyRepository
from app.repositories.employee import EmployeeRepository
from app.schemas.pagination import Page
from app.schemas.report import ReportCreate, ReportRead, ReportUpdate
from app.services.report import ReportService
from src.reports.daily_report.service import DailyReportService
from src.reports.mileage_report.service import MileageReportService

daily_router = APIRouter(prefix="/reports", tags=["Daily Report"])
mileage_router = APIRouter(prefix="/reports", tags=["Mileage Report"])
router = APIRouter()


def _ensure_type(report: Report, expected_type: ReportType) -> None:
    if report.report_type != expected_type:
        msg = "Report not found."
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg)


def _build_create_payload(payload: ReportCreate, report_type: ReportType) -> ReportCreate:
    return payload.model_copy(update={"report_type": report_type})


def _build_update_payload(payload: ReportUpdate) -> ReportUpdate:
    data = payload.model_dump(exclude_unset=True)
    data.pop("report_type", None)
    return ReportUpdate.model_validate(data)


def _generate_filename(month: int) -> str:
    timestamp_iso = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"report_{month}_{timestamp_iso}.xlsx"


async def _build_excel_payload(service: ReportService, report: Report) -> dict[str, object]:
    company = await CompanyRepository(service.session).get_by_id(report.company_id)
    if company is None:
        msg = "Company not found."
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg)

    employee = await EmployeeRepository(service.session).get_by_id(report.employee_id)
    if employee is None:
        msg = "Employee not found."
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg)

    return {
        "company": {
            "name": company.name,
            "tax_id": company.tax_id,
            "address": company.address,
        },
        "employee": {
            "name": employee.name,
            "tax_id": employee.tax_id,
            "address": employee.address,
            "vehicle_plate": employee.vehicle_plate,
        },
        "month": report.month,
        "holidays": report.holidays,
    }


@daily_router.post("/daily-report", response_model=None, status_code=status.HTTP_200_OK)
async def create_daily_report(
    payload: ReportCreate,
    session: AsyncSession = Depends(get_db_session),
) -> StreamingResponse:
    service = ReportService(session)
    report = await service.create(_build_create_payload(payload, ReportType.DAILY))
    excel_payload = await _build_excel_payload(service, report)
    excel_payload["entries"] = [
        {
            "day": item.day,
            "description": item.description,
            "location": item.location,
            "start_time": item.start_time.isoformat(timespec="minutes") if item.start_time else None,
            "end_time": item.end_time.isoformat(timespec="minutes") if item.end_time else None,
            "percentage": item.percentage,
        }
        for item in payload.daily_entries
    ]
    generator = DailyReportService()
    excel_stream = generator.generate(excel_payload, generator.mappings)
    filename = _generate_filename(report.month)
    return StreamingResponse(
        excel_stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@daily_router.get("/daily-report/{report_id}", response_model=ReportRead)
async def get_daily_report(
    report_id: UUID,
    session: AsyncSession = Depends(get_db_session),
) -> ReportRead:
    service = ReportService(session)
    report = await service.get(report_id)
    _ensure_type(report, ReportType.DAILY)
    return ReportRead.model_validate(report)


@daily_router.get("/daily-report", response_model=Page[ReportRead])
async def list_daily_reports(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_db_session),
) -> Page[ReportRead]:
    service = ReportService(session)
    reports, total = await service.list_by_type(
        report_type=ReportType.DAILY,
        limit=limit,
        offset=offset,
    )
    return Page[ReportRead](
        items=[ReportRead.model_validate(item) for item in reports],
        total=total,
        limit=limit,
        offset=offset,
    )


@daily_router.patch("/daily-report/{report_id}", response_model=ReportRead)
async def update_daily_report(
    report_id: UUID,
    payload: ReportUpdate,
    session: AsyncSession = Depends(get_db_session),
) -> ReportRead:
    service = ReportService(session)
    current = await service.get(report_id)
    _ensure_type(current, ReportType.DAILY)
    report = await service.update(report_id=report_id, payload=_build_update_payload(payload))
    return ReportRead.model_validate(report)


@daily_router.delete("/daily-report/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_daily_report(
    report_id: UUID,
    session: AsyncSession = Depends(get_db_session),
) -> Response:
    service = ReportService(session)
    current = await service.get(report_id)
    _ensure_type(current, ReportType.DAILY)
    await service.soft_delete(report_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@mileage_router.post("/mileage-report", response_model=None, status_code=status.HTTP_200_OK)
async def create_mileage_report(
    payload: ReportCreate,
    session: AsyncSession = Depends(get_db_session),
) -> StreamingResponse:
    service = ReportService(session)
    report = await service.create(_build_create_payload(payload, ReportType.MILEAGE))
    excel_payload = await _build_excel_payload(service, report)
    excel_payload["entries"] = [
        {
            "day": item.day,
            "origin": item.origin,
            "destination": item.destination,
            "description": "",
            "distance_km": item.distance_km,
        }
        for item in payload.mileage_entries
    ]
    generator = MileageReportService()
    excel_stream = generator.generate(excel_payload, generator.mappings)
    filename = _generate_filename(report.month)
    return StreamingResponse(
        excel_stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@mileage_router.get("/mileage-report/{report_id}", response_model=ReportRead)
async def get_mileage_report(
    report_id: UUID,
    session: AsyncSession = Depends(get_db_session),
) -> ReportRead:
    service = ReportService(session)
    report = await service.get(report_id)
    _ensure_type(report, ReportType.MILEAGE)
    return ReportRead.model_validate(report)


@mileage_router.get("/mileage-report", response_model=Page[ReportRead])
async def list_mileage_reports(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_db_session),
) -> Page[ReportRead]:
    service = ReportService(session)
    reports, total = await service.list_by_type(
        report_type=ReportType.MILEAGE,
        limit=limit,
        offset=offset,
    )
    return Page[ReportRead](
        items=[ReportRead.model_validate(item) for item in reports],
        total=total,
        limit=limit,
        offset=offset,
    )


@mileage_router.patch("/mileage-report/{report_id}", response_model=ReportRead)
async def update_mileage_report(
    report_id: UUID,
    payload: ReportUpdate,
    session: AsyncSession = Depends(get_db_session),
) -> ReportRead:
    service = ReportService(session)
    current = await service.get(report_id)
    _ensure_type(current, ReportType.MILEAGE)
    report = await service.update(report_id=report_id, payload=_build_update_payload(payload))
    return ReportRead.model_validate(report)


@mileage_router.delete("/mileage-report/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_mileage_report(
    report_id: UUID,
    session: AsyncSession = Depends(get_db_session),
) -> Response:
    service = ReportService(session)
    current = await service.get(report_id)
    _ensure_type(current, ReportType.MILEAGE)
    await service.soft_delete(report_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


router.include_router(daily_router)
router.include_router(mileage_router)
