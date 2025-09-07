from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from app.core.config import settings
import logging
from fastapi import HTTPException
from sqlalchemy.exc import ProgrammingError
import psycopg2.errors as pg_errors

logger = logging.getLogger(__name__)

# Require DATABASE_URL - no fallback
database_url = settings.DATABASE_URL
if not database_url:
    raise ValueError("DATABASE_URL is required in .env file for database connection. Please configure it to connect to Supabase.")

# Validate it's PostgreSQL/Supabase
if not (database_url.startswith("postgresql://") or database_url.startswith("postgres://")):
    raise ValueError("DATABASE_URL must be a PostgreSQL/Supabase URL (starting with postgresql:// or postgres://).")

logger.info(f"Using Supabase database: {database_url.split('@')[1] if '@' in database_url else 'URL parsed'}")  # Mask credentials

# Database engine configuration
engine_kwargs = {
    "pool_pre_ping": True,
    "pool_recycle": 300,
    "echo": settings.DEBUG,
    "pool_size": 10,
    "max_overflow": 20,
    "pool_timeout": 30,
}

# Database engine
engine = create_engine(database_url, **engine_kwargs)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Dependency to get database session with enhanced error handling
def get_db():
    db = SessionLocal()
    try:
        yield db
    except HTTPException as e:
        raise  # Re-raise HTTP exceptions without rollback/log as DB error
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

# Enhanced context manager for database transactions
class DatabaseTransaction:
    """Context manager for database transactions with automatic rollback on error"""
    
    def __init__(self, db_session: Session = None):
        self.db = db_session or SessionLocal()
        self.should_close = db_session is None
        
    def __enter__(self):
        return self.db
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type is not None:
                if not issubclass(exc_type, HTTPException):
                    logger.error(f"Transaction failed: {exc_val}")
                    self.db.rollback()
            else:
                self.db.commit()
        except Exception as e:
            logger.error(f"Error during transaction cleanup: {e}")
            self.db.rollback()
        finally:
            if self.should_close:
                self.db.close()
        
        # Don't suppress exceptions
        return False

def get_db_transaction():
    """Get database session with transaction management"""
    with DatabaseTransaction() as db:
        yield db

# Utility functions for session management
def safe_database_operation(operation_func, *args, **kwargs):
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
        with DatabaseTransaction() as db:
            return operation_func(db, *args, **kwargs)
    except Exception as e:
        logger.error(f"Database operation failed: {e}")
        return None

def execute_with_retry(operation_func, max_retries: int = 3, *args, **kwargs):
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
            return safe_database_operation(operation_func, *args, **kwargs)
        except Exception as e:
            last_exception = e
            if attempt < max_retries:
                logger.warning(f"Database operation failed (attempt {attempt + 1}/{max_retries + 1}): {e}")
                import time
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                logger.error(f"Database operation failed after {max_retries + 1} attempts: {e}")
    
    raise last_exception

# Create all tables with error handling for duplicates
def create_tables():
    try:
        Base.metadata.create_all(bind=engine)
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