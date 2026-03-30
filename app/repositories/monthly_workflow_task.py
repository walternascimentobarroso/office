"""Monthly workflow task repository."""

from __future__ import annotations

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.monthly_workflow import MonthlyWorkflowTask


class MonthlyWorkflowTaskRepository:
    """Persistence for monthly workflow tasks (scoped by organization)."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_by_instance(
        self,
        organization_id: UUID,
        instance_id: UUID,
    ) -> Sequence[MonthlyWorkflowTask]:
        stmt = (
            select(MonthlyWorkflowTask)
            .where(
                MonthlyWorkflowTask.organization_id == organization_id,
                MonthlyWorkflowTask.instance_id == instance_id,
            )
            .order_by(MonthlyWorkflowTask.position.asc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_id(
        self,
        organization_id: UUID,
        task_id: UUID,
    ) -> MonthlyWorkflowTask | None:
        stmt = select(MonthlyWorkflowTask).where(
            MonthlyWorkflowTask.organization_id == organization_id,
            MonthlyWorkflowTask.id == task_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def add(self, task: MonthlyWorkflowTask) -> MonthlyWorkflowTask:
        self.session.add(task)
        await self.session.flush()
        await self.session.refresh(task)
        return task

    async def delete_by_instance(
        self,
        organization_id: UUID,
        instance_id: UUID,
    ) -> None:
        stmt = delete(MonthlyWorkflowTask).where(
            MonthlyWorkflowTask.organization_id == organization_id,
            MonthlyWorkflowTask.instance_id == instance_id,
        )
        await self.session.execute(stmt)
