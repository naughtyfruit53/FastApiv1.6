# RBAC & Organization Management Improvements

## Overview
This document describes the improvements made to the RBAC (Role-Based Access Control) system and organization management components to enhance enum validation, error handling, and role filtering.

## Changes Made

### 1. Frontend React Hook Fixes (`frontend/src/pages/admin/manage-organizations.tsx`)

**Problem**: React hooks were being called conditionally, causing "hook mismatch" runtime errors.

**Solution**:
- Removed unused `availableModules` state variable
- Moved early return (error check) to after all hook calls
- Fixed undefined variable references in `console.error` statements (changed `msg` to proper error messages)

**Impact**: Eliminates React hook mismatch errors and improves error logging clarity.

### 2. Backend RBAC Enum Validation (`app/api/v1/rbac.py`)

**Problem**: No validation of ServiceRoleType enum values when creating or updating roles, leading to potential invalid data in the database.

**Solution**:
Added enum validation in `create_service_role()` endpoint:
```python
try:
    from app.schemas.rbac import ServiceRoleType
    ServiceRoleType(role.name)  # Validates the enum value
except ValueError:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"Invalid role type '{role.name}'. Must be one of: admin, manager, support, viewer"
    )
```

**Impact**: Prevents invalid role types from being created, provides clear error messages to API consumers.

### 3. Backend Error Handling (`app/api/v1/rbac.py`)

**Problem**: Insufficient error handling and logging in RBAC endpoints, making debugging difficult and providing poor user experience.

**Solution**:
Added comprehensive try-catch blocks with proper logging to all RBAC endpoints:
- `get_organization_roles()`
- `create_service_role()`
- `get_service_role()`
- `update_service_role()`
- `delete_service_role()`
- `initialize_default_roles()`
- `assign_roles_to_user()`
- `remove_role_from_user()`

Each endpoint now:
- Logs errors with stack traces using `logger.error(..., exc_info=True)`
- Returns appropriate HTTP status codes (400 for validation, 404 for not found, 500 for server errors)
- Provides meaningful error messages to the frontend
- Distinguishes between HTTPException (re-raise) and general exceptions

**Impact**: 
- Better debugging through comprehensive logging
- Improved user experience with clear error messages
- Prevents network errors from crashing the application

### 4. Frontend Role Filtering (`frontend/src/services/rbacService.ts`)

**Problem**: No centralized role filtering logic for organization settings and user management.

**Solution**:
Added three new functions to `rbacService`:

1. **`filterRolesForAssignment()`**: Filters roles by organization and active status
   ```typescript
   filterRolesForAssignment(
     roles: ServiceRole[],
     organizationId: number,
     onlyActive: boolean = true
   ): ServiceRole[]
   ```

2. **`getAssignableRoles()`**: Fetches and filters roles for a specific organization
   ```typescript
   getAssignableRoles(
     organizationId: number,
     options?: {
       includeInactive?: boolean;
       currentUserOrgId?: number;
     }
   ): Promise<ServiceRole[]>
   ```

**Impact**:
- Ensures only organization-scoped roles are shown in user management
- Filters out inactive roles by default
- Provides reusable filtering logic across the application
- Prevents cross-organization role assignments

### 5. Testing (`tests/test_rbac_enum_validation.py`)

**New Test File**: Comprehensive tests for enum validation:
- Tests valid ServiceRoleType enum values
- Tests invalid enum values raise ValueError
- Tests enum validation error messages
- Tests case sensitivity of enum values
- Tests all expected ServiceRoleType values are defined

**Impact**: Ensures enum validation logic works correctly and prevents regressions.

## Valid ServiceRoleType Values

The following are the only valid values for ServiceRoleType:
- `admin` - Full administrative access
- `manager` - Management access with reporting capabilities
- `support` - Operational access to service tickets and tasks
- `viewer` - Read-only access to service CRM data

## API Error Responses

### 400 Bad Request
Returned when invalid enum values are provided:
```json
{
  "detail": "Invalid role type 'invalid_role'. Must be one of: admin, manager, support, viewer"
}
```

### 404 Not Found
Returned when role or resource doesn't exist:
```json
{
  "detail": "Role not found"
}
```

### 500 Internal Server Error
Returned when unexpected errors occur:
```json
{
  "detail": "Failed to create role: [error message]"
}
```

## Usage Examples

### Creating a Role with Validation
```typescript
import { rbacService } from './services/rbacService';

try {
  const role = await rbacService.createRole(organizationId, {
    name: 'admin',  // Must be valid ServiceRoleType
    display_name: 'Administrator',
    description: 'Full access',
    is_active: true,
  });
} catch (error) {
  // Will receive clear error message if invalid role type
  console.error(error.message);
}
```

### Filtering Roles for Assignment
```typescript
import { rbacService } from './services/rbacService';

// Get only assignable roles for current organization
const assignableRoles = await rbacService.getAssignableRoles(
  organizationId,
  { includeInactive: false }
);

// Or filter existing roles
const filtered = rbacService.filterRolesForAssignment(
  allRoles,
  organizationId,
  true  // Only active roles
);
```

## Best Practices

1. **Always validate role types**: Use the ServiceRoleType enum when creating or updating roles
2. **Handle errors gracefully**: Wrap RBAC operations in try-catch blocks
3. **Use filtered role lists**: Always use `getAssignableRoles()` or `filterRolesForAssignment()` when showing roles in UI
4. **Check organization context**: Ensure users can only manage roles within their organization
5. **Log errors properly**: Use structured logging with proper log levels

## Future Improvements

- Add role hierarchy validation (e.g., managers can't assign admin roles)
- Implement audit logging for role changes
- Add bulk role assignment validation
- Create role templates for common use cases
- Add role permission conflict detection
