"""User repository."""

from __future__ import annotations

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import func, select

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Persistence operations for users."""

    model = User

    async def list_by_company(
        self,
        company_id: UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> Sequence[User]:
        stmt = self._active_stmt().where(User.company_id == company_id).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count_by_company(self, company_id: UUID) -> int:
        stmt = select(func.count()).select_from(User).where(
            User.company_id == company_id,
            User.deleted_at.is_(None),
        )
        result = await self.session.execute(stmt)
        return int(result.scalar_one())

    async def exists_for_company_email(self, company_id: UUID, email: str) -> bool:
        stmt = select(User.id).where(
            User.company_id == company_id,
            User.email == email,
            User.deleted_at.is_(None),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def get_active_by_company_email(self, company_id: UUID, email: str) -> User | None:
        stmt = self._active_stmt().where(
            User.company_id == company_id,
            User.email == email,
            User.is_active.is_(True),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
