# Legacy Entitlements Migration Runbook

## Overview

This runbook guides you through migrating legacy organization module flags (`enabled_modules` JSON field) to the new entitlements system.

---

## Prerequisites

- [ ] Database backup completed
- [ ] Alembic migrations applied (entitlements tables created)
- [ ] Module taxonomy seeded
- [ ] Access to production database (read/write)
- [ ] Super admin credentials available

---

## Phase 1: Pre-Migration Validation

### 1.1 Verify Database Schema

```bash
cd /home/runner/work/FastApiv1.6/FastApiv1.6

# Check migration status
alembic current

# Should show: 20251101_entitlements
```

### 1.2 Verify Module Taxonomy

```bash
python scripts/seed_entitlements.py
```

Expected output:
```
✓ Seeded 17 modules
✓ Seeded 250+ submodules across 17 modules
```

### 1.3 Check Existing Organizations

```sql
-- Count organizations
SELECT COUNT(*) FROM organizations;

-- Sample enabled_modules
SELECT id, name, enabled_modules 
FROM organizations 
LIMIT 5;
```

---

## Phase 2: Dry-Run Migration

### 2.1 Run Dry-Run

```bash
python scripts/migrate_legacy_entitlements.py
```

Expected output:
```
==================================================================
LEGACY ENTITLEMENTS MIGRATION
==================================================================
Mode: DRY-RUN (no changes will be made)
==================================================================

📊 Loaded 17 modules and 250 submodules
📊 Loaded 52 mapping rules
📊 Found 100 organizations to process

📋 Processing organization: Acme Corp (ID: 1)
   Legacy enabled_modules: ['CRM', 'ERP', 'HR', 'Inventory']
   Mapped modules: ['sales', 'finance', 'hr', 'inventory']
   ✓ [DRY-RUN] Would create module entitlement: sales -> enabled
   ✓ [DRY-RUN] Would create module entitlement: finance -> enabled
   ...

[DRY-RUN] No changes were made to the database

==================================================================
MIGRATION SUMMARY
==================================================================
Organizations processed: 100
Module entitlements created: 400
Events created: 100
Errors: 0
==================================================================
```

### 2.2 Review Dry-Run Results

1. Verify organization count matches
2. Check for any errors
3. Validate mapping correctness for sample orgs
4. Confirm no unexpected module keys

### 2.3 Spot Check Sample Organizations

```sql
-- Check a few organizations manually
SELECT 
    o.id,
    o.name,
    o.enabled_modules,
    COUNT(oe.id) as entitlement_count
FROM organizations o
LEFT JOIN org_entitlements oe ON oe.org_id = o.id
WHERE o.id IN (1, 2, 3, 4, 5)
GROUP BY o.id, o.name, o.enabled_modules;
```

Should show 0 entitlements (dry-run didn't create anything).

---

## Phase 3: Execute Migration (Lower Environment)

### 3.1 Test Environment First

**Environment:** Staging/QA

```bash
# Execute migration
python scripts/migrate_legacy_entitlements.py --execute
```

Expected output:
```
==================================================================
Mode: EXECUTE
==================================================================
...
✓ Changes committed to database
...
Module entitlements created: 400
Events created: 100
Errors: 0
==================================================================
```

### 3.2 Verify Migration Results

```sql
-- Check entitlement counts
SELECT 
    m.module_key,
    COUNT(oe.id) as org_count
FROM modules m
LEFT JOIN org_entitlements oe ON oe.module_id = m.id
GROUP BY m.module_key
ORDER BY org_count DESC;

-- Check event log
SELECT 
    event_type,
    COUNT(*) as count
FROM entitlement_events
WHERE event_type = 'legacy_migration'
GROUP BY event_type;
```

### 3.3 Test API Endpoints

```bash
# Get entitlements for a test org
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/orgs/1/entitlements

# Should return entitlements matching legacy enabled_modules
```

### 3.4 Test Frontend Access

1. Log in as regular user
2. Verify menu items match legacy access
3. Test protected routes
4. Verify no regressions

---

## Phase 4: Production Migration

### 4.1 Final Backup

```bash
# Database backup
pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME > backup_pre_migration_$(date +%Y%m%d_%H%M%S).sql
```

### 4.2 Maintenance Window

**Recommended: Low-traffic period (e.g., 2 AM - 4 AM local time)**

1. Notify users of brief maintenance
2. Enable maintenance mode (if available)

### 4.3 Execute Production Migration

```bash
# Double-check database connection
echo $DATABASE_URL

# Execute migration
python scripts/migrate_legacy_entitlements.py --execute
```

### 4.4 Verify Production Results

Same SQL queries as Phase 3.2:

```sql
-- Quick verification
SELECT COUNT(*) FROM org_entitlements;
SELECT COUNT(*) FROM entitlement_events WHERE event_type = 'legacy_migration';
```

### 4.5 Smoke Tests

1. Test with 3-5 real organizations
2. Verify admin panel access
3. Check critical routes (sales, inventory, etc.)
4. Monitor error logs for 403s

### 4.6 Enable Entitlements Feature Flag

```python
# In config or environment
ENABLE_ENTITLEMENTS_GATING = True
```

Or via feature flag service.

---

## Phase 5: Post-Migration Monitoring

### 5.1 First 24 Hours

Monitor:
- 403 errors (unexpected access denials)
- User support tickets
- Frontend error logs
- API latency (caching issues)

### 5.2 Key Metrics

```sql
-- Daily entitlement checks (from logs)
-- Track 403 responses

-- Module usage by org
SELECT 
    o.name,
    COUNT(DISTINCT oe.module_id) as enabled_modules
FROM organizations o
JOIN org_entitlements oe ON oe.org_id = o.id
WHERE oe.status IN ('enabled', 'trial')
GROUP BY o.name
ORDER BY enabled_modules DESC
LIMIT 20;
```

### 5.3 User Feedback

- Collect feedback from power users
- Identify any access issues
- Document edge cases

---

## Rollback Plan

### If Issues Arise Within 4 Hours

1. **Disable Feature Flag**
   ```python
   ENABLE_ENTITLEMENTS_GATING = False
   ```

2. **Frontend Falls Back**
   - Frontend checks legacy `enabled_modules` field
   - No data loss (entitlements remain in DB)

3. **Backend Falls Back**
   - Remove `@require_entitlement` decorators temporarily
   - Or make decorator check legacy field if flag is off

### If Issues Arise After 4 Hours

1. Investigate specific issues
2. Create hotfix for edge cases
3. Update mapping template if needed
4. Re-run migration for affected orgs:
   ```bash
   # Migration is idempotent
   python scripts/migrate_legacy_entitlements.py --execute
   ```

### Complete Rollback (Last Resort)

```sql
-- Truncate entitlement tables (keeps schema)
TRUNCATE TABLE entitlement_events CASCADE;
TRUNCATE TABLE org_subentitlements CASCADE;
TRUNCATE TABLE org_entitlements CASCADE;

-- Disable feature flag
```

---

## Troubleshooting

### Issue: Migration Script Errors

**Symptom:** Script exits with error

**Solutions:**
1. Check database connectivity
2. Verify mapping CSV is present
3. Check for module key mismatches
4. Review stack trace for specific issue

### Issue: Org Lost Access to Module

**Symptom:** User reports lost access after migration

**Investigation:**
```sql
-- Check org's legacy modules
SELECT enabled_modules FROM organizations WHERE id = <org_id>;

-- Check org's entitlements
SELECT m.module_key, oe.status 
FROM org_entitlements oe
JOIN modules m ON m.id = oe.module_id
WHERE oe.org_id = <org_id>;

-- Check mapping
SELECT * FROM entitlement_mapping_template.csv
WHERE target_module = '<module_key>';
```

**Fix:**
```bash
# Re-run migration for specific org (idempotent)
python scripts/migrate_legacy_entitlements.py --execute
```

Or manually via Admin UI.

### Issue: Unexpected 403 Errors

**Symptom:** Users getting 403 on previously accessible routes

**Investigation:**
1. Check entitlement guard logs
2. Verify route has correct module/submodule keys
3. Check if module is disabled vs submodule is disabled

**Fix:**
1. Update route guard with correct keys
2. Or manually enable entitlement via Admin UI

---

## Post-Migration Cleanup

### After 30 Days

If no issues:

1. **Remove Feature Flag** (make entitlements default)
2. **Deprecate Legacy Field** (mark for removal in next major version)
3. **Update Documentation** (remove legacy references)

### After 90 Days

1. **Drop Legacy Field** (if feasible)
   ```sql
   ALTER TABLE organizations DROP COLUMN enabled_modules;
   ```

---

## Support Contacts

- **Database Team:** database@company.com
- **DevOps:** devops@company.com  
- **Product Team:** product@company.com

---

## Checklist

- [ ] Phase 1: Pre-migration validation complete
- [ ] Phase 2: Dry-run successful, reviewed
- [ ] Phase 3: Lower environment migrated and tested
- [ ] Phase 4: Production migrated
- [ ] Phase 5: Monitoring in place, no critical issues
- [ ] Documentation updated
- [ ] Team notified of completion

---

**Migration Prepared By:** DevOps Team  
**Last Updated:** 2025-11-01  
**Version:** 1.0
