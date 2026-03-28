# -*- coding: utf-8 -*-
"""Integration tests for auth guards on protected routes."""

from fastapi.testclient import TestClient

from src.main import app


def test_protected_routes_require_authorization_header() -> None:
    client = TestClient(app)
    response = client.get("/companies")
    assert response.status_code == 401
    assert response.json()["message"] == "Missing Authorization header."
