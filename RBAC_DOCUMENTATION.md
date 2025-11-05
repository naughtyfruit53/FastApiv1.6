# Comprehensive RBAC System Documentation

## Overview

This document describes the comprehensive 3-layer security model implemented in FastAPI v1.6 ERP system, which includes Tenant Isolation, Entitlement Management, and Role-Based Access Control (RBAC).

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Layer 1: Tenant Isolation](#layer-1-tenant-isolation)
3. [Layer 2: Entitlement Management](#layer-2-entitlement-management)
4. [Layer 3: RBAC Permissions](#layer-3-rbac-permissions)
5. [Constants and Configuration](#constants-and-configuration)
6. [Backend Implementation](#backend-implementation)
7. [Frontend Implementation](#frontend-implementation)
8. [Testing Strategy](#testing-strategy)
9. [Best Practices](#best-practices)
10. [Common Patterns](#common-patterns)

---

## Architecture Overview

The security system is built on three fundamental layers that work together to provide comprehensive access control:

### The 3-Layer Security Model

```
┌─────────────────────────────────────────────────────────────┐
│                     Layer 3: RBAC                           │
│              (User Permissions & Roles)                     │
│  - User roles (super_admin, admin, manager, executive)     │
│  - Permission-based access control                          │
│  - Role hierarchy and management                            │
├─────────────────────────────────────────────────────────────┤
│                Layer 2: Entitlements                        │
│              (Module/Feature Access)                        │
│  - Module status (enabled, disabled, trial)                │
│  - Submodule access control                                 │
│  - License-based feature gating                             │
├─────────────────────────────────────────────────────────────┤
│                Layer 1: Tenant                              │
│              (Organization Isolation)                       │
│  - Organization context (org_id)                            │
│  - Multi-tenancy enforcement                                │
│  - Data isolation                                           │
└─────────────────────────────────────────────────────────────┘
```

### Security Flow

Every request goes through all three layers:

1. **Tenant Check**: Validate organization context and user's org membership
2. **Entitlement Check**: Verify organization has access to the requested module/feature
3. **RBAC Check**: Confirm user has the required permission for the action

Any layer can deny access, resulting in a 403 Forbidden response with detailed error information.

---

## Layer 1: Tenant Isolation

### Purpose

Ensures complete data isolation between organizations in the multi-tenant system.

### Key Components

#### Backend

- **`app/core/tenant.py`**: Core tenant context management
  - `TenantContext`: Context variables for org_id and user_id
  - `TenantQueryFilter`: SQLAlchemy query filtering
  - `TenantMiddleware`: Request middleware for extracting org_id

- **`app/utils/tenant_helpers.py`**: Tenant utility functions
  - `TenantHelper`: Main helper class
  - Organization context validation
  - User org access enforcement
  - Record-level tenant checks

#### Frontend

- **`src/context/OrganizationContext.tsx`**: React context for current organization
- **`src/utils/permissionHelpers.ts`**: Tenant validation functions

### Usage Examples

#### Backend: Enforce Tenant Access

```python
from app.utils.tenant_helpers import enforce_user_org_access, validate_data_org_id

# Validate user can access organization
enforce_user_org_access(current_user, org_id)

# Validate and set org_id in create/update data
data = validate_data_org_id(request_data, current_user)
```

#### Backend: Apply Tenant Filter to Queries

```python
from app.utils.tenant_helpers import apply_org_filter
from sqlalchemy import select

stmt = select(Lead)
stmt = apply_org_filter(stmt, Lead, user=current_user)
result = await db.execute(stmt)
```

#### Frontend: Check Tenant Context

```typescript
import { usePermissionCheck } from '@/hooks/usePermissionCheck';

function MyComponent() {
  const { hasTenantContext, checkTenantAccess } = usePermissionCheck();

  if (!hasTenantContext) {
    return <div>No organization context</div>;
  }

  // Check access to specific org
  const canAccess = checkTenantAccess(targetOrgId);
}
```

### Key Principles

1. **Always require org_id**: Every data access must have organization context
2. **Super admin flexibility**: Super admins can access any org but must specify org_id
3. **User constraints**: Regular users can only access their own organization
4. **Query filtering**: All queries automatically filtered by org_id
5. **Data validation**: All creates/updates validated for proper org_id

---

## Layer 2: Entitlement Management

### Purpose

Controls which modules and features are available to each organization based on their license and subscription.

### Module Status Types

- **`enabled`**: Full access to the module
- **`disabled`**: No access to the module
- **`trial`**: Temporary access with expiry date

### Special Module Categories

- **Always-on modules**: Always available regardless of entitlements (e.g., `email`, `dashboard`)
- **RBAC-only modules**: Controlled by permissions only, not entitlements (e.g., `settings`, `admin`, `organization`)

### Key Components

#### Backend

- **`app/core/entitlement_guard.py`**: Decorator-based entitlement enforcement
  - `require_entitlement()`: Decorator for routes
  - `EntitlementGuardException`: Custom exception with details

- **`app/services/entitlement_service.py`**: Entitlement business logic
  - Module status management
  - Submodule access control
  - Trial period handling

- **`app/utils/entitlement_helpers.py`**: Entitlement utility functions
  - `EntitlementHelper`: Main helper class
  - Module status checking
  - Entitlement enforcement

#### Frontend

- **`src/hooks/useEntitlements.ts`**: React hook for entitlements
- **`src/utils/permissionHelpers.ts`**: Entitlement checking functions

### Usage Examples

#### Backend: Check Entitlement

```python
from app.utils.entitlement_helpers import enforce_module_entitlement

# Enforce module entitlement
await enforce_module_entitlement(db, org_id, "manufacturing")

# Check without enforcing
is_entitled, status, reason = await check_module_entitlement(
    db, org_id, "crm", "lead_management"
)
```

#### Backend: Use Decorator

```python
from app.core.entitlement_guard import require_entitlement

@router.get("/manufacturing/orders")
@require_entitlement("manufacturing")
async def get_orders(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Entitlement is automatically checked
    pass
```

#### Frontend: Check Module Entitlement

```typescript
import { usePermissionCheck } from '@/hooks/usePermissionCheck';

function MyComponent() {
  const { 
    checkModuleEntitled, 
    getModuleEntitlementStatus 
  } = usePermissionCheck();

  const isEntitled = checkModuleEntitled('manufacturing');
  const status = getModuleEntitlementStatus('manufacturing'); // 'enabled' | 'disabled' | 'trial'
}
```

### Key Principles

1. **License-based**: Entitlements are tied to organization licenses
2. **Trial support**: Temporary access with automatic expiry
3. **Granular control**: Module and submodule level control
4. **Always-on bypass**: Certain modules always available
5. **RBAC-only bypass**: Admin modules controlled by permissions only

---

## Layer 3: RBAC Permissions

### Purpose

Controls what actions users can perform within entitled modules based on their role and permissions.

### Role Hierarchy

```
Super Admin (100) - Platform-level access, all organizations
    ↓
Admin (80) - Organization-level full access
    ↓
Management (70) - Similar to admin, organizational management
    ↓
Manager (50) - Module-level access, manages executives
    ↓
Executive (30) - Submodule-level access, reports to manager
    ↓
User (10) - Basic access
```

### Permission Format

Permissions follow these patterns:

- **Module-level**: `{module}.{action}` (e.g., `crm.read`, `crm.write`)
- **Wildcard**: `{module}.*` (e.g., `crm.*` for all CRM actions)
- **Submodule**: `{module}_{submodule}_{action}` (e.g., `crm_leads_read`)
- **Admin**: `{module}_admin` (e.g., `crm_admin`)

### Key Components

#### Backend

- **`app/services/rbac.py`**: Core RBAC service
  - Role management
  - Permission management
  - User-role assignments

- **`app/utils/rbac_helpers.py`**: RBAC utility functions
  - `RBACHelper`: Main helper class
  - Permission checking
  - Role hierarchy enforcement

- **`app/core/enforcement.py`**: Combined enforcement decorator
  - `require_access()`: Checks both entitlement and permission

#### Frontend

- **`src/context/AuthContext.tsx`**: User authentication and permissions
- **`src/utils/permissionHelpers.ts`**: Permission checking functions

### Usage Examples

#### Backend: Check Permission

```python
from app.utils.rbac_helpers import has_permission, enforce_permission

# Check if user has permission
if await has_permission(db, current_user, "crm.delete"):
    # Perform action
    pass

# Enforce permission (raises exception if denied)
await enforce_permission(db, current_user, "manufacturing.create")
```

#### Backend: Check Role Management

```python
from app.utils.rbac_helpers import can_manage_role, enforce_can_manage_role

# Check if user can manage another role
if can_manage_role(current_user.role, target_role):
    # Allow role assignment
    pass

# Enforce (raises exception if denied)
enforce_can_manage_role(current_user.role, target_role)
```

#### Frontend: Check Permission

```typescript
import { usePermissionCheck } from '@/hooks/usePermissionCheck';

function MyComponent() {
  const { 
    checkPermission, 
    checkIsSuperAdmin,
    checkIsOrgAdmin 
  } = usePermissionCheck();

  const canDelete = checkPermission('crm.delete');
  const isSuperAdmin = checkIsSuperAdmin();
  const isAdmin = checkIsOrgAdmin();
}
```

### Role-Specific Behaviors

#### Super Admin

- Bypasses all permission checks
- Can access any organization
- Must specify org_id explicitly
- Can create new organizations

#### Admin / Management

- Full access within their organization
- Can create and manage managers
- Can manage executives
- Still respects entitlements

#### Manager

- Access only to assigned modules
- Full access to all submodules in assigned modules
- Can create and manage executives in their modules
- Sees own and team records

#### Executive

- Must report to a manager
- Access limited to manager's modules
- Granular submodule permissions (e.g., read-only on some, create/update on others)
- Sees only own records

---

## Constants and Configuration

### Backend Constants

File: **`app/core/constants.py`**

```python
from app.core.constants import (
    # Roles
    UserRole,
    SUPER_ADMIN_BYPASS_ROLES,
    ORG_ADMIN_ROLES,
    ROLE_HIERARCHY,
    
    # Modules
    CoreModule,
    ExtendedModule,
    AdvancedModule,
    SystemModule,
    
    # Entitlements
    ModuleStatusEnum,
    ALWAYS_ON_MODULES,
    RBAC_ONLY_MODULES,
    
    # Enforcement
    EnforcementLevel,
    ENFORCEMENT_ERRORS,
)
```

### Frontend Constants

File: **`frontend/src/constants/rbac.ts`**

```typescript
import {
  UserRole,
  ModuleStatus,
  SUPER_ADMIN_ROLES,
  ORG_ADMIN_ROLES,
  ALWAYS_ON_MODULES,
  RBAC_ONLY_MODULES,
  PERMISSION_PATTERNS,
  ENFORCEMENT_ERROR_MESSAGES,
} from '@/constants/rbac';
```

---

## Backend Implementation

### API Endpoint Pattern

Every protected endpoint should follow this pattern:

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.enforcement import require_access
from app.utils.tenant_helpers import apply_org_filter
from app.models import MyModel

router = APIRouter(prefix="/mymodule", tags=["MyModule"])

@router.get("/items")
async def get_items(
    # Layer 1 & 3: Tenant + RBAC check
    auth: tuple = Depends(require_access("mymodule", "read")),
    db: AsyncSession = Depends(get_db)
):
    current_user, org_id = auth
    
    # Layer 1: Apply tenant filter
    stmt = select(MyModel)
    stmt = apply_org_filter(stmt, MyModel, user=current_user)
    
    result = await db.execute(stmt)
    return result.scalars().all()

@router.post("/items")
async def create_item(
    data: MyModelCreate,
    auth: tuple = Depends(require_access("mymodule", "create")),
    db: AsyncSession = Depends(get_db)
):
    current_user, org_id = auth
    
    # Layer 1: Validate org_id
    validated_data = validate_data_org_id(data.model_dump(), current_user)
    
    # Create item
    item = MyModel(**validated_data)
    db.add(item)
    await db.commit()
    
    return item
```

### Service Layer Pattern

```python
from app.utils.tenant_helpers import TenantHelper, apply_org_filter
from app.utils.entitlement_helpers import EntitlementHelper
from app.utils.rbac_helpers import RBACHelper

class MyService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_items(self, user: User) -> List[MyModel]:
        # Layer 1: Ensure org context
        org_id = TenantHelper.ensure_org_context()
        
        # Layer 2: Check entitlement
        await EntitlementHelper.enforce_module_entitlement(
            self.db, org_id, "mymodule"
        )
        
        # Layer 3: Check permission
        await RBACHelper.enforce_permission(self.db, user, "mymodule.read")
        
        # Query with tenant filter
        stmt = select(MyModel)
        stmt = apply_org_filter(stmt, MyModel, user=user)
        
        result = await self.db.execute(stmt)
        return result.scalars().all()
```

---

## Frontend Implementation

### Component Pattern

```typescript
import React from 'react';
import { usePermissionCheck } from '@/hooks/usePermissionCheck';

function MyComponent() {
  const {
    isReady,
    checkModuleAccess,
    checkPermission,
  } = usePermissionCheck();

  if (!isReady) {
    return <div>Loading...</div>;
  }

  // Check full access (all 3 layers)
  const moduleAccess = checkModuleAccess('crm', 'read');
  
  if (!moduleAccess.hasPermission) {
    return <div>Access Denied: {moduleAccess.reason}</div>;
  }

  const canDelete = checkPermission('crm.delete');

  return (
    <div>
      <h1>CRM Module</h1>
      {canDelete && (
        <button onClick={handleDelete}>Delete</button>
      )}
    </div>
  );
}
```

### Menu Filtering Pattern

```typescript
import { filterMenuItems } from '@/utils/permissionHelpers';
import { useAuth } from '@/context/AuthContext';
import { useEntitlements } from '@/hooks/useEntitlements';

function Menu() {
  const { userPermissions } = useAuth();
  const { entitlements } = useEntitlements();

  const menuItems = [
    { label: 'CRM', moduleKey: 'crm', permission: 'crm.read' },
    { label: 'Manufacturing', moduleKey: 'manufacturing', permission: 'manufacturing.read' },
    { label: 'Settings', moduleKey: 'settings', permission: 'settings.view' },
  ];

  const filteredItems = filterMenuItems(
    menuItems,
    userPermissions,
    entitlements
  );

  return (
    <nav>
      {filteredItems.map(item => (
        <a key={item.label} href={`/${item.moduleKey}`}>
          {item.label}
        </a>
      ))}
    </nav>
  );
}
```

---

## Testing Strategy

### Test Files

1. **`app/tests/test_three_layer_security.py`** ✅ **NEW** (500+ lines)
   - **TestThreeLayerSecurity**: Tests each layer independently
     - Layer 1 (Tenant): User org access, super admin bypass, cross-org denial
     - Layer 2 (Entitlement): Module enabled/disabled, always-on modules, RBAC-only modules
     - Layer 3 (RBAC): Permission checks, role hierarchy, wildcards
   - **TestIntegratedThreeLayerFlow**: Complete flow tests
     - All 3 layers passing successfully
     - Failures at each individual layer
   - **TestRoleHierarchyAndSpecialCases**: Edge cases
     - Super admin RBAC bypass
     - Always-on and RBAC-only module handling
     - Role management hierarchy (manager can manage executive, etc.)
   - **TestErrorMessages**: Validation of error messages
     - Tenant mismatch errors
     - Entitlement denial errors
     - Permission denial errors

2. **`app/tests/test_user_role_flows.py`** ✅ **NEW** (500+ lines)
   - **TestAdminWorkflow**: Admin user capabilities
     - Full organization access
     - Can create managers and executives
     - Still respects entitlements
   - **TestManagerWorkflow**: Manager user behavior
     - Module-scoped access (only assigned modules)
     - Can create executives in their modules
     - Cannot create other managers or admins
     - Sees team records
   - **TestExecutiveWorkflow**: Executive user behavior
     - Submodule-scoped access (granular permissions)
     - Must report to a manager
     - Cannot manage other users
     - Sees only own records
   - **TestRoleTransitions**: Promotion/demotion scenarios
   - **TestCrossOrgScenarios**: Multi-organization cases
   - **TestModuleAssignmentScenarios**: Module and submodule assignments
   - **TestPermissionPatterns**: Wildcards and admin permissions

3. **`app/tests/test_entitlement_permission_sync.py`** (TODO)
   - Permission revocation on entitlement changes
   - Role-specific sync behaviors
   - Bulk update operations

4. **Existing Tests** (Already present)
   - `test_strict_entitlement_enforcement.py` - Entitlement enforcement without bypasses
   - `test_strict_rbac_enforcement.py` - RBAC enforcement validation
   - `test_organization_modules.py` - Organization module access
   - `test_rbac_resilience.py` - RBAC system resilience

### Running Tests

```bash
# Run new comprehensive 3-layer security tests
pytest app/tests/test_three_layer_security.py -v

# Run new role workflow tests
pytest app/tests/test_user_role_flows.py -v

# Run all security-related tests
pytest app/tests/test_three_layer_security.py app/tests/test_user_role_flows.py -v

# Run existing entitlement enforcement tests
pytest app/tests/test_strict_entitlement_enforcement.py -v

# Run existing RBAC enforcement tests
pytest app/tests/test_strict_rbac_enforcement.py -v

# Run all tests
pytest app/tests/ -v

# Run with coverage
pytest app/tests/ --cov=app.utils --cov=app.core --cov-report=html
```

### Test Coverage Summary

**New Test Coverage (2025-11-05):**
- ✅ **55+ test cases** for 3-layer security
- ✅ **35+ test cases** for role workflows
- ✅ Layer 1 (Tenant): 8 test scenarios
- ✅ Layer 2 (Entitlement): 12 test scenarios
- ✅ Layer 3 (RBAC): 15 test scenarios
- ✅ Integrated flows: 10 test scenarios
- ✅ Role workflows: 25+ test scenarios
- ✅ Edge cases: 20+ test scenarios

**Total: 90+ new test cases** covering the complete 3-layer security model

---

## Best Practices

### 1. Always Use All Three Layers

Never skip any layer. Even if you think a user "should" have access, enforce all three checks.

### 2. Use Helpers and Utilities

Don't implement checks manually. Use the provided helper functions:

```python
# ✅ Good
await enforce_module_entitlement(db, org_id, "crm")

# ❌ Bad
service = EntitlementService(db)
is_entitled, _, _ = await service.check_entitlement(org_id, "crm")
if not is_entitled:
    raise HTTPException(...)
```

### 3. Apply Tenant Filters to All Queries

```python
# ✅ Good
stmt = select(Lead)
stmt = apply_org_filter(stmt, Lead, user=current_user)

# ❌ Bad
stmt = select(Lead).where(Lead.organization_id == org_id)
```

### 4. Use Consistent Error Messages

Use constants from `ENFORCEMENT_ERRORS` for consistent user experience.

### 5. Log Security Events

Log all access denials with context:

```python
logger.warning(
    f"User {user.email} denied access to {module}. "
    f"Reason: {reason}"
)
```

### 6. Test Edge Cases

Always test:
- Super admin access
- Cross-org access attempts
- Missing org context
- Disabled modules
- Trial expiry
- Insufficient permissions

---

## Common Patterns

### Pattern 1: API Endpoint with Full Enforcement

```python
@router.get("/items")
async def get_items(
    auth: tuple = Depends(require_access("module", "read")),
    db: AsyncSession = Depends(get_db)
):
    current_user, org_id = auth
    stmt = apply_org_filter(select(Model), Model, user=current_user)
    result = await db.execute(stmt)
    return result.scalars().all()
```

### Pattern 2: Manual 3-Layer Check

```python
# Layer 1
enforce_user_org_access(current_user, org_id)

# Layer 2
await enforce_module_entitlement(db, org_id, "crm")

# Layer 3
await enforce_permission(db, current_user, "crm.delete")
```

### Pattern 3: Conditional Rendering Based on Access

```typescript
const { checkModuleAccess } = usePermissionCheck();
const access = checkModuleAccess('manufacturing', 'create');

return (
  <>
    {access.hasPermission && (
      <CreateButton onClick={handleCreate} />
    )}
  </>
);
```

### Pattern 4: Super Admin Override

```python
if not is_super_admin(current_user):
    # Regular checks
    enforce_user_org_access(current_user, org_id)
    await enforce_module_entitlement(db, org_id, module)
else:
    # Super admin must specify org
    if not org_id:
        raise HTTPException(400, "org_id required")
```

---

## Conclusion

The 3-layer security model provides comprehensive access control by combining:

1. **Tenant Isolation** - Prevents data leakage between organizations
2. **Entitlement Management** - Controls feature access based on licenses
3. **RBAC Permissions** - Enforces user-level permissions and roles

By following this architecture and using the provided constants, utilities, and patterns, you can build secure, multi-tenant applications with fine-grained access control.

For more details on specific components, refer to the code documentation in the respective files.
