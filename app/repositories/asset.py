"""Asset repository."""

from __future__ import annotations

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import Select, func, or_, select

from app.models.asset import Asset, AssetCategory, AssetStatus
from app.repositories.base import BaseRepository


class AssetRepository(BaseRepository[Asset]):
    """Persistence operations for assets."""

    model = Asset

    def _filtered_stmt(
        self,
        company_id: UUID,
        *,
        search: str | None,
        category: AssetCategory | None,
        status: AssetStatus | None,
        location: str | None,
    ) -> Select[tuple[Asset]]:
        stmt = self._active_stmt().where(Asset.company_id == company_id)
        if search and search.strip():
            term = f"%{search.strip()}%"
            stmt = stmt.where(
                or_(
                    Asset.name.ilike(term),
                    Asset.description.ilike(term),
                    Asset.brand.ilike(term),
                    Asset.location.ilike(term),
                ),
            )
        if category is not None:
            stmt = stmt.where(Asset.category == category)
        if status is not None:
            stmt = stmt.where(Asset.status == status)
        if location is not None and location.strip():
            stmt = stmt.where(Asset.location.ilike(f"%{location.strip()}%"))
        return stmt

    def _order_clause(self, sort_by: str, sort_order: str):
        column_map = {
            "created_at": Asset.created_at,
            "name": Asset.name,
            "price": Asset.price,
            "purchase_date": Asset.purchase_date,
        }
        col = column_map.get(sort_by, Asset.created_at)
        return col.desc() if sort_order.lower() == "desc" else col.asc()

    async def list_by_company(
        self,
        company_id: UUID,
        limit: int,
        offset: int,
        *,
        search: str | None = None,
        category: AssetCategory | None = None,
        status: AssetStatus | None = None,
        location: str | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> Sequence[Asset]:
        stmt = self._filtered_stmt(
            company_id,
            search=search,
            category=category,
            status=status,
            location=location,
        ).order_by(self._order_clause(sort_by, sort_order))
        stmt = stmt.limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count_by_company(
        self,
        company_id: UUID,
        *,
        search: str | None = None,
        category: AssetCategory | None = None,
        status: AssetStatus | None = None,
        location: str | None = None,
    ) -> int:
        filtered = self._filtered_stmt(
            company_id,
            search=search,
            category=category,
            status=status,
            location=location,
        )
        stmt = select(func.count()).select_from(filtered.subquery())
        result = await self.session.execute(stmt)
        return int(result.scalar_one())
