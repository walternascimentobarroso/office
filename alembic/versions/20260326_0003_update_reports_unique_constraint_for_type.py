"""update reports unique constraint for report type

Revision ID: 20260326_0003
Revises: 20260326_0002
Create Date: 2026-03-26 00:20:00.000000
"""

from __future__ import annotations

from alembic import op

revision = "20260326_0003"
down_revision = "20260326_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint("uq_reports_employee_month_year", "reports", type_="unique")
    op.create_unique_constraint(
        "uq_reports_employee_month_year_type",
        "reports",
        ["employee_id", "month", "year", "report_type"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_reports_employee_month_year_type", "reports", type_="unique")
    op.create_unique_constraint(
        "uq_reports_employee_month_year",
        "reports",
        ["employee_id", "month", "year"],
    )
