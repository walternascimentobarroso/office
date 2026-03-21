# -*- coding: utf-8 -*-
"""Pydantic schemas for Mapa KM report."""

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Entry(BaseModel):
    """Activity entry for report rows."""

    day: Optional[int] = None
    description: Optional[str] = None
    location: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    percentagem: Optional[int] = Field(None, ge=0, le=100)


class Vehicle(BaseModel):
    """Vehicle data for footer."""

    modelo: Optional[str] = None
    matricula: Optional[str] = None
    kms: Optional[int] = None


class Meta(BaseModel):
    """Report metadata."""

    empresa: Optional[str] = None
    nif: Optional[str] = None
    mes: str

    @field_validator("mes")
    @classmethod
    def validate_mes(cls, v: str) -> str:
        valid_months = [
            "Janeiro",
            "Fevereiro",
            "Março",
            "Abril",
            "Maio",
            "Junho",
            "Julho",
            "Agosto",
            "Setembro",
            "Outubro",
            "Novembro",
            "Dezembro",
        ]
        if v not in valid_months:
            msg = f'Mês must be one of: {", ".join(valid_months)}'
            raise ValueError(msg)
        return v


class MapaKmRequest(BaseModel):
    """Request schema for Mapa KM report."""

    meta: Meta
    entries: List[Entry] = Field(default_factory=list)
    vehicle: Optional[Vehicle] = None
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
