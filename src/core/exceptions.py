# -*- coding: utf-8 -*-
"""Excel generation API - Custom exceptions"""


class TemplateLoadError(Exception):
    """Raised when Excel template cannot be loaded"""

    pass


class MappingError(Exception):
    """Raised when mapping configuration is invalid"""

    pass


class ExcelWriteError(Exception):
    """Raised when Excel file cannot be written"""

    pass


class ValidationError(Exception):
    """Raised when request validation fails"""

    pass


class InternalServerError(Exception):
    """Raised for unexpected server errors"""

    pass
