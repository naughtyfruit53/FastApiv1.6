# Platform Administration Guide

## Overview

This guide describes the 2-tier platform-level role system for managing the FastAPI SaaS application at the platform level (not organization level).

## Platform Roles

### 1. Super Admin (`super_admin`)

**Description**: The highest level of platform access with full rights to manage the entire application.

**Capabilities**:
- ✅ Create and manage other super admins
- ✅ Create and manage app admins
- ✅ Delete platform-level users (super_admin and app_admin)
- ✅ Reset any user password (platform and organization level)
- ✅ Manage all organizations
- ✅ Create/delete organizations
- ✅ Factory reset the application
- ✅ Reset application data
- ✅ Reset organization data
- ✅ View all audit logs across the platform
- ✅ Full access to all platform features

**Restrictions**:
- Cannot be deleted (except the god account: naughtyfruit53@gmail.com)
- Must be created through seeding or by another super admin

### 2. App Admin (`app_admin`)

**Description**: Platform-level administrators with most rights except managing platform admins and performing destructive operations.

**Capabilities**:
- ✅ Manage organizations (create, view, update)
- ✅ View audit logs
- ✅ Access platform administration features
- ✅ Manage organization settings

**Restrictions**:
- ❌ Cannot create or manage super admins
- ❌ Cannot create or manage app admins
- ❌ Cannot delete platform-level users
- ❌ Cannot reset application data
- ❌ Cannot reset organization data
- ❌ Cannot perform factory reset
- ❌ Cannot reset any user passwords at platform level

## Role Comparison Matrix

| Permission | super_admin | app_admin |
|-----------|-------------|-----------|
| Manage Platform Admins | ✅ | ❌ |
| Create Organizations | ✅ | ✅ |
| Manage Organizations | ✅ | ✅ |
| View Organizations | ✅ | ✅ |
| Delete Organizations | ✅ | ❌ |
| Reset Any Password | ✅ | ❌ |
| Reset App/Org Data | ✅ | ❌ |
| Factory Reset | ✅ | ❌ |
| View All Audit Logs | ✅ | ❌ |
| View Audit Logs | ✅ | ✅ |

## User Management

### Creating a Super Admin

Only existing super admins can create new super admin accounts.

**API Endpoint**: `POST /api/v1/app-users/`

**Request Body**:
```json
{
  "email": "newadmin@example.com",
  "password": "SecurePassword123!",
  "full_name": "New Super Admin",
  "role": "super_admin"
}
```

**Requirements**:
- Must be authenticated as super_admin
- Email must be unique
- Password must meet security requirements (8+ chars, uppercase, lowercase, digit, special char)

### Creating an App Admin

Only super admins can create app admin accounts.

**API Endpoint**: `POST /api/v1/app-users/`

**Request Body**:
```json
{
  "email": "appadmin@example.com",
  "password": "SecurePassword123!",
  "full_name": "App Administrator",
  "role": "app_admin"
}
```

**Requirements**:
- Must be authenticated as super_admin
- Email must be unique
- Password must meet security requirements

### Updating Platform Users

Only super admins can update platform-level users (super_admin or app_admin).

**API Endpoint**: `PUT /api/v1/app-users/{user_id}`

**Allowed Updates**:
- Email
- Full name
- Role (only between super_admin and app_admin)
- Active status
- Profile information

**Restrictions**:
- Cannot modify the god account (naughtyfruit53@gmail.com) critical properties
- Cannot change role to organization-level roles

### Deleting Platform Users

Only super admins can delete platform-level users.

**API Endpoint**: `DELETE /api/v1/app-users/{user_id}`

**Restrictions**:
- Cannot delete the god account (naughtyfruit53@gmail.com)
- Cannot delete your own account
- Must be authenticated as super_admin

### Listing Platform Users

Both super_admin and app_admin can list platform-level users.

**API Endpoint**: `GET /api/v1/app-users/`

**Query Parameters**:
- `skip`: Number of records to skip (default: 0)
- `limit`: Maximum records to return (default: 100)
- `active_only`: Filter to active users only (default: true)

## Onboarding Process

### Initial Bootstrap

1. **Database Setup**: Run migrations to create database schema
   ```bash
   alembic upgrade head
   ```

2. **Seed Super Admin**: Run the seeding script to create the initial super admin
   ```bash
   python scripts/seed_all.py
   ```
   
   This creates:
   - Email: `naughtyfruit53@gmail.com`
   - Password: `Admin123!`
   - Role: `super_admin`
   - Must change password on first login

3. **First Login**: Log in with the seeded super admin credentials

4. **Change Password**: Immediately change the default password

### Creating Additional Platform Admins

1. Log in as super_admin
2. Navigate to App Users Management
3. Create new app_admin or super_admin accounts as needed
4. Notify new admins of their credentials
5. New admins will be forced to change password on first login

## Security Considerations

### Password Requirements

All platform-level users must have passwords that meet these criteria:
- Minimum 8 characters
- At least 1 uppercase letter
- At least 1 lowercase letter
- At least 1 digit
- At least 1 special character (!@#$%^&*()_+-=[]{}|;:,.<>?)

### Account Protection

- The god account (naughtyfruit53@gmail.com) cannot be deleted
- Users cannot delete their own account
- All password changes are logged in audit trail
- Failed login attempts are tracked
- Accounts can be locked after multiple failed attempts

### Audit Logging

All platform-level administrative actions are logged including:
- User creation/updates/deletion
- Organization management
- Password resets
- Data resets
- Permission changes

Super admins have access to all audit logs. App admins have limited audit log access.

## API Authentication

Platform-level users authenticate using the same login endpoint as organization users but without a subdomain:

**Endpoint**: `POST /api/v1/auth/login`

**Request Body**:
```json
{
  "email": "admin@example.com",
  "password": "SecurePassword123!"
}
```

**Response**:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user_role": "super_admin",
  "user_type": "platform",
  "must_change_password": false
}
```

## Testing Role Restrictions

### Validation Checklist

After implementing or modifying platform roles, validate these behaviors:

#### Super Admin Tests
- [ ] Can create super_admin accounts
- [ ] Can create app_admin accounts
- [ ] Can update any platform user
- [ ] Can delete any platform user (except god account)
- [ ] Can perform factory reset
- [ ] Can reset application data
- [ ] Can view all audit logs
- [ ] Can manage all organizations

#### App Admin Tests
- [ ] Cannot create super_admin accounts
- [ ] Cannot create app_admin accounts
- [ ] Cannot update any platform user
- [ ] Cannot delete any platform user
- [ ] Cannot perform factory reset
- [ ] Cannot reset application data
- [ ] Can view limited audit logs
- [ ] Can manage organizations (but not delete)

#### Permission Boundary Tests
- [ ] App admin attempting to create super_admin returns 403
- [ ] App admin attempting to delete platform user returns 403
- [ ] App admin attempting factory reset returns 403
- [ ] Super admin can perform all operations
- [ ] Organization users cannot access platform admin endpoints

## Troubleshooting

### Issue: Cannot create app_admin

**Symptom**: 403 Forbidden when trying to create app_admin

**Solution**: Ensure you are logged in as super_admin, not app_admin

### Issue: Super admin seeding fails

**Symptom**: Error during seed_all.py execution

**Solutions**:
1. Check database connection
2. Verify migrations are up to date
3. Check if super admin already exists
4. Review Supabase Auth configuration

### Issue: Cannot update platform user

**Symptom**: 403 Forbidden when trying to update platform user

**Solution**: Only super_admin can update platform-level users

### Issue: Password doesn't meet requirements

**Symptom**: 400 Bad Request with password validation error

**Solution**: Ensure password meets all security requirements listed above

## Migration Notes

### From Previous System

If migrating from a system with `platform_admin` role:

1. **Database Update**: Run migration to rename role values
   ```sql
   UPDATE users SET role = 'app_admin' WHERE role = 'platform_admin';
   UPDATE platform_users SET role = 'app_admin' WHERE role = 'platform_admin';
   ```

2. **Code Update**: All references to `platform_admin` have been updated to `app_admin`

3. **Permission Update**: Verify app_admin permissions are restricted as documented

### Idempotency

The seeding process is idempotent:
- If super_admin already exists, seeding is skipped
- Running seed_all.py multiple times is safe
- Use `--skip-check` flag to force seeding

## Best Practices

1. **Least Privilege**: Use app_admin for most platform administration tasks
2. **Limited Super Admins**: Create only the necessary number of super_admin accounts
3. **Regular Audits**: Review audit logs regularly for suspicious activity
4. **Password Rotation**: Enforce regular password changes for platform admins
5. **MFA**: Enable multi-factor authentication for platform-level accounts (if available)
6. **Access Review**: Periodically review and revoke unnecessary platform admin access

## Support

For additional support or questions:
- Review API documentation: `API_DOCUMENTATION.md`
- Check RBAC guide: `DEVELOPER_GUIDE_RBAC.md`
- Contact platform administrators
