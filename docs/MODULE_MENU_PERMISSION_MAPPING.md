# Module-Menu-Permission Mapping Guide

## Overview

This guide explains how modules, menu items, and permissions work together in FastAPI v1.6 to control feature access.

## Architecture

### Three-Layer Access Control

```
┌─────────────────────────────────────────┐
│  1. Module Entitlements (Billable)     │
│     - Organization-level enablement     │
│     - Trial/Enabled/Disabled status     │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  2. Menu Visibility (Frontend)          │
│     - Shows/hides menu items            │
│     - Displays lock icons & tooltips    │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  3. RBAC Permissions (User-level)       │
│     - Role-based access control         │
│     - Create/Read/Update/Delete         │
└─────────────────────────────────────────┘
```

### Flow

1. **Check Entitlement** → Is the module enabled for this organization?
2. **Check Menu Access** → Should this user see this menu item?
3. **Check Permission** → Can this user perform this action?

## Module Registry

### Core Modules

Located in `app/core/modules_registry.py`:

```python
class ModuleName(str, Enum):
    # Core Business
    CRM = "crm"
    ERP = "erp"
    HR = "hr"
    INVENTORY = "inventory"
    SERVICE = "service"
    FINANCE = "finance"
    ANALYTICS = "analytics"
    
    # Extended
    MANUFACTURING = "manufacturing"
    PROCUREMENT = "procurement"
    PROJECT = "project"
    ASSET = "asset"
    TRANSPORT = "transport"
    
    # Advanced
    AI_ANALYTICS = "ai_analytics"
    EMAIL = "email"
    SETTINGS = "settings"
    # ... and more
```

### Submodules

Each module can have submodules for fine-grained control:

```python
MODULE_SUBMODULES = {
    'ERP': [
        "inventory",
        "products",
        "stock",
        "warehouse",
        "procurement",
    ],
    'MANUFACTURING': [
        "bom",
        "mrp",
        "production_planning",
        "job_cards",
        "quality",
    ],
    # ...
}
```

## Menu Configuration

### Frontend Menu Structure

Located in `frontend/src/components/menuConfig.tsx`:

```tsx
export const menuItems = {
  master_data: {
    title: 'Master Data',
    icon: <People />,
    sections: [
      {
        title: 'Business Entities',
        items: [
          {
            name: 'Customers',
            path: '/masters/customers',
            permission: 'master_data.view',
            requireModule: 'erp',
            requireSubmodule: {
              module: 'erp',
              submodule: 'customers'
            }
          },
          // ...
        ]
      }
    ]
  },
  // ...
}
```

### Menu Item Properties

| Property | Type | Description |
|----------|------|-------------|
| `name` | string | Display name |
| `path` | string | Route path |
| `icon` | ReactNode | MUI icon |
| `permission` | string | Required RBAC permission |
| `requireModule` | string | Required module key |
| `requireSubmodule` | object | Module + submodule keys |

## Entitlement Checking

### Backend Enforcement

Use the `require_entitlement` dependency:

```python
from app.api.deps.entitlements import require_entitlement

@router.get("/sales/dashboard")
async def get_sales_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    _: None = Depends(require_entitlement("crm"))
):
    # Endpoint logic here
    pass
```

### Combined Check (Entitlement + Permission)

```python
from app.api.deps.entitlements import require_permission_with_entitlement

@router.post("/sales/leads")
async def create_lead(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    _: None = Depends(
        require_permission_with_entitlement("crm", "crm.create")
    )
):
    # Endpoint logic here
    pass
```

### Frontend Check

Use the menu access evaluation:

```typescript
import { evalMenuItemAccess } from '../permissions/menuAccess';

const access = evalMenuItemAccess({
  requireModule: 'erp',
  requireSubmodule: { module: 'erp', submodule: 'customers' },
  entitlements: userEntitlements,
  isAdmin: user.role === 'org_admin',
});

// access.result: 'enabled' | 'disabled' | 'hidden'
// access.reason: User-friendly explanation
// access.isTrial: true if in trial mode
```

## Module Status

### Status Types

1. **Enabled**: Full access
2. **Trial**: Time-limited access with badge
3. **Disabled**: No access, show upgrade prompt

### Status Hierarchy

```
Organization Level (Billable)
└── Module Status (enabled/trial/disabled)
    └── Submodule Status (enabled/disabled)
        └── User Permission (RBAC)
```

### Example Status Combinations

| Module | Submodule | Permission | Result |
|--------|-----------|------------|--------|
| Enabled | Enabled | ✓ Has | ✓ Full Access |
| Enabled | Disabled | ✓ Has | ✗ Blocked (Submodule) |
| Disabled | N/A | ✓ Has | ✗ Blocked (Module) |
| Trial | Enabled | ✓ Has | ✓ Trial Access |
| Trial (Expired) | Enabled | ✓ Has | ✗ Blocked (Trial Expired) |

## Special Cases

### Always-On Modules

Some modules bypass entitlement checks:

```python
ALWAYS_ON_MODULES = {'email'}
```

### RBAC-Only Modules

Non-billable modules that only check permissions:

```python
RBAC_ONLY_MODULES = {
    'settings',
    'admin',
    'administration',
    'organization',
    'rbac'
}
```

## API Endpoints

### Get Entitlements

```typescript
// Current user's organization entitlements
GET /api/v1/organizations/entitlements

Response:
{
  "org_id": 123,
  "entitlements": {
    "erp": {
      "module_key": "erp",
      "status": "enabled",
      "submodules": {
        "customers": true,
        "vendors": true
      }
    },
    "manufacturing": {
      "module_key": "manufacturing",
      "status": "trial",
      "trial_expires_at": "2024-12-31T23:59:59Z",
      "submodules": {}
    }
  }
}
```

### Update Entitlements (Admin)

```typescript
// Update organization entitlements
PUT /api/v1/admin/orgs/{org_id}/entitlements

Request:
{
  "reason": "Enable manufacturing for testing",
  "changes": {
    "modules": [
      {
        "module_key": "manufacturing",
        "status": "trial",
        "trial_expires_at": "2024-12-31T23:59:59Z"
      }
    ],
    "submodules": [
      {
        "module_key": "erp",
        "submodule_key": "customers",
        "enabled": true
      }
    ]
  }
}
```

## Menu Rendering Logic

### Evaluation Process

```typescript
// 1. Check if entitlements are loaded
if (!entitlements) {
  return { result: 'disabled', reason: 'Loading...' };
}

// 2. Check special cases (email, settings)
if (isAlwaysOnModule(module)) {
  return { result: 'enabled' };
}

// 3. Get module entitlement
const moduleEnt = entitlements[moduleKey];
if (!moduleEnt || moduleEnt.status === 'disabled') {
  return {
    result: 'disabled',
    reason: 'Module disabled. Contact administrator.'
  };
}

// 4. Check trial expiration
if (moduleEnt.status === 'trial' && isExpired(moduleEnt.trial_expires_at)) {
  return {
    result: 'disabled',
    reason: 'Trial expired. Please upgrade.'
  };
}

// 5. Check submodule (if specified)
if (submoduleKey && moduleEnt.submodules[submoduleKey] === false) {
  return {
    result: 'disabled',
    reason: 'Feature disabled. Contact administrator.'
  };
}

// 6. Grant access
return {
  result: 'enabled',
  isTrial: moduleEnt.status === 'trial',
  trialExpiresAt: moduleEnt.trial_expires_at
};
```

### UI Rendering

```tsx
// In menu component
const access = evalMenuItemAccess(menuItemParams);

// Render based on access result
<MenuItem
  disabled={access.result === 'disabled'}
  onClick={access.result === 'enabled' ? handleClick : showUpgradeModal}
>
  <ListItemText primary={item.name} />
  
  {access.result === 'disabled' && (
    <Tooltip title={access.reason}>
      <LockIcon fontSize="small" />
    </Tooltip>
  )}
  
  {access.isTrial && (
    <Chip label="Trial" size="small" color="warning" />
  )}
</MenuItem>
```

## Database Schema

### Modules Table

```sql
CREATE TABLE modules (
    id SERIAL PRIMARY KEY,
    module_key VARCHAR(100) UNIQUE NOT NULL,
    display_name VARCHAR(200) NOT NULL,
    description TEXT,
    icon VARCHAR(100),
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Submodules Table

```sql
CREATE TABLE submodules (
    id SERIAL PRIMARY KEY,
    module_id INTEGER REFERENCES modules(id) ON DELETE CASCADE,
    submodule_key VARCHAR(100) NOT NULL,
    display_name VARCHAR(200) NOT NULL,
    description TEXT,
    menu_path VARCHAR(500),
    permission_key VARCHAR(200),
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    UNIQUE(module_id, submodule_key)
);
```

### Organization Entitlements

```sql
CREATE TABLE org_entitlements (
    id SERIAL PRIMARY KEY,
    org_id INTEGER REFERENCES organizations(id) ON DELETE CASCADE,
    module_id INTEGER REFERENCES modules(id) ON DELETE CASCADE,
    status VARCHAR(20) DEFAULT 'disabled',
    trial_expires_at TIMESTAMP WITH TIME ZONE,
    source VARCHAR(100) DEFAULT 'manual',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(org_id, module_id),
    CHECK (status IN ('enabled', 'disabled', 'trial'))
);
```

## Synchronization

### Auto-Migration

When organizations are created or modules are added, entitlements are automatically created:

```python
# In entitlement_service.py
async def get_app_entitlements(self, org_id: int):
    # Check for missing entitlements
    all_modules = get_all_modules()
    existing = set(e.module_key for e in org_entitlements)
    
    # Create missing entitlements
    for module_key in all_modules:
        if module_key not in existing:
            # Auto-create with default status
            ent = OrgEntitlement(
                org_id=org_id,
                module_id=module.id,
                status='disabled',
                source='auto_migration'
            )
            db.add(ent)
```

### Sync Script

Run periodically or after module changes:

```bash
python scripts/sync_all_entitlements.py
```

This script:
1. Seeds all modules from registry
2. Creates missing entitlements for all orgs
3. Validates consistency
4. Reports issues

## Troubleshooting

### Issue: Menu Item Not Showing

**Check:**
1. Is module enabled in org_entitlements?
2. Is submodule enabled in org_subentitlements?
3. Does user have RBAC permission?
4. Is module in modules_registry?

**Debug:**
```typescript
console.log('Entitlements:', entitlements);
console.log('Access:', evalMenuItemAccess(params));
```

### Issue: 403 Forbidden on Endpoint

**Check:**
1. Backend has `require_entitlement()` or `require_permission_with_entitlement()`
2. Module key matches exactly (case-sensitive)
3. Org has entitlement in database
4. User has required permission

**Debug:**
```python
# In endpoint
logger.info(f"User: {current_user.email}")
logger.info(f"Org: {current_user.organization_id}")
logger.info(f"Role: {current_user.role}")
```

### Issue: Trial Not Expiring

**Check:**
1. trial_expires_at is set correctly
2. Timezone handling (use UTC)
3. Frontend caching (invalidate on changes)

## Best Practices

1. **Always use module keys from registry** - Don't hardcode strings
2. **Check entitlements first, permissions second** - Follow the hierarchy
3. **Provide helpful tooltips** - Explain why something is disabled
4. **Cache entitlements** - But invalidate on changes
5. **Log access denials** - For debugging and analytics
6. **Test with different org configurations** - Enabled, trial, disabled scenarios

## See Also

- [API Client Guide](./API_CLIENT_GUIDE.md)
- [RBAC Comprehensive Guide](./RBAC_COMPREHENSIVE_GUIDE.md)
- [Entitlements Implementation Summary](./ENTITLEMENTS_IMPLEMENTATION_SUMMARY.md)
