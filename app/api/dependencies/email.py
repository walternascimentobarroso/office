"""Email-related FastAPI dependencies."""

from __future__ import annotations

from fastapi import HTTPException, status

from app.email.protocol import EmailSender
from app.email.smtp import SmtpEmailSender, load_smtp_settings_from_env


def get_email_sender() -> EmailSender:
    """Provide configured SMTP email sender."""

    try:
        settings = load_smtp_settings_from_env()
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    return SmtpEmailSender(settings)
