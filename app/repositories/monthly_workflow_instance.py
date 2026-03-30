"""Monthly workflow instance repository."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.monthly_workflow import MonthlyWorkflowInstance


class MonthlyWorkflowInstanceRepository:
    """Persistence for monthly workflow instances (scoped by organization)."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_month(
        self,
        organization_id: UUID,
        year: int,
        month: int,
    ) -> MonthlyWorkflowInstance | None:
        stmt = select(MonthlyWorkflowInstance).where(
            MonthlyWorkflowInstance.organization_id == organization_id,
            MonthlyWorkflowInstance.year == year,
            MonthlyWorkflowInstance.month == month,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id(
        self,
        organization_id: UUID,
        instance_id: UUID,
        *,
        with_tasks: bool = False,
    ) -> MonthlyWorkflowInstance | None:
        stmt = select(MonthlyWorkflowInstance).where(
            MonthlyWorkflowInstance.organization_id == organization_id,
            MonthlyWorkflowInstance.id == instance_id,
        )
        if with_tasks:
            stmt = stmt.options(selectinload(MonthlyWorkflowInstance.tasks))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def add(self, instance: MonthlyWorkflowInstance) -> MonthlyWorkflowInstance:
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance
