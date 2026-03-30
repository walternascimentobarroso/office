"""Monthly workflow business logic."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.monthly_workflow import (
    MonthlyWorkflowInstance,
    MonthlyWorkflowTask,
    WorkflowRecurrence,
    WorkflowTaskTemplate,
)
from app.repositories.monthly_workflow_instance import MonthlyWorkflowInstanceRepository
from app.repositories.monthly_workflow_task import MonthlyWorkflowTaskRepository
from app.repositories.workflow_task_template import WorkflowTaskTemplateRepository


def _template_applies(template: WorkflowTaskTemplate, year: int, month: int) -> bool:
    if template.recurrence == WorkflowRecurrence.MONTHLY:
        return True
    if template.recurrence == WorkflowRecurrence.QUARTERLY:
        return month in (1, 4, 7, 10)
    if template.recurrence == WorkflowRecurrence.YEARLY:
        return template.anchor_month is not None and month == template.anchor_month
    if template.recurrence == WorkflowRecurrence.ONE_TIME:
        return (
            template.anchor_year is not None
            and template.anchor_month is not None
            and year == template.anchor_year
            and month == template.anchor_month
        )
    return False


def _sort_templates(templates: list[WorkflowTaskTemplate]) -> list[WorkflowTaskTemplate]:
    return sorted(
        templates,
        key=lambda t: (
            t.due_day,
            t.sort_order if t.sort_order is not None else 10_000_000,
            t.title,
        ),
    )


class MonthlyWorkflowService:
    """Orchestrates monthly workflow instances and tasks."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.templates = WorkflowTaskTemplateRepository(session)
        self.instances = MonthlyWorkflowInstanceRepository(session)
        self.tasks = MonthlyWorkflowTaskRepository(session)

    async def get_or_create_instance(
        self,
        organization_id: UUID,
        year: int,
        month: int,
    ) -> tuple[MonthlyWorkflowInstance, list[MonthlyWorkflowTask]]:
        existing = await self.instances.get_by_month(organization_id, year, month)
        if existing is not None:
            task_rows = await self.tasks.list_by_instance(organization_id, existing.id)
            return existing, list(task_rows)

        instance = MonthlyWorkflowInstance(
            organization_id=organization_id,
            year=year,
            month=month,
        )
        created = await self.instances.add(instance)
        await self.generate_tasks_for_month(created)
        await self.session.commit()
        await self.session.refresh(created)
        task_rows = await self.tasks.list_by_instance(organization_id, created.id)
        return created, list(task_rows)

    async def generate_tasks_for_month(self, instance: MonthlyWorkflowInstance) -> None:
        template_rows = await self.templates.list_for_organization(
            instance.organization_id,
            active_only=True,
        )
        applicable = [t for t in template_rows if _template_applies(t, instance.year, instance.month)]
        ordered = _sort_templates(applicable)
        for position, template in enumerate(ordered):
            task = MonthlyWorkflowTask(
                organization_id=instance.organization_id,
                instance_id=instance.id,
                template_id=template.id,
                title=template.title,
                category=template.category,
                due_day=template.due_day,
                position=position,
            )
            self.session.add(task)
        await self.session.flush()

    async def update_task_completion(
        self,
        task_id: UUID,
        organization_id: UUID,
        year: int,
        month: int,
        is_completed: bool,
    ) -> MonthlyWorkflowTask:
        task = await self.tasks.get_by_id(organization_id, task_id)
        if task is None:
            msg = "Task not found."
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg)

        instance = await self.instances.get_by_id(organization_id, task.instance_id)
        if instance is None or instance.year != year or instance.month != month:
            msg = "Task not found."
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg)

        task.is_completed = is_completed
        task.completed_at = datetime.now(UTC) if is_completed else None
        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def reset_month(
        self,
        organization_id: UUID,
        year: int,
        month: int,
    ) -> tuple[MonthlyWorkflowInstance, list[MonthlyWorkflowTask]]:
        instance = await self.instances.get_by_month(organization_id, year, month)
        if instance is None:
            msg = "Monthly workflow instance not found."
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg)

        await self.tasks.delete_by_instance(organization_id, instance.id)
        await self.session.flush()
        await self.generate_tasks_for_month(instance)
        await self.session.commit()
        await self.session.refresh(instance)
        task_rows = await self.tasks.list_by_instance(organization_id, instance.id)
        return instance, list(task_rows)

    async def get_instance_for_month_or_404(
        self,
        organization_id: UUID,
        year: int,
        month: int,
    ) -> MonthlyWorkflowInstance:
        instance = await self.instances.get_by_month(organization_id, year, month)
        if instance is None:
            msg = "Monthly workflow instance not found."
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg)
        return instance
