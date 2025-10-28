# RBAC and Tenant Isolation Enforcement Guide

## Overview

This guide documents the comprehensive RBAC (Role-Based Access Control) and tenant isolation enforcement system implemented across all backend modules.

## Core Concepts

### Tenant Isolation
- **Organization Scoping**: Every database query must be scoped to the user's organization
- **Data Privacy**: Users can only access data belonging to their organization
- **Super Admin Override**: Platform super admins can access multiple organizations with explicit context

### RBAC (Role-Based Access Control)
- **Permission-Based**: Access is controlled by fine-grained permissions
- **Module-Action Pattern**: Permissions follow `{module}_{action}` format (e.g., `inventory_read`, `voucher_create`)
- **Role Assignment**: Users are assigned roles which grant sets of permissions

## Centralized Enforcement Utilities

### Location
All enforcement utilities are centralized in `/app/core/enforcement.py`

### Key Components

#### 1. TenantEnforcement
Handles organization scoping and isolation.

**Methods:**
- `get_organization_id(current_user)`: Get and validate organization ID
- `enforce_organization_access(obj, organization_id, resource_name)`: Verify object belongs to organization
- `filter_by_organization(stmt, model_class, organization_id)`: Add organization filter to queries

#### 2. RBACEnforcement
Handles permission checking.

**Methods:**
- `check_permission(user, module, action, db)`: Check if user has permission
- `require_module_permission(module, action)`: Create permission dependency

#### 3. CombinedEnforcement
Combines both tenant and RBAC enforcement.

**Usage:**
```python
from app.core.enforcement import require_access

@router.get("/items")
async def get_items(
    auth: tuple = Depends(require_access("inventory", "read")),
    db: Session = Depends(get_db)
):
    user, org_id = auth
    # Query is automatically scoped to org_id
    ...
```

## Implementation Patterns

### Pattern 1: Simple Query with Enforcement
```python
from app.core.enforcement import require_access, get_organization_scoped_query

@router.get("/items")
async def get_items(
    auth: tuple = Depends(require_access("inventory", "read")),
    db: AsyncSession = Depends(get_db)
):
    user, org_id = auth
    
    # Create organization-scoped query
    stmt = await get_organization_scoped_query(Item, org_id, db)
    result = await db.execute(stmt)
    items = result.scalars().all()
    
    return items
```

### Pattern 2: Create with Enforcement
```python
from app.core.enforcement import require_access

@router.post("/items")
async def create_item(
    item_data: ItemCreate,
    auth: tuple = Depends(require_access("inventory", "create")),
    db: AsyncSession = Depends(get_db)
):
    user, org_id = auth
    
    # Create item with organization_id
    item = Item(
        **item_data.dict(),
        organization_id=org_id,
        created_by_id=user.id
    )
    
    db.add(item)
    await db.commit()
    
    return item
```

### Pattern 3: Update with Enforcement
```python
from app.core.enforcement import require_access, TenantEnforcement

@router.put("/items/{item_id}")
async def update_item(
    item_id: int,
    item_data: ItemUpdate,
    auth: tuple = Depends(require_access("inventory", "update")),
    db: AsyncSession = Depends(get_db)
):
    user, org_id = auth
    
    # Get item
    stmt = select(Item).where(Item.id == item_id)
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Enforce organization access
    TenantEnforcement.enforce_organization_access(item, org_id, "Item")
    
    # Update item
    for key, value in item_data.dict(exclude_unset=True).items():
        setattr(item, key, value)
    
    await db.commit()
    return item
```

### Pattern 4: Delete with Enforcement
```python
from app.core.enforcement import require_access, TenantEnforcement

@router.delete("/items/{item_id}")
async def delete_item(
    item_id: int,
    auth: tuple = Depends(require_access("inventory", "delete")),
    db: AsyncSession = Depends(get_db)
):
    user, org_id = auth
    
    # Get item
    stmt = select(Item).where(Item.id == item_id)
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Enforce organization access
    TenantEnforcement.enforce_organization_access(item, org_id, "Item")
    
    # Delete item
    await db.delete(item)
    await db.commit()
    
    return {"message": "Item deleted successfully"}
```

## Module Permissions

### Standard CRUD Permissions
Each module should implement these standard permissions:
- `{module}_create`: Create new records
- `{module}_read`: Read/view records
- `{module}_update`: Update existing records
- `{module}_delete`: Delete records

### Module-Specific Permissions
Modules may define additional permissions for specific actions:
- `voucher_approve`: Approve vouchers
- `inventory_adjust`: Adjust stock levels
- `order_cancel`: Cancel orders

### Current Module Permissions

#### Inventory Module
- `inventory_create`
- `inventory_read`
- `inventory_update`
- `inventory_delete`

#### Voucher Modules
- `voucher_create`
- `voucher_read`
- `voucher_update`
- `voucher_delete`
- `voucher_approve`

#### Manufacturing Module ✅
- `manufacturing_create`
- `manufacturing_read`
- `manufacturing_update`
- `manufacturing_delete`

#### Finance/Analytics Modules ✅
- `finance_create`
- `finance_read`
- `analytics_create`
- `analytics_read`

#### CRM Module ✅
- `crm_read` - View leads, opportunities, activities, analytics
- `crm_create` - Create leads, opportunities, activities, commissions
- `crm_update` - Update leads, opportunities, convert leads
- `crm_delete` - Delete leads, opportunities, commissions

#### Service Desk Module ✅
- `service_read` - View tickets, SLAs, surveys, chatbot data
- `service_create` - Create tickets, SLA policies, surveys
- `service_update` - Update tickets, SLA tracking, channel configs
- `service_delete` - Delete tickets, policies, surveys

#### Notification Module ✅
- `notification_read` - View templates and notification logs
- `notification_create` - Create templates, send notifications
- `notification_update` - Update templates and preferences
- `notification_delete` - Delete templates

#### HR Module ✅
- `hr_read` - View employee profiles, attendance, leave, reviews
- `hr_create` - Create employee profiles, attendance records, leave applications
- `hr_update` - Update profiles, approve leave, performance reviews
- `hr_delete` - Delete profiles and records

#### Order Book Module ✅
- `order_read` - View orders and workflow status
- `order_create` - Create new orders
- `order_update` - Update orders and workflow stages
- `order_delete` - Delete orders

## Database Model Requirements

### Required Fields
All models that store tenant data MUST have:
```python
from sqlalchemy import Column, Integer, ForeignKey

class MyModel(Base):
    __tablename__ = "my_model"
    
    id = Column(Integer, primary_key=True)
    organization_id = Column(
        Integer, 
        ForeignKey("organizations.id"), 
        nullable=False, 
        index=True
    )
    # ... other fields
```

### Indexes
Organization ID should always be indexed for performance:
```python
__table_args__ = (
    Index('idx_mymodel_org', 'organization_id'),
)
```

## Testing

### Unit Tests
Test enforcement utilities in isolation:
```python
from app.core.enforcement import TenantEnforcement, RBACEnforcement

def test_tenant_enforcement():
    obj = Mock()
    obj.organization_id = 123
    
    # Should not raise
    TenantEnforcement.enforce_organization_access(obj, 123, "Test")
    
    # Should raise
    with pytest.raises(HTTPException):
        TenantEnforcement.enforce_organization_access(obj, 456, "Test")
```

### Integration Tests
Test complete endpoint flows:
```python
@pytest.mark.asyncio
async def test_create_item_wrong_org(client, user_token_org_1, user_token_org_2):
    # Create item in org 1
    response = await client.post(
        "/api/v1/items",
        headers={"Authorization": f"Bearer {user_token_org_1}"},
        json={"name": "Test Item"}
    )
    assert response.status_code == 201
    item_id = response.json()["id"]
    
    # Try to access from org 2 - should fail
    response = await client.get(
        f"/api/v1/items/{item_id}",
        headers={"Authorization": f"Bearer {user_token_org_2}"}
    )
    assert response.status_code == 404  # Not found (not 403 to avoid info leak)
```

## Migration Guide

### For Existing Routes

#### Before:
```python
@router.get("/items")
async def get_items(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Potentially insecure - no org scoping or permission check
    stmt = select(Item)
    result = await db.execute(stmt)
    return result.scalars().all()
```

#### After:
```python
from app.core.enforcement import require_access

@router.get("/items")
async def get_items(
    auth: tuple = Depends(require_access("inventory", "read")),
    db: AsyncSession = Depends(get_db)
):
    user, org_id = auth
    
    # Secure - scoped to organization
    stmt = select(Item).where(Item.organization_id == org_id)
    result = await db.execute(stmt)
    return result.scalars().all()
```

## Audit Results

### Summary
- **Total route files analyzed**: 126
- **Files with organization checks**: 111
- **Files with RBAC checks**: 28 (initial audit)
- **Files needing both**: 98

### Phase 2 Update (October 2024)
- **Files now with complete enforcement**: 21
- **Manufacturing module**: 100% complete (10/10 files) ✅
- **Finance/Analytics module**: 100% complete (5/5 files) ✅
- **Voucher module**: 17% complete (3/18 files)

### Phase 4 Update (Late October 2025)
- **Files now with complete enforcement**: 34 total (26.2% of codebase)
- **Voucher module**: **100% complete (18/18 files)** ✅ **FULLY MIGRATED**
  - All voucher types: sales, purchase, journal, contra, credit/debit notes, etc.
  - 100+ endpoints migrated across all voucher families
  - Comprehensive test coverage with 13 automated test cases
  - 100% syntax validation and compilation success

### Phase 5 Update (October 2025)
- **Inventory/Payroll/Master/Integration modules**: Partially migrated (45% of endpoints)
- **14 files updated**: inventory (1/5), payroll (4/5), master_data (1/1), integrations (2/3)
- **Status**: Unfinished - 89 endpoints remain in these 14 files

### Phase 6 Update (October 28, 2025) ✅ **AUDIT COMPLETE**
- **Backend Analysis**: 47/114 files migrated (41.2%), 67 files remaining (58.8%)
- **Frontend Audit**: 43 service files, 315 API calls analyzed
- **Documentation**: Created `FRONTEND_RBAC_INTEGRATION_AUDIT.md`
- **Status**: Planning complete, implementation pending

### High Priority Modules Status
1. Vouchers (all types) - 18 files ✅ **100% COMPLETED - Phase 4**
2. Manufacturing - 10 files ✅ **COMPLETED**
3. Finance - 8 files (5 completed) ✅ **MOSTLY COMPLETED**
4. CRM - 1 file ✅ **COMPLETED**
5. HR - 1 file ✅ **COMPLETED**
6. Service Desk - 1 file ✅ **COMPLETED**
7. Notification - 1 file ✅ **COMPLETED**
8. Order Book - 1 file ✅ **COMPLETED**

**Remaining Critical Modules** (High Business Impact):
9. **Master Data** (customers/vendors) - ⚠️ NOT MIGRATED
10. **Reports** - ⚠️ NOT MIGRATED
11. **Admin/RBAC Management** - ⚠️ NOT MIGRATED (ironic!)
12. **ERP Core** - ⚠️ NOT MIGRATED
13. Inventory/Stock Management - ⚠️ PARTIALLY MIGRATED (Phase 5 incomplete)
14. Integration modules - ⚠️ PARTIALLY MIGRATED (Phase 5 incomplete)

## Frontend Integration Patterns (Phase 6)

### Overview
Frontend services must handle RBAC-enforced backend endpoints properly. This includes:
1. Handling 403 (Permission Denied) responses
2. Showing user-friendly error messages
3. Optional: Checking permissions before making API calls
4. Maintaining organization context

### Error Handling for 403 Responses

**Required**: Add interceptor in your API client to handle permission denials.

```typescript
// frontend/src/lib/api.ts or frontend/src/utils/api.ts
import axios from 'axios';
import { toast } from 'react-toastify'; // or your notification library

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - Add JWT token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor - Handle RBAC errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Handle 403 Permission Denied
    if (error.response?.status === 403) {
      const data = error.response.data;
      const permission = data?.required_permission || 'unknown';
      const module = data?.module || 'this resource';
      
      // Show user-friendly error message
      toast.error(
        `Access Denied: You don't have permission to access ${module}. ` +
        `Required permission: ${permission}. ` +
        `Please contact your administrator to request access.`,
        { duration: 5000 }
      );
      
      // Log for debugging and audit
      console.warn('[RBAC] Permission denied:', {
        endpoint: error.config?.url,
        method: error.config?.method?.toUpperCase(),
        requiredPermission: permission,
        module,
        user: localStorage.getItem('user_email'),
      });
      
      // Optional: Track analytics
      // analytics.track('permission_denied', { permission, module });
      
      // Optional: Redirect to access denied page
      // if (window.location.pathname !== '/access-denied') {
      //   window.location.href = '/access-denied';
      // }
    }
    
    // Handle 401 Unauthorized (token expired/invalid)
    if (error.response?.status === 401) {
      // Existing token refresh logic
      // ...
    }
    
    return Promise.reject(error);
  }
);

export default api;
```

### Permission Context (Optional but Recommended)

Create a React context to manage user permissions globally:

```typescript
// frontend/src/context/PermissionContext.tsx
import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../lib/api';

interface PermissionContextType {
  permissions: string[];
  hasPermission: (module: string, action: string) => boolean;
  loading: boolean;
  refreshPermissions: () => Promise<void>;
}

const PermissionContext = createContext<PermissionContextType>({
  permissions: [],
  hasPermission: () => false,
  loading: true,
  refreshPermissions: async () => {},
});

export const PermissionProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [permissions, setPermissions] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  
  const loadPermissions = async () => {
    try {
      setLoading(true);
      // Adjust endpoint based on your backend
      const response = await api.get('/api/v1/rbac/permissions/me');
      setPermissions(response.data.permissions || []);
    } catch (error) {
      console.error('Failed to load user permissions:', error);
      setPermissions([]);
    } finally {
      setLoading(false);
    }
  };
  
  useEffect(() => {
    loadPermissions();
  }, []);
  
  const hasPermission = (module: string, action: string): boolean => {
    const requiredPermission = `${module}_${action}`;
    return permissions.includes(requiredPermission);
  };
  
  const refreshPermissions = async () => {
    await loadPermissions();
  };
  
  return (
    <PermissionContext.Provider value={{ permissions, hasPermission, loading, refreshPermissions }}>
      {children}
    </PermissionContext.Provider>
  );
};

export const usePermissions = () => useContext(PermissionContext);
```

**Usage in App**:
```typescript
// frontend/src/pages/_app.tsx or App.tsx
import { PermissionProvider } from '../context/PermissionContext';

function MyApp({ Component, pageProps }) {
  return (
    <AuthProvider>
      <PermissionProvider>
        <Component {...pageProps} />
      </PermissionProvider>
    </AuthProvider>
  );
}
```

**Usage in Components**:
```typescript
// frontend/src/components/VoucherForm.tsx
import { usePermissions } from '../context/PermissionContext';

export const VoucherForm = () => {
  const { hasPermission, loading } = usePermissions();
  
  if (loading) return <Spinner />;
  
  if (!hasPermission('voucher', 'create')) {
    return (
      <Alert severity="warning">
        You don't have permission to create vouchers. 
        Please contact your administrator.
      </Alert>
    );
  }
  
  return <form>...</form>;
};
```

### Frontend Service Pattern

Update your service files to handle RBAC properly:

```typescript
// frontend/src/services/vouchersService.ts
import api from '../lib/api';
import { VoucherCreate, VoucherUpdate, Voucher } from '../types/voucher.types';

/**
 * Create a new sales voucher
 * Requires: voucher_create permission
 */
export const createSalesVoucher = async (data: VoucherCreate): Promise<Voucher> => {
  try {
    const response = await api.post('/api/v1/vouchers/sales', data);
    return response.data;
  } catch (error) {
    // Error interceptor will handle 403 automatically
    // Just re-throw for component to handle
    throw error;
  }
};

/**
 * Get all sales vouchers for current organization
 * Requires: voucher_read permission
 */
export const getSalesVouchers = async (params?: {
  skip?: number;
  limit?: number;
  search?: string;
}): Promise<Voucher[]> => {
  try {
    const response = await api.get('/api/v1/vouchers/sales', { params });
    return response.data;
  } catch (error) {
    throw error;
  }
};

/**
 * Update a sales voucher
 * Requires: voucher_update permission
 */
export const updateSalesVoucher = async (
  id: number, 
  data: VoucherUpdate
): Promise<Voucher> => {
  try {
    const response = await api.put(`/api/v1/vouchers/sales/${id}`, data);
    return response.data;
  } catch (error) {
    throw error;
  }
};

/**
 * Delete a sales voucher
 * Requires: voucher_delete permission
 */
export const deleteSalesVoucher = async (id: number): Promise<void> => {
  try {
    await api.delete(`/api/v1/vouchers/sales/${id}`);
  } catch (error) {
    throw error;
  }
};

// With optional permission check before API call:
export const createSalesVoucherWithCheck = async (
  data: VoucherCreate,
  hasPermission: (module: string, action: string) => boolean
): Promise<Voucher> => {
  // Check permission before making API call
  if (!hasPermission('voucher', 'create')) {
    throw new Error('Insufficient permissions to create vouchers');
  }
  
  const response = await api.post('/api/v1/vouchers/sales', data);
  return response.data;
};
```

### Component Error Handling

Handle API errors in components:

```typescript
// frontend/src/components/VoucherList.tsx
import { useState, useEffect } from 'react';
import { getSalesVouchers } from '../services/vouchersService';
import { usePermissions } from '../context/PermissionContext';

export const VoucherList = () => {
  const [vouchers, setVouchers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { hasPermission } = usePermissions();
  
  useEffect(() => {
    loadVouchers();
  }, []);
  
  const loadVouchers = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getSalesVouchers();
      setVouchers(data);
    } catch (err: any) {
      // 403 errors are handled by interceptor (toast shown)
      // But you can also handle them here if needed
      if (err.response?.status === 403) {
        setError('You don\'t have permission to view vouchers');
      } else {
        setError('Failed to load vouchers');
      }
    } finally {
      setLoading(false);
    }
  };
  
  // Alternative: Check permission before rendering
  if (!hasPermission('voucher', 'read')) {
    return (
      <div className="access-denied">
        <h3>Access Denied</h3>
        <p>You don't have permission to view vouchers.</p>
        <p>Required permission: <code>voucher_read</code></p>
      </div>
    );
  }
  
  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;
  
  return (
    <div>
      {vouchers.map(voucher => (
        <VoucherCard key={voucher.id} voucher={voucher} />
      ))}
    </div>
  );
};
```

### Organization Context

Ensure organization context is maintained:

```typescript
// frontend/src/context/OrganizationContext.tsx
import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../lib/api';

interface OrganizationContextType {
  organizationId: number | null;
  organizationName: string | null;
  switchOrganization: (orgId: number) => Promise<void>;
}

const OrganizationContext = createContext<OrganizationContextType>({
  organizationId: null,
  organizationName: null,
  switchOrganization: async () => {},
});

export const OrganizationProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [organizationId, setOrganizationId] = useState<number | null>(null);
  const [organizationName, setOrganizationName] = useState<string | null>(null);
  
  useEffect(() => {
    loadOrganization();
  }, []);
  
  const loadOrganization = async () => {
    try {
      // Get organization from JWT token or API
      const response = await api.get('/api/v1/users/me');
      setOrganizationId(response.data.organization_id);
      setOrganizationName(response.data.organization_name);
    } catch (error) {
      console.error('Failed to load organization:', error);
    }
  };
  
  const switchOrganization = async (orgId: number) => {
    // Clear organization-specific data
    localStorage.removeItem('cached_vouchers');
    localStorage.removeItem('cached_inventory');
    // ... clear other org-specific cache
    
    setOrganizationId(orgId);
    
    // Reload data for new organization
    window.location.reload();
  };
  
  return (
    <OrganizationContext.Provider value={{ organizationId, organizationName, switchOrganization }}>
      {children}
    </OrganizationContext.Provider>
  );
};

export const useOrganization = () => useContext(OrganizationContext);
```

### Frontend Testing Patterns

Test RBAC error handling:

```typescript
// frontend/src/services/__tests__/vouchersService.test.ts
import { createSalesVoucher } from '../vouchersService';
import api from '../../lib/api';
import { toast } from 'react-toastify';

jest.mock('../../lib/api');
jest.mock('react-toastify');

describe('VouchersService RBAC', () => {
  it('should handle 403 permission denied', async () => {
    const error = {
      response: {
        status: 403,
        data: {
          detail: 'Insufficient permissions. Required: voucher_create',
          required_permission: 'voucher_create',
          module: 'voucher',
        },
      },
    };
    
    (api.post as jest.Mock).mockRejectedValue(error);
    
    await expect(createSalesVoucher({ amount: 100 })).rejects.toEqual(error);
    
    // Verify toast was shown (by interceptor)
    expect(toast.error).toHaveBeenCalledWith(
      expect.stringContaining('voucher_create')
    );
  });
  
  it('should successfully create voucher with permission', async () => {
    const mockVoucher = { id: 1, amount: 100, voucher_number: 'SV-001' };
    (api.post as jest.Mock).mockResolvedValue({ data: mockVoucher });
    
    const result = await createSalesVoucher({ amount: 100 });
    
    expect(result).toEqual(mockVoucher);
    expect(api.post).toHaveBeenCalledWith('/api/v1/vouchers/sales', { amount: 100 });
  });
});
```

### Frontend Services Status

**Services Calling RBAC-Enforced Backends** ✅:
- `vouchersService.ts` - All voucher types (Phase 4 complete)
- `analyticsService.ts` - ML/AI analytics (Phase 2 complete)
- `crmService.ts` - CRM operations (Phase 3 complete)
- `hrService.ts` - HR management (Phase 3 complete)
- `notificationService.ts` - Notifications (Phase 3 complete)
- Manufacturing-related services (Phase 2 complete)

**Services Calling Non-RBAC Backends** ⚠️ (Backend Migration Needed):
- `integrationService.ts` → `/api/v1/integrations/*` NOT migrated
- `entityService.ts` → `/api/v1/customers`, `/api/v1/vendors` NOT migrated
- `reportsService.ts` → `/reports/*` NOT migrated
- `stockService.ts` → `/api/v1/stock` partially migrated (Phase 5 incomplete)
- `masterService.ts` → `/api/v1/master-data/*` NOT migrated
- `adminService.ts` → `/api/v1/admin/*` NOT migrated

**Full Audit**: See `FRONTEND_RBAC_INTEGRATION_AUDIT.md` for comprehensive analysis.

## Best Practices

### Backend RBAC
1. **Always use enforcement dependencies**: Never manually check permissions
2. **Scope all queries**: Every database query must include organization filter
3. **Use helper functions**: Utilize `get_organization_scoped_query` for consistency
4. **Test thoroughly**: Add tests for both success and failure cases
5. **Log security events**: Log permission denials for audit trails
6. **Fail securely**: Return 404 instead of 403 to avoid information disclosure

### Frontend RBAC
1. **Handle 403 errors**: Add interceptor to show user-friendly permission denial messages
2. **Check permissions early**: Use PermissionContext to check before rendering UI
3. **Maintain org context**: Ensure organization_id is consistent across all requests
4. **Clear org data**: Clear cached data when switching organizations
5. **Test error cases**: Add tests for permission denial scenarios
6. **Document permissions**: Clearly document which permissions each feature requires

## Security Considerations

### Information Disclosure
- Return 404 "Not found" instead of 403 "Forbidden" when denying cross-org access
- This prevents attackers from discovering resource IDs in other organizations

### Super Admin Access
- Super admins can bypass checks but must explicitly specify organization context
- All super admin actions should be logged

### Audit Logging
- All permission denials are logged
- Organization context switches are logged
- Failed access attempts are monitored

## Support and Questions

For questions or issues with RBAC and tenant enforcement:

### Backend Questions
1. Review this guide (RBAC_TENANT_ENFORCEMENT_GUIDE.md)
2. Check existing test files in `/tests`
3. Consult the core enforcement module at `/app/core/enforcement.py`
4. Review example implementations in well-secured modules like `/app/api/v1/inventory.py`

### Frontend Questions
1. Review the frontend audit (FRONTEND_RBAC_INTEGRATION_AUDIT.md)
2. Check frontend patterns in this guide
3. Review example services in `frontend/src/services/`
4. Test with 403 responses using mock data

### Complete Documentation
- **Backend Guide**: This file (RBAC_TENANT_ENFORCEMENT_GUIDE.md)
- **Frontend Audit**: FRONTEND_RBAC_INTEGRATION_AUDIT.md
- **Phase Reports**: RBAC_ENFORCEMENT_REPORT.md
- **Quick Reference**: QUICK_REFERENCE.md


## Best Practices

### Manufacturing Module Example
```python
from app.core.enforcement import require_access

@router.get("/boms")
async def get_boms(
    skip: int = 0,
    limit: int = 100,
    auth: tuple = Depends(require_access("manufacturing", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get list of Bills of Materials"""
    current_user, org_id = auth
    
    stmt = select(BillOfMaterials).where(
        BillOfMaterials.organization_id == org_id
    ).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()
```

### Finance/Analytics Module Example
```python
from app.core.enforcement import require_access

@router.get("/analytics/dashboard")
async def get_finance_analytics_dashboard(
    period_days: int = Query(30),
    auth: tuple = Depends(require_access("finance", "read")),
    db: Session = Depends(get_db)
):
    """Get comprehensive finance analytics dashboard"""
    current_user, organization_id = auth
    
    # Use organization_id for all queries
    ratios = FinanceAnalyticsService.calculate_financial_ratios(db, organization_id)
    return {"ratios": ratios}
```

### CRM Module Example
```python
from app.core.enforcement import require_access

@router.get("/leads", response_model=List[LeadSchema])
async def get_leads(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = Query(None),
    auth: tuple = Depends(require_access("crm", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get all leads with filtering and pagination"""
    current_user, org_id = auth
    
    stmt = select(Lead).where(Lead.organization_id == org_id)
    if status:
        stmt = stmt.where(Lead.status == status)
    
    result = await db.execute(stmt.offset(skip).limit(limit))
    return result.scalars().all()
```

### Service Desk Module Example
```python
from app.core.enforcement import require_access

@router.get("/tickets", response_model=List[TicketSchema])
async def get_tickets(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = Query(None),
    auth: tuple = Depends(require_access("service", "read")),
    db: Session = Depends(get_db)
):
    """Get all tickets with advanced filtering"""
    current_user, org_id = auth
    
    query = db.query(Ticket).filter(Ticket.organization_id == org_id)
    if status:
        query = query.filter(Ticket.status == status)
    
    return query.offset(skip).limit(limit).all()
```

### HR Module Example
```python
from app.core.enforcement import require_access

@router.get("/employees", response_model=List[EmployeeProfileResponse])
async def get_employees(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    auth: tuple = Depends(require_access("hr", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get employee profiles"""
    current_user, org_id = auth
    
    stmt = select(EmployeeProfile).where(
        EmployeeProfile.organization_id == org_id
    ).offset(skip).limit(limit)
    
    result = await db.execute(stmt)
    return result.scalars().all()
```

## Best Practices

1. **Always use enforcement dependencies**: Never manually check permissions
2. **Scope all queries**: Every database query must include organization filter
3. **Use helper functions**: Utilize `get_organization_scoped_query` for consistency
4. **Test thoroughly**: Add tests for both success and failure cases
5. **Log security events**: Log permission denials for audit trails
6. **Fail securely**: Return 404 instead of 403 to avoid information disclosure

## Security Considerations

### Information Disclosure
- Return 404 "Not found" instead of 403 "Forbidden" when denying cross-org access
- This prevents attackers from discovering resource IDs in other organizations

### Super Admin Access
- Super admins can bypass checks but must explicitly specify organization context
- All super admin actions should be logged

### Audit Logging
- All permission denials are logged
- Organization context switches are logged
- Failed access attempts are monitored

## Support and Questions

For questions or issues with RBAC and tenant enforcement:
1. Review this guide
2. Check existing test files in `/tests`
3. Consult the core enforcement module at `/app/core/enforcement.py`
4. Review example implementations in well-secured modules like `/app/api/v1/inventory.py`
