# app/main.py

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.routing import APIRoute
from fastapi.staticfiles import StaticFiles

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from sqlalchemy import select, text, func
from sqlalchemy.exc import ProgrammingError

from app.core.config import settings as config_settings
from app.core.database import create_tables, AsyncSessionLocal, async_engine
from app.core.seed_super_admin import seed_super_admin
from app.db.session import SessionLocal

from app.models.entitlement_models import *  # register entitlement models
from app.services.entitlement_service import EntitlementService
from app.models.user_models import Organization  # For org loop

logger = logging.getLogger(__name__)


# --- Middleware for HTTPS / proxy handling ------------------------------------


class ForwardedSchemeMiddleware(BaseHTTPMiddleware):
    """
    Minimal proxy-aware middleware.

    It sets request.scope["scheme"] from X-Forwarded-Proto so that FastAPI /
    Starlette generate redirects (e.g. /path -> /path/) with the correct
    https:// scheme when behind a reverse proxy (Railway).
    """

    async def dispatch(self, request: Request, call_next):
        proto = request.headers.get("x-forwarded-proto")
        if proto:
            request.scope["scheme"] = proto.lower()
        return await call_next(request)


class HTTPSRedirectMiddleware(BaseHTTPMiddleware):
    """
    Redirect plain HTTP traffic to HTTPS based on X-Forwarded-Proto header.
    """

    async def dispatch(self, request: Request, call_next):
        proto = request.headers.get("x-forwarded-proto", "https").lower()
        if proto == "http":
            url = request.url.replace(scheme="https")
            logger.debug(f"Redirecting HTTP to HTTPS: {request.url} -> {url}")
            return RedirectResponse(url)
        response = await call_next(request)
        return response


class ForceCORSMiddleware(BaseHTTPMiddleware):
    """
    Ensure CORS headers are present on all responses, including error responses.
    """

    def __init__(self, app: ASGIApp, allowed_origins: list):
        super().__init__(app)
        self.allowed_origins = allowed_origins

    async def dispatch(self, request: Request, call_next):
        origin = request.headers.get("origin")

        # Handle OPTIONS preflight early
        if request.method == "OPTIONS":
            if origin and origin in self.allowed_origins:
                headers = {
                    "Access-Control-Allow-Origin": origin,
                    "Access-Control-Allow-Methods": request.headers.get(
                        "access-control-request-method", "*"
                    ),
                    "Access-Control-Allow-Headers": request.headers.get(
                        "access-control-request-headers", "*"
                    ),
                    "Access-Control-Allow-Credentials": "true",
                    "Access-Control-Max-Age": "86400",
                    "Vary": "Origin",
                }
                return JSONResponse(status_code=200, content={}, headers=headers)

        try:
            response = await call_next(request)
        except Exception as exc:
            logger.error(f"Unhandled exception in request: {exc}", exc_info=True)
            response = JSONResponse(
                status_code=500, content={"detail": "Internal server error"}
            )

        if origin and origin in self.allowed_origins:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Methods"] = "*"
            response.headers["Access-Control-Allow-Headers"] = "*"
            response.headers["Vary"] = "Origin"

        return response


# --- Optional custom APIRouter (as in your original code) ---------------------

from fastapi.routing import APIRouter as FastAPIRouter


class APIRouter(FastAPIRouter):
    def add_api_route(self, path: str, *args, **kwargs):
        if path.endswith("/"):
            non_slash_path = path[:-1]
            super().add_api_route(non_slash_path, *args, **kwargs)
        else:
            super().add_api_route(path, *args, **kwargs)
            # No auto redirect for trailing slash


# --- Startup tasks (same as your previous main.py) ----------------------------


async def init_default_permissions(background_tasks: BackgroundTasks):
    from app.services.rbac import RBACService

    async with AsyncSessionLocal() as db:
        try:
            rbac = RBACService(db)
            await rbac.initialize_initialize_default_permissions()
            logger.info("Default permissions initialized")
        except Exception as e:
            logger.error(f"Error initializing default permissions: {str(e)}")


async def init_org_roles(background_tasks: BackgroundTasks):
    from app.services.rbac import RBACService
    from app.models.user_models import User
    from app.models.rbac_models import UserServiceRole, ServiceRole

    async with AsyncSessionLocal() as db:
        try:
            # Check if user_service_roles table exists
            query = text(
                "SELECT EXISTS (SELECT FROM information_schema.tables "
                "WHERE table_name = 'user_service_roles')"
            )
            result = await db.execute(query)
            table_exists = result.scalar()
            if not table_exists:
                logger.warning(
                    "user_service_roles table not found, skipping role initialization"
                )
                return

            rbac = RBACService(db)
            orgs = (await db.execute(select(Organization))).scalars().all()
            for org in orgs:
                roles = await rbac.get_roles(org.id)
                if not roles:
                    await rbac.initialize_default_roles(org.id)
                    logger.info(
                        f"Initialized default roles for organization {org.id}: {org.name}"
                    )
                else:
                    logger.debug(f"Roles already exist for organization {org.id}")

                admin_role = (
                    (
                        await db.execute(
                            select(ServiceRole).filter_by(
                                organization_id=org.id, name="admin"
                            )
                        )
                    )
                    .scalars()
                    .first()
                )
                if admin_role:
                    org_admins = (
                        (
                            await db.execute(
                                select(User).filter_by(
                                    organization_id=org.id, role="org_admin"
                                )
                            )
                        )
                        .scalars()
                        .all()
                    )
                    for admin in org_admins:
                        existing = (
                            (
                                await db.execute(
                                    select(UserServiceRole).filter_by(
                                        user_id=admin.id, role_id=admin_role.id
                                    )
                                )
                            )
                            .scalars()
                            .first()
                        )
                        if not existing:
                            assignment = UserServiceRole(
                                user_id=admin.id,
                                role_id=admin_role.id,
                                organization_id=org.id,
                                is_active=True,
                            )
                            db.add(assignment)
                            logger.info(
                                f"Assigned admin role to user {admin.email} in org {org.id}"
                            )
                    await db.commit()
        except ProgrammingError as e:
            logger.error(
                f"Database error during role initialization: {str(e)} - skipping role init"
            )
            await db.rollback()
        except Exception as e:
            logger.error(
                f"Error initializing organization roles: {str(e)} - skipping role init"
            )
            await db.rollback()


async def init_org_modules(background_tasks: BackgroundTasks):
    from app.models.user_models import Organization
    from app.core.modules_registry import get_default_enabled_modules

    async with AsyncSessionLocal() as db:
        try:
            orgs = (await db.execute(select(Organization))).scalars().all()
            for org in orgs:
                if not org.enabled_modules or len(org.enabled_modules) == 0:
                    org.enabled_modules = get_default_enabled_modules()
                    logger.info(
                        f"Backfilled default enabled_modules for organization {org.id}: {org.name}"
                    )
            await db.commit()
        except Exception as e:
            logger.error(f"Error backfilling organization modules: {str(e)}")
            await db.rollback()


async def seed_and_sync_entitlements(background_tasks: BackgroundTasks):
    async with AsyncSessionLocal() as db:
        try:
            service = EntitlementService(db)
            created = await service.seed_all_modules()
            logger.info(f"Seeded {created} modules/submodules on startup")

            orgs = (await db.execute(select(Organization))).scalars().all()
            for org in orgs:
                synced = await service.sync_enabled_modules(org.id)
                logger.info(
                    f"Synced enabled_modules for org {org.id} on startup: {synced}"
                )
        except Exception as e:
            logger.error(f"Error during startup seeding/sync: {str(e)}")
            await db.rollback()


async def auto_seed_baseline_data(background_tasks: BackgroundTasks):
    from app.models.entitlement_models import Module
    from app.models.rbac_models import ServicePermission
    from app.models.organization_settings import VoucherFormatTemplate
    from app.models.user_models import User

    async with AsyncSessionLocal() as db:
        try:
            needs_seeding = False

            # Check for super admin
            result = await db.execute(
                select(User).where(User.is_super_admin == True).limit(1)
            )
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
                    select(VoucherFormatTemplate)
                    .where(VoucherFormatTemplate.is_system_template == True)
                    .limit(1)
                )
                if not result.scalar_one_or_none():
                    needs_seeding = True

            if needs_seeding:
                logger.info("=" * 60)
                logger.info("Baseline data not found - starting auto-seed")
                logger.info("=" * 60)

                import sys
                from pathlib import Path

                scripts_dir = Path(__file__).parent.parent / "scripts"
                sys.path.insert(0, str(scripts_dir))

                try:
                    from scripts.seed_all import run_seed_all

                    await run_seed_all(skip_check=True)
                    logger.info("✓ Auto-seed completed successfully")
                except ImportError:
                    logger.warning(
                        "Could not import seed_all script - skipping auto-seed"
                    )
                except Exception as seed_error:
                    logger.error(f"Error during auto-seed: {seed_error}")
            else:
                logger.info("Baseline data exists - skipping auto-seed")

        except Exception as e:
            logger.error(f"Error checking for baseline data: {str(e)}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await create_tables()
        logger.info("Database tables created successfully")
    except ProgrammingError as e:
        logger.warning(
            f"Some tables or indexes already exist, skipping creation: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Failed to create database tables: {str(e)}")
        raise

    from app.core.seed_super_admin import check_database_schema_updated

    async with AsyncSessionLocal() as db:
        if await check_database_schema_updated(db):
            await seed_super_admin(db)
            logger.info("Super admin seeding completed")
        else:
            logger.warning(
                "Database schema is not updated. Run 'alembic upgrade head' to enable super admin seeding."
            )

    include_minimal_routers()

    if os.path.exists("app/static"):
        app.mount("/static", StaticFiles(directory="app/static"), name="static")
        logger.info("Mounted /static directory")
    if os.path.exists("uploads"):
        app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
        logger.info("Mounted /uploads directory")

    background_tasks = BackgroundTasks()
    background_tasks.add_task(auto_seed_baseline_data, background_tasks)
    background_tasks.add_task(init_default_permissions, background_tasks)
    background_tasks.add_task(init_org_roles, background_tasks)
    background_tasks.add_task(init_org_modules, background_tasks)
    background_tasks.add_task(seed_and_sync_entitlements, background_tasks)

    yield

    await async_engine.dispose()
    logger.info("Database engine disposed and connections closed during shutdown")


# --- App creation & middleware wiring -----------------------------------------

app = FastAPI(
    title=config_settings.PROJECT_NAME,
    version=config_settings.VERSION,
    description=config_settings.DESCRIPTION,
    openapi_url="/api/v1/openapi.json",
    lifespan=lifespan,
)

# 1) Fix scheme from X-Forwarded-Proto so redirects stay HTTPS
app.add_middleware(ForwardedSchemeMiddleware)

# 2) Optionally still redirect any real HTTP to HTTPS
app.add_middleware(HTTPSRedirectMiddleware)

# 3) CORS
origins = [
    "https://naughtyfruit.in",
    "https://naughtyfruit.in",
    "http://localhost:3000",
    "http://localhost",
    "http://127.0.0.1:3000",
    *config_settings.BACKEND_CORS_ORIGINS,
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4) Force CORS on all responses
app.add_middleware(ForceCORSMiddleware, allowed_origins=origins)


# --- Global exception handler -------------------------------------------------


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(
        f"Unhandled exception in {request.method} {request.url}: {exc}",
        exc_info=True,
    )

    origin = request.headers.get("origin")
    headers = {}
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
            "error": str(exc) if config_settings.DEBUG else "An unexpected error occurred",
        },
        headers=headers,
    )


@app.on_event("startup")
async def log_cors_config():
    logger.info("=" * 50)
    logger.info("CORS Configuration:")
    logger.info(f"  Allowed Origins: {origins}")
    logger.info("  Allow Credentials: True")
    logger.info('  Allow Methods: ["*"] (all)')
    logger.info('  Allow Headers: ["*"] (all)')
    logger.info("=" * 50)


# --- Router registration (unchanged from your version) ------------------------


def include_minimal_routers():
    routers = []

    try:
        from app.api.v1 import auth as v1_auth

        routers.append((v1_auth.router, "/api/v1/auth", ["authentication-v1"]))
    except Exception as e:
        logger.error(f"Failed to import auth router: {str(e)}")
        raise

    try:
        from app.api.v1 import password as v1_password

        routers.append((v1_password.router, "/api/v1/password", ["password"]))
    except Exception as e:
        logger.error(f"Failed to import password router: {str(e)}")
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
        from app.api.v1 import api_v1_router, register_subrouters

        register_subrouters()
        routers.append((api_v1_router, "/api/v1", ["v1-api"]))
    except Exception as e:
        logger.error(f"Failed to import v1 API router: {str(e)}")
        raise

    try:
        from app.api.v1 import rbac as v1_rbac

        routers.append((v1_rbac.router, "/api/v1/rbac", ["rbac"]))
    except Exception as e:
        logger.error(f"Failed to import rbac router: {str(e)}")
        raise

    try:
        from app.api.v1 import debug as v1_debug

        routers.append((v1_debug.router, "/api/v1/debug", ["debug"]))
        logger.info("Debug router included for RBAC troubleshooting")
    except Exception as e:
        logger.warning(f"Failed to import debug router: {str(e)}")

    try:
        from app.api.v1.organizations import router as organizations_router

        routers.append(
            (organizations_router, "/api/v1/organizations", ["organizations"])
        )
    except Exception as e:
        logger.error(f"Failed to import organizations router: {str(e)}")
        raise

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
        from app.api.v1.vouchers.payment_voucher import router as payment_voucher_router

        routers.append((payment_voucher_router, "/api/v1/payment-vouchers", ["payment-vouchers"]))
    except Exception as e:
        logger.error(f"Failed to import payment_voucher router: {str(e)}")

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

    try:
        from app.api.v1 import gst as v1_gst
        routers.append((v1_gst.router, "/api/v1/gst", ["gst"]))
        logger.info("GST router included unconditionally")
    except Exception as e:
        logger.error(f"Failed to import gst router: {str(e)}")
        raise

    if os.getenv("ENABLE_EXTENDED_ROUTERS", "false").lower() == "true":
        try:
            from app.api.v1 import pdf_extraction as v1_pdf_extraction

            routers.append(
                (v1_pdf_extraction.router, "/api/v1/pdf-extraction", ["pdf-extraction"])
            )
        except Exception as e:
            logger.warning(f"Failed to import pdf_extraction router: {str(e)}")

    try:
        from app.api.v1 import pdf_generation as v1_pdf_generation

        routers.append((v1_pdf_generation.router, "/api/v1", ["pdf-generation"]))
        logger.info("PDF generation router included unconditionally")
    except Exception as e:
        logger.error(f"Failed to import pdf_generation router: {str(e)}")
        raise

    try:
        from app.api.v1.voucher_format_templates import (
            router as voucher_templates_router,
        )

        routers.append((voucher_templates_router, "/api/v1", ["voucher-templates"]))
        logger.info("Voucher format templates router included unconditionally")
    except Exception as e:
        logger.error(f"Failed to import voucher_format_templates router: {str(e)}")
        raise

    if os.getenv("ENABLE_AI_ANALYTICS", "false").lower() == "true":
        try:
            from app.api.v1 import ai_analytics as v1_ai_analytics

            routers.append(
                (v1_ai_analytics.router, "/api/v1/ai-analytics", ["ai-analytics"])
            )
        except Exception as e:
            logger.warning(f"Failed to import ai_analytics router: {str(e)}")

    # Sales orders now unified at /api/v1/vouchers/sales-orders via vouchers router

    for router, prefix, tags in routers:
        try:
            app.include_router(router, prefix=prefix, tags=tags)
            logger.info(f"Router included successfully at prefix: {prefix}")
        except Exception as e:
            logger.warning(f"Failed to include router at prefix {prefix}: {str(e)}")


# --- Utility endpoints --------------------------------------------------------


@app.get("/")
async def root():
    return {
        "message": "Welcome to TritIQ BOS API",
        "version": config_settings.VERSION,
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": config_settings.VERSION}


@app.get("/routes")
def get_routes():
    routes = []
    for route in app.routes:
        if isinstance(route, APIRoute):
            methods = ", ".join(sorted(route.methods)) if route.methods else "ALL"
            routes.append(f"{methods} {route.path}")
    return {"routes": sorted(routes)}


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("app/static/favicon.ico")


# --- Local dev entrypoint (Railway uses gunicorn) -----------------------------

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=config_settings.DEBUG,
        proxy_headers=True,
        forwarded_allow_ips="*",
    )
