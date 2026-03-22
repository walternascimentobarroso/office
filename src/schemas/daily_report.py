# -*- coding: utf-8 -*-
"""Pydantic schemas for the daily report."""

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
    percentage: Optional[int] = Field(None, ge=0, le=100)


Company = CompanyModel
Employee = EmployeeModel


class DailyReportRequest(BaseReportRequest):
    """Request schema for the daily report."""

    entries: List[Entry] = Field(default_factory=list)

    model_config = ConfigDict(extra="ignore")
