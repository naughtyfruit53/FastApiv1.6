# app/db/session.py

"""
Enhanced database session management with automatic rollback and retry logic.
"""

from contextlib import contextmanager, asynccontextmanager
from typing import Generator, Callable, Any, Optional, Type, AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, OperationalError, TimeoutError
from sqlalchemy import text
from app.core.database import AsyncSessionLocal, sync_engine  # Import sync_engine for sync session
from app.core.logging import get_logger, log_database_operation
import time
import logging
import asyncio

# NEW: Import for tenant context
from app.core.tenant import TenantContext

logger = get_logger("session")

# Add sync SessionLocal
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

class SessionManager:
    """Enhanced session manager with automatic error handling and rollback"""
    
    def __init__(self, session_factory: Callable = AsyncSessionLocal):
        self.session_factory = session_factory
    
    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Get an asynchronous database session with automatic rollback on error.
        
        Usage:
            async with session_manager.get_session() as db:
                # perform database operations
                await db.add(model_instance)
                await db.commit()  # Explicit commit required
        """
        session = self.session_factory()
        # NEW: Set RLS session variable if org_id available
        org_id = TenantContext.get_organization_id()
        if org_id is not None:
            # Use string interpolation for SET command value - PostgreSQL does not support bind params for SET
            await session.execute(text(f"SET app.current_organization_id = {org_id}"))
            logger.debug(f"Set session var: app.current_organization_id = {org_id}")
        try:
            yield session
        except Exception as e:
            logger.error(f"Session error occurred: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()
    
    @asynccontextmanager
    async def get_transaction(self, auto_commit: bool = True) -> AsyncGenerator[AsyncSession, None]:
        """
        Get an asynchronous database session with transaction management.
        
        Args:
            auto_commit: If True, automatically commits on success
        
        Usage:
            async with session_manager.get_transaction() as db:
                # perform database operations
                await db.add(model_instance)
                # automatic commit on success, rollback on error
        """
        session = self.session_factory()
        # NEW: Set RLS session variable if org_id available
        org_id = TenantContext.get_organization_id()
        if org_id is not None:
            # Use string interpolation for SET command value - PostgreSQL does not support bind params for SET
            await session.execute(text(f"SET app.current_organization_id = {org_id}"))
            logger.debug(f"Set session var: app.current_organization_id = {org_id}")
        try:
            yield session
            if auto_commit:
                await session.commit()
                logger.debug("Transaction committed successfully")
        except Exception as e:
            logger.error(f"Transaction failed: {e}")
            await session.rollback()
            logger.debug("Transaction rolled back")
            raise
        finally:
            await session.close()
    
    async def execute_with_retry(self, 
                          operation: Callable[[AsyncSession], Any], 
                          max_retries: int = 3,
                          retry_delay: float = 1.0,
                          exponential_backoff: bool = True) -> Any:
        """
        Execute a database operation with retry logic for transient failures.
        
        Args:
            operation: Function that takes a session and returns a result
            max_retries: Maximum number of retry attempts
            retry_delay: Initial delay between retries (seconds)
            exponential_backoff: Whether to use exponential backoff
        
        Returns:
            Result of the operation
        
        Raises:
            Final exception if all retries fail
        """
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                async with self.get_transaction() as session:
                    result = await operation(session)
                    logger.debug(f"Operation succeeded on attempt {attempt + 1}")
                    return result
                    
            except (OperationalError, IntegrityError, TimeoutError, SQLAlchemyError) as e:
                last_exception = e
                if attempt < max_retries:
                    delay = retry_delay * (2 ** attempt) if exponential_backoff else retry_delay
                    logger.warning(f"Operation failed (attempt {attempt + 1}/{max_retries + 1}): {e}. Retrying in {delay}s...")
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"Operation failed after {max_retries + 1} attempts: {e}")
            except Exception as e:
                # Non-retryable exceptions
                logger.error(f"Non-retryable error in database operation: {e}")
                raise
        
        raise last_exception
    
    async def safe_execute(self, operation: Callable[[AsyncSession], Any]) -> tuple[bool, Any, Optional[str]]:
        """
        Safely execute a database operation without raising exceptions.
        
        Args:
            operation: Function that takes a session and returns a result
        
        Returns:
            Tuple of (success: bool, result: Any, error_message: Optional[str])
        """
        try:
            async with self.get_transaction() as session:
                result = await operation(session)
                return True, result, None
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Safe execute failed: {error_msg}")
            return False, None, error_msg

# Global session manager instance
session_manager = SessionManager()

# Convenience functions for common patterns
@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get a database session (alias for session_manager.get_session)"""
    async with session_manager.get_session() as session:
        yield session

@asynccontextmanager
async def get_db_transaction(auto_commit: bool = True) -> AsyncGenerator[AsyncSession, None]:
    """Get a database transaction (alias for session_manager.get_transaction)"""
    async with session_manager.get_transaction(auto_commit=auto_commit) as session:
        yield session

async def execute_db_operation(operation: Callable[[AsyncSession], Any], 
                        with_retry: bool = False,
                        max_retries: int = 3) -> Any:
    """
    Execute a database operation with optional retry logic.
    
    Args:
        operation: Function that takes a session and returns a result
        with_retry: Whether to use retry logic for transient failures
        max_retries: Maximum retry attempts if with_retry is True
    
    Returns:
        Result of the operation
    """
    if with_retry:
        return await session_manager.execute_with_retry(operation, max_retries=max_retries)
    else:
        async with get_db_transaction() as session:
            return await operation(session)

async def safe_db_operation(operation: Callable[[AsyncSession], Any]) -> tuple[bool, Any, Optional[str]]:
    """
    Safely execute a database operation without raising exceptions.
    
    Returns:
        Tuple of (success, result, error_message)
    """
    return await session_manager.safe_execute(operation)

# Decorators for automatic session management
def with_db_session(auto_commit: bool = True):
    """
    Decorator that provides a database session to the decorated function.
    
    Args:
        auto_commit: Whether to automatically commit the transaction
    
    Usage:
        @with_db_session()
        async def my_function(db: AsyncSession, other_param: str):
            # db session is automatically provided
            pass
    """
    def decorator(func: Callable) -> Callable:
        async def wrapper(*args, **kwargs):
            async with get_db_transaction(auto_commit=auto_commit) as session:
                return await func(session, *args, **kwargs)
        return wrapper
    return decorator

def with_db_retry(max_retries: int = 3):
    """
    Decorator that adds retry logic to database operations.
    
    Args:
        max_retries: Maximum number of retry attempts
    
    Usage:
        @with_db_retry(max_retries=3)
        async def my_db_function(db: AsyncSession):
            # This function will be retried on transient failures
            pass
    """
    def decorator(func: Callable) -> Callable:
        async def wrapper(*args, **kwargs):
            async def operation(session: AsyncSession):
                return await func(session, *args, **kwargs)
            return await session_manager.execute_with_retry(operation, max_retries=max_retries)
        return wrapper
    return decorator

# Audit logging helper
def log_db_operation(operation_type: str, table_name: str, record_id: Optional[int] = None):
    """
    Decorator to log database operations for auditing.
    
    Args:
        operation_type: Type of operation (CREATE, UPDATE, DELETE, SELECT)
        table_name: Name of the database table
        record_id: ID of the record (if applicable)
    
    Usage:
        @log_db_operation("CREATE", "users")
        async def create_user(db: AsyncSession, user_data: dict):
            # Operation will be logged
            pass
    """
    def decorator(func: Callable) -> Callable:
        async def wrapper(*args, **kwargs):
            try:
                result = await func(*args, **kwargs)
                log_database_operation(operation_type, table_name, record_id)
                return result
            except Exception as e:
                logger.error(f"Database operation {operation_type} on {table_name} failed: {e}")
                raise
        return wrapper
    return decorator

# Session health check
async def check_session_health() -> dict:
    """
    Check the health of database sessions and connections.
    
    Returns:
        Dictionary with health status information
    """
    try:
        async with get_db_session() as session:
            # Simple query to test connection
            result = await session.execute("SELECT 1")
            result.fetchone()
            
            return {
                "status": "healthy",
                "message": "Database connection is working",
                "timestamp": time.time()
            }
    except Exception as e:
        return {
            "status": "unhealthy",
            "message": f"Database connection failed: {str(e)}",
            "timestamp": time.time()
        }

# Connection pool monitoring
async def get_pool_status() -> dict:
    """
    Get the status of the database connection pool.
    
    Returns:
        Dictionary with pool status information
    """
    try:
        from app.core.database import async_engine
        pool = async_engine.pool
        
        return {
            "pool_size": pool.size(),
            "checked_in": pool.checkedin(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
            "status": "healthy"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

# FastAPI dependency for DB session
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that provides a database session.
    Yields the session and ensures it's closed after use.
    """
    async with session_manager.get_session() as session:
        yield session
        