# Authentication and Role/Permission Foundation Implementation

This document outlines the unified authentication and role/permission foundation that establishes robust authentication, session, and role enforcement using the unified multi-tenancy foundation.

## 🎯 Overview

The authentication system has been enhanced to provide:
- **Unified JWT Token Structure**: Tokens now encode `user_role`, `user_type`, and `organization_id`
- **Comprehensive Permission System**: Role-based permissions with decorators for all endpoints
- **Frontend Consistency**: Organization ID handling and user role management
- **Backward Compatibility**: Super Admins with `organization_id=None` remain fully functional

## 🔧 Implementation Details

### 1. Enhanced JWT Token System

#### JWT Token Structure
```json
{
  "sub": "user@example.com",
  "organization_id": 123,
  "user_role": "org_admin", 
  "user_type": "organization",
  "exp": 1640995200
}
```

#### Token Creation (Backend)
```python
from app.core.security import create_access_token

token = create_access_token(
    subject=user.email,
    organization_id=user.organization_id,
    user_role=user.role,
    user_type="platform" if user.is_platform_user else "organization"
)
```

#### Token Verification (Backend)
```python
from app.core.security import verify_token

email, org_id, user_role, user_type = verify_token(token)
```

### 2. Permission System Integration

#### Role-Based Permissions
The system defines granular permissions for each user role:

- **SUPER_ADMIN**: Full platform access, can manage all organizations
- **ORG_ADMIN**: Manage users within organization, reset org data  
- **ADMIN**: View and create users, access org settings
- **STANDARD_USER**: Basic access, reset own password

#### Permission Decorators (Backend)
```python
from app.core.permissions import PermissionChecker, Permission

# In API endpoints
@router.get("/users/")
async def get_users(
    current_user: User = Depends(get_current_active_user),
    request: Request = None,
    db: Session = Depends(get_db)
):
    # Check permissions
    PermissionChecker.require_permission(Permission.VIEW_USERS, current_user, db, request)
    # ... endpoint logic
```

#### Available Permissions
- `Permission.MANAGE_USERS` - Create, update, delete users
- `Permission.VIEW_USERS` - View user information
- `Permission.CREATE_USERS` - Create new users
- `Permission.VIEW_ORGANIZATIONS` - View organization data
- `Permission.MANAGE_ORGANIZATIONS` - Full organization management
- `Permission.SUPER_ADMIN` - Platform-level super admin access

### 3. Frontend Authentication Updates

#### Enhanced authService
```typescript
// Login now stores complete authentication context
const loginResponse = await authService.loginWithEmail(email, password);

// Stored in localStorage:
// - token
// - organization_id  
// - user_role
// - is_super_admin
```

#### Permission Utilities (Frontend)
```typescript
import { canManageUsers, canViewOrganizations } from '../types/user.types';

// Check permissions in components
if (canManageUsers(user)) {
  // Show user management UI
}

if (canViewOrganizations(user)) {
  // Show organization management UI
}
```

#### API Client Organization Headers
```typescript
// API client automatically sends organization headers
headers: {
  'Authorization': `Bearer ${token}`,
  'X-Organization-ID': organizationId  // Consistent naming
}
```

## 🔄 Migration Guide

### For Existing Deployments

#### 1. Backend Changes
- **JWT Tokens**: Existing tokens remain valid but lack new fields
- **Permission Endpoints**: All user and organization management endpoints now use permission system
- **Backward Compatibility**: Super admin functionality unchanged

#### 2. Frontend Changes  
- **localStorage**: Frontend now stores `user_role` in addition to existing fields
- **API Headers**: `X-Organization-ID` header consistently used instead of legacy `orgId`
- **Permission Checks**: UI components should use new permission utility functions

#### 3. Required Updates
For client applications using the API:

1. **Update API clients** to handle enhanced login response:
```json
{
  "access_token": "jwt-token",
  "token_type": "bearer", 
  "organization_id": 123,
  "user_role": "org_admin",
  "must_change_password": false,
  "user": { /* user object */ }
}
```

2. **Update permission checks** to use granular permission system instead of hardcoded role strings

3. **Update organization header** from `orgId` to `organization_id` in API requests

## 🧪 Testing

### Authentication Tests
```bash
# Run authentication and permission tests
cd v1.1
python test_auth_enhanced.py
```

### Permission System Tests  
```bash
# Test permission system logic
python test_permissions_standalone.py
```

### Integration Tests
The following test scenarios are covered:
- JWT token creation and verification with all fields
- Platform user vs organization user authentication
- Backward compatibility with legacy tokens
- Role-based permission mapping
- Organization access validation

## 🚀 Benefits

### 1. Enhanced Security
- **Granular Permissions**: Fine-grained access control based on specific permissions
- **Organization Isolation**: Strong enforcement of multi-tenant boundaries
- **Audit Trail**: Permission denials are logged with full context

### 2. Improved Maintainability
- **Consistent Permission Checks**: Centralized permission logic across all endpoints
- **Clear Role Definitions**: Standardized user roles with explicit capabilities
- **Type Safety**: Frontend permission utilities provide consistent checking

### 3. Better User Experience
- **Rich Authentication Context**: Login responses include all necessary user information
- **Consistent UI Behavior**: Permission-based UI rendering across all components
- **Session Management**: Complete authentication state management

## 🔒 Security Considerations

### Token Security
- JWT tokens include minimal necessary information
- Organization context prevents cross-tenant access
- Super admin tokens are clearly identified

### Permission Enforcement
- All sensitive endpoints protected by permission decorators
- Organization access validation on every request
- Failed permission attempts are audited

### Backward Compatibility
- Legacy super admin users (`organization_id=None`) retain full access
- Existing JWT tokens without new fields continue to work
- Gradual migration path for existing implementations

## 📋 Validation Checklist

- [x] JWT tokens encode `user_role` and `user_type`
- [x] Permission system integrated into user management endpoints
- [x] Organization management endpoints use permission decorators
- [x] Frontend stores and uses `user_role` consistently
- [x] API client uses `organization_id` header naming
- [x] Permission utility functions available for frontend
- [x] Backward compatibility maintained for super admins
- [x] Test suite covers authentication and permission scenarios
- [x] Migration documentation provided

## 🔮 Future Enhancements

1. **Dynamic Permissions**: Database-driven permission assignments
2. **Permission Caching**: Redis-based permission caching for performance
3. **Audit Dashboard**: UI for viewing permission audit logs
4. **Role Templates**: Predefined permission sets for common role types
5. **Multi-Factor Authentication**: Enhanced security for admin users

This authentication and permission foundation provides a robust, scalable base for the multi-tenant FastAPI application while maintaining full backward compatibility.