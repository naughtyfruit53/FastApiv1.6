# app/main.py

import logging
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.routing import APIRoute
from fastapi.staticfiles import StaticFiles
from app.core.config import settings as config_settings
from app.core.database import create_tables, AsyncSessionLocal
from app.core.seed_super_admin import seed_super_admin

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=config_settings.PROJECT_NAME,
    version=config_settings.VERSION,
    description=config_settings.DESCRIPTION,
    openapi_url="/api/v1/openapi.json"
)

# Set up CORS
logger.info(f"Configuring CORS with allowed origins: {config_settings.BACKEND_CORS_ORIGINS}")
app.add_middleware(
    CORSMiddleware,
    allow_origins=config_settings.BACKEND_CORS_ORIGINS,
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
    logger.info(f"  Allowed Origins: {config_settings.BACKEND_CORS_ORIGINS}")
    logger.info(f"  Allow Credentials: True")
    logger.info(f"  Allow Methods: ['*'] (all)")
    logger.info(f"  Allow Headers: ['*'] (all)")
    logger.info("=" * 50)

# Minimal routers to reduce memory usage
def include_minimal_routers():
    routers = []
    
    # Import and include each router with error handling
    try:
        from app.api.v1 import auth as v1_auth
        routers.append((v1_auth.router, "/api/v1/auth", ["authentication-v1"]))
    except Exception as e:
        logger.error(f"Failed to import auth router: {str(e)}")
        raise
    
    try:
        from app.api.v1 import health as v1_health
        routers.append((v1_health.router, "/api/v1", ["health"]))
    except Exception as e:
        logger.error(f"Failed to import health router: {str(e)}")
        raise
    
    try:
        from app.api.v1 import user as v1_user
        routers.append((v1_user.router, "/api/v1/users", ["users"]))
    except Exception as e:
        logger.error(f"Failed to import user router: {str(e)}")
        raise
    
    try:
        from app.api.v1.organizations import router as organizations_router
        routers.append((organizations_router, "/api/v1/organizations", ["organizations"]))
    except Exception as e:
        logger.error(f"Failed to import organizations router: {str(e)}")
        raise
    
    try:
        from app.api import companies
        routers.append((companies.router, "/api/v1/companies", ["companies"]))
    except Exception as e:
        logger.error(f"Failed to import companies router: {str(e)}")
        raise
    
    try:
        from app.api import vendors
        routers.append((vendors.router, "/api/v1/vendors", ["vendors"]))
    except Exception as e:
        logger.error(f"Failed to import vendors router: {str(e)}")
        raise
    
    try:
        from app.api import customers
        routers.append((customers.router, "/api/v1/customers", ["customers"]))
    except Exception as e:
        logger.error(f"Failed to import customers router: {str(e)}")
        raise
    
    try:
        from app.api import products
        routers.append((products.router, "/api/v1/products", ["products"]))
    except Exception as e:
        logger.error(f"Failed to import products router: {str(e)}")
        raise
    
    try:
        from app.api.v1 import rbac as v1_rbac
        routers.append((v1_rbac.router, "/api/v1/rbac", ["rbac"]))
    except Exception as e:
        logger.error(f"Failed to import rbac router: {str(e)}")
        raise
    
    try:
        from app.api.v1 import inventory as v1_inventory
        routers.append((v1_inventory.router, "/api/v1/inventory", ["inventory"]))
    except Exception as e:
        logger.error(f"Failed to import inventory router: {str(e)}")
        raise
    
    try:
        from app.api.v1 import stock as v1_stock
        routers.append((v1_stock.router, "/api/v1/stock", ["stock"]))
    except Exception as e:
        logger.error(f"Failed to import stock router: {str(e)}")
        raise
    
    try:
        from app.api.v1.vouchers import router as vouchers_router
        routers.append((vouchers_router, "/api/v1", ["vouchers"]))
    except Exception as e:
        logger.error(f"Failed to import vouchers router: {str(e)}")
        raise
    
    try:
        from app.api.v1 import reports as v1_reports
        routers.append((v1_reports.router, "/api/v1", ["reports"]))
    except Exception as e:
        logger.error(f"Failed to import reports router: {str(e)}")
        raise

    # Conditionally include extended routers
    if os.getenv("ENABLE_EXTENDED_ROUTERS", "false").lower() == "true":
        try:
            from app.api.v1 import pdf_extraction as v1_pdf_extraction
            routers.append((v1_pdf_extraction.router, "/api/v1/pdf-extraction", ["pdf-extraction"]))
        except Exception as e:
            logger.error(f"Failed to import pdf_extraction router: {str(e)}")
            raise
        try:
            from app.api.v1 import pdf_generation as v1_pdf_generation
            routers.append((v1_pdf_generation.router, "/api/v1/pdf-generation", ["pdf-generation"]))
        except Exception as e:
            logger.error(f"Failed to import pdf_generation router: {str(e)}")
            raise
        try:
            from app.api.v1 import gst as v1_gst
            routers.append((v1_gst.router, "/api/v1/gst", ["gst"]))
        except Exception as e:
            logger.error(f"Failed to import gst router: {str(e)}")
            raise

    # Conditionally include AI analytics router
    if os.getenv("ENABLE_AI_ANALYTICS", "false").lower() == "true":
        try:
            from app.api.v1 import ai_analytics as v1_ai_analytics
            routers.append((v1_ai_analytics.router, "/api/v1/ai-analytics", ["ai-analytics"]))
        except Exception as e:
            logger.error(f"Failed to import ai_analytics router: {str(e)}")
            raise

    # Include v1 API router (includes chart_of_accounts, erp, etc.)
    try:
        from app.api.v1 import api_v1_router
        routers.append((api_v1_router, "/api/v1", ["v1-api"]))
    except Exception as e:
        logger.error(f"Failed to import v1 API router: {str(e)}")
        raise

    for router, prefix, tags in routers:
        try:
            app.include_router(router, prefix=prefix, tags=tags)
            logger.info(f"Router included successfully at prefix: {prefix}")
        except Exception as e:
            logger.error(f"Failed to include router at prefix {prefix}: {str(e)}")
            raise

# Debug middleware for logging request headers
@app.middleware("http")
async def log_request_headers(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url}")
    logger.info(f"Headers: {dict(request.headers)}")
    response = await call_next(request)
    return response

# Include routers and mounts on startup
@app.on_event("startup")
async def startup_event():
    """Initialize application: log CORS config, setup database, and seed super admin"""
    logger.info("Starting up TritIQ Business Suite API...")
    try:
        await create_tables()
        logger.info("Database tables created successfully")
        from app.core.seed_super_admin import check_database_schema_updated
        db = AsyncSessionLocal()
        try:
            if await check_database_schema_updated(db):
                await seed_super_admin(db)
                logger.info("Super admin seeding completed")
            else:
                logger.warning("Database schema is not updated. Run 'alembic upgrade head' to enable super admin seeding.")
        finally:
            await db.close()
        include_minimal_routers()
        # Conditionally mount static directories
        if os.path.exists("app/static"):
            app.mount("/static", StaticFiles(directory="app/static"), name="static")
            logger.info("Mounted /static directory")
        if os.path.exists("Uploads"):
            app.mount("/Uploads", StaticFiles(directory="Uploads"), name="uploads")
            logger.info("Mounted /Uploads directory")
    except Exception as e:
        logger.error(f"Failed to initialize application: {e}")
        raise

    logger.info("=" * 50)
    logger.info("Registered Routes (for debugging):")
    critical_routes = ["/api/v1/erp/bank-accounts", "/api/v1/chart-of-accounts", "/api/v1/reports/sales-report", "/api/v1/reports/dashboard-stats"]
    for route in app.routes:
        if isinstance(route, APIRoute):
            methods = ', '.join(sorted(route.methods)) if route.methods else 'ALL'
            route_path = route.path
            logger.info(f"{methods} {route_path}")
            if route_path in critical_routes:
                critical_routes.remove(route_path)
    if critical_routes:
        logger.warning(f"Critical routes not registered: {critical_routes}")
    logger.info("=" * 50)

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down TritIQ Business Suite API...")

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