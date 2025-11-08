# Developer Guide: 3-Layer Security System

## Quick Start

This guide helps developers quickly implement the 3-layer security model (Tenant, Entitlement, RBAC) in new and existing code.

## Table of Contents

1. [Quick Reference](#quick-reference)
2. [Backend Development](#backend-development)
3. [Frontend Development](#frontend-development)
4. [Common Tasks](#common-tasks)
5. [Troubleshooting](#troubleshooting)
6. [Migration Guide](#migration-guide)

---

## Quick Reference

### Backend Imports

```python
# Constants
from app.core.constants import (
    UserRole, ModuleStatusEnum, SUPER_ADMIN_BYPASS_ROLES,
    ORG_ADMIN_ROLES, ALWAYS_ON_MODULES, RBAC_ONLY_MODULES
)

# Tenant (Layer 1)
from app.utils.tenant_helpers import (
    enforce_user_org_access, validate_data_org_id,
    apply_org_filter, validate_record_org_access
)

# Entitlement (Layer 2)
from app.utils.entitlement_helpers import (
    enforce_module_entitlement, check_module_entitlement,
    is_always_on_module, is_rbac_only_module
)

# RBAC (Layer 3)
from app.utils.rbac_helpers import (
    enforce_permission, has_permission,
    is_super_admin, is_org_admin, can_manage_role
)

# Combined enforcement
from app.core.enforcement import require_access
```

### Frontend Imports

```typescript
// Constants
import {
  UserRole, ModuleStatus, ALWAYS_ON_MODULES,
  RBAC_ONLY_MODULES, PERMISSION_PATTERNS
} from '@/constants/rbac';

// Permission helpers
import {
  hasPermission, canAccessModule, isModuleEntitled,
  isSuperAdmin, isOrgAdmin, canManageRole
} from '@/utils/permissionHelpers';

// Permission check hook
import { usePermissionCheck } from '@/hooks/usePermissionCheck';

// Contexts
import { useAuth } from '@/context/AuthContext';
import { useOrganization } from '@/context/OrganizationContext';
```

---

## Backend Development

### 1. Creating a New API Endpoint

#### Option A: Use `require_access` Decorator (Recommended)

This automatically handles both entitlement and RBAC checks:

```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.enforcement import require_access
from app.utils.tenant_helpers import apply_org_filter
from app.models.crm_models import Lead

router = APIRouter()

@router.get("/leads")
async def get_leads(
    # Automatically checks entitlement + permission
    auth: tuple = Depends(require_access("crm", "read")),
    db: AsyncSession = Depends(get_db)
):
    current_user, org_id = auth
    
    # Apply tenant filter
    stmt = select(Lead)
    stmt = apply_org_filter(stmt, Lead, user=current_user)
    
    result = await db.execute(stmt)
    return result.scalars().all()
```

#### Option B: Manual Layer Checks

For more control, check each layer manually:

```python
from app.utils.tenant_helpers import enforce_user_org_access
from app.utils.entitlement_helpers import enforce_module_entitlement
from app.utils.rbac_helpers import enforce_permission

@router.get("/leads")
async def get_leads(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Layer 1: Tenant
    org_id = TenantHelper.ensure_org_context()
    enforce_user_org_access(current_user, org_id)
    
    # Layer 2: Entitlement
    await enforce_module_entitlement(db, org_id, "crm")
    
    # Layer 3: RBAC
    await enforce_permission(db, current_user, "crm.read")
    
    # Query with filter
    stmt = apply_org_filter(select(Lead), Lead, user=current_user)
    result = await db.execute(stmt)
    return result.scalars().all()
```

### 2. Creating a New Resource

```python
from app.utils.tenant_helpers import validate_data_org_id
from app.schemas.crm import LeadCreate

@router.post("/leads")
async def create_lead(
    data: LeadCreate,
    auth: tuple = Depends(require_access("crm", "create")),
    db: AsyncSession = Depends(get_db)
):
    current_user, org_id = auth
    
    # Validate and set org_id
    validated_data = validate_data_org_id(
        data.model_dump(),
        current_user
    )
    
    lead = Lead(**validated_data)
    db.add(lead)
    await db.commit()
    await db.refresh(lead)
    
    return lead
```

### 3. Updating a Resource

```python
from app.utils.tenant_helpers import validate_record_org_access

@router.put("/leads/{lead_id}")
async def update_lead(
    lead_id: int,
    data: LeadUpdate,
    auth: tuple = Depends(require_access("crm", "update")),
    db: AsyncSession = Depends(get_db)
):
    current_user, org_id = auth
    
    # Get existing record
    result = await db.execute(
        select(Lead).where(Lead.id == lead_id)
    )
    lead = result.scalar_one_or_none()
    
    if not lead:
        raise HTTPException(404, "Lead not found")
    
    # Validate tenant access
    validate_record_org_access(lead, org_id)
    
    # Update
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(lead, key, value)
    
    await db.commit()
    return lead
```

### 4. Deleting a Resource

```python
@router.delete("/leads/{lead_id}")
async def delete_lead(
    lead_id: int,
    auth: tuple = Depends(require_access("crm", "delete")),
    db: AsyncSession = Depends(get_db)
):
    current_user, org_id = auth
    
    result = await db.execute(
        select(Lead).where(Lead.id == lead_id)
    )
    lead = result.scalar_one_or_none()
    
    if not lead:
        raise HTTPException(404, "Lead not found")
    
    validate_record_org_access(lead, org_id)
    
    await db.delete(lead)
    await db.commit()
    
    return {"message": "Lead deleted"}
```

### 5. Creating a Service Class

```python
from app.utils.tenant_helpers import TenantHelper, apply_org_filter
from app.utils.entitlement_helpers import EntitlementHelper
from app.utils.rbac_helpers import RBACHelper

class LeadService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_leads(
        self,
        user: User,
        filters: Optional[Dict] = None
    ) -> List[Lead]:
        """Get leads with full 3-layer enforcement"""
        
        # Layer 1: Tenant
        org_id = TenantHelper.ensure_org_context()
        TenantHelper.enforce_user_org_access(user, org_id)
        
        # Layer 2: Entitlement
        await EntitlementHelper.enforce_module_entitlement(
            self.db, org_id, "crm"
        )
        
        # Layer 3: RBAC
        await RBACHelper.enforce_permission(
            self.db, user, "crm.read"
        )
        
        # Build query
        stmt = select(Lead)
        stmt = apply_org_filter(stmt, Lead, user=user)
        
        # Apply filters if provided
        if filters:
            if "status" in filters:
                stmt = stmt.where(Lead.status == filters["status"])
        
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def create_lead(
        self,
        user: User,
        data: Dict
    ) -> Lead:
        """Create lead with validation"""
        
        # Validate org_id
        validated_data = TenantHelper.validate_data_org_id(data, user)
        
        # Additional validations...
        
        lead = Lead(**validated_data)
        self.db.add(lead)
        await self.db.commit()
        await self.db.refresh(lead)
        
        return lead
```

### 6. Role-Based Logic

```python
from app.utils.rbac_helpers import is_super_admin, is_org_admin

@router.get("/leads")
async def get_leads(
    auth: tuple = Depends(require_access("crm", "read")),
    db: AsyncSession = Depends(get_db)
):
    current_user, org_id = auth
    
    stmt = select(Lead)
    stmt = apply_org_filter(stmt, Lead, user=current_user)
    
    # Role-based filtering
    if not (is_super_admin(current_user) or is_org_admin(current_user)):
        # Regular users see only their own leads
        stmt = stmt.where(
            or_(
                Lead.assigned_to_id == current_user.id,
                Lead.created_by_id == current_user.id
            )
        )
    
    result = await db.execute(stmt)
    return result.scalars().all()
```

---

## Frontend Development

### 1. Page Component with Access Check

```typescript
import React from 'react';
import { usePermissionCheck } from '@/hooks/usePermissionCheck';
import { useRouter } from 'next/router';

export default function LeadsPage() {
  const router = useRouter();
  const {
    isReady,
    checkModuleAccess,
  } = usePermissionCheck();

  if (!isReady) {
    return <div>Loading...</div>;
  }

  // Check full access
  const access = checkModuleAccess('crm', 'read');
  
  if (!access.hasPermission) {
    return (
      <div>
        <h1>Access Denied</h1>
        <p>{access.reason}</p>
        <button onClick={() => router.push('/dashboard')}>
          Go to Dashboard
        </button>
      </div>
    );
  }

  return (
    <div>
      <h1>Leads</h1>
      {/* Your component content */}
    </div>
  );
}
```

### 2. Conditional Button Rendering

```typescript
import { usePermissionCheck } from '@/hooks/usePermissionCheck';

function LeadActions({ leadId }: { leadId: number }) {
  const { checkPermission } = usePermissionCheck();

  const canEdit = checkPermission('crm.update');
  const canDelete = checkPermission('crm.delete');

  return (
    <div>
      {canEdit && (
        <button onClick={() => handleEdit(leadId)}>
          Edit
        </button>
      )}
      {canDelete && (
        <button onClick={() => handleDelete(leadId)}>
          Delete
        </button>
      )}
    </div>
  );
}
```

### 3. Menu with Access-Based Filtering

```typescript
import { usePermissionCheck } from '@/hooks/usePermissionCheck';

function NavigationMenu() {
  const {
    checkModuleAccess,
    checkPermission,
  } = usePermissionCheck();

  const menuItems = [
    {
      label: 'Dashboard',
      path: '/dashboard',
      check: () => true, // Always accessible
    },
    {
      label: 'CRM',
      path: '/crm',
      check: () => checkModuleAccess('crm', 'read').hasPermission,
    },
    {
      label: 'Manufacturing',
      path: '/manufacturing',
      check: () => checkModuleAccess('manufacturing', 'read').hasPermission,
    },
    {
      label: 'Settings',
      path: '/settings',
      check: () => checkPermission('settings.view'),
    },
  ];

  const visibleItems = menuItems.filter(item => item.check());

  return (
    <nav>
      {visibleItems.map(item => (
        <a key={item.path} href={item.path}>
          {item.label}
        </a>
      ))}
    </nav>
  );
}
```

### 4. Using Individual Hooks

```typescript
import { useHasPermission, useHasModuleAccess } from '@/hooks/usePermissionCheck';

function MyComponent() {
  // Simple boolean checks
  const canCreate = useHasPermission('crm.create');
  const hasManufacturingAccess = useHasModuleAccess('manufacturing', 'read');

  return (
    <div>
      {canCreate && <CreateButton />}
      {hasManufacturingAccess && <ManufacturingLink />}
    </div>
  );
}
```

### 5. Role-Based Rendering

```typescript
import { usePermissionCheck } from '@/hooks/usePermissionCheck';

function UserManagement() {
  const {
    checkIsSuperAdmin,
    checkIsOrgAdmin,
    checkCanManageRole,
  } = usePermissionCheck();

  const isSuperAdmin = checkIsSuperAdmin();
  const isOrgAdmin = checkIsOrgAdmin();
  const canManageManagers = checkCanManageRole('manager');

  return (
    <div>
      {isSuperAdmin && (
        <section>
          <h2>Super Admin Controls</h2>
          <CreateOrganizationButton />
        </section>
      )}
      
      {isOrgAdmin && (
        <section>
          <h2>Organization Management</h2>
          <ManageUsersButton />
        </section>
      )}
      
      {canManageManagers && (
        <section>
          <h2>Manager Assignment</h2>
          <AssignManagerButton />
        </section>
      )}
    </div>
  );
}
```

### 6. Entitlement Status Display

```typescript
import { usePermissionCheck } from '@/hooks/usePermissionCheck';
import { ModuleStatus } from '@/constants/rbac';

function ModuleCard({ moduleKey }: { moduleKey: string }) {
  const {
    getModuleEntitlementStatus,
    checkModuleEntitled,
  } = usePermissionCheck();

  const status = getModuleEntitlementStatus(moduleKey);
  const isEntitled = checkModuleEntitled(moduleKey);

  return (
    <div className={`module-card ${status}`}>
      <h3>{moduleKey}</h3>
      <span className="status-badge">
        {status === ModuleStatus.TRIAL && '🔄 Trial'}
        {status === ModuleStatus.ENABLED && '✅ Enabled'}
        {status === ModuleStatus.DISABLED && '❌ Disabled'}
      </span>
      {!isEntitled && (
        <button onClick={() => requestAccess(moduleKey)}>
          Request Access
        </button>
      )}
    </div>
  );
}
```

---

## Common Tasks

### Task 1: Add a New Module

1. **Add to Constants (Backend)**

```python
# app/core/constants.py
class CoreModule(str, Enum):
    # ... existing modules
    NEW_MODULE = "new_module"
```

2. **Add to Constants (Frontend)**

```typescript
// src/constants/rbac.ts
export enum CoreModule {
  // ... existing modules
  NEW_MODULE = 'new_module',
}
```

3. **Add to Module Registry**

```python
# app/core/modules_registry.py
class ModuleName(str, Enum):
    # ... existing modules
    NEW_MODULE = "new_module"

MODULE_SUBMODULES = {
    # ... existing mappings
    "new_module": [
        "submodule1",
        "submodule2",
    ]
}
```

4. **Create API Router**

```python
# app/api/v1/new_module.py
router = APIRouter(prefix="/new_module", tags=["New Module"])

@router.get("/items")
async def get_items(
    auth: tuple = Depends(require_access("new_module", "read")),
    db: AsyncSession = Depends(get_db)
):
    # Implementation
    pass
```

### Task 2: Add a New Permission

1. **Define Permission Constant**

```python
# In your router or service
PERMISSION_NEW_ACTION = "module.new_action"
```

2. **Use in Enforcement**

```python
@router.post("/special-action")
async def special_action(
    auth: tuple = Depends(require_access("module", "new_action")),
    db: AsyncSession = Depends(get_db)
):
    # Implementation
    pass
```

3. **Seed Permission in Database**

Create a migration or seed script to add the permission to the database.

### Task 3: Create a New Role

1. **Add Role to Constants**

```python
# app/core/constants.py
class UserRole(str, Enum):
    # ... existing roles
    NEW_ROLE = "new_role"

ROLE_HIERARCHY = {
    # ... existing roles
    UserRole.NEW_ROLE: 40,  # Set appropriate level
}
```

2. **Configure Permissions**

Define what permissions this role should have by default.

### Task 4: Migrate Existing Endpoint

**Before:**
```python
@router.get("/leads")
async def get_leads(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # No enforcement
    result = await db.execute(select(Lead))
    return result.scalars().all()
```

**After:**
```python
from app.core.enforcement import require_access
from app.utils.tenant_helpers import apply_org_filter

@router.get("/leads")
async def get_leads(
    auth: tuple = Depends(require_access("crm", "read")),
    db: AsyncSession = Depends(get_db)
):
    current_user, org_id = auth
    
    stmt = select(Lead)
    stmt = apply_org_filter(stmt, Lead, user=current_user)
    
    result = await db.execute(stmt)
    return result.scalars().all()
```

---

## Troubleshooting

### Problem: "Organization context is required"

**Cause**: No org_id in request context

**Solution**:
- Ensure `X-Organization-ID` header is sent
- Check TenantMiddleware is registered
- Verify user has organization_id set

### Problem: "Module not enabled for your organization"

**Cause**: Entitlement check failed

**Solution**:
- Check org entitlements in database
- Verify module is not in trial period that expired
- Check if module should be in ALWAYS_ON_MODULES

### Problem: "You do not have permission for this action"

**Cause**: RBAC check failed

**Solution**:
- Check user's assigned roles and permissions
- Verify permission exists in database
- Check if user's role has the required permission

### Problem: "Access denied: Resource does not belong to your organization"

**Cause**: Tenant isolation violation

**Solution**:
- Verify user is accessing resources from their own org
- Check if resource's org_id matches user's org_id
- Ensure super admin specifies correct org_id

---

## Migration Guide

### Recent Updates (2025-11-05)

The following files were recently updated to use the standard `require_access` pattern:

#### Updated Files

1. **health.py** - Health check endpoints
   ```python
   # Before
   current_user: User = Depends(get_current_active_user)
   organization_id = current_user.organization_id
   
   # After
   auth: tuple = Depends(require_access("email", "read"))
   current_user, organization_id = auth
   ```

2. **debug.py** - Debug endpoints
   ```python
   # After
   auth: tuple = Depends(require_access("admin", "read"))
   current_user, org_id = auth
   ```

3. **org_user_management.py** - User management (7 endpoints)
   ```python
   # After
   auth: tuple = Depends(require_access("user", "create"))
   current_user, org_id = auth
   ```

4. **role_delegation.py** - Role delegation (3 endpoints)
   ```python
   # After
   auth: tuple = Depends(require_access("admin", "create"))
   current_user, organization_id = auth
   ```

5. **financial_modeling.py** - Fixed auth extraction
   ```python
   # Added missing line
   current_user, org_id = auth
   ```

### Migrating Old Code

1. **Identify unprotected endpoints**
   
   Search for routes without `require_access`:
   ```bash
   grep -r "@router" app/api/v1/ | grep -v "require_access"
   ```

2. **Add enforcement**
   
   Replace old auth with `require_access`:
   ```python
   # Old
   current_user: User = Depends(get_current_active_user)
   
   # New
   auth: tuple = Depends(require_access("module", "action"))
   current_user, org_id = auth  # Don't forget to extract!
   ```

3. **Add tenant filtering**
   
   Add org filter to queries:
   ```python
   stmt = apply_org_filter(stmt, Model, user=current_user)
   ```

4. **Test thoroughly**
   
   Test with different roles and organizations.

### Common Migration Mistakes

❌ **Forgetting to extract auth tuple**
```python
auth: tuple = Depends(require_access("module", "read"))
# Missing: current_user, org_id = auth
# This will cause errors when accessing current_user or org_id
```

✅ **Correct pattern**
```python
auth: tuple = Depends(require_access("module", "read"))
current_user, org_id = auth  # Always extract!
```

❌ **Using organization_id from user instead of auth**
```python
auth: tuple = Depends(require_access("module", "read"))
current_user, org_id = auth
organization_id = current_user.organization_id  # Don't do this!
```

✅ **Use org_id from auth**
```python
auth: tuple = Depends(require_access("module", "read"))
current_user, org_id = auth
# Use org_id directly - it's already validated
```

---

## Best Practices Checklist

### Backend

- [ ] Use `require_access` for all protected endpoints
- [ ] Apply `apply_org_filter` to all queries
- [ ] Validate org_id for creates/updates with `validate_data_org_id`
- [ ] Check record ownership with `validate_record_org_access`
- [ ] Use constants from `app/core/constants.py`
- [ ] Log security events
- [ ] Write tests for new endpoints

### Frontend

- [ ] Use `usePermissionCheck` hook
- [ ] Check access before rendering sensitive UI
- [ ] Show appropriate error messages
- [ ] Use constants from `src/constants/rbac.ts`
- [ ] Filter menus based on access
- [ ] Handle loading and error states
- [ ] Write component tests

---

## Additional Resources

- **Full Documentation**: See `RBAC_DOCUMENTATION.md`
- **Test Examples**: See `app/tests/test_three_layer_security.py`
- **Code Examples**: See existing endpoints in `app/api/v1/`

---

## Getting Help

If you encounter issues:

1. Check error messages and logs
2. Review this guide and main documentation
3. Look at existing implementations
4. Review test cases for patterns
5. Ask the team for guidance

Remember: **All three layers must pass for access to be granted!**
