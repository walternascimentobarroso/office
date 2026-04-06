"""Billing / invoice email schemas."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class SendInvoiceEmailRequest(BaseModel):
    """Payload to send or preview a monthly invoice request email."""

    company_id: UUID
    month: int = Field(ge=1, le=12)
    year: int = Field(ge=2000, le=2100)
    to_email: EmailStr
    daily_rate: int = Field(gt=0)
    working_days: int = Field(gt=0)
    client_company_name: str = Field(min_length=1)
    client_company_nipc: str = Field(min_length=1)


class PreviewInvoiceEmailResponse(BaseModel):
    """Preview of generated invoice email (no send)."""

    subject: str
    body: str
    total: int


class SendInvoiceEmailResponse(BaseModel):
    """Result of a send-invoice-email attempt."""

    id: UUID
    status: str
    subject: str
    sent_at: datetime | None = None
    error_message: str | None = None


class InvoiceEmailHistoryItem(BaseModel):
    """Summary row for invoice email history."""

    id: UUID
    month: int
    year: int
    status: str
    to_email: str
    sent_at: datetime | None = None
