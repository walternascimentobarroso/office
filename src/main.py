# -*- coding: utf-8 -*-
"""FastAPI application for Excel generation API"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError
import logging

from src.api.routes import excel
from src.logging_config import setup_logging
from src.core.config import get_config
from src.core.exceptions import TemplateLoadError

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Excel Generation API",
    description="API for generating Excel files from structured JSON input",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(excel.router)


@app.on_event("startup")
async def startup_event():
    """Validate configuration on startup"""
    try:
        config = get_config()
        logger.info("Application started successfully")
        logger.info(
            "Configuration loaded",
            extra={
                "extra_data": {
                    "template_path": config.template_path,
                    "header_mapping_path": config.header_mapping_path,
                    "rows_mapping_path": config.rows_mapping_path,
                }
            },
        )
    except TemplateLoadError as e:
        logger.critical(f"Startup failed: {e}")
        raise


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        config = get_config()
        return {
            "status": "healthy",
            "service": "excel-generation-api",
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=500,
            content={"status": "unhealthy", "error": str(e)},
        )


@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    """Handle Pydantic validation errors"""
    logger.warning(f"Validation error: {exc}")
    errors = []
    for error in exc.errors():
        errors.append(
            {
                "field": ".".join(str(x) for x in error["loc"]),
                "issue": error["msg"],
            }
        )

    return JSONResponse(
        status_code=400,
        content={
            "error": "ValidationError",
            "message": "Invalid request body",
            "status": 400,
            "details": errors,
        },
    )


@app.get("/docs")
async def get_docs():
    """Swagger UI docs"""
    return app.openapi()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
