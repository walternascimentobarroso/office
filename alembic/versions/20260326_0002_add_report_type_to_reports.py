"""add report type to reports

Revision ID: 20260326_0002
Revises: 20260326_0001
Create Date: 2026-03-26 00:10:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "20260326_0002"
down_revision = "20260326_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    report_type = sa.Enum("daily", "mileage", name="report_type")
    report_type.create(op.get_bind(), checkfirst=True)

    op.add_column(
        "reports",
        sa.Column(
            "report_type",
            sa.Enum("daily", "mileage", name="report_type", create_type=False),
            server_default="daily",
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("reports", "report_type")
    sa.Enum(name="report_type").drop(op.get_bind(), checkfirst=True)
