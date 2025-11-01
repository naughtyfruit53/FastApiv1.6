# Migration Notes: Organization RBAC & Entitlement Fix

## Overview

This document describes the database migrations and code changes implemented to fix organization dashboard access issues and remove SnappyMail integration.

## Problem Statement

### Issues Fixed
1. **Entitlement & RBAC Permission Errors**: Organization dashboard endpoints (`/api/v1/organizations/recent-activities` and `/api/v1/organizations/org-statistics`) were returning 403 errors due to:
   - Case mismatch in `enabled_modules` keys (e.g., "CRM" vs "crm")
   - Missing per-organization role definitions in `service_roles` table
   - Ambiguous permission error messages not showing required permission name

2. **SnappyMail Removal**: Complete removal of SnappyMail webmail integration from the codebase

## Database Migrations

Run migrations in order using:
```bash
alembic upgrade head
```

### Migration 1: Normalize enabled_modules (20251101_01_normalize)
**Purpose**: Normalize `enabled_modules` keys to lowercase and ensure "organization": true

**What it does**:
- Detects if `enabled_modules` column is JSON or JSONB
- Lowercases all keys (e.g., "CRM" → "crm", "ERP" → "erp")
- Converts string/numeric boolean-ish values to proper booleans
- Ensures every organization has `"organization": true` in enabled_modules
- Idempotent: safe to run multiple times

**Example**:
```json
// Before
{"CRM": true, "ERP": "true", "Manufacturing": 1}

// After
{"crm": true, "erp": true, "manufacturing": true, "organization": true}
```

### Migration 2: Seed Default Organization Roles (20251101_02_seed_roles)
**Purpose**: Create default `service_roles` for all existing organizations

**What it does**:
- For each organization, creates two roles if they don't exist:
  - `admin`: Full administrative access
  - `org_admin`: Organization-level administrative access
- Idempotent: skips if roles already exist
- Organization-scoped: `organization_id NOT NULL`

**Schema**:
```sql
INSERT INTO service_roles (organization_id, name, display_name, description)
VALUES 
  (<org_id>, 'admin', 'Administrator', 'Full administrative access...'),
  (<org_id>, 'org_admin', 'Organization Admin', 'Organization-level...');
```

### Migration 3: Grant Organization Permissions (20251101_03_grant_perms)
**Purpose**: Ensure organization permissions exist and are granted to default roles

**What it does**:
- Creates permissions if they don't exist:
  - `admin_organizations_view` (id 13595 if already exists)
  - `admin_organizations_read` (id 13592 if already exists)
- Grants both permissions to `admin` and `org_admin` roles for all organizations
- Idempotent: skips if permissions/grants already exist

**Permissions Created**:
| Name | Display Name | Module | Action |
|------|-------------|--------|--------|
| admin_organizations_view | View Organization Dashboard | admin | organizations_view |
| admin_organizations_read | Read Organization Data | admin | organizations_read |

### Migration 4: Create Auto-Seeding Trigger (20251101_04_trigger)
**Purpose**: Automatically seed roles and permissions for future organizations

**What it does**:
- Creates PL/pgSQL function `seed_roles_and_grants_for_org(p_org_id INT)`
- Creates AFTER INSERT trigger on `organizations` table
- When a new organization is created, automatically:
  1. Creates `admin` and `org_admin` roles
  2. Ensures organization permissions exist
  3. Grants permissions to both roles

**Function Signature**:
```sql
CREATE FUNCTION seed_roles_and_grants_for_org(p_org_id INTEGER) RETURNS VOID
```

**Trigger**:
```sql
CREATE TRIGGER trigger_seed_org_roles
AFTER INSERT ON organizations
FOR EACH ROW
EXECUTE FUNCTION seed_roles_and_grants_for_org(NEW.id);
```

### Migration 5: Drop SnappyMail Table (20251101_05_drop_snappymail)
**Purpose**: Remove `snappymail_configs` table as feature is discontinued

**What it does**:
- Drops `snappymail_configs` table if it exists
- Cleans up database from discontinued integration

## Code Changes

### Backend Changes

#### 1. Enforcement & Permission Mapping (`app/core/enforcement.py`)
- Added `PERMISSION_MAP` to map `(module, action)` → canonical permission name
- Example: `('organization', 'read')` → `'admin_organizations_view'`
- Enhanced error messages to include concrete `required_permission` field
- Both entitlement and RBAC errors now show the exact permission needed

#### 2. RBAC User Permission Resolution (`app/services/rbac.py`)
- Updated `user_has_permission()` to properly resolve user roles:
  1. Checks `users.role` + `users.organization_id` against `service_roles`
  2. If found, checks permissions granted to that role
  3. Falls back to explicit `user_service_roles` assignments
- Eliminates hardcoded role checks in favor of proper table lookups

#### 3. Entitlement Helpers (`app/utils/entitlement_helpers.py` - NEW)
- `normalize_enabled_modules()`: Case-insensitive normalization
- `check_module_enabled()`: Safe module checking with normalization
- `ensure_organization_module()`: Guarantees "organization" module is enabled

### Frontend Changes

#### 1. Email Service (`frontend/src/services/emailService.ts`)
- Removed `SnappyMailConfig` interface
- Removed `getSnappyMailConfig()` function
- Removed `getSnappyMailUrl()` function

### Infrastructure Changes

#### 1. Docker Compose (`docker-compose.yml`)
- Removed `snappymail` service
- Removed `snappymail_db` service
- Removed `snappymail_db_data` volume
- Removed `NEXT_PUBLIC_SNAPPYMAIL_URL` environment variable

#### 2. Dockerfiles
- Removed `Dockerfile.snappymail`
- Removed `snappymail-entrypoint.sh`
- Removed `snappymail.conf`

#### 3. Configuration (`app/core/config.py`)
- Removed `SNAPPYMAIL_URL` configuration variable

### Model Changes

#### 1. System Models (`app/models/system_models.py`)
- Removed `SnappyMailConfig` class

#### 2. User Models (`app/models/user_models.py`)
- Removed `snappymail_config` relationship

#### 3. Reset Service (`app/services/reset_service.py`)
- Removed `snappymail_configs` from cleanup tables list

## Role Mapping How-To

### Understanding the New Role System

The system now properly maps user roles through the database:

```
users.role (text) + users.organization_id (int)
         ↓
service_roles (org-scoped table)
         ↓
service_role_permissions (grants)
         ↓
service_permissions (canonical permissions)
```

### For Users with `users.role = 'org_admin'`

1. User has `organization_id = 123` and `role = 'org_admin'`
2. System looks up: `SELECT * FROM service_roles WHERE organization_id = 123 AND name = 'org_admin'`
3. If found, checks granted permissions via `service_role_permissions`
4. If user has `admin_organizations_view` permission → Access granted ✓

### Creating New Roles

To create a custom role for an organization:

```sql
-- 1. Create the role
INSERT INTO service_roles (organization_id, name, display_name, description, is_active)
VALUES (123, 'custom_role', 'Custom Role', 'Custom description', TRUE);

-- 2. Grant permissions to the role
INSERT INTO service_role_permissions (role_id, permission_id)
SELECT 
  (SELECT id FROM service_roles WHERE organization_id = 123 AND name = 'custom_role'),
  (SELECT id FROM service_permissions WHERE name = 'admin_organizations_view');
```

### Assigning Roles to Users

**Option 1: Direct via users.role (recommended for org-wide roles)**
```sql
UPDATE users 
SET role = 'org_admin' 
WHERE id = <user_id> AND organization_id = <org_id>;
```

**Option 2: Explicit via user_service_roles (for additional roles)**
```sql
INSERT INTO user_service_roles (user_id, role_id, is_active)
VALUES (<user_id>, <role_id>, TRUE);
```

## Testing the Fix

### Prerequisites
```bash
# Run migrations
alembic upgrade head

# Restart services
docker-compose restart api
```

### Test Case 1: Existing Organization with org_admin User
```bash
# 1. Verify role exists
SELECT * FROM service_roles 
WHERE organization_id = <your_org_id> AND name = 'org_admin';

# 2. Verify permissions granted
SELECT sp.name FROM service_permissions sp
JOIN service_role_permissions srp ON sp.id = srp.permission_id
JOIN service_roles sr ON srp.role_id = sr.id
WHERE sr.organization_id = <your_org_id> AND sr.name = 'org_admin';

# Should show: admin_organizations_view, admin_organizations_read

# 3. Test API endpoint
curl -H "Authorization: Bearer <token>" \
  http://localhost:8000/api/v1/organizations/recent-activities
# Expected: 200 OK
```

### Test Case 2: New Organization Auto-Seeding
```sql
-- Create new org (trigger fires automatically)
INSERT INTO organizations (name, subdomain, primary_email, primary_phone, ...)
VALUES ('Test Org', 'testorg', 'test@example.com', '1234567890', ...);

-- Verify roles created
SELECT * FROM service_roles WHERE organization_id = <new_org_id>;
-- Expected: 2 rows (admin, org_admin)

-- Verify permissions granted
SELECT COUNT(*) FROM service_role_permissions srp
JOIN service_roles sr ON srp.role_id = sr.id
WHERE sr.organization_id = <new_org_id>;
-- Expected: 4 (2 permissions × 2 roles)
```

### Test Case 3: Permission Denied with Clear Error
```bash
# Test with user who lacks permission
curl -H "Authorization: Bearer <viewer_token>" \
  http://localhost:8000/api/v1/organizations/recent-activities

# Expected: 403 with:
{
  "detail": {
    "error_type": "permission_denied",
    "permission": "admin_organizations_view",
    "required_permission": "admin_organizations_view",
    "message": "Insufficient permissions. Required permission: admin_organizations_view"
  }
}
```

## Troubleshooting

### Issue: Dashboard still returns 403
**Check**:
1. User's `organization_id` is set correctly
2. User's `role` field matches a row in `service_roles` for that org
3. That role has the required permission granted

```sql
-- Debug query
SELECT 
  u.id as user_id,
  u.email,
  u.role as user_role,
  u.organization_id,
  sr.id as service_role_id,
  sr.name as service_role_name,
  sp.name as permission_name
FROM users u
LEFT JOIN service_roles sr ON sr.organization_id = u.organization_id AND sr.name = u.role
LEFT JOIN service_role_permissions srp ON srp.role_id = sr.id
LEFT JOIN service_permissions sp ON sp.id = srp.permission_id
WHERE u.email = '<user_email>';
```

### Issue: Trigger not firing for new orgs
**Check PostgreSQL version**: Trigger requires PostgreSQL 9.0+

```sql
-- Test trigger manually
SELECT seed_roles_and_grants_for_org(<org_id>);
```

### Issue: enabled_modules still has mixed case
**Re-run normalization migration**:
```bash
alembic downgrade -1
alembic upgrade +1
```

## Rollback

To rollback all migrations:
```bash
alembic downgrade 784448bbeca4  # Go back to before our migrations
```

**Warning**: This will:
- Remove the trigger
- **Not** remove created roles/permissions (they may be in use)
- **Not** un-normalize enabled_modules (normalization is safe and idempotent)
- **Not** restore SnappyMail table (feature is discontinued)

## References

- Original issue: Organization dashboard 403 with entitlement/RBAC errors
- Database: PostgreSQL with JSON `enabled_modules` column
- RBAC: Organization-scoped service_roles with `organization_id NOT NULL`
- Permissions: `admin_organizations_view` (id 13595), `admin_organizations_read` (id 13592)
