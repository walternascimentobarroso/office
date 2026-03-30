"""Monthly workflow ORM models (multi-tenant via organization_id)."""

from __future__ import annotations

import enum
import uuid
from datetime import datetime
from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, UUIDPrimaryKeyMixin


class WorkflowRecurrence(str, enum.Enum):
    """Recurrence rule for a workflow task template."""

    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    ONE_TIME = "one_time"


class WorkflowTaskTemplate(UUIDPrimaryKeyMixin, Base):
    """Configurable recurring task template per organization."""

    __tablename__ = "workflow_task_templates"
    __table_args__ = (
        Index("ix_workflow_task_templates_organization_id", "organization_id"),
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
    )
    category: Mapped[str] = mapped_column(String(255), nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    due_day: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    recurrence: Mapped[WorkflowRecurrence] = mapped_column(
        SAEnum(
            WorkflowRecurrence,
            name="workflow_recurrence",
            native_enum=True,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        nullable=False,
    )
    anchor_month: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    anchor_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sort_order: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


class MonthlyWorkflowInstance(UUIDPrimaryKeyMixin, Base):
    """One workflow instance per organization and calendar month."""

    __tablename__ = "monthly_workflow_instances"
    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "year",
            "month",
            name="uq_monthly_workflow_instances_org_year_month",
        ),
        Index("ix_monthly_workflow_instances_organization_id", "organization_id"),
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
    )
    year: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    month: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    frozen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    tasks: Mapped[list["MonthlyWorkflowTask"]] = relationship(
        back_populates="instance",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="MonthlyWorkflowTask.position",
    )


class MonthlyWorkflowTask(UUIDPrimaryKeyMixin, Base):
    """Snapshot task row for a monthly workflow instance."""

    __tablename__ = "monthly_workflow_tasks"
    __table_args__ = (Index("ix_monthly_workflow_tasks_organization_id", "organization_id"),)

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
    )
    instance_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("monthly_workflow_instances.id", ondelete="CASCADE"),
        nullable=False,
    )
    template_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workflow_task_templates.id", ondelete="SET NULL"),
        nullable=True,
    )
    title: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(255), nullable=False)
    due_day: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    is_completed: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    instance: Mapped["MonthlyWorkflowInstance"] = relationship(back_populates="tasks")
