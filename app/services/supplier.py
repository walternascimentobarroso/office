"""Supplier service."""

from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.supplier import Supplier
from app.repositories.company import CompanyRepository
from app.repositories.supplier import SupplierRepository
from app.schemas.supplier import SupplierCreate, SupplierUpdate
from app.utils.soft_delete import mark_deleted


class SupplierService:
    """Business operations for company suppliers."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.company_repository = CompanyRepository(session)
        self.supplier_repository = SupplierRepository(session)

    async def _ensure_company(self, company_id: UUID) -> None:
        company = await self.company_repository.get_by_id(company_id)
        if company is None:
            msg = "Company not found."
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg)

    async def create(self, company_id: UUID, payload: SupplierCreate) -> Supplier:
        await self._ensure_company(company_id)
        supplier = self.supplier_repository.model(
            company_id=company_id,
            name=payload.name,
            contact_name=payload.contact_name,
            email=payload.email,
            phone=payload.phone,
            address=payload.address,
            tax_id=payload.tax_id,
            notes=payload.notes,
        )
        created = await self.supplier_repository.add(supplier)
        await self.session.commit()
        return created

    async def get_in_company(self, company_id: UUID, supplier_id: UUID) -> Supplier:
        await self._ensure_company(company_id)
        supplier = await self.supplier_repository.get_by_id(supplier_id)
        if supplier is None or supplier.company_id != company_id:
            msg = "Supplier not found for this company."
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg)
        return supplier

    async def list_by_company(
        self,
        company_id: UUID,
        limit: int,
        offset: int,
        *,
        search: str | None,
    ) -> tuple[list[Supplier], int]:
        await self._ensure_company(company_id)
        rows = await self.supplier_repository.list_by_company(
            company_id, limit, offset, search=search
        )
        total = await self.supplier_repository.count_by_company(company_id, search=search)
        return list(rows), total

    async def update(self, company_id: UUID, supplier_id: UUID, payload: SupplierUpdate) -> Supplier:
        supplier = await self.get_in_company(company_id=company_id, supplier_id=supplier_id)
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(supplier, field, value)
        await self.session.commit()
        await self.session.refresh(supplier)
        return supplier

    async def soft_delete_in_company(self, company_id: UUID, supplier_id: UUID) -> None:
        supplier = await self.get_in_company(company_id=company_id, supplier_id=supplier_id)
        mark_deleted(supplier)
        await self.session.commit()
