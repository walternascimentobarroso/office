"""Report API routes."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_user, require_roles
from app.db.session import get_db_session
from app.schemas.pagination import Page
from app.schemas.report import ReportCreate, ReportRead, ReportUpdate
from app.services.report import ReportService

router = APIRouter(prefix="/reports", tags=["reports-db"], dependencies=[Depends(get_current_user)])


@router.post("", response_model=ReportRead, status_code=status.HTTP_201_CREATED)
async def create_report(
    payload: ReportCreate,
    _: None = Depends(require_roles("admin")),
    session: AsyncSession = Depends(get_db_session),
) -> ReportRead:
    service = ReportService(session)
    report = await service.create(payload)
    return ReportRead.model_validate(report)


@router.get("/{report_id}", response_model=ReportRead)
async def get_report(
    report_id: UUID,
    session: AsyncSession = Depends(get_db_session),
) -> ReportRead:
    service = ReportService(session)
    report = await service.get(report_id)
    return ReportRead.model_validate(report)


@router.get("", response_model=Page[ReportRead])
async def list_reports(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_db_session),
) -> Page[ReportRead]:
    service = ReportService(session)
    reports, total = await service.list(limit=limit, offset=offset)
    return Page[ReportRead](
        items=[ReportRead.model_validate(item) for item in reports],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_report(
    report_id: UUID,
    _: None = Depends(require_roles("admin")),
    session: AsyncSession = Depends(get_db_session),
) -> Response:
    service = ReportService(session)
    await service.soft_delete(report_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.patch("/{report_id}", response_model=ReportRead)
async def update_report(
    report_id: UUID,
    payload: ReportUpdate,
    _: None = Depends(require_roles("admin")),
    session: AsyncSession = Depends(get_db_session),
) -> ReportRead:
    service = ReportService(session)
    report = await service.update(report_id=report_id, payload=payload)
    return ReportRead.model_validate(report)
