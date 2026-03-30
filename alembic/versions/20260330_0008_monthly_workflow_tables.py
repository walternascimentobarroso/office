"""monthly workflow tables

Revision ID: 20260330_0008
Revises: 20260327_0007
Create Date: 2026-03-30 12:00:00.000000
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "20260330_0008"
down_revision = "20260327_0007"
branch_labels = None
depends_on = None

_WORKFLOW_RECURRENCE = postgresql.ENUM(
    "monthly",
    "quarterly",
    "yearly",
    "one_time",
    name="workflow_recurrence",
    create_type=True,
)


def upgrade() -> None:
    op.create_table(
        "workflow_task_templates",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("category", sa.String(length=255), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("due_day", sa.SmallInteger(), nullable=False),
        sa.Column(
            "recurrence",
            _WORKFLOW_RECURRENCE,
            nullable=False,
        ),
        sa.Column("anchor_month", sa.SmallInteger(), nullable=True),
        sa.Column("anchor_year", sa.Integer(), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
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
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["companies.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_workflow_task_templates_organization_id",
        "workflow_task_templates",
        ["organization_id"],
        unique=False,
    )

    op.create_table(
        "monthly_workflow_instances",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("year", sa.SmallInteger(), nullable=False),
        sa.Column("month", sa.SmallInteger(), nullable=False),
        sa.Column("frozen_at", sa.DateTime(timezone=True), nullable=True),
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
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["companies.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "organization_id",
            "year",
            "month",
            name="uq_monthly_workflow_instances_org_year_month",
        ),
    )
    op.create_index(
        "ix_monthly_workflow_instances_organization_id",
        "monthly_workflow_instances",
        ["organization_id"],
        unique=False,
    )

    op.create_table(
        "monthly_workflow_tasks",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("instance_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("template_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("category", sa.String(length=255), nullable=False),
        sa.Column("due_day", sa.SmallInteger(), nullable=False),
        sa.Column("is_completed", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("position", sa.Integer(), nullable=False),
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
        sa.ForeignKeyConstraint(
            ["instance_id"],
            ["monthly_workflow_instances.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["companies.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["template_id"],
            ["workflow_task_templates.id"],
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_monthly_workflow_tasks_organization_id",
        "monthly_workflow_tasks",
        ["organization_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_monthly_workflow_tasks_organization_id", table_name="monthly_workflow_tasks")
    op.drop_table("monthly_workflow_tasks")

    op.drop_index(
        "ix_monthly_workflow_instances_organization_id",
        table_name="monthly_workflow_instances",
    )
    op.drop_table("monthly_workflow_instances")

    op.drop_index(
        "ix_workflow_task_templates_organization_id",
        table_name="workflow_task_templates",
    )
    op.drop_table("workflow_task_templates")

    postgresql.ENUM(name="workflow_recurrence").drop(op.get_bind(), checkfirst=True)
