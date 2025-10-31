# Consolidated RBAC & Tenant Changelog (PR #148 → Current)

This document provides a comprehensive summary of all RBAC (Role-Based Access Control) and multi-tenancy changes from PR #148 to the current state.

## Table of Contents
1. [Overview](#overview)
2. [Architecture Changes](#architecture-changes)
3. [Permission System](#permission-system)
4. [MegaMenu Integration](#megamenu-integration)
5. [Recent Fixes (Current PR)](#recent-fixes-current-pr)
6. [Migration Guide](#migration-guide)

---

## Overview

The RBAC and tenant system has evolved significantly to provide:
- **Fine-grained permissions** at module and submodule levels
- **Multi-tenant isolation** with organization-scoped data
- **Dynamic menu rendering** based on user permissions
- **Permission normalization** for frontend-backend compatibility

---

## Architecture Changes

### Backend (FastAPI)

#### RBAC Models
- **ServiceRole**: Defines roles with permissions within an organization
- **UserServiceRole**: Maps users to roles
- **ServiceRolePermission**: Defines permissions for each role

#### Permission Format
Backend uses action-specific permissions:
- `module_name.read` - Read access
- `module_name.write` - Write/create access
- `module_name.manage` - Full management access
- `module_name.list` - List/query access
- `module_name.access` - General access

#### Enforcement
- `require_access(module, action)` - Enforces permissions at API level
- Automatic organization context via `TenantContext`
- Permission checks cascade: super_admin → org_admin → user roles

### Frontend (Next.js/React)

#### Permission Format
Frontend uses view-based permissions:
- `module_name.view` - View access to module
- `module_name.create` - Create new items
- `module_name.edit` - Edit existing items
- `module_name.delete` - Delete items

#### Normalization
Permission normalization utility translates backend permissions to frontend:
- `*.read, *.list, *.access, *.manage` → `*.view`
- Grants `module.view` if any permission exists in module namespace
- Extracts modules and submodules from permission strings

---

## Permission System

### Hierarchical Permissions

1. **App Super Admin** (`is_super_admin=true`)
   - Full system access
   - Can manage all organizations
   - Can access admin panel
   - Bypasses all permission checks

2. **Organization Admin** (`role='org_admin'|'super_admin'|'admin'`)
   - Full organization access
   - Can manage organization users
   - Can configure organization settings
   - Cannot access other organizations

3. **Role-Based Users**
   - Permissions defined by assigned roles
   - Scoped to their organization
   - Access determined by role permissions

### Permission Checking

#### Backend
```python
from app.core.enforcement import require_access

@router.get("/items")
async def get_items(
    auth: tuple = Depends(require_access("inventory", "read")),
    db: AsyncSession = Depends(get_db)
):
    current_user, org_id = auth
    # org_id is automatically set for non-super-admins
    ...
```

#### Frontend
```typescript
import { useSharedPermissions } from '../hooks/useSharedPermissions';

const { hasPermission, hasModuleAccess, hasSubmoduleAccess } = useSharedPermissions();

// Check specific permission
if (hasPermission('inventory.view')) {
  // Show inventory module
}

// Check module access
if (hasModuleAccess('finance')) {
  // Show finance menu
}

// Check submodule access
if (hasSubmoduleAccess('master_data', 'vendors')) {
  // Show vendors submodule
}
```

---

## MegaMenu Integration

### Previous Behavior (PR #148)
- MegaMenu only rendered on Dashboard page
- Hardcoded permission checks
- No permission normalization
- Limited module filtering

### Current Implementation

#### Global Layout
- **AppLayout Component**: Wraps all authenticated routes
- MegaMenu rendered globally across all pages
- Consistent navigation experience

#### Permission-Based Filtering
```typescript
// menuConfig.tsx
const menuItem = {
  name: 'Vendors',
  path: '/masters/vendors',
  permission: 'master_data.view', // Normalized permission
  requireModule: 'master_data',
  requireSubmodule: { module: 'master_data', submodule: 'vendors' }
};
```

#### Multi-Level Checks
1. **Module Check**: Is module enabled for organization?
2. **Permission Check**: Does user have required permission?
3. **Submodule Check**: Does user have access to submodule?

#### Fallback Handling
- Shows helpful message if no menu items available
- Provides guidance for requesting access
- Prevents empty/broken menu states

---

## Recent Fixes (Current PR)

### 1. Global MegaMenu
**Problem**: MegaMenu only visible on dashboard

**Solution**:
- Created `AppLayout` component
- Wrapped all authenticated routes
- Removed duplicate MegaMenu instances

**Files Changed**:
- `frontend/src/components/AppLayout.tsx` (new)
- Updated page components to use AppLayout

### 2. Permission Normalization
**Problem**: Backend returns `*.read`, frontend expects `*.view`

**Solution**:
- Created `permissionNormalizer.ts` utility
- Maps backend actions to frontend actions
- Grants `module.view` if any permission in namespace
- Extracts modules and submodules

**Files Changed**:
- `frontend/src/utils/permissionNormalizer.ts` (new)
- Updated MegaMenu to use normalization
- Updated useSharedPermissions hook

### 3. Pincode Lookup Authentication
**Problem**: 401 errors during license creation

**Solution**:
- Updated `usePincodeLookup` to use authenticated axios client
- Added debouncing (500ms) to prevent spam
- Implemented single-flight pattern to avoid duplicate requests
- Better error handling for auth failures

**Files Changed**:
- `frontend/src/hooks/usePincodeLookup.ts`

### 4. Organization Deletion
**Problem**: 500 error - `UserServiceRole.organization_id` doesn't exist

**Solution**:
- Fixed cascade delete to join via User table
- Proper FK constraint ordering
- Transaction-wrapped deletions
- Enhanced logging for debugging

**Files Changed**:
- `app/api/v1/organizations/module_routes.py`

**Fixed SQL Query**:
```python
# Before (WRONG)
delete(UserServiceRole).where(UserServiceRole.organization_id == organization_id)

# After (CORRECT)
delete(UserServiceRole).where(
    UserServiceRole.user_id.in_(
        select(User.id).where(User.organization_id == organization_id)
    )
)
```

### 5. Admin Password Reset
**Status**: Endpoint already exists at `/api/v1/password/admin-reset`

**Features**:
- POST `/api/v1/password/admin-reset`
- Requires `super_admin` role
- Accepts `user_email` in request body
- Generates random password
- Sets `must_change_password=True`
- Sends email notification
- Full audit logging

**Files**:
- `app/api/v1/password.py` (already implemented)

---

## Migration Guide

### For Developers

#### Using New Permission System

1. **Check Permission in Component**:
```typescript
import { useSharedPermissions } from '../hooks/useSharedPermissions';

function MyComponent() {
  const { hasPermission } = useSharedPermissions();
  
  return hasPermission('finance.view') ? (
    <FinanceModule />
  ) : (
    <AccessDenied />
  );
}
```

2. **Add Permission to Menu Item**:
```typescript
// menuConfig.tsx
{
  name: 'My Feature',
  path: '/my-feature',
  icon: <MyIcon />,
  permission: 'my_module.view',
  requireModule: 'my_module',
  requireSubmodule: { module: 'my_module', submodule: 'my_feature' }
}
```

3. **Protect API Endpoint**:
```python
@router.get("/my-endpoint")
async def my_endpoint(
    auth: tuple = Depends(require_access("my_module", "read")),
    db: AsyncSession = Depends(get_db)
):
    current_user, org_id = auth
    # Implementation
```

### For Administrators

#### Setting Up Roles
1. Navigate to **Settings → Role Management**
2. Create new role or edit existing
3. Select modules and permissions
4. Assign role to users

#### Enabling Modules
1. Navigate to **Admin → Organization Management**
2. Select organization
3. Enable/disable modules
4. Save changes

#### Troubleshooting

**User can't see menu items**:
1. Check if user has role assigned
2. Verify role has correct permissions
3. Ensure module is enabled for organization
4. Check browser console for permission logs

**401 Errors**:
1. Clear browser cache and localStorage
2. Log out and log back in
3. Verify token is valid
4. Check network tab for auth headers

---

## Summary

This consolidated changelog replaces the following documents:
- Individual PR summaries (PR #148, #149, etc.)
- RBAC implementation guides
- Permission system documentation
- MegaMenu-specific docs

All RBAC and tenant-related changes should now reference this single source of truth.

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Current | Initial consolidated changelog |
| - | PR #148 | Initial RBAC implementation |
| - | Various | Menu system, permission checks |
| - | Current PR | Global MegaMenu, permission normalization, fixes |

---

For detailed API documentation, see:
- Backend: `/docs` (FastAPI Swagger UI)
- Frontend: Component JSDoc comments
- RBAC Models: `app/models/rbac_models.py`
- Permission Utils: `frontend/src/utils/permissionNormalizer.ts`
