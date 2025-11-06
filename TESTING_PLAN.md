# Testing Plan - Unified Database Seeding and Reset

This document outlines the testing procedures for the unified database seeding system and repository cleanup.

## 1. Database Reset Workflow Tests

### Test 1.1: SQL Drop Script
**Objective**: Verify that the SQL script successfully drops all tables

**Prerequisites**:
- PostgreSQL or Supabase database running
- Database with existing tables
- Backup created (optional but recommended)

**Steps**:
```bash
# 1. Create a test database with some tables
psql -U postgres -c "CREATE DATABASE test_fastapi_db;"

# 2. Run migrations to create tables
alembic upgrade head

# 3. Verify tables exist
psql -U postgres test_fastapi_db -c "\dt"

# 4. Edit sql/drop_all_tables.sql and comment out the safety check

# 5. Run the drop script
psql -U postgres test_fastapi_db -f sql/drop_all_tables.sql

# 6. Verify all tables are dropped
psql -U postgres test_fastapi_db -c "\dt"
```

**Expected Results**:
- All tables should be dropped
- The query should return "No relations found"
- No errors should occur during the drop process

**Rollback**: Restore from backup if needed
```bash
psql -U postgres test_fastapi_db < backup.sql
```

---

### Test 1.2: Complete Reset Workflow
**Objective**: Test the complete database reset and rebuild workflow

**Steps**:
```bash
# 1. Backup current database
pg_dump -U postgres fastapi_db > backup_pre_test.sql

# 2. Drop all tables
psql -U postgres fastapi_db -f sql/drop_all_tables.sql

# 3. Run migrations
alembic upgrade head

# 4. Verify migration applied
alembic current
# Should show latest migration

# 5. Run unified seeding
python scripts/seed_all.py

# 6. Verify seeded data
psql -U postgres fastapi_db -c "SELECT COUNT(*) FROM users WHERE is_super_admin = true;"
# Should return 1

psql -U postgres fastapi_db -c "SELECT COUNT(*) FROM modules;"
# Should return > 0

psql -U postgres fastapi_db -c "SELECT COUNT(*) FROM service_permissions;"
# Should return > 0
```

**Expected Results**:
- Database schema recreated successfully
- All baseline data seeded
- Super admin user exists
- All modules and permissions created

---

## 2. Unified Seeding Script Tests

### Test 2.1: Fresh Database Seeding
**Objective**: Verify seeding works on a completely empty database

**Setup**:
```bash
# Create fresh database
psql -U postgres -c "DROP DATABASE IF EXISTS test_seed_db;"
psql -U postgres -c "CREATE DATABASE test_seed_db;"

# Update .env to point to test database
export DATABASE_URL="postgresql://postgres:password@localhost:5432/test_seed_db"

# Run migrations
alembic upgrade head
```

**Test**:
```bash
# Run the seed script
python scripts/seed_all.py

# Verify logging output shows seeding completed
# Check for success messages
```

**Expected Results**:
- Script completes without errors
- All 6 seeding steps complete successfully
- Success message displayed at end

**Verification Queries**:
```sql
-- Check super admin
SELECT email, role, is_super_admin FROM users WHERE is_super_admin = true;

-- Check modules
SELECT module_key, display_name FROM modules ORDER BY sort_order;

-- Check submodules
SELECT m.module_key, s.submodule_key 
FROM submodules s 
JOIN modules m ON s.module_id = m.id 
ORDER BY m.sort_order, s.sort_order;

-- Check RBAC permissions
SELECT COUNT(*) FROM service_permissions;

-- Check voucher templates
SELECT name, is_system_template FROM voucher_format_templates WHERE is_system_template = true;

-- Check organizations
SELECT id, name, enabled_modules FROM organizations;
```

---

### Test 2.2: Idempotency Test
**Objective**: Verify script can be run multiple times without creating duplicates

**Test**:
```bash
# Run seed script first time
python scripts/seed_all.py

# Count records
ADMIN_COUNT1=$(psql -U postgres test_seed_db -tAc "SELECT COUNT(*) FROM users WHERE is_super_admin = true;")
MODULE_COUNT1=$(psql -U postgres test_seed_db -tAc "SELECT COUNT(*) FROM modules;")

# Run seed script second time
python scripts/seed_all.py

# Count records again
ADMIN_COUNT2=$(psql -U postgres test_seed_db -tAc "SELECT COUNT(*) FROM users WHERE is_super_admin = true;")
MODULE_COUNT2=$(psql -U postgres test_seed_db -tAc "SELECT COUNT(*) FROM modules;")

# Compare counts
echo "Admin count: $ADMIN_COUNT1 vs $ADMIN_COUNT2"
echo "Module count: $MODULE_COUNT1 vs $MODULE_COUNT2"
```

**Expected Results**:
- Counts should be identical after second run
- Script should skip existing data
- Log messages should indicate "already exists - skipping"
- No duplicate records created

---

### Test 2.3: Skip Check Flag
**Objective**: Verify --skip-check flag forces seeding

**Test**:
```bash
# Run with skip-check flag
python scripts/seed_all.py --skip-check

# Check logs for seeding attempts
# Should show seeding attempts even if data exists
```

**Expected Results**:
- Script attempts to seed even if data exists
- Idempotency checks within individual seeds prevent duplicates
- All seeding steps execute

---

### Test 2.4: Partial Data Test
**Objective**: Verify script seeds missing components when some data exists

**Setup**:
```bash
# Create fresh database
psql -U postgres -c "DROP DATABASE IF EXISTS test_partial_db;"
psql -U postgres -c "CREATE DATABASE test_partial_db;"
alembic upgrade head

# Manually seed only super admin
python -c "
import asyncio
from app.core.seed_super_admin import seed_super_admin
from app.core.database import AsyncSessionLocal
async def seed():
    async with AsyncSessionLocal() as db:
        await seed_super_admin(db)
asyncio.run(seed())
"
```

**Test**:
```bash
# Run unified seed script
python scripts/seed_all.py

# Verify it detects and seeds missing data
```

**Expected Results**:
- Script detects super admin exists
- Script detects missing modules, permissions, templates
- Script seeds only missing components
- No errors occur

---

## 3. Auto-Seed on Boot Tests

### Test 3.1: First Boot Auto-Seed
**Objective**: Verify auto-seeding runs on first application startup

**Setup**:
```bash
# Create fresh database
psql -U postgres -c "DROP DATABASE IF EXISTS test_autoboot_db;"
psql -U postgres -c "CREATE DATABASE test_autoboot_db;"

# Update .env
export DATABASE_URL="postgresql://postgres:password@localhost:5432/test_autoboot_db"

# Run migrations only (no manual seeding)
alembic upgrade head
```

**Test**:
```bash
# Start the application
uvicorn app.main:app --reload &
APP_PID=$!

# Wait for startup
sleep 10

# Check logs for auto-seed messages
# Should see "Baseline data not found - starting auto-seed"

# Verify data was created
psql -U postgres test_autoboot_db -c "SELECT COUNT(*) FROM users WHERE is_super_admin = true;"

# Stop application
kill $APP_PID
```

**Expected Results**:
- Application starts successfully
- Auto-seed detection triggers
- Baseline data created
- Application continues running after seeding

---

### Test 3.2: Subsequent Boot (No Auto-Seed)
**Objective**: Verify auto-seed doesn't run when data exists

**Setup**: Use database from Test 3.1 (already has data)

**Test**:
```bash
# Start the application
uvicorn app.main:app --reload &
APP_PID=$!

# Wait for startup
sleep 10

# Check logs for skip message
# Should see "Baseline data exists - skipping auto-seed"

# Stop application
kill $APP_PID
```

**Expected Results**:
- Application starts successfully
- Auto-seed check runs
- Detects existing data
- Skips seeding
- No duplicate data created

---

### Test 3.3: Auto-Seed Error Handling
**Objective**: Verify application starts even if auto-seed fails

**Setup**:
```bash
# Create database with intentional issue
# e.g., missing a required table or constraint
```

**Test**:
```bash
# Start application
uvicorn app.main:app --reload &
APP_PID=$!

# Wait for startup
sleep 10

# Check if application is responsive
curl http://localhost:8000/health

# Stop application
kill $APP_PID
```

**Expected Results**:
- Application starts despite seed failure
- Error is logged but doesn't crash app
- Health endpoint responds
- Application is usable

---

## 4. Integration Tests

### Test 4.1: End-to-End Reset and Onboard
**Objective**: Test complete reset and user onboarding workflow

**Steps**:
```bash
# 1. Reset database
psql -U postgres fastapi_db -f sql/drop_all_tables.sql

# 2. Run migrations
alembic upgrade head

# 3. Start application (triggers auto-seed)
uvicorn app.main:app --reload &

# 4. Wait for startup
sleep 10

# 5. Test login with super admin
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "naughtyfruit53@gmail.com", "password": "123456"}' \
  | jq -r '.access_token')

# 6. Create organization
ORG_ID=$(curl -s -X POST http://localhost:8000/api/v1/organizations \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Org", "subdomain": "testorg"}' \
  | jq -r '.id')

# 7. Create user
USER_ID=$(curl -s -X POST http://localhost:8000/api/v1/users \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@testorg.com",
    "full_name": "Test User",
    "role": "admin",
    "organization_id": '$ORG_ID',
    "password": "password123"
  }' | jq -r '.id')

# 8. Login as new user
USER_TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@testorg.com", "password": "password123"}' \
  | jq -r '.access_token')

# 9. Test access to modules
curl -X GET http://localhost:8000/api/v1/inventory/items \
  -H "Authorization: Bearer $USER_TOKEN"
```

**Expected Results**:
- All steps complete successfully
- Super admin can login
- Organization created
- User created and can login
- User can access assigned modules

---

### Test 4.2: Migration Compatibility
**Objective**: Verify seeding works with existing migration history

**Test**:
```bash
# 1. Create database with old schema
# Use backup from previous version

# 2. Run migrations to latest
alembic upgrade head

# 3. Run seeding
python scripts/seed_all.py

# 4. Verify no conflicts or errors
```

**Expected Results**:
- Migrations apply cleanly
- Seeding completes without errors
- No foreign key violations
- All data accessible

---

## 5. Documentation Tests

### Test 5.1: README Quick Start
**Objective**: Follow README instructions exactly

**Steps**: Follow Quick Start section in README.md exactly as written

**Expected Results**:
- All commands work as documented
- Application starts successfully
- Login works with documented credentials

---

### Test 5.2: USER_GUIDE Workflows
**Objective**: Verify all workflows in USER_GUIDE.md

**Test Cases**:
1. Complete Fresh Start workflow (Section 2)
2. Migration commands (Section 3)
3. Manual seeding (Section 4)
4. Organization setup (Section 5)
5. Troubleshooting steps (Section 6)

**Expected Results**:
- All commands execute successfully
- All expected outcomes occur
- No errors or missing steps

---

### Test 5.3: DATABASE_RESET_GUIDE
**Objective**: Verify reset guide accuracy

**Test Cases**:
1. Quick Reset workflow
2. Complete Reset workflow
3. Migration management commands
4. Verification checklist

**Expected Results**:
- All commands work as documented
- All verification steps pass
- Guide is complete and accurate

---

## 6. Performance Tests

### Test 6.1: Seeding Performance
**Objective**: Measure seeding time

**Test**:
```bash
time python scripts/seed_all.py
```

**Expected Results**:
- Seeding completes in < 30 seconds
- No significant delays in any step

---

### Test 6.2: Startup Performance
**Objective**: Measure application startup time with auto-seed

**Test**:
```bash
# Fresh database
time uvicorn app.main:app

# Existing database
time uvicorn app.main:app
```

**Expected Results**:
- Fresh database startup: < 60 seconds
- Existing database startup: < 10 seconds
- Auto-seed doesn't significantly delay startup

---

## 7. Edge Cases and Error Handling

### Test 7.1: Database Connection Failure
**Test**: Start app with invalid DATABASE_URL

**Expected Results**:
- Clear error message
- Application doesn't crash
- Helpful troubleshooting info

---

### Test 7.2: Partial Migration State
**Test**: Interrupt migration mid-way

**Expected Results**:
- Can recover with downgrade/upgrade
- No corrupted state
- Clear error messages

---

### Test 7.3: Concurrent Seeding
**Test**: Run seed script multiple times simultaneously

**Expected Results**:
- One completes successfully
- Others fail gracefully
- No database corruption

---

## Test Execution Checklist

### Pre-Testing
- [ ] Backup production database
- [ ] Create test databases
- [ ] Install dependencies
- [ ] Configure test environment

### Core Tests
- [ ] Test 1.1: SQL Drop Script
- [ ] Test 1.2: Complete Reset Workflow
- [ ] Test 2.1: Fresh Database Seeding
- [ ] Test 2.2: Idempotency Test
- [ ] Test 2.3: Skip Check Flag
- [ ] Test 2.4: Partial Data Test
- [ ] Test 3.1: First Boot Auto-Seed
- [ ] Test 3.2: Subsequent Boot
- [ ] Test 3.3: Auto-Seed Error Handling

### Integration Tests
- [ ] Test 4.1: End-to-End Reset and Onboard
- [ ] Test 4.2: Migration Compatibility

### Documentation Tests
- [ ] Test 5.1: README Quick Start
- [ ] Test 5.2: USER_GUIDE Workflows
- [ ] Test 5.3: DATABASE_RESET_GUIDE

### Performance Tests
- [ ] Test 6.1: Seeding Performance
- [ ] Test 6.2: Startup Performance

### Edge Cases
- [ ] Test 7.1: Database Connection Failure
- [ ] Test 7.2: Partial Migration State
- [ ] Test 7.3: Concurrent Seeding

### Post-Testing
- [ ] Restore backups
- [ ] Clean up test databases
- [ ] Document any issues found
- [ ] Update documentation if needed

---

## Issue Tracking Template

When issues are found during testing, document them using this template:

```markdown
## Issue: [Brief Description]

**Test**: [Test number and name]
**Severity**: [Critical/High/Medium/Low]
**Date Found**: [Date]

**Steps to Reproduce**:
1. Step 1
2. Step 2
3. ...

**Expected Behavior**:
[What should happen]

**Actual Behavior**:
[What actually happened]

**Error Messages**:
```
[Any error messages or logs]
```

**Impact**:
[How this affects the system]

**Proposed Fix**:
[Suggested solution]

**Workaround**:
[Temporary workaround if available]
```

---

**Last Updated**: 2025-11-06  
**Status**: Ready for Testing  
**Test Environment**: PostgreSQL 14+, Python 3.9+, FastAPI 0.104+
