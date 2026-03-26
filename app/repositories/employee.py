"""Employee repository."""

from __future__ import annotations

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import func, select

from app.models.employee import Employee
from app.repositories.base import BaseRepository


class EmployeeRepository(BaseRepository[Employee]):
    """Persistence operations for employees."""

    model = Employee

    async def get_by_company_and_tax_id(self, company_id: UUID, tax_id: str) -> Employee | None:
        stmt = self._active_stmt().where(
            Employee.company_id == company_id,
            Employee.tax_id == tax_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_company(
        self,
        company_id: UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> Sequence[Employee]:
        stmt = (
            self._active_stmt()
            .where(Employee.company_id == company_id)
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count_by_company(self, company_id: UUID) -> int:
        stmt = select(func.count()).select_from(Employee).where(
            Employee.company_id == company_id,
            Employee.deleted_at.is_(None),
        )
        result = await self.session.execute(stmt)
        return int(result.scalar_one())

    async def exists_for_company_tax_id(self, company_id: UUID, tax_id: str) -> bool:
        stmt = select(Employee.id).where(
            Employee.company_id == company_id,
            Employee.tax_id == tax_id,
            Employee.deleted_at.is_(None),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None
