"""add percentage to daily entries

Revision ID: 20260326_0005
Revises: 20260326_0004
Create Date: 2026-03-26 00:55:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "20260326_0005"
down_revision = "20260326_0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "daily_entries",
        sa.Column("percentage", sa.Integer(), nullable=False, server_default="100"),
    )
    op.create_check_constraint(
        "ck_daily_entries_percentage_range",
        "daily_entries",
        "percentage >= 0 AND percentage <= 100",
    )


def downgrade() -> None:
    op.drop_constraint("ck_daily_entries_percentage_range", "daily_entries", type_="check")
    op.drop_column("daily_entries", "percentage")
