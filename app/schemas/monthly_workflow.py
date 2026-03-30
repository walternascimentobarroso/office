"""Pydantic schemas for monthly workflow APIs."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.monthly_workflow import WorkflowRecurrence
from app.schemas.common import ORMReadModel


class TemplateCreate(BaseModel):
    """Create workflow task template."""

    category: str = Field(max_length=255)
    title: str
    due_day: int = Field(ge=1, le=31)
    recurrence: WorkflowRecurrence
    anchor_month: int | None = Field(default=None, ge=1, le=12)
    anchor_year: int | None = None
    sort_order: int | None = None


class TemplateUpdate(BaseModel):
    """Partial update for workflow task template."""

    category: str | None = Field(default=None, max_length=255)
    title: str | None = None
    due_day: int | None = Field(default=None, ge=1, le=31)
    recurrence: WorkflowRecurrence | None = None
    anchor_month: int | None = Field(default=None, ge=1, le=12)
    anchor_year: int | None = None
    sort_order: int | None = None
    is_active: bool | None = None


class TemplateResponse(ORMReadModel):
    """Workflow task template response."""

    id: UUID
    organization_id: UUID
    category: str
    title: str
    due_day: int
    recurrence: WorkflowRecurrence
    anchor_month: int | None
    anchor_year: int | None
    sort_order: int | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class InstanceResponse(ORMReadModel):
    """Monthly workflow instance response."""

    id: UUID
    organization_id: UUID
    year: int
    month: int
    frozen_at: datetime | None
    created_at: datetime
    updated_at: datetime


class TaskResponse(ORMReadModel):
    """Monthly workflow task response."""

    id: UUID
    organization_id: UUID
    instance_id: UUID
    template_id: UUID | None
    title: str
    category: str
    due_day: int
    is_completed: bool
    completed_at: datetime | None
    position: int
    created_at: datetime
    updated_at: datetime


class MonthlyWorkflowDetailResponse(BaseModel):
    """Instance with tasks for GET monthly workflow."""

    instance: InstanceResponse
    tasks: list[TaskResponse]


class TaskCompletionPatch(BaseModel):
    """PATCH body for task completion."""

    is_completed: bool
