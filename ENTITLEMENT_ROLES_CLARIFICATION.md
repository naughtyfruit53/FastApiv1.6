# Entitlement Management - Role Clarification

## Overview

This document clarifies the roles and responsibilities in the entitlement management system to avoid confusion between different types of administrators.

## Role Hierarchy

### 1. App Super Admin (Platform Administrator)
**Scope**: Entire platform across all organizations

**Responsibilities**:
- Manage organization entitlements (activate/deactivate modules and categories)
- Control licensing and billing for organizations
- View all organizations and their entitlements
- Audit entitlement changes across the platform
- Set trial periods and expiration dates
- Manage platform-level settings

**Entitlement Powers**:
- ✅ Can activate/deactivate entire product categories for organizations
- ✅ Can enable/disable individual modules for organizations
- ✅ Can enable/disable individual submodules for organizations
- ✅ Can set trial periods and manage license types
- ✅ Can override all entitlement restrictions

**API Endpoints**:
- `POST /api/v1/admin/categories/orgs/{org_id}/activate`
- `POST /api/v1/admin/categories/orgs/{org_id}/deactivate`
- `GET /api/v1/admin/categories`
- `GET /api/v1/admin/categories/{category}`
- `GET /api/v1/admin/modules`
- `PUT /api/v1/admin/orgs/{org_id}/entitlements`
- `GET /api/v1/admin/orgs/{org_id}/entitlements`

### 2. Org Admin (Organization Administrator)
**Scope**: Single organization

**Responsibilities**:
- Manage users within their organization
- Configure organization settings
- Access all features that the organization is entitled to
- Manage data and operations within entitled modules
- View organization's active entitlements

**Entitlement Powers**:
- ❌ **Cannot** activate/deactivate modules or categories
- ❌ **Cannot** change licensing or billing settings
- ✅ Can view what entitlements their organization has
- ✅ Can work within all entitled modules
- ✅ Automatically gets access when super admin activates modules

**API Endpoints**:
- `GET /api/v1/orgs/{org_id}/entitlements` (read-only view)

### 3. Management (Organization Management Role)
**Scope**: Single organization

**Responsibilities**:
- Similar to Org Admin but cannot create other Org Admins
- Manage other users (Managers and Executives)
- Access entitled modules based on RBAC permissions

**Entitlement Powers**:
- ❌ **Cannot** activate/deactivate modules or categories
- ✅ Can view organization's entitlements
- ✅ Can work within entitled modules (subject to RBAC)

### 4. Manager & Executive
**Scope**: Single organization, limited module access

**Responsibilities**:
- Work within assigned modules/submodules
- Perform day-to-day operations

**Entitlement Powers**:
- ❌ **Cannot** view or manage entitlements
- ✅ Can access only their assigned modules (which must be entitled)

## Entitlement Workflow

### Step 1: Super Admin Grants Entitlements
```
App Super Admin → Activates "CRM Suite" category for Organization A
                ↓
System → Enables all CRM modules (crm, sales, marketing, seo)
       ↓
System → Updates organization's enabled_modules
       ↓
System → Invalidates entitlement cache
```

### Step 2: Org Admin Gets Access
```
Org Admin logs in to Organization A
         ↓
System checks entitlements → CRM Suite is enabled
         ↓
Org Admin sees → CRM, Sales, Marketing, SEO menus
         ↓
Org Admin can → Access all features in these modules
```

### Step 3: Org Admin Manages Users
```
Org Admin → Creates Manager with "CRM" module access
          ↓
Manager logs in → Only sees CRM module (if entitled)
          ↓
Manager → Can work within CRM features
```

## Key Distinctions

### Module Activation vs Module Assignment

| Operation | Who Can Do It | What It Does |
|-----------|---------------|--------------|
| **Module Activation** | App Super Admin | Grants organization access to a module (licensing) |
| **Module Assignment** | Org Admin / Management | Assigns activated modules to individual users (RBAC) |

### Example Scenario

**Scenario**: Organization wants CRM features

❌ **Wrong Approach**:
- Org Admin tries to activate CRM module
- System denies - insufficient permissions

✅ **Correct Approach**:
1. Org Admin contacts support or purchases CRM license
2. App Super Admin activates "CRM Suite" category for the organization
3. CRM modules instantly become available to the organization
4. Org Admin can now access CRM features and assign them to users

## API Access Control

### Admin Category Endpoints (Super Admin Only)

All endpoints under `/api/v1/admin/categories/` require **super_admin** role:

```python
@router.post("/orgs/{org_id}/activate")
async def activate_category_for_org(
    org_id: int,
    request: ActivateCategoryRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_super_admin)  # ← Super admin required
):
```

### Organization Entitlements Endpoints (Read-Only for Org Admin)

Endpoint under `/api/v1/orgs/{org_id}/entitlements` is read-only:

```python
@router.get("/{org_id}/entitlements")
async def get_app_entitlements(
    org_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)  # ← Org admin can view
):
    # Returns current entitlements (read-only)
```

## Security Considerations

### Entitlement Checks
1. **First**: System checks if module is entitled to the organization
2. **Second**: System checks if user has RBAC permissions for the module
3. **Result**: User must pass both checks to access features

### Bypass Rules
- **Super Admin**: Can bypass entitlement checks (with audit logging)
- **Always-On Modules**: Email module bypasses entitlement checks
- **RBAC-Only Modules**: Settings/Admin modules bypass entitlement checks

## Documentation References

### For App Super Admins
- Module Categories: `MODULE_CATEGORIES.md`
- Admin Category API: `app/api/v1/admin_categories.py`
- Entitlement Service: `app/services/entitlement_service.py`

### For Org Admins
- User Management: `NEW_ROLE_SYSTEM_DOCUMENTATION.md`
- Organization Settings: Organization settings API documentation
- Entitlement Viewing: Read-only access via app entitlements endpoint

### For Developers
- Entitlement Architecture: `ENTITLEMENTS_IMPLEMENTATION_SUMMARY.md`
- RBAC Implementation: `RBAC_COMPREHENSIVE_GUIDE.md`
- Module Categories: `app/core/module_categories.py`

## Common Questions

**Q: Can an Org Admin activate additional modules for their organization?**
A: No. Only App Super Admin can activate modules. This is a licensing/billing operation.

**Q: How does an organization get new modules?**
A: They must purchase or request access, then App Super Admin activates the modules.

**Q: Can an Org Admin see which modules are available but not activated?**
A: They can see what's activated. To see available modules, they need to contact support.

**Q: What happens if a Manager is assigned a module that's not entitled?**
A: The assignment will be saved, but the Manager won't be able to access the module until it's entitled to the organization.

**Q: Can a super admin remove entitlements?**
A: Yes, using the deactivate category/module endpoints. This should be done carefully as it removes access for the entire organization.

## Best Practices

### For Super Admins
1. **Document reasons**: Always provide clear reasons when activating/deactivating categories
2. **Communicate changes**: Notify organization admins before removing entitlements
3. **Use categories**: Prefer category-based activation for cleaner licensing
4. **Monitor usage**: Track entitlement events for billing and auditing

### For Org Admins
1. **Check entitlements first**: Before assigning modules to users, ensure they're entitled
2. **Plan purchases**: Review MODULE_CATEGORIES.md to plan what features to purchase
3. **Train users**: Ensure users understand which features they have access to
4. **Request features**: Contact support to request additional module activations

### For Developers
1. **Always check entitlements**: Use entitlement dependencies in API endpoints
2. **Handle denied access gracefully**: Return clear error messages
3. **Cache wisely**: Invalidate cache when entitlements change
4. **Log access attempts**: Maintain audit trail for security

---

**Last Updated**: 2024-11-03
**Version**: 1.0.0
**Status**: Active
