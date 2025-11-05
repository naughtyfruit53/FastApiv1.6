# Pending Implementation Items

This document tracks implementation items that were not completed in the current PR but should be addressed in follow-up PRs.

## Overview

The current PR focuses on establishing the foundation of the 3-layer security system:
- ✅ Consolidated constants for backend and frontend
- ✅ Standardized utility functions for all 3 layers
- ✅ Comprehensive test suite
- ✅ Updated documentation

The following items require additional work and should be completed in subsequent PRs.

---

## 1. Backend API Route Audit and Enforcement

### Status: **Not Started**

### Description
Comprehensive audit of all 138+ API route files to ensure consistent 3-layer enforcement.

### Tasks

#### 1.1 Route Inventory and Classification
- [ ] Create inventory of all API routes
- [ ] Classify routes by module
- [ ] Identify routes without enforcement
- [ ] Prioritize critical routes

#### 1.2 Apply Standard Enforcement Pattern
- [ ] Replace custom auth with `require_access`
- [ ] Add tenant filtering with `apply_org_filter`
- [ ] Validate org_id in create/update operations
- [ ] Check record ownership in update/delete operations

#### 1.3 High-Priority Routes
Focus on these modules first:
- [ ] **CRM** (`app/api/v1/crm.py`)
- [ ] **Manufacturing** (`app/api/v1/manufacturing.py`)
- [ ] **Finance/Accounting** (`app/api/v1/finance.py`, `app/api/v1/accounting.py`)
- [ ] **Inventory** (`app/api/v1/inventory.py`)
- [ ] **HR** (`app/api/v1/hr.py`)
- [ ] **Admin** (`app/api/v1/admin.py`)

#### 1.4 Module-Specific Routes
- [ ] Sales routes
- [ ] Procurement routes
- [ ] Asset management routes
- [ ] Project management routes
- [ ] Voucher routes
- [ ] Master data routes

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

### Status: **Not Started**

### Description
Update all frontend components and pages to use standardized contexts, hooks, and utilities.

### Tasks

#### 2.1 Context Usage Audit
- [ ] Audit all components using AuthContext
- [ ] Audit all components using OrganizationContext
- [ ] Identify components with direct API calls
- [ ] Identify components with ad-hoc permission checks

#### 2.2 Standardize Permission Checking
- [ ] Replace ad-hoc checks with `usePermissionCheck`
- [ ] Use `checkModuleAccess` for route protection
- [ ] Use `checkPermission` for feature flags
- [ ] Add loading states for permission checks

#### 2.3 High-Priority Components
- [ ] **Dashboard** pages
- [ ] **CRM** module pages
- [ ] **Manufacturing** module pages
- [ ] **Settings** pages
- [ ] **User management** pages
- [ ] **Admin** pages

#### 2.4 Forms and CRUD Components
- [ ] Add entitlement checks to create forms
- [ ] Add permission checks to edit forms
- [ ] Add confirmation for delete operations
- [ ] Show appropriate error messages

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

### Status: **Not Started**

### Description
Update MegaMenu, SidebarMenu, and navigation components for consistent entitlement and permission enforcement.

### Tasks

#### 3.1 MegaMenu Component
File: `frontend/src/components/MegaMenu.tsx` (956 lines)

- [ ] Audit current entitlement/permission logic
- [ ] Replace with `usePermissionCheck` hook
- [ ] Use `filterMenuItems` utility
- [ ] Add module status indicators (trial, disabled)
- [ ] Handle entitlement upgrade prompts

#### 3.2 SidebarMenu (if exists)
- [ ] Apply same pattern as MegaMenu
- [ ] Ensure consistency between menus

#### 3.3 Navigation Guards
- [ ] Add route guards for protected pages
- [ ] Redirect unauthorized users appropriately
- [ ] Show loading states during checks

#### 3.4 Menu Configuration
- [ ] Centralize menu configuration
- [ ] Add moduleKey and permission to all items
- [ ] Document menu structure

### Approach

```typescript
// MegaMenu pattern
import { usePermissionCheck } from '@/hooks/usePermissionCheck';
import { filterMenuItems } from '@/utils/permissionHelpers';

function MegaMenu() {
  const { userPermissions, entitlements } = usePermissionCheck();

  const menuItems = [
    { label: 'CRM', moduleKey: 'crm', permission: 'crm.read', ... },
    { label: 'Manufacturing', moduleKey: 'manufacturing', permission: 'manufacturing.read', ... },
  ];

  const filteredItems = filterMenuItems(
    menuItems,
    userPermissions,
    entitlements
  );

  return (
    <nav>
      {filteredItems.map(item => (
        <MenuItem key={item.moduleKey} {...item} />
      ))}
    </nav>
  );
}
```

### Estimated Effort
- **Time**: 1 week
- **Priority**: High
- **Risk**: Medium (central navigation component)

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
