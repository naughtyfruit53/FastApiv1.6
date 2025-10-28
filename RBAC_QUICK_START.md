# RBAC Frontend Integration - Quick Start Guide

## What's Been Implemented

This guide provides a quick overview of the RBAC (Role-Based Access Control) frontend integration.

## For Developers

### 1. Using RoleGate for Protected Routes/Components

```tsx
import RoleGate from '@/components/RoleGate';

// Permission-based access
<RoleGate requiredPermissions={['finance.read', 'finance.write']}>
  <FinanceDashboard />
</RoleGate>

// Module-based access
<RoleGate requireModule="finance">
  <FinanceSection />
</RoleGate>

// Submodule-based access
<RoleGate requireSubmodule={{ module: 'finance', submodule: 'reports' }}>
  <FinanceReports />
</RoleGate>

// With custom fallback
<RoleGate 
  requiredPermissions={['admin.access']}
  fallbackUI={<CustomUnauthorizedPage />}
>
  <AdminPanel />
</RoleGate>
```

### 2. Using useSharedPermissions Hook

```tsx
import { useSharedPermissions } from '@/hooks/useSharedPermissions';

function MyComponent() {
  const { 
    hasPermission, 
    hasModuleAccess, 
    hasSubmoduleAccess,
    userPermissions 
  } = useSharedPermissions();

  // Check specific permission
  if (!hasPermission('finance.create')) {
    return <AccessDenied />;
  }

  // Check module access
  const canAccessFinance = hasModuleAccess('finance');

  // Check submodule access
  const canAccessReports = hasSubmoduleAccess('finance', 'reports');

  // Get all user permissions
  console.log(userPermissions.permissions); // ['finance.read', 'finance.write', ...]
  console.log(userPermissions.modules);     // ['finance', 'inventory', ...]
  console.log(userPermissions.submodules);  // { finance: ['reports', 'ledger'], ... }

  return <div>...</div>;
}
```

### 3. Using AuthContext for Permissions

```tsx
import { useAuth } from '@/context/AuthContext';

function MyComponent() {
  const { userPermissions, refreshPermissions } = useAuth();

  // Access permissions directly
  const hasFinanceAccess = userPermissions?.modules.includes('finance');

  // Refresh permissions after changes
  const handlePermissionUpdate = async () => {
    await updateUserPermissions(userId, newPermissions);
    await refreshPermissions(); // Sync with backend
  };

  return <div>...</div>;
}
```

### 4. Configuring Menu Items with Permissions

In `menuConfig.tsx`:

```tsx
export const menuItems = {
  finance: {
    title: 'Finance',
    icon: <AccountBalance />,
    sections: [
      {
        title: 'Reports',
        items: [
          {
            name: 'Balance Sheet',
            path: '/finance/balance-sheet',
            icon: <Assessment />,
            permission: PERMISSIONS.FINANCE_READ,           // Add this
            requireModule: 'finance',                       // Add this
            requireSubmodule: {                             // Add this
              module: 'finance',
              submodule: 'reports'
            }
          }
        ]
      }
    ]
  }
};
```

### 5. Managing User Permissions

Navigate to: **Settings → User Management → Click Gear Icon**

Or programmatically:
```tsx
router.push(`/settings/user-permissions/${userId}`);
```

## For Administrators

### Managing User Permissions

1. **Go to User Management:**
   - Navigate to Settings → User Management
   - Find the user in the table

2. **Access Permissions Page:**
   - Click the gear (⚙️) icon in the Actions column
   - Or edit user and click "Manage Permissions"

3. **Configure Module Access:**
   - Select "Module Access" tab
   - Check modules the user should access
   - Changes are hierarchical (submodules depend on modules)

4. **Configure Submodule Access:**
   - Select "Submodule Access" tab
   - Fine-tune access within each module
   - Only available for selected modules

5. **Save Changes:**
   - Click "Save Changes" button
   - Permissions update immediately

### Managing Roles (Admin Only)

Navigate to: **Admin → RBAC**

Features:
- Create/edit/delete roles
- Assign permissions to roles
- View permission matrix
- Assign roles to users

## API Integration Points

### Backend Endpoints Needed

1. **Get User Permissions:**
   ```
   GET /api/rbac/users/{userId}/permissions
   Response: {
     user_id: number,
     permissions: string[],
     roles: Role[],
     total_permissions: number
   }
   ```

2. **Get User Roles:**
   ```
   GET /api/rbac/users/{userId}/roles
   Response: Role[]
   ```

3. **Update User Permissions:**
   ```
   POST /api/rbac/users/{userId}/permissions
   Body: {
     modules: string[],
     submodules: Record<string, string[]>,
     permissions: string[]
   }
   ```

## Permission Naming Convention

Format: `{module}_{action}`

Examples:
- `master_data_read`
- `finance_create`
- `inventory_delete`
- `reports_export`

For submodules: `{module}_{submodule}_{action}`

Examples:
- `finance_reports_read`
- `finance_ledger_create`

## Common Patterns

### Conditional UI Elements

```tsx
// Hide button if no permission
{hasPermission('finance.create') && (
  <Button onClick={handleCreate}>Create Invoice</Button>
)}

// Disable button if no permission
<Button 
  disabled={!hasPermission('finance.delete')}
  onClick={handleDelete}
>
  Delete
</Button>

// Show different content based on permission
{hasPermission('finance.admin') ? (
  <AdminFinanceView />
) : (
  <RegularFinanceView />
)}
```

### Protected Routes

```tsx
// In page component
export default function FinancePage() {
  return (
    <RoleGate requireModule="finance">
      <FinanceContent />
    </RoleGate>
  );
}
```

### Dynamic Navigation

Navigation automatically filters based on permissions. No additional code needed in most cases.

## Troubleshooting

### Permissions Not Updating

1. Check if `refreshPermissions()` is called after changes
2. Verify backend returns updated permissions
3. Check browser console for errors
4. Clear browser cache and reload

### Menu Items Not Showing

1. Verify user has required permissions
2. Check menu item permission configuration
3. Ensure `userPermissions` is loaded in AuthContext
4. Check for typos in permission names

### Access Denied Errors

1. Verify user has required role/permission
2. Check RoleGate configuration
3. Review backend permission validation
4. Check if super admin bypass is working

## Best Practices

1. **Always validate on backend:** Frontend checks are for UX only
2. **Use specific permissions:** Prefer `finance.create` over wildcard `finance.*`
3. **Check permissions early:** Use RoleGate at route level when possible
4. **Provide fallback UI:** Don't leave users with blank screens
5. **Test edge cases:** Super admin, no permissions, partial permissions
6. **Document permissions:** List required permissions in component docs

## Security Notes

⚠️ **Critical:**
- All frontend permission checks are for UX improvement only
- Backend MUST independently validate all permissions
- Never expose sensitive data based on frontend checks alone
- Always use server-side authorization

## Support

For issues or questions:
1. Check RBAC_FRONTEND_IMPLEMENTATION.md for detailed docs
2. Review example implementations in codebase
3. Test with different permission sets
4. Contact backend team for API integration help
