"""Single source of truth for invoice request email subject/body/total."""

from __future__ import annotations

from dataclasses import dataclass

from app.schemas.billing import SendInvoiceEmailRequest


@dataclass(frozen=True)
class InvoiceEmailContent:
    """Generated invoice email template fields."""

    subject: str
    body: str
    total: int


def generate_invoice_email_content(payload: SendInvoiceEmailRequest) -> InvoiceEmailContent:
    """Build subject, body, and total from the same inputs as send/preview."""

    total = payload.daily_rate * payload.working_days
    subject = f"Pedido de emissão de fatura - {payload.month}/{payload.year}"
    body = _build_body(payload=payload, total=total)
    return InvoiceEmailContent(subject=subject, body=body, total=total)


def _build_body(*, payload: SendInvoiceEmailRequest, total: int) -> str:
    m, y = payload.month, payload.year
    return (
        "Olá,\n"
        "\n"
        "Venho por este meio solicitar a emissão da fatura referente ao mês em curso.\n"
        "\n"
        "Dados da empresa cliente para faturação:\n"
        f"Empresa: {payload.client_company_name}\n"
        f"NIPC: {payload.client_company_nipc}\n"
        "\n"
        "Descrição sugerida para a fatura:\n"
        f"Prestação de serviços de desenvolvimento de software referente ao mês de {m}/{y}.\n"
        "\n"
        "No valor faturado incluem-se as ajudas de custo para o mês de referência.\n"
        "\n"
        "Valor acordado:\n"
        f"Valor diário: {payload.daily_rate}€ + IVA\n"
        f"Dias faturáveis no mês: {payload.working_days} dias úteis\n"
        f"Valor total: {total}€ + IVA\n"
        "\n"
        "Fico a aguardar, por favor.\n"
        "\n"
        "Com os melhores cumprimentos,\n"
        "Walter"
    )
