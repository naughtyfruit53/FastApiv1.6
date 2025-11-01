"""Seed default service_roles per organization

Revision ID: 20251101_02_seed_roles
Revises: 20251101_01_normalize
Create Date: 2025-11-01

This migration seeds default service_roles for all existing organizations:
- Creates 'admin' and 'org_admin' roles per organization
- Idempotent: skips if roles already exist
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text
from datetime import datetime

# Revision identifiers, used by Alembic.
revision = '20251101_02_seed_roles'
down_revision = '20251101_01_normalize'
branch_labels = None
depends_on = None


DEFAULT_ROLES = [
    {
        'name': 'admin',
        'display_name': 'Administrator',
        'description': 'Full administrative access to all organization features',
    },
    {
        'name': 'org_admin',
        'display_name': 'Organization Admin',
        'description': 'Organization-level administrative access',
    }
]


def upgrade():
    """Seed default roles for all organizations."""
    connection = op.get_bind()
    
    # Check if service_roles table exists
    inspector = sa.inspect(connection)
    tables = inspector.get_table_names()
    
    if 'service_roles' not in tables:
        print("service_roles table not found, skipping role seeding")
        return
    
    # Get all organization IDs
    result = connection.execute(text("SELECT id FROM organizations"))
    org_ids = [row[0] for row in result]
    
    print(f"Found {len(org_ids)} organizations")
    
    # Check which columns exist in service_roles
    columns = {col['name']: col for col in inspector.get_columns('service_roles')}
    has_created_at = 'created_at' in columns
    has_updated_at = 'updated_at' in columns
    
    roles_created = 0
    
    for org_id in org_ids:
        for role_def in DEFAULT_ROLES:
            # Check if role already exists for this org
            existing = connection.execute(text(
                "SELECT id FROM service_roles WHERE organization_id = :org_id AND name = :name"
            ), {"org_id": org_id, "name": role_def['name']}).fetchone()
            
            if existing:
                print(f"Org {org_id}: Role '{role_def['name']}' already exists, skipping")
                continue
            
            # Build insert statement based on available columns
            if has_created_at and has_updated_at:
                connection.execute(text("""
                    INSERT INTO service_roles (organization_id, name, display_name, description, is_active, created_at, updated_at)
                    VALUES (:org_id, :name, :display_name, :description, TRUE, NOW(), NOW())
                """), {
                    "org_id": org_id,
                    "name": role_def['name'],
                    "display_name": role_def['display_name'],
                    "description": role_def['description']
                })
            elif has_created_at:
                connection.execute(text("""
                    INSERT INTO service_roles (organization_id, name, display_name, description, is_active, created_at)
                    VALUES (:org_id, :name, :display_name, :description, TRUE, NOW())
                """), {
                    "org_id": org_id,
                    "name": role_def['name'],
                    "display_name": role_def['display_name'],
                    "description": role_def['description']
                })
            else:
                connection.execute(text("""
                    INSERT INTO service_roles (organization_id, name, display_name, description, is_active)
                    VALUES (:org_id, :name, :display_name, :description, TRUE)
                """), {
                    "org_id": org_id,
                    "name": role_def['name'],
                    "display_name": role_def['display_name'],
                    "description": role_def['description']
                })
            
            roles_created += 1
            print(f"Org {org_id}: Created role '{role_def['name']}'")
    
    print(f"Created {roles_created} new roles across {len(org_ids)} organizations")


def downgrade():
    """Do not drop roles - they may have been assigned to users."""
    print("Downgrade not implemented - roles may be in use")
    pass
