# RBAC Enforcement - Quick Reference Card

## 🎯 One-Minute Guide

### Step 1: Import
```python
from app.core.enforcement import require_access
```

### Step 2: Apply to Endpoint
```python
@router.get("/items")
async def get_items(
    auth: tuple = Depends(require_access("module", "action")),  # ← Add this
    db: AsyncSession = Depends(get_db)
):
    user, org_id = auth  # ← Extract these
    stmt = select(Item).where(Item.organization_id == org_id)  # ← Use org_id
    ...
```

## 📝 Common Patterns

### List/Get (Read)
```python
auth: tuple = Depends(require_access("voucher", "read"))  # or "inventory", etc.
```

### Create
```python
auth: tuple = Depends(require_access("voucher", "create"))
user, org_id = auth
item = Item(**data, organization_id=org_id, created_by_id=user.id)
```

### Update
```python
auth: tuple = Depends(require_access("voucher", "update"))
user, org_id = auth
stmt = select(Item).where(Item.id == id, Item.organization_id == org_id)
```

### Delete
```python
auth: tuple = Depends(require_access("voucher", "delete"))
user, org_id = auth
stmt = select(Item).where(Item.id == id, Item.organization_id == org_id)
```

## 🔑 Permission Format

```
{module}_{action}
```

Examples:
- `inventory_read`
- `voucher_create`, `voucher_update`, `voucher_delete`
- `manufacturing_read`, `manufacturing_create`
- `finance_read`, `analytics_read`

## 📋 Module-Specific Examples

### Vouchers
```python
auth: tuple = Depends(require_access("voucher", "create"))
user, org_id = auth
```

### Manufacturing
```python
auth: tuple = Depends(require_access("manufacturing", "read"))
user, org_id = auth
stmt = select(BillOfMaterials).where(BillOfMaterials.organization_id == org_id)
```

### Finance/Analytics
```python
auth: tuple = Depends(require_access("finance", "read"))
user, organization_id = auth  # Note: can use organization_id or org_id
```

### CRM ✅
```python
auth: tuple = Depends(require_access("crm", "read"))
user, org_id = auth
stmt = select(Lead).where(Lead.organization_id == org_id)
```

### Service Desk ✅
```python
auth: tuple = Depends(require_access("service", "create"))
user, org_id = auth
query = db.query(Ticket).filter(Ticket.organization_id == org_id)
```

### Notification ✅
```python
auth: tuple = Depends(require_access("notification", "read"))
user, org_id = auth
```

### HR ✅
```python
auth: tuple = Depends(require_access("hr", "update"))
user, org_id = auth
stmt = select(EmployeeProfile).where(EmployeeProfile.organization_id == org_id)
```

### Order Book ✅
```python
auth: tuple = Depends(require_access("order", "read"))
user, organization_id = auth  # Note: Order Book uses organization_id
query = db.query(Order).filter(Order.organization_id == organization_id)
```

## ⚡ Quick Checklist

Before committing:
- [ ] Added `from app.core.enforcement import require_access`
- [ ] All endpoints use `auth: tuple = Depends(require_access(...))`
- [ ] All queries filter by `organization_id`
- [ ] Extracted `user, org_id = auth` at start of function
- [ ] Used `org_id` not `current_user.organization_id`

## 🛠️ Analysis Tool

```bash
# Analyze any route file
python scripts/analyze_route_for_enforcement.py app/api/v1/module/routes.py
```

Outputs:
- Current status
- Recommendations
- Migration template
- Permission suggestions
- Testing checklist

## 📚 Full Docs

- **Implementation Guide**: `/RBAC_TENANT_ENFORCEMENT_GUIDE.md`
- **Full Report**: `/RBAC_ENFORCEMENT_REPORT.md`
- **Examples**:
  - **Vouchers**: `/app/api/v1/vouchers/` (18 files - all migrated ✅)
    - sales_voucher.py, purchase_voucher.py, journal_voucher.py
    - payment_voucher.py, receipt_voucher.py, contra_voucher.py
    - credit_note.py, debit_note.py, delivery_challan.py
    - goods_receipt_note.py, proforma_invoice.py, quotation.py
    - purchase_order.py, sales_order.py, sales_return.py, purchase_return.py
    - inter_department_voucher.py, non_sales_credit_note.py
  - Manufacturing: `/app/api/v1/manufacturing/bom.py` (10 files ✅)
  - Finance: `/app/api/v1/finance_analytics.py` ✅
  - **CRM**: `/app/api/v1/crm.py` ✅
  - **Service Desk**: `/app/api/v1/service_desk.py` ✅
  - **Notification**: `/app/api/notifications.py` ✅
  - **HR**: `/app/api/v1/hr.py` ✅
  - **Order Book**: `/app/api/v1/order_book.py` ✅
- **Tests**: 
  - `/tests/test_rbac_migration_enforcement.py`
  - `/tests/test_phase3_rbac_enforcement.py`
  - `/tests/test_voucher_rbac_migration.py` ✅ **NEW - Phase 4**

## 📊 Migration Progress

**Baseline**: 130 total API route files requiring RBAC enforcement (excluding __init__.py, schemas, and helper modules)

**Phase 4 Complete (Late October 2025)**:
- Total files migrated: **34/130 (26.2%)**
- Voucher modules: **18/18 (100%)** ✅
- Manufacturing modules: **10/10 (100%)** ✅
- Finance modules: **5/8 (62.5%)** ✅
- CRM: **1/1 (100%)** ✅
- HR: **1/1 (100%)** ✅
- Service Desk: **1/1 (100%)** ✅
- Order Book: **1/1 (100%)** ✅
- Notifications: **1/1 (100%)** ✅

## 🧪 Testing

```python
# Cross-org access should return 404
response = await client.get("/items/123", headers={"X-Org-ID": "999"})
assert response.status_code == 404

# Without permission should return 403
response = await client.post("/items", headers={"Authorization": "no-perm-token"})
assert response.status_code == 403
```

## ⚠️ Common Mistakes

❌ **DON'T**:
```python
# Old pattern - inconsistent, not secure
current_user: User = Depends(get_current_active_user)
stmt = select(Item).where(Item.organization_id == current_user.organization_id)
```

✅ **DO**:
```python
# New pattern - consistent, secure
auth: tuple = Depends(require_access("inventory", "read"))
user, org_id = auth
stmt = select(Item).where(Item.organization_id == org_id)
```

## 🆘 Need Help?

1. Check the implementation guide
2. Look at sales_voucher.py example
3. Run the analysis tool
4. Review test examples
