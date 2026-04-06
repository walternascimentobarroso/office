"""Send monthly invoice request email."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

import aiosmtplib
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.email.protocol import EmailSender
from app.models.invoice_email_log import InvoiceEmailLog, InvoiceEmailStatus
from app.repositories.company import CompanyRepository
from app.repositories.invoice_email_log import InvoiceEmailLogRepository
from app.schemas.billing import (
    InvoiceEmailHistoryItem,
    PreviewInvoiceEmailResponse,
    SendInvoiceEmailRequest,
    SendInvoiceEmailResponse,
)
from app.services.billing_scope import ensure_company_scope
from app.services.invoice_email_content import (
    InvoiceEmailContent,
    generate_invoice_email_content,
)


class SendInvoiceEmailService:
    """Generate, send, and log monthly invoice request emails."""

    def __init__(self, session: AsyncSession, email_sender: EmailSender | None) -> None:
        self.session = session
        self.email_sender = email_sender
        self._companies = CompanyRepository(session)
        self._logs = InvoiceEmailLogRepository(session)

    def generate_email_content(self, payload: SendInvoiceEmailRequest) -> InvoiceEmailContent:
        """Build subject, body, and total from the canonical template."""

        return generate_invoice_email_content(payload)

    async def send_email(self, *, to: str, subject: str, body: str) -> tuple[InvoiceEmailStatus, datetime | None, str | None]:
        """Deliver email via SMTP; return status, sent_at (if sent), and error message (if failed)."""

        if self.email_sender is None:
            msg = "Email sender is not configured for this operation."
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=msg)

        try:
            await self.email_sender.send(to=to, subject=subject, body=body)
        except (
            aiosmtplib.SMTPException,
            OSError,
            TimeoutError,
            ValueError,
            RuntimeError,
        ) as exc:
            return InvoiceEmailStatus.failed, None, str(exc)

        return InvoiceEmailStatus.sent, datetime.now(UTC), None

    async def save_log(
        self,
        *,
        company_id: UUID,
        month: int,
        year: int,
        to_email: str,
        subject: str,
        body: str,
        status_value: InvoiceEmailStatus,
        error_message: str | None,
        sent_at: datetime | None,
    ) -> InvoiceEmailLog:
        """Persist a log row and commit."""

        log = InvoiceEmailLog(
            company_id=company_id,
            month=month,
            year=year,
            to_email=to_email,
            subject=subject,
            body=body,
            status=status_value,
            error_message=error_message,
            sent_at=sent_at,
        )
        created = await self._logs.add(log)
        await self.session.commit()
        await self.session.refresh(created)
        return created

    async def preview_invoice_email(
        self,
        *,
        token_company_id: UUID,
        roles: list[str],
        payload: SendInvoiceEmailRequest,
    ) -> PreviewInvoiceEmailResponse:
        """Return subject, body, and total without sending."""

        ensure_company_scope(payload.company_id, token_company_id, roles)

        company = await self._companies.get_by_id(payload.company_id)
        if company is None:
            msg = "Company not found."
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg)

        content = self.generate_email_content(payload)
        return PreviewInvoiceEmailResponse(
            subject=content.subject,
            body=content.body,
            total=content.total,
        )

    async def send_invoice_email(
        self,
        *,
        token_company_id: UUID,
        roles: list[str],
        payload: SendInvoiceEmailRequest,
    ) -> SendInvoiceEmailResponse:
        """Generate, send, and log a monthly invoice request email."""

        ensure_company_scope(payload.company_id, token_company_id, roles)

        company = await self._companies.get_by_id(payload.company_id)
        if company is None:
            msg = "Company not found."
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg)

        content = self.generate_email_content(payload)
        status_value, sent_at, error_message = await self.send_email(
            to=str(payload.to_email),
            subject=content.subject,
            body=content.body,
        )
        created = await self.save_log(
            company_id=payload.company_id,
            month=payload.month,
            year=payload.year,
            to_email=str(payload.to_email),
            subject=content.subject,
            body=content.body,
            status_value=status_value,
            error_message=error_message,
            sent_at=sent_at,
        )

        return SendInvoiceEmailResponse(
            id=created.id,
            status=created.status.value,
            subject=created.subject,
            sent_at=created.sent_at,
            error_message=created.error_message,
        )

    async def list_invoice_emails(
        self,
        *,
        token_company_id: UUID,
        roles: list[str],
        company_id: UUID,
        limit: int,
        offset: int,
    ) -> list[InvoiceEmailHistoryItem]:
        """List invoice email logs for the company (scoped)."""

        ensure_company_scope(company_id, token_company_id, roles)

        rows = await self._logs.list_by_company(company_id, limit=limit, offset=offset)
        return [
            InvoiceEmailHistoryItem(
                id=row.id,
                month=row.month,
                year=row.year,
                status=row.status.value,
                to_email=row.to_email,
                sent_at=row.sent_at,
            )
            for row in rows
        ]

    async def resend_invoice_email(
        self,
        *,
        token_company_id: UUID,
        roles: list[str],
        log_id: UUID,
    ) -> SendInvoiceEmailResponse:
        """Resend stored subject/body from a log and append a new log row."""

        existing = await self._logs.get_active_by_id(log_id)
        if existing is None:
            msg = "Invoice email log not found."
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg)

        ensure_company_scope(existing.company_id, token_company_id, roles)

        status_value, sent_at, error_message = await self.send_email(
            to=existing.to_email,
            subject=existing.subject,
            body=existing.body,
        )
        created = await self.save_log(
            company_id=existing.company_id,
            month=existing.month,
            year=existing.year,
            to_email=existing.to_email,
            subject=existing.subject,
            body=existing.body,
            status_value=status_value,
            error_message=error_message,
            sent_at=sent_at,
        )

        return SendInvoiceEmailResponse(
            id=created.id,
            status=created.status.value,
            subject=created.subject,
            sent_at=created.sent_at,
            error_message=created.error_message,
        )
