# Migration Guide: Transitioning to Strict Permission Enforcement

## Overview

This guide helps you migrate from the permissive access control model to the new strict enforcement model. The migration requires configuration changes to ensure all users have explicit permissions and entitlements.

⚠️ **WARNING**: This is a breaking change. Super admins will lose automatic access to all features. Plan the migration carefully.

---

## Pre-Migration Checklist

### 1. Document Current Access Patterns

**Action Items:**
- [ ] List all super admin users
- [ ] Document which modules each super admin accesses
- [ ] List all organizations and their active modules
- [ ] Document custom roles and their permissions
- [ ] Identify users with cross-organization access needs

**Commands to run:**
```bash
# List all super admin users
python scripts/list_all_users.py --role super_admin

# Check organization modules
python scripts/list_orgs_users.py
```

### 2. Backup Current Configuration

**Action Items:**
- [ ] Export all user permissions
- [ ] Export all role definitions
- [ ] Export organization module configurations
- [ ] Create database backup

**SQL Queries:**
```sql
-- Export user permissions
COPY (
  SELECT u.id, u.email, u.role, u.organization_id, ur.role_id, r.name as role_name
  FROM users u
  LEFT JOIN user_service_roles ur ON u.id = ur.user_id
  LEFT JOIN service_roles r ON ur.role_id = r.id
) TO '/tmp/user_permissions_backup.csv' WITH CSV HEADER;

-- Export organization modules
COPY (
  SELECT id, name, enabled_modules
  FROM organizations
) TO '/tmp/org_modules_backup.csv' WITH CSV HEADER;
```

### 3. Test in Staging Environment

**Action Items:**
- [ ] Deploy changes to staging
- [ ] Test super admin access
- [ ] Test regular user access
- [ ] Verify error messages
- [ ] Test permission assignment flow

---

## Migration Steps

### Step 1: Configure Organization Entitlements

All organizations must have explicit module entitlements configured.

#### 1.1 Audit Current Modules

```python
# Script: audit_current_modules.py
from app.services.organizationService import OrganizationService

async def audit_modules():
    orgs = await OrganizationService.get_all_organizations()
    
    for org in orgs:
        print(f"\nOrganization: {org.name} (ID: {org.id})")
        print(f"Enabled Modules: {org.enabled_modules}")
        
        # Check for missing entitlements
        if not org.enabled_modules:
            print("⚠️ WARNING: No modules enabled!")
```

#### 1.2 Enable Required Modules

For each organization, enable the modules they need:

```python
# Script: enable_org_modules.py
from app.services.organizationService import OrganizationService

async def enable_modules(org_id: int, modules: list[str]):
    """
    Enable modules for an organization
    
    Args:
        org_id: Organization ID
        modules: List of module keys (e.g., ['sales', 'crm', 'inventory'])
    """
    enabled_modules = {
        module.upper(): True
        for module in modules
    }
    
    await OrganizationService.update_organization(
        org_id=org_id,
        enabled_modules=enabled_modules
    )
    
    print(f"✅ Enabled modules for org {org_id}: {', '.join(modules)}")

# Usage
await enable_modules(
    org_id=1,
    modules=['sales', 'crm', 'inventory', 'manufacturing']
)
```

#### 1.3 Verify Entitlements via API

```bash
# Check organization entitlements
curl -X GET "https://api.example.com/api/v1/entitlements?organization_id=1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Expected Response:**
```json
{
  "organization_id": 1,
  "entitlements": {
    "sales": {
      "status": "enabled",
      "submodules": {
        "quotations": true,
        "orders": true
      }
    },
    "crm": {
      "status": "enabled",
      "submodules": {}
    }
  }
}
```

### Step 2: Configure Super Admin Permissions

Super admins need explicit permissions assigned.

#### 2.1 Create Super Admin Role

```python
# Script: create_super_admin_role.py
from app.services.rbac import RBACService
from app.schemas.rbac import ServiceRoleCreate

async def create_super_admin_role(org_id: int):
    """Create comprehensive super admin role"""
    
    # Get all available permissions
    permissions = await RBACService.get_permissions()
    permission_ids = [p.id for p in permissions]
    
    role_data = ServiceRoleCreate(
        name="super_admin",
        display_name="Super Administrator",
        description="Full access to all features with explicit permissions",
        organization_id=org_id,
        permission_ids=permission_ids
    )
    
    role = await RBACService.create_role(role_data, created_by_user_id=1)
    print(f"✅ Created super admin role with {len(permission_ids)} permissions")
    return role
```

#### 2.2 Assign Role to Super Admins

```python
# Script: assign_super_admin_roles.py
from app.services.rbac import RBACService

async def assign_super_admin_roles(org_id: int):
    """Assign super admin role to all super admin users"""
    
    # Get super admin role
    roles = await RBACService.get_roles(org_id)
    super_admin_role = next(r for r in roles if r.name == "super_admin")
    
    # Get all super admin users
    users = await UserService.get_users_by_role(org_id, "super_admin")
    
    for user in users:
        await RBACService.assign_role_to_user(
            user_id=user.id,
            role_id=super_admin_role.id,
            assigned_by_id=1
        )
        print(f"✅ Assigned super admin role to {user.email}")
```

### Step 3: Configure Regular User Permissions

#### 3.1 Map Old Roles to New Permissions

| Old Role | New Permissions Required |
|----------|-------------------------|
| finance_manager | finance.*, accounting.*, reports.viewFinancial |
| sales_manager | sales.*, crm.*, reports.viewOperational |
| inventory_manager | inventory.*, master_data.view, reports.viewInventory |
| hr_manager | hr.*, master_data.view, reports.viewHR |
| user | dashboard.view, email.* |

#### 3.2 Bulk Assign Permissions

```python
# Script: bulk_assign_permissions.py
from app.services.rbac import RBACService

async def bulk_assign_by_role(org_id: int):
    """Assign permissions based on user role"""
    
    role_permission_map = {
        "finance_manager": ["finance_read", "finance_write", "accounting_read"],
        "sales_manager": ["sales_read", "sales_write", "crm_read", "crm_write"],
        "inventory_manager": ["inventory_read", "inventory_write"],
    }
    
    for role_name, permissions in role_permission_map.items():
        users = await UserService.get_users_by_role(org_id, role_name)
        
        for user in users:
            # Create or get role
            service_role = await RBACService.get_or_create_role(
                org_id=org_id,
                name=role_name,
                permissions=permissions
            )
            
            # Assign role
            await RBACService.assign_role_to_user(
                user_id=user.id,
                role_id=service_role.id
            )
            
            print(f"✅ Assigned {role_name} permissions to {user.email}")
```

### Step 4: Update Frontend Configuration

#### 4.1 Clear Browser Caches

Users may have cached old permission data:

```javascript
// Add to login handler
localStorage.removeItem('userPermissions');
localStorage.removeItem('userEntitlements');
sessionStorage.clear();
```

#### 4.2 Update Environment Variables

```bash
# .env.local
NEXT_PUBLIC_STRICT_ENFORCEMENT=true
ENABLE_ENTITLEMENTS_GATING=true  # This is now hardcoded to true, but document it
```

### Step 5: Deploy the Changes

#### 5.1 Pre-Deployment

```bash
# Run database migrations
alembic upgrade head

# Verify migrations
python -c "from app.api.deps.entitlements import ENABLE_ENTITLEMENTS_GATING; print(f'Strict enforcement: {ENABLE_ENTITLEMENTS_GATING}')"
```

#### 5.2 Deployment Order

1. **Database migrations** (if any)
2. **Backend deployment** (API changes)
3. **Frontend deployment** (UI changes)
4. **Verify deployment** (health checks)
5. **Monitor logs** (access denied errors)

#### 5.3 Post-Deployment Verification

```bash
# Test super admin access
curl -X GET "https://api.example.com/api/v1/sales/dashboard" \
  -H "Authorization: Bearer SUPER_ADMIN_TOKEN"

# Should return 403 if entitlement not configured

# Test with entitlement
# Configure org entitlements first, then retry
```

### Step 6: Monitor and Adjust

#### 6.1 Monitor Access Logs

```bash
# Watch for 403 Forbidden errors
tail -f /var/log/fastapi/access.log | grep "403"

# Check error patterns
grep "EntitlementDeniedError\|PermissionDeniedError" /var/log/fastapi/error.log | tail -50
```

#### 6.2 Create Monitoring Alerts

```yaml
# Example Prometheus alert
- alert: HighPermissionDeniedRate
  expr: rate(http_requests_total{status="403"}[5m]) > 10
  for: 5m
  annotations:
    summary: "High rate of permission denied errors"
```

#### 6.3 Collect User Feedback

Create a feedback form for access issues:
- What were you trying to access?
- What error did you see?
- What is your role?
- What organization are you in?

---

## Rollback Plan

If issues arise, you can roll back:

### Option 1: Code Rollback (Recommended)

```bash
# Revert to previous version
git revert <commit-hash>
git push origin main

# Redeploy previous version
./deploy.sh
```

### Option 2: Emergency Entitlement Grant

Temporarily grant all modules to all organizations:

```python
# Emergency script - USE WITH CAUTION
async def emergency_enable_all():
    """Grant all modules to all organizations temporarily"""
    all_modules = [
        'sales', 'crm', 'inventory', 'manufacturing', 
        'hr', 'finance', 'analytics'
    ]
    
    orgs = await OrganizationService.get_all_organizations()
    for org in orgs:
        enabled_modules = {m.upper(): True for m in all_modules}
        await OrganizationService.update_organization(
            org_id=org.id,
            enabled_modules=enabled_modules
        )
```

---

## Common Issues and Solutions

### Issue 1: Super Admin Cannot Access Anything

**Symptoms:**
- Super admin sees all menus disabled
- Gets 403 errors on all requests
- Dashboard is empty

**Root Cause:**
- Organization entitlements not configured
- Super admin role doesn't have permissions

**Solution:**
```python
# 1. Configure org entitlements
await enable_modules(org_id=1, modules=['sales', 'crm', 'inventory'])

# 2. Assign permissions to super admin
await assign_super_admin_roles(org_id=1)

# 3. Verify
permissions = await RBACService.get_user_permissions(super_admin_user_id)
print(f"Super admin has {len(permissions)} permissions")
```

### Issue 2: Regular Users Lose Access

**Symptoms:**
- Users who previously had access now get 403
- Error: "Permission denied"

**Root Cause:**
- Old role-based permissions not migrated
- Missing explicit permission assignments

**Solution:**
```python
# Bulk assign permissions based on old roles
await bulk_assign_by_role(org_id=1)

# Or assign individually
await RBACService.assign_permissions_to_user(
    user_id=user.id,
    permissions=["sales_read", "sales_write"]
)
```

### Issue 3: Module Shows as Disabled

**Symptoms:**
- Menu item is grayed out
- Tooltip says "Module disabled"

**Root Cause:**
- Organization entitlement not configured

**Solution:**
```python
# Enable module for organization
await OrganizationService.update_organization(
    org_id=1,
    enabled_modules={"SALES": True}
)
```

### Issue 4: Cross-Organization Access Broken

**Symptoms:**
- Super admin can't switch between organizations
- Error: "Organization context required"

**Root Cause:**
- Organization context not being set in session

**Solution:**
```python
# Set organization context when super admin switches orgs
from app.core.tenant import TenantContext

TenantContext.set_organization_id(target_org_id)
```

---

## Testing Checklist

After migration, verify:

- [ ] Super admins can access enabled modules
- [ ] Super admins cannot access disabled modules
- [ ] Regular users can access permitted features
- [ ] Regular users cannot access restricted features
- [ ] Error messages are clear and actionable
- [ ] Menu items show correct enabled/disabled state
- [ ] Trial modules show "Trial" badge
- [ ] Expired trials are disabled
- [ ] Email module is always accessible
- [ ] Settings module is accessible (RBAC-only)

---

## Communication Templates

### Email to Super Admins

**Subject:** Important: Permission System Update - Action Required

Dear Super Administrator,

We've upgraded our permission system to enhance security. As part of this change:

**What Changed:**
- Super admins no longer have automatic access to all features
- You now need explicit permissions assigned

**What You Need to Do:**
1. Review your current access needs
2. Contact IT to assign appropriate permissions
3. Verify your organization's enabled modules

**Timeline:**
- Staging deployment: [DATE]
- Production deployment: [DATE]

If you experience access issues after [DATE], please contact IT immediately.

### Slack Message to Development Team

```
🚨 Migration Alert: Strict Permission Enforcement

We're deploying strict permission enforcement on [DATE].

Key Changes:
• Super admin bypass removed
• Explicit permissions required for all users
• Module entitlements must be configured

Action Items:
1. Review migration guide: [LINK]
2. Test in staging
3. Prepare rollback plan
4. Monitor #alerts channel post-deployment

Questions? Ask in #dev-support
```

---

## Support Resources

- **Documentation**: See STRICT_PERMISSION_ENFORCEMENT_GUIDE.md
- **Issue Tracker**: GitHub Issue #185
- **Comparison Table**: main-production-comparison.md
- **Test Examples**: app/tests/test_strict_*.py

---

## Post-Migration Audit

Run this audit 1 week after migration:

```python
# Script: post_migration_audit.py
async def audit_access_denials():
    """Audit access denied errors after migration"""
    
    # Check error logs
    denials = await get_access_denials_last_7_days()
    
    print(f"\n📊 Access Denial Statistics (Last 7 Days)")
    print(f"Total denials: {len(denials)}")
    print(f"Unique users affected: {len(set(d.user_id for d in denials))}")
    print(f"Most common modules: {get_top_denied_modules(denials)}")
    print(f"Most common reasons: {get_top_denial_reasons(denials)}")
    
    # Suggest fixes
    print(f"\n💡 Suggested Actions:")
    for user_id, count in get_users_with_most_denials(denials):
        user = await UserService.get_user(user_id)
        print(f"- Review permissions for {user.email} ({count} denials)")
```

---

## Success Metrics

Track these metrics to measure migration success:

| Metric | Target | How to Measure |
|--------|--------|----------------|
| 403 Error Rate | < 2% of requests | Monitor HTTP 403 responses |
| Support Tickets | < 10 per week | Track access-related tickets |
| User Satisfaction | > 90% | Post-migration survey |
| Configuration Time | < 30 min per org | Time to configure entitlements |
| Rollbacks | 0 | Deployment success rate |

---

## Timeline Template

| Phase | Duration | Activities |
|-------|----------|------------|
| Pre-Migration | Week 1-2 | Documentation, backup, staging tests |
| Configuration | Week 3 | Configure entitlements and permissions |
| Staging Deploy | Week 4 | Deploy to staging, run tests |
| Production Deploy | Week 5 | Deploy to production, monitor closely |
| Post-Migration | Week 6-8 | Monitor, adjust, audit |

---

## Conclusion

The migration to strict enforcement enhances security but requires careful planning. Follow this guide step-by-step, test thoroughly in staging, and monitor closely after production deployment.

**Remember**: It's better to delay deployment and configure properly than to rush and lose user access.

Good luck with your migration! 🚀
