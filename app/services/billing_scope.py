"""Shared billing authorization helpers."""

from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status


def ensure_company_scope(
    payload_company_id: UUID,
    token_company_id: UUID,
    roles: list[str],
) -> None:
    """Ensure the caller may act for the given company (admin or same company)."""

    role_names = {role.lower() for role in roles}
    if "admin" in role_names:
        return
    if payload_company_id != token_company_id:
        msg = "Token does not match requested company scope."
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=msg)
