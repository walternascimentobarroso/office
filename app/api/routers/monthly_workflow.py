"""Monthly workflow and template API routes."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Path, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_user, require_company_access, require_roles
from app.db.session import get_db_session
from app.schemas.monthly_workflow import (
    InstanceResponse,
    MonthlyWorkflowDetailResponse,
    TaskCompletionPatch,
    TaskResponse,
    TemplateCreate,
    TemplateResponse,
    TemplateUpdate,
)
from app.services.monthly_workflow import MonthlyWorkflowService
from app.services.workflow_template import WorkflowTemplateService

monthly_workflow_router = APIRouter(
    prefix="/companies/{company_id}/monthly-workflows",
    tags=["monthly-workflows"],
    dependencies=[Depends(get_current_user), Depends(require_company_access)],
)

workflow_templates_router = APIRouter(
    prefix="/companies/{company_id}/workflow-templates",
    tags=["workflow-templates"],
    dependencies=[Depends(get_current_user), Depends(require_company_access)],
)


@monthly_workflow_router.get(
    "/{year}/{month}",
    response_model=MonthlyWorkflowDetailResponse,
)
async def get_monthly_workflow(
    company_id: UUID,
    year: Annotated[int, Path(ge=2000, le=2100)],
    month: Annotated[int, Path(ge=1, le=12)],
    session: AsyncSession = Depends(get_db_session),
) -> MonthlyWorkflowDetailResponse:
    service = MonthlyWorkflowService(session)
    instance, tasks = await service.get_or_create_instance(
        organization_id=company_id,
        year=year,
        month=month,
    )
    return MonthlyWorkflowDetailResponse(
        instance=InstanceResponse.model_validate(instance),
        tasks=[TaskResponse.model_validate(t) for t in tasks],
    )


@monthly_workflow_router.patch(
    "/{year}/{month}/tasks/{task_id}",
    response_model=TaskResponse,
)
async def patch_task_completion(
    company_id: UUID,
    year: Annotated[int, Path(ge=2000, le=2100)],
    month: Annotated[int, Path(ge=1, le=12)],
    task_id: UUID,
    payload: TaskCompletionPatch,
    session: AsyncSession = Depends(get_db_session),
) -> TaskResponse:
    service = MonthlyWorkflowService(session)
    task = await service.update_task_completion(
        task_id=task_id,
        organization_id=company_id,
        year=year,
        month=month,
        is_completed=payload.is_completed,
    )
    return TaskResponse.model_validate(task)


@monthly_workflow_router.post(
    "/{year}/{month}/reset",
    response_model=MonthlyWorkflowDetailResponse,
    status_code=status.HTTP_200_OK,
)
async def reset_monthly_workflow(
    company_id: UUID,
    year: Annotated[int, Path(ge=2000, le=2100)],
    month: Annotated[int, Path(ge=1, le=12)],
    session: AsyncSession = Depends(get_db_session),
) -> MonthlyWorkflowDetailResponse:
    service = MonthlyWorkflowService(session)
    instance, tasks = await service.reset_month(
        organization_id=company_id,
        year=year,
        month=month,
    )
    return MonthlyWorkflowDetailResponse(
        instance=InstanceResponse.model_validate(instance),
        tasks=[TaskResponse.model_validate(t) for t in tasks],
    )


@workflow_templates_router.post(
    "",
    response_model=TemplateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_workflow_template(
    company_id: UUID,
    payload: TemplateCreate,
    _: None = Depends(require_roles("admin")),
    session: AsyncSession = Depends(get_db_session),
) -> TemplateResponse:
    service = WorkflowTemplateService(session)
    template = await service.create(organization_id=company_id, payload=payload)
    return TemplateResponse.model_validate(template)


@workflow_templates_router.get("", response_model=list[TemplateResponse])
async def list_workflow_templates(
    company_id: UUID,
    include_inactive: bool = Query(default=False),
    session: AsyncSession = Depends(get_db_session),
) -> list[TemplateResponse]:
    service = WorkflowTemplateService(session)
    templates = await service.list_templates(
        organization_id=company_id,
        active_only=not include_inactive,
    )
    return [TemplateResponse.model_validate(t) for t in templates]


@workflow_templates_router.patch("/{template_id}", response_model=TemplateResponse)
async def update_workflow_template(
    company_id: UUID,
    template_id: UUID,
    payload: TemplateUpdate,
    _: None = Depends(require_roles("admin")),
    session: AsyncSession = Depends(get_db_session),
) -> TemplateResponse:
    service = WorkflowTemplateService(session)
    template = await service.update(
        organization_id=company_id,
        template_id=template_id,
        payload=payload,
    )
    return TemplateResponse.model_validate(template)


@workflow_templates_router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workflow_template(
    company_id: UUID,
    template_id: UUID,
    _: None = Depends(require_roles("admin")),
    session: AsyncSession = Depends(get_db_session),
) -> Response:
    service = WorkflowTemplateService(session)
    await service.soft_delete(organization_id=company_id, template_id=template_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
