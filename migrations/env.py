# migrations/env.py

from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import os
import sys
import importlib
import pkgutil
from dotenv import load_dotenv
import logging

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

# Explicitly load .env from project root
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(project_root, '.env')

logger.debug(f"Calculated project_root: {project_root}")
logger.debug(f"Calculated env_path: {env_path}")
logger.debug(f".env exists: {os.path.exists(env_path)}")

load_dotenv(dotenv_path=env_path)  # Use dotenv_path for explicit loading

BASE_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
APP_DIR = os.path.join(BASE_DIR, "app")
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

from app.core.config import settings
from app.core.database import Base, sync_database_url

# Recursive import function for all submodules
def import_submodules(package_name):
    try:
        package = importlib.import_module(package_name)
        for loader, name, is_pkg in pkgutil.walk_packages(package.__path__):
            full_name = f"{package_name}.{name}"
            try:
                importlib.import_module(full_name)
                logger.debug(f"Imported module: {full_name}")
                if is_pkg:
                    import_submodules(full_name)
            except Exception as e:
                logger.warning(f"Failed to import {full_name}: {str(e)}")
    except Exception as e:
        logger.error(f"Error importing package {package_name}: {str(e)}")

# Import all models recursively
models_dir = "app.models"
import_submodules(models_dir)

# Explicit imports for key modules (as backup)
try:
    from app.models import user_models, rbac_models
    logger.debug("Explicitly imported user_models and rbac_models")
except Exception as e:
    logger.warning(f"Failed explicit imports: {str(e)}")

# Import vouchers subpackage explicitly
try:
    import_submodules("app.models.vouchers")
    logger.debug("Imported vouchers subpackage")
except Exception as e:
    logger.warning(f"Failed to import vouchers subpackage: {str(e)}")

# Diagnostic print for metadata after imports
tables = sorted(Base.metadata.tables.keys())
logger.info(f"Metadata tables count in env.py: {len(tables)}")
if len(tables) > 0:
    logger.info("First 10 tables for debug: " + ", ".join(tables[:10]))
else:
    logger.error("No tables detected in Base.metadata - check model definitions or imports")

config = context.config

if not sync_database_url:
    raise RuntimeError("DATABASE_URL must be set in app.core.config.settings or as an environment variable.")
config.set_main_option('sqlalchemy.url', sync_database_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()