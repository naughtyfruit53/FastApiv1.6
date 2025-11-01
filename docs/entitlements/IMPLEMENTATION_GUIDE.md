# Entitlements & Module Management Implementation Guide

## Overview

This guide covers the complete implementation of the organization-based entitlements system for FastAPI v1.6. The system drives menu visibility by modules and submodules without changing the existing menu structure.

## Table of Contents

1. [Architecture](#architecture)
2. [Database Schema](#database-schema)
3. [Backend APIs](#backend-apis)
4. [Frontend Integration](#frontend-integration)
5. [Migration Guide](#migration-guide)
6. [Super Admin UI](#super-admin-ui)
7. [Testing](#testing)
8. [Deployment](#deployment)

---

## Architecture

### High-Level Flow

```
┌─────────────────┐
│  Organization   │
│   Entitlements  │
└────────┬────────┘
         │
         ├──► Module Status (enabled/disabled/trial)
         │
         └──► Submodule Enabled (true/false)
                    │
                    ├──► Backend Guard (403 if disabled)
                    │
                    └──► Frontend Menu Gating (hidden/disabled/enabled)
```

### Key Components

1. **Database Layer**: PostgreSQL tables for modules, submodules, and org entitlements
2. **Backend Service**: `EntitlementService` for business logic
3. **Admin APIs**: Super admin endpoints for managing entitlements
4. **App APIs**: Cached entitlements endpoint for frontend
5. **Middleware Guard**: `require_entitlement` decorator for route protection
6. **Frontend Hooks**: `useEntitlements` for accessing entitlements
7. **Menu Gating**: `evalMenuItemAccess` for menu visibility logic
8. **Route Guard**: `withModuleGuard` HOC for page protection

---

## Database Schema

### Tables

#### `modules`
Top-level features (sales, inventory, manufacturing, etc.)

```sql
- id (SERIAL PRIMARY KEY)
- module_key (VARCHAR, UNIQUE)
- display_name (VARCHAR)
- description (TEXT)
- icon (VARCHAR)
- sort_order (INTEGER)
- is_active (BOOLEAN)
- created_at, updated_at (TIMESTAMP)
```

#### `submodules`
Fine-grained features within modules

```sql
- id (SERIAL PRIMARY KEY)
- module_id (FK to modules)
- submodule_key (VARCHAR)
- display_name (VARCHAR)
- description (TEXT)
- menu_path (VARCHAR) -- e.g., '/sales/leads'
- permission_key (VARCHAR) -- e.g., 'sales.view'
- sort_order (INTEGER)
- is_active (BOOLEAN)
- UNIQUE(module_id, submodule_key)
```

#### `org_entitlements`
Organization-level module entitlements

```sql
- id (SERIAL PRIMARY KEY)
- org_id (FK to organizations)
- module_id (FK to modules)
- status (VARCHAR) -- 'enabled', 'disabled', 'trial'
- trial_expires_at (TIMESTAMP, nullable)
- source (VARCHAR) -- 'manual', 'admin_update', 'legacy_migration'
- created_at, updated_at (TIMESTAMP)
- UNIQUE(org_id, module_id)
```

#### `org_subentitlements`
Organization-level submodule entitlements

```sql
- id (SERIAL PRIMARY KEY)
- org_id (FK to organizations)
- module_id (FK to modules)
- submodule_id (FK to submodules)
- enabled (BOOLEAN)
- source (VARCHAR)
- created_at, updated_at (TIMESTAMP)
- UNIQUE(org_id, module_id, submodule_id)
```

#### `entitlement_events`
Audit log for entitlement changes

```sql
- id (SERIAL PRIMARY KEY)
- org_id (FK to organizations)
- event_type (VARCHAR) -- 'entitlement_update', 'legacy_migration'
- actor_user_id (FK to users, nullable)
- reason (TEXT)
- payload (JSONB) -- Contains diff and metadata
- created_at (TIMESTAMP)
```

### View: `v_effective_entitlements`

Combines org_entitlements and org_subentitlements to show effective status.

---

## Backend APIs

### Admin Endpoints (Super Admin Only)

#### GET `/api/v1/admin/modules`
List all modules and submodules in the taxonomy.

**Response:**
```json
{
  "modules": [
    {
      "id": 1,
      "module_key": "sales",
      "display_name": "Sales & CRM",
      "submodules": [
        {
          "id": 1,
          "submodule_key": "lead_management",
          "display_name": "Lead Management",
          "menu_path": "/sales/leads"
        }
      ]
    }
  ]
}
```

#### GET `/api/v1/admin/orgs/{orgId}/entitlements`
Get effective entitlements for an organization.

**Response:**
```json
{
  "org_id": 1,
  "org_name": "Acme Corp",
  "entitlements": [
    {
      "module_id": 1,
      "module_key": "sales",
      "status": "enabled",
      "trial_expires_at": null,
      "source": "admin_update",
      "submodules": [
        {
          "submodule_id": 1,
          "submodule_key": "lead_management",
          "enabled": true,
          "effective_status": "enabled"
        }
      ]
    }
  ]
}
```

#### PUT `/api/v1/admin/orgs/{orgId}/entitlements`
Update organization entitlements (diff-only).

**Request:**
```json
{
  "reason": "Enabling sales module for Q4 campaign",
  "changes": {
    "modules": [
      {
        "module_key": "sales",
        "status": "enabled"
      }
    ],
    "submodules": [
      {
        "module_key": "sales",
        "submodule_key": "lead_management",
        "enabled": true
      }
    ]
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Entitlements updated successfully",
  "event_id": 42,
  "updated_entitlements": { /* same as GET response */ }
}
```

### App Endpoint

#### GET `/api/v1/orgs/{orgId}/entitlements`
Get entitlements for app use (cached, optimized format).

**Response:**
```json
{
  "org_id": 1,
  "entitlements": {
    "sales": {
      "module_key": "sales",
      "status": "enabled",
      "trial_expires_at": null,
      "submodules": {
        "lead_management": true,
        "opportunity_tracking": true
      }
    }
  }
}
```

---

## Frontend Integration

### 1. Fetch Entitlements

```typescript
import { useEntitlements } from '@/hooks/useEntitlements';

function MyComponent() {
  const { entitlements, isLoading, isModuleEnabled } = useEntitlements(orgId, token);
  
  if (isModuleEnabled('sales')) {
    // Show sales features
  }
}
```

### 2. Menu Gating

```typescript
import { evalMenuItemAccess } from '@/permissions/menuAccess';

const access = evalMenuItemAccess({
  requireModule: 'sales',
  requireSubmodule: { module: 'sales', submodule: 'lead_management' },
  entitlements,
  isAdminLike: user.role === 'org_admin',
  isSuperAdmin: user.role === 'super_admin',
});

if (access.result === 'hidden') {
  // Don't render menu item
} else if (access.result === 'disabled') {
  // Render with lock icon, tooltip, and CTA
} else {
  // Render normally (maybe with "Trial" badge)
}
```

### 3. Route Protection

```typescript
import { withModuleGuard } from '@/permissions/withModuleGuard';

function SalesPage() {
  return <div>Sales Dashboard</div>;
}

export default withModuleGuard(SalesPage, {
  moduleKey: 'sales',
  submoduleKey: 'lead_management',
  showLockedUI: true, // Show locked UI for admins
});
```

### 4. Middleware Guard (Backend)

```python
from app.core.entitlement_guard import require_entitlement

@router.get("/sales/leads")
@require_entitlement("sales", "lead_management")
async def get_leads(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user)
):
    # If user doesn't have entitlement, raises 403 with details
    ...
```

---

## Migration Guide

### 1. Run Database Migration

```bash
cd /home/runner/work/FastApiv1.6/FastApiv1.6
alembic upgrade head
```

This creates all entitlement tables.

### 2. Seed Module Taxonomy

```bash
python scripts/seed_entitlements.py
```

This seeds modules and submodules from `menu_permission_map.csv`.

### 3. Migrate Legacy Entitlements

```bash
# Dry-run to preview changes
python scripts/migrate_legacy_entitlements.py

# Execute migration
python scripts/migrate_legacy_entitlements.py --execute
```

This migrates legacy `enabled_modules` flags to the new system.

### 4. Register API Routes

In `app/main.py`:

```python
from app.api.v1 import admin_entitlements, entitlements

app.include_router(admin_entitlements.router, prefix="/api/v1", tags=["admin"])
app.include_router(entitlements.router, prefix="/api/v1", tags=["app"])
```

---

## Super Admin UI

### Create `/admin/module-management` Page

```typescript
// pages/admin/module-management.tsx

import React, { useState } from 'react';
import { Box, Typography, Grid, Checkbox, Button, TextField } from '@mui/material';
import { fetchAllModules, fetchOrgEntitlementsAdmin, updateOrgEntitlements } from '@/services/entitlementsApi';

export default function ModuleManagement() {
  const [selectedOrg, setSelectedOrg] = useState<number | null>(null);
  const [entitlements, setEntitlements] = useState(null);
  const [reason, setReason] = useState('');
  
  // Load modules and entitlements
  // Render org picker
  // Render module/submodule grid with checkboxes
  // Handle save with diff-only PUT
  
  return (
    <Box p={3}>
      <Typography variant="h4">Module Management</Typography>
      {/* UI implementation */}
    </Box>
  );
}
```

---

## Testing

### Unit Tests

```typescript
// Test evalMenuItemAccess
describe('evalMenuItemAccess', () => {
  it('should hide disabled modules for non-admin', () => {
    const result = evalMenuItemAccess({
      requireModule: 'sales',
      entitlements: { entitlements: {} },
      isAdminLike: false,
    });
    expect(result.result).toBe('hidden');
  });
  
  it('should disable modules for admins', () => {
    const result = evalMenuItemAccess({
      requireModule: 'sales',
      entitlements: { entitlements: {} },
      isAdminLike: true,
    });
    expect(result.result).toBe('disabled');
  });
});
```

### Integration Tests

```python
# Test admin entitlements API
async def test_update_entitlements(client, super_admin_token):
    response = await client.put(
        "/api/v1/admin/orgs/1/entitlements",
        json={
            "reason": "Test update",
            "changes": {
                "modules": [{"module_key": "sales", "status": "enabled"}]
            }
        },
        headers={"Authorization": f"Bearer {super_admin_token}"}
    )
    assert response.status_code == 200
    assert response.json()["success"] == True
```

---

## Deployment

### Phase 1: Dry-Run (Lower Environment)

1. Deploy code with feature flag `enable_entitlements_gating=false`
2. Run migration scripts in dry-run mode
3. Verify data migration
4. Test APIs manually

### Phase 2: Enable for Test Orgs

1. Enable feature flag for specific test organizations
2. Monitor telemetry for issues
3. Gather feedback from test users

### Phase 3: Production Rollout

1. Enable feature flag for all organizations
2. Monitor error rates and user feedback
3. Prepare rollback plan if needed

---

## Rollback Plan

If issues arise:

1. Set feature flag `enable_entitlements_gating=false`
2. Frontend falls back to legacy `enabled_modules` check
3. Backend guard can be disabled via config
4. No data loss (entitlements remain in DB)

---

## Support

For questions or issues, contact the development team or open an issue in the repository.
