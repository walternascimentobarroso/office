"""Email sender protocol."""

from __future__ import annotations

from typing import Protocol


class EmailSender(Protocol):
    """Abstraction for sending transactional email."""

    async def send(self, *, to: str, subject: str, body: str) -> None:
        """Send a plain-text email."""
