# -*- coding: utf-8 -*-
"""Pydantic schemas for Mapa Diário report."""

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


class Funcionario(BaseModel):
    """Employee data for footer."""

    nome_completo: Optional[str] = None
    morada: Optional[str] = None
    nif: Optional[str] = None


class Meta(BaseModel):
    """Report metadata."""

    empresa: Optional[str] = None
    nif: Optional[str] = None
    mes: int = Field(..., ge=1, le=12)


class MapaDiarioRequest(BaseModel):
    """Request schema for Mapa Diário report."""

    meta: Meta
    entries: List[Entry] = Field(default_factory=list)
    funcionario: Optional[Funcionario] = None
    holidays: List[int] = Field(default_factory=list)

    model_config = ConfigDict(extra="ignore")

    @field_validator("holidays", mode="before")
    @classmethod
    def normalize_holidays(cls, value: object) -> list[int]:
        """Keep only valid day-of-month integers (same behaviour as legacy /generate-excel)."""

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
