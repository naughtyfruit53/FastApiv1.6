# Menu Permission Quick Reference

## Quick Permission Checker

### Testing Menu Visibility

1. **Open Browser Console** (F12)
2. **Navigate to Menu** you want to test
3. **Look for logs** like:
   ```
   Permission check failed for item Vendors: requires master_data.read
   Module access check failed for item Products: requires module master_data
   ```

### Common Fixes

| Issue | Solution |
|-------|----------|
| Menu items missing | Check user has permission + module enabled |
| Menu doesn't expand | Wait for fix (auto-expansion now implemented) |
| Empty menu message | User needs permissions or modules enabled |
| All items hidden | Check organization enabled_modules |

## Permission Format Reference

### Module Permissions (Dot Notation)

```
Format: <module>.<action>
Examples:
  master_data.read
  inventory.create
  finance.update
  manufacturing.delete
```

### Service Permissions (Underscore)

```
Format: <module>_<action>
Examples:
  service_create
  technician_read
  appointment_update
  work_order_delete
```

## Module -> Permission Mapping

| Menu Section | Module | Permission Example | Enabled Check |
|-------------|---------|-------------------|---------------|
| Master Data | `master_data` | `master_data.read` | ✓ |
| Inventory | `inventory` | `inventory.read` | ✓ |
| Manufacturing | `manufacturing` | `manufacturing.read` | ✓ |
| Vouchers | `vouchers` | `vouchers.read` | ✓ |
| Finance | `finance` | `finance.read` | ✓ |
| Accounting | `accounting` | `accounting.read` | ✓ |
| Reports | `reports` | `reports.read` | ✓ |
| AI & Analytics | `ai_analytics` | `ai_analytics.read` | ✓ |
| Sales | `sales` | `sales.read` | ✓ |
| Marketing | `marketing` | `marketing.read` | ✓ |
| Service | `service` | `service.read` | ✓ |
| Projects | `projects` | `projects.read` | ✓ |
| HR | `hr` | `hr.read` | ✓ |
| Tasks & Calendar | `tasks_calendar` | `tasks_calendar.read` | ✓ |
| Email | `email` | `email.read` | ✓ |
| Settings | `settings` | `settings.read` | ✓ |

## Adding a New Menu Item - 3 Steps

### 1. Backend Permission (if new)

```python
# app/core/permissions.py or RBAC service
MY_MODULE_READ = "my_module.read"
```

### 2. Frontend Menu Config

```typescript
// frontend/src/components/menuConfig.tsx
{
  name: 'My Feature',
  path: '/my-feature',
  icon: <MyIcon />,
  permission: 'my_module.read',
  requireModule: 'my_module',
  requireSubmodule: {
    module: 'my_module',
    submodule: 'my_feature'
  }
}
```

### 3. Test with Different Roles

- ✅ Super Admin: Should see it
- ✅ User with permission: Should see it
- ❌ User without permission: Should NOT see it

## Debugging Commands

### Check User Permissions (Backend)
```bash
curl -X GET "http://localhost:8000/rbac/users/{user_id}/permissions" \
  -H "Authorization: Bearer {token}"
```

### Check Organization Modules
```bash
curl -X GET "http://localhost:8000/organizations/current" \
  -H "Authorization: Bearer {token}"
```

### Browser Console Checks
```javascript
// Check if user object is loaded
console.log(user);

// Check permission data from AuthContext
console.log(userPermissions);

// Check organization data
console.log(organizationData);
```

## Permission Hierarchy

```
Super Admin (naughtyfruit53@gmail.com)
  └─> God Super Admin Only Items
  
App Super Admin
  └─> Super Admin Only Items
  └─> All Module Items (bypasses org-specific checks)
  
Org Admin
  └─> Organization Items
  └─> Based on enabled_modules + user permissions
  
Regular Users
  └─> Based on enabled_modules + user permissions + role
```

## Wildcard Permissions

```typescript
// These grant access to ALL actions in a module:
'master_data.*'  // All master data permissions
'inventory.*'    // All inventory permissions
'finance.*'      // All finance permissions
```

## Special Flags

```typescript
// In menuConfig.tsx:
{
  godSuperAdminOnly: true,   // Only naughtyfruit53@gmail.com
  superAdminOnly: true,      // Only app super admins
  role: 'admin',             // Requires specific role
  servicePermission: 'xyz',  // Service CRM permission
}
```

## API Quick Reference

| Endpoint | Purpose |
|----------|---------|
| `GET /rbac/users/{id}/permissions` | Get user permissions |
| `GET /users/me` | Get current user |
| `GET /organizations/current` | Get org + enabled modules |
| `GET /rbac/permissions` | List all permissions |
| `GET /rbac/organizations/{id}/roles` | Get org roles |

## Troubleshooting Checklist

- [ ] User has correct role assigned
- [ ] User has required permission
- [ ] Module is enabled in organization
- [ ] Permission format matches (dot vs underscore)
- [ ] Menu config has correct permission key
- [ ] Browser console shows no errors
- [ ] Hard refresh browser (Ctrl+Shift+R)

## Contact

For permission issues:
1. Check this guide
2. Check MENU_PERMISSION_GUIDE.md for detailed info
3. Check browser console logs
4. Contact system administrator

## Related Files

- `/frontend/src/components/MegaMenu.tsx` - Menu rendering
- `/frontend/src/components/menuConfig.tsx` - Menu structure
- `/frontend/src/hooks/useSharedPermissions.ts` - Permission hooks
- `/frontend/src/context/AuthContext.tsx` - Auth + permissions
- `/app/core/permissions.py` - Backend permissions
- `/app/api/v1/rbac.py` - RBAC API endpoints
