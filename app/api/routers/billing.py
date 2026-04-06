"""Billing API routes."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_token_payload
from app.api.dependencies.email import get_email_sender
from app.db.session import get_db_session
from app.email.protocol import EmailSender
from app.schemas.billing import (
    InvoiceEmailHistoryItem,
    PreviewInvoiceEmailResponse,
    SendInvoiceEmailRequest,
    SendInvoiceEmailResponse,
)
from app.services.send_invoice_email import SendInvoiceEmailService

router = APIRouter(prefix="/billing", tags=["billing"])


@router.post(
    "/preview-invoice-email",
    response_model=PreviewInvoiceEmailResponse,
    status_code=status.HTTP_200_OK,
)
async def preview_invoice_email(
    payload: SendInvoiceEmailRequest,
    token_payload: Annotated[
        tuple[UUID, UUID, list[str]],
        Depends(get_current_token_payload),
    ],
    session: AsyncSession = Depends(get_db_session),
) -> PreviewInvoiceEmailResponse:
    """Preview generated subject, body, and total (no email sent)."""

    _, token_company_id, roles = token_payload
    service = SendInvoiceEmailService(session, None)
    return await service.preview_invoice_email(
        token_company_id=token_company_id,
        roles=roles,
        payload=payload,
    )


@router.post(
    "/send-invoice-email",
    response_model=SendInvoiceEmailResponse,
    status_code=status.HTTP_200_OK,
)
async def send_invoice_email(
    payload: SendInvoiceEmailRequest,
    token_payload: Annotated[
        tuple[UUID, UUID, list[str]],
        Depends(get_current_token_payload),
    ],
    session: AsyncSession = Depends(get_db_session),
    email_sender: EmailSender = Depends(get_email_sender),
) -> SendInvoiceEmailResponse:
    """Generate, send, and log a monthly invoice request email."""

    _, token_company_id, roles = token_payload
    service = SendInvoiceEmailService(session, email_sender)
    return await service.send_invoice_email(
        token_company_id=token_company_id,
        roles=roles,
        payload=payload,
    )


@router.get(
    "/invoice-emails",
    response_model=list[InvoiceEmailHistoryItem],
    status_code=status.HTTP_200_OK,
)
async def list_invoice_emails(
    company_id: Annotated[UUID, Query(description="Company scope for history")],
    token_payload: Annotated[
        tuple[UUID, UUID, list[str]],
        Depends(get_current_token_payload),
    ],
    session: AsyncSession = Depends(get_db_session),
    limit: Annotated[int, Query(ge=1, le=200)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[InvoiceEmailHistoryItem]:
    """List invoice email logs for a company."""

    _, token_company_id, roles = token_payload
    service = SendInvoiceEmailService(session, None)
    return await service.list_invoice_emails(
        token_company_id=token_company_id,
        roles=roles,
        company_id=company_id,
        limit=limit,
        offset=offset,
    )


@router.post(
    "/invoice-emails/{log_id}/resend",
    response_model=SendInvoiceEmailResponse,
    status_code=status.HTTP_200_OK,
)
async def resend_invoice_email(
    log_id: UUID,
    token_payload: Annotated[
        tuple[UUID, UUID, list[str]],
        Depends(get_current_token_payload),
    ],
    session: AsyncSession = Depends(get_db_session),
    email_sender: EmailSender = Depends(get_email_sender),
) -> SendInvoiceEmailResponse:
    """Resend a stored invoice email and create a new log entry."""

    _, token_company_id, roles = token_payload
    service = SendInvoiceEmailService(session, email_sender)
    return await service.resend_invoice_email(
        token_company_id=token_company_id,
        roles=roles,
        log_id=log_id,
    )
