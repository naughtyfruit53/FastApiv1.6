# app/api/v1/__init__.py

from fastapi import APIRouter

from .user import router as user_router
from .organizations.routes import router as organizations_router
from .hr import router as hr_router
from .payroll import router as payroll_router

api_v1_router = APIRouter(prefix="/v1")

api_v1_router.include_router(user_router)
api_v1_router.include_router(organizations_router)
api_v1_router.include_router(hr_router)
api_v1_router.include_router(payroll_router)