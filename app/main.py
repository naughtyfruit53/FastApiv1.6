# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.routing import APIRoute
from app.core.config import settings as config_settings
from app.core.database import create_tables, SessionLocal
from app.core.tenant import TenantMiddleware
from app.core.seed_super_admin import seed_super_admin
from app.api import users, companies, vendors, customers, products, reports, platform, settings, pincode, customer_analytics, notifications
from app.api.v1 import stock as v1_stock
from app.api.v1.vouchers import router as v1_vouchers_router  # Updated import
from app.api.routes import admin
import logging

# Configure logging at the top
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import enhanced v1 routers
from app.api.v1 import auth as v1_auth, admin as v1_admin, reset as v1_reset, app_users as v1_app_users
# Added missing v1 imports
from app.api.v1 import admin_setup as v1_admin_setup, login as v1_login, master_auth as v1_master_auth, otp as v1_otp, password as v1_password, user as v1_user
from app.api.v1 import pdf_extraction as v1_pdf_extraction
# Organizations router (modular version)
from app.api.v1.organizations import router as organizations_router

# Add imports for BOM and Manufacturing
from app.api.v1 import bom as v1_bom
from app.api.v1 import manufacturing as v1_manufacturing

# Add import for company branding
from app.api.v1 import company_branding as v1_company_branding

# Add import for SLA management
from app.api.v1 import sla as v1_sla

# Add import for dispatch management
from app.api.v1 import dispatch as v1_dispatch

# Add import for feedback and service closure workflow
from app.api.v1 import feedback as v1_feedback

# Add import for inventory management
from app.api.v1 import inventory as v1_inventory

# Add import for GST
from app.api.v1 import gst as v1_gst

# Add imports for new ERP modules
from app.api.v1 import erp as v1_erp
from app.api.v1 import procurement as v1_procurement
from app.api.v1 import tally as v1_tally
from app.api.v1 import warehouse as v1_warehouse

# Add import for RBAC
from app.api.v1 import rbac as v1_rbac

# Add import for service analytics
from app.api.v1 import service_analytics as v1_service_analytics

# Add imports for new Asset Management and Transport modules
from app.api.v1 import assets as v1_assets
from app.api.v1 import transport as v1_transport

# Log imports with try/except for error handling
try:
    from app.api import companies
    logger.info("Successfully imported companies_router")
except Exception as import_error:
    logger.error(f"Failed to import companies_router: {str(import_error)}")
    raise

try:
    from app.api import products
    logger.info("Successfully imported products_router")
except Exception as import_error:
    logger.error(f"Failed to import products_router: {str(import_error)}")
    raise

try:
    from app.api.v1 import stock as v1_stock
    logger.info("Successfully imported stock_router")
except Exception as import_error:
    logger.error(f"Failed to import stock_router: {str(import_error)}")
    raise

# Create FastAPI app
app = FastAPI(
    title=config_settings.PROJECT_NAME,
    version=config_settings.VERSION,
    description=config_settings.DESCRIPTION,
    openapi_url="/api/v1/openapi.json"
)

app.router.redirect_slashes = True

# Temporarily disable TenantMiddleware to test if it's causing the 404 (re-enable after testing)
# app.add_middleware(TenantMiddleware)

# Set up CORS for frontend integration
logger.info(f"Configuring CORS with allowed origins: {config_settings.BACKEND_CORS_ORIGINS}")
app.add_middleware(
    CORSMiddleware,
    allow_origins=config_settings.BACKEND_CORS_ORIGINS,  # Frontend URLs[](http://localhost:3000)
    allow_credentials=True,                               # Required for authentication cookies/headers
    allow_methods=["*"],                                  # Allow all HTTP methods (GET, POST, PUT, DELETE, OPTIONS, etc.)
    allow_headers=["*"],                                  # Allow all headers (Content-Type, Authorization, etc.)
)

# Debug CORS configuration on startup
@app.on_event("startup")
async def log_cors_config():
    """Log CORS configuration for debugging"""
    logger.info("=" * 50)
    logger.info("CORS Configuration:")
    logger.info(f"  Allowed Origins: {config_settings.BACKEND_CORS_ORIGINS}")
    logger.info(f"  Allow Credentials: True")
    logger.info(f"  Allow Methods: ['*'] (all)")
    logger.info(f"  Allow Headers: ['*'] (all)")
    logger.info("=" * 50)

# ------------------------------------------------------------------------------
# ENHANCED V1 API ROUTERS
# ------------------------------------------------------------------------------
app.include_router(
    v1_auth.router, 
    prefix="/api/v1/auth", 
    tags=["authentication-v1"]
)
logger.info("Auth router included successfully at prefix: /api/v1/auth")
app.include_router(
    v1_admin.router, 
    prefix="/api/v1/admin", 
    tags=["admin-v1"]
)
logger.info("Admin router included successfully at prefix: /api/v1/admin")
app.include_router(
    v1_reset.router, 
    prefix="/api/v1/reset", 
    tags=["reset-v1"]
)
logger.info("Reset router included successfully at prefix: /api/v1/reset")
app.include_router(
    v1_app_users.router,
    prefix="/api/v1/app-users",
    tags=["app-user-management"]
)
logger.info("App users router included successfully at prefix: /api/v1/app-users")

app.include_router(
    v1_admin_setup.router,
    prefix="/api/v1/admin-setup",
    tags=["admin-setup-v1"]
)
logger.info("Admin setup router included successfully at prefix: /api/v1/admin-setup")
app.include_router(
    v1_login.router,
    prefix="/api/v1/login",
    tags=["login-v1"]
)
logger.info("Login router included successfully at prefix: /api/v1/login")
app.include_router(
    v1_master_auth.router,
    prefix="/api/v1/master-auth",
    tags=["master-auth-v1"]
)
logger.info("Master auth router included successfully at prefix: /api/v1/master-auth")
app.include_router(
    v1_otp.router,
    prefix="/api/v1/otp",
    tags=["otp-v1"]
)
logger.info("OTP router included successfully at prefix: /api/v1/otp")
app.include_router(
    v1_password.router,
    prefix="/api/v1/password",
    tags=["password-v1"]
)
logger.info("Password router included successfully at prefix: /api/v1/password")
app.include_router(
    v1_user.router,
    prefix="/api/v1/user",
    tags=["v1-user"]
)
logger.info("User router included successfully at prefix: /api/v1/user")

# PDF Extraction API
app.include_router(
    v1_pdf_extraction.router,
    prefix="/api/v1/pdf-extraction",
    tags=["pdf-extraction"]
)
logger.info("PDF extraction router included successfully at prefix: /api/v1/pdf-extraction")

# Service CRM RBAC API
app.include_router(
    v1_rbac.router,
    prefix="/api/v1/rbac",
    tags=["service-crm-rbac"]
)
logger.info("Service CRM RBAC router included successfully at prefix: /api/v1/rbac")

# GST API
app.include_router(
    v1_gst.router,
    prefix="/api/v1/gst",
    tags=["gst"]
)
logger.info("GST router included successfully at prefix: /api/v1/gst")

# ------------------------------------------------------------------------------
# LEGACY API ROUTERS (business modules)
# ------------------------------------------------------------------------------
app.include_router(platform.router, prefix="/api/v1/platform", tags=["platform"])
logger.info("Platform router included successfully at prefix: /api/v1/platform")
app.include_router(organizations_router, prefix="/api/v1", tags=["organizations"])
logger.info("Organizations router included successfully at prefix: /api/v1")
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
logger.info("Users router included successfully at prefix: /api/v1/users")
app.include_router(admin.router, prefix="/api/admin", tags=["admin-legacy"])
logger.info("Admin legacy router included successfully at prefix: /api/admin")
app.include_router(companies.router, prefix="/api/v1/companies", tags=["companies"])
logger.info("Companies router included successfully at prefix: /api/v1/companies")
app.include_router(vendors.router, prefix="/api/v1/vendors", tags=["vendors"])
logger.info("Vendors router included successfully at prefix: /api/v1/vendors")
app.include_router(customers.router, prefix="/api/v1/customers", tags=["customers"])
logger.info("Customers router included successfully at prefix: /api/v1/customers")
app.include_router(products.router, prefix="/api/v1/products", tags=["products"])
logger.info("Products router included successfully at prefix: /api/v1/products")

# Company branding and PDF audit endpoints (static)
app.include_router(v1_company_branding.router, prefix="/api/v1/company", tags=["company-branding"])
logger.info("Company branding router included successfully at prefix: /api/v1/company")
app.include_router(v1_company_branding.router, prefix="/api/v1/audit", tags=["audit"])
logger.info("Audit router included successfully at prefix: /api/v1/audit")

app.include_router(v1_vouchers_router, prefix="/api/v1")  # Updated to v1 vouchers
logger.info("Vouchers router included successfully at prefix: /api/v1")
app.include_router(reports.router, prefix="/api/v1/reports", tags=["reports"])
logger.info("Reports router included successfully at prefix: /api/v1/reports")
app.include_router(settings.router, prefix="/api/v1/settings", tags=["settings"])
logger.info("Settings router included successfully at prefix: /api/v1/settings")
app.include_router(pincode.router, prefix="/api/v1/pincode", tags=["pincode"])
logger.info("Pincode router included successfully at prefix: /api/v1/pincode")

# Customer Analytics API
app.include_router(customer_analytics.router, prefix="/api/v1/analytics", tags=["customer-analytics"])
logger.info("Customer Analytics router included successfully at prefix: /api/v1/analytics")

# Notifications API for Service CRM
app.include_router(notifications.router, prefix="/api/v1/notifications", tags=["notifications"])
logger.info("Notifications router included successfully at prefix: /api/v1/notifications")

# Include static path routers BEFORE dynamic ones to prevent conflicts
app.include_router(v1_stock.router, prefix="/api/v1/stock", tags=["stock"])  # Static /stock paths
logger.info("Stock router included successfully at prefix: /api/v1/stock")

# Include SLA router
app.include_router(v1_sla.router, prefix="/api/v1/sla", tags=["sla"])
logger.info("SLA router included successfully at prefix: /api/v1/sla")

# Include dispatch router
app.include_router(v1_dispatch.router, prefix="/api/v1/dispatch", tags=["dispatch"])
logger.info("Dispatch router included successfully at prefix: /api/v1/dispatch")

# Include feedback and service closure router
app.include_router(v1_feedback.router, prefix="/api/v1/feedback", tags=["feedback-closure"])
logger.info("Feedback and service closure router included successfully at prefix: /api/v1/feedback")

# Include inventory management router
app.include_router(v1_inventory.router, prefix="/api/v1/inventory", tags=["inventory-management"])
logger.info("Inventory management router included successfully at prefix: /api/v1/inventory")

# Include service analytics router
app.include_router(v1_service_analytics.router, prefix="/api/v1/service-analytics", tags=["service-analytics"])
logger.info("Service Analytics router included successfully at prefix: /api/v1/service-analytics")

# Include new ERP module routers
app.include_router(v1_erp.router, prefix="/api/v1/erp", tags=["erp-core"])
logger.info("ERP Core router included successfully at prefix: /api/v1/erp")

app.include_router(v1_procurement.router, prefix="/api/v1/procurement", tags=["procurement"])
logger.info("Procurement router included successfully at prefix: /api/v1/procurement")

app.include_router(v1_tally.router, prefix="/api/v1/tally", tags=["tally-integration"])
logger.info("Tally Integration router included successfully at prefix: /api/v1/tally")

app.include_router(v1_warehouse.router, prefix="/api/v1/warehouse", tags=["warehouse-management"])
logger.info("Warehouse Management router included successfully at prefix: /api/v1/warehouse")

# Include Asset Management router
app.include_router(v1_assets.router, prefix="/api/v1/assets", tags=["asset-management"])
logger.info("Asset Management router included successfully at prefix: /api/v1/assets")

# Include Transport and Freight router
app.include_router(v1_transport.router, prefix="/api/v1/transport", tags=["transport-freight"])
logger.info("Transport and Freight router included successfully at prefix: /api/v1/transport")

# Include dynamic path routers LAST
app.include_router(v1_bom.router, prefix="/api/v1", tags=["bom"])  # Dynamic /{bom_id}
logger.info("BOM router included successfully at prefix: /api/v1")
app.include_router(v1_manufacturing.router, prefix="/api/v1", tags=["manufacturing"])  # Potential dynamic paths
logger.info("Manufacturing router included successfully at prefix: /api/v1")

@app.get("/routes")
def get_routes():
    """Temporary endpoint to list all registered routes for debugging 404 issues"""
    routes = []
    for route in app.routes:
        if isinstance(route, APIRoute):
            methods = ', '.join(sorted(route.methods)) if route.methods else 'ALL'
            routes.append(f"{methods} {route.path}")
    return {"routes": sorted(routes)}

@app.on_event("startup")
async def startup_event():
    """Initialize application: log CORS config, setup database, and seed super admin"""
    logger.info("Starting up TRITIQ ERP API...")
    try:
        create_tables()
        logger.info("Database tables created successfully")
        from app.core.seed_super_admin import check_database_schema_updated
        db = SessionLocal()
        try:
            if check_database_schema_updated(db):
                seed_super_admin(db)
                logger.info("Super admin seeding completed")
            else:
                logger.warning("Database schema is not updated. Run 'alembic upgrade head' to enable super admin seeding.")
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Failed to initialize application: {e}")
        raise

    logger.info("=" * 50)
    logger.info("Registered Routes (for debugging):")
    for route in app.routes:
        if isinstance(route, APIRoute):
            methods = ', '.join(sorted(route.methods)) if route.methods else 'ALL'
            logger.info(f"{methods} {route.path}")
    logger.info("=" * 50)

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down TRITIQ ERP API...")

@app.get("/")
async def root():
    return {
        "message": "Welcome to TRITIQ ERP API",
        "version": config_settings.VERSION,
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": config_settings.VERSION}

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("app/static/favicon.ico")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=config_settings.DEBUG
    )