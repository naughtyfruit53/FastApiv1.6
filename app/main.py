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

# Minimal routers to reduce memory usage, controlled by environment variable
def include_minimal_routers():
    from app.api.v1 import auth as v1_auth
    from app.api.v1 import health as v1_health
    from app.api import companies, vendors, customers, products

    routers = [
        (v1_auth.router, "/api/v1/auth", ["authentication-v1"]),
        (v1_health.router, "/api/v1", ["health"]),
        (companies.router, "/api/v1/companies", ["companies"]),
        (vendors.router, "/api/v1/vendors", ["vendors"]),
        (customers.router, "/api/v1/customers", ["customers"]),
        (products.router, "/api/v1/products", ["products"]),
    ]

    # Check environment variable for additional routers
    if os.getenv("ENABLE_EXTENDED_ROUTERS", "false").lower() == "true":
        from app.api.v1 import pdf_extraction as v1_pdf_extraction
        from app.api.v1 import pdf_generation as v1_pdf_generation
        from app.api.v1 import gst as v1_gst
        routers.extend([
            (v1_pdf_extraction.router, "/api/v1/pdf-extraction", ["pdf-extraction"]),
            (v1_pdf_generation.router, "/api/v1/pdf-generation", ["pdf-generation"]),
            (v1_gst.router, "/api/v1/gst", ["gst"]),
        ])

    for router, prefix, tags in routers:
        try:
            app.include_router(router, prefix=prefix, tags=tags)
            logger.info(f"Router included successfully at prefix: {prefix}")
        except Exception as e:
            logger.error(f"Failed to include router at prefix {prefix}: {str(e)}")
            raise

# Include routers on startup
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

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.mount("/uploads", StaticFiles(directory="Uploads"), name="uploads")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=config_settings.DEBUG
    )