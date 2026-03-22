# -*- coding: utf-8 -*-
"""Pydantic schemas for Mapa Diário report."""

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from src.schemas.base_report import BaseReportRequest, CompanyModel, EmployeeModel


class Entry(BaseModel):
    """Activity entry for report rows."""

    day: Optional[int] = None
    description: Optional[str] = None
    location: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    percentagem: Optional[int] = Field(None, ge=0, le=100)


# Backward compatibility aliases for legacy model names
Meta = CompanyModel
Funcionario = EmployeeModel


class MapaDiarioRequest(BaseReportRequest):
    """Request schema for Mapa Diário report."""

    entries: List[Entry] = Field(default_factory=list)

    model_config = ConfigDict(extra="ignore")
