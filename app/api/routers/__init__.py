"""Router exports."""

from app.api.routers.companies import router as companies_router
from app.api.routers.employees import router as employees_router
from app.api.routers.reports import router as reports_router

__all__ = ["companies_router", "employees_router", "reports_router"]
