# -*- coding: utf-8 -*-
"""Pydantic schemas for Mapa KM report"""

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


class Vehicle(BaseModel):
    """Vehicle data for footer"""
    modelo: Optional[str] = None
    matricula: Optional[str] = None
    kms: Optional[int] = None


class Meta(BaseModel):
    """Report metadata"""
    empresa: Optional[str] = None
    nif: Optional[str] = None
    mes: str

    @validator('mes')
    def validate_mes(cls, v):
        valid_months = [
            "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
            "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
        ]
        if v not in valid_months:
            raise ValueError(f'Mês must be one of: {", ".join(valid_months)}')
        return v


class MapaKmRequest(BaseModel):
    """Request schema for Mapa KM report"""
    meta: Meta
    entries: List[Entry] = Field(default_factory=list)
    vehicle: Optional[Vehicle] = None
    holidays: List[int] = Field(default_factory=list)

    @validator('holidays', each_item=True)
    def validate_holiday(cls, v):
        if not (1 <= v <= 31):
            raise ValueError('Holiday must be between 1 and 31')
        return v