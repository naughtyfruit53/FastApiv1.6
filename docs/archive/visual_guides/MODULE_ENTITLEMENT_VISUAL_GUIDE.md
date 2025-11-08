# Module Entitlement Restrictions - Visual Guide

## Overview

This document provides a visual guide to understand the user interface and API changes implemented for module entitlement restrictions.

## Backend API Changes

### Before: Organization Module Update (Org Admin Could Access)

```python
@router.put("/{organization_id:int}/modules")
async def update_organization_modules(
    organization_id: int,
    modules_data: dict,
    auth: tuple = Depends(require_access("organization_module", "update")),  # ❌ RBAC-based
    db: AsyncSession = Depends(get_db)
):
    current_user, org_id = auth
    # Could potentially be accessed by org admin with right permissions
```

**Issue**: Org admin with `organization_module.update` permission could modify modules.

### After: Super Admin Only

```python
@router.put("/{organization_id:int}/modules")
async def update_organization_modules(
    organization_id: int,
    modules_data: dict,
    current_user: User = Depends(get_current_active_user),  # ✅ Direct auth check
    db: AsyncSession = Depends(get_db)
):
    # Strict super_admin check - this is a licensing operation
    if not current_user.is_super_admin:  # ✅ Cannot be bypassed
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error_type": "permission_denied",
                "message": "Module entitlement management is restricted to platform administrators only. "
                           "Organization administrators cannot activate or deactivate modules. "
                           "Please contact your platform administrator to request module changes.",
                "required_role": "super_admin",
                "current_role": current_user.role
            }
        )
```

**Solution**: Direct `is_super_admin` check that cannot be bypassed via RBAC.

## API Error Response

### Org Admin Attempting Module Update

**Request**:
```bash
PUT /api/v1/organizations/123/modules
Authorization: Bearer <org_admin_token>
Content-Type: application/json

{
  "enabled_modules": {
    "CRM": true,
    "ERP": true
  }
}
```

**Response**:
```json
{
  "detail": {
    "error_type": "permission_denied",
    "message": "Module entitlement management is restricted to platform administrators only. Organization administrators cannot activate or deactivate modules. Please contact your platform administrator to request module changes.",
    "required_role": "super_admin",
    "current_role": "org_admin"
  }
}
```

**Status Code**: `403 Forbidden`

## Frontend UI Changes

### 1. Module Selection Modal - Super Admin View

```
╔══════════════════════════════════════════════════════╗
║  Module Bundle Selection - Acme Corp                 ║
╠══════════════════════════════════════════════════════╣
║                                                      ║
║  Select the module bundles to enable for this       ║
║  organization. Each bundle activates multiple       ║
║  related modules.                                   ║
║                                                      ║
║  ☑ CRM Suite                                        ║
║    Customer Management, Lead Management, etc.       ║
║                                                      ║
║  ☐ ERP Suite                                        ║
║    Inventory, Purchase Orders, etc.                 ║
║                                                      ║
║  ☑ Manufacturing                                    ║
║    Production, BOM, Quality Control, etc.           ║
║                                                      ║
║  ☐ Finance & Accounting                            ║
║    Chart of Accounts, Journal Entries, etc.         ║
║                                                      ║
║  ☐ HR & Payroll                                    ║
║    Employee Management, Payroll, etc.               ║
║                                                      ║
╠══════════════════════════════════════════════════════╣
║                                    [Cancel] [Save]   ║
╚══════════════════════════════════════════════════════╝
```

**Features**:
- ✅ All checkboxes enabled
- ✅ Save button visible
- ✅ Can modify selections
- ✅ Changes are saved

### 2. Module Selection Modal - Org Admin View

```
╔══════════════════════════════════════════════════════╗
║  Module Bundle Selection - Acme Corp                 ║
╠══════════════════════════════════════════════════════╣
║  ┌─────────────────────────────────────────────┐    ║
║  │ ⚠ Super Admin Access Required               │    ║
║  │                                              │    ║
║  │ Module entitlement management is restricted │    ║
║  │ to platform administrators only.            │    ║
║  │ Organization administrators cannot activate │    ║
║  │ or deactivate modules. Please contact your  │    ║
║  │ platform administrator to request module    │    ║
║  │ changes.                                     │    ║
║  └─────────────────────────────────────────────┘    ║
║                                                      ║
║  View the current module bundles for this           ║
║  organization. Only super admins can modify         ║
║  module entitlements.                               ║
║                                                      ║
║  ☑ CRM Suite (disabled)                             ║
║    Customer Management, Lead Management, etc.       ║
║                                                      ║
║  ☐ ERP Suite (disabled)                             ║
║    Inventory, Purchase Orders, etc.                 ║
║                                                      ║
║  ☑ Manufacturing (disabled)                         ║
║    Production, BOM, Quality Control, etc.           ║
║                                                      ║
║  ☐ Finance & Accounting (disabled)                  ║
║    Chart of Accounts, Journal Entries, etc.         ║
║                                                      ║
║  ☐ HR & Payroll (disabled)                         ║
║    Employee Management, Payroll, etc.               ║
║                                                      ║
╠══════════════════════════════════════════════════════╣
║                                           [Close]    ║
╚══════════════════════════════════════════════════════╝
```

**Features**:
- ⚠️ Warning alert displayed at top
- ❌ All checkboxes disabled (read-only)
- ❌ Save button hidden
- ✅ Close button only
- ℹ️ Explanatory text adjusted

### 3. Organization Management Page - Module Control Button

#### Super Admin View

```
Actions Column:
  [👁️ View Details]
  [⚙️ Module Control] ← ENABLED (blue/secondary color)
  [🔄 Reset Password]
  [📊 Reset Data]
  [🔒 Suspend]
```

**Tooltip on Hover**: "Manage module entitlements (Super Admin only)"
**Button State**: Enabled, clickable, full color

#### Org Admin View

```
Actions Column:
  [👁️ View Details]
  [⚙️ Module Control] ← DISABLED (grayed out)
  [🔄 Reset Password]
  [📊 Reset Data]
  [🔒 Suspend]
```

**Tooltip on Hover**: "Module entitlement management requires Super Admin access"
**Button State**: Disabled, grayed out, not clickable

## User Flows

### Flow 1: Super Admin Manages Modules ✅

```
┌─────────────────┐
│  Super Admin    │
│  Logs In        │
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│  Navigate to            │
│  Manage Organizations   │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Click Module Control   │
│  Button (ENABLED)       │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Modal Opens            │
│  - Editable checkboxes  │
│  - Save button visible  │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Select/Deselect        │
│  Module Bundles         │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Click Save             │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Success! Modules       │
│  Updated                │
└─────────────────────────┘
```

### Flow 2: Org Admin Attempts to Manage Modules ❌

```
┌─────────────────┐
│  Org Admin      │
│  Logs In        │
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│  Navigate to            │
│  Manage Organizations   │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Module Control Button  │
│  is DISABLED            │
│  (with tooltip)         │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Hover over button      │
│  to see tooltip:        │
│  "Requires Super Admin" │
└────────┬────────────────┘
         │
         │ (If somehow modal accessed)
         ▼
┌─────────────────────────┐
│  Modal Shows            │
│  - Warning alert        │
│  - Disabled checkboxes  │
│  - Close button only    │
└────────┬────────────────┘
         │
         │ (If direct API call attempted)
         ▼
┌─────────────────────────┐
│  API Returns 403        │
│  with clear message     │
│  explaining restriction │
└─────────────────────────┘
```

## Access Control Matrix

| Action | Super Admin | Org Admin | Manager | User |
|--------|-------------|-----------|---------|------|
| View organization modules (GET) | ✅ Yes | ✅ Yes | ❌ No | ❌ No |
| Update organization modules (PUT) | ✅ Yes | ❌ No | ❌ No | ❌ No |
| View entitlements (read-only) | ✅ Yes | ✅ Yes | ❌ No | ❌ No |
| Update entitlements (admin API) | ✅ Yes | ❌ No | ❌ No | ❌ No |
| See Module Control button | ✅ Enabled | ❌ Disabled | ❌ Hidden | ❌ Hidden |
| Open ModuleSelectionModal | ✅ Editable | ℹ️ Read-only | ❌ No | ❌ No |
| Save module changes | ✅ Yes | ❌ No | ❌ No | ❌ No |

## Key Visual Indicators

### Super Admin Experience
- ✅ Green checkmark = Can perform action
- 🔓 Unlocked icon = Full access
- "Save" button = Can make changes
- No warnings = Authorized user

### Org Admin Experience
- ⚠️ Warning icon = Restricted access
- 🔒 Locked icon = No access
- ❌ Disabled controls = Read-only
- "Close" button = Cannot save changes
- Alert banner = Clear explanation

## Testing Visual Verification Checklist

- [ ] **Super admin sees enabled Module Control button** - Button should be clickable and full color
- [ ] **Org admin sees disabled Module Control button** - Button should be grayed out
- [ ] **Tooltip shows correct message for each role** - Different text for super admin vs org admin
- [ ] **Modal warning alert displays for org admin** - Yellow/orange warning box at top
- [ ] **Modal checkboxes are disabled for org admin** - Cannot be clicked
- [ ] **Modal Save button hidden for org admin** - Only Close button shown
- [ ] **Help text changes based on role** - Different explanatory text
- [ ] **Direct API call returns proper 403 error** - Clear error message in JSON
- [ ] **Error message is clear and actionable** - Explains what to do next

---

**Status**: Implementation Complete
**Version**: 1.0.0
**Date**: 2025-11-03
