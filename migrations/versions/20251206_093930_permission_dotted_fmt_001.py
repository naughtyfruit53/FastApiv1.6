"""update permissions to dotted format

Revision ID: permission_dotted_fmt_001
Revises: 
Create Date: 2025-12-06 09:39:30

This migration adds dotted-format permissions to the database and ensures
backward compatibility mappings exist. It's idempotent and safe for staging/production.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy import String, Boolean
import logging

logger = logging.getLogger(__name__)

# revision identifiers, used by Alembic.
revision = 'permission_dotted_fmt_001'
down_revision = 'bb1de77828d1'  # Points to initial_migration
branch_labels = None
depends_on = None


def upgrade():
    """
    Upgrade to dotted permission format.
    
    This migration:
    1. Runs the permission seeder to add dotted-format permissions
    2. Ensures all legacy permissions are mapped
    3. Does not delete legacy permissions (for backward compatibility)
    """
    logger.info("Running permission upgrade migration to dotted format")
    
    # Import and run the seeder
    try:
        from app.db.seeds.permission_seeder import seed_permissions
        from app.core.database import SessionLocal
        
        db = SessionLocal()
        try:
            stats = seed_permissions(db)
            logger.info(f"Permission seeding in migration: {stats}")
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Error running permission seeder in migration: {e}")
        # Don't fail the migration if seeding fails - can be run manually
        print(f"Warning: Permission seeding failed: {e}")
        print("You can run the seeder manually with: python -m app.db.seeds.permission_seeder")


def downgrade():
    """
    Downgrade from dotted permission format.
    
    Note: This is a no-op because we maintain backward compatibility.
    Legacy permissions are not removed, so the system can work with both formats.
    """
    logger.info("Running permission downgrade migration (no-op)")
    print("Note: Downgrade is a no-op. Legacy permissions remain for backward compatibility.")
    print("If you need to remove dotted-format permissions, run a custom script.")
