# MegaMenu Permission Guide v2.0 - Strict Enforcement

## Overview

The MegaMenu system uses **strict RBAC (Role-Based Access Control)** with **mandatory entitlement checks** to control menu access. This guide explains the new strict enforcement model where all users, including super admins, must have explicit permissions and entitlements.

## 🔒 Key Changes in v2.0

### What's New?

1. **No Super Admin Bypass**: Super admins must have explicit permissions
2. **Entitlement + Permission**: Both must be present for access
3. **Fail-Closed by Default**: Unknown modules are disabled, not enabled
4. **Clear Error Messages**: Users see exactly why access is denied
5. **No Fallback Logic**: Errors are shown, not hidden

### Breaking Changes

⚠️ **Super admins no longer have automatic access to all menus**
⚠️ **Unknown modules default to disabled (was enabled)**
⚠️ **Missing permissions always deny access**

---

## Permission Structure

### Permission Format

The system supports two permission formats:

1. **Dot Notation** (General Modules): `<module>.<action>`
   - Example: `master_data.read`, `inventory.create`, `finance.update`
   - Used for: Main ERP modules

2. **Underscore Notation** (Service CRM): `<module>_<action>`
   - Example: `service_create`, `technician_read`, `appointment_update`
   - Used for: Service CRM specific permissions

### Supported Modules

Organized by entitlement type:

#### Billable Modules (Require Entitlements)
- `sales` - Sales CRM
- `crm` - Customer Relationship Management
- `manufacturing` - Manufacturing Operations
- `inventory` - Inventory Management
- `finance` - Finance & Accounts
- `accounting` - Accounting & Chart of Accounts
- `hr` - HR Management
- `ai_analytics` - AI & Advanced Analytics
- `marketing` - Marketing Campaigns
- `projects` - Project Management

#### Non-Billable Modules (Always Available)
- `email` - Email Management (always-on)
- `settings` - System Settings (RBAC-only)
- `admin` - Platform Administration (RBAC-only)
- `organization` - Organization Management (RBAC-only)

#### ERP Core Modules (Configurable)
- `master_data` - Master Data Management
- `vouchers` - Purchase, Sales, Financial Vouchers
- `reports` - Reports & Analytics
- `tasks_calendar` - Tasks & Calendar

### Supported Actions

- `create` - Create new records
- `read` - View/read records
- `update` - Edit/update records
- `delete` - Delete records
- `export` - Export data
- `admin` - Administrative access

---

## Menu Access Logic

### Access Evaluation Flow

```
User Attempts to Access Menu Item
        ↓
1. Is it email/settings/admin?
   YES → ✅ ALLOW (non-billable)
   NO → Continue to step 2
        ↓
2. Does user's org have module entitlement?
   NO → ❌ DENY (show disabled with lock icon)
   YES → Continue to step 3
        ↓
3. Is module in trial?
   YES → Check trial expiration
         Expired? → ❌ DENY
         Active? → Continue to step 4
   NO → Continue to step 4
        ↓
4. Does user have required permission?
   NO → ❌ DENY (show disabled with lock icon)
   YES → ✅ ALLOW (show enabled)
```

### Decision Matrix

| Entitlement | Permission | Super Admin? | Result |
|-------------|------------|--------------|--------|
| ❌ Missing  | ❌ Missing | ❌ No       | ❌ DENIED |
| ❌ Missing  | ❌ Missing | ✅ Yes      | ❌ DENIED (NEW!) |
| ❌ Missing  | ✅ Has     | ❌ No       | ❌ DENIED |
| ❌ Missing  | ✅ Has     | ✅ Yes      | ❌ DENIED (NEW!) |
| ✅ Has      | ❌ Missing | ❌ No       | ❌ DENIED |
| ✅ Has      | ❌ Missing | ✅ Yes      | ❌ DENIED (NEW!) |
| ✅ Has      | ✅ Has     | ❌ No       | ✅ ALLOWED |
| ✅ Has      | ✅ Has     | ✅ Yes      | ✅ ALLOWED |

---

## Menu Item Configuration

### Example: Sales Dashboard

```typescript
{
  name: 'Sales Dashboard',
  path: '/sales/dashboard',
  icon: <Dashboard />,
  permission: 'sales.read',           // RBAC permission required
  requireModule: 'sales',             // Entitlement required
  requireSubmodule: {                 // Optional submodule check
    module: 'sales',
    submodule: 'dashboard'
  }
}
```

### What This Means

For a user to access the Sales Dashboard:

1. **Organization** must have `sales` module enabled
2. **User** must have `sales.read` permission
3. **Optionally**: `dashboard` submodule must be enabled
4. **If Super Admin**: Same requirements apply (no bypass!)

---

## Permission Checking Code

### Backend

```python
# app/api/v1/sales.py
from app.api.deps.entitlements import require_permission_with_entitlement

@router.get("/sales/dashboard")
async def get_sales_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    # Checks BOTH entitlement AND permission
    _: None = Depends(require_permission_with_entitlement("sales", "sales.read"))
):
    """
    Sales dashboard endpoint.
    
    Access Requirements:
    - Organization must have 'sales' module entitlement
    - User must have 'sales.read' permission
    - Super admins are NOT exempt from these checks
    """
    # ... implementation
```

### Frontend

```typescript
// frontend/src/components/menuConfig.tsx
import { evalMenuItemAccess } from '../permissions/menuAccess';

const menuItem = {
  name: 'Sales Dashboard',
  path: '/sales/dashboard',
  permission: 'sales.read',
  requireModule: 'sales',
};

// Check if user can access
const access = evalMenuItemAccess({
  requireModule: menuItem.requireModule,
  entitlements: userEntitlements,
  isAdmin: isOrgAdmin(user),
  isSuperAdmin: isSuperAdmin(user), // No longer grants bypass!
});

if (access.result === 'enabled') {
  // Show menu item as clickable
} else if (access.result === 'disabled') {
  // Show menu item as grayed out with lock icon
  // Tooltip: access.reason
}
```

---

## Entitlement Management

### Checking Organization Entitlements

```typescript
// Get organization entitlements
const { entitlements } = useEntitlements(organizationId, authToken);

// Check if module is enabled
const salesEnabled = entitlements?.entitlements?.sales?.status === 'enabled';

// Check if submodule is enabled
const dashboardEnabled = entitlements?.entitlements?.sales?.submodules?.dashboard !== false;
```

### Entitlement Statuses

| Status | Meaning | Menu Behavior |
|--------|---------|---------------|
| `enabled` | Module is active | Show as enabled (if user has permission) |
| `trial` | Module in trial period | Show as enabled with "Trial" badge |
| `disabled` | Module not purchased | Show as disabled with lock icon |
| `undefined` | Module not configured | Show as disabled (fail-closed) |

### Trial Period Handling

```typescript
const access = evalMenuItemAccess({
  requireModule: 'manufacturing',
  entitlements: {
    manufacturing: {
      status: 'trial',
      trial_expires_at: '2024-12-31T23:59:59Z',
      submodules: {}
    }
  },
  isAdmin: false,
  isSuperAdmin: false
});

// If trial active: access.result === 'enabled', access.isTrial === true
// If trial expired: access.result === 'disabled', access.reason === 'Trial has expired'
```

---

## Error Messages

### User-Facing Messages

#### Module Not Enabled
```
❌ Module 'sales' is disabled.
💡 Contact your administrator to enable this module.
```

#### Permission Denied
```
❌ You lack permission 'sales.read'.
💡 Contact your administrator to request access.
```

#### Trial Expired
```
❌ Module 'manufacturing' trial has expired.
💡 Please upgrade your plan to continue using this feature.
```

#### Submodule Disabled
```
❌ Feature 'lead_management' is disabled.
💡 Contact your administrator to enable this feature.
```

### API Error Responses

#### Entitlement Denied (403)
```json
{
  "error_type": "entitlement_denied",
  "module_key": "sales",
  "submodule_key": null,
  "status": "disabled",
  "reason": "Module not enabled for your organization",
  "message": "Organization does not have access to module 'sales'."
}
```

#### Permission Denied (403)
```json
{
  "error_type": "permission_denied",
  "permission": "sales.read",
  "reason": "User lacks required permission",
  "message": "User does not have required permission 'sales.read'."
}
```

---

## Troubleshooting

### Issue: Super Admin Cannot See Any Menus

**Problem**: All menu items are grayed out or showing as disabled.

**Possible Causes**:
1. Organization entitlements not configured
2. Super admin role doesn't have permissions assigned
3. Organization context not set

**Solutions**:

```python
# 1. Check organization entitlements
curl -X GET "/api/v1/entitlements?organization_id=1"

# 2. Check super admin permissions
curl -X GET "/api/v1/rbac/users/{user_id}/permissions"

# 3. Verify organization context
# Super admin must select an organization in the UI
```

### Issue: Menu Item Shows "Loading entitlements..."

**Problem**: Menu stays disabled with "Loading entitlements..." message.

**Possible Causes**:
1. API call to fetch entitlements failed
2. Network issue
3. Invalid auth token

**Solutions**:

```typescript
// Check browser console for errors
// Look for failed API calls to /api/v1/entitlements

// Verify entitlements are loading
const { entitlements, loading, error } = useEntitlements(orgId, token);
console.log({ entitlements, loading, error });
```

### Issue: User Has Permission But Menu Disabled

**Problem**: User has the permission but menu item is still disabled.

**Possible Causes**:
1. Organization doesn't have module entitlement
2. Submodule is disabled
3. Trial has expired

**Solutions**:

```python
# Check organization entitlements
from app.services.entitlement_service import EntitlementService

is_entitled, status, reason = await service.check_entitlement(
    org_id=user.organization_id,
    module_key="sales",
    submodule_key=None
)

print(f"Entitled: {is_entitled}, Status: {status}, Reason: {reason}")
```

### Issue: Regular User Can Access, Super Admin Cannot

**Problem**: Regular user has access but super admin doesn't.

**Possible Causes**:
1. Super admin doesn't have explicit permission assigned
2. Super admin is in wrong organization context

**Solutions**:

```python
# Assign permissions to super admin
await RBACService.assign_role_to_user(
    user_id=super_admin_id,
    role_id=super_admin_role_id
)

# Verify super admin has permissions
permissions = await RBACService.get_user_permissions(super_admin_id)
print(f"Super admin has {len(permissions)} permissions")
```

---

## Best Practices

### 1. Always Specify Both Permission and Module

```typescript
// ✅ GOOD
{
  name: 'Inventory',
  path: '/inventory',
  permission: 'inventory.read',
  requireModule: 'inventory'
}

// ❌ BAD - Missing permission or module
{
  name: 'Inventory',
  path: '/inventory',
  permission: 'inventory.read'  // Missing requireModule!
}
```

### 2. Use Specific Permissions

```typescript
// ✅ GOOD - Specific permission
permission: 'sales.create_quotation'

// ❌ BAD - Too broad
permission: 'sales.*'
```

### 3. Provide Clear Menu Names

```typescript
// ✅ GOOD - Clear and specific
name: 'Create Sales Order'

// ❌ BAD - Vague
name: 'Sales'
```

### 4. Group Related Menu Items

```typescript
// ✅ GOOD - Logical grouping
{
  title: 'Sales',
  sections: [
    {
      title: 'Quotations',
      items: [
        { name: 'Create Quotation', permission: 'sales.create', requireModule: 'sales' },
        { name: 'View Quotations', permission: 'sales.read', requireModule: 'sales' },
      ]
    }
  ]
}
```

### 5. Test All Permission Combinations

```typescript
// Test matrix for each menu item:
// - User with permission, org with entitlement → Enabled
// - User with permission, org without entitlement → Disabled
// - User without permission, org with entitlement → Disabled
// - User without permission, org without entitlement → Disabled
// - Super admin with permission, org with entitlement → Enabled
// - Super admin without permission, org with entitlement → Disabled ⚠️ NEW!
```

---

## Migration from v1.0

### Old Behavior (v1.0 - Permissive)

```typescript
// Super admin had automatic access
if (isSuperAdmin) {
  return { result: 'enabled' };
}

// Unknown modules defaulted to enabled
const enabled = organizationData?.enabled_modules?.[module] ?? true;
```

### New Behavior (v2.0 - Strict)

```typescript
// No super admin bypass
// Super admin checked like any other user

// Unknown modules default to disabled
const enabled = organizationData?.enabled_modules?.[module] ?? false;
```

### Migration Checklist

- [ ] Configure organization entitlements for all orgs
- [ ] Assign explicit permissions to all super admins
- [ ] Test all menu items with super admin account
- [ ] Update custom roles with required permissions
- [ ] Verify organization context is set for super admins
- [ ] Clear browser caches after deployment
- [ ] Monitor 403 errors in production logs

---

## API Reference

### Check User Permissions

```typescript
GET /api/v1/rbac/users/{user_id}/permissions

Response:
{
  "user_id": 1,
  "permissions": ["sales.read", "sales.create", "crm.read"],
  "service_roles": [...],
  "total_permissions": 3
}
```

### Check Organization Entitlements

```typescript
GET /api/v1/entitlements?organization_id={org_id}

Response:
{
  "organization_id": 1,
  "entitlements": {
    "sales": {
      "status": "enabled",
      "submodules": {
        "quotations": true,
        "orders": true
      }
    }
  }
}
```

### Check Specific Permission

```typescript
POST /api/v1/rbac/permissions/check
{
  "user_id": 1,
  "permission": "sales.read"
}

Response:
{
  "has_permission": true,
  "user_id": 1,
  "permission": "sales.read",
  "source": "service_role"
}
```

---

## Testing

### Unit Tests

```typescript
// frontend/src/permissions/__tests__/menuAccess.strict.test.ts

it('should deny super admin access to disabled module', () => {
  const entitlements = {
    entitlements: {
      sales: { status: 'disabled', submodules: {} }
    }
  };

  const result = evalMenuItemAccess({
    requireModule: 'sales',
    entitlements,
    isAdmin: true,
    isSuperAdmin: true
  });

  expect(result.result).toBe('disabled');
  expect(result.reason).toContain('sales');
});
```

### Integration Tests

```python
# app/tests/test_strict_entitlement_enforcement.py

@pytest.mark.asyncio
async def test_super_admin_denied_without_entitlement():
    """Super admin without entitlement should be denied access"""
    mock_user = create_super_admin_user()
    
    with patch('EntitlementService.check_entitlement') as mock:
        mock.return_value = (False, 'disabled', 'Module not enabled')
        
        with pytest.raises(EntitlementDeniedError):
            await require_entitlement("manufacturing")(
                db=mock_db,
                current_user=mock_user
            )
```

---

## Support

For issues or questions:

1. Check this guide's troubleshooting section
2. Review error messages carefully (they tell you what's missing)
3. Check browser console for API errors
4. Verify organization entitlements
5. Verify user permissions
6. Contact system administrator
7. Reference issue #185 for implementation details

---

## Version History

- **v2.0** (2024-11): Strict enforcement
  - Removed super admin bypass
  - Removed fallback logic
  - Added comprehensive error messages
  - Default to disabled for unknown modules

- **v1.0** (2024-10): Original implementation
  - Super admin had automatic access
  - Fallback logic granted access on errors
  - Default to enabled for unknown modules
