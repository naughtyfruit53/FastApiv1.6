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

# Explicitly load .env from project root
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(project_root, '.env')

# Debug prints
print(f"DEBUG: Calculated project_root: {project_root}")
print(f"DEBUG: Calculated env_path: {env_path}")
print(f"DEBUG: .env exists: {os.path.exists(env_path)}")

load_dotenv(env_path)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
APP_DIR = os.path.join(BASE_DIR, "app")
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

from app.core.config import settings
from app.core.database import Base, sync_database_url

# Dynamically import all models, with duplicate check
models_dir = os.path.join(APP_DIR, "models")
imported_modules = set()
for (_, module_name, _) in pkgutil.iter_modules([models_dir]):
    if module_name not in imported_modules:
        try:
            importlib.import_module(f"app.models.{module_name}")
            imported_modules.add(module_name)
        except Exception as e:
            print(f"WARNING: Skipping import of app.models.{module_name}: {e}")

# Explicitly import user_models and rbac_models to ensure new columns are detected
from app.models import user_models
from app.models import rbac_models  # Explicit import to resolve conflict

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