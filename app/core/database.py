# app/core/database.py

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings
import logging
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
import psycopg.errors as pg_errors
import asyncio
import urllib.parse
from sqlalchemy.engine.url import make_url
from sqlalchemy.pool import NullPool  # Import NullPool

logger = logging.getLogger(__name__)

# Require DATABASE_URL - no fallback
database_url = settings.DATABASE_URL
if not database_url:
    raise ValueError("DATABASE_URL is required in .env file for database connection. Please configure it to connect to Supabase.")

# Improved check: Allow for +driver in URL (e.g., postgresql+psycopg://) which is valid for SQLAlchemy async
if not (database_url.startswith("postgresql://") or database_url.startswith("postgres://") or
        database_url.startswith("postgresql+") or database_url.startswith("postgres+")):
    logger.warning("DATABASE_URL is not a PostgreSQL/Supabase URL - this may cause issues in production. For development, continuing...")

logger.info(f"Using database: {database_url.split('@')[1] if '@' in database_url else 'URL parsed'}")  # Mask credentials

# Parse URL to get driver and detect port for Supabase mode
url_obj = make_url(database_url)
driver = url_obj.drivername
parsed_url = urllib.parse.urlparse(database_url)
port = int(parsed_url.port) if parsed_url.port else 5432

# Corrected based on Supabase docs: session mode uses port 5432 on pooler, transaction uses 6543
is_session_mode = port == 5432

# Database engine configuration based on mode
if is_session_mode:
    # Session mode: Increased pool_size to handle more concurrent requests (check Supabase dashboard limits)
    engine_kwargs = {
        "pool_pre_ping": True,  # Test connections before use
        "pool_recycle": 300,  # Recycle connections after 5 min idle
        "echo": settings.DEBUG,
        "pool_size": 20,  # Increased from 5 to 20 to avoid exhaustion (adjust based on Supabase plan)
        "max_overflow": 10,  # Allow temporary overflow
        "pool_timeout": 300,  # Increased timeout to 5 minutes
        "pool_reset_on_return": "rollback",  # Reset on return to avoid leaks
    }
    logger.info("Using Supabase session mode (port 5432) - pool_size=20, max_overflow=10, timeout=300s")
else:
    # Transaction mode: Use NullPool to disable client-side pooling; let Supavisor handle it
    engine_kwargs = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
        "echo": settings.DEBUG,
        "poolclass": NullPool,  # Disable client-side pooling for transaction mode
    }
    logger.info("Using Supabase transaction mode (port 6543) - Using NullPool to avoid client-side pooling issues")

# Common connect_args for async (asyncpg)
connect_args = {
    "timeout": 300,  # Increased connection timeout to 5 minutes
    "command_timeout": 120,  # Increased query timeout to 2 minutes
    "server_settings": {"statement_timeout": "120s", "tcp_keepalives_idle": "60"}  # DB-level statement timeout and keepalive
}

# Execution options
exec_options = {}
if not is_session_mode:
    exec_options["compiled_cache"] = None
    logger.info("Disabled compiled cache for transaction mode")

# Disable prepared statements or equivalent for transaction mode
if not is_session_mode:
    if 'asyncpg' in driver:
        connect_args["statement_cache_size"] = 0
        logger.info("Set statement_cache_size=0 for asyncpg in transaction mode")

logger.debug(f"Creating async engine with connect_args: {connect_args} and kwargs: {engine_kwargs}")

# Async Database engine
try:
    async_engine = create_async_engine(database_url, connect_args=connect_args, execution_options=exec_options, **engine_kwargs)
    logger.info("Async engine created successfully")
except Exception as e:
    logger.error(f"Failed to create async engine: {str(e)}")
    raise

# Async Session factory
AsyncSessionLocal = async_sessionmaker(expire_on_commit=False, autocommit=False, autoflush=False, bind=async_engine)

# Sync engine for background workers
# Adjust driver for sync if asyncpg, using psycopg (psycopg3)
sync_driver = driver.replace('asyncpg', 'psycopg')
sync_database_url = url_obj.set(drivername=sync_driver).render_as_string(hide_password=False)

sync_connect_args = {
    "connect_timeout": 300,  # Increased to 5 minutes
    "keepalives_idle": 60,
    "options": "-c statement_timeout=120s",
    "sslmode": "require"  # Ensure SSL is required for Supabase
}
if not is_session_mode:
    sync_connect_args["prepare_threshold"] = None
    logger.info("Disabled prepared statements for sync engine in transaction mode")

sync_exec_options = {}
if not is_session_mode:
    sync_exec_options["compiled_cache"] = None

sync_engine = create_engine(sync_database_url, connect_args=sync_connect_args, execution_options=sync_exec_options, **engine_kwargs)

# Sync Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

# Base class for models
Base = declarative_base()

# Dependency to get database session with enhanced error handling
async def get_db():
    db = AsyncSessionLocal()
    logger.debug("Opening new DB session")
    try:
        yield db
    except HTTPException as e:
        raise  # Re-raise HTTP exceptions without rollback/log as DB error
    except Exception as e:
        logger.error(f"Database session error: {e}")
        await db.rollback()
        raise
    finally:
        await db.close()
        logger.debug("Closed DB session")

# Enhanced context manager for database transactions
class DatabaseTransaction:
    """Context manager for database transactions with automatic rollback on error"""
    
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
        
        # Don't suppress exceptions
        return False

async def get_db_transaction():
    """Get database session with transaction management"""
    async with DatabaseTransaction() as db:
        yield db

# Utility functions for session management
async def safe_database_operation(operation_func, *args, **kwargs):
    """
    Safely execute a database operation with automatic rollback on error.
    
    Args:
        operation_func: Function to execute that takes db as first parameter
        *args: Additional arguments for the operation function
        **kwargs: Additional keyword arguments for the operation function
    
    Returns:
        Result of the operation function or None if error occurred
    """
    try:
        async with DatabaseTransaction() as db:
            return await operation_func(db, *args, **kwargs)
    except Exception as e:
        logger.error(f"Database operation failed: {e}")
        return None

async def execute_with_retry(operation_func, max_retries: int = 3, *args, **kwargs):
    """
    Execute database operation with retry logic for transient failures.
    
    Args:
        operation_func: Function to execute
        max_retries: Maximum number of retry attempts
        *args: Arguments for the operation function
        **kwargs: Keyword arguments for the operation function
    
    Returns:
        Result of the operation or raises the final exception
    """
    last_exception = None
    
    for attempt in range(max_retries + 1):
        try:
            return await safe_database_operation(operation_func, *args, **kwargs)
        except Exception as e:
            last_exception = e
            if attempt < max_retries:
                logger.warning(f"Database operation failed (attempt {attempt + 1}/{max_retries + 1}): {e}")
                import time
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
            else:
                logger.error(f"Database operation failed after {max_retries + 1} attempts: {e}")
    
    raise last_exception

# Create all tables with error handling for duplicates
def create_tables():
    try:
        Base.metadata.create_all(bind=sync_engine)
        logger.info("Database tables created successfully")
    except ProgrammingError as e:
        if isinstance(e.orig, (pg_errors.DuplicateTable, pg_errors.DuplicateObject)):
            logger.warning(f"Some tables or indexes already exist, skipping creation: {str(e)}")
        else:
            logger.error(f"Unexpected database error during table creation: {str(e)}")
            raise
    except Exception as e:
        logger.error(f"Failed to create database tables: {str(e)}")
        raise

# Add shutdown cleanup
async def dispose_engines():
    await async_engine.dispose()
    sync_engine.dispose()
    logger.info("Database engines disposed")