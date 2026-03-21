# -*- coding: utf-8 -*-
"""Integration tests for /health."""

from fastapi.testclient import TestClient

from src.main import app


def test_health_check_success() -> None:
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
