"""Company suppliers API routes."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_user, require_company_access, require_roles
from app.db.session import get_db_session
from app.schemas.pagination import Page
from app.schemas.supplier import SupplierCreate, SupplierRead, SupplierUpdate
from app.services.supplier import SupplierService

router = APIRouter(
    prefix="/companies/{company_id}/suppliers",
    tags=["suppliers"],
    dependencies=[Depends(get_current_user), Depends(require_company_access)],
)


@router.post("", response_model=SupplierRead, status_code=status.HTTP_201_CREATED)
async def create_supplier(
    company_id: UUID,
    payload: SupplierCreate,
    _: None = Depends(require_roles("admin")),
    session: AsyncSession = Depends(get_db_session),
) -> SupplierRead:
    service = SupplierService(session)
    supplier = await service.create(company_id=company_id, payload=payload)
    return SupplierRead.model_validate(supplier)


@router.get("/{supplier_id}", response_model=SupplierRead)
async def get_supplier(
    company_id: UUID,
    supplier_id: UUID,
    session: AsyncSession = Depends(get_db_session),
) -> SupplierRead:
    service = SupplierService(session)
    supplier = await service.get_in_company(company_id=company_id, supplier_id=supplier_id)
    return SupplierRead.model_validate(supplier)


@router.get("", response_model=Page[SupplierRead])
async def list_suppliers(
    company_id: UUID,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    search: str | None = Query(default=None, max_length=512),
    session: AsyncSession = Depends(get_db_session),
) -> Page[SupplierRead]:
    service = SupplierService(session)
    suppliers, total = await service.list_by_company(
        company_id=company_id,
        limit=limit,
        offset=offset,
        search=search,
    )
    return Page[SupplierRead](
        items=[SupplierRead.model_validate(s) for s in suppliers],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.patch("/{supplier_id}", response_model=SupplierRead)
async def update_supplier(
    company_id: UUID,
    supplier_id: UUID,
    payload: SupplierUpdate,
    _: None = Depends(require_roles("admin")),
    session: AsyncSession = Depends(get_db_session),
) -> SupplierRead:
    service = SupplierService(session)
    supplier = await service.update(
        company_id=company_id,
        supplier_id=supplier_id,
        payload=payload,
    )
    return SupplierRead.model_validate(supplier)


@router.delete("/{supplier_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_supplier(
    company_id: UUID,
    supplier_id: UUID,
    _: None = Depends(require_roles("admin")),
    session: AsyncSession = Depends(get_db_session),
) -> Response:
    service = SupplierService(session)
    await service.soft_delete_in_company(company_id=company_id, supplier_id=supplier_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
