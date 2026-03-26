"""drop reports unique constraint

Revision ID: 20260326_0004
Revises: 20260326_0003
Create Date: 2026-03-26 00:40:00.000000
"""

from __future__ import annotations

from alembic import op

revision = "20260326_0004"
down_revision = "20260326_0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint("uq_reports_employee_month_year_type", "reports", type_="unique")


def downgrade() -> None:
    op.create_unique_constraint(
        "uq_reports_employee_month_year_type",
        "reports",
        ["employee_id", "month", "year", "report_type"],
    )
