# New 4-Role Organization User Management System

## Overview

FastAPI v1.6 now implements a simplified, powerful 4-role organization user management system that replaces the previous complex RBAC setup.

## The Four Roles

### 1. Org Admin
- **Access Level**: Full access based on entitlement only
- **No RBAC**: Org Admins don't go through RBAC checks
- **Permissions**: Access to ALL modules that the organization is entitled to
- **Capabilities**:
  - Create all user roles including Management
  - Manage all organization settings
  - Access all entitled modules and submodules
  - Assign modules to Managers
  - Assign submodules to Executives

### 2. Management
- **Access Level**: Full owner-like access via RBAC
- **Exception**: Cannot create Org Admin users
- **Permissions**: Access to ALL entitled modules through RBAC
- **Capabilities**:
  - Manage Managers and Executives
  - Assign/edit module access for Managers
  - Assign/edit submodule access for Executives
  - Upgrade/downgrade roles (except to Org Admin)
  - Access all organization settings

### 3. Manager
- **Access Level**: Module-level access
- **Permissions**: Only to selected modules assigned at creation or by Org Admin/Management
- **Module Selection**: At creation/edit, Org Admin or Management selects which modules the Manager can access
- **Full Module Access**: Managers get complete data and action rights for assigned modules including all submodules
- **Capabilities**:
  - Create and manage Executives under their management
  - Assign submodules to their Executives (from their own module list)
  - Access settings for assigned modules only

### 4. Executive
- **Access Level**: Submodule-level access
- **Permissions**: Only to selected submodules of their Manager's modules
- **Submodule Selection**: At creation/edit, permitted submodules are selectable based on reporting Manager's role
- **Reporting Structure**: Each Executive has a reporting Manager
- **Upgrade Path**: Can be upgraded to Manager/Management by Org Admin, Management, or their reporting Manager
- **Capabilities**:
  - Work within assigned submodules only
  - No settings menu access
  - No user management capabilities

## Permission Model

### Module/Submodule Assignment = Full Rights

When a module or submodule is assigned to a user, they automatically receive **full permissions** for that scope:
- Read
- Create
- Edit
- Delete
- Export
- All other actions

No granular permission selection is needed - assignment = complete access for that scope.

## API Endpoints

### New Organization User Management API (`/api/v1/org/...`)

#### Create User
```
POST /api/v1/org/users
```
Creates a new organization user with role-based validation.

**Request Body:**
```json
{
  "email": "user@example.com",
  "full_name": "John Doe",
  "password": "SecurePass123!",
  "role": "manager",  // org_admin, management, manager, executive
  "department": "Sales",
  "designation": "Sales Manager",
  
  // For Manager role:
  "assigned_modules": {
    "CRM": true,
    "Sales": true,
    "Inventory": false
  },
  
  // For Executive role:
  "reporting_manager_id": 123,
  "sub_module_permissions": {
    "CRM": ["leads", "contacts"],
    "Sales": ["orders"]
  }
}
```

#### Get Available Modules
```
GET /api/v1/org/available-modules/{role}?manager_id=123
```
Returns available modules and submodules for a specific role.

#### Get User Permissions
```
GET /api/v1/org/users/{user_id}/permissions
```
Returns effective permissions for a user based on their role.

#### Update Manager Modules
```
PUT /api/v1/org/users/{user_id}/modules
```
Update module assignments for a Manager (Org Admin/Management only).

#### Update Executive Submodules
```
PUT /api/v1/org/users/{user_id}/submodules
```
Update submodule permissions for an Executive.

#### Get Managers List
```
GET /api/v1/org/managers
```
Get all managers in the organization (for Executive assignment).

### Settings Menu Visibility

```
GET /api/v1/settings/menu-visibility
```
Returns which settings menu items should be visible based on user role and entitlements.

**Response:**
```json
{
  "role": "manager",
  "visible_settings": {
    "CRM": true,
    "Sales": true,
    "Inventory": false,
    "HR": false
  }
}
```

## API Versioning

All API routes have been moved from `app/api/` to `app/api/v1/` for proper versioning:
- Base path: `/api/v1/`
- All routes now include version prefix
- Maintains backward compatibility during transition

### Migrated Routes:
- `/api/v1/companies/` (was `/api/companies/`)
- `/api/v1/customer-analytics/` (new)
- `/api/v1/management-reports/` (new)
- `/api/v1/notifications/` (new)
- `/api/v1/pincode/` (new)
- `/api/v1/platform/` (new)
- `/api/v1/settings/` (new)

## Services

### OrgRoleService
**Location**: `app/services/org_role_service.py`

Handles role-specific operations:
- Role transition validation
- Module/submodule availability calculation
- Module assignment to Managers
- Submodule assignment to Executives
- Effective permission calculation

### PermissionEnforcer
**Location**: `app/services/permission_enforcement.py`

Enforces permissions based on the 4-role system:
- Module access checking
- Submodule access checking
- Settings menu visibility
- User management authorization

## Database Migration

### Migration Script
**Location**: `migrations/versions/20251103_01_cleanup_legacy_roles.py`

This migration:
1. Maps legacy roles to new 4-role system:
   - `admin` → `org_admin`
   - `crm_admin`, `service_admin` → `management`
   - `crm_manager`, `service_manager` → `manager`
   - `crm_executive`, `service_executive`, `user`, `staff` → `executive`

2. Removes legacy service roles not in the 4-role system
3. Cleans up module-specific permissions
4. Updates all users to valid roles

**To run:**
```bash
alembic upgrade head
```

## User Creation Flow

### For Org Admin:
1. Select role: org_admin, management, manager, or executive
2. Enter basic information
3. For Manager: Select modules from entitled list
4. For Executive: Select reporting manager, then select submodules from manager's modules
5. User created with appropriate permissions

### For Management:
1. Select role: management, manager, or executive (cannot create org_admin)
2. Same as Org Admin flow for other roles

### For Manager:
1. Can only create: executive
2. Select from their own module list for submodule assignment
3. Executive automatically reports to this Manager

## Settings Menu Logic

### Visibility Rules:

**Org Admin:**
- Sees all settings for entitled modules
- Based purely on entitlement

**Management:**
- Sees all settings for entitled modules
- Via RBAC access

**Manager:**
- Sees settings only for assigned modules
- No access to settings for unassigned modules

**Executive:**
- No settings menu access
- Cannot configure any system settings

## Role Hierarchy and Upgrade Paths

```
Org Admin (Organization Owner)
    ↓ can create
Management (Full RBAC Access)
    ↓ can create
Manager (Module-level Access)
    ↓ can create
Executive (Submodule-level Access)
```

### Upgrade Paths:
- **Executive → Manager**: By Org Admin, Management, or reporting Manager
- **Executive → Management**: By Org Admin or Management
- **Manager → Management**: By Org Admin or Management
- **Any → Org Admin**: Only by existing Org Admin

### Downgrade Rules:
- Any role can be downgraded by higher roles
- Org Admin can downgrade anyone except other Org Admins
- Management can downgrade Managers and Executives

## Security Considerations

1. **Role Validation**: All role transitions are validated before execution
2. **Module Entitlement**: Module assignments are validated against organization entitlements
3. **Hierarchy Enforcement**: Users can only manage users below them in hierarchy
4. **No RBAC for Org Admin**: Org Admin bypasses RBAC for performance and simplicity
5. **Supabase Integration**: User creation includes Supabase auth with rollback on failure

## Testing

### Unit Tests:
Create tests for:
- Role validation logic
- Module/submodule assignment
- Permission checking
- Settings visibility
- User creation with different roles

### Integration Tests:
Test:
- Complete user creation flow
- Module assignment and access
- Submodule assignment and access
- Settings menu visibility API
- Role upgrade/downgrade

## Migration Path from Old System

1. **Run migration script**: Maps old roles to new roles
2. **Verify user roles**: Check that all users have valid roles
3. **Assign modules**: For Managers, assign modules based on previous access
4. **Assign reporting managers**: For Executives, set reporting managers
5. **Test access**: Verify users can access appropriate modules/submodules

## Frontend Integration

### User Creation Component:
```javascript
// Hierarchical module/submodule selection
// Role-based field visibility
// Reporting manager dropdown for Executives
// Real-time module availability based on role
```

### Settings Menu:
```javascript
// Fetch visibility from /api/v1/settings/menu-visibility
// Show/hide menu items based on response
// Role badge display
```

## Summary of Changes

1. ✅ Updated User model with new role documentation
2. ✅ Updated UserRole enum with role descriptions
3. ✅ Created OrgRoleService for role management
4. ✅ Created PermissionEnforcer for permission checking
5. ✅ Created org_user_management API endpoints
6. ✅ Moved all API files to v1/ directory
7. ✅ Updated settings API with menu visibility endpoint
8. ✅ Created migration script for legacy cleanup
9. ✅ Updated main.py for v1 routing

## Next Steps

1. Run database migration
2. Test user creation with all roles
3. Verify permission enforcement
4. Test settings menu visibility
5. Update frontend components
6. Deploy to staging environment
7. Perform end-to-end testing
