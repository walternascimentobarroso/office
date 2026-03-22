# -*- coding: utf-8 -*-
"""Pydantic schemas for Mapa KM report."""

from typing import List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field

from src.schemas.base_report import BaseReportRequest


class Entry(BaseModel):
    """One KM row: day, route, justification, distance."""

    day: Optional[int] = None
    origem: Optional[str] = None
    destino: Optional[str] = None
    description: Optional[str] = None
    n_kms: Optional[Union[str, int, float]] = None


class MapaKmRequest(BaseReportRequest):
    """Request schema for Mapa KM."""

    entries: List[Entry] = Field(default_factory=list)

    model_config = ConfigDict(extra="ignore")
