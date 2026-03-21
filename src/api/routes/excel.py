# -*- coding: utf-8 -*-
"""POST /generate-excel endpoint"""

from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, JSONResponse
import logging

from src.models.request import GenerateExcelRequest
from src.models.response import ErrorResponse, ErrorDetail
from src.services.excel_service import ExcelService
from src.core.config import get_config
from src.core.exceptions import (
    TemplateLoadError,
    MappingError,
    ExcelWriteError,
    ValidationError as CustomValidationError,
)
from pydantic import ValidationError

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize service
_excel_service = None


def get_excel_service() -> ExcelService:
    """Get or create Excel service (singleton)"""
    global _excel_service
    if _excel_service is None:
        _excel_service = ExcelService(get_config())
    return _excel_service


def _generate_filename(request: GenerateExcelRequest) -> str:
    """Generate filename for Excel output"""
    mes = request.meta.mes or "report"
    # Sanitize mes for use in filename (remove special chars)
    mes_safe = "".join(c for c in mes if c.isalnum() or c in (" ", "-", "_"))[:20]
    timestamp_iso = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"relatorio_{mes_safe}_{timestamp_iso}.xlsx"


@router.post("/generate-excel")
async def generate_excel(request: GenerateExcelRequest) -> FileResponse:
    """
    Generate Excel file from structured JSON input
    
    Request body:
    {
        "meta": {
            "empresa": "string (optional)",
            "nif": "string (optional)",
            "mes": "string (optional)"
        },
        "entries": [
            {
                "day": "int (optional)",
                "description": "string (optional)",
                "location": "string (optional)",
                "start_time": "string (optional)",
                "end_time": "string (optional)"
            }
        ]
    }
    
    Returns:
        FileResponse: Excel file (XLSX format)
    
    Raises:
        HTTPException: 400 for validation errors, 500 for template/processing errors
    """
    try:
        logger.info(
            "Excel generation request received",
            extra={
                "extra_data": {
                    "meta_fields": len(
                        [v for v in request.meta.model_dump().values() if v]
                    ),
                    "entries_count": len(request.entries),
                }
            },
        )

        # Get Excel service and generate file
        service = get_excel_service()
        excel_stream = await service.generate(request)

        # Generate filename
        filename = _generate_filename(request)

        logger.info(
            "Excel generation successful",
            extra={"extra_data": {"filename": filename, "file_size": excel_stream.getbuffer().nbytes}},
        )

        # Return file response
        return FileResponse(
            excel_stream,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename=filename,
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )

    except (TemplateLoadError, MappingError, ExcelWriteError) as e:
        logger.error(f"Service error: {e}", exc_info=True)
        error_response = {
            "error": type(e).__name__,
            "message": str(e),
            "status": 500,
        }
        return JSONResponse(status_code=500, content=error_response)

    except Exception as e:
        logger.error(f"Unexpected error in /generate-excel: {e}", exc_info=True)
        error_response = {
            "error": "InternalServerError",
            "message": "An unexpected error occurred",
            "status": 500,
        }
        return JSONResponse(status_code=500, content=error_response)
