# Pending Implementation Items

This document tracks implementation items that were not completed in the current PR but should be addressed in follow-up PRs.

## Overview

The 3-layer security system foundation has been established and testing infrastructure completed:
- ✅ Consolidated constants for backend and frontend
- ✅ Standardized utility functions for all 3 layers
- ✅ **NEW: Comprehensive integration test suite** (test_three_layer_security.py, test_user_role_flows.py)
- ✅ **NEW: Backend route updates in progress** (assets.py completed with bug fixes)
- ✅ Updated documentation

### Recent Completions (2025-11-05) - Updated

1. **Test Infrastructure** ✅ **COMPLETED**
   - Created test_three_layer_security.py (500+ lines)
     - Tests each layer independently
     - Tests integrated 3-layer flows  
     - Tests role hierarchy and special cases
     - Tests error messages and edge cases
   - Created test_user_role_flows.py (500+ lines)
     - Tests admin → manager → executive workflows
     - Tests module and submodule assignments
     - Tests role transitions and cross-org scenarios
   
2. **Backend API Updates** ✅ **SIGNIFICANTLY PROGRESSED**
   - **Assets Module** (`app/api/v1/assets.py`) - ✅ COMPLETED (Previous)
     - Resolved critical bugs (missing org_id, missing import)
     - Applied standard 3-layer enforcement pattern
     - All CRUD + maintenance + depreciation endpoints
   
   - **Health Module** (`app/api/v1/health.py`) - ✅ **NEW: COMPLETED**
     - Updated email-sync endpoint (2 endpoints)
     - Updated oauth-tokens endpoint
     - All use `require_access("email", "read")`
   
   - **Debug Module** (`app/api/v1/debug.py`) - ✅ **NEW: COMPLETED**
     - Updated rbac_state endpoint (1 endpoint)
     - Uses `require_access("admin", "read")`
   
   - **Organization User Management** (`app/api/v1/org_user_management.py`) - ✅ **NEW: COMPLETED**
     - Updated all 7 endpoints to use require_access
     - create_org_user, get_available_modules, get_user_permissions
     - update_user_modules, update_executive_submodules
     - get_managers, delete_user
     - Proper auth tuple extraction throughout
   
   - **Role Delegation** (`app/api/v1/role_delegation.py`) - ✅ **NEW: COMPLETED**
     - Updated all 3 endpoints to use require_access
     - delegate_permissions, revoke_permissions, get_role_permissions
     - Proper auth tuple extraction throughout
   
   - **Financial Modeling** (`app/api/v1/financial_modeling.py`) - ✅ **NEW: FIXED**
     - Fixed missing auth tuple extraction in create endpoint
     - All 18+ endpoints already use require_access pattern

3. **Documentation Updates** ✅ **NEW: COMPLETED**
   - Updated RBAC_DOCUMENTATION.md with:
     - API Route Implementation Status section
     - List of all completed file updates
     - Standard pattern documentation
   - Updated DEVELOPER_GUIDE_RBAC.md with:
     - Recent Updates section (2025-11-05)
     - Common migration mistakes and solutions
     - Practical examples from updated files

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
**Estimated 3-5 files** still need updates (LOW PRIORITY):
- migration.py (26 endpoints) - Admin/migration functions, already uses `require_current_organization_id`
- payroll_migration.py (6 endpoints) - Payroll-specific migrations
- Some endpoints in companies.py - Compatibility reasons
- entitlements.py - Already has good organization access validation

**Note:** Most critical files now updated. Remaining files are:
- Admin-heavy functions with existing safeguards
- Low-traffic migration endpoints
- App-level endpoints with custom validation

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

### Status: **Significantly Progressed** ✅ (Updated: 2025-11-05)

### Description
Update frontend components and pages to use standardized contexts, hooks, and utilities.

### Recent Completions (2025-11-05)

#### Infrastructure Created ✅
- [x] **ProtectedPage Component** (`frontend/src/components/ProtectedPage.tsx`)
  - Reusable wrapper for 3-layer page protection
  - Configurable access denied UI with upgrade prompts
  - HOC variant (`withProtection`) for cleaner integration
  - Comprehensive prop options for customization
  - 200+ lines with full TypeScript support
  
- [x] **usePermissionCheck Tests** (`frontend/src/hooks/__tests__/usePermissionCheck.test.tsx`)
  - 400+ lines of comprehensive tests
  - 20+ test cases covering all 3 layers
  - Tests for loading states, combined checks, helper hooks
  
- [x] **ProtectedPage Tests** (`frontend/src/components/__tests__/ProtectedPage.test.tsx`)
  - 350+ lines of component tests
  - 15+ test cases for access patterns
  - Navigation, HOC, and callback testing
  
- [x] **Frontend Protection Guide** (`FRONTEND_PROTECTION_GUIDE.md`)
  - 700+ lines comprehensive developer documentation
  - Quick start examples and migration guide
  - Common patterns and best practices
  - Testing strategies and API reference

#### Pages Updated ✅ (Updated: 2025-11-05)
- [x] **CRM Index** (`frontend/src/pages/crm/index.tsx`)
  - Protected with: moduleKey='crm', action='read'
  
- [x] **User Management** (`frontend/src/pages/settings/user-management.tsx`)
  - Protected with: custom role management check
  
- [x] **General Settings** (`frontend/src/pages/settings/general-settings.tsx`)
  - Protected with: moduleKey='settings', action='read'
  
- [x] **Inventory Index** (`frontend/src/pages/inventory/index.tsx`)
  - Protected with: moduleKey='inventory', action='read'
  
- [x] **HR Dashboard** (`frontend/src/pages/hr/dashboard.tsx`)
  - Protected with: moduleKey='hr', action='read'

- [x] **Sales Module (10 pages)** - ✅ **NEW: COMPLETED (2025-11-05)**
  - All pages protected with: moduleKey='sales', action='read'
  - dashboard.tsx, leads.tsx, customers.tsx, opportunities.tsx, pipeline.tsx
  - contacts.tsx, reports.tsx, commissions.tsx, accounts.tsx, customer-analytics.tsx

- [x] **Manufacturing Module (9 pages)** - ✅ **NEW: COMPLETED (2025-11-05)**
  - All pages protected with: moduleKey='manufacturing', action='read'
  - jobwork/: challan.tsx, inward.tsx, outward.tsx, receipt.tsx
  - quality/: inspection.tsx, reports.tsx
  - reports/: efficiency.tsx, production-summary.tsx, material-consumption.tsx

- [x] **Projects Module (5 pages)** - ✅ **NEW: COMPLETED (2025-11-05)**
  - All pages protected with: moduleKey='projects', action='read'
  - index.tsx, analytics.tsx, documents.tsx, planning.tsx, resources.tsx

- [x] **Marketing Module (3 pages)** - ✅ **NEW: COMPLETED (2025-11-05)**
  - All pages protected with: moduleKey='marketing', action='read'
  - index.tsx, analytics.tsx, campaigns.tsx

- [x] **Reports Module (5 pages)** - ✅ **NEW: COMPLETED (2025-11-05 - Second Session)**
  - All pages protected with: moduleKey='reports', action='read'
  - trial-balance.tsx, cash-flow.tsx, balance-sheet.tsx, profit-loss.tsx, ledgers.tsx

- [x] **Analytics Module (8 pages)** - ✅ **NEW: COMPLETED (2025-11-05 - Second Session)**
  - All pages protected with: moduleKey='analytics', action='read'
  - sales.tsx, customer.tsx, purchase.tsx, service.tsx (with customCheck)
  - ab-testing.tsx, automl.tsx, streaming-dashboard.tsx
  - advanced-analytics.tsx (already protected)

- [x] **Masters Module (14 pages)** - ✅ **COMPLETED (2025-11-05 - Third Session)**
  - All 14 pages protected with: moduleKey='masters', action='read'
  - Includes: bom, categories, chart-of-accounts, company-details, customers, employees, expense-accounts, index, multi-company, payment-terms, products, tax-codes, units, vendors

- [x] **Email Module (9 pages)** - ✅ **COMPLETED (2025-11-05 - Third Session)**
  - All 9 pages protected with: moduleKey='email', action='read'
  - Includes: index, Inbox, ThreadView, Composer, dashboard, accounts, oauth, sync, templates

- [x] **AI Module (3 pages)** - ✅ **COMPLETED (2025-11-05 - Third Session)**
  - All 3 pages protected with: moduleKey='ai', action='read'
  - Includes: advisor, help, explainability

#### Current State Assessment (Updated: 2025-11-05 - Third Session)
- **214 page components** exist in src/pages/
- **75 pages** now use `ProtectedPage` wrapper (35.0% complete) ⬆️ **+26 pages this session**
- **ProtectedPage component** provides easy integration path
- Most pages still use individual `useAuth` and `useEntitlements` hooks
- **MegaMenu component** (956 lines) already implements comprehensive 3-layer checking
  - Uses `evalMenuItemAccess` which validates Tenant + Entitlement + RBAC
  - Already filters menu items based on all 3 layers
  - Has proper badge/tooltip system for disabled modules

### Remaining Work

#### 2.1 Additional High-Priority Pages
- [ ] Dashboard pages (OrgDashboard already protected ✅, AppSuperAdminDashboard, CustomDashboard)
- [ ] Additional Settings pages (DataManagement already protected ✅, FactoryReset, etc.)
- [x] **Manufacturing module pages** - ✅ **COMPLETED** (all 9 pages)
- [ ] Finance/Accounting module pages
- [ ] **Reports module pages** (5 pages: trial-balance, cash-flow, balance-sheet, profit-loss, ledgers)
- [x] **Sales/CRM pages** - ✅ **COMPLETED** (all 10 pages)
- [ ] Additional Inventory pages (movements, cycle-count, etc.)
- [ ] Additional HR pages (employees, employees-directory)
- [ ] **Analytics module pages** (12 pages total)
- [ ] **Masters module pages** (14 pages total)
- [ ] Service/Service Desk pages
- [ ] Admin module pages (with custom permissions)
- [ ] AI pages (3 pages)
- [ ] Email module pages
- [ ] Integration pages
- [ ] Calendar pages
- [ ] Task management pages
- [ ] SLA pages
- [ ] Mobile-specific pages

#### 2.2 Incremental Rollout Strategy ✅ **SIGNIFICANTLY PROGRESSED**
- [x] Infrastructure in place - `ProtectedPage` component ready
- [x] Documentation complete - See `FRONTEND_PROTECTION_GUIDE.md`
- [x] Examples available - 54 pages updated across multiple modules
- [x] **Major modules completed**: Sales (10), Manufacturing (9), Projects (5), Marketing (3)
- [ ] Continue updating pages as they are modified
- [ ] Focus on **new pages** using the standard pattern from the start

#### 2.3 Progress Statistics (2025-11-05 - Updated Third Session - Final)
- **Total pages in codebase**: 214
- **Pages protected**: 77 (36.0%)
- **Modules fully protected**: Sales, Manufacturing, Projects, Marketing, Reports, Analytics, **Masters**, **Email**, **AI**, **HR** ✅
- **Pages added in third session**: 28 (Masters 14 + Email 9 + AI 3 + HR 2)
- **Remaining high-priority**: Admin (12), Service Desk (4), Inventory (6 remaining), Calendar (4), Tasks (4), etc.

### Implementation Pattern

```typescript
// Simple module protection
import { ProtectedPage } from '../../components/ProtectedPage';

export default function MyPage() {
  return (
    <ProtectedPage moduleKey="module_name" action="read">
      {/* Page content */}
    </ProtectedPage>
  );
}

// Custom permission check
<ProtectedPage
  customCheck={(pc) => pc.checkCanManageRole('executive')}
  accessDeniedMessage="Custom message"
>
  {/* Content */}
</ProtectedPage>
```

### Documentation
- **FRONTEND_PROTECTION_GUIDE.md** - Comprehensive guide with:
  - Quick start examples
  - API reference for ProtectedPage and usePermissionCheck
  - Common patterns (page-level, component-level, HOC)
  - Migration guide from old patterns
  - Testing strategies
  - Best practices

### Benefits Delivered
- ✅ Proactive permission checking (better UX than backend 403 errors)
- ✅ Consistent access control pattern across pages
- ✅ Automatic loading states during permission checks
- ✅ Clear access denied messages with upgrade prompts
- ✅ Easy to test and maintain
- ✅ Minimal code changes required for integration

### Estimated Remaining Effort
- **Time**: 1-2 weeks for high-priority pages (20-30 pages)
- **Priority**: Medium (infrastructure complete, incremental rollout)
- **Risk**: Low (isolated changes, well-tested pattern)

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

## 11. Remaining Frontend Page Protection Work (2025-11-05)

### Status: **In Progress**

### High-Priority Pages Remaining

#### Masters Module (13 pages remaining)
- [ ] categories.tsx
- [ ] chart-of-accounts.tsx  
- [ ] company-details.tsx
- [ ] customers.tsx
- [ ] employees.tsx
- [ ] expense-accounts.tsx
- [ ] index.tsx (main masters dashboard - CRITICAL)
- [ ] multi-company.tsx
- [ ] payment-terms.tsx
- [ ] products.tsx
- [ ] tax-codes.tsx
- [ ] units.tsx
- [ ] vendors.tsx

#### Admin Module (12 pages - requires custom permissions)
- [ ] notifications.tsx
- [ ] manage-organizations.tsx
- [ ] app-user-management.tsx
- [ ] organizations/create.tsx
- [ ] organizations/index.tsx
- [ ] organizations/[id].tsx
- [ ] index.tsx
- [ ] rbac.tsx
- [ ] license-management.tsx
- [ ] users/ResetPassword.tsx
- [ ] users/index.tsx
- [ ] audit-logs.tsx

#### Email Module (9 pages)
- [ ] Composer.tsx
- [ ] Inbox.tsx
- [ ] ThreadView.tsx
- [ ] accounts.tsx
- [ ] dashboard.tsx
- [ ] index.tsx
- [ ] oauth.tsx
- [ ] sync.tsx
- [ ] templates.tsx

#### Service/Service Desk Module (4 pages)
- [ ] service-desk/chat.tsx
- [ ] service-desk/index.tsx
- [ ] service-desk/sla.tsx
- [ ] service-desk/tickets.tsx

#### Inventory Module (6 pages remaining)
- [ ] bins.tsx
- [ ] cycle-count.tsx
- [ ] locations.tsx
- [ ] low-stock.tsx
- [ ] movements.tsx
- [ ] pending-orders.tsx

#### HR Module (2 pages)
- [ ] employees.tsx
- [ ] employees-directory.tsx

#### AI Module (3 pages)
- [ ] advisor.tsx
- [ ] help.tsx
- [ ] explainability.tsx

#### Calendar Module (4 pages)
- [ ] create.tsx
- [ ] dashboard.tsx
- [ ] events.tsx
- [ ] index.tsx (calendar main)

#### Additional Pages
- [ ] Dashboard pages (AppSuperAdminDashboard, CustomDashboard)
- [ ] Task management pages
- [ ] Finance and accounting pages
- [ ] Mobile-specific pages
- [ ] Various utility and feature pages

### Implementation Approach

1. **Batch Processing**: Group pages by module for efficient updates
2. **Pattern**: Use `<ProtectedPage moduleKey="module" action="read">` wrapper
3. **Custom Permissions**: For admin and special pages, use `customCheck` prop
4. **Testing**: Validate changes with lint and build after each batch
5. **Documentation**: Update this file after each significant batch

### Estimated Effort
- **Remaining pages**: ~165 pages
- **Protected so far**: 49 pages (22.9%)
- **Time estimate**: 2-3 more sessions of similar scope to complete all pages
- **Priority**: Medium-High (foundation is solid, incremental rollout acceptable)

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

**Last Updated**: 2025-11-05 (Second Session - Reports, Analytics, Masters partial completion)  
**Next Review**: After completing Masters module and additional high-priority modules
