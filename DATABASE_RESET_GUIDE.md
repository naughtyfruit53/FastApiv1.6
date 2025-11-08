# Database Reset and Seeding Guide

Comprehensive guide for resetting the database, running migrations, and seeding data for the 3-layer security system.

## Overview

This guide covers:
- Complete database reset and rebuild
- Running Alembic migrations
- Seeding initial data with proper tenant/entitlement/RBAC setup
- Troubleshooting common issues

## Prerequisites

```bash
# Ensure environment is set up
source myenv/bin/activate  # or venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your database credentials
```

## Database Reset Workflows

### Quick Reset (Development)

For rapid development cycles when you need a fresh database:

```bash
# Method 1: Drop and recreate database
psql -U postgres -c "DROP DATABASE IF EXISTS fastapi_db;"
psql -U postgres -c "CREATE DATABASE fastapi_db;"

# Method 2: Using SQLAlchemy (if available)
python -c "from app.core.database import engine; from app.models import Base; Base.metadata.drop_all(engine); Base.metadata.create_all(engine)"

# Run migrations
alembic upgrade head

# Seed initial data
python scripts/seed_entitlements.py
python seed_hr_data.py
python seed_crm_marketing_service_data.py
```

### Complete Reset (Production-like)

For a complete reset that mimics production setup:

```bash
# 1. Backup current database (if needed)
pg_dump -U postgres fastapi_db > backup_$(date +%Y%m%d_%H%M%S).sql

# 2. Drop and recreate database
psql -U postgres -c "DROP DATABASE IF EXISTS fastapi_db;"
psql -U postgres -c "CREATE DATABASE fastapi_db;"

# 3. Run all migrations from scratch
alembic upgrade head

# 4. Verify migrations
alembic current
alembic history

# 5. Seed data in order
python scripts/seed_entitlements.py        # Entitlements first
python scripts/seed_test_emails.py          # Test email accounts
python seed_hr_data.py                      # HR master data
python seed_crm_marketing_service_data.py   # CRM data
python seed_asset_transport_data.py         # Asset/Transport data

# 6. Verify seeding
python -c "from app.core.database import get_db; from app.models import Organization; print(Organization.query.count(), 'organizations')"
```

## Migration Management

### Creating New Migrations

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "Add new security fields"

# Create empty migration for custom logic
alembic revision -m "Custom data migration"

# Edit the generated file in migrations/versions/
# Add upgrade() and downgrade() logic
```

### Running Migrations

```bash
# Upgrade to latest
alembic upgrade head

# Upgrade one version
alembic upgrade +1

# Downgrade one version
alembic downgrade -1

# Downgrade to specific version
alembic downgrade <revision_id>

# Show current version
alembic current

# Show migration history
alembic history --verbose
```

### Fixing Migration Issues

```bash
# If migrations are out of sync
alembic stamp head  # Mark current state as head

# If migration fails
alembic downgrade -1  # Rollback
# Fix the issue
alembic upgrade +1    # Try again

# If completely stuck
# 1. Note current version
alembic current
# 2. Reset alembic_version table
psql -U postgres fastapi_db -c "DELETE FROM alembic_version;"
# 3. Mark as current
alembic stamp head
```

## Seeding Data with 3-Layer Security

### 1. Seed Entitlements

**Script:** `scripts/seed_entitlements.py`

**Purpose:** Set up default module entitlements for organizations

```bash
python scripts/seed_entitlements.py
```

**What it does:**
- Creates default entitlement profiles (Free, Starter, Professional, Enterprise)
- Assigns module access based on tier
- Sets up trial periods where applicable
- Configures always-on modules (email, dashboard)
- Configures RBAC-only modules (settings, admin, organization)

**Expected Output:**
```
✓ Created entitlement profile: Free
  - Modules: email, dashboard, crm (trial)
✓ Created entitlement profile: Starter
  - Modules: email, dashboard, crm, sales, inventory
✓ Created entitlement profile: Professional
  - All standard modules enabled
✓ Created entitlement profile: Enterprise
  - All modules enabled including advanced features
```

### 2. Seed Organizations

**Purpose:** Create test organizations with proper entitlements

```python
# In seed script
from app.models import Organization
from app.core.constants import ModuleStatusEnum

org = Organization(
    name="Test Corp",
    enabled_modules={
        "CRM": True,
        "MANUFACTURING": True,
        "FINANCE": True,
    },
    # Other fields...
)
db.add(org)
db.commit()
```

**Best Practices:**
- Always set `enabled_modules` dictionary
- Use uppercase keys for modules (normalized to lowercase in code)
- Set `license_tier` to determine default entitlements
- Consider trial periods for testing

### 3. Seed Users with Roles

**Purpose:** Create users with appropriate roles and permissions

```python
from app.models import User
from app.core.constants import UserRole

# Create super admin (platform level)
super_admin = User(
    email="superadmin@example.com",
    role=UserRole.SUPER_ADMIN,
    organization_id=None,  # Platform level
    is_super_admin=True,
    # ...
)

# Create org admin
org_admin = User(
    email="admin@testcorp.com",
    role=UserRole.ADMIN,
    organization_id=org.id,
    is_company_admin=True,
    # ...
)

# Create manager with module assignments
manager = User(
    email="manager@testcorp.com",
    role=UserRole.MANAGER,
    organization_id=org.id,
    # Assign to CRM and Sales modules
)

# Create executive with submodule permissions
executive = User(
    email="executive@testcorp.com",
    role=UserRole.EXECUTIVE,
    organization_id=org.id,
    reports_to_id=manager.id,
    # Assign specific submodule permissions
)

db.add_all([super_admin, org_admin, manager, executive])
db.commit()
```

**Role Setup Guidelines:**

#### Super Admin
- `role = UserRole.SUPER_ADMIN`
- `organization_id = None`
- `is_super_admin = True`
- Can access any organization
- Platform-level access

#### Admin
- `role = UserRole.ADMIN`
- `organization_id = <org_id>`
- `is_company_admin = True`
- Full access within organization
- Can create managers and executives
- Still respects organization entitlements

#### Manager
- `role = UserRole.MANAGER`
- `organization_id = <org_id>`
- Assign to specific modules
- Full access to assigned modules
- Can create executives in their modules
- Can see team records

#### Executive
- `role = UserRole.EXECUTIVE`
- `organization_id = <org_id>`
- `reports_to_id = <manager_id>` (required)
- Granular submodule permissions
- Limited to own records
- Cannot create other users

### 4. Seed RBAC Permissions

**Purpose:** Set up permission structure for roles

```python
from app.models import Permission, RolePermission
from app.core.constants import UserRole

# Create permissions
permissions = [
    Permission(name="crm.read", description="Read CRM data"),
    Permission(name="crm.create", description="Create CRM records"),
    Permission(name="crm.update", description="Update CRM records"),
    Permission(name="crm.delete", description="Delete CRM records"),
    Permission(name="crm.*", description="Full CRM access"),
    Permission(name="crm_admin", description="CRM admin access"),
]

db.add_all(permissions)
db.commit()

# Assign permissions to roles
# Manager gets full module access
RolePermission(role=UserRole.MANAGER, permission_name="crm.*")
RolePermission(role=UserRole.MANAGER, permission_name="sales.*")

# Executive gets limited access
RolePermission(role=UserRole.EXECUTIVE, permission_name="crm_leads_read")
RolePermission(role=UserRole.EXECUTIVE, permission_name="crm_leads_create")
```

### 5. Seed Module-Specific Data

```bash
# HR data
python seed_hr_data.py

# CRM, Marketing, Service data
python seed_crm_marketing_service_data.py

# Asset and Transport data
python seed_asset_transport_data.py
```

**Important:** All seeded data must include `organization_id` for proper tenant isolation.

## Verification Checklist

After reset and seeding, verify the setup:

### 1. Database Structure
```bash
# Check tables exist
psql -U postgres fastapi_db -c "\dt"

# Check alembic version
psql -U postgres fastapi_db -c "SELECT * FROM alembic_version;"

# Check key tables
psql -U postgres fastapi_db -c "SELECT COUNT(*) FROM organizations;"
psql -U postgres fastapi_db -c "SELECT COUNT(*) FROM users;"
psql -U postgres fastapi_db -c "SELECT COUNT(*) FROM permissions;"
```

### 2. Organizations and Entitlements
```python
from app.core.database import get_db
from app.models import Organization

db = next(get_db())
orgs = db.query(Organization).all()

for org in orgs:
    print(f"Org: {org.name}")
    print(f"  Enabled Modules: {org.enabled_modules}")
    print(f"  License Tier: {org.license_tier}")
```

### 3. Users and Roles
```python
from app.models import User

users = db.query(User).all()

for user in users:
    print(f"User: {user.email}")
    print(f"  Role: {user.role}")
    print(f"  Org: {user.organization_id}")
    print(f"  Super Admin: {user.is_super_admin}")
```

### 4. Permissions
```python
from app.models import Permission, RolePermission

permissions = db.query(Permission).count()
role_perms = db.query(RolePermission).count()

print(f"Total Permissions: {permissions}")
print(f"Role Permissions: {role_perms}")
```

### 5. Test Authentication

```bash
# Start the server
uvicorn app.main:app --reload

# Test login (in another terminal)
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@testcorp.com",
    "password": "password123"
  }'

# Should return access token
```

### 6. Test 3-Layer Security

```bash
# Test with valid token
TOKEN="<access_token_from_login>"

# Should succeed - user has access
curl -X GET http://localhost:8000/api/v1/crm/leads \
  -H "Authorization: Bearer $TOKEN"

# Should fail 403 - no manufacturing entitlement
curl -X GET http://localhost:8000/api/v1/manufacturing/orders \
  -H "Authorization: Bearer $TOKEN"
```

## Troubleshooting

### Issue: Alembic reports "Can't locate revision"

**Solution:**
```bash
# Check migration files exist
ls migrations/versions/

# Reinitialize alembic
alembic stamp head

# If still failing, reset
rm migrations/versions/*.py
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### Issue: Foreign key constraint failures

**Solution:**
```bash
# Seed in correct order:
# 1. Organizations first
# 2. Users next (reference organizations)
# 3. Entitlements (reference organizations)
# 4. Permissions
# 5. Role permissions
# 6. Module data (reference organizations and users)
```

### Issue: org_id missing in queries

**Solution:**
Check that all queries use the standard pattern:
```python
# Good
auth: tuple = Depends(require_access("module", "read"))
current_user, org_id = auth

stmt = select(Model).where(Model.organization_id == org_id)

# Bad
current_user = Depends(get_current_active_user)
# org_id is undefined!
```

### Issue: Entitlement check always fails

**Solution:**
```python
# Check organization has modules enabled
org = db.query(Organization).first()
print(org.enabled_modules)  # Should be dict with module keys

# Check module keys are correct (case-insensitive)
# Both "CRM" and "crm" should work
```

### Issue: Permission denied for valid user

**Solution:**
```python
# Verify user has permissions
from app.services.rbac import RBACService

rbac = RBACService(db)
permissions = await rbac.get_user_service_permissions(user.id)
print(permissions)  # Should include required permission

# Check permission format
# Correct: "crm.read", "crm.*", "crm_admin"
# Incorrect: "crm-read", "crm read", "crm"
```

## Best Practices

### 1. Always Seed in Order
```
Organizations → Users → Entitlements → Permissions → Module Data
```

### 2. Use Transactions
```python
try:
    # Seed operations
    db.add_all([...])
    db.commit()
except Exception as e:
    db.rollback()
    raise
```

### 3. Validate After Seeding
Run the verification checklist after every seed operation.

### 4. Keep Seed Scripts Idempotent
```python
# Check if data exists before creating
existing = db.query(Organization).filter_by(name="Test Corp").first()
if not existing:
    org = Organization(name="Test Corp", ...)
    db.add(org)
```

### 5. Document Seed Dependencies
Include comments explaining what data must exist before running the script.

### 6. Test with Minimal Data First
Start with one organization, one user per role, basic permissions. Expand as needed.

## Quick Reference

### Common Commands

```bash
# Reset everything
alembic downgrade base && alembic upgrade head

# Seed fresh
python scripts/seed_entitlements.py && \
python seed_hr_data.py && \
python seed_crm_marketing_service_data.py

# Run tests
pytest app/tests/test_three_layer_security.py -v

# Start server
uvicorn app.main:app --reload --port 8000

# Check logs
tail -f logs/app.log
```

### Environment Variables

Key variables for database operations:

```bash
DATABASE_URL=postgresql://user:pass@localhost/fastapi_db
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

---

**Last Updated:** 2025-11-05
**Compatible With:** FastAPI v1.6, Alembic, PostgreSQL
**Status:** Production-ready
