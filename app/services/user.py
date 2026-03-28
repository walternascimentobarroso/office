"""User service."""

from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.role import Role
from app.models.user import User
from app.models.user_role import UserRole
from app.repositories.company import CompanyRepository
from app.repositories.role import RoleRepository
from app.repositories.user import UserRepository
from app.repositories.user_role import UserRoleRepository
from app.schemas.user import UserCreate, UserUpdate
from app.services.password import PasswordService
from app.utils.soft_delete import mark_deleted, restore_deleted


class UserService:
    """Business operations for users and their role assignments."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.company_repository = CompanyRepository(session)
        self.user_repository = UserRepository(session)
        self.role_repository = RoleRepository(session)
        self.user_role_repository = UserRoleRepository(session)
        self.password_service = PasswordService()

    async def create(self, company_id: UUID, payload: UserCreate) -> User:
        await self._ensure_company_exists(company_id)
        await self._ensure_unique_email(company_id=company_id, email=payload.email)
        role_ids = set(payload.role_ids)
        await self._validate_role_ids(role_ids)

        password_hash = (
            self.password_service.hash_password(payload.password) if payload.password is not None else None
        )
        user = User(
            company_id=company_id,
            name=payload.name,
            email=payload.email,
            password_hash=password_hash,
        )
        created = await self.user_repository.add(user)
        await self._sync_roles(user_id=created.id, target_role_ids=role_ids)
        await self.session.commit()
        await self.session.refresh(created)
        return created

    async def get_in_company(self, company_id: UUID, user_id: UUID) -> User:
        user = await self.user_repository.get_by_id(user_id)
        if user is None or user.company_id != company_id:
            msg = "User not found for this company."
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg)
        return user

    async def list_by_company(
        self,
        company_id: UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[User], int]:
        await self._ensure_company_exists(company_id)
        users = await self.user_repository.list_by_company(
            company_id=company_id,
            limit=limit,
            offset=offset,
        )
        total = await self.user_repository.count_by_company(company_id=company_id)
        return list(users), total

    async def update(self, company_id: UUID, user_id: UUID, payload: UserUpdate) -> User:
        user = await self.get_in_company(company_id=company_id, user_id=user_id)
        update_data = payload.model_dump(exclude_unset=True)

        new_email = update_data.get("email")
        if new_email and new_email != user.email:
            await self._ensure_unique_email(company_id=company_id, email=new_email)

        role_ids_input = update_data.pop("role_ids", None)
        password = update_data.pop("password", None)
        if password is not None:
            user.password_hash = self.password_service.hash_password(password)
        for field, value in update_data.items():
            setattr(user, field, value)

        if role_ids_input is not None:
            role_ids = set(role_ids_input)
            await self._validate_role_ids(role_ids)
            await self._sync_roles(user_id=user.id, target_role_ids=role_ids)

        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def soft_delete_in_company(self, company_id: UUID, user_id: UUID) -> None:
        user = await self.get_in_company(company_id=company_id, user_id=user_id)
        mark_deleted(user)
        active_links = await self.user_role_repository.list_active_links(user.id)
        for link in active_links:
            mark_deleted(link)
        await self.session.commit()

    async def list_roles_for_user(self, user_id: UUID) -> list[Role]:
        roles = await self.user_role_repository.list_active_roles_for_user(user_id)
        return list(roles)

    async def _ensure_company_exists(self, company_id: UUID) -> None:
        company = await self.company_repository.get_by_id(company_id)
        if company is None:
            msg = "Company not found."
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg)

    async def _ensure_unique_email(self, company_id: UUID, email: str) -> None:
        if await self.user_repository.exists_for_company_email(company_id=company_id, email=email):
            msg = "User email already exists for this company."
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=msg)

    async def _validate_role_ids(self, role_ids: set[UUID]) -> None:
        if not role_ids:
            return
        active_roles = await self.role_repository.list_by_ids_active(role_ids)
        if len(active_roles) != len(role_ids):
            msg = "One or more roles were not found."
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg)

    async def _sync_roles(self, user_id: UUID, target_role_ids: set[UUID]) -> None:
        active_links = await self.user_role_repository.list_active_links(user_id)
        active_by_role = {link.role_id: link for link in active_links}
        active_role_ids = set(active_by_role.keys())

        role_ids_to_remove = active_role_ids - target_role_ids
        role_ids_to_add = target_role_ids - active_role_ids

        for role_id in role_ids_to_remove:
            mark_deleted(active_by_role[role_id])

        for role_id in role_ids_to_add:
            existing_link = await self.user_role_repository.get_any_link(user_id=user_id, role_id=role_id)
            if existing_link is None:
                await self.user_role_repository.add(UserRole(user_id=user_id, role_id=role_id))
                continue
            restore_deleted(existing_link)
