"""Grant organization permissions to default roles

Revision ID: 20251101_03_grant_perms
Revises: 20251101_02_seed_roles
Create Date: 2025-11-01

This migration:
1. Ensures admin_organizations_view and admin_organizations_read permissions exist in service_permissions
2. Grants these permissions to admin and org_admin roles for all organizations
3. Idempotent: skips if permissions/grants already exist
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# Revision identifiers, used by Alembic.
revision = '20251101_03_grant_perms'
down_revision = '20251101_02_seed_roles'
branch_labels = None
depends_on = None


REQUIRED_PERMISSIONS = [
    {
        'name': 'admin_organizations_view',
        'display_name': 'View Organization Dashboard',
        'description': 'Permission to view organization dashboard and statistics',
        'module': 'admin',
        'action': 'organizations_view',
    },
    {
        'name': 'admin_organizations_read',
        'display_name': 'Read Organization Data',
        'description': 'Permission to read organization-level data and activities',
        'module': 'admin',
        'action': 'organizations_read',
    }
]


def upgrade():
    """Ensure permissions exist and grant them to default roles."""
    connection = op.get_bind()
    
    # Check if required tables exist
    inspector = sa.inspect(connection)
    tables = inspector.get_table_names()
    
    if 'service_permissions' not in tables:
        print("service_permissions table not found, skipping permission grants")
        return
    
    if 'service_roles' not in tables:
        print("service_roles table not found, skipping permission grants")
        return
    
    if 'service_role_permissions' not in tables:
        print("service_role_permissions table not found, skipping permission grants")
        return
    
    # Check which columns exist in service_permissions
    perm_columns = {col['name']: col for col in inspector.get_columns('service_permissions')}
    has_created_at = 'created_at' in perm_columns
    has_updated_at = 'updated_at' in perm_columns
    has_module = 'module' in perm_columns
    has_action = 'action' in perm_columns
    
    # Step 1: Ensure permissions exist
    permission_ids = {}
    
    for perm_def in REQUIRED_PERMISSIONS:
        # Check if permission exists
        existing = connection.execute(text(
            "SELECT id FROM service_permissions WHERE name = :name"
        ), {"name": perm_def['name']}).fetchone()
        
        if existing:
            permission_ids[perm_def['name']] = existing[0]
            print(f"Permission '{perm_def['name']}' already exists (id={existing[0]})")
        else:
            # Create permission
            if has_module and has_action and has_created_at and has_updated_at:
                result = connection.execute(text("""
                    INSERT INTO service_permissions (name, display_name, description, module, action, is_active, created_at, updated_at)
                    VALUES (:name, :display_name, :description, :module, :action, TRUE, NOW(), NOW())
                    RETURNING id
                """), {
                    "name": perm_def['name'],
                    "display_name": perm_def['display_name'],
                    "description": perm_def['description'],
                    "module": perm_def['module'],
                    "action": perm_def['action']
                })
            elif has_module and has_action and has_created_at:
                result = connection.execute(text("""
                    INSERT INTO service_permissions (name, display_name, description, module, action, is_active, created_at)
                    VALUES (:name, :display_name, :description, :module, :action, TRUE, NOW())
                    RETURNING id
                """), {
                    "name": perm_def['name'],
                    "display_name": perm_def['display_name'],
                    "description": perm_def['description'],
                    "module": perm_def['module'],
                    "action": perm_def['action']
                })
            elif has_module and has_action:
                result = connection.execute(text("""
                    INSERT INTO service_permissions (name, display_name, description, module, action, is_active)
                    VALUES (:name, :display_name, :description, :module, :action, TRUE)
                    RETURNING id
                """), {
                    "name": perm_def['name'],
                    "display_name": perm_def['display_name'],
                    "description": perm_def['description'],
                    "module": perm_def['module'],
                    "action": perm_def['action']
                })
            else:
                # Minimal insert if module/action columns don't exist
                result = connection.execute(text("""
                    INSERT INTO service_permissions (name, display_name, description, is_active)
                    VALUES (:name, :display_name, :description, TRUE)
                    RETURNING id
                """), {
                    "name": perm_def['name'],
                    "display_name": perm_def['display_name'],
                    "description": perm_def.get('description', '')
                })
            
            perm_id = result.fetchone()[0]
            permission_ids[perm_def['name']] = perm_id
            print(f"Created permission '{perm_def['name']}' (id={perm_id})")
    
    # Step 2: Grant permissions to admin and org_admin roles for all organizations
    role_names = ['admin', 'org_admin']
    grants_created = 0
    
    for role_name in role_names:
        # Get all roles with this name across all orgs
        roles = connection.execute(text("""
            SELECT id, organization_id FROM service_roles 
            WHERE name = :role_name AND is_active = TRUE
        """), {"role_name": role_name}).fetchall()
        
        print(f"Found {len(roles)} '{role_name}' roles to grant permissions to")
        
        for role_row in roles:
            role_id = role_row[0]
            org_id = role_row[1]
            
            for perm_name, perm_id in permission_ids.items():
                # Check if grant already exists
                existing = connection.execute(text("""
                    SELECT id FROM service_role_permissions 
                    WHERE role_id = :role_id AND permission_id = :perm_id
                """), {"role_id": role_id, "perm_id": perm_id}).fetchone()
                
                if existing:
                    continue
                
                # Create grant
                srp_columns = {col['name']: col for col in inspector.get_columns('service_role_permissions')}
                if 'created_at' in srp_columns:
                    connection.execute(text("""
                        INSERT INTO service_role_permissions (role_id, permission_id, created_at)
                        VALUES (:role_id, :perm_id, NOW())
                    """), {"role_id": role_id, "perm_id": perm_id})
                else:
                    connection.execute(text("""
                        INSERT INTO service_role_permissions (role_id, permission_id)
                        VALUES (:role_id, :perm_id)
                    """), {"role_id": role_id, "perm_id": perm_id})
                
                grants_created += 1
                print(f"Granted '{perm_name}' to role_id={role_id} (org={org_id}, role={role_name})")
    
    print(f"Created {grants_created} new permission grants")


def downgrade():
    """Do not revoke permissions - they may be in use."""
    print("Downgrade not implemented - permissions may be in use")
    pass
