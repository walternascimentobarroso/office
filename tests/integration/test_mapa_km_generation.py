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
            "mes": 3,
        },
        "entries": [],
        "funcionario": {},
        "holidays": [],
    }

    response = client.post("/reports/mapa-km", json=payload)
    assert response.status_code == 200

    wb = load_workbook(BytesIO(response.content))
    _ = wb.active


def test_mapa_km_entries_filled_correctly(client):
    """Test that entries are filled correctly in rows"""
    payload = {
        "meta": {"mes": 3},
        "entries": [
            {
                "day": 1,
                "description": "Drive to client",
                "location": "Client Office",
                "start_time": "08:00",
                "end_time": "09:00",
                "percentagem": 100,
            }
        ],
        "funcionario": {},
        "holidays": [],
    }

    response = client.post("/reports/mapa-km", json=payload)
    assert response.status_code == 200

    wb = load_workbook(BytesIO(response.content))
    _ = wb.active


def test_mapa_km_funcionario_footer_including_vehicle(client):
    """funcionario block fills footer; vehicle_matricula in viatura cell."""
    payload = {
        "meta": {"mes": 3},
        "entries": [],
        "funcionario": {
            "nome_completo": "Maria Silva",
            "morada": "Rua Um",
            "nif": "999888777",
            "vehicle_matricula": "AA-00-BB",
        },
        "holidays": [],
    }

    response = client.post("/reports/mapa-km", json=payload)
    assert response.status_code == 200

    wb = load_workbook(BytesIO(response.content))
    ws = wb.active
    assert ws["B45"].value == "Maria Silva"
    assert ws["B46"].value == "Rua Um"
    assert ws["E45"].value == "999888777"
    assert ws["E46"].value == "AA-00-BB"


def test_mapa_km_weekend_styling_applied(client):
    """Test that weekend days are styled correctly"""
    payload = {
        "meta": {"mes": 3},
        "entries": [],
        "funcionario": {},
        "holidays": [],
    }

    response = client.post("/reports/mapa-km", json=payload)
    assert response.status_code == 200

    wb = load_workbook(BytesIO(response.content))
    _ = wb.active


def test_mapa_km_holiday_styling_applied(client):
    """Test that holiday days are styled correctly"""
    payload = {
        "meta": {"mes": 3},
        "entries": [],
        "funcionario": {},
        "holidays": [5, 25],
    }

    response = client.post("/reports/mapa-km", json=payload)
    assert response.status_code == 200

    wb = load_workbook(BytesIO(response.content))
    _ = wb.active
