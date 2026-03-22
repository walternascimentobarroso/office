# -*- coding: utf-8 -*-
"""API routes for Mapa Diário report."""

import logging
from datetime import datetime, timezone

from fastapi import APIRouter
from fastapi.responses import JSONResponse, StreamingResponse

from src.core.exceptions import (
    ExcelWriteError,
    MappingError,
    TemplateLoadError,
)
from src.reports.mapa_diario.service import MapaDiarioService
from src.schemas.mapa_diario import MapaDiarioRequest

logger = logging.getLogger(__name__)

router = APIRouter()


def _generate_filename(request: MapaDiarioRequest) -> str:
    mes_label = str(request.month)
    mes_safe = "".join(
        c for c in mes_label if c.isalnum() or c in (" ", "-", "_")
    )[:20]
    timestamp_iso = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"relatorio_{mes_safe}_{timestamp_iso}.xlsx"


@router.post("/reports/mapa-diario", response_model=None)
async def generate_mapa_diario(
    request: MapaDiarioRequest,
) -> StreamingResponse | JSONResponse:
    """
    Generate Mapa Diário Excel file from structured JSON (legacy /generate-excel behaviour).

    Returns an .xlsx attachment with weekend/holiday column A styling, percentagem formatting,
    and footer including último dia útil do mês.
    """
    try:
        logger.info(
            "Mapa Diário generation request received",
            extra={
                "extra_data": {
                    "company_fields": len(
                        [v for v in request.company.model_dump().values() if v]
                    ),
                    "entries_count": len(request.entries),
                }
            },
        )

        service = MapaDiarioService()
        data = request.model_dump()
        excel_stream = service.generate(data, service.mappings)

        filename = _generate_filename(request)

        logger.info(
            "Mapa Diário generation successful",
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
        logger.error("Unexpected error in /reports/mapa-diario: %s", e, exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": "InternalServerError",
                "message": "An unexpected error occurred",
                "status": 500,
            },
        )
