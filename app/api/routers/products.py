"""Company products API routes."""

from __future__ import annotations

import asyncio
from uuid import UUID

from fastapi import APIRouter, Depends, File, Query, Response, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_user, require_company_access, require_roles
from app.db.session import get_db_session
from app.schemas.pagination import Page
from app.schemas.product import ProductCreate, ProductRead, ProductUpdate
from app.services.product import ProductService

router = APIRouter(
    prefix="/companies/{company_id}/products",
    tags=["products"],
    dependencies=[Depends(get_current_user), Depends(require_company_access)],
)


@router.post("", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
async def create_product(
    company_id: UUID,
    payload: ProductCreate,
    _: None = Depends(require_roles("admin")),
    session: AsyncSession = Depends(get_db_session),
) -> ProductRead:
    service = ProductService(session)
    product = await service.create(company_id=company_id, payload=payload)
    return await service.to_read(product, resolve_image_url=False)


@router.get("/{product_id}", response_model=ProductRead)
async def get_product(
    company_id: UUID,
    product_id: UUID,
    session: AsyncSession = Depends(get_db_session),
) -> ProductRead:
    service = ProductService(session)
    product = await service.get_in_company(company_id=company_id, product_id=product_id)
    return await service.to_read(product, resolve_image_url=True)


@router.get("", response_model=Page[ProductRead])
async def list_products(
    company_id: UUID,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    search: str | None = Query(default=None, max_length=512),
    category: str | None = Query(default=None, max_length=256),
    active: bool | None = None,
    session: AsyncSession = Depends(get_db_session),
) -> Page[ProductRead]:
    service = ProductService(session)
    products, total = await service.list_by_company(
        company_id=company_id,
        limit=limit,
        offset=offset,
        search=search,
        category=category,
        active=active,
    )
    items = list(
        await asyncio.gather(
            *[service.to_read(p, resolve_image_url=False) for p in products],
        ),
    )
    return Page[ProductRead](items=items, total=total, limit=limit, offset=offset)


@router.patch("/{product_id}", response_model=ProductRead)
async def update_product(
    company_id: UUID,
    product_id: UUID,
    payload: ProductUpdate,
    _: None = Depends(require_roles("admin")),
    session: AsyncSession = Depends(get_db_session),
) -> ProductRead:
    service = ProductService(session)
    product = await service.update(
        company_id=company_id,
        product_id=product_id,
        payload=payload,
    )
    return await service.to_read(product, resolve_image_url=True)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    company_id: UUID,
    product_id: UUID,
    _: None = Depends(require_roles("admin")),
    session: AsyncSession = Depends(get_db_session),
) -> Response:
    service = ProductService(session)
    await service.soft_delete_in_company(company_id=company_id, product_id=product_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{product_id}/image", response_model=ProductRead)
async def upload_product_image(
    company_id: UUID,
    product_id: UUID,
    file: UploadFile = File(...),
    _: None = Depends(require_roles("admin")),
    session: AsyncSession = Depends(get_db_session),
) -> ProductRead:
    service = ProductService(session)
    raw = await file.read()
    product = await service.attach_image(
        company_id=company_id,
        product_id=product_id,
        filename=file.filename or "image",
        content=raw,
        content_type=file.content_type,
    )
    return await service.to_read(product, resolve_image_url=True)
