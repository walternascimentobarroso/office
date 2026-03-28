"""Company API routes."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_user, require_roles
from app.db.session import get_db_session
from app.schemas.company import CompanyCreate, CompanyRead, CompanyUpdate
from app.schemas.pagination import Page
from app.services.company import CompanyService

router = APIRouter(prefix="/companies", tags=["companies"], dependencies=[Depends(get_current_user)])


@router.post("", response_model=CompanyRead, status_code=status.HTTP_201_CREATED)
async def create_company(
    payload: CompanyCreate,
    _: None = Depends(require_roles("admin")),
    session: AsyncSession = Depends(get_db_session),
) -> CompanyRead:
    service = CompanyService(session)
    company = await service.create(payload)
    return CompanyRead.model_validate(company)


@router.get("/{company_id}", response_model=CompanyRead)
async def get_company(
    company_id: UUID,
    session: AsyncSession = Depends(get_db_session),
) -> CompanyRead:
    service = CompanyService(session)
    company = await service.get(company_id)
    return CompanyRead.model_validate(company)


@router.get("", response_model=Page[CompanyRead])
async def list_companies(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_db_session),
) -> Page[CompanyRead]:
    service = CompanyService(session)
    companies, total = await service.list(limit=limit, offset=offset)
    return Page[CompanyRead](
        items=[CompanyRead.model_validate(item) for item in companies],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_company(
    company_id: UUID,
    _: None = Depends(require_roles("admin")),
    session: AsyncSession = Depends(get_db_session),
) -> Response:
    service = CompanyService(session)
    await service.soft_delete(company_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.patch("/{company_id}", response_model=CompanyRead)
async def update_company(
    company_id: UUID,
    payload: CompanyUpdate,
    _: None = Depends(require_roles("admin")),
    session: AsyncSession = Depends(get_db_session),
) -> CompanyRead:
    service = CompanyService(session)
    company = await service.update(company_id=company_id, payload=payload)
    return CompanyRead.model_validate(company)
