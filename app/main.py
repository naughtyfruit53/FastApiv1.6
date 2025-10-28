# app/main.py

import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.routing import APIRoute
from fastapi.staticfiles import StaticFiles
from app.core.config import settings as config_settings
from app.core.database import create_tables, AsyncSessionLocal
from app.core.seed_super_admin import seed_super_admin
from app.db.session import SessionLocal
from sqlalchemy import select, text
from sqlalchemy.exc import ProgrammingError

logger = logging.getLogger(__name__)

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
    if os.path.exists("Uploads"):
        app.mount("/Uploads", StaticFiles(directory="Uploads"), name="uploads")
        logger.info("Mounted /Uploads directory")
    
    # Schedule non-essential inits as background tasks to speed up startup
    background_tasks = BackgroundTasks()
    background_tasks.add_task(init_default_permissions, background_tasks)
    background_tasks.add_task(init_org_roles, background_tasks)
    
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
        from app.api.v1.organizations import router as organizations_router
        routers.append((organizations_router, "/api/v1/organizations", ["organizations"]))
    except Exception as e:
        logger.error(f"Failed to import organizations router: {str(e)}")
        raise  # Core
    
    try:
        from app.api.companies import router as companies_router
        routers.append((companies_router, "/api/v1/companies", ["companies"]))
    except Exception as e:
        logger.error(f"Failed to import companies router: {str(e)}")
    
    try:
        from app.api.vendors import router as vendors_router
        routers.append((vendors_router, "/api/v1/vendors", ["vendors"]))
    except Exception as e:
        logger.error(f"Failed to import vendors router: {str(e)}")
    
    try:
        from app.api.customers import router as customers_router
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

# Debug middleware for logging request headers
@app.middleware("http")
async def log_request_headers(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url}")
    logger.info(f"Headers: {dict(request.headers)}")
    response = await call_next(request)
    return response

@app.get("/")
async def root():
    return {
        "message": "Welcome to TritIQ Business Suite API",
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