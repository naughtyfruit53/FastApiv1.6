# MegaMenu Permission Guide

## Overview

The MegaMenu system uses a comprehensive RBAC (Role-Based Access Control) approach to filter menu items based on user permissions. This guide explains how permissions are checked and how to troubleshoot menu visibility issues.

## Permission Structure

### Permission Format

The system supports two permission formats:

1. **Dot Notation** (General Modules): `<module>.<action>`
   - Example: `master_data.read`, `inventory.create`, `finance.update`
   - Used for: Main ERP modules (Master Data, Inventory, Manufacturing, Vouchers, Finance, etc.)

2. **Underscore Notation** (Service CRM): `<module>_<action>`
   - Example: `service_create`, `technician_read`, `appointment_update`
   - Used for: Service CRM specific permissions

### Supported Modules

As defined in `/frontend/src/types/rbac.types.ts`:

- `master_data` - Master Data (Vendors, Customers, Products, etc.)
- `inventory` - Inventory Management
- `manufacturing` - Manufacturing Operations
- `vouchers` - Purchase, Sales, and Financial Vouchers
- `finance` - Finance & Accounts Payable/Receivable
- `accounting` - Accounting & Chart of Accounts
- `reports` - Reports & Analytics
- `ai_analytics` - AI & Advanced Analytics
- `sales` - Sales CRM
- `marketing` - Marketing Campaigns
- `service` - Service Desk & CRM
- `projects` - Project Management
- `hr` - HR Management
- `tasks_calendar` - Tasks & Calendar
- `email` - Email Management
- `settings` - System Settings

### Supported Actions

- `create` - Permission to create new records
- `read` - Permission to view/read records
- `update` - Permission to edit/update records
- `delete` - Permission to delete records
- `export` - Permission to export data
- `admin` - Administrative access

## Menu Item Permission Configuration

### Basic Permission Check

Each menu item in `menuConfig.tsx` can specify permissions using three properties:

```typescript
{
  name: 'Vendors',
  path: '/masters/vendors',
  icon: <People />,
  permission: 'master_data.read',           // Basic permission check
  requireModule: 'master_data',              // Module-level access check
  requireSubmodule: {                        // Submodule-level access check
    module: 'master_data',
    submodule: 'vendors'
  }
}
```

### Permission Check Logic

The menu filtering system (`MegaMenu.tsx`) performs checks in the following order:

1. **Super Admin Bypass**: Super admins can access all items (unless `godSuperAdminOnly` is set)
2. **God Super Admin Check**: Items marked `godSuperAdminOnly` only visible to naughtyfruit53@gmail.com
3. **Super Admin Only Items**: Items marked `superAdminOnly` only visible to app super admins
4. **Permission Check**: If `item.permission` is set, checks if user has that specific permission
5. **Module Access**: If `item.requireModule` is set, checks if user has access to that module
6. **Enabled Modules**: Checks if the module is enabled in organization settings
7. **Submodule Access**: If `item.requireSubmodule` is set, checks specific submodule access

## Menu Expansion Behavior

### Auto-Expansion

When a user clicks on a top-level menu:

1. The menu automatically selects the first section with accessible items
2. Items are displayed immediately instead of showing an empty menu
3. If no items are accessible, a helpful error message is shown

### Fallback UI

If a user has no access to any items in a menu section:

```
No Menu Items Available

You don't have permission to access any items in this menu, 
or the required modules are not enabled for your organization.

Contact your administrator to request access or enable required modules.
```

## Troubleshooting

### Menu Items Not Visible

**Problem**: Expected menu items don't appear for a user

**Checklist**:

1. **Check User Permissions**:
   - Verify user has correct role assigned
   - Check RBAC permissions via `/rbac/users/{user_id}/permissions`
   - Confirm permission format matches menu item (dot notation vs underscore)

2. **Check Organization Modules**:
   - Verify module is enabled in organization settings
   - Check `enabled_modules` in organization data
   - Module must be both enabled AND user must have permissions

3. **Check Menu Configuration**:
   - Verify `permission` key matches backend RBAC format
   - Confirm `requireModule` matches Module enum values
   - Check `requireSubmodule` module/submodule names are correct

4. **Browser Console Logs**:
   - Open browser developer tools
   - Check for permission check failure logs:
     ```
     Permission check failed for item <name>: requires <permission>
     Module access check failed for item <name>: requires module <module>
     Submodule access check failed for item <name>: requires <module>.<submodule>
     ```

### Menu Doesn't Expand

**Problem**: Clicking menu shows no content

**Solutions**:

1. Check if first section has any permitted items
2. Verify useEffect hook is selecting first section
3. Check browser console for filtering warnings
4. Manually select a section to see if items appear

### Permission Format Mismatch

**Problem**: Permissions in database don't match menu requirements

**Common Mismatches**:

- Backend uses `master_data_read` but menu expects `master_data.read`
- Solution: Update menu config OR backend permission names to match

### Module Not Enabled

**Problem**: User has permissions but items still hidden

**Solution**:

1. Navigate to Organization Settings
2. Check "Enabled Modules" section
3. Enable required modules for the organization
4. Refresh page and check menu again

## API Endpoints

### Get User Permissions

```
GET /rbac/users/{user_id}/permissions
```

Returns:
```json
{
  "user_id": 123,
  "permissions": ["master_data.read", "inventory.read", ...],
  "service_roles": [...],
  "total_permissions": 25
}
```

### Get Current User Permissions

```
GET /users/me
```

Returns user object with role and organization data.

### Get Organization Data

```
GET /organizations/current
```

Returns organization with `enabled_modules` object.

## Implementation Details

### AuthContext Integration

The `useAuth` hook from `AuthContext` provides:
- `user` - Current user object
- `userPermissions` - User's RBAC permissions including:
  - `role` - User's role name
  - `permissions` - Array of permission strings
  - `modules` - Array of accessible modules
  - `submodules` - Object mapping modules to submodule arrays

### useSharedPermissions Hook

Provides helper functions:
- `hasPermission(permission)` - Check specific permission
- `hasModuleAccess(module)` - Check module access
- `hasSubmoduleAccess(module, submodule)` - Check submodule access

### Wildcard Permissions

The system supports wildcard permissions:
- `finance.*` grants all finance permissions
- `inventory.*` grants all inventory permissions
- Super admins automatically get `*.*` (all permissions)

## Adding New Menu Items

### Step 1: Define Permission in Backend

Add to `/app/core/permissions.py` or RBAC service:

```python
# If using dot notation
MASTER_DATA_READ = "master_data.read"

# If using underscore notation
SERVICE_CREATE = "service_create"
```

### Step 2: Add to Menu Config

Update `/frontend/src/components/menuConfig.tsx`:

```typescript
{
  name: 'New Feature',
  path: '/new-feature',
  icon: <NewIcon />,
  permission: 'master_data.read',        // Must match backend
  requireModule: 'master_data',          // Module enum value
  requireSubmodule: {                     // Optional
    module: 'master_data',
    submodule: 'new_feature'
  }
}
```

### Step 3: Test with Multiple Roles

1. Test as Super Admin - should see item
2. Test as user WITH permission - should see item
3. Test as user WITHOUT permission - should NOT see item
4. Check browser console for permission check logs

## Best Practices

1. **Consistent Naming**: Use same format (dot or underscore) throughout
2. **Granular Permissions**: Use module.action format for fine-grained control
3. **Module Enablement**: Always check both permissions AND enabled modules
4. **Clear Logging**: Permission check failures are logged to console
5. **Fallback UI**: Always show helpful message when no items available
6. **Auto-Expansion**: Menus should auto-select first accessible section
7. **Testing**: Test with multiple user roles before deploying

## Common Permission Patterns

### Read-Only Access
```typescript
permission: 'module.read'
```

### Full CRUD Access
Multiple items with different permissions:
```typescript
permission: 'module.create'  // Create button
permission: 'module.read'    // View list
permission: 'module.update'  // Edit button
permission: 'module.delete'  // Delete button
```

### Admin-Only Features
```typescript
superAdminOnly: true,  // For app super admins
// OR
godSuperAdminOnly: true  // For god user only
// OR
permission: 'admin'  // For any admin
```

## Support

For issues or questions:
1. Check browser console logs for permission failures
2. Verify backend permission definitions match frontend
3. Confirm organization modules are enabled
4. Contact system administrator for role/permission changes

## Version History

- v1.0 (2025-01-29): Initial menu permission system with RBAC integration
- v1.1 (2025-01-29): Added auto-expansion and fallback UI
- v1.2 (2025-01-29): Enhanced permission logging and documentation
