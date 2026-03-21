# -*- coding: utf-8 -*-
"""Excel generation API - Pydantic request models"""

from typing import Optional, Any
from pydantic import BaseModel, ConfigDict, field_validator


class Meta(BaseModel):
    """Company metadata fields for Excel header"""

    empresa: Optional[str] = None
    nif: Optional[str] = None
    mes: int  # Required month (1-12) for weekend highlighting

    model_config = ConfigDict(extra="ignore")

    @field_validator('mes')
    @classmethod
    def mes_must_be_valid(cls, v):
        if not isinstance(v, int) or v < 1 or v > 12:
            raise ValueError('mes must be an integer between 1 and 12')
        return v


class Funcionario(BaseModel):
    """Employee fields for the footer block of the Excel template"""

    nome_completo: Optional[str] = None
    morada: Optional[str] = None
    nif: Optional[str] = None

    model_config = ConfigDict(extra="ignore")


class Entry(BaseModel):
    """Time/activity entry that maps to a row in Excel"""

    day: Optional[int | str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    percentagem: Optional[int] = None

    model_config = ConfigDict(extra="ignore")

    @field_validator('percentagem')
    @classmethod
    def percentagem_must_be_valid(cls, v):
        if v is not None and (v < 0 or v > 100):
            raise ValueError('percentagem must be between 0 and 100')
        return v


class GenerateExcelRequest(BaseModel):
    """Request payload for POST /generate-excel"""

    meta: Meta
    entries: list[Entry] = []
    funcionario: Optional[Funcionario] = None

    model_config = ConfigDict(extra="ignore")
