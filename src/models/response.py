# -*- coding: utf-8 -*-
"""Excel generation API - Pydantic response models"""

from typing import Optional, Any
from pydantic import BaseModel


class ErrorDetail(BaseModel):
    """Details of a validation error"""

    field: str
    issue: str


class ErrorResponse(BaseModel):
    """Standard error response format"""

    error: str
    message: str
    status: int
    details: Optional[list[ErrorDetail]] = None
