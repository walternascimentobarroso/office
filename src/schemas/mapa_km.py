# -*- coding: utf-8 -*-
"""Pydantic schemas for Mapa KM report (same shape as Mapa Diário + vehicle in funcionario)."""

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.schemas.mapa_diario import Entry, Meta


class Funcionario(BaseModel):
    """Employee + optional vehicle plate for Mapa KM footer."""

    nome_completo: Optional[str] = None
    morada: Optional[str] = None
    nif: Optional[str] = None
    vehicle_matricula: Optional[str] = None


class MapaKmRequest(BaseModel):
    """Request schema for Mapa KM — mirrors Mapa Diário; funcionario may include vehicle_matricula."""

    meta: Meta
    entries: List[Entry] = Field(default_factory=list)
    funcionario: Optional[Funcionario] = None
    holidays: List[int] = Field(default_factory=list)

    model_config = ConfigDict(extra="ignore")

    @field_validator("holidays", mode="before")
    @classmethod
    def normalize_holidays(cls, value: object) -> list[int]:
        if value is None:
            return []
        if not isinstance(value, list):
            return []
        out: list[int] = []
        for item in value:
            if item is None or isinstance(item, bool):
                continue
            if isinstance(item, int) and 1 <= item <= 31:
                out.append(item)
        return out
