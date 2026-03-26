"""Employee API routes."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.schemas.employee import EmployeeCreate, EmployeeRead, EmployeeUpdate
from app.schemas.pagination import Page
from app.services.employee import EmployeeService

router = APIRouter(prefix="/companies/{company_id}/employees", tags=["employees"])


@router.post("", response_model=EmployeeRead, status_code=status.HTTP_201_CREATED)
async def create_employee(
    company_id: UUID,
    payload: EmployeeCreate,
    session: AsyncSession = Depends(get_db_session),
) -> EmployeeRead:
    service = EmployeeService(session)
    employee = await service.create(company_id=company_id, payload=payload)
    return EmployeeRead.model_validate(employee)


@router.get("/{employee_id}", response_model=EmployeeRead)
async def get_employee(
    company_id: UUID,
    employee_id: UUID,
    session: AsyncSession = Depends(get_db_session),
) -> EmployeeRead:
    service = EmployeeService(session)
    employee = await service.get_in_company(company_id=company_id, employee_id=employee_id)
    return EmployeeRead.model_validate(employee)


@router.get("", response_model=Page[EmployeeRead])
async def list_employees(
    company_id: UUID,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_db_session),
) -> Page[EmployeeRead]:
    service = EmployeeService(session)
    employees, total = await service.list_by_company(
        company_id=company_id,
        limit=limit,
        offset=offset,
    )
    return Page[EmployeeRead](
        items=[EmployeeRead.model_validate(item) for item in employees],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_employee(
    company_id: UUID,
    employee_id: UUID,
    session: AsyncSession = Depends(get_db_session),
) -> Response:
    service = EmployeeService(session)
    await service.soft_delete_in_company(company_id=company_id, employee_id=employee_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.patch("/{employee_id}", response_model=EmployeeRead)
async def update_employee(
    company_id: UUID,
    employee_id: UUID,
    payload: EmployeeUpdate,
    session: AsyncSession = Depends(get_db_session),
) -> EmployeeRead:
    service = EmployeeService(session)
    employee = await service.update(
        company_id=company_id,
        employee_id=employee_id,
        payload=payload,
    )
    return EmployeeRead.model_validate(employee)
