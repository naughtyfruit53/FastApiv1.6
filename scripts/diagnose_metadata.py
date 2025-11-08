# scripts/diagnose_metadata.py
"""
Diagnostic script to check if SQLAlchemy Base metadata detects models.
Run: python scripts/diagnose_metadata.py
Share the output for further debugging.
"""

import sys
import os
import importlib
import pkgutil
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Add project root to sys.path (assuming run from project root/v1.6/)
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# Import Base
try:
    from app.core.database import Base
    logger.debug("Successfully imported Base")
except ImportError as e:
    logger.error(f"Failed to import Base: {str(e)}")
    sys.exit(1)

# Recursive import function
def import_submodules(package_name):
    try:
        package = importlib.import_module(package_name)
        for loader, name, is_pkg in pkgutil.walk_packages(package.__path__):
            full_name = f"{package_name}.{name}"
            try:
                importlib.import_module(full_name)
                logger.debug(f"Imported: {full_name}")
                if is_pkg:
                    import_submodules(full_name)
            except Exception as e:
                logger.warning(f"Failed to import {full_name}: {str(e)}")
    except Exception as e:
        logger.error(f"Error importing package {package_name}: {str(e)}")

# Import all models recursively
models_package = 'app.models'
import_submodules(models_package)

# Check and print metadata
tables = Base.metadata.tables
sorted_tables = sorted(tables.keys())
print(f"\nNumber of detected tables: {len(sorted_tables)}")
if sorted_tables:
    print("Detected tables:")
    for table_name in sorted_tables:
        print(f"- {table_name}")
else:
    print("No tables detected in Base.metadata - imports may have failed or models not registered.")

# Print registered classes for extra debug
print("\nRegistered model classes:")
for cls in Base.registry.mappers:
    print(f"- {cls.class_.__name__}")