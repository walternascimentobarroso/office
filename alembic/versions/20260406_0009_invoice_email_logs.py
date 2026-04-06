"""invoice email logs

Revision ID: 20260406_0009
Revises: 20260330_0008
Create Date: 2026-04-06 00:00:00.000000
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "20260406_0009"
down_revision = "20260330_0008"
branch_labels = None
depends_on = None

_INVOICE_EMAIL_STATUS = postgresql.ENUM(
    "sent",
    "failed",
    name="invoice_email_status",
    create_type=True,
)


def upgrade() -> None:
    _INVOICE_EMAIL_STATUS.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "invoice_email_logs",
        sa.Column("company_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("month", sa.Integer(), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("to_email", sa.Text(), nullable=False),
        sa.Column("subject", sa.Text(), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column(
            "status",
            postgresql.ENUM(
                "sent",
                "failed",
                name="invoice_email_status",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("month >= 1 AND month <= 12", name="ck_invoice_email_logs_month_range"),
        sa.CheckConstraint("year >= 2000", name="ck_invoice_email_logs_year_min"),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_invoice_email_logs_company_id_active",
        "invoice_email_logs",
        ["company_id"],
        unique=False,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )


def downgrade() -> None:
    op.drop_index("ix_invoice_email_logs_company_id_active", table_name="invoice_email_logs")
    op.drop_table("invoice_email_logs")
    _INVOICE_EMAIL_STATUS.drop(op.get_bind(), checkfirst=True)
