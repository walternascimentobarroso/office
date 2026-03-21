# -*- coding: utf-8 -*-
"""Pydantic schemas for Mapa Diário report"""

from typing import Optional, List
from pydantic import BaseModel, Field, validator


class Entry(BaseModel):
    """Activity entry for report rows"""
    day: Optional[int] = None
    description: Optional[str] = None
    location: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    percentagem: Optional[int] = Field(None, ge=0, le=100)


class Funcionario(BaseModel):
    """Employee data for footer"""
    nome_completo: Optional[str] = None
    morada: Optional[str] = None
    nif: Optional[str] = None


class Meta(BaseModel):
    """Report metadata"""
    empresa: Optional[str] = None
    nif: Optional[str] = None
    mes: int = Field(..., ge=1, le=12)


class MapaDiarioRequest(BaseModel):
    """Request schema for Mapa Diário report"""
    meta: Meta
    entries: List[Entry] = Field(default_factory=list)
    funcionario: Optional[Funcionario] = None
    holidays: List[int] = Field(default_factory=list)

    @validator('holidays', each_item=True)
    def validate_holiday(cls, v):
        if not (1 <= v <= 31):
            raise ValueError('Holiday must be between 1 and 31')
        return v