"""make org state_code required for GST

Revision ID: 20251103_02
Revises: 20251103_01
Create Date: 2024-11-03 17:31:00.000000

This migration makes the state_code field required in the organizations table
to support proper GST calculation. It also provides a default value for any
existing organizations that don't have a state_code set.
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20251103_02'
down_revision = '20251103_01'
branch_labels = None
depends_on = None


def upgrade():
    """Make state_code required in organizations table"""
    
    # First, set a default state_code for any organizations that don't have one
    # Using '27' (Maharashtra) as a reasonable default for India
    op.execute("""
        UPDATE organizations 
        SET state_code = '27' 
        WHERE state_code IS NULL OR state_code = ''
    """)
    
    # Now make the column non-nullable
    op.alter_column(
        'organizations',
        'state_code',
        existing_type=sa.String(),
        nullable=False,
        comment='Required for GST calculation'
    )
    
    # Add an index for better query performance
    op.create_index(
        'idx_organizations_state_code',
        'organizations',
        ['state_code'],
        unique=False
    )


def downgrade():
    """Revert state_code back to nullable"""
    
    # Drop the index
    op.drop_index('idx_organizations_state_code', table_name='organizations')
    
    # Make the column nullable again
    op.alter_column(
        'organizations',
        'state_code',
        existing_type=sa.String(),
        nullable=True
    )
