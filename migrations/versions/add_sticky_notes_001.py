"""Add sticky notes table and user settings

Revision ID: add_sticky_notes_001
Revises: a0e2cc05d20e
Create Date: 2024-01-20 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_sticky_notes_001'
down_revision = 'a0e2cc05d20e'
branch_labels = None
depends_on = None


def upgrade():
    # Create sticky_notes table
    op.create_table('sticky_notes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('color', sa.String(length=20), nullable=False, server_default='yellow'),
        sa.Column('position', sa.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name='fk_sticky_note_organization_id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_sticky_note_user_id'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sticky_notes_id'), 'sticky_notes', ['id'], unique=False)
    op.create_index(op.f('ix_sticky_notes_user_id'), 'sticky_notes', ['user_id'], unique=False)
    op.create_index(op.f('ix_sticky_notes_organization_id'), 'sticky_notes', ['organization_id'], unique=False)
    
    # Add user_settings column to users table
    op.add_column('users', sa.Column('user_settings', sa.JSON(), nullable=True, server_default='{"sticky_notes_enabled": true}'))


def downgrade():
    # Remove user_settings column from users table
    op.drop_column('users', 'user_settings')
    
    # Drop sticky_notes table
    op.drop_index(op.f('ix_sticky_notes_organization_id'), table_name='sticky_notes')
    op.drop_index(op.f('ix_sticky_notes_user_id'), table_name='sticky_notes')
    op.drop_index(op.f('ix_sticky_notes_id'), table_name='sticky_notes')
    op.drop_table('sticky_notes')