# RBAC Account-Type Roles Implementation Guide

## Overview

This document describes the new account-type RBAC system that replaces the legacy role-based access control with a simplified, organization-scoped hierarchy.

## Account-Type Roles

The system now uses four standardized roles per organization:

### 1. **org_admin** (Organization Administrator)
- **Purpose**: Full administrative access to all enabled modules and submodules
- **Automatic Permissions**: Automatically receives all permissions for any module enabled in the organization
- **Capabilities**:
  - Full access to all organization features
  - Can delegate permissions to manager and executive roles
  - Can manage users and organization settings
  - Cannot be restricted from any enabled module

### 2. **management** (Management)
- **Purpose**: Management-level access equivalent to org_admin
- **Automatic Permissions**: Automatically receives all permissions for any module enabled in the organization
- **Capabilities**:
  - Full access to all organization features
  - Can delegate permissions to manager and executive roles
  - Typically used for senior management team
  - Cannot be restricted from any enabled module

### 3. **manager** (Manager)
- **Purpose**: Middle management with delegated access
- **Permissions**: Must be explicitly delegated by org_admin or management
- **Capabilities**:
  - Access only to explicitly granted modules and submodules
  - Cannot delegate permissions to other roles
  - Suitable for department heads or team leads

### 4. **executive** (Executive)
- **Purpose**: Executive-level access with delegated permissions
- **Permissions**: Must be explicitly delegated by org_admin or management
- **Capabilities**:
  - Access only to explicitly granted modules and submodules
  - Cannot delegate permissions to other roles
  - Suitable for executives who need specific module access

## Permission Model

### Module and Submodule Permissions

Permissions follow a compact naming convention:
```
{module}_{submodule}_{action}
```

Examples:
- `organization_dashboard_view` - View organization dashboard
- `crm_leads_view` - View CRM leads
- `crm_leads_edit` - Create and modify CRM leads
- `erp_vouchers_view` - View ERP vouchers
- `email_accounts_manage` - Manage email accounts (OAuth-based)

### Automatic Permission Grants

When a module is enabled in `organizations.enabled_modules`:
1. The system automatically grants ALL permissions for that module to `org_admin` and `management` roles
2. The module permissions are available for delegation to `manager` and `executive` roles

## Database Migrations

### Migration 20251101_06: Reset to Account-Type Roles
- Creates the four standard roles for all existing organizations
- Marks legacy roles (admin, support, viewer) as inactive
- Idempotent and safe to run multiple times

### Migration 20251101_07: Simplify Permissions Model
- Seeds canonical permissions for all core modules
- Automatically grants all permissions to org_admin and management roles
- Prepares permissions for delegation

### Migration 20251101_08: Update Organization Trigger
- Updates the auto-seeding trigger for new organizations
- Ensures new organizations automatically get the four standard roles
- Grants all active permissions to org_admin and management

## API Endpoints

### Role Delegation APIs

#### Delegate Permissions
```http
POST /api/v1/role-delegation/delegate
Content-Type: application/json
Authorization: Bearer <token>

{
  "target_role_name": "manager",
  "permission_names": [
    "crm_leads_view",
    "crm_leads_edit",
    "crm_contacts_view"
  ]
}
```

**Response:**
```json
{
  "success": true,
  "message": "Delegated 3 permissions to manager",
  "granted_permissions": ["crm_leads_view", "crm_leads_edit", "crm_contacts_view"],
  "failed_permissions": []
}
```

#### Revoke Permissions
```http
POST /api/v1/role-delegation/revoke
Content-Type: application/json
Authorization: Bearer <token>

{
  "target_role_name": "executive",
  "permission_names": [
    "erp_vouchers_edit"
  ]
}
```

**Response:**
```json
{
  "success": true,
  "message": "Revoked 1 permissions from executive",
  "revoked_permissions": ["erp_vouchers_edit"],
  "failed_permissions": []
}
```

#### Get Role Permissions
```http
GET /api/v1/role-delegation/role/{role_name}/permissions
Authorization: Bearer <token>
```

**Response:**
```json
{
  "role_name": "manager",
  "role_id": 123,
  "organization_id": 456,
  "permissions": [
    {
      "id": 1,
      "name": "crm_leads_view",
      "display_name": "View CRM Leads",
      "description": "Access to CRM leads",
      "module": "crm",
      "action": "leads_view"
    }
  ]
}
```

## Access Control

### Who Can Delegate?
- Only users with `org_admin` or `management` roles can delegate permissions
- Delegation is only allowed to `manager` and `executive` roles
- `org_admin` and `management` cannot have their permissions restricted

### Module Enablement Flow

1. **Enable Module in Organization**
   ```json
   {
     "enabled_modules": {
       "organization": true,
       "crm": true,
       "erp": true
     }
   }
   ```

2. **System automatically grants all module permissions to org_admin and management**

3. **org_admin/management delegates specific permissions to manager/executive**
   ```http
   POST /api/v1/role-delegation/delegate
   {
     "target_role_name": "manager",
     "permission_names": ["crm_leads_view", "crm_leads_edit"]
   }
   ```

## Email Integration (OAuth-based)

The system now uses OAuth2 for email integration instead of SnappyMail:

### Supported Providers
- Google (Gmail)
- Microsoft (Outlook/Office 365)
- Generic XOAUTH2

### Email Permissions
- `email_accounts_view` - View email accounts
- `email_accounts_manage` - Add and configure email accounts (OAuth)
- `email_messages_view` - Read email messages
- `email_messages_send` - Send email messages

### OAuth Token Storage
- Tokens are encrypted using AES-GCM encryption
- Stored in `user_email_tokens` table
- Automatic token refresh supported
- Background sync enabled for inbox synchronization

## Migration from Legacy Roles

### Before (Legacy System)
- Multiple custom roles per organization (admin, manager, support, viewer)
- Complex permission assignments
- Manual permission management for each module

### After (Account-Type System)
- Four standardized roles: org_admin, management, manager, executive
- Automatic permission grants for org_admin and management
- Simple delegation model for manager and executive

### Migration Process
1. Run migrations 20251101_06, 20251101_07, 20251101_08
2. Legacy roles are marked inactive (not deleted)
3. Users with legacy roles need to be reassigned to account-type roles
4. Historical data is preserved

## Best Practices

1. **Use org_admin sparingly**: Only assign to users who truly need full access
2. **Leverage management role**: Use for senior team members who need broad access
3. **Delegate specifically**: Grant only necessary permissions to manager/executive roles
4. **Review periodically**: Regularly audit role assignments and delegated permissions
5. **Enable modules carefully**: When enabling new modules, review who needs access

## Troubleshooting

### Permission Denied Errors
- Check if user has the appropriate role assigned
- For manager/executive, verify permissions have been delegated
- Check if module is enabled in organization settings

### Delegation Not Working
- Ensure you have org_admin or management role
- Verify target role exists and is active
- Check that permission names are correct

### Module Access Issues
- Confirm module is enabled in `organizations.enabled_modules`
- Verify migrations have been run successfully
- Check that org_admin/management roles have been seeded

## Security Considerations

1. **Role Hierarchy**: org_admin and management cannot be restricted
2. **Delegation Control**: Only top-level roles can delegate
3. **Audit Trail**: All permission changes are logged
4. **Token Security**: OAuth tokens are encrypted at rest
5. **Organization Isolation**: All roles are organization-scoped

## Support

For issues or questions:
- Check migration logs for any errors
- Review API response messages for specific failures
- Consult database logs for permission grant/revoke operations
