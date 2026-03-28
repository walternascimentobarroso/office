"""Refresh token repository."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import select

from app.models.refresh_token import RefreshToken
from app.repositories.base import BaseRepository


class RefreshTokenRepository(BaseRepository[RefreshToken]):
    """Persistence operations for refresh tokens."""

    model = RefreshToken

    async def get_active_by_jti(self, jti: str) -> RefreshToken | None:
        stmt = self._active_stmt().where(
            RefreshToken.jti == jti,
            RefreshToken.revoked_at.is_(None),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def revoke(self, token: RefreshToken, revoked_at: datetime) -> None:
        token.revoked_at = revoked_at

    async def revoke_family(self, user_id: UUID, token_family_id: UUID, revoked_at: datetime) -> int:
        stmt = self._active_stmt().where(
            RefreshToken.user_id == user_id,
            RefreshToken.token_family_id == token_family_id,
            RefreshToken.revoked_at.is_(None),
        )
        result = await self.session.execute(stmt)
        tokens = result.scalars().all()
        for token in tokens:
            token.revoked_at = revoked_at
        return len(tokens)
