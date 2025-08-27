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
   - Organization-scoped administrative privileges

3. **ADMIN** (`admin`)
   - **DEPRECATED**: Use ORG_ADMIN instead for new implementations
   - Legacy role maintained for backward compatibility
   - Similar permissions to ORG_ADMIN but being phased out

4. **STANDARD_USER** (`standard_user`)
   - Regular user with basic access
   - Can access features within their organization
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

## Migration Notes

When updating existing code:
1. Replace mixed role checks with single ORG_ADMIN checks
2. Update documentation to reflect ORG_ADMIN usage
3. Ensure existing ADMIN users are properly migrated to ORG_ADMIN role
4. Update frontend components to use consistent role display names