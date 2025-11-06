# Module-to-Menu Mapping Guide

This guide documents the mapping between backend organization modules and frontend MegaMenu items. Understanding this mapping is essential for troubleshooting menu visibility issues and managing feature access.

## Overview

The FastAPI backend manages module enablement at the organization level via the `enabled_modules` field in the Organization model. The frontend MegaMenu uses these modules to control menu item visibility through the `requireModule` and `requireSubmodule` properties.

## Architecture Flow

```
Organization (Backend)
  └─> enabled_modules: Dict[str, bool]
        │
        └─> API: GET /api/v1/organizations/{org_id}/modules
              │
              └─> Frontend AuthContext
                    │
                    └─> MegaMenu Component
                          │
                          └─> menuConfig.tsx (menu items with module requirements)
```

## Core Module Mappings

### 1. Master Data Module
**Backend Module Key**: `master_data`

**Frontend Menu Items**:
- Master Data → Business Entities
  - Vendors (`requireSubmodule: { module: 'master_data', submodule: 'vendors' }`)
  - Customers (`requireSubmodule: { module: 'master_data', submodule: 'customers' }`)
  - Employees (`requireSubmodule: { module: 'master_data', submodule: 'employees' }`)
  - Company Details (`requireSubmodule: { module: 'master_data', submodule: 'company_details' }`)

- Master Data → Product & Inventory
  - Products (`requireSubmodule: { module: 'master_data', submodule: 'products' }`)
  - Categories (`requireSubmodule: { module: 'master_data', submodule: 'categories' }`)
  - Units (`requireSubmodule: { module: 'master_data', submodule: 'units' }`)
  - Bill of Materials (`requireSubmodule: { module: 'master_data', submodule: 'bom' }`)

- Master Data → Financial Configuration
  - Chart of Accounts (`requireSubmodule: { module: 'master_data', submodule: 'chart_of_accounts' }`)
  - Tax Codes (`requireSubmodule: { module: 'master_data', submodule: 'tax_codes' }`)
  - Payment Terms (`requireSubmodule: { module: 'master_data', submodule: 'payment_terms' }`)
  - Bank Account (`requireSubmodule: { module: 'master_data', submodule: 'bank_account' }`)

### 2. Inventory Module
**Backend Module Key**: `inventory`

**Frontend Menu Items**:
- Inventory → Stock Management
  - Current Stock (all inventory submodules)
  - Stock Adjustments
  - Stock Transfer
  - Stock Reports

### 3. Finance Module
**Backend Module Key**: `finance`

**Frontend Menu Items**:
- Finance menu and all sub-items
- Accounting menu items
- Chart of Accounts
- Ledger entries
- Bank reconciliation

### 4. Sales Module
**Backend Module Key**: `sales`

**Frontend Menu Items**:
- Sales menu
- Sales Orders
- Invoices
- Quotations
- Sales Reports

### 5. CRM Module
**Backend Module Key**: `crm`

**Frontend Menu Items**:
- CRM menu
- Contacts
- Leads
- Opportunities
- CRM Analytics

### 6. HR Module
**Backend Module Key**: `hr`

**Frontend Menu Items**:
- HR menu
- Employees
- Attendance
- Payroll
- Leave Management

### 7. Service Module
**Backend Module Key**: `service`

**Frontend Menu Items**:
- Service menu
- Service Orders
- Appointments
- Work Orders
- Technicians

### 8. Manufacturing Module
**Backend Module Key**: `manufacturing`

**Frontend Menu Items**:
- Manufacturing menu
- Production Orders
- Work Centers
- Quality Control
- Manufacturing Reports

### 9. Reports & Analytics Module
**Backend Module Key**: `reportsAnalytics`

**Frontend Menu Items**:
- Reports menu
- Financial Reports
- Operational Reports
- Custom Reports
- Analytics Dashboard

### 10. Settings Module
**Backend Module Key**: `settings`

**Frontend Menu Items**:
- Settings menu
- Organization Settings
- User Management
- Role Management
- Module Configuration

## Module Visibility Logic

The frontend determines menu item visibility using the following logic:

```typescript
const isModuleEnabled = (module: string): boolean => {
  // Super admin sees all modules
  if (isSuperAdmin) return true;
  
  // Check organization's enabled modules
  const enabled = organizationData?.enabled_modules?.[module] ?? false;
  return enabled;
};
```

## User Permission Flow

1. **User Login**
   - Backend authenticates user
   - Returns user details with organization_id
   - Frontend stores user in AuthContext

2. **Fetch Organization Modules**
   - Frontend calls `GET /api/v1/organizations/{org_id}/modules`
   - Backend returns `enabled_modules` dictionary
   - Frontend stores in React Query cache

3. **Fetch User Permissions**
   - Frontend calls `GET /api/v1/rbac/users/{user_id}/permissions`
   - Backend returns user's RBAC permissions
   - Frontend stores in AuthContext

4. **Menu Rendering**
   - MegaMenu component checks module enablement
   - Filters menu items based on enabled modules
   - Checks RBAC permissions for fine-grained access
   - Renders visible menu items

## Troubleshooting

### Issue: "No Menu Items Available"

**Possible Causes**:
1. Organization modules not set properly
   ```sql
   -- Check organization modules in database
   SELECT id, name, enabled_modules FROM organizations WHERE id = ?;
   ```

2. API endpoint failing to return modules
   - Check backend logs for errors in `/api/v1/organizations/{org_id}/modules`
   - Verify organization_id is correctly set in requests

3. Frontend not receiving modules
   - Check browser console for API errors
   - Verify React Query cache has organization data
   - Check AuthContext state

**Solutions**:
1. Set default modules for organization:
   ```python
   # Backend: Set default modules
   from app.core.modules_registry import get_default_enabled_modules
   organization.enabled_modules = get_default_enabled_modules()
   ```

2. For super_admin accessing modules:
   - The backend now allows super_admin to access organization modules without prior context
   - Organization ID is extracted from path parameters
   - No "No current organization specified" error

### Issue: Super Admin Cannot Access Organization Modules

**Fix Applied**:
The `require_current_organization_id` function now returns `None` for super_admin users without organization context, allowing them to access organization-scoped endpoints. The organization_id is extracted from the URL path parameter in the endpoint handler.

### Issue: Specific Menu Item Not Showing

**Check**:
1. Module enabled:
   ```typescript
   console.log(organizationData?.enabled_modules);
   ```

2. Submodule enabled (if applicable):
   ```typescript
   console.log(organizationData?.enabled_modules?.master_data?.submodules);
   ```

3. User has permission:
   ```typescript
   console.log(userPermissions?.permissions);
   ```

## API Endpoints

### Get Organization Modules
```http
GET /api/v1/organizations/{organization_id}/modules
```

**Response**:
```json
{
  "enabled_modules": {
    "master_data": true,
    "inventory": true,
    "finance": true,
    "sales": true,
    "crm": true,
    "hr": true,
    "service": false,
    "manufacturing": false,
    "reportsAnalytics": true,
    "settings": true
  }
}
```

### Update Organization Modules
```http
PUT /api/v1/organizations/{organization_id}/modules
Content-Type: application/json

{
  "enabled_modules": {
    "master_data": true,
    "inventory": true,
    ...
  }
}
```

**Permissions Required**:
- `organization_module.update` permission
- User must be org_admin or super_admin

### Get User Permissions
```http
GET /api/v1/rbac/users/{user_id}/permissions
```

**Response**:
```json
{
  "user_id": 123,
  "permissions": ["master_data.view", "inventory.read", ...],
  "service_roles": [...],
  "total_permissions": 45
}
```

**Note**: This endpoint has resilient error handling. On failure, it returns:
```json
{
  "user_id": 123,
  "permissions": [],
  "service_roles": [],
  "total_permissions": 0,
  "error": "Failed to fetch permissions",
  "fallback": true
}
```

## Testing Module Visibility

### Test with Modules Enabled
```typescript
// Enable all modules
const testModules = {
  master_data: true,
  inventory: true,
  finance: true,
  // ...
};

// Update organization
await organizationService.updateModules(orgId, { enabled_modules: testModules });

// Verify menu shows all items
```

### Test with Modules Disabled
```typescript
// Disable specific module
const testModules = {
  master_data: true,
  inventory: false,  // Disabled
  // ...
};

// Update organization
await organizationService.updateModules(orgId, { enabled_modules: testModules });

// Verify inventory menu items are hidden
```

## Security Considerations

1. **Module enablement does NOT grant permissions** - it only controls UI visibility
2. Backend endpoints still enforce RBAC permissions regardless of module enablement
3. Super admin bypasses both module and permission checks
4. Organization isolation enforced at the database query level

## Default Module Configuration

New organizations are created with the following default modules enabled:

```python
def get_default_enabled_modules():
    return {
        "master_data": True,
        "inventory": True,
        "finance": True,
        "sales": True,
        "crm": True,
        "hr": True,
        "service": True,
        "manufacturing": False,  # Advanced feature
        "reportsAnalytics": True,
        "settings": True,
    }
```

## Related Files

### Backend
- `app/api/v1/organizations/module_routes.py` - Module management endpoints
- `app/core/modules_registry.py` - Module definitions and defaults
- `app/core/tenant.py` - Organization context management
- `app/core/enforcement.py` - Permission enforcement

### Frontend
- `frontend/src/components/MegaMenu.tsx` - Main menu component
- `frontend/src/components/menuConfig.tsx` - Menu structure and module mappings
- `frontend/src/context/AuthContext.tsx` - Authentication and permission context
- `frontend/src/services/organizationService.ts` - Organization API client
- `frontend/src/services/rbacService.ts` - RBAC API client

## Changelog

### 2025-10-29 - Organization Context Fix
- Fixed "No current organization specified" error for super_admin
- Modified `require_current_organization_id` to return `Optional[int]`
- Super_admin can now access organization-scoped endpoints without prior context
- Organization ID extracted from path parameters in endpoint handlers
- Maintained backward compatibility for regular users
- Added comprehensive tests for tenant context handling

---

For questions or issues, please refer to the main documentation or contact the development team.
