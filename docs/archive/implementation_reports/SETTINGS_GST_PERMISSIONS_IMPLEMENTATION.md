# Settings & GST Permissions Overhaul Implementation Guide

## Overview
This document describes the implementation of comprehensive RBAC and entitlement fixes for the main branch, addressing GST search permissions, settings visibility restrictions, voucher settings controls, management-level access, and user CRUD operations.

## Changes Implemented

### 1. GST Search Permissions

#### Backend Changes
- **File**: `app/api/v1/gst_search.py`
- GST search endpoint already uses `require_access("gst", "read")` for permission checking
- Added comprehensive audit logging for all GST lookups
- Audit logs capture:
  - User performing the search
  - GST number searched
  - Success/failure status
  - API response details
  - Cache hits

#### Permissions Added
- `gst_read`: Read GST data permission
- `gst_view`: View GST lookup interface
- `gst_search`: Perform GST number searches

#### Role Access
- ✅ **org_admin**: Full GST search access
- ✅ **management**: Full GST search access (same as org_admin)
- ❌ **manager**: No GST access by default (can be granted)
- ❌ **executive**: No GST access by default (can be granted)

### 2. General Settings Visibility

#### Backend Changes
- **File**: `app/api/v1/organizations/settings_routes.py`
- Settings endpoints use `require_access("settings", "read")` and `require_access("settings", "update")`
- RBAC enforcement automatically restricts based on role permissions

#### Frontend Changes
- **File**: `frontend/src/components/menuConfig.tsx`
  - Added `orgAdminOnly: true` flag to General Settings menu item
  - Only org_admin and super_admin users see this menu item

- **File**: `frontend/src/components/MegaMenu.tsx`
  - Added support for `orgAdminOnly` flag in menu filtering
  - Filters out org_admin-only items for non-admin users

#### Role Access
- ✅ **org_admin**: Full access to General Settings
- ❌ **management**: No access to General Settings page
- ❌ **manager**: No access to General Settings page
- ❌ **executive**: No access to General Settings page

### 3. Voucher Settings Restrictions

#### Backend Changes
- **File**: `app/api/v1/organizations/settings_routes.py`
- Added role-based field filtering in the settings update endpoint
- Restricted fields: `voucher_prefix`, `voucher_prefix_enabled`, `voucher_counter_reset_period`
- Non-org_admin users attempting to update these fields:
  - Fields are silently removed from the update
  - If no other fields remain, returns 403 error with clear message

#### Frontend Changes
- **File**: `frontend/src/pages/settings/voucher-settings.tsx`
- Added `useAuth` hook to get current user role
- Conditionally render voucher prefix and counter reset period fields:
  - **org_admin**: Full edit controls
  - **non-org_admin**: Read-only info alerts showing current values

#### Role Access for Restricted Fields
- ✅ **org_admin**: Can edit voucher prefix and counter reset period
- ❌ **management**: Cannot edit (read-only display)
- ❌ **manager**: Cannot edit (read-only display)
- ❌ **executive**: Cannot edit (read-only display)

#### Role Access for Other Voucher Settings
- ✅ **org_admin**: Full access
- ✅ **management**: Can edit terms & conditions, format templates
- ✅ **manager**: Can view settings
- ❌ **executive**: Limited view access

### 4. Management Role Access

#### Permissions Granted to Management
The management role now has comprehensive access to all modules except admin-only features:

**Full Access Modules:**
- CRM (leads, contacts, opportunities)
- ERP (ledger, vouchers, accounting)
- Inventory (products, stock)
- HR (employees, attendance, payroll)
- Manufacturing (orders, BOM)
- Service (tickets, SLA)
- Analytics (reports, dashboards)
- Email (accounts, messages)
- GST (search, validation)

**Restricted Modules:**
- General Settings (org_admin only)
- Voucher Prefix/Counter (org_admin only)
- Factory Reset (super_admin only)
- License Management (super_admin only)
- Organization Management (super_admin only)

#### Migration Script
- **File**: `migrations/versions/20251104_01_fix_gst_settings_permissions.py`
- Seeds all necessary permissions
- Grants permissions to existing roles in all organizations
- Idempotent - safe to run multiple times

### 5. User CRUD Operations

#### Backend Changes
- **File**: `app/api/v1/org_user_management.py`

**New Endpoint**: `DELETE /api/v1/org-users/users/{user_id}`

#### Deletion Rules
1. **org_admin** can delete:
   - ✅ Managers
   - ✅ Executives
   - ✅ Management
   - ❌ Themselves (self-deletion blocked)
   - ❌ Super admins

2. **management** can delete:
   - ✅ Managers
   - ✅ Executives
   - ❌ org_admin
   - ❌ Themselves
   - ❌ Super admins

3. **manager** can delete:
   - ✅ Executives reporting to them
   - ❌ Other managers
   - ❌ Themselves

#### Audit Logging
- **User Creation**: Logs who created the user, role, organization
- **User Deletion**: Logs who deleted the user, target role, reason
- Metadata includes full context for compliance

### 6. Audit Logging

#### GST Search Audit
Captures:
- User ID and email
- Organization ID
- GST number searched
- Search result (success/failure)
- Data source (API/cache/fallback)
- Timestamp

#### User Management Audit
Captures:
- Action (create/delete)
- Actor (who performed the action)
- Target user details
- Roles involved
- Timestamp
- Status

## Database Migration

### Running the Migration
```bash
# Using Alembic
alembic upgrade head

# Or directly
python -m alembic upgrade 20251104_01_fix_perms
```

### What the Migration Does
1. Creates 25+ new permissions for GST, settings, and user management
2. Updates existing permissions with proper module/action metadata
3. Grants permissions to org_admin roles (all permissions)
4. Grants permissions to management roles (all except admin-only)
5. Grants limited permissions to manager roles (read/view only)

### Verification
After running the migration, verify:
```sql
-- Check GST permissions exist
SELECT * FROM service_permissions WHERE module = 'gst';

-- Check org_admin has all permissions
SELECT COUNT(*) FROM service_role_permissions srp
JOIN service_roles sr ON srp.role_id = sr.id
WHERE sr.name = 'org_admin' AND sr.organization_id = YOUR_ORG_ID;

-- Check management has correct permissions
SELECT sp.name FROM service_role_permissions srp
JOIN service_roles sr ON srp.role_id = sr.id
JOIN service_permissions sp ON srp.permission_id = sp.id
WHERE sr.name = 'management' AND sr.organization_id = YOUR_ORG_ID;
```

## Testing

### Test Files
- `tests/test_settings_permissions_overhaul.py`: Comprehensive test suite

### Test Coverage
1. **GST Permissions**
   - org_admin can search GST
   - management can search GST
   - executive cannot search GST (no permission)

2. **Voucher Settings Restrictions**
   - org_admin can update prefix/counter
   - management cannot update prefix/counter
   - management can update other settings

3. **User CRUD Operations**
   - org_admin create/delete users
   - management create/delete allowed users
   - Self-deletion blocked
   - Super admin deletion blocked

4. **Permission Seeding**
   - Verify permissions exist in database
   - Verify correct role assignments

### Running Tests
```bash
# Run all tests
pytest tests/test_settings_permissions_overhaul.py -v

# Run specific test class
pytest tests/test_settings_permissions_overhaul.py::TestGSTPermissions -v

# Run with coverage
pytest tests/test_settings_permissions_overhaul.py --cov=app --cov-report=html
```

## Security Considerations

### 1. Defense in Depth
- **Frontend**: Menu items hidden, fields disabled
- **Backend**: Permission checks enforce access
- **Database**: Role-based permissions required

### 2. Audit Trail
- All sensitive operations logged
- Immutable audit records
- Compliance-ready logging format

### 3. Principle of Least Privilege
- Management role has broad but not complete access
- Specific admin operations restricted to org_admin
- Executive/manager roles further restricted

### 4. Self-Service Prevention
- Users cannot delete themselves
- Users cannot elevate their own permissions
- Admin users cannot be deleted by non-admins

## Frontend User Experience

### For org_admin Users
- See all menu items including General Settings
- Can edit all voucher settings including prefix and counter
- Can create and delete any non-admin users
- Full system access

### For management Users
- Cannot see General Settings menu item
- Can view but not edit voucher prefix/counter (shows current value)
- Can edit other voucher settings (terms, templates)
- Can create managers and executives
- Can delete managers and executives
- Full module access except admin features

### For manager Users
- Cannot see General Settings
- Can view voucher settings but not edit restricted fields
- Can create executives under their management
- Can delete executives under their management
- Module access based on assigned modules

### For executive Users
- Cannot see admin or settings menus
- Read-only access to assigned submodules
- Cannot perform user management
- Limited access based on role configuration

## API Documentation

### GST Search
```http
GET /api/v1/gst/search/{gst_number}
Authorization: Bearer <token>

Response: GSTDetails
{
  "name": "Company Name",
  "gst_number": "27AABCU9603R1ZM",
  "address1": "123 Street",
  "city": "Mumbai",
  "state": "Maharashtra",
  "pin_code": "400001",
  "pan_number": "AABCU9603R",
  "state_code": "27"
}
```

### Update Settings (org_admin only for restricted fields)
```http
PUT /api/v1/organizations/settings/
Authorization: Bearer <token>
Content-Type: application/json

{
  "voucher_prefix": "TEST",
  "voucher_prefix_enabled": true,
  "voucher_counter_reset_period": "annually"
}

Response 200: OrganizationSettings
Response 403: If non-org_admin tries to update restricted fields
```

### Delete User
```http
DELETE /api/v1/org-users/users/{user_id}
Authorization: Bearer <token>

Response 200:
{
  "message": "User deleted successfully",
  "deleted_user_id": 123,
  "deleted_user_email": "user@example.com"
}

Response 400: Cannot delete self
Response 403: Insufficient permissions
Response 404: User not found
```

## Troubleshooting

### Issue: GST Search Returns 403
**Cause**: User lacks `gst_read` permission
**Solution**: 
1. Run migration: `alembic upgrade head`
2. Verify user's role has permission
3. Check audit logs for details

### Issue: Management Cannot Access Modules
**Cause**: Permissions not seeded
**Solution**:
1. Run migration script
2. Verify service_role_permissions table
3. Check entitlement service for module access

### Issue: Voucher Prefix Still Editable by Management
**Cause**: Frontend not checking role properly
**Solution**:
1. Verify `useAuth()` hook returns correct role
2. Check `isOrgAdmin` logic
3. Clear browser cache
4. Verify backend also blocks the update

### Issue: Cannot Delete Users
**Cause**: Missing permission or validation error
**Solution**:
1. Check user is not trying to delete themselves
2. Verify target user is not super_admin
3. Confirm requester has permission to delete target role
4. Check audit logs for error details

## Rollback Procedure

If issues arise, rollback in this order:

1. **Database**: 
   ```bash
   alembic downgrade -1
   ```

2. **Code**: 
   ```bash
   git revert <commit-hash>
   git push origin main
   ```

3. **Verify**:
   - Check old permissions still work
   - Verify no broken functionality
   - Review audit logs

## Future Enhancements

1. **Granular Voucher Permissions**: Per-voucher-type prefix settings
2. **Role Templates**: Pre-configured permission sets
3. **Bulk User Operations**: Create/delete multiple users
4. **Advanced Audit**: Real-time audit dashboard
5. **Permission Inheritance**: Hierarchical role system

## Support

For issues or questions:
1. Check audit logs: `/api/v1/admin/audit-logs`
2. Review migration status: `alembic current`
3. Verify permissions: Query `service_role_permissions` table
4. Contact system administrator

## Version History

- **v1.0.0** (2025-11-04): Initial implementation
  - GST permissions added
  - Settings visibility restrictions
  - Voucher field restrictions
  - Management role full access
  - User CRUD operations
  - Comprehensive audit logging
