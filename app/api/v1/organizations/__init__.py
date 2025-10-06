# app/api/v1/organizations/__init__.py

from fastapi import APIRouter

from .routes import router
from .settings_routes import router as settings_router

router.include_router(settings_router, prefix="/settings", tags=["organization-settings"])

__all__ = ["router"]