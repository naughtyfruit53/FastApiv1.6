# RBAC Enforcement Migration Guide - Phase 6

## Overview

This guide provides step-by-step instructions for migrating backend API endpoints to use centralized RBAC and tenant isolation enforcement.

## Goal

Migrate all remaining 78 backend files to use `app.core.enforcement.require_access` for consistent security enforcement.

## Migration Checklist

### Files Completed
- [x] `app/api/customers.py` - 13 endpoints migrated ✅
- [x] `app/api/notifications.py` - 8 endpoints (completed in Phase 5) ✅
- [x] All voucher modules - 18 files (completed in Phase 4) ✅
- [x] All manufacturing modules - 10 files (completed in Phase 3) ✅

### Files Remaining (78 total)

#### Priority 1: Core Business (4 files)
- [ ] `app/api/vendors.py` - Vendor management
- [ ] `app/api/products.py` - Product catalog  
- [ ] `app/api/companies.py` - Company management
- [ ] `app/api/pincode.py` - Pincode lookup

#### Priority 2: ERP Core (6 files)
- [ ] `app/api/v1/accounts.py`
- [ ] `app/api/v1/chart_of_accounts.py`
- [ ] `app/api/v1/ledger.py`
- [ ] `app/api/v1/expense_account.py`
- [ ] `app/api/v1/gst.py`
- [ ] `app/api/v1/contacts.py`

#### Priority 3: Admin & RBAC (8 files)
- [ ] `app/api/routes/admin.py`
- [ ] `app/api/v1/organizations/routes.py`
- [ ] `app/api/v1/organizations/user_routes.py`
- [ ] `app/api/v1/organizations/settings_routes.py`
- [ ] `app/api/v1/organizations/module_routes.py`
- [ ] `app/api/v1/organizations/license_routes.py`
- [ ] `app/api/v1/organizations/invitation_routes.py`
- [ ] `app/api/v1/user.py`

#### Priority 4: Analytics (7 files)
- [ ] `app/api/customer_analytics.py`
- [ ] `app/api/management_reports.py`
- [ ] `app/api/v1/reporting_hub.py`
- [ ] `app/api/v1/service_analytics.py`
- [ ] `app/api/v1/streaming_analytics.py`
- [ ] `app/api/v1/ai_analytics.py`
- [ ] `app/api/v1/ml_analytics.py`

#### Priority 5: Integrations (5 files)
- [ ] `app/api/v1/tally.py`
- [ ] `app/api/v1/oauth.py`
- [ ] `app/api/v1/email.py`
- [ ] `app/api/v1/mail.py`
- [ ] `app/api/platform.py`

#### Priority 6: AI Features (7 files)
- [ ] `app/api/v1/ai.py`
- [ ] `app/api/v1/ai_agents.py`
- [ ] `app/api/v1/chatbot.py`
- [ ] `app/api/v1/forecasting.py`
- [ ] `app/api/v1/financial_modeling.py`
- [ ] `app/api/v1/ml_algorithms.py`
- [ ] `app/api/v1/automl.py`

#### Priority 7: Supporting (8 files)
- [ ] `app/api/v1/assets.py`
- [ ] `app/api/v1/transport.py`
- [ ] `app/api/v1/calendar.py`
- [ ] `app/api/v1/tasks.py`
- [ ] `app/api/v1/project_management.py`
- [ ] `app/api/v1/workflow_approval.py`
- [ ] `app/api/v1/audit_log.py`
- [ ] `app/api/v1/feedback.py`

#### Priority 8: Utility (7 files)
- [ ] `app/api/settings.py`
- [ ] `app/api/v1/company_branding.py`
- [ ] `app/api/v1/seo.py`
- [ ] `app/api/v1/marketing.py`
- [ ] `app/api/v1/ab_testing.py`
- [ ] `app/api/v1/plugin.py`
- [ ] `app/api/v1/explainability.py`

#### Special Cases (26 files)
These files may not need migration or require special handling:
- Authentication/Login: `app/api/v1/auth.py`, `app/api/v1/login.py`, `app/api/v1/password.py`, `app/api/v1/otp.py`, `app/api/v1/reset.py`, `app/api/v1/master_auth.py`
- Health/Status: `app/api/v1/health.py`
- System: `app/api/v1/migration.py`, `app/api/v1/admin_setup.py`, `app/api/v1/payroll_migration.py`
- Utilities: `app/api/v1/pdf_generation.py`, `app/api/v1/pdf_extraction.py`, `app/api/v1/voucher_email_templates.py`, `app/api/v1/voucher_format_templates.py`
- External: `app/api/v1/api_gateway.py`, `app/api/v1/website_agent.py`, `app/api/v1/exhibition.py`
- Background: `app/api/routes/websocket.py`
- Others: `app/api/v1/app_users.py`, `app/api/v1/bom.py`, `app/api/v1/gst_search.py`, `app/api/v1/sla.py`, `app/api/manufacturing/schemas.py`, `app/api/v1/organizations/services.py`, `app/api/v1/organizations/utils.py`

## Step-by-Step Migration Process

### Step 1: Update Imports

**Remove:**
```python
from app.api.v1.auth import get_current_active_user, get_current_admin_user
from app.core.tenant import TenantQueryMixin, TenantQueryFilter
from app.core.org_restrictions import require_current_organization_id
from app.core.rbac_dependencies import check_service_permission
```

**Add:**
```python
from app.core.enforcement import require_access
```

### Step 2: Update Endpoint Signatures

**Before:**
```python
@router.get("/items")
async def get_items(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get items"""
    org_id = require_current_organization_id(current_user)
    # ... rest of function
```

**After:**
```python
@router.get("/items")
async def get_items(
    skip: int = 0,
    limit: int = 100,
    auth: tuple = Depends(require_access("module_name", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get items"""
    current_user, org_id = auth
    # ... rest of function
```

### Step 3: Choose Correct Action

Map HTTP methods and operation types to RBAC actions:

| HTTP Method | Operation | RBAC Action |
|-------------|-----------|-------------|
| GET (list/search) | Read data | `"read"` |
| GET (single item) | Read data | `"read"` |
| POST | Create new | `"create"` |
| PUT/PATCH | Update existing | `"update"` |
| DELETE | Delete existing | `"delete"` |
| Export/Download | Read data | `"read"` |
| Import/Upload | Create/Update | `"create"` |

### Step 4: Choose Correct Module Name

Use the primary entity or feature the endpoint manages:

| File Path | Module Name | Example Actions |
|-----------|-------------|-----------------|
| `app/api/vendors.py` | `"vendor"` | vendor_read, vendor_create |
| `app/api/products.py` | `"product"` | product_read, product_create |
| `app/api/v1/ledger.py` | `"ledger"` | ledger_read, ledger_update |
| `app/api/v1/assets.py` | `"asset"` | asset_read, asset_create |

### Step 5: Remove Manual Organization Scoping

**Before:**
```python
if not current_user.is_super_admin:
    org_id = current_user.organization_id
    if org_id is None:
        raise HTTPException(...)
    stmt = TenantQueryMixin.filter_by_tenant(stmt, org_id)
```

**After:**
```python
# org_id already enforced by require_access
stmt = stmt.where(Model.organization_id == org_id)
```

### Step 6: Remove Manual Permission Checks

**Before:**
```python
rbac = RBACService(db)
if not rbac.user_has_service_permission(current_user.id, "module_action"):
    raise HTTPException(status_code=403, ...)
```

**After:**
```python
# Permission already enforced by require_access - remove manual check
```

### Step 7: Update Error Responses

All access denials should return 404 (not found) instead of 403 (forbidden) for anti-enumeration:

**Before:**
```python
if not customer:
    raise HTTPException(status_code=404, detail="Customer not found")

if customer.organization_id != org_id:
    raise HTTPException(status_code=403, detail="Access denied")
```

**After:**
```python
stmt = select(Customer).where(
    Customer.id == customer_id,
    Customer.organization_id == org_id  # Combines existence and access check
)
result = await db.execute(stmt)
customer = result.scalar_one_or_none()

if not customer:
    raise HTTPException(status_code=404, detail="Customer not found")
```

### Step 8: Remove Super Admin Overrides

**Before:**
```python
if current_user.is_super_admin:
    # Special logic for super admin
    stmt = select(Model)
else:
    stmt = select(Model).where(Model.organization_id == org_id)
```

**After:**
```python
# Super admin handling is in enforcement layer
stmt = select(Model).where(Model.organization_id == org_id)
```

## Common Patterns

### Pattern 1: List Endpoint

```python
@router.get("", response_model=List[ItemInDB])
async def get_items(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    auth: tuple = Depends(require_access("item", "read")),
    db: AsyncSession = Depends(get_db)
):
    """List all items"""
    current_user, org_id = auth
    
    stmt = select(Item).where(Item.organization_id == org_id)
    
    if search:
        stmt = stmt.where(Item.name.contains(search))
    
    result = await db.execute(stmt.offset(skip).limit(limit))
    return result.scalars().all()
```

### Pattern 2: Get Single Item

```python
@router.get("/{item_id}", response_model=ItemInDB)
async def get_item(
    item_id: int,
    auth: tuple = Depends(require_access("item", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get item by ID"""
    current_user, org_id = auth
    
    stmt = select(Item).where(
        Item.id == item_id,
        Item.organization_id == org_id
    )
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    return item
```

### Pattern 3: Create Item

```python
@router.post("", response_model=ItemInDB)
async def create_item(
    item_data: ItemCreate,
    auth: tuple = Depends(require_access("item", "create")),
    db: AsyncSession = Depends(get_db)
):
    """Create new item"""
    current_user, org_id = auth
    
    # Create with organization_id
    db_item = Item(
        organization_id=org_id,
        **item_data.dict()
    )
    
    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)
    
    return db_item
```

### Pattern 4: Update Item

```python
@router.put("/{item_id}", response_model=ItemInDB)
async def update_item(
    item_id: int,
    item_update: ItemUpdate,
    auth: tuple = Depends(require_access("item", "update")),
    db: AsyncSession = Depends(get_db)
):
    """Update item"""
    current_user, org_id = auth
    
    # Verify exists and belongs to org
    stmt = select(Item).where(
        Item.id == item_id,
        Item.organization_id == org_id
    )
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    # Update fields
    for field, value in item_update.dict(exclude_unset=True).items():
        setattr(item, field, value)
    
    await db.commit()
    await db.refresh(item)
    
    return item
```

### Pattern 5: Delete Item

```python
@router.delete("/{item_id}")
async def delete_item(
    item_id: int,
    auth: tuple = Depends(require_access("item", "delete")),
    db: AsyncSession = Depends(get_db)
):
    """Delete item"""
    current_user, org_id = auth
    
    # Verify exists and belongs to org
    stmt = select(Item).where(
        Item.id == item_id,
        Item.organization_id == org_id
    )
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    await db.delete(item)
    await db.commit()
    
    return {"message": "Item deleted successfully"}
```

## Verification Checklist

After migrating each file, verify:

- [ ] All endpoints use `require_access(module, action)`
- [ ] All database queries filter by `organization_id`
- [ ] Access denials return 404, not 403
- [ ] No manual permission checks remain
- [ ] No super admin special cases remain
- [ ] Imports are updated
- [ ] File syntax is valid (`python -m py_compile <file>`)

## Testing

For each migrated endpoint, test:

1. **Valid Access**: User with permission can access
2. **No Permission**: User without permission gets 404
3. **Wrong Org**: User from different org gets 404
4. **Super Admin**: Super admin bypasses checks (if appropriate)

Example test:
```python
async def test_get_item_requires_permission(client, db):
    # User without permission
    response = await client.get("/items/1")
    assert response.status_code == 404  # Not 403!

async def test_get_item_wrong_org(client, db):
    # User from different organization
    response = await client.get("/items/1")
    assert response.status_code == 404
```

## Automation

Use the migration script for batch processing:

```bash
# Migrate single file
python scripts/migrate_to_rbac_enforcement.py --file app/api/vendors.py --module vendor

# Dry run (preview changes)
python scripts/migrate_to_rbac_enforcement.py --file app/api/vendors.py --module vendor --dry-run

# Migrate all known files
python scripts/migrate_to_rbac_enforcement.py --all

# List all files
python scripts/migrate_to_rbac_enforcement.py --list
```

## Progress Tracking

Update the checklist in this document and `RBAC_ENFORCEMENT_REPORT.md` after each file is migrated.

Current Status:
- **Total Files**: 130 API files
- **Migrated**: 52 files (40%)
- **Remaining**: 78 files (60%)

## Security Benefits

After complete migration:
- ✅ **Centralized Security**: One enforcement point for all APIs
- ✅ **Consistent Behavior**: Same permission model everywhere
- ✅ **Anti-Enumeration**: 404 responses prevent information leakage
- ✅ **Audit Trail**: All access is logged centrally
- ✅ **Maintainability**: Easy to add new permissions
- ✅ **Testability**: Simplified security testing
