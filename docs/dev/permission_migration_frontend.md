# Frontend Permission Migration Guide

## Overview

This guide documents the migration of the frontend permission system from mixed formats (underscore `_`, colon `:`) to a unified **dotted format** (`module.action`) with hierarchical permission support.

## Migration Timeline

- **Phase 1**: Backend migration to dotted format with compatibility layer (Completed)
- **Phase 2**: Frontend migration with compatibility shim (Current - Q1 2026)
- **Phase 3**: Remove compatibility shim after monitoring (Q2 2026)

## What Changed

### 1. Permission Format Standardization

#### Before (Mixed Formats)
```typescript
// Old formats were inconsistent
'inventory_read'      // Underscore format
'voucher:create'      // Colon format
'master_data.delete'  // Dotted format (partial)
```

#### After (Dotted Format)
```typescript
// New unified format
'inventory.read'
'voucher.create'
'master_data.delete'
```

### 2. Permission Hierarchy Support

Parent permissions now grant all child permissions automatically:

```typescript
// If user has 'master_data.read', they automatically get:
'vendors.read'
'products.read'
'inventory.read'

// If user has 'crm.admin', they automatically get:
'crm.settings'
'crm.commission.read'
'crm.commission.create'
'crm.commission.update'
'crm.commission.delete'
```

### 3. Backend Feature Detection

The frontend now queries the backend for permission format configuration:

```typescript
GET /api/v1/system/permission-format

Response:
{
  "primary_format": "dotted",
  "compatibility": true,
  "legacy_formats": ["underscore", "colon"],
  "hierarchy_enabled": true,
  "version": "1.0",
  "migration_status": "in_progress"
}
```

## Updated Components

### PermissionContext.tsx

**New Features:**
- Automatic permission format detection from backend
- Hierarchy-aware permission checking
- Compatibility shim for legacy formats (temporary)
- `permissionFormat` state exposed to consumers

**Usage:**
```typescript
import { usePermissions } from '@/context/PermissionContext';

const MyComponent = () => {
  const { hasPermission, permissionFormat } = usePermissions();
  
  // Standard check (supports all formats during migration)
  if (!hasPermission('inventory', 'read')) {
    return <AccessDenied />;
  }
  
  // Check format for debugging
  console.log('Primary format:', permissionFormat?.primaryFormat); // 'dotted'
  
  return <InventoryList />;
};
```

### rbac.ts

**New Exports:**
- `PERMISSION_HIERARCHY`: Client-side hierarchy mapping
- `hasPermissionThroughHierarchy()`: Helper function for hierarchy checks
- `PermissionCheck.isLoading`: Added loading state to interface

### usePermissionCheck.ts

**Enhancements:**
- Now checks permissions in dotted format by default
- Falls back to legacy formats when compatibility is enabled
- Supports hierarchy checks when enabled

## Migration Instructions

### For Component Developers

#### 1. Update Permission Checks

**Before:**
```typescript
// Old mixed format checks
if (hasPermission('inventory_read') || hasPermission('inventory:read')) {
  // ...
}
```

**After:**
```typescript
// New unified format
if (hasPermission('inventory', 'read')) {
  // Automatically checks: inventory.read, inventory_read, inventory:read
  // ...
}
```

#### 2. Update Permission Arrays

**Before:**
```typescript
const permissions = ['voucher_create', 'voucher:update', 'voucher.delete'];
```

**After:**
```typescript
const permissions = ['voucher.create', 'voucher.update', 'voucher.delete'];
```

#### 3. Use hasAnyPermission and hasAllPermissions

```typescript
// Check multiple permissions
if (hasAnyPermission(['inventory.read', 'inventory.write'])) {
  // User has at least one permission
}

if (hasAllPermissions(['voucher.create', 'voucher.update'])) {
  // User has all permissions
}
```

### For Page Developers

#### Protected Routes

**Before:**
```typescript
// Manual permission checks scattered in components
if (!permissions.includes('inventory_read')) {
  return <AccessDenied />;
}
```

**After:**
```typescript
// Use HOC for cleaner protection
import { withPermission } from '@/context/PermissionContext';

const InventoryPage = () => {
  return <InventoryList />;
};

export default withPermission(InventoryPage, 'inventory', 'read');
```

## Compatibility Mode

### Current State (Q1 2026)

The frontend currently operates in **compatibility mode**, which means:

1. ✅ Dotted format is the primary format
2. ✅ Legacy formats (underscore, colon) are still supported
3. ✅ Hierarchy checks are enabled
4. ⚠️ Performance overhead from checking multiple formats

### After Migration (Q2 2026)

Once all clients are migrated:

1. ✅ Only dotted format will be supported
2. ✅ Compatibility shim will be removed
3. ✅ Better performance from single format checks
4. ✅ Reduced bundle size

## Testing

### Unit Tests

Run permission tests:
```bash
npm test -- --testPathPattern="PermissionContext"
```

### Integration Tests

Run permission integration tests:
```bash
npm test -- --testPathPattern="menuAccess"
```

### Smoke Tests

Run permission smoke tests:
```bash
npm test -- --testPathPattern="PermissionContext.hierarchy"
```

## Hierarchy Reference

Full hierarchy mapping:

```typescript
PERMISSION_HIERARCHY = {
  "master_data.read": [
    "vendors.read",
    "products.read", 
    "inventory.read"
  ],
  "master_data.write": [
    "vendors.create",
    "vendors.update",
    "products.write",
    "products.update",
    "inventory.write",
    "inventory.update"
  ],
  "master_data.delete": [
    "vendors.delete",
    "products.delete",
    "inventory.delete"
  ],
  "crm.admin": [
    "crm.settings",
    "crm.commission.read",
    "crm.commission.create",
    "crm.commission.update",
    "crm.commission.delete"
  ],
  "platform.super_admin": [
    "platform.admin",
    "platform.factory_reset"
  ],
  "platform.admin": [
    "organizations.manage",
    "organizations.view",
    "organizations.create",
    "organizations.delete",
    "audit.view_all"
  ]
}
```

## Troubleshooting

### Permission Denied But Should Have Access

1. Check the backend returns permissions in dotted format:
   ```bash
   GET /api/v1/rbac/permissions/me
   ```

2. Verify compatibility mode is enabled:
   ```bash
   GET /api/v1/system/permission-format
   ```

3. Check browser console for permission format configuration:
   ```javascript
   const { permissionFormat } = usePermissions();
   console.log(permissionFormat);
   ```

### Hierarchy Not Working

1. Verify hierarchy is enabled in backend response:
   ```json
   {
     "hierarchy_enabled": true
   }
   ```

2. Check the permission hierarchy mapping matches backend:
   ```bash
   GET /api/v1/system/permission-format/hierarchy
   ```

3. Ensure parent permission is in user's permission list

### Mixed Format Issues

During migration, if you see mixed formats:

1. Use dotted format in new code
2. Legacy formats will be automatically mapped during compatibility mode
3. Report any unmapped legacy formats to the team

## FAQ

### Q: When will compatibility mode be removed?

**A:** Q2 2026, after monitoring shows all clients are using dotted format.

### Q: Do I need to update existing permission checks?

**A:** Not immediately. Compatibility mode supports old formats. However, please update to dotted format when making changes to those components.

### Q: What if I find a permission in an old format?

**A:** It will work during compatibility mode, but please update it to dotted format and submit a PR.

### Q: How do I know which format my backend is returning?

**A:** Call `GET /api/v1/system/permission-format` or check the `permissionFormat` state in `usePermissions()`.

### Q: Can I still use underscore or colon format?

**A:** Yes, during compatibility mode (until Q2 2026). After that, only dotted format will be supported.

### Q: What about super admins?

**A:** Super admins bypass all permission checks regardless of format.

## Contact

For questions or issues:
- Create an issue in the repository
- Contact the backend team for permission-related questions
- Review the [RBAC Comprehensive Guide](../../RBAC_COMPREHENSIVE_GUIDE.md)

## Related Documentation

- [Backend Permission Migration Guide](./permission_migration_backend.md)
- [RBAC Comprehensive Guide](../../RBAC_COMPREHENSIVE_GUIDE.md)
- [Permission Matrix](../../docs/PERMISSION_MATRIX.md)
- [Frontend Testing Guide](../../FRONTEND_TESTING_GUIDE.md)
