"""cleanup legacy roles and permissions

Revision ID: 20251103_01
Revises: 
Create Date: 2025-11-03 08:44:00.000000

This migration removes legacy roles and permissions that are no longer part of the new
4-role system (org_admin, management, manager, executive).

Legacy roles to be removed/migrated:
- All module-specific roles (CRM roles, Service roles, etc.)
- Special purpose roles not in the 4-role system
- Legacy RBAC tables that conflict with new system

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = '20251103_01'
down_revision = None  # Update this to point to the latest migration
branch_labels = None
depends_on = None


def upgrade():
    """
    Remove legacy roles and permissions.
    Migrate users to new 4-role system if needed.
    """
    conn = op.get_bind()
    
    # Step 1: Update any users with legacy roles to valid roles
    # Map legacy roles to new roles
    legacy_role_mapping = {
        'admin': 'org_admin',
        'crm_admin': 'management',
        'service_admin': 'management',
        'crm_manager': 'manager',
        'service_manager': 'manager',
        'crm_executive': 'executive',
        'service_executive': 'executive',
        'user': 'executive',
        'staff': 'executive',
        # Add more mappings as needed
    }
    
    print("Migrating users with legacy roles to new role system...")
    for old_role, new_role in legacy_role_mapping.items():
        try:
            result = conn.execute(
                text(f"UPDATE users SET role = :new_role WHERE role = :old_role"),
                {"new_role": new_role, "old_role": old_role}
            )
            if result.rowcount > 0:
                print(f"  Migrated {result.rowcount} users from '{old_role}' to '{new_role}'")
        except Exception as e:
            print(f"  Warning: Could not migrate role '{old_role}': {str(e)}")
    
    # Step 2: Clean up service_roles table if it contains legacy data
    # Note: We keep the table structure for compatibility but remove legacy role definitions
    try:
        # Check if service_roles table exists
        inspector = sa.inspect(conn)
        if 'service_roles' in inspector.get_table_names():
            print("Cleaning up legacy service roles...")
            # Keep only the 4 standard roles
            conn.execute(
                text("""
                    DELETE FROM service_role_permissions 
                    WHERE role_id IN (
                        SELECT id FROM service_roles 
                        WHERE name NOT IN ('org_admin', 'management', 'manager', 'executive')
                    )
                """)
            )
            conn.execute(
                text("""
                    DELETE FROM user_service_roles 
                    WHERE role_id IN (
                        SELECT id FROM service_roles 
                        WHERE name NOT IN ('org_admin', 'management', 'manager', 'executive')
                    )
                """)
            )
            result = conn.execute(
                text("""
                    DELETE FROM service_roles 
                    WHERE name NOT IN ('org_admin', 'management', 'manager', 'executive')
                """)
            )
            print(f"  Removed {result.rowcount} legacy service roles")
    except Exception as e:
        print(f"  Warning: Could not clean up service_roles: {str(e)}")
    
    # Step 3: Clean up module-specific permissions that don't align with new system
    try:
        if 'service_permissions' in inspector.get_table_names():
            print("Cleaning up legacy module-specific permissions...")
            # Remove CRM-specific and Service-specific permissions
            result = conn.execute(
                text("""
                    DELETE FROM service_role_permissions 
                    WHERE permission_id IN (
                        SELECT id FROM service_permissions 
                        WHERE module IN ('CRM_specific', 'Service_specific', 'legacy_module')
                    )
                """)
            )
            result = conn.execute(
                text("""
                    DELETE FROM service_permissions 
                    WHERE module IN ('CRM_specific', 'Service_specific', 'legacy_module')
                """)
            )
            print(f"  Removed {result.rowcount} legacy module-specific permissions")
    except Exception as e:
        print(f"  Warning: Could not clean up service_permissions: {str(e)}")
    
    print("Legacy role cleanup completed!")


def downgrade():
    """
    Downgrade is not supported for this migration as it involves data cleanup.
    If you need to restore legacy roles, you should restore from a backup.
    """
    print("Downgrade not supported for legacy role cleanup migration.")
    pass
