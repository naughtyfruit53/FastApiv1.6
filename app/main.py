# app/main.py

import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.routing import APIRoute
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from app.core.config import settings as config_settings
from app.core.database import create_tables, AsyncSessionLocal
from app.core.seed_super_admin import seed_super_admin
from app.db.session import SessionLocal
from sqlalchemy import select, text
from sqlalchemy.exc import ProgrammingError
from app.models.entitlement_models import *  # Import to register entitlement models
from app.services.entitlement_service import EntitlementService  # Import for seeding
from app.models.user_models import Organization  # For org loop

logger = logging.getLogger(__name__)

# ForceCORSMiddleware: Inject CORS headers on ALL responses (including 500s and exceptions)
class ForceCORSMiddleware(BaseHTTPMiddleware):
    """
    Middleware that ensures CORS headers are present on all responses,
    including error responses (4xx, 5xx) that might bypass standard CORS middleware.
    """
    def __init__(self, app: ASGIApp, allowed_origins: list):
        super().__init__(app)
        self.allowed_origins = allowed_origins
    
    async def dispatch(self, request: Request, call_next):
        origin = request.headers.get("origin")

        # Handle OPTIONS preflight requests early to avoid route dependencies
        if request.method == "OPTIONS":
            if origin and origin in self.allowed_origins:
                headers = {
                    "Access-Control-Allow-Origin": origin,
                    "Access-Control-Allow-Methods": request.headers.get("access-control-request-method", "*"),
                    "Access-Control-Allow-Headers": request.headers.get("access-control-request-headers", "*"),
                    "Access-Control-Allow-Credentials": "true",
                    "Access-Control-Max-Age": "86400",  # Cache preflight for 24 hours
                    "Vary": "Origin",
                }
                return JSONResponse(status_code=200, content={}, headers=headers)
        
        # Process the request
        try:
            response = await call_next(request)
        except Exception as exc:
            # If an unhandled exception occurs, create an error response with CORS headers
            logger.error(f"Unhandled exception in request: {exc}", exc_info=True)
            response = JSONResponse(
                status_code=500,
                content={"detail": "Internal server error"}
            )
        
        # Add CORS headers if origin is in allowed list
        if origin and origin in self.allowed_origins:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Methods"] = "*"
            response.headers["Access-Control-Allow-Headers"] = "*"
            response.headers["Vary"] = "Origin"
        
        return response

# Custom APIRouter to disable slash redirection
from fastapi.routing import APIRouter as FastAPIRouter

class APIRouter(FastAPIRouter):
    def add_api_route(self, path: str, *args, **kwargs):
        # Add without trailing slash
        if path.endswith("/"):
            non_slash_path = path[:-1]
            super().add_api_route(non_slash_path, *args, **kwargs)
            # Add redirect from slash to non-slash if needed
        else:
            super().add_api_route(path, *args, **kwargs)
            slash_path = path + "/"
            # But don't add automatic redirect

# Initialize default permissions asynchronously
async def init_default_permissions(background_tasks: BackgroundTasks):
    from app.services.rbac import RBACService  # Lazy import to avoid circular import
    async with AsyncSessionLocal() as db:
        try:
            rbac = RBACService(db)
            await rbac.initialize_default_permissions()
            logger.info("Default permissions initialized")
        except Exception as e:
            logger.error(f"Error initializing default permissions: {str(e)}")

# Initialize roles and assign to org_admins for existing organizations asynchronously
async def init_org_roles(background_tasks: BackgroundTasks):
    from app.services.rbac import RBACService  # Lazy import to avoid circular import
    from app.models.user_models import User
    from app.models.rbac_models import UserServiceRole, ServiceRole
    from app.models.user_models import Organization  # Corrected import path
    async with AsyncSessionLocal() as db:
        try:
            # Check if user_service_roles table exists
            query = text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'user_service_roles')")
            result = await db.execute(query)
            table_exists = result.scalar()
            if not table_exists:
                logger.warning("user_service_roles table not found, skipping role initialization")
                return

            rbac = RBACService(db)
            orgs = (await db.execute(select(Organization))).scalars().all()
            for org in orgs:
                roles = await rbac.get_roles(org.id)
                if not roles:
                    await rbac.initialize_default_roles(org.id)
                    logger.info(f"Initialized default roles for organization {org.id}: {org.name}")
                else:
                    logger.debug(f"Roles already exist for organization {org.id}")
                
                # Assign 'admin' role to org_admins if not assigned
                admin_role = (await db.execute(select(ServiceRole).filter_by(organization_id=org.id, name="admin"))).scalars().first()
                if admin_role:
                    org_admins = (await db.execute(select(User).filter_by(organization_id=org.id, role="org_admin"))).scalars().all()
                    for admin in org_admins:
                        existing = (await db.execute(select(UserServiceRole).filter_by(user_id=admin.id, role_id=admin_role.id))).scalars().first()
                        if not existing:
                            assignment = UserServiceRole(
                                user_id=admin.id, 
                                role_id=admin_role.id, 
                                organization_id=org.id,
                                is_active=True
                            )
                            db.add(assignment)
                            logger.info(f"Assigned admin role to user {admin.email} in org {org.id}")
                    await db.commit()
        except ProgrammingError as e:
            logger.error(f"Database error during role initialization: {str(e)} - skipping role init")
            await db.rollback()
        except Exception as e:
            logger.error(f"Error initializing organization roles: {str(e)} - skipping role init")
            await db.rollback()

# Backfill default enabled_modules for organizations that have missing or empty modules
async def init_org_modules(background_tasks: BackgroundTasks):
    from app.models.user_models import Organization
    from app.core.modules_registry import get_default_enabled_modules
    async with AsyncSessionLocal() as db:
        try:
            orgs = (await db.execute(select(Organization))).scalars().all()
            for org in orgs:
                if not org.enabled_modules or len(org.enabled_modules) == 0:
                    org.enabled_modules = get_default_enabled_modules()
                    logger.info(f"Backfilled default enabled_modules for organization {org.id}: {org.name}")
            await db.commit()
        except Exception as e:
            logger.error(f"Error backfilling organization modules: {str(e)}")
            await db.rollback()

# Seed all modules and sync enabled_modules on startup
async def seed_and_sync_entitlements(background_tasks: BackgroundTasks):
    async with AsyncSessionLocal() as db:
        try:
            service = EntitlementService(db)
            created = await service.seed_all_modules()
            logger.info(f"Seeded {created} modules/submodules on startup")
            
            orgs = (await db.execute(select(Organization))).scalars().all()
            for org in orgs:
                synced = await service.sync_enabled_modules(org.id)
                logger.info(f"Synced enabled_modules for org {org.id} on startup: {synced}")
        except Exception as e:
            logger.error(f"Error during startup seeding/sync: {str(e)}")
            await db.rollback()

# Auto-seed baseline data on first boot (idempotent)
async def auto_seed_baseline_data(background_tasks: BackgroundTasks):
    """
    Automatically seed baseline data if database is empty.
    This runs on application startup and is idempotent.
    """
    from app.models.entitlement_models import Module
    from app.models.rbac_models import ServicePermission
    from app.models.organization_settings import VoucherFormatTemplate
    
    async with AsyncSessionLocal() as db:
        try:
            # Check if baseline data exists
            needs_seeding = False
            
            # Check for super admin
            result = await db.execute(select(User).where(User.is_super_admin == True).limit(1))
            if not result.scalar_one_or_none():
                needs_seeding = True
            
            # Check for modules
            if not needs_seeding:
                result = await db.execute(select(Module).limit(1))
                if not result.scalar_one_or_none():
                    needs_seeding = True
            
            # Check for RBAC permissions
            if not needs_seeding:
                result = await db.execute(select(ServicePermission).limit(1))
                if not result.scalar_one_or_none():
                    needs_seeding = True
            
            # Check for voucher templates
            if not needs_seeding:
                result = await db.execute(
                    select(VoucherFormatTemplate).where(
                        VoucherFormatTemplate.is_system_template == True
                    ).limit(1)
                )
                if not result.scalar_one_or_none():
                    needs_seeding = True
            
            if needs_seeding:
                logger.info("=" * 60)
                logger.info("Baseline data not found - starting auto-seed")
                logger.info("=" * 60)
                
                # Import and run the unified seeding script
                import sys
                from pathlib import Path
                
                # Add scripts directory to path
                scripts_dir = Path(__file__).parent.parent / "scripts"
                sys.path.insert(0, str(scripts_dir))
                
                try:
                    from scripts.seed_all import run_seed_all
                    await run_seed_all(skip_check=True)
                    logger.info("✓ Auto-seed completed successfully")
                except ImportError:
                    logger.warning("Could not import seed_all script - skipping auto-seed")
                except Exception as seed_error:
                    logger.error(f"Error during auto-seed: {seed_error}")
                    # Don't raise - allow app to start even if seeding fails
            else:
                logger.info("Baseline data exists - skipping auto-seed")
                
        except Exception as e:
            logger.error(f"Error checking for baseline data: {str(e)}")
            # Don't raise - allow app to start even if check fails

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        await create_tables()
        logger.info("Database tables created successfully")
    except ProgrammingError as e:
        logger.warning(f"Some tables or indexes already exist, skipping creation: {str(e)}")
    except Exception as e:
        logger.error(f"Failed to create database tables: {str(e)}")
        raise
    from app.core.seed_super_admin import check_database_schema_updated
    async with AsyncSessionLocal() as db:
        if await check_database_schema_updated(db):
            await seed_super_admin(db)
            logger.info("Super admin seeding completed")
        else:
            logger.warning("Database schema is not updated. Run 'alembic upgrade head' to enable super admin seeding.")
    include_minimal_routers()
    # Conditionally mount static directories
    if os.path.exists("app/static"):
        app.mount("/static", StaticFiles(directory="app/static"), name="static")
        logger.info("Mounted /static directory")
    if os.path.exists("uploads"):
        app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
        logger.info("Mounted /uploads directory")
    
    # Schedule non-essential inits as background tasks to speed up startup
    background_tasks = BackgroundTasks()
    background_tasks.add_task(auto_seed_baseline_data, background_tasks)  # Auto-seed baseline data if needed
    background_tasks.add_task(init_default_permissions, background_tasks)
    background_tasks.add_task(init_org_roles, background_tasks)
    background_tasks.add_task(init_org_modules, background_tasks)
    background_tasks.add_task(seed_and_sync_entitlements, background_tasks)  # New: Seed and sync entitlements
    
    yield
    # Shutdown

# Create FastAPI app
app = FastAPI(
    title=config_settings.PROJECT_NAME,
    version=config_settings.VERSION,
    description=config_settings.DESCRIPTION,
    openapi_url="/api/v1/openapi.json",
    lifespan=lifespan
)

# Set up CORS with explicit origins
origins = [
    "https://naughtyfruit.in",
    "https://www.naughtyfruit.in",
    "http://localhost:3000",
    "http://localhost",
    "http://127.0.0.1:3000",
    *config_settings.BACKEND_CORS_ORIGINS  # Keep existing if any
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add ForceCORSMiddleware to ensure CORS headers on ALL responses (including errors)
app.add_middleware(ForceCORSMiddleware, allowed_origins=origins)

# Global exception handler to ensure JSON error responses include CORS headers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler that ensures all unhandled exceptions
    return JSON responses with proper CORS headers.
    """
    logger.error(f"Unhandled exception in {request.method} {request.url}: {exc}", exc_info=True)
    
    origin = request.headers.get("origin")
    headers = {}
    
    # Add CORS headers if origin is in allowed list
    if origin and origin in origins:
        headers = {
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
            "Vary": "Origin",
        }
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error": str(exc) if config_settings.DEBUG else "An unexpected error occurred"
        },
        headers=headers
    )

# Debug CORS configuration on startup
@app.on_event("startup")
async def log_cors_config():
    """Log CORS configuration for debugging"""
    logger.info("=" * 50)
    logger.info("CORS Configuration:")
    logger.info(f"  Allowed Origins: {origins}")
    logger.info(f"  Allow Credentials: True")
    logger.info(f"  Allow Methods: [\"*\"] (all)")
    logger.info(f"  Allow Headers: [\"*\"] (all)")
    logger.info("=" * 50)

# Minimal routers to reduce memory usage
def include_minimal_routers():
    routers = []
    
    # Import and include each router with error handling (log but don't raise for optional)
    try:
        from app.api.v1 import auth as v1_auth
        routers.append((v1_auth.router, "/api/v1/auth", ["authentication-v1"]))
    except Exception as e:
        logger.error(f"Failed to import auth router: {str(e)}")
        raise  # Core, so raise
    
    try:
        from app.api.v1 import password as v1_password
        routers.append((v1_password.router, "/api/v1/password", ["password"]))
    except Exception as e:
        logger.error(f"Failed to import password router: {str(e)}")
        raise  # Core, so raise
    
    try:
        from app.api.v1 import health as v1_health
        routers.append((v1_health.router, "/api/v1", ["health"]))
    except Exception as e:
        logger.error(f"Failed to import health router: {str(e)}")
        raise  # Core
    
    try:
        from app.api.v1 import user as v1_user
        routers.append((v1_user.router, "/api/v1/users", ["users"]))
    except Exception as e:
        logger.error(f"Failed to import user router: {str(e)}")
        raise  # Core
    
    try:
        from app.api.v1 import api_v1_router, register_subrouters
        register_subrouters()
        routers.append((api_v1_router, "/api/v1", ["v1-api"]))
    except Exception as e:
        logger.error(f"Failed to import v1 API router: {str(e)}")
        raise  # Core
    
    try:
        from app.api.v1 import rbac as v1_rbac
        routers.append((v1_rbac.router, "/api/v1/rbac", ["rbac"]))
    except Exception as e:
        logger.error(f"Failed to import rbac router: {str(e)}")
        raise  # Core
    
    try:
        from app.api.v1 import debug as v1_debug
        routers.append((v1_debug.router, "/api/v1/debug", ["debug"]))
        logger.info("Debug router included for RBAC troubleshooting")
    except Exception as e:
        logger.warning(f"Failed to import debug router: {str(e)}")  # Optional, warn only
    
    try:
        from app.api.v1.organizations import router as organizations_router
        routers.append((organizations_router, "/api/v1/organizations", ["organizations"]))
    except Exception as e:
        logger.error(f"Failed to import organizations router: {str(e)}")
        raise  # Core
    
    try:
        from app.api.v1.companies import router as companies_router
        routers.append((companies_router, "/api/v1/companies", ["companies"]))
    except Exception as e:
        logger.error(f"Failed to import companies router: {str(e)}")
    
    try:
        from app.api.v1.vendors import router as vendors_router
        routers.append((vendors_router, "/api/v1/vendors", ["vendors"]))
    except Exception as e:
        logger.error(f"Failed to import vendors router: {str(e)}")
    
    try:
        from app.api.v1.customers import router as customers_router
        routers.append((customers_router, "/api/v1/customers", ["customers"]))
    except Exception as e:
        logger.error(f"Failed to import customers router: {str(e)}")
    
    try:
        from app.api.v1 import inventory as v1_inventory
        routers.append((v1_inventory.router, "/api/v1/inventory", ["inventory"]))
    except Exception as e:
        logger.error(f"Failed to import inventory router: {str(e)}")
    
    try:
        from app.api.v1 import stock as v1_stock
        routers.append((v1_stock.router, "/api/v1/stock", ["stock"]))
    except Exception as e:
        logger.error(f"Failed to import stock router: {str(e)}")
    
    try:
        from app.api.routes import websocket as websocket_routes
        routers.append((websocket_routes.router, "/api", ["websocket"]))
        logger.info("WebSocket routes included for real-time collaboration")
    except Exception as e:
        logger.warning(f"Failed to import websocket router: {str(e)}")
        # Don't raise - WebSocket is optional

    # Conditionally include extended routers
    if os.getenv("ENABLE_EXTENDED_ROUTERS", "false").lower() == "true":
        try:
            from app.api.v1 import pdf_extraction as v1_pdf_extraction
            routers.append((v1_pdf_extraction.router, "/api/v1/pdf-extraction", ["pdf-extraction"]))
        except Exception as e:
            logger.warning(f"Failed to import pdf_extraction router: {str(e)}")  # Optional, warn only
        try:
            from app.api.v1 import gst as v1_gst
            routers.append((v1_gst.router, "/api/v1/gst", ["gst"]))
        except Exception as e:
            logger.warning(f"Failed to import gst router: {str(e)}")

    # Always include pdf_generation router unconditionally
    try:
        from app.api.v1 import pdf_generation as v1_pdf_generation
        routers.append((v1_pdf_generation.router, "/api/v1", ["pdf-generation"]))
        logger.info("PDF generation router included unconditionally")
    except Exception as e:
        logger.error(f"Failed to import pdf_generation router: {str(e)}")
        raise  # Make it core now

    # Always include voucher_format_templates router unconditionally
    try:
        from app.api.v1.voucher_format_templates import router as voucher_templates_router
        routers.append((voucher_templates_router, "/api/v1", ["voucher-templates"]))
        logger.info("Voucher format templates router included unconditionally")
    except Exception as e:
        logger.error(f"Failed to import voucher_format_templates router: {str(e)}")
        raise  # Make it core now

    # Conditionally include AI analytics router
    if os.getenv("ENABLE_AI_ANALYTICS", "false").lower() == "true":
        try:
            from app.api.v1 import ai_analytics as v1_ai_analytics
            routers.append((v1_ai_analytics.router, "/api/v1/ai-analytics", ["ai-analytics"]))
        except Exception as e:
            logger.warning(f"Failed to import ai_analytics router: {str(e)}")

    for router, prefix, tags in routers:
        try:
            app.include_router(router, prefix=prefix, tags=tags)
            logger.info(f"Router included successfully at prefix: {prefix}")
        except Exception as e:
            logger.warning(f"Failed to include router at prefix {prefix}: {str(e)}")  # Warn but continue

@app.get("/")
async def root():
    return {
        "message": "Welcome to TritIQ BOS API",
        "version": config_settings.VERSION,
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": config_settings.VERSION}

@app.get("/routes")
def get_routes():
    """Temporary endpoint to list all registered routes for debugging 404 issues"""
    routes = []
    for route in app.routes:
        if isinstance(route, APIRoute):
            methods = ', '.join(sorted(route.methods)) if route.methods else 'ALL'
            routes.append(f"{methods} {route.path}")
    return {"routes": sorted(routes)}

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