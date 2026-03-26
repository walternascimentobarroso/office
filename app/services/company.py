"""Company service."""

from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company import Company
from app.repositories.company import CompanyRepository
from app.schemas.company import CompanyCreate, CompanyUpdate
from app.utils.soft_delete import mark_deleted


class CompanyService:
    """Business operations for companies."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = CompanyRepository(session)

    async def create(self, payload: CompanyCreate) -> Company:
        if await self.repository.tax_id_exists(payload.tax_id):
            msg = "Company tax_id already exists."
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=msg)

        company = Company(
            name=payload.name,
            tax_id=payload.tax_id,
            address=payload.address,
        )
        created = await self.repository.add(company)
        await self.session.commit()
        return created

    async def get(self, company_id: UUID) -> Company:
        company = await self.repository.get_by_id(company_id)
        if company is None:
            msg = "Company not found."
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg)
        return company

    async def list(self, limit: int = 50, offset: int = 0) -> tuple[list[Company], int]:
        companies = await self.repository.list(limit=limit, offset=offset)
        total = await self.repository.count()
        return list(companies), total

    async def soft_delete(self, company_id: UUID) -> None:
        company = await self.get(company_id)
        mark_deleted(company)
        await self.session.commit()

    async def update(self, company_id: UUID, payload: CompanyUpdate) -> Company:
        company = await self.get(company_id)
        update_data = payload.model_dump(exclude_unset=True)
        new_tax_id = update_data.get("tax_id")
        if new_tax_id and new_tax_id != company.tax_id:
            if await self.repository.tax_id_exists(new_tax_id):
                msg = "Company tax_id already exists."
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=msg)
        for field, value in update_data.items():
            setattr(company, field, value)
        await self.session.commit()
        await self.session.refresh(company)
        return company
