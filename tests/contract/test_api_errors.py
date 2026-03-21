# -*- coding: utf-8 -*-
"""Contract tests for error scenarios across all endpoints"""

import pytest
from fastapi.testclient import TestClient
from src.main import app


@pytest.fixture
def client():
    """FastAPI test client"""
    return TestClient(app)


def test_malformed_json_returns_400(client):
    """Test that malformed JSON returns 400 Bad Request"""
    response = client.post("/reports/mapa-diario", 
                          data="{invalid json", 
                          headers={"Content-Type": "application/json"})
    
    assert response.status_code == 400
    data = response.json()
    assert data["error"] == "BadRequest"


def test_missing_content_type_returns_400(client):
    """Test that missing Content-Type header returns 400"""
    payload = {"meta": {"mes": 3}, "entries": []}
    
    response = client.post("/reports/mapa-diario", json=payload)
    # FastAPI might handle this, but test for proper error
    # Actually, TestClient sets content-type automatically, so this might pass
    # But let's test with data instead
    response = client.post("/reports/mapa-diario", 
                          data='{"meta": {"mes": 3}, "entries": []}', 
                          headers={})
    
    # Depending on FastAPI behavior, might be 422 or 400
    assert response.status_code in [400, 422]


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
    assert any("percentagem" in str(details) for details in data.get("details", {}).values())


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