"""Authentication service."""

from __future__ import annotations

import secrets
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.models.user_identity import UserIdentity
from app.models.user_role import UserRole
from app.repositories.refresh_token import RefreshTokenRepository
from app.repositories.user import UserRepository
from app.repositories.user_identity import UserIdentityRepository
from app.repositories.user_role import UserRoleRepository
from app.schemas.auth import AuthenticatedUserRead, LoginResponse, TokenPairRead
from app.schemas.user import UserRoleRead
from app.services.oidc import OidcProviderClient, build_oidc_providers, new_sso_state
from app.services.password import PasswordService
from app.services.token import TokenPayload, TokenService


@dataclass(frozen=True)
class OidcStateEntry:
    """Tracks in-flight OIDC state to prevent CSRF."""

    provider: str
    nonce: str
    created_at: datetime


@dataclass(frozen=True)
class PendingLoginExchange:
    """One-time login payload for SPA handoff after browser SSO."""

    login: LoginResponse
    expires_at: datetime


class AuthService:
    """Business logic for local and SSO authentication."""

    _state_store: dict[str, OidcStateEntry] = {}
    _exchange_store: dict[str, PendingLoginExchange] = {}
    _exchange_ttl = timedelta(minutes=5)

    def __init__(
        self,
        session: AsyncSession,
        *,
        token_service: TokenService | None = None,
        password_service: PasswordService | None = None,
        providers: dict[str, OidcProviderClient] | None = None,
    ) -> None:
        self.session = session
        self.token_service = token_service or TokenService()
        self.password_service = password_service or PasswordService()
        self.user_repository = UserRepository(session)
        self.user_role_repository = UserRoleRepository(session)
        self.refresh_token_repository = RefreshTokenRepository(session)
        self.user_identity_repository = UserIdentityRepository(session)
        self.providers = providers or build_oidc_providers()

    async def login_local(self, *, company_id: uuid.UUID, email: str, password: str) -> LoginResponse:
        """Authenticate user using local credentials."""

        user = await self.user_repository.get_active_by_company_email(company_id=company_id, email=email)
        if user is None or not self.password_service.verify_password(password, user.password_hash):
            msg = "Invalid credentials."
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=msg)
        return await self._build_login_response(user)

    async def refresh(self, refresh_token: str) -> TokenPairRead:
        """Rotate refresh token and issue a new token pair."""

        payload = self._decode_or_raise(refresh_token, expected_type="refresh")
        token_entry = await self.refresh_token_repository.get_active_by_jti(payload.jti)
        if token_entry is None:
            msg = "Refresh token is invalid or revoked."
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=msg)
        if token_entry.expires_at <= datetime.now(UTC):
            msg = "Refresh token has expired."
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=msg)

        user = await self.user_repository.get_by_id(uuid.UUID(payload.sub))
        if user is None or not user.is_active:
            msg = "User is not active."
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=msg)

        revoked_at = datetime.now(UTC)
        await self.refresh_token_repository.revoke(token_entry, revoked_at)

        role_names = await self._list_role_names(user.id)
        access_token, expires_in = self.token_service.create_access_token(
            user_id=user.id,
            company_id=user.company_id,
            roles=role_names,
        )
        next_refresh_token, next_jti = self.token_service.create_refresh_token(
            user_id=user.id,
            company_id=user.company_id,
            token_family_id=token_entry.token_family_id,
        )
        await self.refresh_token_repository.add(
            RefreshToken(
                user_id=user.id,
                token_family_id=token_entry.token_family_id,
                jti=next_jti,
                expires_at=datetime.fromtimestamp(self._decode_or_raise(next_refresh_token, "refresh").exp, tz=UTC),
            )
        )
        await self.session.commit()
        return TokenPairRead(
            access_token=access_token,
            refresh_token=next_refresh_token,
            expires_in=expires_in,
        )

    async def logout(self, refresh_token: str) -> None:
        """Revoke one refresh token family."""

        payload = self._decode_or_raise(refresh_token, expected_type="refresh")
        token_entry = await self.refresh_token_repository.get_active_by_jti(payload.jti)
        if token_entry is None:
            return
        await self.refresh_token_repository.revoke_family(
            user_id=token_entry.user_id,
            token_family_id=token_entry.token_family_id,
            revoked_at=datetime.now(UTC),
        )
        await self.session.commit()

    async def me(self, access_token: str) -> AuthenticatedUserRead:
        """Resolve authenticated user profile from access token."""

        payload = self._decode_or_raise(access_token, expected_type="access")
        user = await self.user_repository.get_by_id(uuid.UUID(payload.sub))
        if user is None or not user.is_active:
            msg = "User is not active."
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=msg)
        roles = await self._list_roles(user.id)
        return AuthenticatedUserRead(
            id=user.id,
            company_id=user.company_id,
            name=user.name,
            email=user.email,
            roles=roles,
        )

    def sso_start(self, provider: str) -> tuple[str, str]:
        """Prepare provider login start URL and state."""

        client = self._provider_or_404(provider)
        state, nonce = new_sso_state()
        self._state_store[state] = OidcStateEntry(
            provider=provider,
            nonce=nonce,
            created_at=datetime.now(UTC),
        )
        return client.build_authorization_url(state=state, nonce=nonce), state

    async def sso_callback(self, *, provider: str, code: str, state: str) -> LoginResponse:
        """Exchange provider callback data for API credentials."""

        client = self._provider_or_404(provider)
        state_entry = self._state_store.get(state)
        if state_entry is None or state_entry.provider != provider:
            msg = "Invalid state."
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)
        self._state_store.pop(state, None)

        try:
            profile = await client.exchange_code(code=code)
        except Exception as exc:  # noqa: BLE001
            msg = "SSO callback exchange failed."
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=msg) from exc

        provider_subject = profile["provider_subject"]
        email = profile["email"].lower()
        name = profile["name"]
        email_verified = profile["email_verified"] == "true"

        identity = await self.user_identity_repository.get_by_provider_subject(provider, provider_subject)
        if identity is not None:
            user = await self.user_repository.get_by_id(identity.user_id)
            if user is None or not user.is_active:
                msg = "User is not active."
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=msg)
            return await self._build_login_response(user)

        # Fallback: attach to existing user by email when possible.
        # If multiple tenants contain same email, we reject and require explicit link flow.
        user = await self._find_unique_active_user_by_email(email)
        if user is None:
            msg = "No local user found for this SSO account."
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg)

        await self.user_identity_repository.add(
            UserIdentity(
                user_id=user.id,
                provider=provider,
                provider_subject=provider_subject,
                email_verified=email_verified,
            )
        )
        await self.session.commit()
        return await self._build_login_response(user)

    def store_pending_login(self, login: LoginResponse) -> str:
        """Store login result for one-time exchange; returns opaque code."""

        code = secrets.token_urlsafe(32)
        expires_at = datetime.now(UTC) + self._exchange_ttl
        AuthService._exchange_store[code] = PendingLoginExchange(login=login, expires_at=expires_at)
        return code

    @classmethod
    def consume_exchange_code(cls, code: str) -> LoginResponse:
        """Redeem one-time code from SSO redirect; invalidates code."""

        entry = cls._exchange_store.pop(code, None)
        if entry is None or entry.expires_at <= datetime.now(UTC):
            msg = "Invalid or expired exchange code."
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=msg)
        return entry.login

    async def _build_login_response(self, user: User) -> LoginResponse:
        user.last_login_at = datetime.now(UTC)
        role_names = await self._list_role_names(user.id)
        access_token, expires_in = self.token_service.create_access_token(
            user_id=user.id,
            company_id=user.company_id,
            roles=role_names,
        )
        token_family_id = uuid.uuid4()
        refresh_token, refresh_jti = self.token_service.create_refresh_token(
            user_id=user.id,
            company_id=user.company_id,
            token_family_id=token_family_id,
        )
        refresh_payload = self._decode_or_raise(refresh_token, expected_type="refresh")
        await self.refresh_token_repository.add(
            RefreshToken(
                user_id=user.id,
                token_family_id=token_family_id,
                jti=refresh_jti,
                expires_at=datetime.fromtimestamp(refresh_payload.exp, tz=UTC),
            )
        )
        await self.session.commit()
        roles = await self._list_roles(user.id)
        return LoginResponse(
            user=AuthenticatedUserRead(
                id=user.id,
                company_id=user.company_id,
                name=user.name,
                email=user.email,
                roles=roles,
            ),
            tokens=TokenPairRead(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=expires_in,
            ),
        )

    async def _list_role_names(self, user_id: uuid.UUID) -> list[str]:
        roles = await self.user_role_repository.list_active_roles_for_user(user_id)
        return [role.name for role in roles]

    async def _list_roles(self, user_id: uuid.UUID) -> list[UserRoleRead]:
        roles = await self.user_role_repository.list_active_roles_for_user(user_id)
        return [UserRoleRead(id=role.id, name=role.name, description=role.description) for role in roles]

    def _decode_or_raise(self, token: str, expected_type: str) -> TokenPayload:
        try:
            payload = self.token_service.decode_token(token)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
        if payload.token_type != expected_type:
            msg = f"Expected a {expected_type} token."
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=msg)
        return payload

    def _provider_or_404(self, provider: str) -> OidcProviderClient:
        client = self.providers.get(provider)
        if client is None:
            msg = "Unsupported SSO provider."
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg)
        return client

    async def _find_unique_active_user_by_email(self, email: str) -> User | None:
        # Reuse existing user repository by scanning active users per tenant is not available.
        # Query directly through repository session to avoid introducing a leaky abstraction.
        from sqlalchemy import select

        stmt = select(User).where(
            User.email == email,
            User.deleted_at.is_(None),
            User.is_active.is_(True),
        )
        result = await self.session.execute(stmt)
        users = result.scalars().all()
        if len(users) != 1:
            return None
        return users[0]
