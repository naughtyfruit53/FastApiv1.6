# app/api/v1/__init__.py

from fastapi import APIRouter
from fastapi.routing import APIRoute
import logging
import traceback

logger = logging.getLogger(__name__)

# Import routers
try:
    from .user import router as user_router
    logger.debug("Imported user_router")
except Exception as e:
    logger.error(f"Failed to import user_router: {str(e)}\n{traceback.format_exc()}")
    raise

try:
    from .organizations.routes import router as organizations_router
    logger.debug("Imported organizations_router")
except Exception as e:
    logger.error(f"Failed to import organizations_router: {str(e)}\n{traceback.format_exc()}")
    raise

try:
    from .hr import router as hr_router
    logger.debug("Imported hr_router")
except Exception as e:
    logger.error(f"Failed to import hr_router: {str(e)}\n{traceback.format_exc()}")
    raise

try:
    from .payroll import router as payroll_router
    logger.debug("Imported payroll_router")
except Exception as e:
    logger.error(f"Failed to import payroll_router: {str(e)}\n{traceback.format_exc()}")
    raise

try:
    from .oauth import router as oauth_router
    logger.debug("Imported oauth_router")
except Exception as e:
    logger.error(f"Failed to import oauth_router: {str(e)}\n{traceback.format_exc()}")
    raise

try:
    from .ledger import router as ledger_router
    logger.debug("Imported ledger_router")
except Exception as e:
    logger.error(f"Failed to import ledger_router: {str(e)}\n{traceback.format_exc()}")
    raise

try:
    from .master_data import router as master_data_router
    logger.debug("Imported master_data_router")
except Exception as e:
    logger.error(f"Failed to import master_data_router: {str(e)}\n{traceback.format_exc()}")
    raise

try:
    from .email import router as email_router
    logger.debug("Imported email_router")
except Exception as e:
    logger.error(f"Failed to import email_router: {str(e)}\n{traceback.format_exc()}")
    raise

try:
    from .voucher_email_templates import router as voucher_email_templates_router
    logger.debug("Imported voucher_email_templates_router")
except Exception as e:
    logger.error(f"Failed to import voucher_email_templates_router: {str(e)}\n{traceback.format_exc()}")
    raise

try:
    from .voucher_format_templates import router as voucher_format_templates_router
    logger.debug("Imported voucher_format_templates_router")
except Exception as e:
    logger.error(f"Failed to import voucher_format_templates_router: {str(e)}\n{traceback.format_exc()}")
    raise

try:
    from .chatbot import router as chatbot_router
    logger.debug("Imported chatbot_router")
except Exception as e:
    logger.error(f"Failed to import chatbot_router: {str(e)}\n{traceback.format_exc()}")
    raise

try:
    from .ai import router as ai_router
    logger.debug("Imported ai_router")
except Exception as e:
    logger.error(f"Failed to import ai_router: {str(e)}\n{traceback.format_exc()}")
    raise

try:
    from .manufacturing import router as manufacturing_router
    logger.debug("Imported manufacturing_router")
except Exception as e:
    logger.error(f"Failed to import manufacturing_router: {str(e)}\n{traceback.format_exc()}")
    raise

try:
    from .transport import router as transport_router
    logger.debug("Imported transport_router")
except Exception as e:
    logger.error(f"Failed to import transport_router: {str(e)}\n{traceback.format_exc()}")
    raise

try:
    from .chart_of_accounts import router as chart_of_accounts_router
    logger.debug("Imported chart_of_accounts_router")
except Exception as e:
    logger.error(f"Failed to import chart_of_accounts_router: {str(e)}\n{traceback.format_exc()}")
    raise

try:
    from .erp import router as erp_router
    logger.debug("Imported erp_router")
except Exception as e:
    logger.error(f"Failed to import erp_router: {str(e)}\n{traceback.format_exc()}")
    raise

try:
    from .crm import router as crm_router
    logger.debug("Imported crm_router")
except Exception as e:
    logger.error(f"Failed to import crm_router: {str(e)}\n{traceback.format_exc()}")
    raise

try:
    from ..pincode import router as pincode_router
    logger.debug("Imported pincode_router")
except Exception as e:
    logger.error(f"Failed to import pincode_router: {str(e)}\n{traceback.format_exc()}")
    raise

try:
    from .website_agent import router as website_agent_router
    logger.debug("Imported website_agent_router")
except Exception as e:
    logger.error(f"Failed to import website_agent_router: {str(e)}\n{traceback.format_exc()}")
    raise

api_v1_router = APIRouter()

# Include routers with detailed logging
try:
    api_v1_router.include_router(manufacturing_router, tags=["Manufacturing"])
    manufacturing_routes = [f"{', '.join(sorted(route.methods)) if route.methods else 'ALL'} {route.path}" for route in manufacturing_router.routes if isinstance(route, APIRoute)]
    logger.debug(f"Registered manufacturing endpoints: {len(manufacturing_routes)} routes")
    for route_path in manufacturing_routes:
        logger.debug(f"  {route_path}")
except Exception as e:
    logger.error(f"Failed to include manufacturing_router: {str(e)}\n{traceback.format_exc()}")
    raise

try:
    api_v1_router.include_router(transport_router, prefix="/transport", tags=["Transport"])
    transport_routes = [f"{', '.join(sorted(route.methods)) if route.methods else 'ALL'} /transport{route.path}" for route in transport_router.routes if isinstance(route, APIRoute)]
    logger.debug(f"Registered transport endpoints: {len(transport_routes)} routes")
    for route_path in transport_routes:
        logger.debug(f"  {route_path}")
except Exception as e:
    logger.error(f"Failed to include transport_router: {str(e)}\n{traceback.format_exc()}")
    raise

try:
    api_v1_router.include_router(organizations_router)
    org_routes = [f"{', '.join(sorted(route.methods)) if route.methods else 'ALL'} {route.path}" for route in organizations_router.routes if isinstance(route, APIRoute)]
    logger.debug(f"Registered organizations endpoints: {len(org_routes)} routes")
    for route_path in org_routes:
        logger.debug(f"  {route_path}")
except Exception as e:
    logger.error(f"Failed to include organizations_router: {str(e)}\n{traceback.format_exc()}")
    raise

try:
    api_v1_router.include_router(hr_router)
    hr_routes = [f"{', '.join(sorted(route.methods)) if route.methods else 'ALL'} {route.path}" for route in hr_router.routes if isinstance(route, APIRoute)]
    logger.debug(f"Registered hr endpoints: {len(hr_routes)} routes")
    for route_path in hr_routes:
        logger.debug(f"  {route_path}")
except Exception as e:
    logger.error(f"Failed to include hr_router: {str(e)}\n{traceback.format_exc()}")
    raise

try:
    api_v1_router.include_router(payroll_router)
    payroll_routes = [f"{', '.join(sorted(route.methods)) if route.methods else 'ALL'} {route.path}" for route in payroll_router.routes if isinstance(route, APIRoute)]
    logger.debug(f"Registered payroll endpoints: {len(payroll_routes)} routes")
    for route_path in payroll_routes:
        logger.debug(f"  {route_path}")
except Exception as e:
    logger.error(f"Failed to include payroll_router: {str(e)}\n{traceback.format_exc()}")
    raise

try:
    api_v1_router.include_router(oauth_router, prefix="/oauth", tags=["OAuth2"])
    oauth_routes = [f"{', '.join(sorted(route.methods)) if route.methods else 'ALL'} /oauth{route.path}" for route in oauth_router.routes if isinstance(route, APIRoute)]
    logger.debug(f"Registered oauth endpoints: {len(oauth_routes)} routes")
    for route_path in oauth_routes:
        logger.debug(f"  {route_path}")
except Exception as e:
    logger.error(f"Failed to include oauth_router: {str(e)}\n{traceback.format_exc()}")
    raise

try:
    api_v1_router.include_router(ledger_router)
    ledger_routes = [f"{', '.join(sorted(route.methods)) if route.methods else 'ALL'} {route.path}" for route in ledger_router.routes if isinstance(route, APIRoute)]
    logger.debug(f"Registered ledger endpoints: {len(ledger_routes)} routes")
    for route_path in ledger_routes:
        logger.debug(f"  {route_path}")
except Exception as e:
    logger.error(f"Failed to include ledger_router: {str(e)}\n{traceback.format_exc()}")
    raise

try:
    api_v1_router.include_router(master_data_router, prefix="/master-data", tags=["master-data"])
    master_data_routes = [f"{', '.join(sorted(route.methods)) if route.methods else 'ALL'} /master-data{route.path}" for route in master_data_router.routes if isinstance(route, APIRoute)]
    logger.debug(f"Registered master_data endpoints: {len(master_data_routes)} routes")
    for route_path in master_data_routes:
        logger.debug(f"  {route_path}")
except Exception as e:
    logger.error(f"Failed to include master_data_router: {str(e)}\n{traceback.format_exc()}")
    raise

try:
    api_v1_router.include_router(email_router, prefix="/email", tags=["email"])
    email_routes = [f"{', '.join(sorted(route.methods)) if route.methods else 'ALL'} /email{route.path}" for route in email_router.routes if isinstance(route, APIRoute)]
    logger.debug(f"Registered email endpoints: {len(email_routes)} routes")
    for route_path in email_routes:
        logger.debug(f"  {route_path}")
except Exception as e:
    logger.error(f"Failed to include email_router: {str(e)}\n{traceback.format_exc()}")
    raise

try:
    api_v1_router.include_router(voucher_email_templates_router)
    voucher_email_routes = [f"{', '.join(sorted(route.methods)) if route.methods else 'ALL'} {route.path}" for route in voucher_email_templates_router.routes if isinstance(route, APIRoute)]
    logger.debug(f"Registered voucher_email_templates endpoints: {len(voucher_email_routes)} routes")
    for route_path in voucher_email_routes:
        logger.debug(f"  {route_path}")
except Exception as e:
    logger.error(f"Failed to include voucher_email_templates_router: {str(e)}\n{traceback.format_exc()}")
    raise

try:
    api_v1_router.include_router(voucher_format_templates_router)
    voucher_format_routes = [f"{', '.join(sorted(route.methods)) if route.methods else 'ALL'} {route.path}" for route in voucher_format_templates_router.routes if isinstance(route, APIRoute)]
    logger.debug(f"Registered voucher_format_templates endpoints: {len(voucher_format_routes)} routes")
    for route_path in voucher_format_routes:
        logger.debug(f"  {route_path}")
except Exception as e:
    logger.error(f"Failed to include voucher_format_templates_router: {str(e)}\n{traceback.format_exc()}")
    raise

try:
    api_v1_router.include_router(chatbot_router, prefix="/chatbot", tags=["Chatbot"])
    chatbot_routes = [f"{', '.join(sorted(route.methods)) if route.methods else 'ALL'} /chatbot{route.path}" for route in chatbot_router.routes if isinstance(route, APIRoute)]
    logger.debug(f"Registered chatbot endpoints: {len(chatbot_routes)} routes")
    for route_path in chatbot_routes:
        logger.debug(f"  {route_path}")
except Exception as e:
    logger.error(f"Failed to include chatbot_router: {str(e)}\n{traceback.format_exc()}")
    raise

try:
    api_v1_router.include_router(ai_router, prefix="/ai", tags=["AI Agent"])
    ai_routes = [f"{', '.join(sorted(route.methods)) if route.methods else 'ALL'} /ai{route.path}" for route in ai_router.routes if isinstance(route, APIRoute)]
    logger.debug(f"Registered ai_router endpoints: {len(ai_routes)} routes")
    for route_path in ai_routes:
        logger.debug(f"  {route_path}")
except Exception as e:
    logger.error(f"Failed to include ai_router: {str(e)}\n{traceback.format_exc()}")
    raise

try:
    api_v1_router.include_router(chart_of_accounts_router, tags=["Chart of Accounts"])
    chart_of_accounts_routes = [f"{', '.join(sorted(route.methods)) if route.methods else 'ALL'} {route.path}" for route in chart_of_accounts_router.routes if isinstance(route, APIRoute)]
    logger.debug(f"Registered chart_of_accounts endpoints: {len(chart_of_accounts_routes)} routes")
    for route_path in chart_of_accounts_routes:
        logger.debug(f"  {route_path}")
except Exception as e:
    logger.error(f"Failed to include chart_of_accounts_router: {str(e)}\n{traceback.format_exc()}")
    raise

try:
    api_v1_router.include_router(erp_router, prefix="/erp", tags=["ERP"])
    erp_routes = [f"{', '.join(sorted(route.methods)) if route.methods else 'ALL'} /erp{route.path}" for route in erp_router.routes if isinstance(route, APIRoute)]
    logger.debug(f"Registered erp endpoints: {len(erp_routes)} routes")
    for route_path in erp_routes:
        logger.debug(f"  {route_path}")
except Exception as e:
    logger.error(f"Failed to include erp_router: {str(e)}\n{traceback.format_exc()}")
    raise

try:
    api_v1_router.include_router(crm_router, tags=["CRM"])
    crm_routes = [f"{', '.join(sorted(route.methods)) if route.methods else 'ALL'} {route.path}" for route in crm_router.routes if isinstance(route, APIRoute)]
    logger.debug(f"Registered crm endpoints: {len(crm_routes)} routes")
    for route_path in crm_routes:
        logger.debug(f"  {route_path}")
except Exception as e:
    logger.error(f"Failed to include crm_router: {str(e)}\n{traceback.format_exc()}")
    raise

try:
    api_v1_router.include_router(pincode_router, prefix="/pincode", tags=["Pincode"])
    pincode_routes = [f"{', '.join(sorted(route.methods)) if route.methods else 'ALL'} /pincode{route.path}" for route in pincode_router.routes if isinstance(route, APIRoute)]
    logger.debug(f"Registered pincode endpoints: {len(pincode_routes)} routes")
    for route_path in pincode_routes:
        logger.debug(f"  {route_path}")
except Exception as e:
    logger.error(f"Failed to include pincode_router: {str(e)}\n{traceback.format_exc()}")
    raise

try:
    api_v1_router.include_router(user_router)
    user_routes = [f"{', '.join(sorted(route.methods)) if route.methods else 'ALL'} {route.path}" for route in user_router.routes if isinstance(route, APIRoute)]
    logger.debug(f"Registered user endpoints: {len(user_routes)} routes")
    for route_path in user_routes:
        logger.debug(f"  {route_path}")
except Exception as e:
    logger.error(f"Failed to include user_router: {str(e)}\n{traceback.format_exc()}")
    raise

try:
    api_v1_router.include_router(website_agent_router, tags=["Website Agent"])
    website_agent_routes = [f"{', '.join(sorted(route.methods)) if route.methods else 'ALL'} {route.path}" for route in website_agent_router.routes if isinstance(route, APIRoute)]
    logger.debug(f"Registered website_agent endpoints: {len(website_agent_routes)} routes")
    for route_path in website_agent_routes:
        logger.debug(f"  {route_path}")
except Exception as e:
    logger.error(f"Failed to include website_agent_router: {str(e)}\n{traceback.format_exc()}")
    raise