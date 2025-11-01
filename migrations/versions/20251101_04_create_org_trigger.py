"""Create trigger to auto-seed roles and permissions for new organizations

Revision ID: 20251101_04_trigger
Revises: 20251101_03_grant_perms
Create Date: 2025-11-01

This migration creates a PostgreSQL trigger that automatically:
1. Creates default service_roles (admin, org_admin) for new organizations
2. Grants organization permissions to those roles
3. Ensures new orgs have proper RBAC setup from creation
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# Revision identifiers, used by Alembic.
revision = '20251101_04_trigger'
down_revision = '20251101_03_grant_perms'
branch_labels = None
depends_on = None


def upgrade():
    """Create trigger function and trigger for new organizations."""
    connection = op.get_bind()
    
    # Check if we're on PostgreSQL
    dialect_name = connection.dialect.name
    if dialect_name != 'postgresql':
        print(f"Skipping trigger creation - not supported on {dialect_name}")
        return
    
    # Check if required tables exist
    inspector = sa.inspect(connection)
    tables = inspector.get_table_names()
    
    required_tables = ['organizations', 'service_roles', 'service_permissions', 'service_role_permissions']
    if not all(table in tables for table in required_tables):
        print(f"One or more required tables not found, skipping trigger creation")
        return
    
    # Drop existing trigger and function if they exist
    connection.execute(text("""
        DROP TRIGGER IF EXISTS trigger_seed_org_roles ON organizations;
    """))
    
    connection.execute(text("""
        DROP FUNCTION IF EXISTS seed_roles_and_grants_for_org(INTEGER);
    """))
    
    print("Creating seed_roles_and_grants_for_org function...")
    
    # Create the function that seeds roles and grants
    connection.execute(text("""
        CREATE OR REPLACE FUNCTION seed_roles_and_grants_for_org(p_org_id INTEGER)
        RETURNS VOID AS $$
        DECLARE
            v_admin_role_id INTEGER;
            v_org_admin_role_id INTEGER;
            v_perm_view_id INTEGER;
            v_perm_read_id INTEGER;
        BEGIN
            -- Log the operation
            RAISE NOTICE 'Seeding roles and grants for organization %', p_org_id;
            
            -- Create admin role for this org (if not exists)
            INSERT INTO service_roles (organization_id, name, display_name, description, is_active, created_at, updated_at)
            VALUES (p_org_id, 'admin', 'Administrator', 'Full administrative access to all organization features', TRUE, NOW(), NOW())
            ON CONFLICT (organization_id, name) DO NOTHING
            RETURNING id INTO v_admin_role_id;
            
            -- If we didn't insert (already existed), fetch the existing id
            IF v_admin_role_id IS NULL THEN
                SELECT id INTO v_admin_role_id
                FROM service_roles
                WHERE organization_id = p_org_id AND name = 'admin'
                LIMIT 1;
            END IF;
            
            -- Create org_admin role for this org (if not exists)
            INSERT INTO service_roles (organization_id, name, display_name, description, is_active, created_at, updated_at)
            VALUES (p_org_id, 'org_admin', 'Organization Admin', 'Organization-level administrative access', TRUE, NOW(), NOW())
            ON CONFLICT (organization_id, name) DO NOTHING
            RETURNING id INTO v_org_admin_role_id;
            
            -- If we didn't insert (already existed), fetch the existing id
            IF v_org_admin_role_id IS NULL THEN
                SELECT id INTO v_org_admin_role_id
                FROM service_roles
                WHERE organization_id = p_org_id AND name = 'org_admin'
                LIMIT 1;
            END IF;
            
            -- Get permission IDs (create if they don't exist)
            SELECT id INTO v_perm_view_id
            FROM service_permissions
            WHERE name = 'admin_organizations_view'
            LIMIT 1;
            
            IF v_perm_view_id IS NULL THEN
                INSERT INTO service_permissions (name, display_name, description, module, action, is_active, created_at, updated_at)
                VALUES ('admin_organizations_view', 'View Organization Dashboard', 'Permission to view organization dashboard and statistics', 'admin', 'organizations_view', TRUE, NOW(), NOW())
                RETURNING id INTO v_perm_view_id;
            END IF;
            
            SELECT id INTO v_perm_read_id
            FROM service_permissions
            WHERE name = 'admin_organizations_read'
            LIMIT 1;
            
            IF v_perm_read_id IS NULL THEN
                INSERT INTO service_permissions (name, display_name, description, module, action, is_active, created_at, updated_at)
                VALUES ('admin_organizations_read', 'Read Organization Data', 'Permission to read organization-level data and activities', 'admin', 'organizations_read', TRUE, NOW(), NOW())
                RETURNING id INTO v_perm_read_id;
            END IF;
            
            -- Grant permissions to admin role
            IF v_admin_role_id IS NOT NULL THEN
                INSERT INTO service_role_permissions (role_id, permission_id, created_at)
                VALUES (v_admin_role_id, v_perm_view_id, NOW())
                ON CONFLICT (role_id, permission_id) DO NOTHING;
                
                INSERT INTO service_role_permissions (role_id, permission_id, created_at)
                VALUES (v_admin_role_id, v_perm_read_id, NOW())
                ON CONFLICT (role_id, permission_id) DO NOTHING;
            END IF;
            
            -- Grant permissions to org_admin role
            IF v_org_admin_role_id IS NOT NULL THEN
                INSERT INTO service_role_permissions (role_id, permission_id, created_at)
                VALUES (v_org_admin_role_id, v_perm_view_id, NOW())
                ON CONFLICT (role_id, permission_id) DO NOTHING;
                
                INSERT INTO service_role_permissions (role_id, permission_id, created_at)
                VALUES (v_org_admin_role_id, v_perm_read_id, NOW())
                ON CONFLICT (role_id, permission_id) DO NOTHING;
            END IF;
            
            RAISE NOTICE 'Successfully seeded roles and grants for organization %', p_org_id;
        EXCEPTION
            WHEN OTHERS THEN
                RAISE WARNING 'Error seeding roles for org %: %', p_org_id, SQLERRM;
        END;
        $$ LANGUAGE plpgsql;
    """))
    
    print("Creating trigger on organizations table...")
    
    # Create the trigger
    connection.execute(text("""
        CREATE TRIGGER trigger_seed_org_roles
        AFTER INSERT ON organizations
        FOR EACH ROW
        EXECUTE FUNCTION seed_roles_and_grants_for_org(NEW.id);
    """))
    
    print("Trigger created successfully!")
    print("New organizations will automatically get admin and org_admin roles with organization permissions")


def downgrade():
    """Drop the trigger and function."""
    connection = op.get_bind()
    
    # Check if we're on PostgreSQL
    if connection.dialect.name != 'postgresql':
        return
    
    print("Dropping trigger and function...")
    
    connection.execute(text("""
        DROP TRIGGER IF EXISTS trigger_seed_org_roles ON organizations;
    """))
    
    connection.execute(text("""
        DROP FUNCTION IF EXISTS seed_roles_and_grants_for_org(INTEGER);
    """))
    
    print("Trigger and function dropped")
