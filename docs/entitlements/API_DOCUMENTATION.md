# Entitlements API Documentation

## Base URL

```
/api/v1
```

## Authentication

All endpoints require authentication via Bearer token:

```
Authorization: Bearer <token>
```

---

## Admin Endpoints

Admin endpoints require `super_admin` role.

### GET `/admin/modules`

List all modules and submodules in the taxonomy.

**Authorization:** super_admin

**Response:** `200 OK`

```json
{
  "modules": [
    {
      "id": 1,
      "module_key": "sales",
      "display_name": "Sales & CRM",
      "description": "Sales pipeline, leads, and customer management",
      "icon": "Business",
      "sort_order": 1,
      "is_active": true,
      "submodules": [
        {
          "id": 1,
          "submodule_key": "lead_management",
          "display_name": "Lead Management",
          "description": null,
          "menu_path": "/sales/leads",
          "permission_key": "sales.view",
          "sort_order": 0,
          "is_active": true
        }
      ]
    }
  ]
}
```

**Error Responses:**
- `401 Unauthorized`: Missing or invalid token
- `403 Forbidden`: User is not super_admin

---

### GET `/admin/orgs/{orgId}/entitlements`

Get effective entitlements for an organization.

**Authorization:** super_admin

**Path Parameters:**
- `orgId` (integer, required): Organization ID

**Response:** `200 OK`

```json
{
  "org_id": 1,
  "org_name": "Acme Corporation",
  "entitlements": [
    {
      "module_id": 1,
      "module_key": "sales",
      "module_display_name": "Sales & CRM",
      "status": "enabled",
      "trial_expires_at": null,
      "source": "admin_update",
      "submodules": [
        {
          "submodule_id": 1,
          "submodule_key": "lead_management",
          "submodule_display_name": "Lead Management",
          "enabled": true,
          "effective_status": "enabled",
          "source": null
        }
      ]
    },
    {
      "module_id": 2,
      "module_key": "inventory",
      "module_display_name": "Inventory",
      "status": "trial",
      "trial_expires_at": "2025-12-31T23:59:59Z",
      "source": "admin_update",
      "submodules": []
    },
    {
      "module_id": 3,
      "module_key": "manufacturing",
      "module_display_name": "Manufacturing",
      "status": "disabled",
      "trial_expires_at": null,
      "source": "default",
      "submodules": []
    }
  ]
}
```

**Status Values:**
- `enabled`: Module is fully enabled
- `trial`: Module is in trial period
- `disabled`: Module is disabled

**Effective Status (Submodules):**
- Depends on both module status and submodule enabled flag
- If module is disabled, all submodules are disabled
- If module is trial, submodules inherit trial status

**Error Responses:**
- `401 Unauthorized`: Missing or invalid token
- `403 Forbidden`: User is not super_admin
- `404 Not Found`: Organization not found

---

### PUT `/admin/orgs/{orgId}/entitlements`

Update organization entitlements (diff-only changes).

**Authorization:** super_admin

**Path Parameters:**
- `orgId` (integer, required): Organization ID

**Request Body:**

```json
{
  "reason": "Enabling sales module for Q4 2025 campaign",
  "changes": {
    "modules": [
      {
        "module_key": "sales",
        "status": "enabled"
      },
      {
        "module_key": "inventory",
        "status": "trial",
        "trial_expires_at": "2025-12-31T23:59:59Z"
      }
    ],
    "submodules": [
      {
        "module_key": "sales",
        "submodule_key": "lead_management",
        "enabled": true
      },
      {
        "module_key": "sales",
        "submodule_key": "opportunity_tracking",
        "enabled": false
      }
    ]
  }
}
```

**Request Body Schema:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `reason` | string | Yes | Reason for change (10-500 chars) |
| `changes.modules` | array | No | Module-level changes |
| `changes.submodules` | array | No | Submodule-level changes |

**Module Change Schema:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `module_key` | string | Yes | Module key to update |
| `status` | string | Yes | New status: `enabled`, `disabled`, or `trial` |
| `trial_expires_at` | string (ISO 8601) | Conditional | Required if status is `trial` |

**Submodule Change Schema:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `module_key` | string | Yes | Module key |
| `submodule_key` | string | Yes | Submodule key |
| `enabled` | boolean | Yes | Whether submodule is enabled |

**Response:** `200 OK`

```json
{
  "success": true,
  "message": "Entitlements updated successfully",
  "event_id": 42,
  "updated_entitlements": {
    /* Same structure as GET /admin/orgs/{orgId}/entitlements */
  }
}
```

**Error Responses:**
- `401 Unauthorized`: Missing or invalid token
- `403 Forbidden`: User is not super_admin
- `404 Not Found`: Organization not found
- `422 Unprocessable Entity`: Invalid module/submodule keys or validation error

**Example Error Response:**

```json
{
  "detail": "Invalid module_key: invalid_module"
}
```

---

## App Endpoints

### GET `/orgs/{orgId}/entitlements`

Get effective entitlements for an organization (app use, cached).

**Authorization:** Authenticated user with access to the organization

**Path Parameters:**
- `orgId` (integer, required): Organization ID

**Response:** `200 OK`

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
        "opportunity_tracking": true,
        "sales_dashboard": true
      }
    },
    "inventory": {
      "module_key": "inventory",
      "status": "trial",
      "trial_expires_at": "2025-12-31T23:59:59Z",
      "submodules": {
        "current_stock": true,
        "stock_movements": true
      }
    }
  }
}
```

**Caching:**
- Response is cached with 5-minute TTL
- Cache is invalidated when entitlements are updated via PUT endpoint
- Client should cache this response in memory/localStorage

**Error Responses:**
- `401 Unauthorized`: Missing or invalid token
- `403 Forbidden`: User does not have access to this organization

---

## Entitlement Guard (Backend Middleware)

Backend routes can be protected with the `@require_entitlement` decorator:

```python
from app.core.entitlement_guard import require_entitlement

@router.get("/sales/leads")
@require_entitlement("sales", "lead_management")
async def get_leads(...):
    ...
```

**403 Response (Access Denied):**

```json
{
  "detail": {
    "error": "entitlement_required",
    "module_key": "sales",
    "submodule_key": "lead_management",
    "status": "disabled",
    "reason": "Module 'sales' is disabled for this organization",
    "message": "Module 'sales' access denied: Module 'sales' is disabled for this organization"
  }
}
```

---

## Event Logging

All entitlement changes create audit events in the `entitlement_events` table:

```json
{
  "id": 42,
  "org_id": 1,
  "event_type": "entitlement_update",
  "actor_user_id": 5,
  "reason": "Enabling sales module for Q4 2025 campaign",
  "payload": {
    "changes": {
      "modules": [
        {
          "module_key": "sales",
          "old_status": "disabled",
          "new_status": "enabled"
        }
      ],
      "submodules": [
        {
          "module_key": "sales",
          "submodule_key": "lead_management",
          "old_enabled": false,
          "new_enabled": true
        }
      ]
    }
  },
  "created_at": "2025-11-01T03:00:00Z"
}
```

---

## Rate Limiting

- Admin endpoints: 100 requests per minute
- App endpoints: 1000 requests per minute (cached)

---

## Webhooks (Future)

Webhooks will be added to notify external systems of entitlement changes:

```
POST <webhook_url>
{
  "event": "entitlement.updated",
  "org_id": 1,
  "changes": {...}
}
```

---

## SDK / Client Libraries

TypeScript/JavaScript client is available:

```typescript
import { fetchOrgEntitlements, updateOrgEntitlements } from '@/services/entitlementsApi';

// Fetch entitlements
const entitlements = await fetchOrgEntitlements(orgId, token);

// Update entitlements (admin only)
const result = await updateOrgEntitlements(orgId, {
  reason: "Test",
  changes: { modules: [], submodules: [] }
}, token);
```

---

## Changelog

### v1.0.0 (2025-11-01)

- Initial release
- Module and submodule entitlement management
- Admin and app APIs
- Caching support
- Event logging
