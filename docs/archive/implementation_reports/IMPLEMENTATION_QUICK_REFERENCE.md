# 3-Layer Security Implementation - Quick Reference

**Last Updated**: 2025-11-05

## Quick Pattern Reference

### Backend API Endpoint Pattern

```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.enforcement import require_access
from app.utils.tenant_helpers import apply_org_filter

router = APIRouter()

@router.get("/items")
async def get_items(
    auth: tuple = Depends(require_access("module", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get items - Protected by 3-layer security"""
    current_user, org_id = auth  # ⚠️ ALWAYS EXTRACT!
    
    # Query with tenant filter
    stmt = select(Model)
    stmt = apply_org_filter(stmt, Model, user=current_user)
    result = await db.execute(stmt)
    return result.scalars().all()

@router.post("/items")
async def create_item(
    data: ModelCreate,
    auth: tuple = Depends(require_access("module", "create")),
    db: AsyncSession = Depends(get_db)
):
    """Create item - Protected by 3-layer security"""
    current_user, org_id = auth  # ⚠️ ALWAYS EXTRACT!
    
    # Validate org_id in data
    validated_data = validate_data_org_id(data.model_dump(), current_user)
    
    # Create with validated org_id
    item = Model(**validated_data)
    db.add(item)
    await db.commit()
    return item
```

## Common Actions Mapping

| Action | Permission String | Use Case |
|--------|------------------|----------|
| View/List | `"module.read"` | GET endpoints, viewing data |
| Create | `"module.create"` | POST endpoints, creating records |
| Update | `"module.update"` | PUT/PATCH endpoints, editing records |
| Delete | `"module.delete"` | DELETE endpoints, removing records |
| Manage | `"module.manage"` | Admin functions, full control |
| Execute | `"module.execute"` | Special actions, operations |

## Module Keys

Common module keys used in `require_access()`:

- `"user"` - User management
- `"admin"` - Admin functions
- `"crm"` - CRM operations
- `"sales"` - Sales module
- `"inventory"` - Inventory management
- `"manufacturing"` - Manufacturing
- `"finance"` - Financial operations
- `"hr"` - Human resources
- `"email"` - Email functionality
- `"settings"` - Settings pages

## Common Mistakes ❌ → ✅

### Mistake 1: Forgetting to Extract Auth Tuple
```python
# ❌ WRONG - Will fail when accessing current_user or org_id
@router.get("/items")
async def get_items(
    auth: tuple = Depends(require_access("module", "read")),
    db: AsyncSession = Depends(get_db)
):
    # Missing: current_user, org_id = auth
    result = await db.execute(select(Model))  # No tenant filter!
    return result.scalars().all()

# ✅ CORRECT - Always extract immediately
@router.get("/items")
async def get_items(
    auth: tuple = Depends(require_access("module", "read")),
    db: AsyncSession = Depends(get_db)
):
    current_user, org_id = auth  # Extract first!
    stmt = apply_org_filter(select(Model), Model, user=current_user)
    result = await db.execute(stmt)
    return result.scalars().all()
```

### Mistake 2: Using User's org_id Instead of Auth org_id
```python
# ❌ WRONG - Don't use user's organization_id
@router.get("/items")
async def get_items(
    auth: tuple = Depends(require_access("module", "read")),
    db: AsyncSession = Depends(get_db)
):
    current_user, org_id = auth
    organization_id = current_user.organization_id  # Don't do this!
    
# ✅ CORRECT - Use org_id from auth
@router.get("/items")
async def get_items(
    auth: tuple = Depends(require_access("module", "read")),
    db: AsyncSession = Depends(get_db)
):
    current_user, org_id = auth
    # Use org_id directly - it's validated
    stmt = select(Model).where(Model.organization_id == org_id)
```

### Mistake 3: Not Applying Tenant Filter
```python
# ❌ WRONG - No tenant filter, can access other orgs' data
@router.get("/items")
async def get_items(
    auth: tuple = Depends(require_access("module", "read")),
    db: AsyncSession = Depends(get_db)
):
    current_user, org_id = auth
    result = await db.execute(select(Model))  # SECURITY ISSUE!
    return result.scalars().all()

# ✅ CORRECT - Always apply tenant filter
@router.get("/items")
async def get_items(
    auth: tuple = Depends(require_access("module", "read")),
    db: AsyncSession = Depends(get_db)
):
    current_user, org_id = auth
    stmt = apply_org_filter(select(Model), Model, user=current_user)
    result = await db.execute(stmt)
    return result.scalars().all()
```

### Mistake 4: Not Validating org_id on Create
```python
# ❌ WRONG - Accepting org_id from user input without validation
@router.post("/items")
async def create_item(
    data: ModelCreate,
    auth: tuple = Depends(require_access("module", "create")),
    db: AsyncSession = Depends(get_db)
):
    current_user, org_id = auth
    item = Model(**data.model_dump())  # User could set any org_id!
    db.add(item)
    await db.commit()
    return item

# ✅ CORRECT - Validate and set org_id
@router.post("/items")
async def create_item(
    data: ModelCreate,
    auth: tuple = Depends(require_access("module", "create")),
    db: AsyncSession = Depends(get_db)
):
    current_user, org_id = auth
    validated_data = validate_data_org_id(data.model_dump(), current_user)
    item = Model(**validated_data)
    db.add(item)
    await db.commit()
    return item
```

## What require_access Does

When you use `require_access("module", "action")`:

1. ✅ **Layer 1: Tenant** - Validates user belongs to an organization
2. ✅ **Layer 2: Entitlement** - Checks org has access to the module
3. ✅ **Layer 3: RBAC** - Verifies user has the required permission
4. ✅ Returns tuple: `(current_user, org_id)`

All three checks must pass, or the request is denied with 403 Forbidden.

## Essential Imports

```python
# Core enforcement
from app.core.enforcement import require_access

# Tenant helpers
from app.utils.tenant_helpers import (
    apply_org_filter,
    validate_data_org_id,
    enforce_user_org_access,
)

# Database
from app.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

# FastAPI
from fastapi import APIRouter, Depends, HTTPException
```

## Testing Pattern

```python
import pytest
from unittest.mock import AsyncMock, MagicMock

@pytest.mark.asyncio
async def test_endpoint_with_auth():
    """Test endpoint with proper auth"""
    # Mock user and org
    mock_user = MagicMock(spec=User)
    mock_user.id = 1
    mock_user.organization_id = 100
    
    # Mock database
    mock_db = AsyncMock()
    
    # Test your endpoint
    # ...
```

## Quick Checklist

Before merging code with security changes:

- [ ] Used `require_access("module", "action")`
- [ ] Extracted `current_user, org_id = auth`
- [ ] Applied `apply_org_filter` to queries
- [ ] Used `validate_data_org_id` for creates
- [ ] Removed old `get_current_active_user` if replaced
- [ ] No unused imports
- [ ] Syntax validated (run `python3 -m py_compile file.py`)
- [ ] Tested endpoint with different roles

## Example Files to Reference

Look at these recently updated files for examples:

- `app/api/v1/health.py` - Simple read operations
- `app/api/v1/org_user_management.py` - CRUD operations
- `app/api/v1/role_delegation.py` - Admin operations
- `app/tests/test_three_layer_security.py` - Test examples
- `app/tests/test_user_role_flows.py` - Workflow tests

## Getting Help

1. Check **RBAC_DOCUMENTATION.md** for comprehensive docs
2. Check **DEVELOPER_GUIDE_RBAC.md** for detailed guide
3. Check **PendingImplementation.md** for status updates
4. Look at test files for patterns
5. Ask the team

---

**Remember**: All three layers must pass for access to be granted!
