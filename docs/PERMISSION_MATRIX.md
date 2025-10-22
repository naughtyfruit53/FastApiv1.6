# Permission Matrix

This document provides a comprehensive overview of the permission system in the application, including role-based access control (RBAC), permission assignments, and audit logging.

## Table of Contents

1. [Overview](#overview)
2. [Role Hierarchy](#role-hierarchy)
3. [Permission Types](#permission-types)
4. [Role-Permission Mapping](#role-permission-mapping)
5. [Module-Specific Permissions](#module-specific-permissions)
6. [How to Request Permissions](#how-to-request-permissions)
7. [Troubleshooting Permission Issues](#troubleshooting-permission-issues)

## Overview

The application uses a hierarchical role-based permission system with two levels:
- **Platform Level**: Super admins and platform admins who manage the entire system
- **Organization Level**: Organization admins, management, managers, and executives who work within specific organizations

## Role Hierarchy

### Platform Roles

| Role | Level | Description |
|------|-------|-------------|
| `super_admin` | Platform | Highest level access, can manage all organizations and platform settings |
| `platform_admin` | Platform | Can manage organizations but with limited platform settings access |

### Organization Roles

| Role | Level | Description |
|------|-------|-------------|
| `org_admin` | Organization | Administrator for a specific organization |
| `management` | Organization | Management level user with elevated permissions |
| `manager` | Organization | Middle management, can manage executives |
| `executive` | Organization | Basic user role with limited permissions |

## Permission Types

### User Management Permissions

- `manage_users` - Create, update, delete users
- `view_users` - View user information
- `create_users` - Create new users
- `delete_users` - Delete users

### Password Management Permissions

- `reset_own_password` - Reset own password
- `reset_org_passwords` - Reset passwords within organization
- `reset_any_password` - Reset any user's password (platform level)

### Data Management Permissions

- `reset_own_data` - Reset own data
- `reset_org_data` - Reset organization data
- `reset_any_data` - Reset any organization's data (platform level)

### Organization Management Permissions

- `manage_organizations` - Full organization management
- `view_organizations` - View organization details
- `create_organizations` - Create new organizations
- `delete_organizations` - Delete organizations

### Platform Administration Permissions

- `platform_admin` - Platform administrator access
- `super_admin` - Super administrator access
- `factory_reset` - Perform factory reset (highest level)

### Audit Permissions

- `view_audit_logs` - View audit logs for own organization
- `view_all_audit_logs` - View audit logs for all organizations

### Voucher Permissions

- `view_vouchers` - View vouchers
- `manage_vouchers` - Create, update, delete vouchers

### CRM Permissions

- `crm_lead_read` - View leads
- `crm_lead_create` - Create leads
- `crm_lead_update` - Update leads
- `crm_lead_delete` - Delete leads
- `crm_lead_manage_all` - Manage all leads in organization
- `crm_opportunity_read` - View opportunities
- `crm_opportunity_create` - Create opportunities
- `crm_opportunity_update` - Update opportunities
- `crm_opportunity_delete` - Delete opportunities
- `crm_commission_read` - View commissions
- `crm_commission_create` - Create commissions
- `crm_commission_update` - Update commissions
- `crm_commission_delete` - Delete commissions
- `crm_admin` - CRM administrator access

### Service Module Permissions

- `service_create` - Create service records
- `service_read` - View service records
- `service_update` - Update service records
- `service_delete` - Delete service records
- `technician_create` - Create technician records
- `technician_read` - View technician records
- `technician_update` - Update technician records
- `technician_delete` - Delete technician records
- `appointment_create` - Create appointments
- `appointment_read` - View appointments
- `appointment_update` - Update appointments
- `appointment_delete` - Delete appointments

## Role-Permission Mapping

### Platform Super Admin

Platform super admins have access to ALL permissions, including:
- All user management permissions
- All password management permissions
- All data management permissions
- All organization management permissions
- All platform administration permissions
- All audit permissions
- Factory reset capability

### Platform Admin

Platform admins have:
- `platform_admin`
- `manage_organizations`
- `create_organizations`
- `view_organizations`
- `reset_any_password`
- `view_audit_logs`

### Organization Admin

Organization admins have:
- `manage_users`
- `view_users`
- `create_users`
- `delete_users`
- `reset_own_password`
- `reset_org_passwords`
- `reset_own_data`
- `reset_org_data`
- `view_audit_logs`
- `access_org_settings`
- `view_vouchers`
- `manage_vouchers`

### Management

Management level users have:
- `view_users`
- `reset_own_password`
- `reset_org_passwords`
- `reset_own_data`
- `reset_org_data`
- `view_audit_logs`
- `access_org_settings`
- `view_vouchers`
- `manage_vouchers`

### Manager

Managers have:
- `view_users`
- `create_users` (can create executives)
- `reset_own_password`
- `view_audit_logs`
- `access_org_settings` (limited)
- `view_vouchers`

### Executive

Executives have:
- `reset_own_password`
- `access_org_settings` (basic)
- `view_vouchers`

## Module-Specific Permissions

### CRM Module

To access CRM features, users need one or more of the following permissions:

**Leads:**
- `crm_lead_read` - Required to view the leads page
- `crm_lead_create` - Required to create new leads
- `crm_lead_update` - Required to edit leads
- `crm_lead_delete` - Required to delete leads
- `crm_lead_manage_all` - Allows viewing and managing all leads in the organization

**Opportunities:**
- `crm_opportunity_read` - Required to view opportunities
- `crm_opportunity_create` - Required to create opportunities
- `crm_opportunity_update` - Required to edit opportunities
- `crm_opportunity_delete` - Required to delete opportunities

**Commissions:**
- `crm_commission_read` - **Required** to view the commission tracking page
- `crm_commission_create` - Required to create commission records
- `crm_commission_update` - Required to edit commission records
- `crm_commission_delete` - Required to delete commission records

**Admin:**
- `crm_admin` - Full CRM administrator access, overrides other CRM permissions

### Sales Module

**Reports:**
- No specific permission required for viewing reports
- Export functionality requires general read access to the module

**Commissions:**
- See CRM Module permissions above

### Voucher Module

- `view_vouchers` - Required to view vouchers
- `manage_vouchers` - Required to create, update, or delete vouchers

## How to Request Permissions

If you encounter a permission error, follow these steps:

### For Organization Users

1. Contact your organization administrator
2. Specify which feature you need access to (e.g., "Commission Tracking")
3. Your organization admin can assign the required role or specific permissions through the user management interface

### For Platform-Level Access

1. Contact the platform super administrator
2. Explain your use case and required access level
3. Platform admin will evaluate and grant appropriate permissions

### Error Messages

When you lack a permission, you'll see error messages like:

- **403 Forbidden**: "Insufficient permissions to view commissions. Required permission: 'crm_commission_read'. Please contact your administrator to request access."
- **403 Forbidden**: "Insufficient permissions to manage organizations. This action requires platform administrator access."

## Troubleshooting Permission Issues

### Issue: "Insufficient permissions to view commissions"

**Solution:**
1. Ensure you have the `crm_commission_read` permission
2. Contact your organization admin to request this permission
3. If you're an org admin, check that the CRM module is enabled for your organization

### Issue: "You don't have permission to manage organizations"

**Solution:**
1. This requires platform administrator access
2. Only platform super admins or platform admins can manage organizations
3. Contact your platform administrator if you believe you should have this access

### Issue: Company details (GST number, state code) not saving

**Solution:**
1. Ensure you have `org_admin` role or higher
2. Verify all required fields are filled in
3. Check that the form is properly submitted (no validation errors)
4. Contact support if the issue persists after fixing validation errors

### Issue: Sales report export fails

**Solution:**
1. Ensure there is data available for the selected time range
2. Check your browser console for specific error messages
3. Try a different time range or report type
4. Contact support if the issue persists with proper data

## Audit Logging

All permission checks and denials are logged in the audit system. Administrators can review:
- Who attempted what action
- When the attempt was made
- Why the permission was denied
- IP address and user agent information

To view audit logs:
1. Navigate to the Audit Logs section (requires `view_audit_logs` permission)
2. Filter by user, action type, or date range
3. Review denied permission attempts to identify permission issues

## Permission Assignment UI

### For Organization Admins

1. Navigate to **Users** > **User Management**
2. Select the user you want to modify
3. Click **Edit User** or **Manage Permissions**
4. Select the appropriate role from the dropdown
5. For fine-grained control, check/uncheck specific permissions
6. Save changes

### For Platform Admins

1. Navigate to **Admin** > **User Management** or **License Management**
2. Select the organization or platform user
3. Update roles through the user management interface
4. Changes take effect immediately

## Related Documentation

- [RBAC Implementation Summary](RBAC_IMPLEMENTATION_SUMMARY.md)
- [RBAC Fixes Summary](RBAC_FIXES_SUMMARY.md)
- [CRM Usage Guide](CRM_USAGE_GUIDE.md)
- [Authentication & Permission Foundation](AUTHENTICATION_PERMISSION_FOUNDATION.md)

## Support

For additional help with permissions:
- Contact your organization administrator
- Contact platform support
- Review error messages carefully for specific permission requirements
- Check audit logs to see permission denial reasons
