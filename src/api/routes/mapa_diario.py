# -*- coding: utf-8 -*-
"""API routes for Mapa Diário report"""

import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from src.schemas.mapa_diario import MapaDiarioRequest
from src.reports.mapa_diario.service import MapaDiarioService
from src.services.style_service import StyleService
from src.services.holiday_service import HolidayService


logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/reports/mapa-diario")
async def generate_mapa_diario(request: MapaDiarioRequest) -> StreamingResponse:
    """Generate Mapa Diário Excel report"""
    try:
        logger.info("Generating Mapa Diário report")

        # Process holidays
        holidays = HolidayService.process_holidays(request.holidays)

        # Prepare data
        data = request.dict()
        data['holidays'] = list(holidays)

        # Generate report
        style_service = StyleService()
        service = MapaDiarioService(style_service)
        excel_data = service.generate(data, service.mappings)

        # Generate filename
        timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H-%M-%S")
        mes = request.meta.mes
        filename = f"relatorio_{mes}_{timestamp}.xlsx"

        # Return response
        return StreamingResponse(
            excel_data,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    except Exception as e:
        logger.error(f"Error generating Mapa Diário report: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate report")