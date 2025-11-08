#!/usr/bin/env python3
"""
Script to help apply RBAC and tenant enforcement to route files.
This script analyzes a route file and suggests changes needed.
"""

import sys
import re
from pathlib import Path
from typing import List, Tuple

def analyze_route_file(filepath: Path) -> dict:
    """Analyze a route file and provide enforcement recommendations"""
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Find all route definitions
    routes = re.findall(r'@router\.(get|post|put|patch|delete)\([^)]*\)\s*(?:async\s+)?def\s+(\w+)', content)
    
    # Check for enforcement imports
    has_require_access = 'require_access' in content
    has_tenant_enforcement = 'TenantEnforcement' in content
    
    # Check for current patterns
    uses_get_current_active_user = 'get_current_active_user' in content
    uses_organization_id = bool(re.search(r'current_user\.organization_id|organization_id\s*=', content))
    
    # Determine module name from path
    module_name = filepath.stem.replace('_', '-')
    
    recommendations = []
    
    if not has_require_access:
        recommendations.append("Add import: from app.core.enforcement import require_access")
    
    if uses_get_current_active_user:
        recommendations.append(f"Found {len(routes)} routes using get_current_active_user")
        recommendations.append("Replace with: auth: tuple = Depends(require_access('module', 'action'))")
    
    if uses_organization_id:
        recommendations.append("Organization ID checks found - good!")
        recommendations.append("Ensure all queries use org_id from auth tuple")
    else:
        recommendations.append("WARNING: No organization_id checks found!")
        recommendations.append("Add organization scoping to all database queries")
    
    return {
        'file': filepath,
        'routes': routes,
        'has_enforcement': has_require_access,
        'has_org_checks': uses_organization_id,
        'recommendations': recommendations,
        'module_name': module_name
    }

def suggest_module_permissions(module_name: str) -> List[str]:
    """Suggest permission names for a module"""
    base_name = module_name.replace('-', '_').replace('voucher', 'voucher').replace('_routes', '')
    
    return [
        f"{base_name}_create",
        f"{base_name}_read",
        f"{base_name}_update",
        f"{base_name}_delete",
    ]

def generate_migration_template(analysis: dict) -> str:
    """Generate a template showing how to migrate the file"""
    
    module = analysis['module_name'].replace('-', '_')
    if 'voucher' in module:
        module = 'voucher'
    
    template = f"""
# Migration Template for {analysis['file'].name}
# ============================================

## Step 1: Add Imports
```python
from app.core.enforcement import require_access
```

## Step 2: Update Each Route

### Example - List Endpoint
BEFORE:
```python
@router.get("/items")
async def get_items(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    stmt = select(Model).where(Model.organization_id == current_user.organization_id)
    ...
```

AFTER:
```python
@router.get("/items")
async def get_items(
    auth: tuple = Depends(require_access("{module}", "read")),
    db: AsyncSession = Depends(get_db)
):
    user, org_id = auth
    stmt = select(Model).where(Model.organization_id == org_id)
    ...
```

### Example - Create Endpoint
BEFORE:
```python
@router.post("/items")
async def create_item(
    item: ItemCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_item = Model(**item.dict(), organization_id=current_user.organization_id)
    ...
```

AFTER:
```python
@router.post("/items")
async def create_item(
    item: ItemCreate,
    auth: tuple = Depends(require_access("{module}", "create")),
    db: AsyncSession = Depends(get_db)
):
    user, org_id = auth
    db_item = Model(**item.dict(), organization_id=org_id, created_by_id=user.id)
    ...
```

### Example - Update Endpoint
BEFORE:
```python
@router.put("/items/{{item_id}}")
async def update_item(
    item_id: int,
    item: ItemUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    stmt = select(Model).where(
        Model.id == item_id,
        Model.organization_id == current_user.organization_id
    )
    ...
```

AFTER:
```python
@router.put("/items/{{item_id}}")
async def update_item(
    item_id: int,
    item: ItemUpdate,
    auth: tuple = Depends(require_access("{module}", "update")),
    db: AsyncSession = Depends(get_db)
):
    user, org_id = auth
    stmt = select(Model).where(
        Model.id == item_id,
        Model.organization_id == org_id
    )
    ...
```

### Example - Delete Endpoint
BEFORE:
```python
@router.delete("/items/{{item_id}}")
async def delete_item(
    item_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    stmt = select(Model).where(
        Model.id == item_id,
        Model.organization_id == current_user.organization_id
    )
    ...
```

AFTER:
```python
@router.delete("/items/{{item_id}}")
async def delete_item(
    item_id: int,
    auth: tuple = Depends(require_access("{module}", "delete")),
    db: AsyncSession = Depends(get_db)
):
    user, org_id = auth
    stmt = select(Model).where(
        Model.id == item_id,
        Model.organization_id == org_id
    )
    ...
```

## Step 3: Permission Mappings

Routes found in {analysis['file'].name}:
{chr(10).join(f"- {method.upper():6} {func}() → Needs '{module}_{_get_action_from_name(func, method)}'" for method, func in analysis['routes'])}

## Step 4: Suggested Permissions
{chr(10).join(f"- {perm}" for perm in suggest_module_permissions(module))}

## Step 5: Testing Checklist
- [ ] All endpoints use require_access dependency
- [ ] All queries filter by org_id
- [ ] Test cross-org access is denied (returns 404)
- [ ] Test without permissions (returns 403)
- [ ] Test super admin can access
- [ ] Verify audit logs

## Step 6: Common Patterns

### Pattern: List with Filters
```python
auth: tuple = Depends(require_access("{module}", "read"))
user, org_id = auth

stmt = select(Model).where(Model.organization_id == org_id)
if some_filter:
    stmt = stmt.where(Model.field == value)
```

### Pattern: Get Single Item
```python
auth: tuple = Depends(require_access("{module}", "read"))
user, org_id = auth

stmt = select(Model).where(
    Model.id == item_id,
    Model.organization_id == org_id
)
result = await db.execute(stmt)
item = result.scalar_one_or_none()
if not item:
    raise HTTPException(status_code=404, detail="Not found")
```

### Pattern: Create with Metadata
```python
auth: tuple = Depends(require_access("{module}", "create"))
user, org_id = auth

db_item = Model(
    **item_data.dict(),
    organization_id=org_id,
    created_by_id=user.id,
    created_at=datetime.utcnow()
)
```
"""
    return template

def _get_action_from_name(func_name: str, method: str) -> str:
    """Determine action from function name and HTTP method"""
    func_lower = func_name.lower()
    
    if method == 'get':
        if 'list' in func_lower or func_name.endswith('s'):
            return 'read'
        return 'read'
    elif method == 'post':
        return 'create'
    elif method in ['put', 'patch']:
        return 'update'
    elif method == 'delete':
        return 'delete'
    
    return 'read'  # default

def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze_route_for_enforcement.py <path_to_route_file.py>")
        print("\nExample:")
        print("  python analyze_route_for_enforcement.py app/api/v1/vouchers/purchase_voucher.py")
        sys.exit(1)
    
    filepath = Path(sys.argv[1])
    
    if not filepath.exists():
        print(f"Error: File not found: {filepath}")
        sys.exit(1)
    
    print(f"\n{'='*80}")
    print(f"Analyzing: {filepath}")
    print(f"{'='*80}\n")
    
    analysis = analyze_route_file(filepath)
    
    print(f"Module: {analysis['module_name']}")
    print(f"Routes found: {len(analysis['routes'])}")
    print(f"Has enforcement: {'✅' if analysis['has_enforcement'] else '❌'}")
    print(f"Has org checks: {'✅' if analysis['has_org_checks'] else '⚠️'}")
    
    print(f"\n{'='*80}")
    print("RECOMMENDATIONS")
    print(f"{'='*80}")
    for rec in analysis['recommendations']:
        print(f"  • {rec}")
    
    print(f"\n{'='*80}")
    print("MIGRATION TEMPLATE")
    print(f"{'='*80}")
    print(generate_migration_template(analysis))
    
    # Offer to save template
    save = input("\nSave migration template to file? (y/n): ")
    if save.lower() == 'y':
        output_file = filepath.parent / f"{filepath.stem}_MIGRATION_TEMPLATE.md"
        with open(output_file, 'w') as f:
            f.write(generate_migration_template(analysis))
        print(f"✅ Saved to: {output_file}")

if __name__ == '__main__':
    main()
