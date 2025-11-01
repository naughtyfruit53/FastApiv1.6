"""Reset service_roles to account-type roles per organization

Revision ID: 20251101_06_account_roles
Revises: 20251101_05_drop_snappymail
Create Date: 2025-11-01

This migration:
1. Resets service_roles to use account-type roles: org_admin, management, manager, executive
2. Clears legacy role assignments (admin/manager/support/viewer)
3. Creates the four standardized roles for all organizations
4. Idempotent: safe to run multiple times
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# Revision identifiers, used by Alembic.
revision = '20251101_06_account_roles'
down_revision = '20251101_05_drop_snappymail'
branch_labels = None
depends_on = None


# Define the new account-type roles
ACCOUNT_TYPE_ROLES = [
    {
        'name': 'org_admin',
        'display_name': 'Organization Administrator',
        'description': 'Full administrative access to all enabled modules and submodules',
    },
    {
        'name': 'management',
        'display_name': 'Management',
        'description': 'Management-level access to all enabled modules and submodules',
    },
    {
        'name': 'manager',
        'display_name': 'Manager',
        'description': 'Manager role with delegated access to specific modules',
    },
    {
        'name': 'executive',
        'display_name': 'Executive',
        'description': 'Executive role with delegated access to specific modules',
    }
]

# Legacy roles to be deprecated (but not removed to preserve historical data)
LEGACY_ROLES = ['admin', 'support', 'viewer']


def upgrade():
    """Reset roles to account-type roles."""
    connection = op.get_bind()
    
    # Check if service_roles table exists
    inspector = sa.inspect(connection)
    tables = inspector.get_table_names()
    
    if 'service_roles' not in tables:
        print("service_roles table not found, skipping role reset")
        return
    
    # Get all organization IDs
    result = connection.execute(text("SELECT id FROM organizations"))
    org_ids = [row[0] for row in result]
    
    print(f"Found {len(org_ids)} organizations to update")
    
    # Check which columns exist in service_roles
    columns = {col['name']: col for col in inspector.get_columns('service_roles')}
    has_created_at = 'created_at' in columns
    has_updated_at = 'updated_at' in columns
    
    roles_created = 0
    roles_updated = 0
    
    # For each organization, ensure account-type roles exist
    for org_id in org_ids:
        for role_def in ACCOUNT_TYPE_ROLES:
            # Check if role already exists for this org
            existing = connection.execute(text(
                "SELECT id, display_name, description, is_active FROM service_roles "
                "WHERE organization_id = :org_id AND name = :name"
            ), {"org_id": org_id, "name": role_def['name']}).fetchone()
            
            if existing:
                # Update existing role to ensure consistency
                role_id = existing[0]
                if has_updated_at:
                    connection.execute(text("""
                        UPDATE service_roles 
                        SET display_name = :display_name,
                            description = :description,
                            is_active = TRUE,
                            updated_at = NOW()
                        WHERE id = :role_id
                    """), {
                        "role_id": role_id,
                        "display_name": role_def['display_name'],
                        "description": role_def['description']
                    })
                else:
                    connection.execute(text("""
                        UPDATE service_roles 
                        SET display_name = :display_name,
                            description = :description,
                            is_active = TRUE
                        WHERE id = :role_id
                    """), {
                        "role_id": role_id,
                        "display_name": role_def['display_name'],
                        "description": role_def['description']
                    })
                roles_updated += 1
                print(f"Org {org_id}: Updated role '{role_def['name']}' (id={role_id})")
            else:
                # Create new role
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
    
    # Mark legacy roles as inactive (but don't delete to preserve historical data)
    deprecated_roles = []
    if LEGACY_ROLES:
        legacy_roles_str = "', '".join(LEGACY_ROLES)
        if has_updated_at:
            result = connection.execute(text(f"""
                UPDATE service_roles 
                SET is_active = FALSE,
                    updated_at = NOW()
                WHERE name IN ('{legacy_roles_str}')
                AND is_active = TRUE
                RETURNING id, name, organization_id
            """))
        else:
            result = connection.execute(text(f"""
                UPDATE service_roles 
                SET is_active = FALSE
                WHERE name IN ('{legacy_roles_str}')
                AND is_active = TRUE
                RETURNING id, name, organization_id
            """))
        
        deprecated_roles = result.fetchall()
        if deprecated_roles:
            print(f"Deprecated {len(deprecated_roles)} legacy roles:")
            for role_row in deprecated_roles:
                print(f"  - Role '{role_row[1]}' (id={role_row[0]}, org={role_row[2]})")
    
    print(f"\nSummary:")
    print(f"  - Created {roles_created} new account-type roles")
    print(f"  - Updated {roles_updated} existing roles")
    print(f"  - Deprecated {len(deprecated_roles) if deprecated_roles else 0} legacy roles")


def downgrade():
    """No automatic downgrade - manual intervention required."""
    print("Downgrade not implemented - role changes require manual review")
    print("Legacy roles have been marked inactive, not deleted")
    pass
