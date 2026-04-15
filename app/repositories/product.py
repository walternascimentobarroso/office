"""Product repository."""

from __future__ import annotations

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import Select, func, or_, select

from app.models.product import Product
from app.repositories.base import BaseRepository


class ProductRepository(BaseRepository[Product]):
    """Persistence operations for products."""

    model = Product

    def _filtered_stmt(
        self,
        company_id: UUID,
        *,
        search: str | None,
        category: str | None,
        active: bool | None,
    ) -> Select[tuple[Product]]:
        stmt = self._active_stmt().where(Product.company_id == company_id)
        if search and search.strip():
            term = f"%{search.strip()}%"
            stmt = stmt.where(
                or_(
                    Product.name.ilike(term),
                    Product.category.ilike(term),
                ),
            )
        if category is not None:
            stmt = stmt.where(Product.category.ilike(category))
        if active is not None:
            stmt = stmt.where(Product.active == active)
        return stmt

    async def list_by_company(
        self,
        company_id: UUID,
        limit: int,
        offset: int,
        *,
        search: str | None = None,
        category: str | None = None,
        active: bool | None = None,
    ) -> Sequence[Product]:
        stmt = (
            self._filtered_stmt(company_id, search=search, category=category, active=active)
            .order_by(Product.name.asc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count_by_company(
        self,
        company_id: UUID,
        *,
        search: str | None = None,
        category: str | None = None,
        active: bool | None = None,
    ) -> int:
        filtered = self._filtered_stmt(company_id, search=search, category=category, active=active)
        stmt = select(func.count()).select_from(filtered.subquery())
        result = await self.session.execute(stmt)
        return int(result.scalar_one())
