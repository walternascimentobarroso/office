"""Workflow task template CRUD."""

from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.monthly_workflow import WorkflowTaskTemplate
from app.repositories.workflow_task_template import WorkflowTaskTemplateRepository
from app.schemas.monthly_workflow import TemplateCreate, TemplateUpdate


class WorkflowTemplateService:
    """Create and maintain workflow task templates."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.templates = WorkflowTaskTemplateRepository(session)

    async def create(self, organization_id: UUID, payload: TemplateCreate) -> WorkflowTaskTemplate:
        template = WorkflowTaskTemplate(
            organization_id=organization_id,
            category=payload.category,
            title=payload.title,
            due_day=payload.due_day,
            recurrence=payload.recurrence,
            anchor_month=payload.anchor_month,
            anchor_year=payload.anchor_year,
            sort_order=payload.sort_order,
        )
        created = await self.templates.add(template)
        await self.session.commit()
        await self.session.refresh(created)
        return created

    async def list_templates(
        self,
        organization_id: UUID,
        *,
        active_only: bool = True,
    ) -> list[WorkflowTaskTemplate]:
        rows = await self.templates.list_for_organization(
            organization_id,
            active_only=active_only,
        )
        return list(rows)

    async def update(
        self,
        organization_id: UUID,
        template_id: UUID,
        payload: TemplateUpdate,
    ) -> WorkflowTaskTemplate:
        template = await self.templates.get_by_id(organization_id, template_id)
        if template is None:
            msg = "Workflow template not found."
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg)

        data = payload.model_dump(exclude_unset=True)
        for key, value in data.items():
            setattr(template, key, value)
        await self.session.commit()
        await self.session.refresh(template)
        return template

    async def soft_delete(self, organization_id: UUID, template_id: UUID) -> None:
        template = await self.templates.get_by_id(organization_id, template_id)
        if template is None:
            msg = "Workflow template not found."
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg)
        template.is_active = False
        await self.session.commit()
