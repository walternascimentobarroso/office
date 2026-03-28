# -*- coding: utf-8 -*-
"""Unit tests for auth primitives."""

from __future__ import annotations

import uuid

import pytest

from app.services.password import PasswordService
from app.services.token import TokenService


def test_password_hash_and_verify_roundtrip() -> None:
    service = PasswordService()
    password_hash = service.hash_password("SuperSafePass123!")
    assert password_hash.startswith("pbkdf2_sha256$")
    assert service.verify_password("SuperSafePass123!", password_hash)
    assert not service.verify_password("wrong-password", password_hash)


def test_token_service_creates_and_decodes_access_token() -> None:
    service = TokenService()
    user_id = uuid.uuid4()
    company_id = uuid.uuid4()
    token, expires_in = service.create_access_token(
        user_id=user_id,
        company_id=company_id,
        roles=["admin", "manager"],
    )
    assert expires_in > 0
    payload = service.decode_token(token)
    assert payload.sub == str(user_id)
    assert payload.company_id == str(company_id)
    assert payload.token_type == "access"
    assert "admin" in payload.roles


def test_token_service_rejects_invalid_token() -> None:
    service = TokenService()
    with pytest.raises(ValueError):
        service.decode_token("invalid.token.value")
