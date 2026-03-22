# -*- coding: utf-8 -*-
"""API routes for the mileage report."""

import logging
from datetime import datetime, timezone

from fastapi import APIRouter
from fastapi.responses import JSONResponse, StreamingResponse

from src.core.exceptions import (
    ExcelWriteError,
    MappingError,
    TemplateLoadError,
)
from src.reports.mileage_report.service import MileageReportService
from src.schemas.mileage_report import MileageReportRequest
from src.services.date_service import DateService

logger = logging.getLogger(__name__)

router = APIRouter()


def _generate_filename(request: MileageReportRequest) -> str:
    month_num = DateService.resolve_month(request.month)
    month_safe = str(month_num)
    timestamp_iso = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"report_{month_safe}_{timestamp_iso}.xlsx"


@router.post("/reports/mileage-report", response_model=None)
async def generate_mileage_report(
    request: MileageReportRequest,
) -> StreamingResponse | JSONResponse:
    """Generate mileage report Excel file."""
    try:
        logger.info(
            "Mileage report generation request received",
            extra={
                "extra_data": {
                    "company_fields": len(
                        [v for v in request.company.model_dump().values() if v]
                    ),
                    "entries_count": len(request.entries),
                }
            },
        )

        service = MileageReportService()
        data = request.model_dump()
        excel_stream = service.generate(data, service.mappings)

        filename = _generate_filename(request)

        logger.info(
            "Mileage report generation successful",
            extra={
                "extra_data": {
                    "filename": filename,
                    "file_size": excel_stream.getbuffer().nbytes,
                }
            },
        )

        return StreamingResponse(
            excel_stream,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )

    except (TemplateLoadError, MappingError, ExcelWriteError) as e:
        logger.error("Service error: %s", e, exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": type(e).__name__,
                "message": str(e),
                "status": 500,
            },
        )

    except Exception as e:
        logger.error("Unexpected error in /reports/mileage-report: %s", e, exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": "InternalServerError",
                "message": "An unexpected error occurred",
                "status": 500,
            },
        )
