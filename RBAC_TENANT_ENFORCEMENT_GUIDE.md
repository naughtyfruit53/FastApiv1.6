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

#### CRM Module
- `crm_lead_create`
- `crm_lead_read`
- `crm_lead_update`
- `crm_lead_delete`
- `crm_opportunity_create`
- `crm_opportunity_read`
- `crm_opportunity_update`
- `crm_opportunity_delete`

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
- **Files with RBAC checks**: 28
- **Files needing both**: 98

### High Priority Modules
1. Vouchers (all types) - 16 files
2. Manufacturing - 10 files
3. Finance - 8 files
4. CRM - 1 file
5. HR - 1 file

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
