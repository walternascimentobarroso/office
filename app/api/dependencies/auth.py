"""Authentication and authorization dependencies for FastAPI routes."""

from __future__ import annotations

import uuid
from collections.abc import Callable

from fastapi import Depends, HTTPException, Path, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.schemas.auth import AuthenticatedUserRead
from app.services.auth import AuthService
from app.services.token import TokenService

_bearer_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
    session: AsyncSession = Depends(get_db_session),
) -> AuthenticatedUserRead:
    """Resolve currently authenticated user from bearer token."""

    return await AuthService(session).me(credentials.credentials)


async def get_current_token_payload(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
) -> tuple[uuid.UUID, uuid.UUID, list[str]]:
    """Return (user_id, company_id, roles) from access token."""

    token = credentials.credentials
    token_service = TokenService()
    try:
        payload = token_service.decode_token(token)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
    if payload.token_type != "access":
        msg = "Expected an access token."
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=msg)
    return uuid.UUID(payload.sub), uuid.UUID(payload.company_id), payload.roles


def require_roles(*expected_roles: str) -> Callable[[tuple[uuid.UUID, uuid.UUID, list[str]]], None]:
    """Create dependency that enforces at least one expected role."""

    expected = {item.lower() for item in expected_roles}

    async def _dependency(
        payload: tuple[uuid.UUID, uuid.UUID, list[str]] = Depends(get_current_token_payload),
    ) -> None:
        _, _, roles = payload
        user_roles = {role.lower() for role in roles}
        if expected and user_roles.isdisjoint(expected):
            msg = "Insufficient permissions."
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=msg)

    return _dependency


async def require_company_access(
    company_id: uuid.UUID = Path(...),
    payload: tuple[uuid.UUID, uuid.UUID, list[str]] = Depends(get_current_token_payload),
) -> None:
    """Ensure token company matches path company unless user is admin."""

    _, token_company_id, roles = payload
    role_names = {role.lower() for role in roles}
    if "admin" in role_names:
        return
    if token_company_id != company_id:
        msg = "Token does not match requested company scope."
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=msg)
