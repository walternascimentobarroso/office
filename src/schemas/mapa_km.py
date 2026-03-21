# -*- coding: utf-8 -*-
"""Pydantic schemas for Mapa KM report."""

from typing import List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Meta(BaseModel):
    """Mapa KM header: company, optional address, tax id, month (1–12)."""

    empresa: Optional[str] = None
    endereco: Optional[str] = None
    nif: Optional[str] = None
    mes: int = Field(..., ge=1, le=12)


class Entry(BaseModel):
    """One KM row: day, route, justification, distance."""

    day: Optional[int] = None
    origem: Optional[str] = None
    destino: Optional[str] = None
    description: Optional[str] = None
    n_kms: Optional[Union[str, int, float]] = None


class Funcionario(BaseModel):
    """Employee + optional vehicle plate for Mapa KM footer."""

    nome_completo: Optional[str] = None
    morada: Optional[str] = None
    nif: Optional[str] = None
    vehicle_matricula: Optional[str] = None


class MapaKmRequest(BaseModel):
    """Request schema for Mapa KM."""

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
