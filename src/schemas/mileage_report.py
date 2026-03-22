# -*- coding: utf-8 -*-
"""Pydantic schemas for the mileage report."""

from typing import List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field

from src.schemas.base_report import BaseReportRequest


class Entry(BaseModel):
    """One mileage row: day, route, justification, distance."""

    day: Optional[int] = None
    origin: Optional[str] = None
    destination: Optional[str] = None
    description: Optional[str] = None
    distance_km: Optional[Union[str, int, float]] = None


class MileageReportRequest(BaseReportRequest):
    """Request schema for the mileage report."""

    entries: List[Entry] = Field(default_factory=list)

    model_config = ConfigDict(extra="ignore")
