"""Update organization trigger for account-type roles

Revision ID: 20251101_08_trigger_update
Revises: 20251101_07_permissions
Create Date: 2025-11-01

This migration:
1. Updates the auto-seeding trigger to use account-type roles
2. Creates org_admin, management, manager, executive roles for new organizations
3. Grants full access to org_admin and management automatically
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# Revision identifiers, used by Alembic.
revision = '20251101_08_trigger_update'
down_revision = '20251101_07_permissions'
branch_labels = None
depends_on = None


def upgrade():
    """Update the organization trigger to seed account-type roles."""
    connection = op.get_bind()
    
    # Drop old trigger and function if they exist
    print("Dropping old trigger and function...")
    connection.execute(text("DROP TRIGGER IF EXISTS trigger_seed_org_roles ON organizations"))
    connection.execute(text("DROP FUNCTION IF EXISTS seed_roles_and_grants_for_org(INTEGER)"))
    
    # Create updated function with account-type roles
    print("Creating updated trigger function...")
    connection.execute(text("""
        CREATE OR REPLACE FUNCTION seed_account_roles_for_org(p_org_id INTEGER)
        RETURNS VOID AS $$
        DECLARE
            v_role_id INTEGER;
            v_perm_id INTEGER;
            v_admin_role_id INTEGER;
            v_mgmt_role_id INTEGER;
        BEGIN
            -- Create account-type roles for the new organization
            
            -- 1. org_admin role
            INSERT INTO service_roles (organization_id, name, display_name, description, is_active, created_at, updated_at)
            VALUES (p_org_id, 'org_admin', 'Organization Administrator', 
                    'Full administrative access to all enabled modules and submodules', 
                    TRUE, NOW(), NOW())
            ON CONFLICT (organization_id, name) DO NOTHING
            RETURNING id INTO v_admin_role_id;
            
            IF v_admin_role_id IS NULL THEN
                SELECT id INTO v_admin_role_id 
                FROM service_roles 
                WHERE organization_id = p_org_id AND name = 'org_admin';
            END IF;
            
            -- 2. management role
            INSERT INTO service_roles (organization_id, name, display_name, description, is_active, created_at, updated_at)
            VALUES (p_org_id, 'management', 'Management', 
                    'Management-level access to all enabled modules and submodules', 
                    TRUE, NOW(), NOW())
            ON CONFLICT (organization_id, name) DO NOTHING
            RETURNING id INTO v_mgmt_role_id;
            
            IF v_mgmt_role_id IS NULL THEN
                SELECT id INTO v_mgmt_role_id 
                FROM service_roles 
                WHERE organization_id = p_org_id AND name = 'management';
            END IF;
            
            -- 3. manager role (delegated access)
            INSERT INTO service_roles (organization_id, name, display_name, description, is_active, created_at, updated_at)
            VALUES (p_org_id, 'manager', 'Manager', 
                    'Manager role with delegated access to specific modules', 
                    TRUE, NOW(), NOW())
            ON CONFLICT (organization_id, name) DO NOTHING;
            
            -- 4. executive role (delegated access)
            INSERT INTO service_roles (organization_id, name, display_name, description, is_active, created_at, updated_at)
            VALUES (p_org_id, 'executive', 'Executive', 
                    'Executive role with delegated access to specific modules', 
                    TRUE, NOW(), NOW())
            ON CONFLICT (organization_id, name) DO NOTHING;
            
            -- Grant all active permissions to org_admin and management roles
            IF v_admin_role_id IS NOT NULL THEN
                INSERT INTO service_role_permissions (role_id, permission_id, created_at)
                SELECT v_admin_role_id, id, NOW()
                FROM service_permissions
                WHERE is_active = TRUE
                ON CONFLICT (role_id, permission_id) DO NOTHING;
            END IF;
            
            IF v_mgmt_role_id IS NOT NULL THEN
                INSERT INTO service_role_permissions (role_id, permission_id, created_at)
                SELECT v_mgmt_role_id, id, NOW()
                FROM service_permissions
                WHERE is_active = TRUE
                ON CONFLICT (role_id, permission_id) DO NOTHING;
            END IF;
            
            RAISE NOTICE 'Successfully seeded account-type roles for organization %', p_org_id;
        EXCEPTION
            WHEN OTHERS THEN
                RAISE WARNING 'Error seeding roles for organization %: %', p_org_id, SQLERRM;
        END;
        $$ LANGUAGE plpgsql;
    """))
    
    # Create trigger
    print("Creating trigger...")
    connection.execute(text("""
        CREATE TRIGGER trigger_seed_account_roles
        AFTER INSERT ON organizations
        FOR EACH ROW
        EXECUTE FUNCTION seed_account_roles_for_org(NEW.id);
    """))
    
    print("Trigger updated successfully")


def downgrade():
    """Restore old trigger (not recommended)."""
    connection = op.get_bind()
    
    print("Dropping updated trigger...")
    connection.execute(text("DROP TRIGGER IF EXISTS trigger_seed_account_roles ON organizations"))
    connection.execute(text("DROP FUNCTION IF EXISTS seed_account_roles_for_org(INTEGER)"))
    
    print("Downgrade complete - old trigger not restored")
    print("Run migration 20251101_04 if you need the old trigger back")
