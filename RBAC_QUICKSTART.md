# FastAPI v1.6 - RBAC Quickstart Guide

**Version**: 1.6  
**Last Updated**: October 29, 2025  
**Reading Time**: 10 minutes

---

## What You'll Learn

This quickstart guide will help you:
- ✅ Understand RBAC concepts in 5 minutes
- ✅ Implement RBAC in new endpoints
- ✅ Test permission enforcement
- ✅ Debug common issues

---

## Core Concepts (5-Minute Overview)

### 1. RBAC = Role-Based Access Control

**Three Pillars**:
1. **Authentication**: Who are you? (Login, JWT tokens)
2. **Authorization**: What can you do? (Permissions)
3. **Tenant Isolation**: What data can you see? (Organization scoping)

### 2. Organization = Tenant

Each **organization** is a separate tenant with:
- ✅ Its own users
- ✅ Its own data
- ✅ Its own permissions
- ✅ No access to other organizations' data

### 3. Permission = Action on Resource

Format: `{module}:{action}`

**Examples**:
- `product:read` - Can view products
- `invoice:create` - Can create invoices
- `user:delete` - Can delete users

### 4. Role = Set of Permissions

**Built-in Roles**:
- **Super Admin**: All permissions, can access all organizations
- **Admin**: All permissions within their organization
- **Manager**: Read/write access to assigned modules
- **User**: Read-only or limited write access

---

## Implementation in 3 Steps

### Step 1: Import Dependencies

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.enforcement import require_access
from app.models import YourModel
```

### Step 2: Add `require_access` to Endpoint

**Before (No RBAC)**:
```python
@router.get("/products")
async def list_products(
    db: AsyncSession = Depends(get_db)
):
    products = await db.execute(select(Product))
    return products.scalars().all()
```

**After (With RBAC)**:
```python
@router.get("/products")
async def list_products(
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_access("product", "read"))
):
    current_user, organization_id = auth
    
    # Auto-filtered by organization
    products = await db.execute(
        select(Product).where(Product.organization_id == organization_id)
    )
    return products.scalars().all()
```

### Step 3: Enforce Tenant Isolation

Always filter queries by `organization_id`:

```python
# ✅ CORRECT - Tenant isolated
products = await db.execute(
    select(Product).where(Product.organization_id == organization_id)
)

# ❌ WRONG - Can see all organizations' data
products = await db.execute(select(Product))
```

---

## Common Patterns

### Pattern 1: List Records (Read)

```python
@router.get("/items", response_model=List[ItemResponse])
async def list_items(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_access("item", "read"))
):
    current_user, organization_id = auth
    
    stmt = (
        select(Item)
        .where(Item.organization_id == organization_id)
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()
```

### Pattern 2: Get Single Record (Read)

```python
@router.get("/items/{item_id}", response_model=ItemResponse)
async def get_item(
    item_id: int,
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_access("item", "read"))
):
    current_user, organization_id = auth
    
    # Get item
    result = await db.execute(
        select(Item).where(Item.id == item_id)
    )
    item = result.scalar_one_or_none()
    
    # Check if exists
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Check organization (anti-enumeration)
    if item.organization_id != organization_id:
        raise HTTPException(status_code=404, detail="Item not found")
    
    return item
```

### Pattern 3: Create Record (Create)

```python
@router.post("/items", response_model=ItemResponse)
async def create_item(
    item_data: ItemCreate,
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_access("item", "create"))
):
    current_user, organization_id = auth
    
    # Create item with organization_id
    item = Item(
        **item_data.dict(),
        organization_id=organization_id,
        created_by=current_user.id
    )
    
    db.add(item)
    await db.commit()
    await db.refresh(item)
    
    return item
```

### Pattern 4: Update Record (Update)

```python
@router.put("/items/{item_id}", response_model=ItemResponse)
async def update_item(
    item_id: int,
    item_data: ItemUpdate,
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_access("item", "update"))
):
    current_user, organization_id = auth
    
    # Get item
    result = await db.execute(
        select(Item).where(Item.id == item_id)
    )
    item = result.scalar_one_or_none()
    
    # Check if exists
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Check organization (anti-enumeration)
    if item.organization_id != organization_id:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Update fields
    for field, value in item_data.dict(exclude_unset=True).items():
        setattr(item, field, value)
    
    item.updated_by = current_user.id
    
    await db.commit()
    await db.refresh(item)
    
    return item
```

### Pattern 5: Delete Record (Delete)

```python
@router.delete("/items/{item_id}")
async def delete_item(
    item_id: int,
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_access("item", "delete"))
):
    current_user, organization_id = auth
    
    # Get item
    result = await db.execute(
        select(Item).where(Item.id == item_id)
    )
    item = result.scalar_one_or_none()
    
    # Check if exists
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Check organization (anti-enumeration)
    if item.organization_id != organization_id:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Soft delete (preferred) or hard delete
    item.is_deleted = True
    item.deleted_by = current_user.id
    # Or: await db.delete(item)
    
    await db.commit()
    
    return {"message": "Item deleted successfully"}
```

---

## Special Cases

### Super Admin Bypass

Super admins can access all organizations:

```python
@router.get("/admin/items")
async def admin_list_all_items(
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_access("item", "read"))
):
    current_user, organization_id = auth
    
    # Super admins can see all
    if current_user.is_super_admin:
        stmt = select(Item)
    else:
        stmt = select(Item).where(Item.organization_id == organization_id)
    
    result = await db.execute(stmt)
    return result.scalars().all()
```

### Multiple Permissions

Require multiple permissions:

```python
from app.core.enforcement import require_access, check_permissions

@router.post("/items/bulk-delete")
async def bulk_delete_items(
    item_ids: List[int],
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_access("item", "delete"))
):
    current_user, organization_id = auth
    
    # Additional permission check
    if len(item_ids) > 100:
        # Require special permission for large operations
        if not check_permissions(current_user, "item", "bulk_delete"):
            raise HTTPException(
                status_code=403,
                detail="Bulk delete permission required for >100 items"
            )
    
    # ... deletion logic
```

### Pre-Auth Endpoints

Public endpoints (no RBAC required):

```python
# Login - no auth required
@router.post("/auth/login")
async def login(
    credentials: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    # No require_access dependency
    # Public endpoint
    pass

# Password reset - no auth required  
@router.post("/password/reset")
async def reset_password(
    reset_data: PasswordResetRequest,
    db: AsyncSession = Depends(get_db)
):
    # No require_access dependency
    # Pre-auth endpoint
    pass
```

---

## Testing RBAC

### Test 1: Permission Check

```python
import pytest
from fastapi.testclient import TestClient

def test_list_items_requires_permission(client: TestClient):
    # No auth token
    response = client.get("/api/v1/items")
    assert response.status_code == 401
    
    # Wrong permission
    token = create_token(user_id=1, org_id=1, permissions=["product:read"])
    response = client.get(
        "/api/v1/items",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403
    
    # Correct permission
    token = create_token(user_id=1, org_id=1, permissions=["item:read"])
    response = client.get(
        "/api/v1/items",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
```

### Test 2: Tenant Isolation

```python
def test_cannot_access_other_org_items(client: TestClient, db: Session):
    # Create items in org 1 and org 2
    org1_item = Item(id=1, name="Org 1 Item", organization_id=1)
    org2_item = Item(id=2, name="Org 2 Item", organization_id=2)
    db.add_all([org1_item, org2_item])
    db.commit()
    
    # Org 1 user token
    token = create_token(user_id=1, org_id=1, permissions=["item:read"])
    
    # Can access org 1 item
    response = client.get(
        "/api/v1/items/1",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    
    # Cannot access org 2 item (404, not 403 for anti-enumeration)
    response = client.get(
        "/api/v1/items/2",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404
```

### Test 3: Anti-Enumeration

```python
def test_cross_org_access_returns_404(client: TestClient):
    # Org 1 user tries to access org 2 resource
    token = create_token(user_id=1, org_id=1, permissions=["item:read"])
    
    response = client.get(
        "/api/v1/items/999",  # Exists in org 2
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Should return 404 (not 403) to prevent enumeration
    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"
    # Should NOT reveal that item exists in different org
```

---

## Debugging

### Check User Permissions

```python
from app.services.rbac import RBACService

# In your endpoint or test
permissions = await RBACService.get_user_permissions(
    db, current_user.id, organization_id
)
print(f"User permissions: {permissions}")

# Check specific permission
has_permission = await RBACService.check_permission(
    db, current_user.id, organization_id, "item", "read"
)
print(f"Has item:read permission: {has_permission}")
```

### Common Errors

#### Error: "Not authenticated"
**Status**: 401  
**Cause**: Missing or invalid JWT token  
**Fix**: Ensure `Authorization: Bearer <token>` header is set

#### Error: "Permission denied" or "Forbidden"
**Status**: 403  
**Cause**: User lacks required permission  
**Fix**: 
1. Check user's role: `current_user.role`
2. Check user's permissions: See "Check User Permissions" above
3. Grant required permission via admin panel

#### Error: "Item not found"
**Status**: 404  
**Cause**: Item doesn't exist OR belongs to different organization  
**Fix**: 
1. Verify item ID is correct
2. Check item's `organization_id` matches user's organization
3. This is expected for cross-org access (anti-enumeration)

---

## Best Practices

### ✅ DO

1. **Always filter by organization_id**
   ```python
   stmt = select(Item).where(Item.organization_id == organization_id)
   ```

2. **Return 404 for cross-org access** (anti-enumeration)
   ```python
   if item.organization_id != organization_id:
       raise HTTPException(status_code=404, detail="Item not found")
   ```

3. **Use tuple unpacking for auth**
   ```python
   current_user, organization_id = auth
   ```

4. **Validate permissions early**
   ```python
   auth: tuple = Depends(require_access("module", "action"))
   ```

### ❌ DON'T

1. **Don't skip organization filtering**
   ```python
   # BAD - Shows all organizations' data
   items = await db.execute(select(Item))
   ```

2. **Don't return 403 for cross-org access**
   ```python
   # BAD - Reveals item exists in different org
   if item.organization_id != organization_id:
       raise HTTPException(status_code=403, detail="Access denied")
   ```

3. **Don't hardcode permissions**
   ```python
   # BAD - Hardcoded permission check
   if current_user.role != "admin":
       raise HTTPException(status_code=403)
   ```

4. **Don't forget to handle super admin**
   ```python
   # INCOMPLETE - Doesn't handle super admin case
   stmt = select(Item).where(Item.organization_id == organization_id)
   ```

---

## Next Steps

1. **Read Full Documentation**
   - `RBAC_COMPREHENSIVE_GUIDE.md` - Complete reference
   - `RBAC_TENANT_ENFORCEMENT_GUIDE.md` - Implementation details
   - `PAID_USER_GUIDE.md` - User perspective

2. **Review Examples**
   - Check existing migrated files in `app/api/`
   - Look at test files in `tests/test_rbac*.py`

3. **Test Your Implementation**
   - Write unit tests for permissions
   - Write integration tests for workflows
   - Test cross-org access (should fail with 404)

4. **Ask for Help**
   - Slack: #rbac-migration
   - Email: dev-team@company.com
   - Docs: https://docs.fastapiv16.com

---

## Cheat Sheet

| Task | Code |
|------|------|
| Add RBAC to endpoint | `auth: tuple = Depends(require_access("module", "action"))` |
| Unpack auth | `current_user, organization_id = auth` |
| Filter by org | `.where(Model.organization_id == organization_id)` |
| Check super admin | `if current_user.is_super_admin:` |
| Anti-enumeration | `raise HTTPException(status_code=404, detail="Not found")` |
| Create with org | `item.organization_id = organization_id` |

---

**Quick Reference**: Keep this guide handy while implementing RBAC!  
**Questions?**: Check the full documentation or ask the team.

**Happy Coding! 🚀**
