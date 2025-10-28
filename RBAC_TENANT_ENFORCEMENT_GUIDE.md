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

### Phase 2 Update (December 2025)
- **Files now with complete enforcement**: 21
- **Manufacturing module**: 100% complete (10/10 files) ✅
- **Finance/Analytics module**: 100% complete (5/5 files) ✅
- **Voucher module**: 17% complete (3/18 files)

### Phase 3 Update (October 2025)
- **Files now with complete enforcement**: 26 total
- **CRM module**: 100% complete (1/1 file, 19 endpoints) ✅
- **Service Desk module**: 100% complete (1/1 file, 15+ endpoints) ✅
- **Notification module**: 100% complete (1/1 file, 10+ endpoints) ✅
- **HR module**: 100% complete (1/1 file, 12+ endpoints) ✅
- **Order Book module**: 100% complete (1/1 file, 8+ endpoints) ✅

### Phase 4 Update (October 2025)
- **Files now with complete enforcement**: 34 total (26.2% of codebase)
- **Voucher module**: **100% complete (18/18 files)** ✅ **FULLY MIGRATED**
  - All voucher types: sales, purchase, journal, contra, credit/debit notes, etc.
  - 100+ endpoints migrated across all voucher families
  - Comprehensive test coverage with 13 automated test cases
  - 100% syntax validation and compilation success

### High Priority Modules Status
1. Vouchers (all types) - 18 files ✅ **100% COMPLETED - Phase 4**
2. Manufacturing - 10 files ✅ **COMPLETED**
3. Finance - 8 files (5 completed) ✅ **MOSTLY COMPLETED**
4. CRM - 1 file ✅ **COMPLETED**
5. HR - 1 file ✅ **COMPLETED**
6. Service Desk - 1 file ✅ **COMPLETED**
7. Notification - 1 file ✅ **COMPLETED**
8. Order Book - 1 file ✅ **COMPLETED**

**Remaining Priority Modules**:
9. Inventory/Stock Management - 3 files (inventory.py, stock.py, warehouse.py)
10. Payroll Components - 6 files (payroll modules)
11. Integration/External Systems - Multiple files
12. Master Data - Various files (products.py, customers.py, vendors.py, companies.py)

## Module-Specific Examples

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
