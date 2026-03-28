"""Authentication API routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_user
from app.db.session import get_db_session
from app.schemas.auth import (
    AuthenticatedUserRead,
    LoginRequest,
    LoginResponse,
    LogoutRequest,
    RefreshRequest,
    SsoCallbackRequest,
    SsoStartRead,
    TokenPairRead,
)
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
async def login(
    payload: LoginRequest,
    session: AsyncSession = Depends(get_db_session),
) -> LoginResponse:
    service = AuthService(session)
    return await service.login_local(
        company_id=payload.company_id,
        email=payload.email.lower(),
        password=payload.password,
    )


@router.post("/refresh", response_model=TokenPairRead)
async def refresh_tokens(
    payload: RefreshRequest,
    session: AsyncSession = Depends(get_db_session),
) -> TokenPairRead:
    service = AuthService(session)
    return await service.refresh(payload.refresh_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    payload: LogoutRequest,
    session: AsyncSession = Depends(get_db_session),
) -> Response:
    service = AuthService(session)
    await service.logout(payload.refresh_token)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/me", response_model=AuthenticatedUserRead)
async def me(current_user: AuthenticatedUserRead = Depends(get_current_user)) -> AuthenticatedUserRead:
    return current_user


@router.get("/sso/{provider}/start", response_model=SsoStartRead)
async def sso_start(
    provider: str,
    session: AsyncSession = Depends(get_db_session),
) -> SsoStartRead:
    service = AuthService(session)
    authorization_url, state = service.sso_start(provider)
    return SsoStartRead(authorization_url=authorization_url, state=state)


@router.get("/sso/{provider}/callback", response_model=LoginResponse)
async def sso_callback(
    provider: str,
    code: str,
    state: str,
    session: AsyncSession = Depends(get_db_session),
) -> LoginResponse:
    service = AuthService(session)
    payload = SsoCallbackRequest(code=code, state=state)
    return await service.sso_callback(provider=provider, code=payload.code, state=payload.state)


@router.post("/sso/{provider}/callback", response_model=LoginResponse)
async def sso_callback_post(
    provider: str,
    payload: SsoCallbackRequest,
    session: AsyncSession = Depends(get_db_session),
) -> LoginResponse:
    service = AuthService(session)
    return await service.sso_callback(provider=provider, code=payload.code, state=payload.state)
