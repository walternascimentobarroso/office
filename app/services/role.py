"""Role service."""

from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.role import Role
from app.repositories.role import RoleRepository
from app.schemas.role import RoleCreate, RoleUpdate
from app.utils.soft_delete import mark_deleted


class RoleService:
    """Business operations for roles."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = RoleRepository(session)

    async def create(self, payload: RoleCreate) -> Role:
        if await self.repository.name_exists(payload.name):
            msg = "Role name already exists."
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=msg)

        role = Role(name=payload.name, description=payload.description)
        created = await self.repository.add(role)
        await self.session.commit()
        return created

    async def get(self, role_id: UUID) -> Role:
        role = await self.repository.get_by_id(role_id)
        if role is None:
            msg = "Role not found."
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg)
        return role

    async def list(self, limit: int = 50, offset: int = 0) -> tuple[list[Role], int]:
        roles = await self.repository.list(limit=limit, offset=offset)
        total = await self.repository.count()
        return list(roles), total

    async def update(self, role_id: UUID, payload: RoleUpdate) -> Role:
        role = await self.get(role_id)
        update_data = payload.model_dump(exclude_unset=True)
        new_name = update_data.get("name")

        if new_name and new_name != role.name:
            if await self.repository.name_exists(new_name):
                msg = "Role name already exists."
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=msg)

        for field, value in update_data.items():
            setattr(role, field, value)
        await self.session.commit()
        await self.session.refresh(role)
        return role

    async def soft_delete(self, role_id: UUID) -> None:
        role = await self.get(role_id)
        mark_deleted(role)
        await self.session.commit()
