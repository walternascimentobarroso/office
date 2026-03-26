"""Employee service."""

from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.company import CompanyRepository
from app.repositories.employee import EmployeeRepository
from app.schemas.employee import EmployeeCreate, EmployeeUpdate
from app.utils.soft_delete import mark_deleted


class EmployeeService:
    """Business operations for employees."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.company_repository = CompanyRepository(session)
        self.employee_repository = EmployeeRepository(session)

    async def create(self, company_id: UUID, payload: EmployeeCreate):
        company = await self.company_repository.get_by_id(company_id)
        if company is None:
            msg = "Company not found."
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg)

        duplicate = await self.employee_repository.exists_for_company_tax_id(
            company_id=company_id,
            tax_id=payload.tax_id,
        )
        if duplicate:
            msg = "Employee tax_id already exists for this company."
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=msg)

        employee = self.employee_repository.model(
            company_id=company_id,
            name=payload.name,
            tax_id=payload.tax_id,
            address=payload.address,
            vehicle_plate=payload.vehicle_plate,
        )
        created = await self.employee_repository.add(employee)
        await self.session.commit()
        return created

    async def get(self, employee_id: UUID):
        employee = await self.employee_repository.get_by_id(employee_id)
        if employee is None:
            msg = "Employee not found."
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg)
        return employee

    async def list_by_company(
        self,
        company_id: UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list, int]:
        company = await self.company_repository.get_by_id(company_id)
        if company is None:
            msg = "Company not found."
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg)

        employees = await self.employee_repository.list_by_company(
            company_id=company_id,
            limit=limit,
            offset=offset,
        )
        total = await self.employee_repository.count_by_company(company_id=company_id)
        return list(employees), total

    async def soft_delete(self, employee_id: UUID) -> None:
        employee = await self.get(employee_id)
        mark_deleted(employee)
        await self.session.commit()

    async def get_in_company(self, company_id: UUID, employee_id: UUID):
        employee = await self.get(employee_id)
        if employee.company_id != company_id:
            msg = "Employee not found for this company."
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg)
        return employee

    async def soft_delete_in_company(self, company_id: UUID, employee_id: UUID) -> None:
        employee = await self.get_in_company(company_id=company_id, employee_id=employee_id)
        mark_deleted(employee)
        await self.session.commit()

    async def update(self, company_id: UUID, employee_id: UUID, payload: EmployeeUpdate):
        employee = await self.get_in_company(company_id=company_id, employee_id=employee_id)
        update_data = payload.model_dump(exclude_unset=True)

        target_tax_id = update_data.get("tax_id", employee.tax_id)
        if target_tax_id != employee.tax_id:
            duplicate = await self.employee_repository.exists_for_company_tax_id(
                company_id=company_id,
                tax_id=target_tax_id,
            )
            if duplicate:
                msg = "Employee tax_id already exists for this company."
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=msg)

        for field, value in update_data.items():
            setattr(employee, field, value)
        await self.session.commit()
        await self.session.refresh(employee)
        return employee
