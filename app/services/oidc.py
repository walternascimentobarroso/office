"""OIDC provider abstractions and clients."""

from __future__ import annotations

import secrets
from dataclasses import dataclass
from typing import Protocol
from urllib.parse import urlencode

import httpx

from app.core.security import SecuritySettings, get_security_settings


class OidcProviderClient(Protocol):
    """Abstraction for provider-specific OIDC operations."""

    provider_name: str

    def build_authorization_url(self, state: str, nonce: str) -> str:
        """Return provider authorization URL."""

    async def exchange_code(self, code: str) -> dict[str, str]:
        """Exchange auth code and return external identity data."""


@dataclass(frozen=True)
class ProviderEndpoints:
    """Provider endpoint metadata."""

    authorize_url: str
    token_url: str
    userinfo_url: str


class _BaseOidcClient:
    """Shared logic for OIDC providers."""

    def __init__(
        self,
        *,
        provider_name: str,
        endpoints: ProviderEndpoints,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
    ) -> None:
        self.provider_name = provider_name
        self.endpoints = endpoints
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri

    def build_authorization_url(self, state: str, nonce: str) -> str:
        params = urlencode(
            {
                "client_id": self.client_id,
                "response_type": "code",
                "redirect_uri": self.redirect_uri,
                "scope": "openid email profile",
                "state": state,
                "nonce": nonce,
            }
        )
        return f"{self.endpoints.authorize_url}?{params}"

    async def exchange_code(self, code: str) -> dict[str, str]:
        async with httpx.AsyncClient(timeout=10.0) as client:
            token_response = await client.post(
                self.endpoints.token_url,
                data={
                    "grant_type": "authorization_code",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "code": code,
                    "redirect_uri": self.redirect_uri,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            token_response.raise_for_status()
            token_data = token_response.json()
            access_token = str(token_data.get("access_token", ""))
            if not access_token:
                msg = "Provider did not return an access token."
                raise ValueError(msg)

            userinfo_response = await client.get(
                self.endpoints.userinfo_url,
                headers={"Authorization": f"Bearer {access_token}"},
            )
            userinfo_response.raise_for_status()
            profile = userinfo_response.json()

        provider_subject = str(profile.get("sub", ""))
        email = str(profile.get("email", ""))
        email_verified = bool(profile.get("email_verified", False))
        if not provider_subject or not email:
            msg = "Provider user info is incomplete."
            raise ValueError(msg)

        return {
            "provider_subject": provider_subject,
            "email": email,
            "email_verified": "true" if email_verified else "false",
            "name": str(profile.get("name", email.split("@", maxsplit=1)[0])),
        }


class GoogleOidcClient(_BaseOidcClient):
    """Google OIDC implementation."""


class MicrosoftOidcClient(_BaseOidcClient):
    """Microsoft OIDC implementation."""


def build_oidc_providers(
    settings: SecuritySettings | None = None,
) -> dict[str, OidcProviderClient]:
    """Create configured OIDC provider clients."""

    cfg = settings or get_security_settings()
    providers: dict[str, OidcProviderClient] = {}

    if cfg.oidc_google_client_id and cfg.oidc_google_client_secret and cfg.oidc_google_redirect_uri:
        providers["google"] = GoogleOidcClient(
            provider_name="google",
            endpoints=ProviderEndpoints(
                authorize_url="https://accounts.google.com/o/oauth2/v2/auth",
                token_url="https://oauth2.googleapis.com/token",
                userinfo_url="https://openidconnect.googleapis.com/v1/userinfo",
            ),
            client_id=cfg.oidc_google_client_id,
            client_secret=cfg.oidc_google_client_secret,
            redirect_uri=cfg.oidc_google_redirect_uri,
        )

    if cfg.oidc_microsoft_client_id and cfg.oidc_microsoft_client_secret and cfg.oidc_microsoft_redirect_uri:
        providers["microsoft"] = MicrosoftOidcClient(
            provider_name="microsoft",
            endpoints=ProviderEndpoints(
                authorize_url="https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
                token_url="https://login.microsoftonline.com/common/oauth2/v2.0/token",
                userinfo_url="https://graph.microsoft.com/oidc/userinfo",
            ),
            client_id=cfg.oidc_microsoft_client_id,
            client_secret=cfg.oidc_microsoft_client_secret,
            redirect_uri=cfg.oidc_microsoft_redirect_uri,
        )
    return providers


def new_sso_state() -> tuple[str, str]:
    """Create state and nonce values."""

    return secrets.token_urlsafe(24), secrets.token_urlsafe(24)
