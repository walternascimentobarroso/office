"""Company repository."""

from __future__ import annotations

from sqlalchemy import select

from app.models.company import Company
from app.repositories.base import BaseRepository


class CompanyRepository(BaseRepository[Company]):
    """Persistence operations for companies."""

    model = Company

    async def get_by_tax_id(self, tax_id: str) -> Company | None:
        stmt = self._active_stmt().where(Company.tax_id == tax_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def tax_id_exists(self, tax_id: str) -> bool:
        stmt = select(Company.id).where(Company.tax_id == tax_id, Company.deleted_at.is_(None))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None
