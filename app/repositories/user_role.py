"""User-role association repository."""

from __future__ import annotations

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select

from app.models.role import Role
from app.models.user_role import UserRole
from app.repositories.base import BaseRepository


class UserRoleRepository(BaseRepository[UserRole]):
    """Persistence operations for user-role assignments."""

    model = UserRole

    async def list_active_links(self, user_id: UUID) -> Sequence[UserRole]:
        stmt = self._active_stmt().where(UserRole.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_any_link(self, user_id: UUID, role_id: UUID) -> UserRole | None:
        stmt = select(UserRole).where(UserRole.user_id == user_id, UserRole.role_id == role_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_active_roles_for_user(self, user_id: UUID) -> Sequence[Role]:
        stmt = (
            select(Role)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(
                UserRole.user_id == user_id,
                UserRole.deleted_at.is_(None),
                Role.deleted_at.is_(None),
            )
            .order_by(Role.name.asc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
