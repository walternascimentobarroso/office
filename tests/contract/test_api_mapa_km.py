# -*- coding: utf-8 -*-
"""Contract tests for POST /reports/mapa-km endpoint"""

import pytest
from fastapi.testclient import TestClient
from src.main import app


@pytest.fixture
def client():
    """FastAPI test client"""
    return TestClient(app)


def test_mapa_km_valid_request_returns_excel(client):
    """Test that valid request returns Excel file"""
    payload = {
        "meta": {
            "empresa": "Test Company",
            "nif": "123456789",
            "mes": "Março"
        },
        "entries": [
            {
                "day": 1,
                "description": "Test activity",
                "location": "Test location",
                "start_time": "09:00",
                "end_time": "10:00",
                "percentagem": 100
            }
        ],
        "vehicle": {
            "modelo": "Test Model",
            "matricula": "AA-12-BB",
            "kms": 1000
        },
        "holidays": [5, 25]
    }
    
    response = client.post("/reports/mapa-km", json=payload)
    
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    assert "attachment; filename=" in response.headers.get("content-disposition", "")
    assert b"PK" in response.content  # XLSX files start with PK (ZIP header)


def test_mapa_km_invalid_month_returns_422(client):
    """Test that invalid month returns validation error"""
    payload = {
        "meta": {
            "mes": "InvalidMonth"  # Invalid month name
        },
        "entries": [],
        "vehicle": {},
        "holidays": []
    }
    
    response = client.post("/reports/mapa-km", json=payload)
    
    assert response.status_code == 422
    data = response.json()
    assert data["error"] == "ValidationError"
    assert any(
        "mes" in str(err.get("loc", ()))
        for err in data["details"]
    )


def test_mapa_km_missing_required_fields_returns_422(client):
    """Test that missing required fields return validation error"""
    payload = {
        "entries": []
    }  # Missing meta.mes
    
    response = client.post("/reports/mapa-km", json=payload)
    
    assert response.status_code == 422
    data = response.json()
    assert data["error"] == "ValidationError"
    assert any(
        "meta" in str(err.get("loc", ()))
        for err in data["details"]
    )


def test_mapa_km_invalid_holidays_filtered_like_mapa_diario(client):
    """Invalid holiday values are dropped (same as legacy /generate-excel)."""

    payload = {
        "meta": {
            "mes": "Março"
        },
        "entries": [],
        "vehicle": {},
        "holidays": [32, "invalid", 5],
    }

    response = client.post("/reports/mapa-km", json=payload)

    assert response.status_code == 200