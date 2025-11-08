# Module Entitlement Restrictions - Implementation Guide

## Overview

This guide documents the implementation of strict access controls for module entitlement management, ensuring that only **App Super Admins** (platform administrators) can activate or deactivate modules for organizations.

## Background

Module entitlement management is a licensing and billing operation that affects an organization's access to platform features. Prior to this implementation, the system used RBAC permissions which could potentially allow organization administrators to modify their own module entitlements. This implementation enforces a strict super_admin-only policy.

## Key Principles

1. **Super Admin Only**: Only users with `is_super_admin=True` can modify module entitlements
2. **Read-Only for Org Admins**: Organization administrators can view but not modify entitlements
3. **Clear User Communication**: Users receive helpful error messages explaining restrictions
4. **Consistent Enforcement**: Restrictions apply across both backend API and frontend UI
5. **Audit Trail**: All entitlement changes are logged with the acting user

## Implementation Details

### Backend Enforcement

#### 1. Organization Modules API (`/api/v1/organizations/{org_id}/modules`)

**PUT Endpoint (Update Modules)**
- **Access**: Super Admin ONLY
- **Method**: Direct `is_super_admin` check (bypasses RBAC)
- **Error Response**: HTTP 403 with detailed explanation

```python
@router.put("/{organization_id:int}/modules")
async def update_organization_modules(
    organization_id: int,
    modules_data: dict,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    # Strict super_admin check - this is a licensing operation
    if not current_user.is_super_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error_type": "permission_denied",
                "message": "Module entitlement management is restricted to platform administrators only...",
                "required_role": "super_admin",
                "current_role": current_user.role
            }
        )
```

**GET Endpoint (View Modules)**
- **Access**: Org Admin and Super Admin (read-only)
- **Method**: RBAC via `require_access("organization_module", "read")`

#### 2. Admin Entitlement APIs (`/api/v1/admin/...`)

All admin entitlement endpoints require super_admin:
- `GET /admin/modules` - List all available modules
- `GET /admin/orgs/{org_id}/entitlements` - View org entitlements
- `PUT /admin/orgs/{org_id}/entitlements` - Update org entitlements
- `POST /admin/categories/orgs/{org_id}/activate` - Activate category
- `POST /admin/categories/orgs/{org_id}/deactivate` - Deactivate category

All use `Depends(get_current_super_admin)` dependency.

#### 3. Error Response Format

When an org admin attempts to update modules:

```json
{
  "detail": {
    "error_type": "permission_denied",
    "message": "Module entitlement management is restricted to platform administrators only. Organization administrators cannot activate or deactivate modules. Please contact your platform administrator to request module changes.",
    "required_role": "super_admin",
    "current_role": "org_admin"
  }
}
```

### Frontend Enforcement

#### 1. ModuleSelectionModal Component

**Props**:
- `isSuperAdmin: boolean` - Controls editing capability

**Behavior**:
- **Super Admin**: Full editing capability with Save button
- **Org Admin**: Read-only view with disabled checkboxes and Close button
- **Warning Alert**: Displayed to non-super admins explaining the restriction

**Visual Changes**:
```tsx
{!isSuperAdmin && (
  <Alert severity="warning" sx={{ mb: 2 }}>
    <Typography variant="body2" fontWeight="bold">
      Super Admin Access Required
    </Typography>
    <Typography variant="body2">
      Module entitlement management is restricted to platform administrators only.
      Organization administrators cannot activate or deactivate modules.
      Please contact your platform administrator to request module changes.
    </Typography>
  </Alert>
)}
```

#### 2. Organization Management Page

**Module Control Button**:
- Disabled for non-super admins
- Tooltip explains the restriction

```tsx
<Tooltip 
  title={isSuperAdmin 
    ? "Manage module entitlements (Super Admin only)" 
    : "Module entitlement management requires Super Admin access"
  }
>
  <span>
    <IconButton
      onClick={() => handleModuleControl(org)}
      disabled={!isSuperAdmin}
    >
      <Settings />
    </IconButton>
  </span>
</Tooltip>
```

## User Experience

### Super Admin Flow

1. Super admin logs into the admin panel
2. Navigates to "Manage Organizations"
3. Clicks the Module Control button (enabled with gear icon)
4. ModuleSelectionModal opens with editable checkboxes
5. Selects/deselects module bundles
6. Clicks "Save" to apply changes
7. Receives success notification
8. Changes are immediately reflected

### Org Admin Flow

1. Org admin logs into the admin panel
2. Navigates to "Manage Organizations" (if they have access)
3. Module Control button is disabled with tooltip
4. If they somehow access the modal, they see:
   - Warning alert about super admin requirement
   - Disabled checkboxes (view-only)
   - "Close" button instead of "Save"
5. If they attempt API call directly, receive 403 error with clear message

### Regular User Flow

- Regular users don't have access to the admin panel
- Cannot view or modify module entitlements
- Their access to features is controlled by:
  1. Organization's enabled modules (set by super admin)
  2. Their assigned modules (set by org admin)
  3. Their RBAC permissions (set by org admin)

## Security Considerations

### Why Direct `is_super_admin` Check?

We bypass RBAC for module updates because:

1. **Licensing Operation**: Module entitlement is fundamentally different from feature permissions
2. **Prevent Escalation**: Org admins could potentially grant themselves `organization_module.update` permission
3. **Clear Separation**: Super admin is a platform role, not an organization role
4. **Audit and Control**: Centralized control point for licensing decisions

### Defense in Depth

The implementation uses multiple layers of protection:

1. **Backend API**: Strict `is_super_admin` check
2. **Frontend UI**: Disabled controls for non-super admins
3. **Error Messages**: Clear communication of restrictions
4. **Audit Logging**: All changes tracked with user ID
5. **Database Schema**: Entitlement tables separate from RBAC

### Bypass Prevention

- RBAC permissions cannot override `is_super_admin` check
- Token manipulation won't work (server-side validation)
- Direct API calls return 403 with explanation
- No fallback or escape routes

## Testing

### Unit Tests

File: `app/tests/test_module_entitlement_restrictions.py`

**Test Coverage**:
1. ✅ Module update requires authentication
2. ✅ Module get accessible to authenticated users
3. ✅ Error message structure is correct
4. ✅ Admin entitlement APIs require super admin
5. ✅ Admin modules API requires super admin
6. ✅ App entitlements endpoint accessible
7. ✅ All required endpoints registered
8. ✅ CORS headers present

### Manual Testing Checklist

- [ ] Super admin can update organization modules
- [ ] Org admin cannot update organization modules (gets 403)
- [ ] Org admin can read organization modules
- [ ] Module Control button disabled for org admin in UI
- [ ] Modal shows warning for org admin
- [ ] Modal checkboxes disabled for org admin
- [ ] Save button hidden for org admin
- [ ] Tooltip shows correct message
- [ ] Direct API call by org admin returns 403
- [ ] Error message is clear and actionable

### Integration Testing

1. Create test super admin user
2. Create test org admin user
3. Create test organization
4. Verify super admin can update modules
5. Verify org admin cannot update modules
6. Verify org admin can view modules
7. Verify frontend reflects changes immediately

## Deployment

### Prerequisites

- Existing entitlement schema (already deployed)
- Super admin user seeded
- Frontend environment variables configured
- Backend authentication working

### Deployment Steps

1. **Backend Deployment**
   ```bash
   # Deploy updated module_routes.py
   git pull origin main
   # Restart backend services
   systemctl restart fastapi-app
   ```

2. **Frontend Deployment**
   ```bash
   # Deploy updated components
   npm run build
   npm run deploy
   ```

3. **Verification**
   - Test super admin can update modules
   - Test org admin receives 403
   - Check error logs for any issues
   - Verify UI displays correctly

### Rollback Plan

If issues occur:

1. **Backend Rollback**
   ```bash
   git revert <commit-hash>
   systemctl restart fastapi-app
   ```

2. **Frontend Rollback**
   ```bash
   git revert <commit-hash>
   npm run build
   npm run deploy
   ```

3. **Quick Fix**: Temporarily allow org admins by adding bypass (not recommended):
   ```python
   if not current_user.is_super_admin and not current_user.role == "org_admin":
       raise HTTPException(...)
   ```

## Monitoring

### Metrics to Track

- `entitlement_update_attempts_total` - Total update attempts
- `entitlement_update_denied_total` - Denied by role check
- `entitlement_update_success_total` - Successful updates
- `module_selection_modal_opens_total` - UI interactions

### Alerts

- High rate of 403 errors on module endpoints
- Repeated attempts by org admins to update modules
- Unexpected changes to entitlements

### Logging

All entitlement update attempts are logged:

```
logger.warning(
    f"User {current_user.email} (role: {current_user.role}) attempted to update modules "
    f"for organization {organization_id}. Only super_admin can perform this action."
)
```

## Troubleshooting

### Issue: Org admin claims they need to update modules

**Solution**: This is by design. Explain:
- Module entitlements are licensing decisions
- Only platform administrators can modify them
- Org admin should request changes through proper channels

### Issue: Super admin cannot update modules

**Diagnosis**:
1. Check `is_super_admin` flag in database
2. Verify authentication token is valid
3. Check API error response
4. Review server logs

### Issue: Frontend shows Save button for org admin

**Diagnosis**:
1. Check `isSuperAdmin` prop is passed correctly
2. Verify user object has correct `is_super_admin` value
3. Check AuthContext is properly initialized
4. Review browser console for errors

### Issue: API returns 403 but should allow

**Diagnosis**:
1. Verify user truly has `is_super_admin=True`
2. Check token hasn't expired
3. Verify organization ID is correct
4. Review API endpoint implementation

## FAQ

**Q: Why can't org admins manage their own modules?**
A: Module entitlements are licensing and billing decisions that affect platform revenue. Only platform administrators should control these.

**Q: Can we add a "request module" feature for org admins?**
A: Yes! This would be a great enhancement. Org admins could submit requests that super admins review and approve.

**Q: What if we want to allow org admins to manage modules in development?**
A: You can add an environment variable flag, but this should NEVER be enabled in production.

**Q: How do we audit entitlement changes?**
A: All changes are logged via the `entitlement_events` table with user ID, timestamp, and change details.

**Q: Can RBAC override this restriction?**
A: No. The `is_super_admin` check is performed before RBAC checks and cannot be overridden.

## Related Documentation

- [ENTITLEMENT_ROLES_CLARIFICATION.md](./ENTITLEMENT_ROLES_CLARIFICATION.md) - Role hierarchy and responsibilities
- [ENTITLEMENTS_IMPLEMENTATION_SUMMARY.md](./ENTITLEMENTS_IMPLEMENTATION_SUMMARY.md) - Overall entitlement system
- [RBAC_COMPREHENSIVE_GUIDE.md](./RBAC_COMPREHENSIVE_GUIDE.md) - RBAC system documentation
- [NEW_ROLE_SYSTEM_DOCUMENTATION.md](./NEW_ROLE_SYSTEM_DOCUMENTATION.md) - User role system

## Support

For issues or questions:
1. Check this documentation
2. Review related documentation above
3. Check server logs for error details
4. Contact platform engineering team

---

**Version**: 1.0.0
**Last Updated**: 2025-11-03
**Status**: Active
**Authors**: GitHub Copilot Team
