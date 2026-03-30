"""Workflow task template repository."""

from __future__ import annotations

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.monthly_workflow import WorkflowTaskTemplate


class WorkflowTaskTemplateRepository:
    """Persistence for workflow task templates (scoped by organization)."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_for_organization(
        self,
        organization_id: UUID,
        *,
        active_only: bool = True,
    ) -> Sequence[WorkflowTaskTemplate]:
        stmt = select(WorkflowTaskTemplate).where(
            WorkflowTaskTemplate.organization_id == organization_id,
        )
        if active_only:
            stmt = stmt.where(WorkflowTaskTemplate.is_active.is_(True))
        stmt = stmt.order_by(
            WorkflowTaskTemplate.sort_order.asc().nulls_last(),
            WorkflowTaskTemplate.due_day.asc(),
            WorkflowTaskTemplate.title.asc(),
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_id(
        self,
        organization_id: UUID,
        template_id: UUID,
    ) -> WorkflowTaskTemplate | None:
        stmt = select(WorkflowTaskTemplate).where(
            WorkflowTaskTemplate.organization_id == organization_id,
            WorkflowTaskTemplate.id == template_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def add(self, template: WorkflowTaskTemplate) -> WorkflowTaskTemplate:
        self.session.add(template)
        await self.session.flush()
        await self.session.refresh(template)
        return template
