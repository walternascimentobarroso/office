# -*- coding: utf-8 -*-
"""Excel generation API - Pydantic request models"""

from typing import Optional, Any
from pydantic import BaseModel, ConfigDict


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

    model_config = ConfigDict(extra="ignore")


class GenerateExcelRequest(BaseModel):
    """Request payload for POST /generate-excel"""

    meta: Meta
    entries: list[Entry] = []

    model_config = ConfigDict(extra="ignore")
