# Strict Permission and Entitlement Enforcement Guide

## Overview

This guide explains the strict permission and entitlement enforcement model implemented in FastAPI v1.6. All fallback logic that previously granted automatic access has been removed to enhance security and ensure explicit access control.

## Key Changes

### What Changed?

1. **Super Admin Bypass Removed**: Super admins no longer have automatic access to all modules and features
2. **Fail-Closed by Default**: Missing or errored permissions/entitlements deny access instead of allowing it
3. **No Feature Flags**: Cannot disable entitlement enforcement via environment variables
4. **Explicit Permissions Required**: All users must have permissions explicitly assigned
5. **Organization Context Required**: All operations require valid organization context

### Why These Changes?

- **Security**: Prevents accidental or unauthorized access
- **Compliance**: Ensures audit trails and explicit access grants
- **Clarity**: Users know exactly what they can and cannot access
- **Scalability**: Easier to manage permissions as organization grows

---

## Backend Enforcement

### Entitlement Checks

#### Before (Permissive):
```python
# Super admin could bypass entitlement checks
@router.get("/sales/dashboard")
async def get_sales_dashboard(
    _: None = Depends(require_entitlement("sales", allow_super_admin_bypass=True))
):
    # Super admin had automatic access even if module disabled
    pass
```

#### After (Strict):
```python
# ALL users must have entitlement
@router.get("/sales/dashboard")
async def get_sales_dashboard(
    _: None = Depends(require_entitlement("sales"))
):
    # Super admin needs explicit entitlement like everyone else
    pass
```

### Permission Checks

#### Before (Permissive):
```python
# Errors returned empty permissions as fallback
try:
    permissions = await rbac_service.get_user_permissions(user_id)
except Exception:
    return {"permissions": [], "fallback": True}  # DANGEROUS!
```

#### After (Strict):
```python
# Errors propagate to caller
permissions = await rbac_service.get_user_permissions(user_id)
# No try-catch - errors fail the request
```

### Organization Context

#### Before (Permissive):
```python
# Super admins without org returned empty data
if current_user.organization_id is None and current_user.is_super_admin:
    return []  # Empty fallback
```

#### After (Strict):
```python
# All users must have organization context
if current_user.organization_id is None:
    raise HTTPException(
        status_code=400,
        detail="Organization context required"
    )
```

---

## Frontend Enforcement

### Menu Access Control

#### Before (Permissive):
```typescript
// Super admin bypassed all checks
if (isSuperAdmin) {
  return { result: 'enabled' };
}

// Unknown modules defaulted to enabled
const enabled = organizationData?.enabled_modules?.[module] ?? true;
```

#### After (Strict):
```typescript
// No super admin bypass
// Super admin must have explicit entitlements

// Unknown modules default to disabled
const enabled = organizationData?.enabled_modules?.[module] ?? false;
```

### Permission Context

#### Before (Permissive):
```typescript
const hasPermission = (module: string, action: string) => {
  // Super admins had all permissions
  if (isSuperAdmin) {
    return true;
  }
  return permissions.includes(`${module}_${action}`);
};
```

#### After (Strict):
```typescript
const hasPermission = (module: string, action: string) => {
  // No bypass - check actual permissions
  return permissions.includes(`${module}_${action}`);
};
```

---

## Module Configuration

### Always-On Modules (Non-Billable)

These modules skip entitlement checks because they are non-billable:

- **email**: Communication is always available
- **settings**: Configuration access controlled by RBAC only
- **admin**: Platform administration controlled by RBAC only
- **organization**: Organization management controlled by RBAC only

### RBAC-Only Modules

These modules use RBAC permissions only (no entitlements):
- settings
- admin
- administration
- organization

### Billable Modules

All other modules require entitlements:
- sales
- crm
- manufacturing
- inventory
- hr
- finance
- analytics
- etc.

---

## Error Handling

### Entitlement Denied

**Error Response:**
```json
{
  "error_type": "entitlement_denied",
  "module_key": "manufacturing",
  "submodule_key": "production_planning",
  "status": "disabled",
  "reason": "Module not enabled for your organization",
  "message": "Organization does not have access to module 'manufacturing'. Module not enabled for your organization"
}
```

**HTTP Status:** 403 Forbidden

### Permission Denied

**Error Response:**
```json
{
  "error_type": "permission_denied",
  "permission": "inventory.write",
  "reason": "User lacks required permission",
  "message": "User does not have required permission 'inventory.write'. User lacks required permission"
}
```

**HTTP Status:** 403 Forbidden

### Organization Context Required

**Error Response:**
```json
{
  "detail": "Organization context required. Please specify an organization."
}
```

**HTTP Status:** 400 Bad Request

---

## Best Practices

### 1. Always Check Both Entitlement and Permission

```python
@router.post("/sales/leads")
async def create_lead(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    _: None = Depends(require_permission_with_entitlement("sales", "crm.create"))
):
    # Both entitlement AND permission checked
    pass
```

### 2. Provide Clear Error Messages

```python
if not is_entitled:
    raise EntitlementDeniedError(
        module_key="manufacturing",
        reason="Your organization needs to upgrade to access manufacturing features"
    )
```

### 3. Use Specific Permissions

Instead of:
```python
# Too broad
permission = "admin.*"
```

Use:
```python
# Specific
permission = "organization.manage_users"
```

### 4. Log Access Denials

```python
logger.warning(
    f"User {current_user.email} (role: {current_user.role}) "
    f"denied access to {module_key}. Reason: {reason}"
)
```

---

## Migration Guide

### For Administrators

1. **Audit Super Admin Access**
   - Identify all super admins in your organization
   - Document which modules they currently access
   - Assign explicit entitlements for those modules

2. **Configure Organization Entitlements**
   - Review all enabled modules in organization settings
   - Ensure all required modules have explicit entitlements
   - Enable trial mode for evaluation if needed

3. **Assign User Permissions**
   - Review each user's role and responsibilities
   - Assign explicit permissions matching their duties
   - Test access after assignment

4. **Monitor Access Logs**
   - Watch for 403 Forbidden errors
   - Identify legitimate access needs
   - Adjust permissions as needed

### For Developers

1. **Update Tests**
   - Remove assumptions about super admin bypass
   - Add explicit entitlement setup in test fixtures
   - Test denied access scenarios

2. **Update Endpoint Guards**
   ```python
   # Old
   @router.get("/data")
   async def get_data(
       _: None = Depends(require_entitlement("sales", allow_super_admin_bypass=True))
   ):
       pass
   
   # New
   @router.get("/data")
   async def get_data(
       _: None = Depends(require_entitlement("sales"))
   ):
       pass
   ```

3. **Remove Fallback Logic**
   ```python
   # Old
   try:
       data = await fetch_data()
   except Exception:
       return []  # Dangerous fallback
   
   # New
   data = await fetch_data()  # Let errors propagate
   ```

4. **Add Organization Context**
   ```python
   # Old
   org_id = current_user.organization_id or None
   
   # New
   if not current_user.organization_id:
       raise HTTPException(400, "Organization context required")
   org_id = current_user.organization_id
   ```

---

## Testing Guide

### Backend Tests

```python
@pytest.mark.asyncio
async def test_super_admin_denied_without_entitlement():
    """Super admin should be denied without explicit entitlement"""
    mock_user = create_super_admin()
    mock_service.check_entitlement.return_value = (False, 'disabled', 'Not enabled')
    
    with pytest.raises(EntitlementDeniedError):
        await dependency(db=mock_db, current_user=mock_user)
```

### Frontend Tests

```typescript
it('should disable menu item for super admin without entitlement', () => {
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
});
```

---

## Troubleshooting

### Issue: "Organization context required"

**Cause:** User doesn't have organization_id set

**Solution:**
1. Ensure user belongs to an organization
2. Set organization context in session
3. For super admins, select an organization to manage

### Issue: "Module not enabled"

**Cause:** Organization lacks entitlement for the module

**Solution:**
1. Check organization settings
2. Enable the module for the organization
3. Contact administrator to purchase module

### Issue: "Permission denied"

**Cause:** User lacks the specific permission

**Solution:**
1. Check user's assigned roles
2. Assign appropriate role or permission
3. Contact administrator for access

### Issue: Super admin can't access anything

**Cause:** Entitlements not configured

**Solution:**
1. Configure organization entitlements
2. Assign permissions to super admin role
3. Verify organization context is set

---

## API Reference

### `require_entitlement(module_key, submodule_key)`

Dependency for checking module entitlements.

**Parameters:**
- `module_key` (str): Module to check (e.g., "sales", "manufacturing")
- `submodule_key` (str, optional): Submodule to check (e.g., "lead_management")

**Raises:**
- `EntitlementDeniedError`: If entitlement is missing or disabled

**Example:**
```python
@router.get("/sales/dashboard")
async def dashboard(
    _: None = Depends(require_entitlement("sales"))
):
    pass
```

### `require_permission_with_entitlement(module_key, permission, submodule_key)`

Dependency for checking both entitlement and permission.

**Parameters:**
- `module_key` (str): Module to check
- `permission` (str): Permission to check (e.g., "crm.create")
- `submodule_key` (str, optional): Submodule to check

**Raises:**
- `EntitlementDeniedError`: If entitlement missing
- `PermissionDeniedError`: If permission missing

**Example:**
```python
@router.post("/sales/leads")
async def create_lead(
    _: None = Depends(require_permission_with_entitlement("sales", "crm.create"))
):
    pass
```

### `evalMenuItemAccess(params)`

Frontend function for evaluating menu item access.

**Parameters:**
- `requireModule` (string, optional): Required module
- `requireSubmodule` (object, optional): Required submodule
- `entitlements` (object): User's entitlements
- `isAdmin` (boolean): Whether user is admin
- `isSuperAdmin` (boolean): Whether user is super admin (no longer bypasses)

**Returns:** `MenuItemAccess` object with `result`, `reason`, `isTrial`, `trialExpiresAt`

**Example:**
```typescript
const access = evalMenuItemAccess({
  requireModule: 'sales',
  entitlements: userEntitlements,
  isAdmin: false,
  isSuperAdmin: false
});

if (access.result === 'enabled') {
  // Show enabled menu item
}
```

---

## Support

For questions or issues:
1. Check the troubleshooting section above
2. Review error messages carefully
3. Check audit logs for access denials
4. Contact your system administrator
5. Refer to issue #185 for full implementation details

---

## Version History

- **v1.6.0**: Initial implementation of strict enforcement
  - Removed super admin bypass
  - Removed fallback logic
  - Added comprehensive error messages
  - Created 62 test cases
