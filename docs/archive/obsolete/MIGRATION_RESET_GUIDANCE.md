# Migration and Database Reset Guidance
## For Tenant/Entitlement/RBAC System v1.6

**Document Date:** 2025-11-06  
**Version:** 1.0  
**Status:** Production Ready

---

## Executive Summary

### Can Existing Organizations Work As-Is? ✅ **YES**

The tenant/entitlement/RBAC system changes are **backward compatible** with existing organizations. No database reset is required for production deployments.

### Key Findings

1. **Schema is Additive**: New tables added (modules, org_entitlements, etc.) don't break existing tables
2. **Migrations are Non-Destructive**: All migrations use proper upgrade/downgrade paths
3. **Default Values Present**: Organization.enabled_modules has sensible defaults
4. **Graceful Fallbacks**: Code handles missing entitlement data gracefully

### Recommendation: **Run Migrations Only** ✅

For existing production systems:
- ✅ Run `alembic upgrade head` to apply new schemas
- ✅ Run seed scripts to initialize entitlement data
- ❌ **Do NOT** drop/recreate database
- ❌ **Do NOT** delete existing migration files

---

## Migration Approach by Scenario

### Scenario 1: Existing Production System (RECOMMENDED)

**Situation:** Live system with existing organizations and users

**Approach:** Migration without reset

**Steps:**
```bash
# 1. Backup database (CRITICAL!)
pg_dump -U postgres fastapi_db > backup_pre_rbac_$(date +%Y%m%d).sql

# 2. Apply new migrations
alembic upgrade head

# 3. Verify migration success
alembic current
# Should show: 20251104_01_fix_gst_settings_permissions (or later)

# 4. Seed entitlement data
python scripts/seed_entitlements.py

# 5. Initialize entitlements for existing orgs
python scripts/initialize_existing_org_entitlements.py

# 6. Verify organizations
python -c "from app.core.database import SessionLocal; from app.models import Organization; db = SessionLocal(); print(f'{len(db.query(Organization).all())} orgs found')"

# 7. Test with existing user credentials
# Login should work with existing users
```

**Benefits:**
- ✅ Zero data loss
- ✅ Existing users continue working
- ✅ Existing data preserved
- ✅ Rollback possible

**Risks:**
- ⚠️ Need to initialize entitlements for existing orgs
- ⚠️ May need to assign default permissions to existing users

---

### Scenario 2: Development/Staging Environment

**Situation:** Non-production system where data loss is acceptable

**Approach:** Optional clean reset for fresh start

**Steps:**
```bash
# Option A: Migration (Preserves Data)
alembic upgrade head
python scripts/seed_entitlements.py

# Option B: Clean Reset (Fresh Start)
# 1. Drop database
psql -U postgres -c "DROP DATABASE IF EXISTS fastapi_db;"
psql -U postgres -c "CREATE DATABASE fastapi_db;"

# 2. Run all migrations
alembic upgrade head

# 3. Seed all data
python scripts/seed_entitlements.py
python seed_hr_data.py
python seed_crm_marketing_service_data.py
python seed_asset_transport_data.py
```

**Benefits:**
- ✅ Clean slate
- ✅ Known good state
- ✅ Test full onboarding flow

**Risks:**
- ❌ All data lost
- ❌ Users need recreation

---

### Scenario 3: New Installation

**Situation:** Fresh installation, no existing data

**Approach:** Standard setup

**Steps:**
```bash
# 1. Create database
psql -U postgres -c "CREATE DATABASE fastapi_db;"

# 2. Run migrations
alembic upgrade head

# 3. Seed initial data
python scripts/seed_entitlements.py
python seed_hr_data.py
python seed_crm_marketing_service_data.py
```

**Benefits:**
- ✅ Proper 3-layer security from start
- ✅ All features enabled
- ✅ Clean initial state

---

## Migration Scripts Required

### Script 1: Initialize Existing Organization Entitlements

**File:** `scripts/initialize_existing_org_entitlements.py`

**Purpose:** Create entitlement records for organizations that existed before the entitlement system

```python
# scripts/initialize_existing_org_entitlements.py
"""
Initialize entitlements for existing organizations.
Run this ONCE after applying entitlement migrations.
"""

import asyncio
from sqlalchemy import select
from app.core.database import SessionLocal, async_session_maker
from app.models.user_models import Organization
from app.models.rbac_models import Module, OrgEntitlement
from app.core.constants import ModuleStatusEnum
import logging

logger = logging.getLogger(__name__)

async def initialize_org_entitlements():
    """Initialize entitlements for existing organizations"""
    async with async_session_maker() as db:
        try:
            # Get all organizations
            result = await db.execute(select(Organization))
            orgs = result.scalars().all()
            
            logger.info(f"Found {len(orgs)} organizations")
            
            # Get all modules
            result = await db.execute(select(Module))
            modules = result.scalars().all()
            
            logger.info(f"Found {len(modules)} modules")
            
            for org in orgs:
                logger.info(f"Processing org: {org.name} (ID: {org.id})")
                
                # Get org's enabled_modules (from JSON field)
                enabled_modules = org.enabled_modules or {}
                
                for module in modules:
                    # Check if entitlement already exists
                    result = await db.execute(
                        select(OrgEntitlement).where(
                            OrgEntitlement.org_id == org.id,
                            OrgEntitlement.module_id == module.id
                        )
                    )
                    existing = result.scalars().first()
                    
                    if existing:
                        logger.info(f"  - {module.module_key}: Already exists")
                        continue
                    
                    # Determine status from org.enabled_modules
                    module_key_lower = module.module_key.lower()
                    module_key_upper = module.module_key.upper()
                    module_key_title = module.module_key.title()
                    
                    is_enabled = (
                        enabled_modules.get(module_key_lower, False) or
                        enabled_modules.get(module_key_upper, False) or
                        enabled_modules.get(module_key_title, False)
                    )
                    
                    # Always-on modules
                    if module_key_lower in ['email', 'dashboard']:
                        status = ModuleStatusEnum.ENABLED
                    elif is_enabled:
                        status = ModuleStatusEnum.ENABLED
                    else:
                        status = ModuleStatusEnum.DISABLED
                    
                    # Create entitlement
                    entitlement = OrgEntitlement(
                        org_id=org.id,
                        module_id=module.id,
                        status=status.value,
                        source='migration'
                    )
                    db.add(entitlement)
                    logger.info(f"  - {module.module_key}: Created ({status.value})")
                
                await db.commit()
                logger.info(f"Completed org: {org.name}")
            
            logger.info("✅ Entitlement initialization complete!")
            
        except Exception as e:
            logger.error(f"❌ Error initializing entitlements: {e}")
            await db.rollback()
            raise

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(initialize_org_entitlements())
```

**When to run:** Once after applying entitlement migrations to production

---

### Script 2: Seed Entitlements

**File:** `scripts/seed_entitlements.py` (already exists)

**Purpose:** Create base module and plan data

**When to run:** 
- After fresh database creation
- After running migrations (before initializing org entitlements)

---

## Data Compatibility Matrix

| Component | Backward Compatible | Notes |
|-----------|-------------------|-------|
| Organizations | ✅ Yes | enabled_modules field already exists with defaults |
| Users | ✅ Yes | Role field exists, new permission tables are additive |
| Modules | ✅ N/A | New table, no conflicts |
| Entitlements | ✅ N/A | New table, linked to orgs via foreign key |
| Permissions | ✅ Yes | Existing RBAC tables enhanced, not replaced |
| Business Data | ✅ Yes | No changes to CRM, inventory, vouchers, etc. |

---

## Schema Changes Summary

### New Tables (Additive - No Breaking Changes)

1. **modules** - Module definitions
2. **submodules** - Submodule definitions
3. **plans** - Subscription plans
4. **plan_entitlements** - Plan-to-module mappings
5. **org_entitlements** - Organization module access
6. **org_subentitlements** - Organization submodule access
7. **entitlement_events** - Audit trail for entitlement changes

### Modified Tables (Non-Breaking)

1. **organizations** - Already has `enabled_modules` JSON field (no changes needed)
2. **users** - Already has `role` field (enhanced in code, not schema)
3. **permissions** - Existing table extended with new permission patterns

### No Changes To

- Business entity tables (customers, products, vouchers, etc.)
- Transaction tables (sales, purchases, manufacturing, etc.)
- Master data tables (chart of accounts, employees, etc.)

---

## Rollback Strategy

### If Migration Succeeds But System Has Issues

```bash
# Rollback to previous migration
alembic downgrade -1

# Or rollback to specific revision
alembic downgrade <previous_revision_id>

# Restore from backup if needed
psql -U postgres -c "DROP DATABASE IF EXISTS fastapi_db;"
psql -U postgres -c "CREATE DATABASE fastapi_db;"
psql -U postgres fastapi_db < backup_pre_rbac_YYYYMMDD.sql
```

### If System Works But Want to Undo Entitlement Changes

```bash
# Remove entitlement data (keeps tables)
psql -U postgres fastapi_db -c "TRUNCATE TABLE org_entitlements CASCADE;"
psql -U postgres fastapi_db -c "TRUNCATE TABLE org_subentitlements CASCADE;"
psql -U postgres fastapi_db -c "TRUNCATE TABLE entitlement_events CASCADE;"

# System will fall back to enabled_modules field
```

---

## Testing Checklist Post-Migration

### 1. Basic System Health
```bash
# Database connection
python -c "from app.core.database import SessionLocal; db = SessionLocal(); print('✅ DB Connected')"

# Migration status
alembic current
# Should show latest revision

# Table counts
psql -U postgres fastapi_db -c "SELECT COUNT(*) FROM organizations;"
psql -U postgres fastapi_db -c "SELECT COUNT(*) FROM users;"
psql -U postgres fastapi_db -c "SELECT COUNT(*) FROM modules;"
psql -U postgres fastapi_db -c "SELECT COUNT(*) FROM org_entitlements;"
```

### 2. Authentication
```bash
# Test login with existing credentials
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@testorg.com", "password": "yourpassword"}'

# Should return access token
```

### 3. Entitlement System
```bash
# Get org entitlements
curl -X GET http://localhost:8000/api/v1/entitlements/org \
  -H "Authorization: Bearer <token>"

# Should return module list with statuses
```

### 4. RBAC System
```bash
# Get user permissions
curl -X GET http://localhost:8000/api/v1/rbac/permissions \
  -H "Authorization: Bearer <token>"

# Should return user's effective permissions
```

### 5. Business Operations
- ✅ Create CRM lead
- ✅ Create inventory item
- ✅ Create voucher
- ✅ Generate report
- ✅ Access dashboard

All should work with existing users if they have proper entitlements.

---

## FAQ

### Q: Will existing users lose access after migration?

**A:** No. The system has fallbacks:
1. If no entitlement record exists, system checks `organization.enabled_modules`
2. Super admins and org admins maintain access
3. Migration script creates entitlement records from existing `enabled_modules`

### Q: Do I need to reassign user permissions?

**A:** Depends on your setup:
- **Super Admins:** No change needed, keep full access
- **Org Admins:** No change needed, keep full org access
- **Managers/Executives:** May need to run permission assignment if using granular RBAC

### Q: Can I run migrations on production without downtime?

**A:** Yes, with caveats:
- Migrations are additive (create new tables)
- No existing table alterations that break code
- Brief unavailability during migration execution (~30-60 seconds)
- Recommend maintenance window for peace of mind

### Q: What if organizations have custom enabled_modules values?

**A:** Migration script preserves them:
- Script reads each org's `enabled_modules` JSON field
- Creates matching entitlement records
- Existing org settings are honored

### Q: Should I delete migration files and recreate?

**A:** **NO!** Never delete migration files in production:
- ❌ Will break alembic history
- ❌ Will prevent rollback
- ❌ Will cause migration conflicts
- ✅ Always run `alembic upgrade head`

---

## Conclusion

### For Production: ✅ Migration Without Reset

**Recommended Steps:**
1. Backup database
2. Run `alembic upgrade head`
3. Run `python scripts/seed_entitlements.py`
4. Run `python scripts/initialize_existing_org_entitlements.py`
5. Test with existing user
6. Monitor for 24 hours

**Result:** Zero data loss, zero downtime, full backward compatibility

### For Development: Either Approach Works

- **Migration:** Keep test data
- **Reset:** Fresh clean start

### For New Installations: Standard Setup

- Create DB → Run migrations → Seed data

---

## Support

If issues arise post-migration:
1. Check logs: `tail -f logs/app.log`
2. Verify migration status: `alembic current`
3. Test entitlement endpoint: `/api/v1/entitlements/org`
4. Rollback if needed: `alembic downgrade -1`
5. Restore backup if critical: `psql ... < backup.sql`

---

**Last Updated:** 2025-11-06  
**Next Review:** After production deployment  
**Status:** ✅ Ready for production migration
