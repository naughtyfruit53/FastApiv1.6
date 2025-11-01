# MegaMenu Runtime Error Checklist

## Purpose

This checklist helps diagnose and prevent common runtime errors in MegaMenu related to entitlements, icon imports, and module gating.

## Pre-Deployment Checklist

### ✅ Icon Imports

- [ ] All icons imported at top of `menuConfig.tsx`
- [ ] No dynamic icon imports or JSX strings
- [ ] Icon components used as `<IconName />`, not `IconName`
- [ ] No duplicate imports with different names
- [ ] Verify imports match Material-UI icon names exactly

**Common Issues:**
```typescript
// ❌ Bad: Dynamic import
const icon = require(`@mui/icons-material/${iconName}`);

// ❌ Bad: String instead of component
icon: "Settings"

// ❌ Bad: Function call
icon: Settings()

// ✅ Good: Static import and JSX component
import { Settings } from '@mui/icons-material';
icon: <Settings />
```

### ✅ Module Entitlement Mapping

- [ ] All menu items have correct `requireModule` property
- [ ] Submodule items have correct `requireSubmodule` property
- [ ] Email module marked as always-on (no entitlement check)
- [ ] Settings/Admin marked as RBAC-only (no entitlement check)
- [ ] Module keys match database module_key values exactly
- [ ] No orphaned menu items (no parent module defined)

**Module Key Validation:**
```typescript
// ✅ Valid module keys
requireModule: 'crm'           // ✅ Sales/Marketing
requireModule: 'erp'           // ✅ Master Data/Inventory/Vouchers/Projects/Tasks
requireModule: 'manufacturing' // ✅ Manufacturing
requireModule: 'finance'       // ✅ Accounting/Finance
requireModule: 'service'       // ✅ Service Management
requireModule: 'hr'            // ✅ Human Resources
requireModule: 'analytics'     // ✅ Reporting/AI Analytics

// ❌ Invalid (not in database)
requireModule: 'sales'         // ❌ Should be 'crm'
requireModule: 'inventory'     // ❌ Should be 'erp'
```

### ✅ Email Menu Placement

- [ ] Email is top-level, between "Menu" button and "Settings"
- [ ] Email not duplicated under Menu dropdown
- [ ] Email has no `requireModule` (always-on)
- [ ] Email visible to all users regardless of entitlements
- [ ] Email icon imported and used correctly

**Correct Structure:**
```typescript
// ✅ Top-level order
<MegaMenuButton />           // "Menu" dropdown
<EmailButton />              // Email (always visible)
<SettingsButton />           // Settings (admin-only, RBAC)
<NotificationsButton />
<LogoutButton />
```

### ✅ Settings/Admin Visibility

- [ ] Settings visible only to admin users (isAdminLike check)
- [ ] Settings has no `requireModule` (RBAC-only)
- [ ] Admin panel items under Settings (not separate)
- [ ] Super admin options properly nested
- [ ] No entitlement checks on Settings items

### ✅ ErrorBoundary Protection

- [ ] MegaMenu wrapped in ErrorBoundary
- [ ] ErrorBoundary has fallback UI
- [ ] ErrorBoundary logs errors for debugging
- [ ] Child components have their own ErrorBoundaries where needed

```typescript
// ✅ Proper ErrorBoundary usage
<ErrorBoundary
  fallback={<div>Menu temporarily unavailable</div>}
  onError={(error) => console.error('MegaMenu error:', error)}
>
  <MegaMenu {...props} />
</ErrorBoundary>
```

## Runtime Validation

### ✅ Entitlements Loading

- [ ] EntitlementsContext provides data to MegaMenu
- [ ] Loading state handled gracefully (show skeleton or disable items)
- [ ] Error state handled (show fallback, allow retry)
- [ ] Cache invalidation working after module selection
- [ ] Entitlements refresh on org switch

**Debug Commands:**
```javascript
// Check entitlements in browser console
const { entitlements } = useEntitlements();
console.log('Loaded entitlements:', entitlements);

// Check context
console.log('Context:', React.useContext(EntitlementsContext));
```

### ✅ Menu Item Access Evaluation

- [ ] `evalMenuItemAccess` called for each conditional item
- [ ] Super admin bypass working (all items enabled)
- [ ] Disabled modules show with lock icon (not hidden)
- [ ] Trial badges display correctly
- [ ] Tooltips show helpful messages for disabled items

**Test Scenarios:**
```typescript
// Test with different entitlement states
evalMenuItemAccess({
  requireModule: 'manufacturing',
  entitlements: mockEntitlements,
  isAdmin: false,
  isSuperAdmin: false,
});
// Expected: 'disabled' if module not in entitlements

// Test super admin bypass
evalMenuItemAccess({
  requireModule: 'manufacturing',
  entitlements: mockEntitlements,
  isAdmin: true,
  isSuperAdmin: true,
});
// Expected: 'enabled' regardless of entitlements
```

### ✅ Bundle Mapping Consistency

- [ ] ModuleSelectionModal bundles match menu modules
- [ ] Bundle changes immediately reflect in menu
- [ ] No orphaned menu items after bundle deselection
- [ ] Email remains visible after all bundles disabled
- [ ] Settings remains visible for admin users

**Bundle to Module Mapping:**
```typescript
CRM → ['crm']
ERP → ['erp']
Manufacturing → ['manufacturing']
Finance → ['finance']
Service → ['service']
HR → ['hr']
Analytics → ['analytics']
```

### ✅ Cache Invalidation

- [ ] Cache invalidates on entitlement update
- [ ] Menu updates within 5 minutes of change (cache TTL)
- [ ] Force refresh available if needed
- [ ] No stale data after org switch
- [ ] Browser localStorage cleared on logout

## Common Runtime Errors

### Error: "Cannot read property 'map' of undefined"

**Cause**: Entitlements not loaded or null

**Fix**:
```typescript
// ❌ Bad: No null check
menuItems.filter(item => evalMenuItemAccess(...))

// ✅ Good: Null check
if (!entitlements) return <LoadingSkeleton />;
menuItems.filter(item => evalMenuItemAccess(...))
```

### Error: "Element type is invalid: expected a string (for built-in components) or a class/function"

**Cause**: Icon imported incorrectly or used as string

**Fix**:
```typescript
// ❌ Bad: String icon
icon: "Settings"

// ❌ Bad: Function call
icon: Settings()

// ✅ Good: JSX component
import { Settings } from '@mui/icons-material';
icon: <Settings />
```

### Error: "Module 'sales' not found in entitlements"

**Cause**: Module key mismatch (frontend uses 'sales', backend has 'crm')

**Fix**:
```typescript
// ❌ Bad: Wrong module key
requireModule: 'sales'

// ✅ Good: Correct module key
requireModule: 'crm'
```

### Warning: "Email not visible"

**Cause**: Email incorrectly gated by entitlement check

**Fix**:
```typescript
// ❌ Bad: Email gated
{
  title: 'Email',
  requireModule: 'email', // This would gate it
  ...
}

// ✅ Good: Email always-on (no requireModule)
{
  title: 'Email',
  // No requireModule property
  ...
}
```

### Error: "Settings visible to non-admin users"

**Cause**: Missing admin check in Settings visibility logic

**Fix**:
```typescript
// ❌ Bad: No admin check
<MenuItem>Settings</MenuItem>

// ✅ Good: Admin check
{isAdminLike && <MenuItem>Settings</MenuItem>}
```

## Testing Commands

### Manual Testing

```bash
# Run frontend tests
cd frontend
npm test -- MegaMenu.entitlements.test.tsx

# Run specific test
npm test -- --testNamePattern="Email is always visible"

# Watch mode
npm test -- --watch MegaMenu
```

### Browser Console Tests

```javascript
// 1. Check entitlements load
console.log(localStorage.getItem('access_token'));

// 2. Inspect entitlements data
fetch('/api/v1/orgs/1/entitlements', {
  headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` }
})
.then(r => r.json())
.then(data => console.log('Entitlements:', data));

// 3. Check module access evaluation
import { evalMenuItemAccess } from '@/permissions/menuAccess';
const result = evalMenuItemAccess({
  requireModule: 'manufacturing',
  entitlements: window.__ENTITLEMENTS__, // Set this in dev
  isAdmin: false,
  isSuperAdmin: false,
});
console.log('Access result:', result);

// 4. Verify cache
console.log('Cached:', localStorage.getItem('entitlements:org:1'));
```

## Deployment Verification

### Post-Deployment Checklist

- [ ] MegaMenu renders without console errors
- [ ] All icons display correctly
- [ ] Email is visible and clickable
- [ ] Settings visible only to admins
- [ ] Disabled modules show lock icon with tooltip
- [ ] Trial badges display for trial modules
- [ ] Module selection modal works end-to-end
- [ ] Menu updates after module selection within TTL
- [ ] Super admin sees all items regardless of entitlements
- [ ] Non-admin users see only enabled modules
- [ ] No duplicate menu items
- [ ] All links navigate correctly

### Smoke Tests

**Test 1: Email Always Visible**
1. Log in as any user
2. Verify Email button is visible in top bar
3. Click Email, verify it opens
4. Expected: ✅ Email always works

**Test 2: Disabled Module**
1. Log in as non-admin
2. Select org with Manufacturing disabled
3. Verify Manufacturing menu items disabled with lock icon
4. Try to access Manufacturing page directly
5. Expected: ✅ Menu disabled, API returns 403

**Test 3: Module Selection**
1. Log in as super admin
2. Open Module Selection Modal
3. Disable CRM bundle
4. Save changes
5. Wait for cache invalidation (< 5 min)
6. Verify CRM menu items disabled
7. Expected: ✅ Menu updates correctly

**Test 4: Super Admin Bypass**
1. Log in as super admin
2. Select org with all modules disabled
3. Verify all menu items still enabled
4. Access API endpoints
5. Expected: ✅ Super admin has full access

## Monitoring

### Metrics to Track

- Menu render time
- Entitlement API response time
- Cache hit rate
- Number of 403 entitlement_denied errors
- Icon load failures
- JavaScript errors in MegaMenu component

### Alerts

Set up alerts for:
- High rate of 403 entitlement_denied errors
- Menu fails to render (JavaScript error)
- Entitlements API unavailable
- Cache invalidation failures

## Troubleshooting Flow

```
User reports: "Menu not showing items"
  ↓
1. Check: Is user logged in?
  → No: Redirect to login
  → Yes: Continue
  ↓
2. Check: Are entitlements loaded?
  → No: Check API response (network tab)
  → Yes: Continue
  ↓
3. Check: Does org have modules enabled?
  → No: Explain entitlements (not a bug)
  → Yes: Continue
  ↓
4. Check: Is cache stale?
  → Yes: Wait for TTL or force refresh
  → No: Continue
  ↓
5. Check: Console errors?
  → Yes: Fix icon import or JSX issue
  → No: Escalate to engineering
```

## Support Resources

- [Entitlements Architecture](ENTITLEMENTS_ARCHITECTURE.md)
- [Menu Permission Map](menu_permission_map.csv)
- [Module Bundle Mapping](../../frontend/src/config/moduleBundleMap.ts)
- [MegaMenu Component](../../frontend/src/components/MegaMenu.tsx)
- [Menu Access Tests](../../frontend/src/permissions/__tests__/menuAccess.test.ts)
