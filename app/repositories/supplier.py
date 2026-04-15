"""Supplier repository."""

from __future__ import annotations

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import Select, func, or_, select

from app.models.supplier import Supplier
from app.repositories.base import BaseRepository


class SupplierRepository(BaseRepository[Supplier]):
    """Persistence operations for suppliers."""

    model = Supplier

    def _filtered_stmt(self, company_id: UUID, *, search: str | None) -> Select[tuple[Supplier]]:
        stmt = self._active_stmt().where(Supplier.company_id == company_id)
        if search and search.strip():
            term = f"%{search.strip()}%"
            stmt = stmt.where(
                or_(
                    Supplier.name.ilike(term),
                    Supplier.contact_name.ilike(term),
                    Supplier.email.ilike(term),
                    Supplier.tax_id.ilike(term),
                ),
            )
        return stmt

    async def list_by_company(
        self,
        company_id: UUID,
        limit: int,
        offset: int,
        *,
        search: str | None = None,
    ) -> Sequence[Supplier]:
        stmt = (
            self._filtered_stmt(company_id, search=search)
            .order_by(Supplier.name.asc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count_by_company(self, company_id: UUID, *, search: str | None = None) -> int:
        filtered = self._filtered_stmt(company_id, search=search)
        stmt = select(func.count()).select_from(filtered.subquery())
        result = await self.session.execute(stmt)
        return int(result.scalar_one())
