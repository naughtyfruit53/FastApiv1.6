"""Fix GST and Settings Permissions for org_admin and management roles

Revision ID: 20251104_01_fix_perms
Revises: 20251103_02
Create Date: 2025-11-04

This migration:
1. Adds GST module permissions (gst_read, gst_view)
2. Adds comprehensive settings permissions
3. Grants all non-admin permissions to management role
4. Ensures org_admin has all permissions
5. Adds audit logging permissions
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text
from datetime import datetime

# Revision identifiers, used by Alembic.
revision = '20251104_01_fix_perms'
down_revision = '20251103_02'
branch_labels = None
depends_on = None


# Define all needed permissions
REQUIRED_PERMISSIONS = [
    # GST Module permissions
    ('gst_read', 'Read GST Data', 'Permission to search and read GST information', 'gst', 'read'),
    ('gst_view', 'View GST', 'Permission to view GST lookup interface', 'gst', 'view'),
    ('gst_search', 'Search GST', 'Permission to perform GST number searches', 'gst', 'search'),
    
    # Settings Module permissions - General
    ('settings_read', 'Read Settings', 'Permission to read organization settings', 'settings', 'read'),
    ('settings_view', 'View Settings', 'Permission to view settings interface', 'settings', 'view'),
    ('settings_create', 'Create Settings', 'Permission to create organization settings', 'settings', 'create'),
    ('settings_update', 'Update Settings', 'Permission to update organization settings', 'settings', 'update'),
    ('settings_delete', 'Delete Settings', 'Permission to delete settings', 'settings', 'delete'),
    
    # Settings Submodule permissions - General Settings (org_admin only)
    ('settings_general_settings_view', 'View General Settings', 'View general organization settings (org_admin only)', 'settings', 'general_settings_view'),
    ('settings_general_settings_update', 'Update General Settings', 'Update general organization settings (org_admin only)', 'settings', 'general_settings_update'),
    
    # Settings Submodule permissions - Voucher Settings
    ('settings_voucher_settings_view', 'View Voucher Settings', 'View voucher configuration settings', 'settings', 'voucher_settings_view'),
    ('settings_voucher_settings_update', 'Update Voucher Settings', 'Update voucher configuration settings', 'settings', 'voucher_settings_update'),
    
    # Voucher Settings - Restricted fields (org_admin only)
    ('settings_voucher_prefix_edit', 'Edit Voucher Prefix', 'Edit voucher number prefix (org_admin only)', 'settings', 'voucher_prefix_edit'),
    ('settings_voucher_counter_edit', 'Edit Voucher Counter', 'Edit counter reset period (org_admin only)', 'settings', 'voucher_counter_edit'),
    
    # Settings Submodule permissions - Other settings
    ('settings_company_profile_view', 'View Company Profile', 'View company profile settings', 'settings', 'company_profile_view'),
    ('settings_company_profile_update', 'Update Company Profile', 'Update company profile settings', 'settings', 'company_profile_update'),
    ('settings_user_management_view', 'View User Management', 'View user management interface', 'settings', 'user_management_view'),
    ('settings_user_management_update', 'Manage Users', 'Create, update, delete users', 'settings', 'user_management_update'),
    
    # Audit and logging
    ('audit_logs_view', 'View Audit Logs', 'Permission to view audit logs', 'admin', 'audit_logs_view'),
    ('audit_logs_export', 'Export Audit Logs', 'Permission to export audit logs', 'admin', 'audit_logs_export'),
    
    # User management permissions
    ('users_create', 'Create Users', 'Permission to create new user accounts', 'organization', 'users_create'),
    ('users_update', 'Update Users', 'Permission to update user accounts', 'organization', 'users_update'),
    ('users_delete', 'Delete Users', 'Permission to delete user accounts', 'organization', 'users_delete'),
    ('users_view', 'View Users', 'Permission to view user list', 'organization', 'users_view'),
]


def upgrade():
    """Add missing permissions and grant them to appropriate roles."""
    connection = op.get_bind()
    
    # Check if required tables exist
    inspector = sa.inspect(connection)
    tables = inspector.get_table_names()
    
    if 'service_permissions' not in tables:
        print("service_permissions table not found, skipping permission seeding")
        return
    
    if 'service_roles' not in tables:
        print("service_roles table not found, skipping permission grants")
        return
    
    if 'service_role_permissions' not in tables:
        print("service_role_permissions table not found, skipping permission grants")
        return
    
    # Check which columns exist
    perm_columns = {col['name']: col for col in inspector.get_columns('service_permissions')}
    has_module = 'module' in perm_columns
    has_action = 'action' in perm_columns
    has_created_at = 'created_at' in perm_columns
    has_updated_at = 'updated_at' in perm_columns
    
    # Step 1: Ensure permissions exist
    permission_ids = {}
    permissions_created = 0
    permissions_updated = 0
    
    for perm_def in REQUIRED_PERMISSIONS:
        name, display_name, description, module, action = perm_def
        
        # Check if permission exists by name
        existing = connection.execute(text(
            "SELECT id FROM service_permissions WHERE name = :name"
        ), {"name": name}).fetchone()
        
        if existing:
            permission_ids[name] = existing[0]
            # Update existing permission to ensure metadata is correct
            if has_module and has_action and has_updated_at:
                connection.execute(text("""
                    UPDATE service_permissions 
                    SET display_name = :display_name,
                        description = :description,
                        module = :module,
                        action = :action,
                        is_active = TRUE,
                        updated_at = NOW()
                    WHERE id = :id
                """), {
                    "id": existing[0],
                    "display_name": display_name,
                    "description": description,
                    "module": module,
                    "action": action
                })
                permissions_updated += 1
                print(f"Updated permission '{name}' (id={existing[0]})")
            continue  # Proceed to next permission
        
        # If not found by name, and module/action columns exist, check by module and action
        if not existing and has_module and has_action:
            existing_by_ma = connection.execute(text(
                "SELECT id FROM service_permissions WHERE module = :module AND action = :action"
            ), {"module": module, "action": action}).fetchone()
            
            if existing_by_ma:
                # Update this existing permission to match our name/display/desc
                connection.execute(text("""
                    UPDATE service_permissions 
                    SET name = :name,
                        display_name = :display_name,
                        description = :description,
                        is_active = TRUE,
                        updated_at = NOW()
                    WHERE id = :id
                """), {
                    "id": existing_by_ma[0],
                    "name": name,
                    "display_name": display_name,
                    "description": description
                })
                permission_ids[name] = existing_by_ma[0]
                permissions_updated += 1
                print(f"Updated existing permission by module/action to '{name}' (id={existing_by_ma[0]})")
                continue  # Skip insert
        
        # If still not found, create new permission
        if has_module and has_action and has_created_at and has_updated_at:
            result = connection.execute(text("""
                INSERT INTO service_permissions (name, display_name, description, module, action, is_active, created_at, updated_at)
                VALUES (:name, :display_name, :description, :module, :action, TRUE, NOW(), NOW())
                RETURNING id
            """), {
                "name": name,
                "display_name": display_name,
                "description": description,
                "module": module,
                "action": action
            })
        elif has_module and has_action and has_created_at:
            result = connection.execute(text("""
                INSERT INTO service_permissions (name, display_name, description, module, action, is_active, created_at)
                VALUES (:name, :display_name, :description, :module, :action, TRUE, NOW())
                RETURNING id
            """), {
                "name": name,
                "display_name": display_name,
                "description": description,
                "module": module,
                "action": action
            })
        elif has_module and has_action:
            result = connection.execute(text("""
                INSERT INTO service_permissions (name, display_name, description, module, action, is_active)
                VALUES (:name, :display_name, :description, :module, :action, TRUE)
                RETURNING id
            """), {
                "name": name,
                "display_name": display_name,
                "description": description,
                "module": module,
                "action": action
            })
        else:
            # Fallback without module/action columns
            result = connection.execute(text("""
                INSERT INTO service_permissions (name, display_name, description, is_active)
                VALUES (:name, :display_name, :description, TRUE)
                RETURNING id
            """), {
                "name": name,
                "display_name": display_name,
                "description": description
            })
        
        perm_id = result.fetchone()[0]
        permission_ids[name] = perm_id
        permissions_created += 1
        print(f"Created permission '{name}' (id={perm_id})")
    
    print(f"\nPermission summary: {permissions_created} created, {permissions_updated} updated")
    
    # Step 2: Define which permissions go to which roles
    role_permissions = {
        'org_admin': list(permission_ids.keys()),  # org_admin gets ALL permissions
        'management': [  # management gets all except admin-only permissions
            p for p in permission_ids.keys()
            if not p.startswith('settings_general_settings')  # Exclude general settings
            and not p.startswith('settings_voucher_prefix')   # Exclude voucher prefix
            and not p.startswith('settings_voucher_counter')  # Exclude voucher counter
        ],
        'manager': [  # manager gets read/view permissions only
            p for p in permission_ids.keys()
            if 'view' in p or 'read' in p
        ],
    }
    
    # Step 3: Grant permissions to roles
    grants_created = 0
    grants_skipped = 0
    
    for role_name, perm_list in role_permissions.items():
        # Get all roles with this name across all orgs
        roles = connection.execute(text("""
            SELECT id, organization_id FROM service_roles 
            WHERE name = :role_name AND is_active = TRUE
        """), {"role_name": role_name}).fetchall()
        
        print(f"\nGranting {len(perm_list)} permissions to {len(roles)} '{role_name}' roles")
        
        for role_row in roles:
            role_id = role_row[0]
            org_id = role_row[1]
            
            for perm_name in perm_list:
                perm_id = permission_ids.get(perm_name)
                if not perm_id:
                    continue
                
                # Check if grant already exists
                existing = connection.execute(text("""
                    SELECT id FROM service_role_permissions 
                    WHERE role_id = :role_id AND permission_id = :perm_id
                """), {"role_id": role_id, "perm_id": perm_id}).fetchone()
                
                if existing:
                    grants_skipped += 1
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
    
    print(f"\nGrant summary: {grants_created} created, {grants_skipped} skipped (already exist)")
    print("\n✅ Migration completed successfully!")
    print("\nKey changes:")
    print("- GST search permissions added and granted to org_admin and management")
    print("- Settings permissions properly configured with role-based access")
    print("- Voucher prefix and counter restrictions added for org_admin only")
    print("- Management role granted full access except admin-only features")


def downgrade():
    """Do not revoke permissions - they may be in use."""
    print("Downgrade not implemented - permissions may be in use")
    print("To manually remove: DELETE FROM service_permissions WHERE name IN (...)")
    pass