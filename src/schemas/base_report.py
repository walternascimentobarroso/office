# -*- coding: utf-8 -*-
"""Shared base schemas for all report request payloads."""

from __future__ import annotations

from datetime import date
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, conint


class CompanyModel(BaseModel):
    """Company metadata in English fields."""

    name: str
    tax_id: str
    address: str


class EmployeeModel(BaseModel):
    """Employee metadata in English fields."""

    name: str
    address: str
    tax_id: str
    vehicle_plate: Optional[str] = None


class BaseReportRequest(BaseModel):
    """Base report request containing common fields for all reports."""

    company: CompanyModel
    employee: EmployeeModel
    month: conint(ge=1, le=12)
    year: Optional[conint(ge=2000, le=2100)] = None
    holidays: List[int] = Field(default_factory=list)
    entries: List[Dict[str, Any]] = Field(default_factory=list)

    model_config = ConfigDict(extra="ignore")

    @field_validator("year", mode="before")
    @classmethod
    def validate_year(cls, value: Any) -> int:
        if value is None:
            return date.today().year
        return value

    @field_validator("holidays", mode="before")
    @classmethod
    def normalize_holidays(cls, value: Any) -> List[int]:
        if value is None:
            return []
        if not isinstance(value, list):
            return []

        normalized: List[int] = []
        for item in value:
            if item is None or isinstance(item, bool):
                continue
            if isinstance(item, int) and 1 <= item <= 31:
                normalized.append(item)

        return normalized
