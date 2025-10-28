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

**Baseline**: 114 total API route files with endpoints requiring RBAC enforcement (updated October 2025)

**Phase 6 Status (October 28, 2025)**:
- **Total files migrated**: **47/114 (41.2%)** ✅
- **Total files not migrated**: **67/114 (58.8%)** ⚠️

**By Module**:
- Voucher modules: **18/18 (100%)** ✅ Phase 4
- Manufacturing modules: **10/10 (100%)** ✅ Phase 2
- Finance modules: **5/8 (62.5%)** ✅ Phase 2
- CRM: **1/1 (100%)** ✅ Phase 3
- HR: **1/1 (100%)** ✅ Phase 3
- Service Desk: **1/1 (100%)** ✅ Phase 3
- Order Book: **1/1 (100%)** ✅ Phase 3
- Notifications: **1/1 (100%)** ✅ Phase 3
- Inventory: **1/5 (20%)** ⚠️ Phase 5 partial
- Payroll: **4/5 (80%)** ⚠️ Phase 5 partial
- Master Data: **1/1 (76% endpoints)** ⚠️ Phase 5 partial
- Integrations: **2/3 (67% endpoints)** ⚠️ Phase 5 partial

**Frontend Analysis (Phase 6)** ✅:
- Frontend service files: 43
- API calls identified: 315
- Calls to RBAC-enforced backends: ~42%
- Calls to non-RBAC backends: ~58%
- Full audit: `FRONTEND_RBAC_INTEGRATION_AUDIT.md`

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

## 🌐 Frontend Integration (Phase 6)

### Error Handling for 403 Responses

```typescript
// frontend/src/lib/api.ts or utils/api.ts
import axios from 'axios';
import { toast } from 'react-toastify';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
});

// Add response interceptor for RBAC errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 403) {
      const permission = error.response.data?.required_permission;
      const module = error.response.data?.module;
      
      toast.error(
        `Access Denied: You need '${permission}' permission for ${module}. ` +
        `Contact your administrator.`
      );
      
      console.warn('[RBAC] Permission denied:', {
        url: error.config.url,
        method: error.config.method,
        required: permission,
      });
    }
    
    return Promise.reject(error);
  }
);

export default api;
```

### Permission Context (Optional)

```typescript
// frontend/src/context/PermissionContext.tsx
import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../lib/api';

interface PermissionContextType {
  permissions: string[];
  hasPermission: (module: string, action: string) => boolean;
  loading: boolean;
}

const PermissionContext = createContext<PermissionContextType>({
  permissions: [],
  hasPermission: () => false,
  loading: true,
});

export const PermissionProvider: React.FC = ({ children }) => {
  const [permissions, setPermissions] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    loadPermissions();
  }, []);
  
  const loadPermissions = async () => {
    try {
      const response = await api.get('/api/v1/rbac/permissions/me');
      setPermissions(response.data.permissions || []);
    } catch (error) {
      console.error('Failed to load permissions:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const hasPermission = (module: string, action: string) => {
    const required = `${module}_${action}`;
    return permissions.includes(required);
  };
  
  return (
    <PermissionContext.Provider value={{ permissions, hasPermission, loading }}>
      {children}
    </PermissionContext.Provider>
  );
};

export const usePermissions = () => useContext(PermissionContext);

// Usage in component:
// const { hasPermission } = usePermissions();
// if (!hasPermission('voucher', 'create')) return <AccessDenied />;
```

### Frontend Service Example

```typescript
// frontend/src/services/vouchersService.ts
import api from '../lib/api';

export const createVoucher = async (data: VoucherCreate) => {
  // Optional: Check permission before API call
  // const { hasPermission } = usePermissions();
  // if (!hasPermission('voucher', 'create')) {
  //   throw new Error('Insufficient permissions');
  // }
  
  try {
    const response = await api.post('/api/v1/vouchers/sales', data);
    return response.data;
  } catch (error) {
    // Error handler will show toast for 403
    throw error;
  }
};
```

### Frontend Services Status

**✅ Calling RBAC-Enforced Backends**:
- vouchersService.ts (all voucher types)
- analyticsService.ts (ML/AI analytics)
- crmService.ts (CRM operations)
- hrService.ts (HR management)
- notificationService.ts (notifications)

**⚠️ Calling Non-RBAC Backends** (Need Backend Migration First):
- integrationService.ts → backend NOT migrated
- entityService.ts (customers/vendors) → backend NOT migrated
- reportsService.ts → backend NOT migrated
- stockService.ts → backend partially migrated
- masterService.ts → backend NOT migrated

**📄 Full Audit**: See `FRONTEND_RBAC_INTEGRATION_AUDIT.md`

## 🆘 Need Help?

### Backend RBAC
1. Check the implementation guide: `RBAC_TENANT_ENFORCEMENT_GUIDE.md`
2. Look at sales_voucher.py example
3. Run the analysis tool
4. Review test examples

### Frontend RBAC
1. Review `FRONTEND_RBAC_INTEGRATION_AUDIT.md`
2. Check error handling patterns above
3. See PermissionContext example
4. Test with 403 responses

### Full Documentation
- **Backend Guide**: `RBAC_TENANT_ENFORCEMENT_GUIDE.md`
- **Frontend Audit**: `FRONTEND_RBAC_INTEGRATION_AUDIT.md`
- **Phase Reports**: `RBAC_ENFORCEMENT_REPORT.md`
- **Quick Reference**: This file
