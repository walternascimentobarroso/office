"""Authentication and security settings."""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


def _split_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


@dataclass(frozen=True)
class SecuritySettings:
    """Runtime settings for authentication and authorization."""

    jwt_secret: str
    jwt_algorithm: str
    access_token_ttl_min: int
    refresh_token_ttl_days: int
    cors_origins: list[str]
    oidc_google_client_id: str | None
    oidc_google_client_secret: str | None
    oidc_google_redirect_uri: str | None
    oidc_microsoft_client_id: str | None
    oidc_microsoft_client_secret: str | None
    oidc_microsoft_redirect_uri: str | None
    frontend_url: str | None
    frontend_sso_success_path: str


@lru_cache(maxsize=1)
def get_security_settings() -> SecuritySettings:
    """Build and cache security settings from environment."""

    jwt_secret = os.getenv("JWT_SECRET", "dev-insecure-change-me-32-bytes-min")

    jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256")
    access_token_ttl_min = int(os.getenv("ACCESS_TOKEN_TTL_MIN", "15"))
    refresh_token_ttl_days = int(os.getenv("REFRESH_TOKEN_TTL_DAYS", "7"))
    cors_origins_raw = os.getenv("CORS_ALLOW_ORIGINS", "http://localhost:3000,http://localhost:5173")
    cors_origins = _split_csv(cors_origins_raw)

    return SecuritySettings(
        jwt_secret=jwt_secret,
        jwt_algorithm=jwt_algorithm,
        access_token_ttl_min=access_token_ttl_min,
        refresh_token_ttl_days=refresh_token_ttl_days,
        cors_origins=cors_origins,
        oidc_google_client_id=os.getenv("OIDC_GOOGLE_CLIENT_ID"),
        oidc_google_client_secret=os.getenv("OIDC_GOOGLE_CLIENT_SECRET"),
        oidc_google_redirect_uri=os.getenv("OIDC_GOOGLE_REDIRECT_URI"),
        oidc_microsoft_client_id=os.getenv("OIDC_MICROSOFT_CLIENT_ID"),
        oidc_microsoft_client_secret=os.getenv("OIDC_MICROSOFT_CLIENT_SECRET"),
        oidc_microsoft_redirect_uri=os.getenv("OIDC_MICROSOFT_REDIRECT_URI"),
        frontend_url=(os.getenv("FRONTEND_URL") or None),
        frontend_sso_success_path=os.getenv("FRONTEND_SSO_SUCCESS_PATH", "/auth/callback"),
    )
