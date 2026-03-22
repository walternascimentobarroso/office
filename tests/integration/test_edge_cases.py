# -*- coding: utf-8 -*-
"""Integration tests for edge cases in report generation"""

import pytest
from io import BytesIO
from openpyxl import load_workbook
from fastapi.testclient import TestClient
from src.main import app


@pytest.fixture
def client():
    """FastAPI test client"""
    return TestClient(app)


def test_large_number_of_entries(client):
    """Test handling of large number of entries (performance and correctness)"""
    entries = []
    for i in range(31):  # Full month
        entries.append({
            "day": i + 1,
            "description": f"Activity {i+1}",
            "percentage": 100
        })

    payload = {
        "company": {
            "name": "Test Company Ltd",
            "tax_id": "123456789",
            "address": "1 Test Ave",
        },
        "employee": {
            "name": "Test Employee",
            "address": "Test Address",
            "tax_id": "987654321",
        },
        "month": 3,
        "entries": entries,
        "holidays": [],
    }

    response = client.post("/reports/daily-report", json=payload)
    assert response.status_code == 200

    wb = load_workbook(BytesIO(response.content))
    _ = wb.active


def test_special_characters_in_text_fields(client):
    """Test that special characters in text fields are handled correctly"""
    payload = {
        "company": {
            "name": "Empresa Têst & Cía.",
            "tax_id": "123456789",
            "address": "Av. Teste 99",
        },
        "employee": {
            "name": "José María González",
            "address": "Rua João Paulo II, nº 123",
            "tax_id": "987654321",
        },
        "month": 3,
        "entries": [
            {
                "day": 1,
                "description": "Meeting with João & Maria (coffee)",
                "location": "São Paulo - SP"
            }
        ],
        "holidays": []
    }

    response = client.post("/reports/daily-report", json=payload)
    assert response.status_code == 200

    wb = load_workbook(BytesIO(response.content))
    _ = wb.active


def test_empty_strings_vs_missing_fields(client):
    """Test difference between empty strings and missing fields"""
    payload = {
        "company": {
            "name": "Test Company Ltd",
            "tax_id": "123456789",
            "address": "1 Test Ave",
        },
        "employee": {
            "name": "Test Employee",
            "address": "Test Address",
            "tax_id": "987654321",
        },
        "month": 3,
        "entries": [
            {
                "day": 1,
                "description": "",  # Empty string
                "location": None,   # Missing field
                "percentage": 0    # Zero value
            }
        ],
        "holidays": []
    }

    response = client.post("/reports/daily-report", json=payload)
    assert response.status_code == 200

    wb = load_workbook(BytesIO(response.content))
    _ = wb.active


def test_holiday_filtering_invalid_values(client):
    """Test that invalid holiday values are filtered out"""
    payload = {
        "company": {
            "name": "Test Company Ltd",
            "tax_id": "123456789",
            "address": "1 Test Ave",
        },
        "employee": {
            "name": "Test Employee",
            "address": "Test Address",
            "tax_id": "987654321",
        },
        "month": 3,
        "entries": [],
        "holidays": [5, 32, "invalid", -1, 0, 15]  # Mix of valid and invalid
    }

    response = client.post("/reports/daily-report", json=payload)
    assert response.status_code == 200

    wb = load_workbook(BytesIO(response.content))
    _ = wb.active


def test_month_boundary_cases(client):
    """Test month boundary values"""
    payload_jan = {
        "company": {
            "name": "Test Company Ltd",
            "tax_id": "123456789",
            "address": "1 Test Ave",
        },
        "employee": {
            "name": "Test Employee",
            "address": "Test Address",
            "tax_id": "987654321",
        },
        "month": 1,
        "entries": [],
        "holidays": [],
    }
    response = client.post("/reports/daily-report", json=payload_jan)
    assert response.status_code == 200

    payload_dec = {
        "company": {
            "name": "Test Company Ltd",
            "tax_id": "123456789",
            "address": "1 Test Ave",
        },
        "employee": {
            "name": "Test Employee",
            "address": "Test Address",
            "tax_id": "987654321",
        },
        "month": 12,
        "entries": [],
        "holidays": [],
    }
    response = client.post("/reports/daily-report", json=payload_dec)
    assert response.status_code == 200


def test_km_month_integers_1_to_12(client):
    """Mileage report accepts month as 1–12 like daily report."""

    for month in range(1, 13):
        payload = {
            "company": {
                "name": "Test Company Ltd",
                "tax_id": "123456789",
                "address": "Av. Teste 99",
            },
            "employee": {
                "name": "Test Employee",
                "address": "Test Address",
                "tax_id": "987654321",
            },
            "month": month,
            "entries": [],
            "holidays": [],
        }
        response = client.post("/reports/mileage-report", json=payload)
        assert response.status_code == 200, f"Failed for month {month}"
