"""Add user_service_roles table

Revision ID: c2e1da5453c0
Revises: 1a4bc96c540d
Create Date: 2025-10-25 19:17:33.163541

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision = 'c2e1da5453c0'
down_revision = '1a4bc96c540d'
branch_labels = None
depends_on = None


def upgrade():
    # Create user_service_roles table only if it doesn't exist
    conn = op.get_bind()
    if not conn.dialect.has_table(conn, 'user_service_roles'):
        op.create_table(
            'user_service_roles',
            sa.Column('id', sa.Integer, primary_key=True, index=True),
            sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'), nullable=False, index=True),
            sa.Column('role_id', sa.Integer, sa.ForeignKey('service_roles.id'), nullable=False, index=True),
            sa.Column('assigned_by_id', sa.Integer, sa.ForeignKey('users.id'), nullable=True),
            sa.Column('is_active', sa.Boolean, default=True, nullable=False),
            sa.Column('created_at', sa.DateTime, default=datetime.utcnow, nullable=False),
            sa.Column('updated_at', sa.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False),
            sa.UniqueConstraint('user_id', 'role_id', name='uq_user_service_role'),
            sa.Index('idx_user_service_role_active', 'user_id', 'is_active')
        )

def downgrade():
    # Drop user_service_roles table only if it exists
    conn = op.get_bind()
    if conn.dialect.has_table(conn, 'user_service_roles'):
        op.drop_table('user_service_roles')