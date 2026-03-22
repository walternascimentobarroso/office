# -*- coding: utf-8 -*-
"""API routes for the daily report."""

import logging
from datetime import datetime, timezone

from fastapi import APIRouter
from fastapi.responses import JSONResponse, StreamingResponse

from src.core.exceptions import (
    ExcelWriteError,
    MappingError,
    TemplateLoadError,
)
from src.reports.daily_report.service import DailyReportService
from src.schemas.daily_report import DailyReportRequest

logger = logging.getLogger(__name__)

router = APIRouter()


def _generate_filename(request: DailyReportRequest) -> str:
    month_label = str(request.month)
    month_safe = "".join(
        c for c in month_label if c.isalnum() or c in (" ", "-", "_")
    )[:20]
    timestamp_iso = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"report_{month_safe}_{timestamp_iso}.xlsx"


@router.post("/reports/daily-report", response_model=None)
async def generate_daily_report(
    request: DailyReportRequest,
) -> StreamingResponse | JSONResponse:
    """
    Generate daily report Excel file from structured JSON.

    Returns an .xlsx attachment with weekend/holiday column A styling, percentage formatting,
    and footer including last business day of the month.
    """
    try:
        logger.info(
            "Daily report generation request received",
            extra={
                "extra_data": {
                    "company_fields": len(
                        [v for v in request.company.model_dump().values() if v]
                    ),
                    "entries_count": len(request.entries),
                }
            },
        )

        service = DailyReportService()
        data = request.model_dump()
        excel_stream = service.generate(data, service.mappings)

        filename = _generate_filename(request)

        logger.info(
            "Daily report generation successful",
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
        logger.error("Unexpected error in /reports/daily-report: %s", e, exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": "InternalServerError",
                "message": "An unexpected error occurred",
                "status": 500,
            },
        )
