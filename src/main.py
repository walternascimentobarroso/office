# -*- coding: utf-8 -*-
"""FastAPI application for Excel generation API."""

import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routers import (
    auth_router,
    billing_router,
    companies_router,
    employees_router,
    monthly_workflow_router,
    report_types_router,
    roles_router,
    users_router,
    workflow_templates_router,
)
from app.core.security import get_security_settings
from src.core.config import get_config
from src.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Excel Generation API",
    description="API for generating Excel files from structured JSON input",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_security_settings().cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(billing_router)
app.include_router(companies_router)
app.include_router(employees_router)
app.include_router(report_types_router)
app.include_router(roles_router)
app.include_router(users_router)
app.include_router(monthly_workflow_router)
app.include_router(workflow_templates_router)


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """Align validation errors with contract tests (422 + error/details)."""

    _ = request
    return JSONResponse(
        status_code=422,
        content={
            "error": "ValidationError",
            "message": "Request validation failed",
            "details": jsonable_encoder(exc.errors()),
        },
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTP exceptions."""

    _ = request
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": "HTTPError", "message": exc.detail},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle uncaught exceptions (last resort)."""

    _ = request
    logger.error("Unhandled exception: %s", exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "InternalError", "message": "An unexpected error occurred"},
    )


@app.on_event("startup")
async def startup_event() -> None:
    """Log startup."""

    _ = get_config()
    logger.info("Application started successfully")


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""

    _ = get_config()
    return {
        "status": "healthy",
        "service": "excel-generation-api",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
