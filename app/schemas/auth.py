"""Authentication schemas."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.user import UserRoleRead


class LoginRequest(BaseModel):
    """Payload for local login."""

    company_id: UUID
    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=8, max_length=255)


class TokenPairRead(BaseModel):
    """Access and refresh token payload."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class AuthenticatedUserRead(BaseModel):
    """Authenticated user profile."""

    id: UUID
    company_id: UUID
    name: str
    email: str
    roles: list[UserRoleRead] = Field(default_factory=list)


class LoginResponse(BaseModel):
    """Response returned by successful login."""

    user: AuthenticatedUserRead
    tokens: TokenPairRead


class RefreshRequest(BaseModel):
    """Payload for refreshing access credentials."""

    refresh_token: str = Field(min_length=1)


class LogoutRequest(BaseModel):
    """Payload for logout."""

    refresh_token: str = Field(min_length=1)


class SsoStartRead(BaseModel):
    """Response with provider redirect URL."""

    authorization_url: str
    state: str


class SsoCallbackRequest(BaseModel):
    """Input for provider callback exchange."""

    code: str = Field(min_length=1)
    state: str = Field(min_length=1)
