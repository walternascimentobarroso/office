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
        "company": {
            "name": "Test Company",
            "tax_id": "123456789",
            "address": "Rua Um, 1",
        },
        "employee": {
            "name": "João Costa",
            "address": "Av. Central 50",
            "tax_id": "222333444",
            "vehicle_plate": "34-XY-56",
        },
        "month": 3,
        "year": 2025,
        "entries": [
            {
                "day": 1,
                "origem": "Braga",
                "destino": "Lisboa",
                "description": "Deslocação",
                "n_kms": "363,000",
            }
        ],
        "holidays": [5, 25],
    }

    response = client.post("/reports/mapa-km", json=payload)

    assert response.status_code == 200
    assert response.headers["content-type"] == (
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    assert "attachment; filename=" in response.headers.get("content-disposition", "")
    assert b"PK" in response.content


def test_mapa_km_invalid_month_returns_422(client):
    """Test that invalid month returns validation error"""
    payload = {
        "company": {
            "name": "Test Company",
            "tax_id": "123456789",
            "address": "Rua Um, 1",
        },
        "employee": {
            "name": "João Costa",
            "address": "Av. Central 50",
            "tax_id": "222333444",
        },
        "month": 13,
        "entries": [],
        "holidays": [],
    }

    response = client.post("/reports/mapa-km", json=payload)

    assert response.status_code == 422
    data = response.json()
    assert data["error"] == "ValidationError"
    assert any(
        "month" in str(err.get("loc", ()))
        for err in data["details"]
    )


def test_mapa_km_missing_required_fields_returns_422(client):
    """Test that missing required fields return validation error"""
    payload = {
        "company": {
            "name": "Test Company",
            "tax_id": "123456789",
            "address": "Rua Um, 1",
        },
        "employee": {
            "name": "João Costa",
            "address": "Av. Central 50",
            "tax_id": "222333444",
        },
        "entries": [],
    }

    response = client.post("/reports/mapa-km", json=payload)

    assert response.status_code == 422
    data = response.json()
    assert data["error"] == "ValidationError"
    assert any(
        "month" in str(err.get("loc", ()))
        for err in data["details"]
    )


def test_mapa_km_invalid_holidays_filtered_like_mapa_diario(client):
    """Invalid holiday values are dropped (same as legacy /generate-excel)."""

    payload = {
        "company": {
            "name": "Test Company",
            "tax_id": "123456789",
            "address": "Rua Um, 1",
        },
        "employee": {
            "name": "João Costa",
            "address": "Av. Central 50",
            "tax_id": "222333444",
        },
        "month": 3,
        "entries": [],
        "holidays": [32, "invalid", 5],
    }

    response = client.post("/reports/mapa-km", json=payload)

    assert response.status_code == 200
