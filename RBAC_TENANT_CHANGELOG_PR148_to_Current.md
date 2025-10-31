# RBAC & Tenant System: Consolidated Changelog (PR #148 to Current)

## Overview

This document consolidates all changes made to the RBAC (Role-Based Access Control) and tenant/organization management system from PR #148 through the current implementation. It replaces previous per-PR summaries with a comprehensive view of the evolution of these critical systems.

---

## Table of Contents

1. [Core RBAC System](#core-rbac-system)
2. [Permission Management](#permission-management)
3. [Organization & Tenant Management](#organization--tenant-management)
4. [UI/UX Improvements](#uiux-improvements)
5. [Bug Fixes](#bug-fixes)
6. [Security Enhancements](#security-enhancements)

---

## Core RBAC System

### Permission Model Architecture

**Database Models** (`app/models/rbac_models.py`):
- `ServicePermission`: Defines granular permissions (module.action format)
- `ServiceRole`: Organization-scoped roles with permission sets
- `ServiceRolePermission`: Maps roles to permissions
- `UserServiceRole`: Assigns roles to users within organizations

**Key Features**:
- Module-based permission namespacing (e.g., `master_data.read`, `inventory.write`)
- Hierarchical role structure with inheritance
- Organization-scoped isolation
- Dynamic permission assignment

### Permission Normalization Layer

**Frontend Utility** (`frontend/src/utils/permissionNormalizer.ts`):

```typescript
// Maps backend permission keys to frontend canonical keys
const PERMISSION_ALIASES = {
  'master_data.view': ['master_data.read', 'master_data.manage'],
  'inventory.view': ['inventory.read', 'inventory.manage'],
  // ... additional mappings
};
```

**Purpose**:
- Resolves backend/frontend permission key mismatches
- Backend returns `*.read`, frontend expects `*.view`
- Supports module-level base access inference
- Enables permission alias resolution

**Integration Points**:
- `useSharedPermissions` hook
- `AuthContext` permission loading
- Menu filtering and visibility logic

### Service & Enforcement Layer

**Backend Enforcement** (`app/core/enforcement.py`):
- `require_access(module: str, action: str)`: FastAPI dependency for route protection
- Validates user has required permission for module/action
- Returns `(user, organization_id)` tuple
- Raises HTTP 403 on permission denial

**Frontend Utilities**:
- `hasPermission(permission)`: Check single permission
- `hasModuleAccess(module)`: Check module-level access
- `hasSubmoduleAccess(module, submodule)`: Check specific submodule

---

## Permission Management

### Default Permission Initialization

**Backend Service** (`app/services/rbac.py`):
```python
async def initialize_default_permissions(self):
    """Seeds default permissions on system startup"""
    # Creates core permissions for all modules
    # Executed during app startup lifecycle
```

**Modules with Permissions**:
- Master Data (vendors, customers, products, employees, company_details, etc.)
- Inventory & Stock Management
- Manufacturing (BOM, work orders, quality control)
- Financial (vouchers, accounting, banking)
- Sales & CRM
- HR & Payroll
- Reports & Analytics
- Email & Communication
- Settings & Administration

### Organization Role Management

**Automatic Role Creation**:
- `org_admin` role created on organization setup
- Grants comprehensive permissions across enabled modules
- Automatically assigned to organization creator

**Role Hierarchy**:
1. **Super Admin** (Platform-level): All permissions
2. **Org Admin** (Organization-level): Full org permissions
3. **Custom Roles** (Organization-defined): Selective permissions

---

## Organization & Tenant Management

### Multi-Tenancy Architecture

**Data Isolation**:
- Every entity has `organization_id` foreign key
- Queries automatically filtered by organization context
- Row-level security enforced at ORM level

**Organization Lifecycle**:
```
Create Organization → Issue License → Seed Default Data → Assign Admin
```

### Organization Deletion & Reset

**Issue Fixed**: Cascade delete error on `UserServiceRole.organization_id`

**Root Cause**: 
`UserServiceRole` model lacks `organization_id` column - it's related to organizations through `ServiceRole`.

**Solution** (`app/services/reset_service.py`):
```python
# Delete user_service_roles via ServiceRole join
user_service_roles_subquery = select(UserServiceRole.id).join(
    ServiceRole, UserServiceRole.role_id == ServiceRole.id
).where(ServiceRole.organization_id == organization_id)

await db.execute(
    delete(UserServiceRole).where(UserServiceRole.id.in_(user_service_roles_subquery))
)
```

**Applied To**:
- `reset_organization_business_data()`: Organization-specific reset
- `factory_default_system()`: Complete system wipe (unaffected - deletes all)

### License Management

**License Creation Flow**:
1. Admin creates organization with license details
2. System generates temporary password for org admin
3. Sends welcome email with credentials
4. Admin must change password on first login

**Pincode Lookup Enhancement**:

**Issue**: 401 Unauthorized during license creation pincode lookup

**Changes**:
- **Backend** (`app/api/pincode.py`): Removed auth requirement (public endpoint)
- **Frontend** (`frontend/src/hooks/usePincodeLookup.ts`): 
  - Switched from bare axios to centralized `apiClient`
  - Added single-flight pattern (prevents duplicate requests)
  - Added session-based caching
  - Graceful handling of auth/network errors

```typescript
// Before
const response = await axios.get(`/api/v1/pincode/lookup/${pincode}`);

// After
const response = await apiClient.get<PincodeData>(`/pincode/lookup/${pincode}`);
```

---

## UI/UX Improvements

### Global MegaMenu Implementation

**Issue**: MegaMenu only visible on dashboard, not other pages

**Root Cause**: MegaMenu mounted per-page via `DashboardLayout`, not globally

**Solution**:
- Created `AppLayout` component (`frontend/src/components/AppLayout.tsx`)
- Wraps all pages in `_app.tsx`
- Conditionally renders MegaMenu for authenticated users
- Excludes public routes (login, register, etc.)

**Benefits**:
- Consistent navigation across all authenticated pages
- Single source of truth for menu state
- Simplified page components (no need to manually include menu)

### Permission-Aware Menu Filtering

**Menu Configuration** (`frontend/src/components/menuConfig.tsx`):
```typescript
{
  name: 'Vendors',
  path: '/masters/vendors',
  permission: 'master_data.view',
  requireModule: 'master_data',
  requireSubmodule: { module: 'master_data', submodule: 'vendors' }
}
```

**Filtering Logic** (`MegaMenu.tsx`):
- Checks `hasPermission(item.permission)`
- Validates `hasModuleAccess(item.requireModule)`
- Verifies `hasSubmoduleAccess(item.requireSubmodule)`
- Falls back gracefully when permissions unavailable

**Debugging**:
```typescript
console.log('Menu item requires:', item.permission);
console.log('User has permission:', hasPermission(item.permission));
console.log('Required keys vs normalized:', debugPermissions(...));
```

### Mobile-First Enhancements

- MegaMenu detects mobile via `useMobileDetection` hook
- Switches to `MobileNav` drawer on small screens
- Touch-optimized navigation for mobile devices

---

## Bug Fixes

### 1. Organization Deletion Cascade Error

**Symptom**: 500 Error - `type object 'UserServiceRole' has no attribute 'organization_id'`

**Fix**: Updated cascade delete to use proper SQL joins through `ServiceRole` relationship

**Files Changed**:
- `app/services/reset_service.py`

### 2. MegaMenu "No Menu Items Available" Despite Permissions

**Symptom**: org_admin user sees fallback message despite successful permission load

**Root Cause**: Backend returns `*.read`, frontend expects `*.view`

**Fix**: Implemented permission normalization layer with alias mapping

**Files Changed**:
- `frontend/src/utils/permissionNormalizer.ts` (new)
- `frontend/src/hooks/useSharedPermissions.ts`

### 3. Pincode Lookup 401 Unauthorized

**Symptom**: Repeated 401s on `GET /api/v1/pincode/lookup/{code}` during license creation

**Fix**: 
- Made pincode endpoint public (no auth required)
- Updated frontend hook to use authenticated client as fallback
- Added request deduplication and caching

**Files Changed**:
- `app/api/pincode.py`
- `frontend/src/hooks/usePincodeLookup.ts`

### 4. Admin Password Reset Endpoint 404

**Symptom**: `POST /api/v1/password/admin-reset` returns 404

**Root Cause**: Password router not registered in main application

**Fix**: Added password router registration in `app/main.py`

**Route Available**: `POST /api/v1/password/admin-reset`

**Payload**:
```json
{
  "user_email": "user@example.com"
}
```

**Response**:
```json
{
  "message": "Password reset successfully",
  "target_email": "user@example.com",
  "new_password": "TempPassword123",
  "email_sent": true,
  "must_change_password": true
}
```

---

## Security Enhancements

### 1. Permission-Based Access Control

**Route Protection**:
```python
@router.get("/vendors")
async def get_vendors(
    auth: tuple = Depends(require_access("vendor", "read")),
    db: AsyncSession = Depends(get_db)
):
    current_user, org_id = auth
    # org_id automatically scopes query
```

### 2. Audit Logging

**Password Reset Audit** (`app/api/v1/password.py`):
```python
await AuditLogger.log_password_reset(
    db=db,
    admin_email=current_user.email,
    target_email=user.email,
    success=True,
    reset_type="ADMIN_PASSWORD_RESET"
)
```

### 3. CORS & Authentication

**Forced CORS Middleware** (`app/main.py`):
- Ensures CORS headers on all responses (including errors)
- Handles OPTIONS preflight correctly
- Supports credentials for auth

**Token Refresh Flow**:
- Access token expires → 401
- Frontend automatically attempts refresh
- On failure → redirect to login
- Preserves form data and return URL

---

## Migration Path for Existing Installations

### 1. Database Migrations

```bash
# Apply RBAC schema changes
alembic upgrade head
```

### 2. Initialize Default Permissions

Permissions are automatically initialized on app startup via `init_default_permissions()` background task.

### 3. Assign Roles to Existing Users

```bash
# Run admin script
python scripts/assign_service_role.py --organization-id <id> --user-id <id> --role org_admin
```

### 4. Enable Modules for Organizations

Modules are controlled via `Organization.enabled_modules` JSON field:

```python
organization.enabled_modules = {
    "master_data": ["vendors", "customers", "products"],
    "inventory": ["stock", "warehouses"],
    "manufacturing": ["work_orders", "bom"]
}
```

---

## API Reference

### Permission Endpoints

**Get User Permissions**:
```
GET /api/v1/rbac/users/{user_id}/permissions
```

**Get All Permissions**:
```
GET /api/v1/rbac/permissions
```

**Assign Role to User**:
```
POST /api/v1/rbac/users/{user_id}/roles/{role_id}
```

### Organization Management

**Get Current Organization**:
```
GET /api/v1/organizations/current
```

**Reset Organization Data**:
```
POST /api/v1/organizations/reset-business-data
```

**Factory Default** (Super Admin Only):
```
POST /api/v1/organizations/factory-default
```

---

## Frontend Permission Utilities

### useSharedPermissions Hook

```typescript
const {
  hasPermission,
  hasModuleAccess,
  hasSubmoduleAccess,
  userPermissions
} = useSharedPermissions();

// Check permission
if (hasPermission('master_data.view')) {
  // Show vendors menu
}

// Check module access
if (hasModuleAccess('inventory')) {
  // Enable inventory features
}

// Check submodule access
if (hasSubmoduleAccess('master_data', 'vendors')) {
  // Show vendor-specific options
}
```

### Permission Normalization

```typescript
import { normalizePermissions, hasPermission, debugPermissions } from '@/utils/permissionNormalizer';

// Normalize backend permissions
const backendPerms = ['master_data.read', 'inventory.read'];
const normalized = normalizePermissions(backendPerms);
// Returns: Set(['master_data.read', 'master_data.view', 'inventory.read', 'inventory.view', ...])

// Check with aliases
hasPermission(normalized, 'master_data.view'); // true (aliased from .read)

// Debug in development
debugPermissions(backendPerms, ['master_data.view', 'inventory.view']);
// Logs comparison and missing permissions
```

---

## Testing Checklist

### Backend Tests

- [ ] Permission enforcement on protected routes
- [ ] Organization-scoped data access
- [ ] Role assignment and removal
- [ ] Cascade delete without errors
- [ ] Public endpoint access (pincode)
- [ ] Admin password reset flow

### Frontend Tests

- [ ] MegaMenu visibility on all authenticated pages
- [ ] Menu items filtered by permissions
- [ ] Permission normalization (*.read → *.view)
- [ ] Pincode lookup without 401 errors
- [ ] Global layout on non-dashboard pages

### Integration Tests

- [ ] Create organization → assign role → user can access modules
- [ ] Disable module → menu items hidden
- [ ] Revoke permission → route returns 403
- [ ] Delete organization → clean cascade (no 500)

---

## Performance Considerations

### Caching Strategies

**Frontend**:
- Permission data cached in AuthContext
- Menu configuration memoized via useMemo
- Pincode lookups cached per session

**Backend**:
- Permission checks leverage SQLAlchemy eager loading
- Organization data loaded once per request via dependency injection

### Optimization Tips

1. **Minimize Permission Checks**: Use `userPermissions` object instead of repeated `hasPermission()` calls
2. **Debounce Permission Fetches**: Avoid refetching on every render
3. **Lazy Load Menus**: Render menus on-demand vs all upfront

---

## Known Limitations

1. **Permission Inheritance**: Currently flat structure, no role hierarchy
2. **Custom Permissions**: Organizations cannot define custom permissions (only assign existing)
3. **Temporal Permissions**: No time-based or expiring permissions
4. **Audit Detail**: Limited detail on permission checks (only logs failures)

---

## Future Enhancements

### Planned Features

- [ ] Permission groups for easier bulk assignment
- [ ] Role templates for common job functions
- [ ] Permission request workflow (user → admin approval)
- [ ] Audit dashboard for permission changes
- [ ] API rate limiting per role
- [ ] Custom permission creation for organizations

### Under Consideration

- [ ] Attribute-based access control (ABAC)
- [ ] Conditional permissions (e.g., "edit own records")
- [ ] Permission delegation (temporary grants)

---

## Change Log

### Current PR (Post-PR #148)

**Date**: 2025-10-31

**Changes**:
1. ✅ Fixed organization deletion cascade error (UserServiceRole)
2. ✅ Implemented permission normalization layer
3. ✅ Made pincode endpoint public + enhanced frontend hook
4. ✅ Registered password router for admin-reset endpoint
5. ✅ Created global AppLayout with MegaMenu for all pages
6. ✅ Created this consolidated documentation

**Files Modified**:
- Backend: 3 files (reset_service.py, pincode.py, main.py)
- Frontend: 5 files (usePincodeLookup.ts, useSharedPermissions.ts, permissionNormalizer.ts, AppLayout.tsx, _app.tsx, DashboardLayout.tsx)

---

## Support & Resources

### Documentation

- [RBAC Quick Start](./RBAC_QUICK_START.md)
- [Permission Matrix](./PERMISSION_MATRIX.md)
- [Module-to-Menu Mapping](./MODULE_TO_MENU_MAPPING_GUIDE.md)

### Related PRs

- PR #148: Initial RBAC implementation
- See individual PR docs for historical context (deprecated by this consolidated doc)

### Contact

For questions or issues related to RBAC/tenant system:
- GitHub Issues: Use `[RBAC]` or `[Tenant]` tag
- Team Slack: #rbac-support channel

---

## Appendix

### Permission Naming Conventions

**Format**: `module.action`

**Actions**:
- `read` / `view`: Read-only access
- `create`: Create new records
- `update` / `edit`: Modify existing records
- `delete`: Remove records
- `manage`: Full CRUD access
- `export`: Export data
- `import`: Import data

**Examples**:
- `master_data.read`
- `inventory.manage`
- `reports.export`
- `settings.update`

### Module Registry

Complete list of modules and their submodules:

```python
{
  "master_data": ["vendors", "customers", "products", "employees", "company_details", "categories", "units", "bom", "chart_of_accounts", "tax_codes", "payment_terms", "bank_account"],
  "inventory": ["stock", "warehouses", "adjustments", "transfers"],
  "manufacturing": ["work_orders", "bom", "quality_control", "production_planning"],
  "vouchers": ["sales_invoice", "purchase_order", "grn", "payment_voucher"],
  "accounting": ["ledgers", "journal_entries", "trial_balance"],
  "sales": ["orders", "invoices", "quotations"],
  "crm": ["leads", "contacts", "opportunities"],
  "hr": ["employees", "attendance", "leave"],
  "payroll": ["salary", "deductions", "payslips"],
  "reports": ["financial", "operational", "inventory"],
  "email": ["accounts", "messages", "folders"],
  "settings": ["users", "roles", "organization", "modules"],
  "admin": ["organizations", "licenses", "system_stats"]
}
```

---

**Document Version**: 1.0  
**Last Updated**: 2025-10-31  
**Maintained By**: Development Team
