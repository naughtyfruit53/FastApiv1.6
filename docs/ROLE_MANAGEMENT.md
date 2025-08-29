# Role Management and Permissions

## Role Hierarchy

This document outlines the role management system and permission hierarchy in the application.

### User Roles

1. **SUPER_ADMIN** (`super_admin`)
   - Highest level access
   - Can manage all organizations and users across the platform
   - Can create new organization licenses
   - Platform-wide administrative privileges

2. **ORG_ADMIN** (`org_admin`)
   - Organization-level administrator
   - Can manage users within their organization
   - Can invite new users to their organization
   - Can create and manage multiple companies within the organization
   - Can assign users to companies and appoint company admins
   - Organization-scoped administrative privileges

3. **COMPANY_ADMIN** (`company_admin`)
   - Company-level administrator within an organization
   - Has all ORG_ADMIN rights but scoped to their assigned companies only
   - Can manage users within their companies
   - Can access company-specific data and features
   - Cannot create new companies or manage organization-level settings
   - Company-scoped administrative privileges

4. **ADMIN** (`admin`)
   - **DEPRECATED**: Use ORG_ADMIN instead for new implementations
   - Legacy role maintained for backward compatibility
   - Similar permissions to ORG_ADMIN but being phased out

5. **STANDARD_USER** (`standard_user`)
   - Regular user with basic access
   - Can access features within their organization
   - Must be assigned to specific companies to access company data
   - Cannot manage other users

## Permission Guidelines

### Role Standardization

- **Use `ORG_ADMIN`** consistently for organization-level administration
- **Avoid mixing** `ADMIN` and `ORG_ADMIN` in permission checks
- **Phase out** `ADMIN` role in favor of `ORG_ADMIN`

### Best Practices

1. **Single Role Check**: Use `current_user.role == UserRole.ORG_ADMIN` instead of checking multiple roles
2. **Consistent Naming**: Use ORG_ADMIN for organization administrators
3. **Clear Hierarchy**: Super Admin > Org Admin > Standard User

### Code Examples

#### Correct Permission Check
```python
# Good: Single, clear role check
if not current_user.is_super_admin and current_user.role != UserRole.ORG_ADMIN:
    raise HTTPException(status_code=403, detail="Insufficient permissions")
```

#### Deprecated Pattern
```python
# Avoid: Mixing roles
if current_user.role not in [UserRole.ORG_ADMIN, UserRole.ADMIN]:
    # This creates confusion and inconsistency
```

## Multi-Company Support

### Overview

The application supports multiple companies within a single organization. This feature allows organizations to:

- Create multiple companies based on their `max_companies` limit (set by app super admin)
- Assign users to one or more companies
- Appoint company admins who have organization admin rights within their company scope
- Maintain data isolation between companies while sharing organization-level resources

### Role Hierarchy in Multi-Company Context

```
App Super Admin (Platform Level)
└── Organization Admin (Organization Level)
    └── Company Admin (Company Level)
        └── Standard User (Company Level)
```

### Permission Inheritance

- **App Super Admin**: Full access to all organizations and companies
- **Organization Admin**: Full access to all companies within their organization
- **Company Admin**: Organization admin rights scoped to their assigned companies only
- **Standard User**: Basic access to assigned companies only

### Company-Scoped Permissions

Company admins inherit most organization admin permissions but with the following restrictions:

**Allowed for Company Admins:**
- Manage users within their companies
- Access company-specific data and features
- Invite users to their companies
- Manage company settings and configuration

**Restricted for Company Admins:**
- Cannot create new companies
- Cannot modify organization-level settings
- Cannot access other companies' data
- Cannot manage organization license or billing

### User-Company Assignment

Users can be assigned to multiple companies within an organization:

```python
# Check if user has access to a specific company
rbac_service.user_has_company_access(user_id, company_id)

# Check if user is admin of a specific company
rbac_service.user_is_company_admin(user_id, company_id)

# Enforce company access in API endpoints
rbac_service.enforce_company_access(user_id, company_id, permission_name)
```

### API Endpoints for Multi-Company Management

- `GET /companies/` - List all companies in organization
- `POST /companies/` - Create new company (checks max_companies limit)
- `GET /companies/{company_id}/users` - Get users assigned to company
- `POST /companies/{company_id}/users` - Assign user to company
- `PUT /companies/{company_id}/users/{user_id}` - Update user assignment (toggle admin)
- `DELETE /companies/{company_id}/users/{user_id}` - Remove user from company

## Migration Notes

When updating existing code:
1. Replace mixed role checks with single ORG_ADMIN checks
2. Update documentation to reflect ORG_ADMIN usage
3. Ensure existing ADMIN users are properly migrated to ORG_ADMIN role
4. Update frontend components to use consistent role display names