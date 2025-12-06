# Permission Migration Backend Guide

## Overview

This document describes the backend permission standardization migration from legacy formats (underscore, colon) to the new dotted format (`module.action`), including permission hierarchy support.

## Migration Goals

1. **Standardize permission naming** to dotted format (e.g., `users.manage`, `inventory.read`)
2. **Implement permission hierarchy** where parent permissions grant child permissions
3. **Maintain backward compatibility** during transition period
4. **Provide API for frontend feature detection** during rollout

## Permission Formats

### New Format (Dotted)

```
module.action
module.submodule.action
```

Examples:
- `users.manage`
- `inventory.read`
- `crm.commission.create`
- `platform.super_admin`

### Legacy Formats (Deprecated)

**Underscore format:**
```
module_action
```
Examples: `manage_users`, `view_audit_logs`

**Colon format:**
```
module:submodule:action
```
Examples: `mail:accounts:read`, `mail:emails:compose`

## Permission Hierarchy

Parent permissions automatically grant child permissions:

```python
PERMISSION_HIERARCHY = {
    "master_data.read": [
        "vendors.read",
        "products.read",
        "inventory.read",
    ],
    "master_data.write": [
        "vendors.create",
        "vendors.update",
        "products.write",
        "products.update",
        "inventory.write",
        "inventory.update",
    ],
    "crm.admin": [
        "crm.settings",
        "crm.commission.read",
        "crm.commission.create",
        "crm.commission.update",
        "crm.commission.delete",
    ],
    # ... more hierarchies
}
```

## Backward Compatibility

The system maintains backward compatibility through `LEGACY_PERMISSION_MAP` in `app/core/permissions.py`:

```python
LEGACY_PERMISSION_MAP = {
    "manage_users": "users.manage",
    "view_users": "users.view",
    # ... all legacy mappings
}
```

All permission checks automatically normalize legacy formats to dotted format.

## Migration Steps

### 1. Database Migration

Run the Alembic migration to seed dotted-format permissions:

```bash
# Review migration
alembic current
alembic history

# Apply migration
alembic upgrade head

# Verify permissions were seeded
python -c "
from app.core.database import SessionLocal
from app.models.rbac_models import ServicePermission
db = SessionLocal()
perms = db.query(ServicePermission).filter(ServicePermission.permission_key.like('%.%')).count()
print(f'Dotted permissions: {perms}')
db.close()
"
```

### 2. Manual Seeding (if migration fails)

```bash
# Run seeder manually
python -m app.db.seeds.permission_seeder
```

### 3. Verify API Endpoints

Test the new system endpoints:

```bash
# Get permission format info
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/system/permission-format

# Expected response:
{
  "primary_format": "dotted",
  "compatibility": true,
  "legacy_formats": ["underscore", "colon"],
  "hierarchy_enabled": true,
  "version": "1.0",
  "migration_status": "in_progress",
  "total_legacy_mappings": 45,
  "total_hierarchy_rules": 6
}

# Get permission mappings (admin only)
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/system/permission-format/mappings

# Get permission hierarchy (admin only)
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/system/permission-format/hierarchy
```

## Related Files

- `app/core/permissions.py` - Permission constants and hierarchy
- `app/db/seeds/permission_seeder.py` - Database seeder
- `app/api/v1/system.py` - Feature detection API
- `migrations/versions/20251206_093930_permission_dotted_fmt_001.py` - Alembic migration
