# migrations/env.py

from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
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
from app.core.database import Base

# Dynamically import all models
models_dir = os.path.join(APP_DIR, "models")
for (_, module_name, _) in pkgutil.iter_modules([models_dir]):
    importlib.import_module(f"app.models.{module_name}")

# Explicitly import user_models to ensure new columns are detected
from app.models import user_models

config = context.config

database_url = getattr(settings, "SESSION_DATABASE_URL", None) or getattr(settings, "DATABASE_URL", None) or "sqlite:///./tritiq_erp.db"
if not database_url:
    raise RuntimeError("DATABASE_URL or SESSION_DATABASE_URL must be set in app.core.config.settings or as an environment variable.")
config.set_main_option('sqlalchemy.url', database_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def is_sqlite(url):
    return url.lower().startswith("sqlite")

def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
        render_as_batch=is_sqlite(url),
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
            render_as_batch=is_sqlite(database_url),
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()