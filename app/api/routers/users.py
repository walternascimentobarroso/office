"""User API routes."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.models.role import Role
from app.models.user import User
from app.schemas.pagination import Page
from app.schemas.user import UserCreate, UserRead, UserRoleRead, UserUpdate
from app.services.user import UserService

router = APIRouter(prefix="/companies/{company_id}/users", tags=["users"])


def _to_user_read(user: User, roles: list[Role]) -> UserRead:
    return UserRead(
        id=user.id,
        company_id=user.company_id,
        name=user.name,
        email=user.email,
        created_at=user.created_at,
        updated_at=user.updated_at,
        deleted_at=user.deleted_at,
        roles=[
            UserRoleRead(id=role.id, name=role.name, description=role.description)
            for role in roles
        ],
    )


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(
    company_id: UUID,
    payload: UserCreate,
    session: AsyncSession = Depends(get_db_session),
) -> UserRead:
    service = UserService(session)
    user = await service.create(company_id=company_id, payload=payload)
    roles = await service.list_roles_for_user(user.id)
    return _to_user_read(user, roles)


@router.get("/{user_id}", response_model=UserRead)
async def get_user(
    company_id: UUID,
    user_id: UUID,
    session: AsyncSession = Depends(get_db_session),
) -> UserRead:
    service = UserService(session)
    user = await service.get_in_company(company_id=company_id, user_id=user_id)
    roles = await service.list_roles_for_user(user.id)
    return _to_user_read(user, roles)


@router.get("", response_model=Page[UserRead])
async def list_users(
    company_id: UUID,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_db_session),
) -> Page[UserRead]:
    service = UserService(session)
    users, total = await service.list_by_company(
        company_id=company_id,
        limit=limit,
        offset=offset,
    )
    items: list[UserRead] = []
    for user in users:
        roles = await service.list_roles_for_user(user.id)
        items.append(_to_user_read(user, roles))
    return Page[UserRead](items=items, total=total, limit=limit, offset=offset)


@router.patch("/{user_id}", response_model=UserRead)
async def update_user(
    company_id: UUID,
    user_id: UUID,
    payload: UserUpdate,
    session: AsyncSession = Depends(get_db_session),
) -> UserRead:
    service = UserService(session)
    user = await service.update(company_id=company_id, user_id=user_id, payload=payload)
    roles = await service.list_roles_for_user(user.id)
    return _to_user_read(user, roles)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    company_id: UUID,
    user_id: UUID,
    session: AsyncSession = Depends(get_db_session),
) -> Response:
    service = UserService(session)
    await service.soft_delete_in_company(company_id=company_id, user_id=user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
