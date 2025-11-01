# Entitlements Architecture

## Overview

This document describes the entitlements system architecture, implementing an **entitlement-first, RBAC-second** enforcement pattern for API access control.

## Core Principles

### 1. Entitlement-First, RBAC-Second

Access control follows a two-tier hierarchy:

1. **Entitlements (Org-Level)**: Determines which modules/features an organization can access (billing/licensing)
2. **RBAC (User-Level)**: Determines what actions individual users can perform within enabled modules

```
Request → Entitlement Check → RBAC Check → Tenant Isolation → Business Logic
          (Can org access?)   (Can user do this?)  (Right org?)
```

### 2. Enforcement Order

All API endpoints follow this enforcement order:

1. **Authentication**: Verify user identity
2. **Entitlement Check**: Verify organization has access to the module/submodule
3. **RBAC Permission Check**: Verify user has permission for the action
4. **Tenant Isolation**: Ensure data access is scoped to user's organization

## Exceptions to Entitlement Checks

### Always-On Modules

These modules skip entitlement checks and are always available:
- **Email**: Core communication functionality

```python
ALWAYS_ON_MODULES = {'email'}
```

### RBAC-Only Modules

These modules are non-billable and skip entitlement checks (RBAC only):
- **Settings**: Organization configuration
- **Admin**: Administrative functions
- **Administration**: Platform-level administration

```python
RBAC_ONLY_MODULES = {'settings', 'admin', 'administration'}
```

### Super Admin Bypass

Super admins can bypass entitlement checks with audit logging:
- Used for support, debugging, and management tasks
- All bypasses are logged for security audit
- Can be disabled per-endpoint if needed

## API Structure

### Module Taxonomy

Modules represent top-level billable features:
- `crm`: Customer Relationship Management (Sales + Marketing)
- `erp`: Enterprise Resource Planning (Master Data, Vouchers, Inventory, Projects, Tasks/Calendar)
- `manufacturing`: Manufacturing operations
- `finance`: Financial management (Accounting + Finance)
- `service`: Service management and help desk
- `hr`: Human Resources
- `analytics`: Reporting and AI Analytics

### Submodules

Submodules provide fine-grained feature control within modules:
- Example: `crm` module → `lead_management`, `opportunity_tracking` submodules
- Submodules inherit from module status (can't be enabled if module is disabled)
- Organization-specific overrides allow disabling specific submodules

### Module Status

- **enabled**: Fully operational, included in plan or purchased
- **disabled**: Not accessible (returns 403 entitlement_denied)
- **trial**: Temporarily enabled with expiration date

## Implementation

### Backend: Unified Dependency

The `require_entitlement` dependency provides consistent enforcement:

```python
from app.api.deps.entitlements import require_entitlement

@router.get("/sales/dashboard")
async def get_sales_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    _: None = Depends(require_entitlement("crm"))
):
    # Business logic here
    ...
```

For submodule-level control:

```python
@router.get("/sales/leads")
async def get_leads(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    _: None = Depends(require_entitlement("crm", "lead_management"))
):
    # Business logic here
    ...
```

### Combined with RBAC

Most endpoints use `require_access` which combines entitlements and RBAC:

```python
from app.core.enforcement import require_access

@router.post("/sales/leads")
async def create_lead(
    auth: tuple = Depends(require_access("crm", "create")),
    db: AsyncSession = Depends(get_db)
):
    current_user, org_id = auth
    # Business logic here
    ...
```

### Frontend: Menu Access Evaluation

Frontend uses `evalMenuItemAccess` to determine menu visibility:

```typescript
import { evalMenuItemAccess } from '@/permissions/menuAccess';

const access = evalMenuItemAccess({
  requireModule: 'crm',
  entitlements: orgEntitlements,
  isAdmin: user.is_admin,
  isSuperAdmin: user.is_super_admin,
});

if (access.result === 'disabled') {
  // Show locked UI with tooltip: access.reason
}
```

## Error Responses

### Entitlement Denied (403)

When organization lacks module access:

```json
{
  "error_type": "entitlement_denied",
  "module_key": "manufacturing",
  "submodule_key": null,
  "status": "disabled",
  "reason": "Module is not enabled for this organization",
  "message": "Organization does not have access to module 'manufacturing'. Module is not enabled for this organization"
}
```

### Permission Denied (403)

When user lacks RBAC permission (after passing entitlement check):

```json
{
  "error_type": "permission_denied",
  "permission": "crm.create",
  "reason": "User lacks required permission 'crm.create'",
  "message": "User does not have required permission 'crm.create'. User lacks required permission 'crm.create'"
}
```

## Data Flow

### 1. Initial Load

```
App Start
  → GET /orgs/{orgId}/entitlements
  → Cache entitlements in EntitlementsContext
  → Render menu based on entitlements
```

### 2. Module Selection

```
Admin opens ModuleSelectionModal
  → Display bundles (CRM, ERP, Manufacturing, etc.)
  → User selects/deselects bundles
  → PUT /admin/orgs/{orgId}/entitlements
  → Invalidate cache
  → Refresh entitlements
  → Menu updates immediately
```

### 3. API Request

```
User clicks menu item
  → Frontend checks entitlements (optional, for UX)
  → API request to endpoint
  → Backend enforces: Entitlement → RBAC → Tenant
  → Response or 403 error
```

## Database Schema

### Core Tables

- **modules**: Module taxonomy (module_key, display_name, icon, etc.)
- **submodules**: Submodule taxonomy (linked to modules)
- **org_entitlements**: Organization module entitlements (status, trial_expires_at)
- **org_subentitlements**: Organization submodule entitlements (enabled boolean)
- **entitlement_events**: Audit log of entitlement changes

### Effective Entitlements View

```sql
CREATE VIEW v_effective_entitlements AS
SELECT 
    oe.org_id,
    m.module_key,
    oe.status AS module_status,
    s.submodule_key,
    COALESCE(ose.enabled, true) AS submodule_enabled,
    CASE 
        WHEN oe.status = 'enabled' AND COALESCE(ose.enabled, true) = true THEN 'enabled'
        WHEN oe.status = 'trial' AND COALESCE(ose.enabled, true) = true 
             AND (oe.trial_expires_at IS NULL OR oe.trial_expires_at > CURRENT_TIMESTAMP) 
             THEN 'trial'
        ELSE 'disabled'
    END AS effective_status
FROM org_entitlements oe
INNER JOIN modules m ON oe.module_id = m.id
LEFT JOIN submodules s ON s.module_id = m.id
LEFT JOIN org_subentitlements ose ON ose.org_id = oe.org_id AND ose.submodule_id = s.id
WHERE m.is_active = true;
```

## Caching Strategy

### Cache Key Pattern

```
entitlements:org:{org_id}
```

### Cache Invalidation

Cache is invalidated on:
- `PUT /admin/orgs/{orgId}/entitlements` (manual update)
- License events (subscription changes)
- Trial expiration events

### TTL

- Default: 5 minutes (300 seconds)
- Can be adjusted based on update frequency

## Feature Flag

### `ENABLE_ENTITLEMENTS_GATING`

Controls whether entitlement enforcement is active:

```python
# app/api/deps/entitlements.py
ENABLE_ENTITLEMENTS_GATING = True  # Set to False to disable
```

**Rollout Plan:**
1. **Phase 1**: Deploy with flag=False (disabled), verify APIs work
2. **Phase 2**: Enable in lower environment, test module selection flows
3. **Phase 3**: Enable in production, monitor entitlement_denied metrics

## Migration from Legacy enabled_modules

### Deprecation Strategy

1. **Read Path**: Replace `organization.enabled_modules` reads with entitlements
2. **Write Path**: Continue syncing enabled_modules for backward compatibility
3. **Cleanup**: Remove enabled_modules column after full migration

### Sync Logic

When entitlements are updated, `enabled_modules` is automatically synced:

```python
# app/services/entitlement_service.py
enabled_modules = {}
for ent in current_entitlements:
    upper_key = ent.module.module_key.upper()
    if ent.status == 'enabled':
        enabled_modules[upper_key] = True
    elif ent.status == 'trial' and not_expired:
        enabled_modules[upper_key] = True
    else:
        enabled_modules[upper_key] = False

org.enabled_modules = enabled_modules
```

## Testing Strategy

### Unit Tests

- `test_entitlement_deps.py`: Dependency logic, exceptions, error structures
- `menuAccess.test.ts`: Frontend evaluation logic

### Integration Tests

- Module selection flows (CRM only, ERP only, combinations)
- API endpoint enforcement (entitlement_denied vs permission_denied)
- Cache invalidation and refresh

### E2E Tests

- Full user journey from module selection to API access
- Trial expiration scenarios
- Super admin bypass verification

## Monitoring & Observability

### Key Metrics

- `entitlement_denied_count`: Number of 403 responses due to entitlements
- `permission_denied_count`: Number of 403 responses due to RBAC
- `super_admin_bypass_count`: Number of bypass events
- `cache_hit_rate`: Entitlements cache efficiency

### Logging

- **INFO**: Super admin bypasses
- **WARNING**: Access denials (entitlement or permission)
- **DEBUG**: Successful access grants, cache operations

## Security Considerations

### Entitlement Bypass Audit

All super admin bypasses are logged:

```python
logger.info(
    f"Super admin {current_user.email} (ID: {current_user.id}) "
    f"bypassed entitlement check for {module_key}/{submodule_key}"
)
```

### Permission Separation

- Entitlements: Managed by super_admin only
- RBAC permissions: Managed by org_admin (within their organization)

### Tenant Isolation

Even with entitlements and permissions, all data access is scoped to organization:

```python
stmt = stmt.where(Model.organization_id == org_id)
```

## Best Practices

### 1. Always Use Unified Dependencies

❌ **Don't** check entitlements manually:
```python
# Bad
if not org.enabled_modules.get('CRM'):
    raise HTTPException(403, "CRM disabled")
```

✅ **Do** use standard dependencies:
```python
# Good
auth: tuple = Depends(require_access("crm", "read"))
```

### 2. Consistent Error Handling

Always use standardized error classes for predictable client handling.

### 3. Frontend Pre-Check (Optional)

Frontend can check entitlements before API calls for better UX, but backend enforcement is mandatory.

### 4. Document Module Mapping

Keep `menu_permission_map.csv` up-to-date with module/submodule mappings.

## Support & Troubleshooting

### Common Issues

**Q: Menu shows item but API returns 403**
- Check entitlement status in admin panel
- Verify cache is not stale (try force refresh)
- Check if trial has expired

**Q: Super admin cannot access disabled module**
- Verify `allow_super_admin_bypass=True` in dependency
- Check feature flag is enabled
- Review audit logs for bypass events

**Q: Module selection doesn't update menu**
- Check cache invalidation is working
- Verify EntitlementsContext refresh hook
- Check browser console for API errors

## References

- [Menu Permission Mapping](menu_permission_map.csv)
- [Admin Entitlement API Contract](admin_entitlement_api_contract.json)
- [Module Bundle Mapping](../frontend/src/config/moduleBundleMap.ts)
