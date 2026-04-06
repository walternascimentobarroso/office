"""SMTP-backed async email sender."""

from __future__ import annotations

import os
from dataclasses import dataclass
from email.message import EmailMessage

import aiosmtplib


@dataclass(frozen=True)
class SmtpSettings:
    """SMTP connection and envelope settings."""

    host: str
    port: int
    username: str
    password: str
    from_address: str
    use_implicit_tls: bool
    use_starttls: bool


def load_smtp_settings_from_env() -> SmtpSettings:
    """Build SMTP settings from environment variables."""

    host = os.getenv("SMTP_HOST", "").strip()
    username = os.getenv("SMTP_USER", "").strip()
    password = os.getenv("SMTP_PASSWORD", "")
    from_address = os.getenv("SMTP_FROM", "").strip()
    port_raw = os.getenv("SMTP_PORT", "587").strip()
    if not host or not username or not from_address:
        msg = "SMTP is not configured (SMTP_HOST, SMTP_USER, SMTP_FROM are required)."
        raise RuntimeError(msg)
    port = int(port_raw)
    if port == 465:
        use_implicit_tls = True
        use_starttls = False
    else:
        use_implicit_tls = False
        starttls_default = "true" if port == 587 else "false"
        use_starttls = os.getenv("SMTP_STARTTLS", starttls_default).lower() in ("1", "true", "yes")
    return SmtpSettings(
        host=host,
        port=port,
        username=username,
        password=password,
        from_address=from_address,
        use_implicit_tls=use_implicit_tls,
        use_starttls=use_starttls,
    )


class SmtpEmailSender:
    """Async SMTP sender using aiosmtplib."""

    def __init__(self, settings: SmtpSettings) -> None:
        self._settings = settings

    async def send(self, *, to: str, subject: str, body: str) -> None:
        """Send a plain-text email via SMTP."""

        message = EmailMessage()
        message["From"] = self._settings.from_address
        message["To"] = to
        message["Subject"] = subject
        message.set_content(body)
        await aiosmtplib.send(
            message,
            hostname=self._settings.host,
            port=self._settings.port,
            username=self._settings.username,
            password=self._settings.password,
            use_tls=self._settings.use_implicit_tls,
            start_tls=self._settings.use_starttls,
        )
