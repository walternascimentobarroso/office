# -*- coding: utf-8 -*-
"""Unit tests for Pydantic schemas (Mapa Diário)."""

import pytest
from pydantic import ValidationError

from src.schemas.mapa_diario import Entry, MapaDiarioRequest, Meta, Funcionario


class TestMeta:
    """Tests for Meta (CompanyModel) model."""

    def test_meta_all_fields(self) -> None:
        meta = Meta(name="Acme Corp", tax_id="123456", address="Rua X")
        assert meta.name == "Acme Corp"
        assert meta.tax_id == "123456"
        assert meta.address == "Rua X"

    def test_meta_required_fields(self) -> None:
        with pytest.raises(ValidationError):
            Meta(name="x")



class TestFuncionario:
    """Tests for Funcionario (EmployeeModel) model."""

    def test_funcionario_all_fields(self) -> None:
        f = Funcionario(name="Ana Costa", address="Rua X", tax_id="999")
        assert f.name == "Ana Costa"
        assert f.address == "Rua X"
        assert f.tax_id == "999"


class TestEntry:
    """Tests for Entry model."""

    def test_entry_percentagem_invalid(self) -> None:
        with pytest.raises(ValidationError):
            Entry(percentagem=-1)
        with pytest.raises(ValidationError):
            Entry(percentagem=101)


class TestMapaDiarioRequest:
    """Tests for MapaDiarioRequest model."""

    def test_valid_request_full_data(self) -> None:
        request = MapaDiarioRequest(
            company={"name": "Corp", "tax_id": "123", "address": "Rua X"},
            employee={"name": "Ana Costa", "tax_id": "999", "address": "Rua X"},
            month=3,
            entries=[
                {
                    "day": 1,
                    "description": "Task 1",
                    "location": "Office",
                    "start_time": "09:00",
                    "end_time": "10:00",
                    "percentagem": 75,
                },
            ],
        )
        assert len(request.entries) == 1
        assert request.company.name == "Corp"
        assert request.entries[0].percentagem == 75

    def test_holidays_normalized_drops_invalid(self) -> None:
        r = MapaDiarioRequest(
            company={"name": "Corp", "tax_id": "123", "address": "Rua X"},
            employee={"name": "Ana Costa", "tax_id": "999", "address": "Rua X"},
            month=3,
            holidays=[1, 32, 0, 5],
        )
        assert r.holidays == [1, 5]

    def test_extra_fields_ignored(self) -> None:
        r = MapaDiarioRequest.model_validate(
            {
                "company": {"name": "Corp", "tax_id": "123", "address": "Rua X"},
                "employee": {"name": "Ana", "tax_id": "123", "address": "Address"},
                "month": 3,
                "entries": [],
                "extra_top": "ignored",
            }
        )
        assert "extra_top" not in r.model_dump()
