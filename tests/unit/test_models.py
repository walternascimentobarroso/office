# -*- coding: utf-8 -*-
"""Unit tests for Pydantic schemas (Mapa Diário)."""

import pytest
from pydantic import ValidationError

from src.schemas.mapa_diario import Entry, Funcionario, MapaDiarioRequest, Meta


class TestMeta:
    """Tests for Meta model."""

    def test_meta_all_fields(self) -> None:
        meta = Meta(empresa="Acme Corp", nif="123456", mes=3)
        assert meta.empresa == "Acme Corp"
        assert meta.nif == "123456"
        assert meta.mes == 3

    def test_meta_mes_required(self) -> None:
        with pytest.raises(ValidationError):
            Meta(empresa="x")


class TestFuncionario:
    """Tests for Funcionario model."""

    def test_funcionario_all_fields(self) -> None:
        f = Funcionario(nome_completo="Ana Costa", morada="Rua X", nif="999")
        assert f.nome_completo == "Ana Costa"
        assert f.morada == "Rua X"
        assert f.nif == "999"


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
            meta={"empresa": "Corp", "nif": "123", "mes": 3},
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
        assert request.meta.empresa == "Corp"
        assert request.entries[0].percentagem == 75

    def test_holidays_normalized_drops_invalid(self) -> None:
        r = MapaDiarioRequest(
            meta={"mes": 3},
            holidays=[1, 32, 0, 5],
        )
        assert r.holidays == [1, 5]

    def test_extra_fields_ignored(self) -> None:
        r = MapaDiarioRequest.model_validate(
            {
                "meta": {"mes": 3},
                "entries": [],
                "extra_top": "ignored",
            }
        )
        assert "extra_top" not in r.model_dump()
