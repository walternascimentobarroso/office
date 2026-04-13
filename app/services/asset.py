"""Asset (equipment) service."""

from __future__ import annotations

from datetime import date
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.asset import Asset, AssetCategory, AssetStatus
from app.repositories.asset import AssetRepository
from app.repositories.company import CompanyRepository
from app.schemas.asset import AssetCreate, AssetRead, AssetUpdate
from app.core.storage_settings import get_storage_settings
from app.services.object_storage import ObjectStorageService
from app.utils.soft_delete import mark_deleted


def _validate_warranty_vs_purchase(purchase: date | None, warranty: date | None) -> None:
    if (
        purchase is not None
        and warranty is not None
        and warranty < purchase
    ):
        msg = "warranty_until must be on or after purchase_date"
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=msg)


class AssetService:
    """Business operations for company assets."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.company_repository = CompanyRepository(session)
        self.asset_repository = AssetRepository(session)
        self._storage = ObjectStorageService()

    async def _ensure_company(self, company_id: UUID) -> None:
        company = await self.company_repository.get_by_id(company_id)
        if company is None:
            msg = "Company not found."
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg)

    async def to_read(self, asset: Asset, *, resolve_invoice_url: bool) -> AssetRead:
        base = AssetRead.model_validate(asset)
        if not asset.invoice_storage_key or not resolve_invoice_url:
            return base.model_copy(update={"invoice_file_url": None})
        if not self._storage.is_ready():
            return base.model_copy(update={"invoice_file_url": None})
        settings = get_storage_settings()
        if settings.backend == "local":
            if settings.local_public_base_url:
                url = f"{settings.local_public_base_url}/{asset.invoice_storage_key}"
            else:
                url = None
            return base.model_copy(update={"invoice_file_url": url})
        if settings.public_base_url:
            url = f"{settings.public_base_url}/{asset.invoice_storage_key}"
        else:
            url = await self._storage.presigned_get_url(key=asset.invoice_storage_key)
        return base.model_copy(update={"invoice_file_url": url})

    async def create(self, company_id: UUID, payload: AssetCreate) -> Asset:
        await self._ensure_company(company_id)
        asset = self.asset_repository.model(
            company_id=company_id,
            name=payload.name,
            description=payload.description,
            price=payload.price,
            category=payload.category,
            status=payload.status,
            location=payload.location,
            purchase_date=payload.purchase_date,
            warranty_until=payload.warranty_until,
            serial_number=payload.serial_number,
            brand=payload.brand,
            notes=payload.notes,
            invoice_storage_key=None,
        )
        created = await self.asset_repository.add(asset)
        await self.session.commit()
        return created

    async def get_in_company(self, company_id: UUID, asset_id: UUID) -> Asset:
        await self._ensure_company(company_id)
        asset = await self.asset_repository.get_by_id(asset_id)
        if asset is None or asset.company_id != company_id:
            msg = "Asset not found for this company."
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg)
        return asset

    async def list_by_company(
        self,
        company_id: UUID,
        limit: int,
        offset: int,
        *,
        search: str | None,
        category: AssetCategory | None,
        status: AssetStatus | None,
        location: str | None,
        sort_by: str,
        sort_order: str,
    ) -> tuple[list[Asset], int]:
        await self._ensure_company(company_id)
        rows = await self.asset_repository.list_by_company(
            company_id,
            limit,
            offset,
            search=search,
            category=category,
            status=status,
            location=location,
            sort_by=sort_by,
            sort_order=sort_order,
        )
        total = await self.asset_repository.count_by_company(
            company_id,
            search=search,
            category=category,
            status=status,
            location=location,
        )
        return list(rows), total

    async def update(self, company_id: UUID, asset_id: UUID, payload: AssetUpdate) -> Asset:
        asset = await self.get_in_company(company_id=company_id, asset_id=asset_id)
        update_data = payload.model_dump(exclude_unset=True)

        purchase = update_data.get("purchase_date", asset.purchase_date)
        warranty = update_data.get("warranty_until", asset.warranty_until)
        _validate_warranty_vs_purchase(purchase, warranty)

        for field, value in update_data.items():
            setattr(asset, field, value)
        await self.session.commit()
        await self.session.refresh(asset)
        return asset

    async def soft_delete_in_company(self, company_id: UUID, asset_id: UUID) -> None:
        asset = await self.get_in_company(company_id=company_id, asset_id=asset_id)
        mark_deleted(asset)
        await self.session.commit()

    async def attach_invoice(
        self,
        company_id: UUID,
        asset_id: UUID,
        *,
        filename: str,
        content: bytes,
        content_type: str | None,
    ) -> Asset:
        if not self._storage.is_ready():
            msg = (
                "Storage is not configured. "
                "Use ASSET_STORAGE_BACKEND=local (default) or set S3_BUCKET and AWS credentials for s3."
            )
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=msg)

        if len(content) > get_storage_settings().invoice_max_bytes:
            msg = "Invoice file is too large."
            raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail=msg)

        asset = await self.get_in_company(company_id=company_id, asset_id=asset_id)
        key, _public = await self._storage.upload_asset_invoice(
            company_id=company_id,
            asset_id=asset_id,
            filename=filename,
            content=content,
            content_type=content_type,
        )
        asset.invoice_storage_key = key
        await self.session.commit()
        await self.session.refresh(asset)
        return asset
