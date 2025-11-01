"""Simplify permissions model with module/submodule access

Revision ID: 20251101_07_permissions
Revises: 20251101_06_account_roles
Create Date: 2025-11-01

This migration:
1. Seeds canonical permissions for modules and submodules
2. Uses compact naming: module_submodule_action (e.g., crm_leads_view, crm_leads_edit)
3. Automatically grants org_admin and management full access to all permissions
4. Prepares delegation framework for manager and executive roles
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# Revision identifiers, used by Alembic.
revision = '20251101_07_permissions'
down_revision = '20251101_06_account_roles'
branch_labels = None
depends_on = None


# Define canonical permissions for core modules and submodules
# Format: (name, display_name, description, module, action)
CANONICAL_PERMISSIONS = [
    # Organization module (always enabled)
    ('organization_dashboard_view', 'View Organization Dashboard', 'Access to organization overview and statistics', 'organization', 'dashboard_view'),
    ('organization_settings_view', 'View Organization Settings', 'View organization configuration', 'organization', 'settings_view'),
    ('organization_settings_edit', 'Edit Organization Settings', 'Modify organization settings', 'organization', 'settings_edit'),
    ('organization_users_view', 'View Users', 'View organization users list', 'organization', 'users_view'),
    ('organization_users_manage', 'Manage Users', 'Add, edit, or remove users', 'organization', 'users_manage'),
    
    # CRM module
    ('crm_leads_view', 'View CRM Leads', 'Access to CRM leads', 'crm', 'leads_view'),
    ('crm_leads_edit', 'Edit CRM Leads', 'Create and modify CRM leads', 'crm', 'leads_edit'),
    ('crm_leads_delete', 'Delete CRM Leads', 'Delete CRM leads', 'crm', 'leads_delete'),
    ('crm_contacts_view', 'View CRM Contacts', 'Access to CRM contacts', 'crm', 'contacts_view'),
    ('crm_contacts_edit', 'Edit CRM Contacts', 'Create and modify CRM contacts', 'crm', 'contacts_edit'),
    ('crm_opportunities_view', 'View Opportunities', 'Access to opportunities', 'crm', 'opportunities_view'),
    ('crm_opportunities_edit', 'Edit Opportunities', 'Create and modify opportunities', 'crm', 'opportunities_edit'),
    
    # ERP module
    ('erp_dashboard_view', 'View ERP Dashboard', 'Access to ERP overview', 'erp', 'dashboard_view'),
    ('erp_ledger_view', 'View Ledger', 'Access to accounting ledger', 'erp', 'ledger_view'),
    ('erp_ledger_edit', 'Edit Ledger', 'Create and modify ledger entries', 'erp', 'ledger_edit'),
    ('erp_vouchers_view', 'View Vouchers', 'Access to vouchers', 'erp', 'vouchers_view'),
    ('erp_vouchers_edit', 'Edit Vouchers', 'Create and modify vouchers', 'erp', 'vouchers_edit'),
    
    # Inventory module
    ('inventory_products_view', 'View Products', 'Access to product catalog', 'inventory', 'products_view'),
    ('inventory_products_edit', 'Edit Products', 'Create and modify products', 'inventory', 'products_edit'),
    ('inventory_stock_view', 'View Stock', 'Access to stock levels', 'inventory', 'stock_view'),
    ('inventory_stock_edit', 'Edit Stock', 'Adjust stock levels', 'inventory', 'stock_edit'),
    
    # HR module
    ('hr_employees_view', 'View Employees', 'Access to employee records', 'hr', 'employees_view'),
    ('hr_employees_edit', 'Edit Employees', 'Create and modify employee records', 'hr', 'employees_edit'),
    ('hr_attendance_view', 'View Attendance', 'Access to attendance records', 'hr', 'attendance_view'),
    ('hr_payroll_view', 'View Payroll', 'Access to payroll data', 'hr', 'payroll_view'),
    ('hr_payroll_edit', 'Edit Payroll', 'Process payroll', 'hr', 'payroll_edit'),
    
    # Manufacturing module
    ('manufacturing_orders_view', 'View Manufacturing Orders', 'Access to manufacturing orders', 'manufacturing', 'orders_view'),
    ('manufacturing_orders_edit', 'Edit Manufacturing Orders', 'Create and modify manufacturing orders', 'manufacturing', 'orders_edit'),
    ('manufacturing_bom_view', 'View Bill of Materials', 'Access to BOM', 'manufacturing', 'bom_view'),
    ('manufacturing_bom_edit', 'Edit Bill of Materials', 'Create and modify BOM', 'manufacturing', 'bom_edit'),
    
    # Service module
    ('service_tickets_view', 'View Service Tickets', 'Access to service tickets', 'service', 'tickets_view'),
    ('service_tickets_edit', 'Edit Service Tickets', 'Create and modify service tickets', 'service', 'tickets_edit'),
    
    # Analytics module
    ('analytics_reports_view', 'View Analytics Reports', 'Access to analytics and reports', 'analytics', 'reports_view'),
    ('analytics_dashboards_view', 'View Analytics Dashboards', 'Access to custom dashboards', 'analytics', 'dashboards_view'),
    
    # Email module (OAuth-based)
    ('email_accounts_view', 'View Email Accounts', 'Access to email accounts', 'email', 'accounts_view'),
    ('email_accounts_manage', 'Manage Email Accounts', 'Add and configure email accounts', 'email', 'accounts_manage'),
    ('email_messages_view', 'View Emails', 'Read email messages', 'email', 'messages_view'),
    ('email_messages_send', 'Send Emails', 'Send email messages', 'email', 'messages_send'),
]


def upgrade():
    """Seed canonical permissions and grant to org_admin/management roles."""
    connection = op.get_bind()
    
    # Check if required tables exist
    inspector = sa.inspect(connection)
    tables = inspector.get_table_names()
    
    if 'service_permissions' not in tables:
        print("service_permissions table not found, skipping permission seeding")
        return
    
    if 'service_roles' not in tables:
        print("service_roles table not found, skipping permission seeding")
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
    
    # Step 1: Seed canonical permissions
    permission_ids = {}
    permissions_created = 0
    permissions_updated = 0
    
    for perm_def in CANONICAL_PERMISSIONS:
        name, display_name, description, module, action = perm_def
        
        # Check if permission exists
        existing = connection.execute(text(
            "SELECT id FROM service_permissions WHERE name = :name"
        ), {"name": name}).fetchone()
        
        if existing:
            permission_ids[name] = existing[0]
            # Update existing permission
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
            elif has_module and has_action:
                connection.execute(text("""
                    UPDATE service_permissions 
                    SET display_name = :display_name,
                        description = :description,
                        module = :module,
                        action = :action,
                        is_active = TRUE
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
        else:
            # Create new permission
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
    
    # Step 2: Grant all permissions to org_admin and management roles
    admin_roles = ['org_admin', 'management']
    grants_created = 0
    
    for role_name in admin_roles:
        # Get all roles with this name across all orgs
        roles = connection.execute(text("""
            SELECT id, organization_id FROM service_roles 
            WHERE name = :role_name AND is_active = TRUE
        """), {"role_name": role_name}).fetchall()
        
        print(f"\nGranting all permissions to {len(roles)} '{role_name}' roles")
        
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
    
    print(f"\nSummary:")
    print(f"  - Created {permissions_created} new permissions")
    print(f"  - Updated {permissions_updated} existing permissions")
    print(f"  - Created {grants_created} permission grants for org_admin and management roles")


def downgrade():
    """No automatic downgrade - permissions may be in use."""
    print("Downgrade not implemented - permissions may be actively used")
    pass
