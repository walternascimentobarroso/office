"""Product service."""

from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.storage_settings import get_storage_settings
from app.models.product import Product
from app.repositories.company import CompanyRepository
from app.repositories.product import ProductRepository
from app.schemas.product import ProductCreate, ProductRead, ProductUpdate
from app.services.object_storage import ObjectStorageService
from app.utils.soft_delete import mark_deleted


class ProductService:
    """Business operations for company products."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.company_repository = CompanyRepository(session)
        self.product_repository = ProductRepository(session)
        self._storage = ObjectStorageService()

    async def _ensure_company(self, company_id: UUID) -> None:
        company = await self.company_repository.get_by_id(company_id)
        if company is None:
            msg = "Company not found."
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg)

    async def to_read(self, product: Product, *, resolve_image_url: bool) -> ProductRead:
        base = ProductRead.model_validate(product)
        if not product.image_storage_key or not resolve_image_url:
            return base.model_copy(update={"image_url": None})
        if not self._storage.is_ready():
            return base.model_copy(update={"image_url": None})
        settings = get_storage_settings()
        if settings.backend == "local":
            url = (
                f"{settings.local_public_base_url}/{product.image_storage_key}"
                if settings.local_public_base_url
                else None
            )
            return base.model_copy(update={"image_url": url})
        if settings.public_base_url:
            url = f"{settings.public_base_url}/{product.image_storage_key}"
        else:
            url = await self._storage.presigned_get_url(key=product.image_storage_key)
        return base.model_copy(update={"image_url": url})

    async def create(self, company_id: UUID, payload: ProductCreate) -> Product:
        await self._ensure_company(company_id)
        product = self.product_repository.model(
            company_id=company_id,
            name=payload.name,
            price=payload.price,
            category=payload.category,
            active=payload.active,
            image_storage_key=None,
        )
        created = await self.product_repository.add(product)
        await self.session.commit()
        return created

    async def get_in_company(self, company_id: UUID, product_id: UUID) -> Product:
        await self._ensure_company(company_id)
        product = await self.product_repository.get_by_id(product_id)
        if product is None or product.company_id != company_id:
            msg = "Product not found for this company."
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg)
        return product

    async def list_by_company(
        self,
        company_id: UUID,
        limit: int,
        offset: int,
        *,
        search: str | None,
        category: str | None,
        active: bool | None,
    ) -> tuple[list[Product], int]:
        await self._ensure_company(company_id)
        rows = await self.product_repository.list_by_company(
            company_id, limit, offset, search=search, category=category, active=active
        )
        total = await self.product_repository.count_by_company(
            company_id, search=search, category=category, active=active
        )
        return list(rows), total

    async def update(self, company_id: UUID, product_id: UUID, payload: ProductUpdate) -> Product:
        product = await self.get_in_company(company_id=company_id, product_id=product_id)
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(product, field, value)
        await self.session.commit()
        await self.session.refresh(product)
        return product

    async def soft_delete_in_company(self, company_id: UUID, product_id: UUID) -> None:
        product = await self.get_in_company(company_id=company_id, product_id=product_id)
        mark_deleted(product)
        await self.session.commit()

    async def attach_image(
        self,
        company_id: UUID,
        product_id: UUID,
        *,
        filename: str,
        content: bytes,
        content_type: str | None,
    ) -> Product:
        if not self._storage.is_ready():
            msg = "Storage is not configured."
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=msg)
        settings = get_storage_settings()
        if len(content) > settings.invoice_max_bytes:
            msg = "Image file is too large."
            raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail=msg)
        product = await self.get_in_company(company_id=company_id, product_id=product_id)
        key, _ = await self._storage.upload_product_image(
            company_id=company_id,
            product_id=product_id,
            filename=filename,
            content=content,
            content_type=content_type,
        )
        product.image_storage_key = key
        await self.session.commit()
        await self.session.refresh(product)
        return product
