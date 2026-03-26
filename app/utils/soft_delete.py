"""Soft-delete helpers."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Protocol


class SoftDeletable(Protocol):
    """Contract for objects carrying deleted_at."""

    deleted_at: datetime | None


def mark_deleted(entity: SoftDeletable) -> None:
    """Mark an entity as soft deleted."""
    entity.deleted_at = datetime.now(UTC)


def restore_deleted(entity: SoftDeletable) -> None:
    """Restore a soft-deleted entity."""
    entity.deleted_at = None
