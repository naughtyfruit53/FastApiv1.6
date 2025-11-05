# Pending Implementation Items

This document tracks implementation items that were not completed in the current PR but should be addressed in follow-up PRs.

## Overview

The 3-layer security system foundation has been established and testing infrastructure completed:
- ✅ Consolidated constants for backend and frontend
- ✅ Standardized utility functions for all 3 layers
- ✅ **NEW: Comprehensive integration test suite** (test_three_layer_security.py, test_user_role_flows.py)
- ✅ **NEW: Backend route updates in progress** (assets.py completed with bug fixes)
- ✅ Updated documentation

### Recent Completions (2025-11-05)

1. **Test Infrastructure** ✅
   - Created test_three_layer_security.py (500+ lines)
     - Tests each layer independently
     - Tests integrated 3-layer flows  
     - Tests role hierarchy and special cases
     - Tests error messages and edge cases
   - Created test_user_role_flows.py (500+ lines)
     - Tests admin → manager → executive workflows
     - Tests module and submodule assignments
     - Tests role transitions and cross-org scenarios
   
2. **Backend API Updates** ✅ (Partially)
   - Fixed and updated assets.py (15 endpoints)
     - Resolved critical bugs (missing org_id, missing import)
     - Applied standard 3-layer enforcement pattern
     - All CRUD + maintenance + depreciation endpoints

The following items require additional work and should be completed in subsequent PRs.

---

## 1. Backend API Route Audit and Enforcement

### Status: **In Progress** (Updated: 2025-11-05)

### Description
Comprehensive audit of all 138+ API route files to ensure consistent 3-layer enforcement.

### Completed Tasks

#### 1.1 Route Inventory and Classification ✅
- [x] Audited API routes and identified patterns
- [x] Found 819 routes already using `require_access`
- [x] Found ~15-20 routes still using old `get_current_active_user` pattern
- [x] Identified high-priority files for immediate update

#### 1.2 Apply Standard Enforcement Pattern (Partially Complete)
- [x] **Assets Module** (`app/api/v1/assets.py`) - ✅ **COMPLETED**
  - Fixed critical bug: `org_id` was used but never defined
  - Fixed missing import: `get_current_active_user` was referenced but not imported
  - Updated all 15 endpoints to use `require_access` pattern
  - Applied proper `current_user, org_id = auth` extraction
- [ ] Update remaining files: settings.py, org_user_management.py, password.py, etc.

#### 1.3 High-Priority Routes Status
- [x] **CRM** (`app/api/v1/crm.py`) - Already using `require_access` ✅
- [ ] **Manufacturing** (`app/api/v1/manufacturing.py`) - Need to audit
- [ ] **Finance/Accounting** (`app/api/v1/finance.py`, `app/api/v1/accounting.py`) - Need to audit
- [ ] **Inventory** (`app/api/v1/inventory.py`) - Need to audit
- [ ] **HR** (`app/api/v1/hr.py`) - Need to audit
- [ ] **Admin** (`app/api/v1/admin.py`) - Uses old pattern, low priority (admin functions)

#### 1.4 Module-Specific Routes Status
- [ ] Sales routes - Need to audit
- [ ] Procurement routes - Need to audit
- [x] **Asset management routes** - ✅ **COMPLETED** (app/api/v1/assets.py)
- [ ] Project management routes - Need to audit
- [ ] Voucher routes - Need to audit
- [ ] Master data routes - Need to audit

### Remaining Work
**Estimated 10-15 files** still need updates:
- admin.py, settings.py, user.py, password.py
- org_user_management.py, role_delegation.py, rbac.py
- entitlements.py, migration.py, payroll_migration.py
- financial_modeling.py, health.py, companies.py, debug.py

### Approach

```python
# Standard pattern to apply
from app.core.enforcement import require_access
from app.utils.tenant_helpers import apply_org_filter, validate_data_org_id

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

### Estimated Effort
- **Time**: 2-3 weeks
- **Priority**: High
- **Risk**: Medium (regression testing required)

---

## 2. Frontend Component and Page Updates

### Status: **Low Priority** (Deferred - Updated: 2025-11-05)

### Description
Update frontend components and pages to use standardized contexts, hooks, and utilities.

### Analysis Results

#### Current State Assessment
- **214 page components** exist in src/pages/
- **0 pages** currently use `usePermissionCheck` hook
- Most pages use individual `useAuth` and `useEntitlements` hooks
- **MegaMenu component** (956 lines) already implements comprehensive 3-layer checking
  - Uses `evalMenuItemAccess` which validates Tenant + Entitlement + RBAC
  - Already filters menu items based on all 3 layers
  - Has proper badge/tooltip system for disabled modules
  
#### Decision: LOW PRIORITY for this PR
**Reasoning:**
1. The 3-layer enforcement is **already effective at the backend API level**
2. Frontend pages will get 403 errors if they try unauthorized actions
3. MegaMenu already hides/disables menu items appropriately
4. Converting 214 pages is a massive effort with low immediate value
5. Better to do incrementally as pages are naturally updated

### Recommended Approach (Future PRs)

#### 2.1 Incremental Page Updates
- [ ] Update pages **as they are modified** for other reasons
- [ ] Focus on **new pages** using the standard pattern from the start
- [ ] Document the pattern in DEVELOPER_GUIDE_RBAC.md

#### 2.2 Priority Order (When Updating)
1. **Dashboard** pages - High visibility
2. **Settings** pages - Admin functions
3. **User management** pages - RBAC management
4. **CRM** module pages - Frequently used
5. **Manufacturing** module pages - Complex permissions
6. Other module pages as needed

#### 2.3 Low-Effort High-Value Changes
- [ ] Add wrapper component that uses `usePermissionCheck` for route-level checks
- [ ] Create HOC (Higher-Order Component) for page-level protection
- [ ] Add loading states for permission checks in new pages

### Approach

```typescript
// Standard pattern to apply
import { usePermissionCheck } from '@/hooks/usePermissionCheck';

function MyPage() {
  const { isReady, checkModuleAccess } = usePermissionCheck();

  if (!isReady) return <Loading />;

  const access = checkModuleAccess('module', 'read');
  if (!access.hasPermission) {
    return <AccessDenied reason={access.reason} />;
  }

  return <PageContent />;
}
```

### Estimated Effort
- **Time**: 2-3 weeks
- **Priority**: High
- **Risk**: Low (isolated changes)

---

## 3. MegaMenu and Navigation Updates

### Status: **Already Implemented** ✅ (Verified: 2025-11-05)

### Description
MegaMenu and navigation components already have comprehensive 3-layer enforcement implemented.

### Verified Implementation

#### 3.1 MegaMenu Component ✅
File: `frontend/src/components/MegaMenu.tsx` (956 lines)

**Already Implemented:**
- [x] Uses `useEntitlements` hook for entitlement data
- [x] Uses `useAuth` for user context
- [x] Uses `usePermissions` for RBAC checks
- [x] Implements `evalMenuItemAccess` function for 3-layer checks
  - Validates Tenant context (organizationId)
  - Validates Entitlement (module enabled/disabled/trial)
  - Validates RBAC permissions (user has permission)
- [x] Module status indicators implemented
  - Trial badge for trial modules
  - Lock icon for disabled modules
  - Tooltips explaining access denial reasons
- [x] Upgrade prompts and CTAs for disabled modules
- [x] Proper filtering of menu items based on all 3 layers

**Current Implementation:**
```typescript
// In MegaMenu.tsx (already exists)
const accessResult = evalMenuItemAccess({
  requireModule: item.requireModule,
  requireSubmodule: item.requireSubmodule,
  entitlements: entitlements,
  isAdmin: isAdminLike,
  isSuperAdmin: isSuperAdmin,
  orgId: organizationId,
});

const disabled = accessResult.result === 'disabled';
const badge = getMenuItemBadge(...);  // Shows "Trial" badge
const tooltip = getMenuItemTooltip(...);  // Shows denial reason
```

#### 3.2 Menu Access Logic ✅
File: `frontend/src/permissions/menuAccess.ts`

**Already Implemented:**
- [x] `evalMenuItemAccess()` - Complete 3-layer evaluation
- [x] Handles always-on modules (email, dashboard)
- [x] Handles RBAC-only modules (settings, admin, organization)
- [x] Handles trial modules with expiry
- [x] Handles submodule-level access control
- [x] No super admin bypass (strict enforcement)

#### 3.3 Menu Configuration ✅
File: `frontend/src/components/menuConfig.ts`

**Already Implemented:**
- [x] Centralized menu configuration
- [x] Each item has `requireModule` or `requireSubmodule`
- [x] Items have proper `permission` field for RBAC
- [x] Well-documented structure

### No Further Work Needed
The MegaMenu and navigation system is already fully implementing the 3-layer security model correctly.

---

## 4. User Management and License Components

### Status: **Not Started**

### Description
Update user management pages and license modal to integrate with new security system.

### Tasks

#### 4.1 User Management Pages
- [ ] User list with role-based filtering
- [ ] User creation with module/submodule selection
- [ ] Role assignment validation
- [ ] Manager-executive relationship management

#### 4.2 License/Entitlement Management
- [ ] License modal updates
- [ ] Entitlement status display
- [ ] Module enable/disable UI
- [ ] Trial period management
- [ ] Upgrade prompts

#### 4.3 Role-Specific Workflows
- [ ] **Admin**: Create manager with module selection
- [ ] **Manager**: Create executive with submodule selection
- [ ] **Executive**: View only, no user management

#### 4.4 Permission Synchronization UI
- [ ] Show impact of entitlement changes
- [ ] Warn about permission revocation
- [ ] Confirm bulk operations

### Code TODOs

```typescript
// User creation form
interface UserCreateFormProps {
  currentUser: User;
  availableModules: string[]; // From entitlements
  availableRoles: UserRole[]; // Based on current user's role
}

// Manager creation by admin
- Show module selection checkboxes
- Validate at least one module selected
- Save module assignments

// Executive creation by manager
- Show manager's modules only
- Show submodule checkboxes for each module
- Allow granular permission selection per submodule
```

### Estimated Effort
- **Time**: 1-2 weeks
- **Priority**: High
- **Risk**: Medium (complex UI flows)

---

## 5. Service Layer Refactoring

### Status: **Partially Complete**

### Description
Refactor service classes to use new utility functions consistently.

### Tasks

#### 5.1 Audit Existing Services
- [ ] List all service classes in `app/services/`
- [ ] Identify services without enforcement
- [ ] Document current patterns

#### 5.2 Refactor Services
- [ ] **EntitlementService**: Already updated, verify completeness
- [ ] **RBACService**: Already updated, verify completeness
- [ ] **OrganizationService**: Add consistent enforcement
- [ ] **UserService**: Add role validation
- [ ] **CRMService**: Add 3-layer checks
- [ ] **ManufacturingService**: Add 3-layer checks
- [ ] Other module services

#### 5.3 Service Method Pattern
```python
class MyModuleService:
    async def get_items(self, user: User) -> List[Model]:
        # Layer 1
        org_id = TenantHelper.ensure_org_context()
        TenantHelper.enforce_user_org_access(user, org_id)
        
        # Layer 2
        await EntitlementHelper.enforce_module_entitlement(
            self.db, org_id, "module"
        )
        
        # Layer 3
        await RBACHelper.enforce_permission(
            self.db, user, "module.read"
        )
        
        # Business logic
        stmt = apply_org_filter(select(Model), Model, user=user)
        result = await self.db.execute(stmt)
        return result.scalars().all()
```

### Estimated Effort
- **Time**: 1-2 weeks
- **Priority**: Medium
- **Risk**: Low (good test coverage)

---

## 6. Integration with Organization Creation Flow

### Status: **Not Started**

### Description
Ensure organization creation properly initializes entitlements and permissions.

### Tasks

#### 6.1 Organization Creation
- [ ] Set default entitlements on org creation
- [ ] Create default roles for new org
- [ ] Assign admin user to org
- [ ] Initialize RBAC structure

#### 6.2 License Integration
- [ ] Link license to entitlements
- [ ] Enable modules based on license tier
- [ ] Set trial periods appropriately
- [ ] Handle license upgrades/downgrades

#### 6.3 Initial User Setup
- [ ] First user is org admin
- [ ] Grant admin all permissions
- [ ] Set up default roles (manager, executive templates)

### Code TODOs

```python
# In organization creation endpoint
async def create_organization(org_data: OrgCreate):
    # Create org
    org = Organization(**org_data)
    db.add(org)
    await db.flush()
    
    # TODO: Initialize entitlements based on license
    await initialize_org_entitlements(org.id, org_data.license_tier)
    
    # TODO: Create default roles
    await create_default_roles(org.id)
    
    # TODO: Assign admin user
    await assign_org_admin(org.id, admin_user.id)
    
    await db.commit()
    return org
```

### Estimated Effort
- **Time**: 1 week
- **Priority**: High
- **Risk**: Medium (impacts new org creation)

---

## 7. Integration with User Creation Flow

### Status: **Not Started**

### Description
Ensure user creation properly handles role assignment, module selection, and inheritance.

### Tasks

#### 7.1 Role-Based User Creation
- [ ] Validate creating user can assign target role
- [ ] Enforce role hierarchy
- [ ] Validate reports_to relationships

#### 7.2 Manager Creation
- [ ] Require module selection (at least one)
- [ ] Grant full permissions for selected modules
- [ ] Set up default submodule access

#### 7.3 Executive Creation
- [ ] Require reports_to (manager)
- [ ] Show only manager's modules
- [ ] Granular submodule permission selection
- [ ] Inherit from manager's scope

### Code TODOs

```python
# In user creation endpoint
async def create_user(
    user_data: UserCreate,
    current_user: User,
    db: AsyncSession
):
    # Validate role hierarchy
    enforce_can_manage_role(current_user.role, user_data.role)
    
    # Create user
    user = User(**user_data.model_dump(exclude={'modules', 'submodule_permissions'}))
    
    if user_data.role == UserRole.MANAGER:
        # TODO: Validate and assign modules
        if not user_data.modules:
            raise HTTPException(400, "Manager must have at least one module")
        await assign_manager_modules(user.id, user_data.modules)
    
    elif user_data.role == UserRole.EXECUTIVE:
        # TODO: Validate reports_to and assign submodule permissions
        if not user_data.reports_to_id:
            raise HTTPException(400, "Executive must report to a manager")
        await assign_executive_permissions(
            user.id,
            user_data.reports_to_id,
            user_data.submodule_permissions
        )
    
    await db.commit()
    return user
```

### Estimated Effort
- **Time**: 1 week
- **Priority**: High
- **Risk**: Medium (impacts user onboarding)

---

## 8. Permission Revocation on Entitlement Change

### Status: **Design Complete, Implementation Pending**

### Description
Implement automatic permission revocation/restoration when entitlements change.

### Tasks

#### 8.1 Event System
- [ ] Create entitlement change event
- [ ] Register permission sync listener
- [ ] Handle bulk operations

#### 8.2 Permission Synchronization
- [ ] Revoke permissions when module disabled
- [ ] Grant default permissions when module enabled
- [ ] Handle trial expiry
- [ ] Handle submodule changes

#### 8.3 Permission History
- [ ] Track permission changes
- [ ] Store revocation reason
- [ ] Enable permission restoration
- [ ] Audit trail

#### 8.4 User Notification
- [ ] Notify users of permission changes
- [ ] Explain reason for revocation
- [ ] Provide upgrade options

### Code TODOs

```python
# In EntitlementService
async def update_module_status(
    self,
    org_id: int,
    module_key: str,
    new_status: ModuleStatusEnum
):
    # Update entitlement
    old_status = await self._get_module_status(org_id, module_key)
    await self._update_status(org_id, module_key, new_status)
    
    # TODO: Sync permissions
    if new_status == ModuleStatusEnum.DISABLED:
        await self._revoke_module_permissions(org_id, module_key)
    elif old_status == ModuleStatusEnum.DISABLED and new_status == ModuleStatusEnum.ENABLED:
        await self._restore_module_permissions(org_id, module_key)
    
    # TODO: Notify affected users
    await self._notify_permission_changes(org_id, module_key, new_status)
```

### Estimated Effort
- **Time**: 1-2 weeks
- **Priority**: Medium
- **Risk**: Medium (complex state management)

---

## 9. Advanced Testing

### Status: **Basic Tests Complete, Advanced Pending**

### Description
Add advanced integration and E2E tests.

### Tasks

#### 9.1 Integration Tests
- [ ] Multi-role workflows
- [ ] Org switching scenarios
- [ ] Permission inheritance
- [ ] Entitlement sync

#### 9.2 E2E Tests
- [ ] Complete user journeys
- [ ] Admin creates manager
- [ ] Manager creates executive
- [ ] Cross-module workflows
- [ ] License upgrade/downgrade

#### 9.3 Performance Tests
- [ ] Permission checking overhead
- [ ] Entitlement caching
- [ ] Query optimization
- [ ] Concurrent user scenarios

#### 9.4 Security Tests
- [ ] Attempt cross-org access
- [ ] Attempt permission escalation
- [ ] Attempt entitlement bypass
- [ ] SQL injection attempts

### Estimated Effort
- **Time**: 2 weeks
- **Priority**: Medium
- **Risk**: Low

---

## 10. Performance Optimization

### Status: **Not Started**

### Description
Optimize permission checking and enforce caching.

### Tasks

#### 10.1 Caching Strategy
- [ ] Implement Redis/memory cache for permissions
- [ ] Cache entitlement status
- [ ] Cache role hierarchy
- [ ] Implement cache invalidation

#### 10.2 Query Optimization
- [ ] Add database indexes
- [ ] Optimize tenant filters
- [ ] Batch permission checks
- [ ] Reduce N+1 queries

#### 10.3 Frontend Optimization
- [ ] Cache user permissions in React
- [ ] Prefetch entitlements
- [ ] Lazy load permission checks
- [ ] Optimize re-renders

### Code TODOs

```python
# Implement caching
from app.core.cache import cache

@cache.memoize(ttl=300)  # 5 minutes
async def get_user_permissions(user_id: int) -> List[str]:
    # Get from database
    pass

# Invalidate cache on permission change
await cache.delete(f"user_permissions:{user_id}")
```

### Estimated Effort
- **Time**: 1 week
- **Priority**: Low
- **Risk**: Medium (caching complexity)

---

## Summary

### Immediate Next Steps (PR #2)
1. Backend API route audit (high priority routes first)
2. Frontend page updates (core modules)
3. MegaMenu refactoring

### Follow-up (PR #3)
4. User management and license components
5. Service layer completion
6. Organization/user creation integration

### Future Enhancements (PR #4+)
7. Permission revocation automation
8. Advanced testing
9. Performance optimization

---

## Notes

- Each item should be a separate PR for easier review
- Prioritize based on usage and risk
- Test thoroughly at each step
- Update documentation as you go
- Consider backwards compatibility

## Questions or Concerns

If you have questions about any pending item:

1. Review this document and main RBAC_DOCUMENTATION.md
2. Check the test files for expected behavior
3. Review similar completed implementations
4. Consult with the team

---

**Last Updated**: 2025-11-05  
**Next Review**: After completing next PR
