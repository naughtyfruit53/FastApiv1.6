# migrations/versions/add_organization_id_to_otp_verifications.py

"""Add organization_id to otp_verifications

Revision ID: <generate a unique id, e.g., using alembic revision --autogenerate>
Revises: 2be0230fa04b
Create Date: 2025-08-27 15:30:00

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '<unique_revision_id>'  # Replace with actual generated ID
down_revision = '2be0230fa04b'
branch_labels = None
depends_on = None

def upgrade():
    # Add the organization_id column to otp_verifications table
    op.add_column('otp_verifications',
        sa.Column('organization_id', sa.Integer(), nullable=True, index=True)
    )
    
    # Add foreign key constraint
    op.create_foreign_key(
        'fk_otp_organization_id',
        'otp_verifications',
        'organizations',
        ['organization_id'],
        ['id']
    )

def downgrade():
    # Remove the foreign key constraint
    op.drop_constraint('fk_otp_organization_id', 'otp_verifications', type_='foreignkey')
    
    # Remove the organization_id column
    op.drop_column('otp_verifications', 'organization_id')