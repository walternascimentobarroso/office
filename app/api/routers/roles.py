"""Role API routes."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.schemas.pagination import Page
from app.schemas.role import RoleCreate, RoleRead, RoleUpdate
from app.services.role import RoleService

router = APIRouter(prefix="/roles", tags=["roles"])


@router.post("", response_model=RoleRead, status_code=status.HTTP_201_CREATED)
async def create_role(
    payload: RoleCreate,
    session: AsyncSession = Depends(get_db_session),
) -> RoleRead:
    service = RoleService(session)
    role = await service.create(payload)
    return RoleRead.model_validate(role)


@router.get("/{role_id}", response_model=RoleRead)
async def get_role(
    role_id: UUID,
    session: AsyncSession = Depends(get_db_session),
) -> RoleRead:
    service = RoleService(session)
    role = await service.get(role_id)
    return RoleRead.model_validate(role)


@router.get("", response_model=Page[RoleRead])
async def list_roles(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_db_session),
) -> Page[RoleRead]:
    service = RoleService(session)
    roles, total = await service.list(limit=limit, offset=offset)
    return Page[RoleRead](
        items=[RoleRead.model_validate(item) for item in roles],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.patch("/{role_id}", response_model=RoleRead)
async def update_role(
    role_id: UUID,
    payload: RoleUpdate,
    session: AsyncSession = Depends(get_db_session),
) -> RoleRead:
    service = RoleService(session)
    role = await service.update(role_id=role_id, payload=payload)
    return RoleRead.model_validate(role)


@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(
    role_id: UUID,
    session: AsyncSession = Depends(get_db_session),
) -> Response:
    service = RoleService(session)
    await service.soft_delete(role_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
