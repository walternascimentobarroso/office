"""Invoice email log repository."""

from __future__ import annotations

from collections.abc import Sequence
from uuid import UUID

from app.models.invoice_email_log import InvoiceEmailLog
from app.repositories.base import BaseRepository


class InvoiceEmailLogRepository(BaseRepository[InvoiceEmailLog]):
    """Persistence operations for invoice email logs."""

    model = InvoiceEmailLog

    async def get_active_by_id(self, log_id: UUID) -> InvoiceEmailLog | None:
        stmt = self._active_stmt().where(InvoiceEmailLog.id == log_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_company(
        self,
        company_id: UUID,
        *,
        limit: int = 100,
        offset: int = 0,
    ) -> Sequence[InvoiceEmailLog]:
        stmt = (
            self._active_stmt()
            .where(InvoiceEmailLog.company_id == company_id)
            .order_by(InvoiceEmailLog.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
