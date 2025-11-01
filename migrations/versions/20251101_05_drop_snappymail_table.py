"""Drop snappymail_configs table

Revision ID: 20251101_05_drop_snappymail
Revises: 20251101_04_trigger
Create Date: 2025-11-01

This migration removes the snappymail_configs table and any related data
as SnappyMail integration has been discontinued.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# Revision identifiers, used by Alembic.
revision = '20251101_05_drop_snappymail'
down_revision = '20251101_04_trigger'
branch_labels = None
depends_on = None


def upgrade():
    """Drop snappymail_configs table if it exists."""
    connection = op.get_bind()
    
    # Check if table exists
    inspector = sa.inspect(connection)
    tables = inspector.get_table_names()
    
    if 'snappymail_configs' in tables:
        print("Dropping snappymail_configs table...")
        op.drop_table('snappymail_configs')
        print("snappymail_configs table dropped successfully")
    else:
        print("snappymail_configs table does not exist, skipping drop")


def downgrade():
    """Recreate snappymail_configs table (not recommended)."""
    print("Downgrade not fully implemented - SnappyMail integration is discontinued")
    print("If you need to restore this table, refer to initial migration f178178734f5")
    # Not recreating as the feature is being removed
    pass
