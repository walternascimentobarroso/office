"""Company assets (equipment) API routes."""

from __future__ import annotations

import asyncio
from uuid import UUID

from fastapi import APIRouter, Depends, File, Query, Response, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_user, require_company_access, require_roles
from app.db.session import get_db_session
from app.models.asset import AssetCategory, AssetStatus
from app.schemas.asset import AssetCreate, AssetRead, AssetUpdate
from app.schemas.pagination import Page
from app.services.asset import AssetService

_SORT_FIELDS = frozenset({"created_at", "name", "price", "purchase_date"})

router = APIRouter(
    prefix="/companies/{company_id}/assets",
    tags=["assets"],
    dependencies=[Depends(get_current_user), Depends(require_company_access)],
)


def _normalize_sort(sort_by: str, sort_order: str) -> tuple[str, str]:
    field = sort_by if sort_by in _SORT_FIELDS else "created_at"
    order = sort_order.lower() if sort_order.lower() in {"asc", "desc"} else "desc"
    return field, order


@router.post("", response_model=AssetRead, status_code=status.HTTP_201_CREATED)
async def create_asset(
    company_id: UUID,
    payload: AssetCreate,
    _: None = Depends(require_roles("admin")),
    session: AsyncSession = Depends(get_db_session),
) -> AssetRead:
    service = AssetService(session)
    asset = await service.create(company_id=company_id, payload=payload)
    return await service.to_read(asset, resolve_invoice_url=False)


@router.get("/{asset_id}", response_model=AssetRead)
async def get_asset(
    company_id: UUID,
    asset_id: UUID,
    session: AsyncSession = Depends(get_db_session),
) -> AssetRead:
    service = AssetService(session)
    asset = await service.get_in_company(company_id=company_id, asset_id=asset_id)
    return await service.to_read(asset, resolve_invoice_url=True)


@router.get("", response_model=Page[AssetRead])
async def list_assets(
    company_id: UUID,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    search: str | None = Query(default=None, max_length=512),
    category: AssetCategory | None = None,
    status: AssetStatus | None = None,
    location: str | None = Query(default=None, max_length=1024),
    sort_by: str = Query(default="created_at", description="created_at | name | price | purchase_date"),
    sort_order: str = Query(default="desc", description="asc | desc"),
    session: AsyncSession = Depends(get_db_session),
) -> Page[AssetRead]:
    field, order = _normalize_sort(sort_by, sort_order)
    service = AssetService(session)
    assets, total = await service.list_by_company(
        company_id=company_id,
        limit=limit,
        offset=offset,
        search=search,
        category=category,
        status=status,
        location=location,
        sort_by=field,
        sort_order=order,
    )
    items = list(
        await asyncio.gather(
            *[service.to_read(a, resolve_invoice_url=False) for a in assets],
        ),
    )
    return Page[AssetRead](
        items=items,
        total=total,
        limit=limit,
        offset=offset,
    )


@router.delete("/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_asset(
    company_id: UUID,
    asset_id: UUID,
    _: None = Depends(require_roles("admin")),
    session: AsyncSession = Depends(get_db_session),
) -> Response:
    service = AssetService(session)
    await service.soft_delete_in_company(company_id=company_id, asset_id=asset_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.patch("/{asset_id}", response_model=AssetRead)
async def update_asset(
    company_id: UUID,
    asset_id: UUID,
    payload: AssetUpdate,
    _: None = Depends(require_roles("admin")),
    session: AsyncSession = Depends(get_db_session),
) -> AssetRead:
    service = AssetService(session)
    asset = await service.update(
        company_id=company_id,
        asset_id=asset_id,
        payload=payload,
    )
    return await service.to_read(asset, resolve_invoice_url=True)


@router.post("/{asset_id}/invoice", response_model=AssetRead)
async def upload_asset_invoice(
    company_id: UUID,
    asset_id: UUID,
    file: UploadFile = File(...),
    _: None = Depends(require_roles("admin")),
    session: AsyncSession = Depends(get_db_session),
) -> AssetRead:
    service = AssetService(session)
    raw = await file.read()
    asset = await service.attach_invoice(
        company_id=company_id,
        asset_id=asset_id,
        filename=file.filename or "invoice",
        content=raw,
        content_type=file.content_type,
    )
    return await service.to_read(asset, resolve_invoice_url=True)
