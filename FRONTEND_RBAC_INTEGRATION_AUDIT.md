# Frontend RBAC Integration Audit Report

## Executive Summary

This document provides a comprehensive audit of frontend services and their integration with RBAC-enforced backend endpoints. The audit was conducted as part of Phase 6 of the RBAC migration initiative.

**Date**: October 28, 2025  
**Scope**: All frontend service files in `frontend/src/services/`  
**Total Services Analyzed**: 43  
**Total API Calls Found**: 315  

## Audit Findings

### Frontend Service Coverage

| Category | Service Files | API Calls | Status |
|----------|--------------|-----------|--------|
| Integration Services | 3 | 45 | ⚠️ Needs Review |
| Entity Services | 1 | 12 | ⚠️ Needs Review |
| Analytics Services | 4 | 38 | ✅ Backend Migrated |
| Financial Services | 2 | 24 | ✅ Partial Backend Migration |
| Master Data Services | 1 | 15 | ⚠️ Needs Review |
| Voucher Services | 1 | 28 | ✅ Backend Fully Migrated |
| CRM Services | 1 | 22 | ✅ Backend Migrated |
| Notification Services | 2 | 18 | ✅ Backend Migrated |
| HR Services | 1 | 12 | ✅ Backend Migrated |
| Other Services | 27 | 101 | Mixed |

### Key Backend Endpoints Called by Frontend

#### ✅ RBAC-Enforced (Backend Migrated)
These backend endpoints have been migrated to use `require_access` enforcement:

- **Vouchers** (18 files migrated in Phase 4):
  - `/api/v1/vouchers/sales`, `/api/v1/vouchers/purchase`
  - `/api/v1/vouchers/payment`, `/api/v1/vouchers/receipt`
  - All voucher types (sales_order, purchase_order, journal, etc.)

- **Manufacturing** (10 files migrated in Phase 2):
  - `/api/v1/manufacturing/orders`, `/api/v1/manufacturing/bom`
  - `/api/v1/manufacturing/job-cards`, `/api/v1/manufacturing/production-plan`

- **CRM** (1 file migrated in Phase 3):
  - `/api/v1/crm/campaigns`, `/api/v1/crm/interactions`
  - `/api/v1/crm/segments`

- **HR** (1 file migrated in Phase 3):
  - `/api/v1/hr/employees`, `/api/v1/hr/leave-requests`

- **Finance/Analytics** (5 files migrated in Phase 2):
  - `/api/v1/finance/analytics`, `/api/v1/finance/balance-sheet`
  - `/api/v1/ml-analytics/dashboard`, `/api/v1/ai-analytics`

- **Service Desk** (1 file migrated in Phase 3):
  - Service-related endpoints

- **Notification** (1 file migrated in Phase 3):
  - `/api/v1/notifications/templates`, `/api/v1/notifications/send`

- **Order Book** (1 file migrated in Phase 3):
  - Order management endpoints

- **Inventory** (1 file migrated in Phase 5):
  - `/api/v1/inventory/analytics` (partial)

#### ⚠️ NOT YET RBAC-Enforced (Backend NOT Migrated)
These backend endpoints are called by frontend but have NOT been migrated to RBAC enforcement:

- **Integration Endpoints** (NOT migrated):
  - `/api/v1/integrations/*`
  - `/api/v1/integration-settings/*` (Phase 5 incomplete)
  - `/api/v1/external-integrations/*` (Phase 5 partial)

- **Master Data Endpoints** (NOT migrated):
  - `/api/v1/customers` (critical)
  - `/api/v1/vendors` (critical)
  - `/api/v1/master-data/tax-codes`

- **Reports Endpoints** (NOT migrated):
  - `/reports/complete-ledger`
  - `/reports/outstanding-ledger`
  - `/reports/inventory-report`
  - `/api/v1/reports/*`

- **Admin Endpoints** (NOT migrated):
  - `/api/v1/admin/*`
  - `/api/v1/rbac/*` (RBAC management itself not enforced)

- **Stock/Warehouse** (Phase 5 incomplete):
  - `/api/v1/stock`
  - `/api/v1/warehouse/*`
  - `/api/v1/dispatch/*`
  - `/api/v1/procurement/*`

- **ERP Core** (NOT migrated):
  - `/api/v1/erp/*` (24 endpoints)

- **Auth/User Management** (NOT migrated):
  - `/api/v1/auth/*` (4 endpoints)
  - `/api/v1/user/*` (7 endpoints)

#### 📊 Other Modules
- **Assets**: `/api/v1/assets/*` (NOT migrated)
- **Transport**: `/api/v1/transport/*` (NOT migrated)
- **Project Management**: `/api/v1/project-management/*` (NOT migrated)
- **Marketing**: `/api/v1/marketing/*` (NOT migrated)
- **Workflow**: `/api/v1/workflow/*` (NOT migrated)

## Frontend Error Handling Analysis

### Current State
Most frontend services use the centralized API client (`frontend/src/lib/api.ts` or `frontend/src/utils/api.ts`) which includes:

✅ **Existing Features**:
- Automatic JWT token inclusion
- Token refresh on 401 responses
- Basic error handling
- CORS support
- Request/response logging

⚠️ **Missing Features for RBAC**:
- No specific handling for 403 (Permission Denied) errors
- No user-friendly permission denial messages
- No retry logic for transient permission errors
- Limited contextual error messages for different modules

### Recommendations

1. **Enhance Error Handler for RBAC**:
```typescript
// frontend/src/lib/api.ts or utils/api.ts
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 403) {
      const requiredPermission = error.response.data?.required_permission;
      const module = error.response.data?.module;
      
      // Show user-friendly message
      toast.error(
        `Access Denied: You don't have permission to ${module}. ` +
        `Required permission: ${requiredPermission}. ` +
        `Please contact your administrator.`
      );
      
      // Log for audit
      console.warn('[RBAC] Permission denied:', {
        endpoint: error.config.url,
        method: error.config.method,
        requiredPermission,
        module
      });
      
      // Optionally redirect to access denied page
      // router.push('/access-denied');
    }
    
    return Promise.reject(error);
  }
);
```

2. **Add Permission Check Before API Calls**:
```typescript
// frontend/src/services/vouchersService.ts
export const createVoucher = async (data: VoucherCreate) => {
  // Check permission before making API call
  const hasPermission = await checkPermission('voucher', 'create');
  if (!hasPermission) {
    throw new Error('Insufficient permissions to create vouchers');
  }
  
  const response = await api.post('/api/v1/vouchers/sales', data);
  return response.data;
};
```

3. **Implement Permission Context**:
```typescript
// frontend/src/context/PermissionContext.tsx
interface PermissionContextType {
  permissions: string[];
  hasPermission: (module: string, action: string) => boolean;
  refreshPermissions: () => Promise<void>;
}

export const PermissionProvider: React.FC = ({ children }) => {
  const [permissions, setPermissions] = useState<string[]>([]);
  
  const hasPermission = (module: string, action: string) => {
    const required = `${module}_${action}`;
    return permissions.includes(required);
  };
  
  // Load permissions on mount and user change
  useEffect(() => {
    refreshPermissions();
  }, []);
  
  return (
    <PermissionContext.Provider value={{ permissions, hasPermission, refreshPermissions }}>
      {children}
    </PermissionContext.Provider>
  );
};
```

## Organization Context in Frontend

### Current Implementation
Frontend services currently rely on:
- JWT token containing organization_id claim
- Organization context in Redux/React Context
- Manual organization_id extraction in some services

### Verification Needed

1. **Check if organization_id is consistently used**:
   - Review all API calls to ensure org context is properly included
   - Verify multi-tenant isolation in frontend state management

2. **Audit localStorage/sessionStorage**:
   - Ensure no cross-organization data leakage
   - Clear org-specific data on organization switch

3. **Review React Context/Redux Store**:
   - Verify organization isolation in global state
   - Ensure state reset on organization change

## Integration Scripts Audit

### Python Integration Scripts
Located in project root and scripts/:

| Script | Purpose | RBAC Status | Action Needed |
|--------|---------|-------------|---------------|
| `test_backend_integration.py` | Backend integration tests | ⚠️ | Update to test RBAC endpoints |
| `test_frontend_ui.py` | Frontend UI tests | ⚠️ | Add permission denial tests |
| `tests/test_dispatch_api_integration.py` | Dispatch API tests | ⚠️ | Verify RBAC enforcement |
| `app/services/integration_service.py` | Integration service layer | ⚠️ | Needs RBAC update |
| `app/services/external_integrations_service.py` | External integrations | ⚠️ | Needs RBAC update |

### Integration Module Status (Phase 5 Incomplete)

**Files Partially Migrated**:
1. `app/api/v1/integration.py` - 67% migrated (6/9 endpoints)
2. `app/api/v1/integration_settings.py` - 0% migrated (0/15 endpoints) ⚠️
3. `app/api/v1/external_integrations.py` - 70% migrated (7/10 endpoints)

**Frontend Impact**:
- `frontend/src/services/integrationService.ts` - Calls integration endpoints
- `frontend/src/services/integration/apiIntegrationService.ts` - Extensive integration usage

## Action Items

### High Priority (Critical for Business Operations)

1. **Complete Phase 5 Integration Module Migration** (5 files):
   - [ ] Complete `app/api/v1/integration_settings.py` (15 endpoints)
   - [ ] Complete `app/api/v1/stock.py` (12 endpoints)
   - [ ] Complete `app/api/v1/warehouse.py` (11 endpoints)
   - [ ] Complete `app/api/v1/dispatch.py` (21 endpoints)
   - [ ] Complete `app/api/v1/procurement.py` (10 endpoints)

2. **Migrate Critical Master Data Endpoints** (3 files):
   - [ ] Migrate `app/api/v1/customers.py` (if exists) or create RBAC enforcement
   - [ ] Migrate `app/api/v1/vendors.py` (if exists) or create RBAC enforcement
   - [ ] Verify entity endpoints in ERP module

3. **Migrate Admin & RBAC Endpoints** (2 files):
   - [ ] Migrate `app/api/v1/admin.py` (12 endpoints)
   - [ ] Migrate `app/api/v1/rbac.py` (17 endpoints) - Ironically, RBAC management not RBAC-enforced!

### Medium Priority

4. **Update Frontend Error Handling**:
   - [ ] Add 403 permission denial handling in API interceptor
   - [ ] Create PermissionContext for frontend
   - [ ] Add permission checks before API calls in critical services

5. **Migrate Reports Module**:
   - [ ] Migrate `app/api/v1/reports.py` (12 endpoints)
   - [ ] Ensure frontend reports service handles permission denials

6. **Update Integration Tests**:
   - [ ] Add RBAC permission tests to integration test suite
   - [ ] Test 403 error responses
   - [ ] Test cross-org access prevention

### Low Priority

7. **Documentation**:
   - [ ] Document frontend-backend API contract
   - [ ] Create permission matrix (feature → required permission)
   - [ ] Update developer onboarding guide

8. **Migrate Remaining Modules**:
   - [ ] Assets, Transport, Marketing, Project Management (as needed)

## Testing Requirements

### Frontend Tests Needed

1. **Permission Denial Tests**:
```typescript
describe('Permission Handling', () => {
  it('should show error when user lacks voucher_create permission', async () => {
    // Mock 403 response
    mockApi.onPost('/api/v1/vouchers/sales').reply(403, {
      detail: 'Insufficient permissions. Required: voucher_create'
    });
    
    await expect(createVoucher(data)).rejects.toThrow('Insufficient permissions');
    expect(toast.error).toHaveBeenCalledWith(expect.stringContaining('voucher_create'));
  });
});
```

2. **Organization Isolation Tests**:
```typescript
describe('Organization Isolation', () => {
  it('should not leak data between organizations', async () => {
    // Create voucher in org 1
    const voucher1 = await createVoucherInOrg(1, data);
    
    // Switch to org 2
    await switchOrganization(2);
    
    // Should not be able to access org 1 voucher
    await expect(getVoucher(voucher1.id)).rejects.toThrow('Not found');
  });
});
```

### Integration Tests Needed

1. **End-to-End RBAC Flow**:
   - User login → Permission loading → Feature access → API call → Success/Denial
   
2. **Cross-Module Permission Tests**:
   - Test that voucher permissions don't grant inventory access, etc.

## Security Considerations

### Current Risk Assessment

| Risk | Severity | Mitigation Status |
|------|----------|-------------------|
| Unauthorized access to unmigrated endpoints | 🔴 HIGH | In Progress (58% not migrated) |
| Cross-organization data leakage | 🟡 MEDIUM | Needs verification |
| Insufficient permission checks in frontend | 🟡 MEDIUM | Needs enhancement |
| Missing audit trail for denied actions | 🟡 MEDIUM | Needs implementation |

### Recommendations

1. **Immediate**:
   - Complete Phase 5 integration module migrations
   - Add 403 error handling in frontend
   - Implement permission checks for critical operations

2. **Short-term**:
   - Migrate all master data endpoints
   - Add comprehensive permission denial logging
   - Create permission management UI

3. **Long-term**:
   - Automated enforcement checking in CI/CD
   - Real-time permission monitoring dashboard
   - Regular security audits

## Conclusion

The frontend services are generally well-structured and use a centralized API client, which makes RBAC integration straightforward. However, **58% of backend endpoints** (67 out of 114 files) are still not RBAC-enforced, including critical master data and integration endpoints that are heavily used by frontend services.

**Priority Actions**:
1. Complete the 5 partially-migrated Phase 5 files
2. Migrate 7 critical backend files (admin, RBAC, reports, master data)
3. Add frontend 403 error handling
4. Create comprehensive integration tests

**Estimated Impact**:
- **Security**: 🔴 HIGH - Completing these migrations closes major security gaps
- **Effort**: 🟡 MEDIUM - ~20 backend files + frontend enhancements
- **User Experience**: 🟢 LOW - Mostly transparent, better error messages

## Appendix: Backend Migration Status by Module

### Completed (47 files, 41.2%):
- Vouchers: 18/18 (100%) ✅
- Manufacturing: 10/10 (100%) ✅  
- Finance/Analytics: 5/5 (100%) ✅
- CRM: 1/1 (100%) ✅
- HR: 1/1 (100%) ✅
- Service Desk: 1/1 (100%) ✅
- Order Book: 1/1 (100%) ✅
- Notifications: 1/1 (100%) ✅
- Inventory: 1/5 (20%) (inventory.py only)
- Payroll: 4/5 (80%) (missing payroll_migration.py)
- Master Data: 1/1 (76% of endpoints)
- Integrations: 2/3 (67% of endpoints)

### Not Started (67 files, 58.8%):
- Reports: 0/1
- Admin: 0/1
- RBAC Management: 0/1
- Customers/Vendors: 0/2 (if separate files)
- ERP Core: 0/1
- Stock/Warehouse/Dispatch: 0/4
- Organizations: 0/5 (subdirectory)
- Auth: 0/1
- Assets: 0/1
- 50+ other utility modules

---

**Report Generated**: October 28, 2025  
**Next Review**: After Phase 6 completion  
**Contact**: Development Team
