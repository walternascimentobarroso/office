# -*- coding: utf-8 -*-
"""Contract tests for POST /reports/daily-report endpoint"""

import pytest
from fastapi.testclient import TestClient
from src.main import app


@pytest.fixture
def client():
    """FastAPI test client"""
    return TestClient(app)


def test_daily_report_valid_request_returns_excel(client):
    """Test that valid request returns Excel file"""
    payload = {
        "company": {
            "name": "Test Company",
            "address": "1 Test Ave",
            "tax_id": "123456789",
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
                "description": "Test activity",
                "location": "Test location",
                "start_time": "09:00",
                "end_time": "10:00",
                "percentage": 100,
            }
        ],
        "holidays": [5, 25],
    }

    response = client.post("/reports/daily-report", json=payload)

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    assert "attachment; filename=" in response.headers.get("content-disposition", "")
    assert b"PK" in response.content  # XLSX files start with PK (ZIP header)


def test_daily_report_invalid_month_returns_422(client):
    """Test that invalid month returns validation error"""
    payload = {
        "company": {
            "name": "Test Company",
            "tax_id": "123456789",
            "address": "1 Test Ave",
        },
        "employee": {
            "name": "Test Employee",
            "address": "Test Address",
            "tax_id": "987654321",
        },
        "month": 13,  # Invalid month
        "entries": [],
        "holidays": [],
    }

    response = client.post("/reports/daily-report", json=payload)

    assert response.status_code == 422
    data = response.json()
    assert data["error"] == "ValidationError"
    assert any(
        "month" in str(err.get("loc", ()))
        for err in data["details"]
    )


def test_daily_report_missing_required_fields_returns_422(client):
    """Test that missing required fields return validation error"""
    payload = {
        "company": {
            "name": "Test Company",
            "tax_id": "123456789",
            "address": "1 Test Ave",
        },
        "employee": {
            "name": "Test Employee",
            "address": "Test Address",
            "tax_id": "987654321",
        },
        "entries": [],
    }  # Missing month

    response = client.post("/reports/daily-report", json=payload)

    assert response.status_code == 422
    data = response.json()
    assert data["error"] == "ValidationError"
    assert any(
        "month" in str(err.get("loc", ()))
        for err in data["details"]
    )


def test_daily_report_invalid_holidays_filtered_like_legacy(client):
    """Invalid holiday values are dropped (same as legacy /generate-excel)."""
    payload = {
        "company": {
            "name": "Test Company",
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
        "holidays": [32, "invalid", 5],
    }

    response = client.post("/reports/daily-report", json=payload)

    assert response.status_code == 200
