# Frontend Protection Implementation Guide

## Overview

This guide explains how to implement 3-layer security (Tenant Isolation + Entitlement + RBAC) in frontend pages using the `ProtectedPage` component and `usePermissionCheck` hook.

## Table of Contents

1. [Quick Start](#quick-start)
2. [ProtectedPage Component](#protectedpage-component)
3. [usePermissionCheck Hook](#usepermissioncheck-hook)
4. [Common Patterns](#common-patterns)
5. [Migration Guide](#migration-guide)
6. [Testing](#testing)
7. [Best Practices](#best-practices)

---

## Quick Start

### Basic Module Protection

The simplest way to protect a page is to wrap it with `ProtectedPage`:

```tsx
// pages/crm/index.tsx
import { ProtectedPage } from '../../components/ProtectedPage';

export default function CRMDashboard() {
  return (
    <ProtectedPage moduleKey="crm" action="read">
      <div>
        {/* Your CRM dashboard content */}
      </div>
    </ProtectedPage>
  );
}
```

This ensures:
- ✅ User has valid organization context (Layer 1: Tenant)
- ✅ Organization has CRM module enabled (Layer 2: Entitlement)
- ✅ User has 'crm.read' permission (Layer 3: RBAC)

---

## ProtectedPage Component

### Props

| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `moduleKey` | string | No* | - | Module to check (e.g., 'crm', 'inventory') |
| `submoduleKey` | string | No | - | Submodule to check (requires moduleKey) |
| `action` | string | No | 'read' | Action to check ('read', 'write', 'delete') |
| `customCheck` | function | No | - | Custom permission check function |
| `accessDeniedMessage` | string | No | - | Custom access denied message |
| `showUpgradePrompt` | boolean | No | true | Show upgrade prompt for disabled modules |
| `onAccessDenied` | function | No | - | Callback when access is denied |
| `redirectOnDenied` | boolean | No | false | Redirect to dashboard on access denial |
| `loadingComponent` | ReactNode | No | - | Custom loading component |
| `accessDeniedComponent` | ReactNode | No | - | Custom access denied component |

*Either `moduleKey` or `customCheck` is required.

### Examples

#### 1. Module-Level Protection

```tsx
// Protect entire module
<ProtectedPage moduleKey="inventory" action="read">
  <InventoryDashboard />
</ProtectedPage>
```

#### 2. Submodule-Level Protection

```tsx
// Protect specific submodule
<ProtectedPage 
  moduleKey="crm" 
  submoduleKey="leads" 
  action="write"
>
  <LeadForm />
</ProtectedPage>
```

#### 3. Custom Permission Check

```tsx
// Custom role-based check
<ProtectedPage
  customCheck={(pc) => pc.checkIsSuperAdmin()}
  accessDeniedMessage="Only super admins can access this page"
>
  <AdminPanel />
</ProtectedPage>
```

#### 4. User Management Protection

```tsx
// Check role management capability
<ProtectedPage
  moduleKey="settings"
  customCheck={(pc) => pc.checkCanManageRole('executive')}
  accessDeniedMessage="You do not have permission to manage users"
>
  <UserManagement />
</ProtectedPage>
```

#### 5. Custom Access Denied UI

```tsx
<ProtectedPage
  moduleKey="finance"
  action="read"
  accessDeniedComponent={
    <Box>
      <Typography variant="h4">Finance Module Required</Typography>
      <Button onClick={handleUpgrade}>Upgrade Plan</Button>
    </Box>
  }
>
  <FinanceDashboard />
</ProtectedPage>
```

#### 6. Auto-Redirect on Denial

```tsx
// Redirect to dashboard if access denied
<ProtectedPage
  moduleKey="manufacturing"
  action="read"
  redirectOnDenied={true}
>
  <ManufacturingDashboard />
</ProtectedPage>
```

#### 7. Access Denial Callback

```tsx
function MyPage() {
  const handleAccessDenied = (reason: string) => {
    console.log('Access denied:', reason);
    // Track analytics, show toast, etc.
  };

  return (
    <ProtectedPage
      moduleKey="reports"
      action="read"
      onAccessDenied={handleAccessDenied}
    >
      <ReportsPage />
    </ProtectedPage>
  );
}
```

---

## usePermissionCheck Hook

For more granular control, use the `usePermissionCheck` hook directly:

### Basic Usage

```tsx
import { usePermissionCheck } from '../hooks/usePermissionCheck';

function MyComponent() {
  const {
    isReady,
    checkModuleAccess,
    checkPermission,
    checkIsSuperAdmin,
  } = usePermissionCheck();

  if (!isReady) {
    return <Loading />;
  }

  const crmAccess = checkModuleAccess('crm', 'read');
  if (!crmAccess.hasPermission) {
    return <AccessDenied reason={crmAccess.reason} />;
  }

  return <div>Content</div>;
}
```

### API Reference

#### State Properties

- `isLoading: boolean` - Whether permission data is still loading
- `isReady: boolean` - Whether all checks can be performed
- `user: User | null` - Current user object
- `organizationId: number | null` - Current organization ID
- `userPermissions: string[]` - User's permission list
- `entitlements: OrgEntitlements | null` - Organization entitlements

#### Layer 1: Tenant Functions

- `hasTenantContext: boolean` - Whether valid org context exists
- `checkTenantAccess(targetOrgId: number): boolean` - Check access to specific org

#### Layer 2: Entitlement Functions

- `checkModuleEntitled(moduleKey: string): boolean` - Check if module is enabled
- `checkSubmoduleEntitled(moduleKey: string, submoduleKey: string): boolean`
- `getModuleEntitlementStatus(moduleKey: string): string` - Get module status ('enabled', 'disabled', 'trial')

#### Layer 3: RBAC Functions

- `checkPermission(permission: string): boolean` - Check specific permission
- `checkUserRole(role: string): boolean` - Check user's role
- `checkIsSuperAdmin(): boolean` - Check if super admin
- `checkIsOrgAdmin(): boolean` - Check if org admin
- `checkCanManageRole(targetRole: string): boolean` - Check role management capability

#### Combined Functions (All 3 Layers)

- `checkModuleAccess(moduleKey: string, action?: string): PermissionCheck`
- `checkSubmoduleAccess(moduleKey: string, submoduleKey: string, action?: string): PermissionCheck`

**PermissionCheck Type:**
```ts
interface PermissionCheck {
  hasPermission: boolean;
  reason?: string;
  enforcementLevel?: 'TENANT' | 'ENTITLEMENT' | 'RBAC';
}
```

### Examples

#### 1. Conditional UI Elements

```tsx
function Toolbar() {
  const { checkModuleAccess, checkPermission } = usePermissionCheck();

  const canExport = checkModuleAccess('reports', 'read').hasPermission;
  const canDelete = checkPermission('inventory.delete');

  return (
    <Box>
      {canExport && <Button>Export</Button>}
      {canDelete && <Button color="error">Delete</Button>}
    </Box>
  );
}
```

#### 2. Multi-Module Check

```tsx
function Dashboard() {
  const { checkModuleAccess, isReady } = usePermissionCheck();

  if (!isReady) return <Loading />;

  const hasCRM = checkModuleAccess('crm', 'read').hasPermission;
  const hasInventory = checkModuleAccess('inventory', 'read').hasPermission;
  const hasHR = checkModuleAccess('hr', 'read').hasPermission;

  return (
    <Grid container spacing={3}>
      {hasCRM && <Grid item xs={12} md={4}><CRMWidget /></Grid>}
      {hasInventory && <Grid item xs={12} md={4}><InventoryWidget /></Grid>}
      {hasHR && <Grid item xs={12} md={4}><HRWidget /></Grid>}
    </Grid>
  );
}
```

#### 3. Role-Based Features

```tsx
function UserMenu() {
  const { 
    checkIsSuperAdmin, 
    checkIsOrgAdmin, 
    checkCanManageRole 
  } = usePermissionCheck();

  return (
    <Menu>
      <MenuItem>Profile</MenuItem>
      {checkCanManageRole('executive') && (
        <MenuItem>Manage Users</MenuItem>
      )}
      {checkIsOrgAdmin() && (
        <MenuItem>Organization Settings</MenuItem>
      )}
      {checkIsSuperAdmin() && (
        <MenuItem>Admin Panel</MenuItem>
      )}
    </Menu>
  );
}
```

#### 4. Custom Permission Logic

```tsx
function DocumentEditor() {
  const { checkPermission, user, organizationId } = usePermissionCheck();

  const canEdit = checkPermission('documents.write');
  const isOwner = document.created_by === user?.id;
  const isSameOrg = document.organization_id === organizationId;

  // Custom business logic
  const allowEdit = canEdit && (isOwner || isSameOrg);

  return (
    <Box>
      <Document />
      {allowEdit && <EditControls />}
    </Box>
  );
}
```

---

## Common Patterns

### Pattern 1: Page-Level Protection

**Use Case:** Protect entire page with standard module access

```tsx
// pages/inventory/index.tsx
import { ProtectedPage } from '../../components/ProtectedPage';

export default function InventoryPage() {
  return (
    <ProtectedPage moduleKey="inventory" action="read">
      <InventoryContent />
    </ProtectedPage>
  );
}
```

### Pattern 2: Component-Level Protection

**Use Case:** Protect specific components within a page

```tsx
function Dashboard() {
  return (
    <Box>
      <Header />
      
      <ProtectedPage moduleKey="crm" action="read">
        <CRMSection />
      </ProtectedPage>
      
      <ProtectedPage moduleKey="inventory" action="read">
        <InventorySection />
      </ProtectedPage>
    </Box>
  );
}
```

### Pattern 3: HOC Protection

**Use Case:** Create reusable protected components

```tsx
import { withProtection } from '../../components/ProtectedPage';

const BaseCRMPage = () => <div>CRM Content</div>;

export const ProtectedCRMPage = withProtection(BaseCRMPage, {
  moduleKey: 'crm',
  action: 'read',
});
```

### Pattern 4: Hybrid Protection

**Use Case:** Page-level + feature-level checks

```tsx
function SettingsPage() {
  const { checkPermission } = usePermissionCheck();

  return (
    <ProtectedPage moduleKey="settings" action="read">
      <Box>
        <GeneralSettings />
        
        {checkPermission('settings.advanced') && (
          <AdvancedSettings />
        )}
        
        {checkPermission('settings.security') && (
          <SecuritySettings />
        )}
      </Box>
    </ProtectedPage>
  );
}
```

---

## Migration Guide

### Before (Old Pattern)

```tsx
// ❌ Old way - individual checks, no unified protection
function OldPage() {
  const { user } = useAuth();
  const { entitlements } = useEntitlements();
  const { hasPermission } = usePermissions();

  // Manual checks scattered throughout
  if (!user) return <Redirect to="/login" />;
  if (!entitlements?.enabled_modules.includes('crm')) {
    return <div>CRM not enabled</div>;
  }
  if (!hasPermission('crm.read')) {
    return <div>No permission</div>;
  }

  return <div>Content</div>;
}
```

### After (New Pattern)

```tsx
// ✅ New way - unified protection with ProtectedPage
function NewPage() {
  return (
    <ProtectedPage moduleKey="crm" action="read">
      <div>Content</div>
    </ProtectedPage>
  );
}
```

### Step-by-Step Migration

1. **Add Import**
   ```tsx
   import { ProtectedPage } from '../../components/ProtectedPage';
   ```

2. **Identify Protection Requirements**
   - What module does this page belong to?
   - What action is being performed? (read/write/delete)
   - Are there any special permission requirements?

3. **Wrap Content**
   ```tsx
   return (
     <ProtectedPage moduleKey="MODULE_NAME" action="ACTION">
       {/* existing content */}
     </ProtectedPage>
   );
   ```

4. **Remove Manual Checks**
   - Remove redundant `useAuth`, `useEntitlements`, `usePermissions` checks
   - Keep only business-logic-specific checks

5. **Test**
   - Verify loading state
   - Verify access with proper permissions
   - Verify access denial with missing permissions
   - Verify access denial with disabled module

---

## Testing

### Unit Testing ProtectedPage

```tsx
import { render, screen } from '@testing-library/react';
import { ProtectedPage } from '../ProtectedPage';

// Mock usePermissionCheck
jest.mock('../hooks/usePermissionCheck');

describe('MyProtectedPage', () => {
  it('should show content when access granted', () => {
    mockUsePermissionCheck.mockReturnValue({
      isReady: true,
      checkModuleAccess: () => ({ hasPermission: true }),
    });

    render(
      <ProtectedPage moduleKey="crm" action="read">
        <div>Protected Content</div>
      </ProtectedPage>
    );

    expect(screen.getByText('Protected Content')).toBeInTheDocument();
  });

  it('should show access denied when permission missing', () => {
    mockUsePermissionCheck.mockReturnValue({
      isReady: true,
      checkModuleAccess: () => ({
        hasPermission: false,
        reason: 'Module not enabled',
      }),
    });

    render(
      <ProtectedPage moduleKey="crm" action="read">
        <div>Protected Content</div>
      </ProtectedPage>
    );

    expect(screen.getByText('Access Denied')).toBeInTheDocument();
    expect(screen.queryByText('Protected Content')).not.toBeInTheDocument();
  });
});
```

### Integration Testing

```tsx
describe('CRM Page Integration', () => {
  it('should allow access with proper setup', async () => {
    // Setup: Create org, enable CRM, assign permissions
    const { user, org } = await setupTestEnvironment({
      role: 'manager',
      enabledModules: ['crm'],
      permissions: ['crm.read', 'crm.write'],
    });

    // Navigate to CRM page
    renderWithAuth(<CRMPage />, { user, org });

    // Should show content
    await waitFor(() => {
      expect(screen.getByText('CRM Dashboard')).toBeInTheDocument();
    });
  });

  it('should deny access without module entitlement', async () => {
    const { user, org } = await setupTestEnvironment({
      role: 'manager',
      enabledModules: [], // CRM not enabled
      permissions: ['crm.read'],
    });

    renderWithAuth(<CRMPage />, { user, org });

    // Should show access denied
    await waitFor(() => {
      expect(screen.getByText('Access Denied')).toBeInTheDocument();
      expect(screen.getByText(/module not enabled/i)).toBeInTheDocument();
    });
  });
});
```

---

## Best Practices

### 1. Choose the Right Level of Protection

- **Page-Level:** Use `ProtectedPage` wrapper for entire pages
- **Component-Level:** Use `usePermissionCheck` for conditional UI elements
- **Mixed:** Combine both for complex pages

### 2. Be Specific with Actions

```tsx
// ✅ Good - specific action
<ProtectedPage moduleKey="inventory" action="write">
  <InventoryEditor />
</ProtectedPage>

// ❌ Bad - too permissive
<ProtectedPage moduleKey="inventory" action="read">
  <InventoryEditor />
</ProtectedPage>
```

### 3. Provide Clear Error Messages

```tsx
<ProtectedPage
  moduleKey="reports"
  action="read"
  accessDeniedMessage="Reports module is required. Please contact your administrator to enable this feature."
>
  <Reports />
</ProtectedPage>
```

### 4. Handle Loading States

```tsx
function MyPage() {
  const { isReady, isLoading } = usePermissionCheck();

  if (isLoading) {
    return <Skeleton />;
  }

  return (
    <ProtectedPage moduleKey="crm">
      <Content />
    </ProtectedPage>
  );
}
```

### 5. Combine with Business Logic

```tsx
function DocumentPage({ documentId }) {
  const { checkPermission, user } = usePermissionCheck();
  const { data: document } = useDocument(documentId);

  const canEdit = checkPermission('documents.write') && 
                  document.owner_id === user?.id;

  return (
    <ProtectedPage moduleKey="documents" action="read">
      <Document data={document} />
      {canEdit && <EditButton />}
    </ProtectedPage>
  );
}
```

### 6. Avoid Over-Protection

```tsx
// ❌ Don't do this - redundant checks
<ProtectedPage moduleKey="crm">
  <ProtectedPage moduleKey="crm" submoduleKey="leads">
    <ProtectedPage moduleKey="crm" action="write">
      <Content />
    </ProtectedPage>
  </ProtectedPage>
</ProtectedPage>

// ✅ Do this - single comprehensive check
<ProtectedPage 
  moduleKey="crm" 
  submoduleKey="leads" 
  action="write"
>
  <Content />
</ProtectedPage>
```

### 7. Document Your Protection

```tsx
/**
 * CRM Leads Management Page
 * 
 * Protection:
 * - Module: CRM (must be enabled)
 * - Submodule: Leads (must be enabled)
 * - Permission: crm.write (for editing leads)
 * 
 * Access: Manager and above
 */
export default function LeadsPage() {
  return (
    <ProtectedPage 
      moduleKey="crm" 
      submoduleKey="leads" 
      action="write"
    >
      <LeadsContent />
    </ProtectedPage>
  );
}
```

---

## Summary

### Quick Checklist for New Pages

- [ ] Import `ProtectedPage` component
- [ ] Identify required module and action
- [ ] Wrap page content with `ProtectedPage`
- [ ] Test with proper permissions (should work)
- [ ] Test with missing permissions (should deny)
- [ ] Test with disabled module (should deny)
- [ ] Remove any redundant permission checks
- [ ] Document protection requirements

### Module Keys Reference

Common module keys:
- `crm` - CRM/Sales
- `inventory` - Inventory Management
- `manufacturing` - Manufacturing
- `hr` - Human Resources
- `finance` - Finance/Accounting
- `reports` - Reports
- `settings` - Settings
- `admin` - Admin Panel

### Action Keys Reference

- `read` - View/list data
- `write` - Create/update data
- `delete` - Delete data
- `export` - Export data
- `import` - Import data

---

## Support

For questions or issues:
1. Check existing tests in `src/components/__tests__/ProtectedPage.test.tsx`
2. Review examples in updated pages (CRM, Settings, Inventory, HR)
3. Consult `RBAC_DOCUMENTATION.md` for backend integration
4. Contact the development team

---

**Last Updated:** 2025-11-05  
**Version:** 1.0
