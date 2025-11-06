# TritIQ Business Suite - User Guide

Complete guide for database reset, migration, seeding, and system onboarding.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Database Reset Workflow](#database-reset-workflow)
3. [Migration Guide](#migration-guide)
4. [Seeding Baseline Data](#seeding-baseline-data)
5. [User Onboarding](#user-onboarding)
6. [Troubleshooting](#troubleshooting)
7. [Advanced Operations](#advanced-operations)

---

## Quick Start

### Prerequisites

```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Set up environment variables
cp .env.example .env
# Edit .env with your database credentials

# 3. Ensure PostgreSQL/Supabase is running
```

### First Time Setup

```bash
# 1. Run database migrations
alembic upgrade head

# 2. Start the application (auto-seeding will run on first boot)
uvicorn app.main:app --reload

# That's it! The system will automatically seed baseline data.
```

### Default Credentials

After first boot, you can login with:
- **Email**: `naughtyfruit53@gmail.com`
- **Password**: `123456`
- **⚠️ IMPORTANT**: Change this password immediately after first login!

---

## Database Reset Workflow

### Complete Fresh Start

When you need to completely reset the database:

#### Step 1: Backup Current Data (Optional)

```bash
# Create a backup before dropping everything
pg_dump -U postgres -d your_database > backup_$(date +%Y%m%d_%H%M%S).sql
```

#### Step 2: Drop All Tables

```bash
# Option A: Using SQL script (RECOMMENDED)
psql -U postgres -d your_database

# In psql, edit the safety check in the SQL file first:
\e sql/drop_all_tables.sql
# Comment out the safety check line, then run:
\i sql/drop_all_tables.sql

# Option B: Drop and recreate database
psql -U postgres -c "DROP DATABASE IF EXISTS your_database;"
psql -U postgres -c "CREATE DATABASE your_database;"
```

#### Step 3: Run Migrations

```bash
# Apply all migrations to create fresh schema
alembic upgrade head

# Verify migrations applied successfully
alembic current
alembic history
```

#### Step 4: Seed Baseline Data

```bash
# Option A: Let the app auto-seed on startup (RECOMMENDED)
uvicorn app.main:app --reload
# The app will detect missing baseline data and seed automatically

# Option B: Manual seeding
python scripts/seed_all.py

# Option C: Force re-seed even if data exists
python scripts/seed_all.py --skip-check
```

#### Step 5: Verify Setup

```bash
# Start the application
uvicorn app.main:app --reload

# In another terminal, test the API
curl http://localhost:8000/health

# Test login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "naughtyfruit53@gmail.com", "password": "123456"}'
```

---

## Migration Guide

### Understanding Migrations

Alembic manages database schema changes. Each migration is a versioned script that can upgrade or downgrade your database schema.

### Common Migration Commands

```bash
# Show current migration version
alembic current

# Show migration history
alembic history --verbose

# Upgrade to latest version
alembic upgrade head

# Upgrade one version at a time
alembic upgrade +1

# Downgrade one version
alembic downgrade -1

# Downgrade to specific version
alembic downgrade <revision_id>

# Stamp database at current version (without running migrations)
alembic stamp head
```

### Creating New Migrations

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "Add new field to users table"

# Create empty migration for custom logic
alembic revision -m "Custom data migration"

# Edit the generated file in migrations/versions/
# Add upgrade() and downgrade() logic
```

### Migration Troubleshooting

#### Issue: "Can't locate revision"

```bash
# Check migration files exist
ls migrations/versions/

# Reset alembic version table
psql -U postgres your_database -c "DELETE FROM alembic_version;"
alembic stamp head
```

#### Issue: Migration fails mid-way

```bash
# Downgrade to previous version
alembic downgrade -1

# Fix the issue in code or migration script
# Try again
alembic upgrade +1
```

#### Issue: Migrations out of sync

```bash
# Mark current state as head without running migrations
alembic stamp head
```

---

## Seeding Baseline Data

### What Gets Seeded

The unified seeding script (`scripts/seed_all.py`) creates:

1. **Super Admin User**
   - Platform-level admin account
   - Email: naughtyfruit53@gmail.com
   - Full system access

2. **Module Taxonomy**
   - All system modules (Sales, Inventory, Manufacturing, etc.)
   - Submodules for granular entitlements
   - Module metadata and configuration

3. **RBAC Permissions**
   - Default service permissions
   - Default roles (org_admin, etc.)
   - Role-permission mappings

4. **Chart of Accounts**
   - Standard CoA structure
   - Default account categories
   - Basic financial setup

5. **Voucher Templates**
   - System voucher format templates
   - Standard, Modern, Classic, Minimal styles

6. **Organization Defaults**
   - Default enabled modules for organizations
   - Basic organization configuration

### Manual Seeding

```bash
# Run the unified seeding script
python scripts/seed_all.py

# The script is idempotent - it checks for existing data before seeding
# To force re-seed (not recommended unless you know what you're doing):
python scripts/seed_all.py --skip-check
```

### Auto-Seeding on First Boot

The system automatically checks for baseline data on startup and seeds if needed:

1. Checks for super admin user
2. Checks for module taxonomy
3. Checks for RBAC permissions
4. Checks for voucher templates
5. If any are missing, runs unified seeding automatically

**This means you typically don't need to run seeding manually!**

### Seeding Test/Demo Data

For development or demonstration purposes, additional demo data can be seeded:

```bash
# These scripts create sample business data (not essential for operation)
python scripts/archive/demo/seed_hr_data.py
python scripts/archive/demo/seed_crm_marketing_service_data.py
python scripts/archive/demo/seed_asset_transport_data.py
```

⚠️ **Note**: Demo data scripts are in the archive and are optional.

---

## User Onboarding

### Organization Setup

#### 1. Create Organization

After logging in as super admin:

```bash
# Via API
curl -X POST http://localhost:8000/api/v1/organizations \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Your Company Name",
    "subdomain": "yourcompany",
    "enabled_modules": {
      "sales": true,
      "inventory": true,
      "manufacturing": true
    }
  }'
```

Or use the frontend UI: Settings → Organizations → Create New

#### 2. Create Admin User

```bash
# Via API
curl -X POST http://localhost:8000/api/v1/users \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@yourcompany.com",
    "full_name": "Admin User",
    "role": "admin",
    "organization_id": 1,
    "password": "secure_password"
  }'
```

#### 3. Assign Modules and Permissions

Navigate to: Settings → Entitlements → Assign Modules

Or via API:
```bash
curl -X POST http://localhost:8000/api/v1/organizations/1/entitlements \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "modules": ["sales", "inventory", "manufacturing"],
    "license_tier": "professional"
  }'
```

### Adding New Users

#### Standard User Creation

```bash
curl -X POST http://localhost:8000/api/v1/users \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@yourcompany.com",
    "full_name": "New User",
    "role": "manager",
    "organization_id": 1,
    "password": "initial_password"
  }'
```

#### Assign RBAC Roles

```bash
curl -X POST http://localhost:8000/api/v1/rbac/users/{user_id}/roles \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "role_id": 1
  }'
```

### Module Access Control

The system uses a 3-layer security model:

1. **Organization Entitlements** - What modules the organization has access to
2. **User Roles** - What permissions users have within allowed modules
3. **RBAC Permissions** - Granular action-level permissions

Example workflow:
1. Enable modules for organization in entitlements
2. Create roles with specific permissions
3. Assign roles to users

---

## Troubleshooting

### Database Connection Issues

```bash
# Check PostgreSQL is running
pg_isready -h localhost -p 5432

# Test connection with psql
psql -U postgres -d your_database -c "SELECT 1;"

# Check DATABASE_URL in .env
echo $DATABASE_URL
```

### Migration Issues

```bash
# Check alembic version
alembic current

# If stuck, reset alembic state
psql -U postgres your_database -c "DELETE FROM alembic_version;"
alembic stamp head

# Then try migration again
alembic upgrade head
```

### Seeding Issues

```bash
# Check if super admin exists
python -c "
from app.core.database import SessionLocal
from app.models.user_models import User
db = SessionLocal()
admin = db.query(User).filter(User.is_super_admin == True).first()
print(f'Super admin exists: {admin is not None}')
"

# Force re-seed if needed
python scripts/seed_all.py --skip-check
```

### Authentication Issues

```bash
# Test login endpoint
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "naughtyfruit53@gmail.com", "password": "123456"}'

# Check user exists
psql -U postgres your_database -c "SELECT id, email, role FROM users LIMIT 5;"
```

### Permission Denied Errors

```bash
# Check organization enabled_modules
psql -U postgres your_database -c "SELECT id, name, enabled_modules FROM organizations;"

# Check user roles
psql -U postgres your_database -c "
  SELECT u.email, r.name as role_name 
  FROM users u 
  JOIN user_service_roles usr ON u.id = usr.user_id 
  JOIN service_roles r ON usr.role_id = r.id;
"

# Check RBAC permissions
curl -X GET http://localhost:8000/api/v1/rbac/users/{user_id}/permissions \
  -H "Authorization: Bearer <token>"
```

---

## Advanced Operations

### Environment-Specific Configuration

```bash
# Development
export DATABASE_URL="postgresql://user:pass@localhost/dev_db"
export DEBUG=True

# Production
export DATABASE_URL="postgresql://user:pass@prod.server/prod_db"
export DEBUG=False
export SECRET_KEY="your-production-secret-key"
```

### Backup and Restore

```bash
# Backup
pg_dump -U postgres your_database > backup.sql

# Restore
psql -U postgres your_database < backup.sql
```

### Performance Monitoring

```bash
# Check slow queries
psql -U postgres your_database -c "
  SELECT query, calls, total_time, mean_time 
  FROM pg_stat_statements 
  ORDER BY mean_time DESC 
  LIMIT 10;
"

# Check connection pool
curl http://localhost:8000/api/v1/debug/db-stats
```

### Database Maintenance

```bash
# Vacuum database
psql -U postgres your_database -c "VACUUM ANALYZE;"

# Reindex
psql -U postgres your_database -c "REINDEX DATABASE your_database;"

# Check table sizes
psql -U postgres your_database -c "
  SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
  FROM pg_tables
  WHERE schemaname = 'public'
  ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
"
```

---

## Additional Resources

- **RBAC Documentation**: See `RBAC_COMPREHENSIVE_GUIDE.md` for detailed RBAC setup
- **Entitlement Guide**: See `MODULE_ENTITLEMENT_RESTRICTIONS_GUIDE.md` for module access control
- **Database Reset**: See `DATABASE_RESET_GUIDE.md` for detailed reset procedures
- **API Documentation**: Access `/docs` when the app is running
- **Testing Guide**: See `TESTING_GUIDE.md` for testing procedures

---

## Support and Contact

For issues, questions, or contributions:
- Create an issue on GitHub
- Review `CONTRIBUTING.md` for contribution guidelines
- Check existing documentation in the `docs/` directory

---

**Last Updated**: 2025-11-06  
**Version**: 1.6  
**Status**: Production Ready
