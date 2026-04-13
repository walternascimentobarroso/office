"""Router exports."""

from app.api.routers.assets import router as assets_router
from app.api.routers.auth import router as auth_router
from app.api.routers.billing import router as billing_router
from app.api.routers.companies import router as companies_router
from app.api.routers.employees import router as employees_router
from app.api.routers.report_types import router as report_types_router
from app.api.routers.roles import router as roles_router
from app.api.routers.monthly_workflow import (
    monthly_workflow_router,
    workflow_templates_router,
)
from app.api.routers.users import router as users_router

__all__ = [
    "assets_router",
    "auth_router",
    "billing_router",
    "companies_router",
    "employees_router",
    "report_types_router",
    "roles_router",
    "users_router",
    "monthly_workflow_router",
    "workflow_templates_router",
]
