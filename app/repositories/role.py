"""Role repository."""

from __future__ import annotations

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select

from app.models.role import Role
from app.repositories.base import BaseRepository


class RoleRepository(BaseRepository[Role]):
    """Persistence operations for roles."""

    model = Role

    async def name_exists(self, name: str) -> bool:
        stmt = select(Role.id).where(Role.name == name, Role.deleted_at.is_(None))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def list_by_ids_active(self, role_ids: set[UUID]) -> Sequence[Role]:
        if not role_ids:
            return []
        stmt = self._active_stmt().where(Role.id.in_(role_ids))
        result = await self.session.execute(stmt)
        return result.scalars().all()
