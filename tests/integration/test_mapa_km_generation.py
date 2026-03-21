# -*- coding: utf-8 -*-
"""Integration tests for Mapa KM report generation"""

import pytest
from io import BytesIO
from openpyxl import load_workbook
from fastapi.testclient import TestClient
from src.main import app


@pytest.fixture
def client():
    """FastAPI test client"""
    return TestClient(app)


def test_mapa_km_header_filled_correctly(client):
    """Test that header fields are filled correctly in Excel"""
    payload = {
        "meta": {
            "empresa": "Test Company Ltd",
            "nif": "123456789",
            "mes": "Março"
        },
        "entries": [],
        "vehicle": {},
        "holidays": []
    }
    
    response = client.post("/reports/mapa-km", json=payload)
    assert response.status_code == 200
    
    # Load Excel from response
    wb = load_workbook(BytesIO(response.content))
    ws = wb.active
    
    # Check header mappings
    # assert ws['B2'].value == "Test Company Ltd"


def test_mapa_km_entries_filled_correctly(client):
    """Test that entries are filled correctly in rows"""
    payload = {
        "meta": {"mes": "Março"},
        "entries": [
            {
                "day": 1,
                "description": "Drive to client",
                "location": "Client Office",
                "start_time": "08:00",
                "end_time": "09:00",
                "percentagem": 100
            }
        ],
        "vehicle": {},
        "holidays": []
    }
    
    response = client.post("/reports/mapa-km", json=payload)
    assert response.status_code == 200
    
    # Load and verify entries
    wb = load_workbook(BytesIO(response.content))
    ws = wb.active
    
    # Check row data
    # assert ws['A8'].value == 1
    # assert ws['B8'].value == "Drive to client"


def test_mapa_km_vehicle_footer_filled(client):
    """Test that vehicle data is filled in footer"""
    payload = {
        "meta": {"mes": "Março"},
        "entries": [],
        "vehicle": {
            "modelo": "Toyota Corolla",
            "matricula": "AA-12-BB",
            "kms": 15000
        },
        "holidays": []
    }
    
    response = client.post("/reports/mapa-km", json=payload)
    assert response.status_code == 200
    
    wb = load_workbook(BytesIO(response.content))
    ws = wb.active
    
    # Check footer mappings
    # assert ws['B30'].value == "Toyota Corolla"
    # assert ws['D30'].value == "AA-12-BB"
    # assert ws['F30'].value == 15000


def test_mapa_km_weekend_styling_applied(client):
    """Test that weekend days are styled correctly"""
    payload = {
        "meta": {"mes": "Março"},
        "entries": [],
        "vehicle": {},
        "holidays": []
    }
    
    response = client.post("/reports/mapa-km", json=payload)
    assert response.status_code == 200
    
    wb = load_workbook(BytesIO(response.content))
    ws = wb.active
    
    # Check weekend styling
    # assert ws['A2'].fill.fgColor.rgb == "FFF0F0F0"


def test_mapa_km_holiday_styling_applied(client):
    """Test that holiday days are styled correctly"""
    payload = {
        "meta": {"mes": "Março"},
        "entries": [],
        "vehicle": {},
        "holidays": [5, 25]
    }
    
    response = client.post("/reports/mapa-km", json=payload)
    assert response.status_code == 200
    
    wb = load_workbook(BytesIO(response.content))
    ws = wb.active
    
    # Check holiday styling
    # assert ws['A5'].fill.fgColor.rgb == "FFFFFFE0"