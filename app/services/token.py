"""JWT token service."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

import jwt
from jwt import InvalidTokenError

from app.core.security import SecuritySettings, get_security_settings


@dataclass(frozen=True)
class TokenPayload:
    """Validated token payload data."""

    sub: str
    token_type: str
    jti: str
    exp: int
    iat: int
    company_id: str
    roles: list[str]


class TokenService:
    """Encodes and decodes JWT access/refresh tokens."""

    def __init__(self, settings: SecuritySettings | None = None) -> None:
        self.settings = settings or get_security_settings()

    def create_access_token(self, *, user_id: uuid.UUID, company_id: uuid.UUID, roles: list[str]) -> tuple[str, int]:
        """Create a short-lived access token and return ttl in seconds."""

        now = datetime.now(UTC)
        expires_at = now + timedelta(minutes=self.settings.access_token_ttl_min)
        ttl_seconds = int((expires_at - now).total_seconds())
        token = jwt.encode(
            payload={
                "sub": str(user_id),
                "type": "access",
                "jti": uuid.uuid4().hex,
                "iat": int(now.timestamp()),
                "exp": int(expires_at.timestamp()),
                "company_id": str(company_id),
                "roles": roles,
            },
            key=self.settings.jwt_secret,
            algorithm=self.settings.jwt_algorithm,
        )
        return token, ttl_seconds

    def create_refresh_token(self, *, user_id: uuid.UUID, company_id: uuid.UUID, token_family_id: uuid.UUID) -> tuple[str, str]:
        """Create a refresh token and return token with jti."""

        now = datetime.now(UTC)
        expires_at = now + timedelta(days=self.settings.refresh_token_ttl_days)
        jti = uuid.uuid4().hex
        token = jwt.encode(
            payload={
                "sub": str(user_id),
                "type": "refresh",
                "jti": jti,
                "iat": int(now.timestamp()),
                "exp": int(expires_at.timestamp()),
                "company_id": str(company_id),
                "token_family_id": str(token_family_id),
            },
            key=self.settings.jwt_secret,
            algorithm=self.settings.jwt_algorithm,
        )
        return token, jti

    def decode_token(self, token: str) -> TokenPayload:
        """Decode and validate token signature and required claims."""

        try:
            payload = jwt.decode(
                jwt=token,
                key=self.settings.jwt_secret,
                algorithms=[self.settings.jwt_algorithm],
            )
        except InvalidTokenError as exc:
            msg = "Invalid token."
            raise ValueError(msg) from exc

        try:
            sub = str(payload["sub"])
            token_type = str(payload["type"])
            jti = str(payload["jti"])
            exp = int(payload["exp"])
            iat = int(payload["iat"])
            company_id = str(payload["company_id"])
        except (KeyError, TypeError, ValueError) as exc:
            msg = "Token payload is malformed."
            raise ValueError(msg) from exc

        roles_raw = payload.get("roles")
        roles = [str(item) for item in roles_raw] if isinstance(roles_raw, list) else []
        return TokenPayload(
            sub=sub,
            token_type=token_type,
            jti=jti,
            exp=exp,
            iat=iat,
            company_id=company_id,
            roles=roles,
        )
