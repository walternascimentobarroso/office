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
        "/reports/mapa-diario",
        data="{invalid json",
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 422


def test_missing_content_type_still_parses_json_body(client):
    """Starlette may infer JSON from raw body even without Content-Type."""

    response = client.post(
        "/reports/mapa-diario",
        content='{"meta": {"mes": 3}, "entries": []}',
        headers={},
    )

    assert response.status_code == 200


def test_invalid_percentagem_range_returns_422(client):
    """Test that percentagem outside 0-100 returns validation error"""
    payload = {
        "meta": {"mes": 3},
        "entries": [
            {
                "day": 1,
                "percentagem": 150  # Invalid percentage
            }
        ],
        "holidays": []
    }
    
    response = client.post("/reports/mapa-diario", json=payload)
    
    assert response.status_code == 422
    data = response.json()
    assert data["error"] == "ValidationError"
    assert any(
        "percentagem" in str(err.get("loc", ()))
        for err in data.get("details", [])
    )


def test_empty_entries_list_allowed(client):
    """Test that empty entries list is allowed"""
    payload = {
        "meta": {"mes": 3},
        "entries": [],  # Empty list allowed
        "holidays": []
    }
    
    response = client.post("/reports/mapa-diario", json=payload)
    
    assert response.status_code == 200


def test_missing_optional_fields_allowed(client):
    """Test that missing optional fields in entries are allowed"""
    payload = {
        "meta": {"mes": 3},
        "entries": [
            {
                "day": 1
                # All other fields optional
            }
        ],
        "holidays": []
    }
    
    response = client.post("/reports/mapa-diario", json=payload)
    
    assert response.status_code == 200


def test_invalid_endpoint_returns_404(client):
    """Test that invalid endpoint returns 404"""
    payload = {"meta": {"mes": 3}, "entries": []}
    
    response = client.post("/reports/invalid-report", json=payload)
    
    assert response.status_code == 404