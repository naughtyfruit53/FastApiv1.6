"""
Database configuration and session management
"""

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings
import logging
import psutil
import os
import json
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
import psycopg.errors as pg_errors
import asyncio
import urllib.parse
from sqlalchemy.engine.url import make_url
from sqlalchemy.pool import NullPool

logger = logging.getLogger(__name__)

# Cache for table and type existence
_table_existence_cache = {}
_type_existence_cache = {}
_cache_file = os.path.join(settings.SCHEMA_CACHE_DIR, '.schema_cache')
_MEMORY_THRESHOLD_MB = 400  # Warn if RSS exceeds 400MB
_MAX_CACHE_SIZE = 100  # Limit cache to 100 entries each
_REFLECTION_TIMEOUT_SECONDS = 30  # Timeout for schema reflection

def log_memory_usage(context: str):
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()
    rss_mb = mem_info.rss / 1024 / 1024
    logger.info(f"Memory usage ({context}): RSS={rss_mb:.2f}MB, VMS={mem_info.vms / 1024 / 1024:.2f}MB")
    if rss_mb > _MEMORY_THRESHOLD_MB:
        logger.warning(f"Memory usage exceeds threshold of {_MEMORY_THRESHOLD_MB}MB: RSS={rss_mb:.2f}MB")

def check_cache_permissions():
    try:
        cache_dir = settings.SCHEMA_CACHE_DIR
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir, exist_ok=True)
            logger.info(f"Created cache directory: {cache_dir}")
        if not os.access(cache_dir, os.W_OK):
            logger.warning(f"Cache directory {cache_dir} lacks write permissions")
            return False
        return True
    except Exception as e:
        logger.warning(f"Error checking schema cache permissions: {str(e)}")
        return False

def load_schema_cache():
    if not check_cache_permissions():
        logger.warning("Skipping schema cache load due to permission issues")
        return
    try:
        if os.path.exists(_cache_file):
            with open(_cache_file, 'r') as f:
                cache = json.load(f)
                tables = cache.get('tables', {})
                types = cache.get('types', {})
                # Validate cache format
                if not (isinstance(tables, dict) and isinstance(types, dict)):
                    logger.warning("Corrupted schema cache detected, clearing cache")
                    clear_schema_cache()
                    return
                _table_existence_cache.update({k: v for k, v in tables.items()[:_MAX_CACHE_SIZE]})
                _type_existence_cache.update({k: v for k, v in types.items()[:_MAX_CACHE_SIZE]})
                logger.info(f"Loaded schema cache: {len(_table_existence_cache)} tables, {len(_type_existence_cache)} types")
    except json.JSONDecodeError:
        logger.warning("Corrupted schema cache file, clearing cache")
        clear_schema_cache()
    except Exception as e:
        logger.warning(f"Failed to load schema cache: {str(e)}")
        clear_schema_cache()

def clear_schema_cache():
    try:
        _table_existence_cache.clear()
        _type_existence_cache.clear()
        if os.path.exists(_cache_file):
            os.remove(_cache_file)
            logger.info("Cleared schema cache file")
    except Exception as e:
        logger.warning(f"Failed to clear schema cache: {str(e)}")

def save_schema_cache():
    if not check_cache_permissions():
        logger.warning("Skipping schema cache save due to permission issues")
        return
    try:
        cache = {
            'tables': dict(list(_table_existence_cache.items())[:_MAX_CACHE_SIZE]),
            'types': dict(list(_type_existence_cache.items())[:_MAX_CACHE_SIZE])
        }
        with open(_cache_file, 'w') as f:
            json.dump(cache, f)
        logger.info(f"Saved schema cache: {len(cache['tables'])} tables, {len(cache['types'])} types")
    except Exception as e:
        logger.warning(f"Failed to save schema cache: {str(e)}")

async def check_database_initialized(db: AsyncSession) -> bool:
    log_memory_usage("Checking database initialization")
    try:
        query = text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'schema_version')")
        result = await db.execute(query)
        table_exists = result.scalar()
        if table_exists:
            query = text("SELECT version FROM schema_version ORDER BY id DESC LIMIT 1")
            result = await db.execute(query)
            version = result.scalar()
            if version:
                logger.info(f"Database initialized with schema version: {version}")
                return True
        return False
    except Exception as e:
        logger.warning(f"Error checking database initialization: {str(e)}")
        return False

database_url = settings.DATABASE_URL
if not database_url:
    raise ValueError("DATABASE_URL is required in .env file for database connection. Please configure it to connect to Supabase.")

if not (database_url.startswith("postgresql://") or database_url.startswith("postgres://") or
        database_url.startswith("postgresql+") or database_url.startswith("postgres+")):
    logger.warning("DATABASE_URL is not a PostgreSQL/Supabase URL - this may cause issues in production. For development, continuing...")

logger.info(f"Using database: {database_url.split('@')[1] if '@' in database_url else 'URL parsed'}")

url_obj = make_url(database_url)
driver = url_obj.drivername
parsed_url = urllib.parse.urlparse(database_url)
port = int(parsed_url.port) if parsed_url.port else 5432
is_session_mode = port == 5432

if is_session_mode:
    engine_kwargs = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
        "echo": settings.DEBUG,
        "pool_size": 10,
        "max_overflow": 5,
        "pool_timeout": 300,
        "pool_reset_on_return": "rollback",
    }
    logger.info("Using Supabase session mode (port 5432) - pool_size=10, max_overflow=5, timeout=300s")
else:
    engine_kwargs = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
        "echo": settings.DEBUG,
        "poolclass": NullPool,
    }
    logger.info("Using Supabase transaction mode (port 6543) - Using NullPool to avoid client-side pooling issues")

connect_args = {
    "timeout": 300,
    "command_timeout": 120,
    "server_settings": {"statement_timeout": "120s", "tcp_keepalives_idle": "60"},
    "ssl": "require"  # Enforce SSL for Supabase
}

exec_options = {}
if not is_session_mode:
    exec_options["compiled_cache"] = None
    logger.info("Disabled compiled cache for transaction mode")

if not is_session_mode and 'asyncpg' in driver:
    connect_args["statement_cache_size"] = 0
    logger.info("Set statement_cache_size=0 for asyncpg in transaction mode")

logger.debug(f"Creating async engine with connect_args: {connect_args} and kwargs: {engine_kwargs}")

try:
    async_engine = create_async_engine(database_url, connect_args=connect_args, execution_options=exec_options, **engine_kwargs)
    logger.info("Async engine created successfully")
except Exception as e:
    logger.error(f"Failed to create async engine: {str(e)}")
    raise

AsyncSessionLocal = async_sessionmaker(expire_on_commit=False, autocommit=False, autoflush=False, bind=async_engine)

sync_driver = driver.replace('asyncpg', 'psycopg')
sync_database_url = url_obj.set(drivername=sync_driver).render_as_string(hide_password=False)
sync_connect_args = {
    "connect_timeout": 300,
    "keepalives_idle": 60,
    "options": "-c statement_timeout=120s",
    "sslmode": "require"
}
if not is_session_mode:
    sync_connect_args["prepare_threshold"] = None
    logger.info("Disabled prepared statements for sync engine in transaction mode")

sync_exec_options = {}
if not is_session_mode:
    sync_exec_options["compiled_cache"] = None

sync_engine = create_engine(sync_database_url, connect_args=sync_connect_args, execution_options=sync_exec_options, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

Base = declarative_base()

async def get_db():
    db = AsyncSessionLocal()
    logger.debug("Opening new DB session")
    try:
        yield db
    except HTTPException as e:
        raise
    except Exception as e:
        logger.error(f"Database session error: {e}")
        await db.rollback()
        raise
    finally:
        await db.close()
        logger.debug("Closed DB session")

class DatabaseTransaction:
    def __init__(self, db_session: AsyncSession = None):
        self.db = db_session or AsyncSessionLocal()
        self.should_close = db_session is None
        logger.debug(f"Opening transaction, should_close={self.should_close}")
        
    async def __aenter__(self):
        return self.db
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type is not None:
                if not issubclass(exc_type, HTTPException):
                    logger.error(f"Transaction failed: {exc_val}")
                    await self.db.rollback()
            else:
                await self.db.commit()
        except Exception as e:
            logger.error(f"Error during transaction cleanup: {e}")
            await self.db.rollback()
        finally:
            if self.should_close:
                await self.db.close()
                logger.debug("Closed transaction session")
        return False

async def get_db_transaction():
    async with DatabaseTransaction() as db:
        yield db

async def safe_database_operation(operation_func, *args, **kwargs):
    try:
        async with DatabaseTransaction() as db:
            return await operation_func(db, *args, **kwargs)
    except Exception as e:
        logger.error(f"Database operation failed: {e}")
        return None

async def execute_with_retry(operation_func, max_retries: int = 3, *args, **kwargs):
    last_exception = None
    for attempt in range(max_retries + 1):
        try:
            return await safe_database_operation(operation_func, *args, **kwargs)
        except Exception as e:
            last_exception = e
            if attempt < max_retries:
                logger.warning(f"Database operation failed (attempt {attempt + 1}/{max_retries + 1}): {e}")
                await asyncio.sleep(2 ** attempt)
            else:
                logger.error(f"Database operation failed after {max_retries + 1} attempts: {e}")
    raise last_exception

async def check_table_exists(db: AsyncSession, table_name: str) -> bool:
    if table_name in _table_existence_cache:
        return _table_existence_cache[table_name]
    log_memory_usage(f"Checking table {table_name}")
    try:
        async with asyncio.timeout(_REFLECTION_TIMEOUT_SECONDS):
            query = text(
                """
                SELECT EXISTS (
                    SELECT FROM pg_tables 
                    WHERE schemaname = 'public' AND tablename = :table_name
                )
                """
            )
            result = await db.execute(query, {"table_name": table_name})
            exists = result.scalar()
            _table_existence_cache[table_name] = exists
            save_schema_cache()
            return exists
    except asyncio.TimeoutError:
        logger.error(f"Timeout checking table {table_name} after {_REFLECTION_TIMEOUT_SECONDS} seconds")
        return False
    except Exception as e:
        logger.error(f"Error checking table {table_name}: {str(e)}")
        return False

async def check_type_exists(db: AsyncSession, type_name: str) -> bool:
    if type_name in _type_existence_cache:
        return _type_existence_cache[type_name]
    log_memory_usage(f"Checking type {type_name}")
    try:
        async with asyncio.timeout(_REFLECTION_TIMEOUT_SECONDS):
            query = text(
                """
                SELECT EXISTS (
                    SELECT FROM pg_type 
                    WHERE typname = :type_name AND typnamespace IN (
                        SELECT oid FROM pg_namespace WHERE nspname = 'public'
                    )
                )
                """
            )
            result = await db.execute(query, {"type_name": type_name})
            exists = result.scalar()
            _type_existence_cache[type_name] = exists
            save_schema_cache()
            return exists
    except asyncio.TimeoutError:
        logger.error(f"Timeout checking type {type_name} after {_REFLECTION_TIMEOUT_SECONDS} seconds")
        return False
    except Exception as e:
        logger.error(f"Error checking type {type_name}: {str(e)}")
        return False

async def create_tables():
    log_memory_usage("Before table creation")
    load_schema_cache()
    skip_reflection = os.getenv("SKIP_SCHEMA_REFLECTION", "false").lower() == "true"
    if skip_reflection:
        logger.info("SKIP_SCHEMA_REFLECTION is set to true, skipping table creation")
        return
    async with AsyncSessionLocal() as db:
        if await check_database_initialized(db):
            logger.info("Database is initialized, skipping schema reflection")
            return
    try:
        async with asyncio.timeout(_REFLECTION_TIMEOUT_SECONDS * 2):
            async with AsyncSessionLocal() as db:
                critical_tables = ['users', 'organizations', 'platform_users', 'purchase_orders']
                critical_types = ['ratelimittype', 'webhookstatus', 'integrationtype']
                tables_exist = all(await check_table_exists(db, table) for table in critical_tables)
                types_exist = all(await check_type_exists(db, type_name) for type_name in critical_types)
                if not (tables_exist and types_exist):
                    logger.info("Creating database tables for critical models...")
                    log_memory_usage("Before model imports")
                    from app.models.vouchers.purchase import PurchaseOrder, GoodsReceiptNote, PurchaseVoucher, PurchaseReturn
                    from app.models.user_models import User
                    log_memory_usage("After model imports")
                    Base.metadata.create_all(
                        bind=sync_engine,
                        tables=[
                            User.__table__,
                            PurchaseOrder.__table__,
                            GoodsReceiptNote.__table__,
                            PurchaseVoucher.__table__,
                            PurchaseReturn.__table__,
                        ]
                    )
                    logger.info("Database tables for critical models created successfully")
                    await db.execute(text("INSERT INTO schema_version (version) VALUES (:version)"), {"version": "1.0"})
                    await db.commit()
                else:
                    logger.info("Critical tables and types already exist, skipping creation")
    except asyncio.TimeoutError:
        logger.error(f"Timeout during table creation after {_REFLECTION_TIMEOUT_SECONDS * 2} seconds")
        raise
    except ProgrammingError as e:
        if isinstance(e.orig, (pg_errors.DuplicateTable, pg_errors.DuplicateObject)):
            logger.warning(f"Some tables or indexes already exist, skipping creation: {str(e)}")
        else
            logger.error(f"Unexpected database error during table creation: {str(e)}")
            raise
    except Exception as e:
        logger.error(f"Failed to create database tables: {str(e)}")
        raise
    finally:
        log_memory_usage("After table creation")