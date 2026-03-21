# -*- coding: utf-8 -*-
"""Excel generation API - Pydantic request models"""

from typing import Optional, Any
from pydantic import BaseModel, ConfigDict, field_validator


class Meta(BaseModel):
    """Company metadata fields for Excel header"""

    empresa: Optional[str] = None
    nif: Optional[str] = None
    mes: Optional[str] = None

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

    model_config = ConfigDict(extra="ignore")
