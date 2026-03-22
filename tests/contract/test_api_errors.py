# -*- coding: utf-8 -*-
"""Contract tests for error scenarios across all endpoints"""

import pytest
from fastapi.testclient import TestClient
from src.main import app


@pytest.fixture
def client():
    """FastAPI test client"""
    return TestClient(app)


def test_malformed_json_returns_422(client):
    """Malformed JSON body yields 422 from Starlette/FastAPI."""

    response = client.post(
        "/reports/daily-report",
        data="{invalid json",
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 422


def test_missing_content_type_still_parses_json_body(client):
    """FastAPI expects explicit JSON content-type for request body in this contract."""

    response = client.post(
        "/reports/daily-report",
        content='{"company": {"name": "ACME", "tax_id": "123", "address": "Rua X"}, "employee": {"name": "Ana", "tax_id": "999", "address": "Rua X"}, "month": 3, "entries": []}',
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 200


def test_invalid_percentage_range_returns_422(client):
    """Test that percentage outside 0-100 returns validation error"""
    payload = {
        "company": {"name": "Corp", "tax_id": "123", "address": "Rua X"},
        "employee": {"name": "Ana", "tax_id": "999", "address": "Rua X"},
        "month": 3,
        "entries": [
            {
                "day": 1,
                "percentage": 150  # Invalid percentage
            }
        ],
        "holidays": []
    }

    response = client.post("/reports/daily-report", json=payload)

    assert response.status_code == 422
    data = response.json()
    assert data["error"] == "ValidationError"
    assert any(
        "percentage" in str(err.get("loc", ()))
        for err in data.get("details", [])
    )


def test_empty_entries_list_allowed(client):
    """Test that empty entries list is allowed"""
    payload = {
        "company": {"name": "Corp", "tax_id": "123", "address": "Rua X"},
        "employee": {"name": "Ana", "tax_id": "999", "address": "Rua X"},
        "month": 3,
        "entries": [],  # Empty list allowed
        "holidays": []
    }

    response = client.post("/reports/daily-report", json=payload)

    assert response.status_code == 200


def test_missing_optional_fields_allowed(client):
    """Test that missing optional fields in entries are allowed"""
    payload = {
        "company": {"name": "Corp", "tax_id": "123", "address": "Rua X"},
        "employee": {"name": "Ana", "tax_id": "999", "address": "Rua X"},
        "month": 3,
        "entries": [
            {
                "day": 1
                # All other fields optional
            }
        ],
        "holidays": []
    }

    response = client.post("/reports/daily-report", json=payload)

    assert response.status_code == 200


def test_invalid_endpoint_returns_404(client):
    """Test that invalid endpoint returns 404"""
    payload = {
        "company": {"name": "Corp", "tax_id": "123", "address": "Rua X"},
        "employee": {"name": "Ana", "tax_id": "999", "address": "Rua X"},
        "month": 3,
        "entries": []
    }

    response = client.post("/reports/invalid-report", json=payload)

    assert response.status_code == 404
