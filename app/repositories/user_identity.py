"""User identity repository."""

from __future__ import annotations

from sqlalchemy import select

from app.models.user_identity import UserIdentity
from app.repositories.base import BaseRepository


class UserIdentityRepository(BaseRepository[UserIdentity]):
    """Persistence operations for external user identities."""

    model = UserIdentity

    async def get_by_provider_subject(self, provider: str, provider_subject: str) -> UserIdentity | None:
        stmt = self._active_stmt().where(
            UserIdentity.provider == provider,
            UserIdentity.provider_subject == provider_subject,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
