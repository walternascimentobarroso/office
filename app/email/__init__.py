"""Email delivery abstractions."""

from app.email.protocol import EmailSender
from app.email.smtp import SmtpEmailSender, load_smtp_settings_from_env

__all__ = [
    "EmailSender",
    "SmtpEmailSender",
    "load_smtp_settings_from_env",
]
