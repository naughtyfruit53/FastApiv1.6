# app/api/v1/__init__.py

from fastapi import APIRouter

from .user import router as user_router
from .organizations.routes import router as organizations_router
from .hr import router as hr_router
from .payroll import router as payroll_router
from .oauth import router as oauth_router
from .ledger import router as ledger_router
from .master_data import router as master_data_router
from .email import router as email_router
from .voucher_email_templates import router as voucher_email_templates_router
from .voucher_format_templates import router as voucher_format_templates_router
from .chatbot import router as chatbot_router

api_v1_router = APIRouter(prefix="/v1")

api_v1_router.include_router(user_router)
api_v1_router.include_router(organizations_router)
api_v1_router.include_router(hr_router)
api_v1_router.include_router(payroll_router)
api_v1_router.include_router(oauth_router, prefix="/oauth", tags=["OAuth2"])
api_v1_router.include_router(ledger_router)
api_v1_router.include_router(master_data_router, prefix="/master-data", tags=["master-data"])
api_v1_router.include_router(email_router, prefix="/email", tags=["email"])
api_v1_router.include_router(voucher_email_templates_router)
api_v1_router.include_router(voucher_format_templates_router)
api_v1_router.include_router(chatbot_router, prefix="/chatbot", tags=["Chatbot"])
# Removed: vouchers_router inclusion to avoid conflict with main.py mounting at /api/v1