# RBAC Fixes Test Plan

## Test Environment Setup

### Test Users
1. **God Superadmin:** `naughtyfruit53@gmail.com` (no organization_id)
2. **App-Level Superadmin:** Any superadmin user without organization_id
3. **Organization Superadmin:** Superadmin user with organization_id
4. **Organization User:** Regular user with organization_id

## Test Cases

### 1. Settings Menu Visibility Tests

#### Test 1.1: Organization User - Settings Menu
**User:** Organization User  
**Steps:**
1. Login as organization user
2. Click Settings in mega menu
3. Verify menu items visible

**Expected Results:**
- ✅ General Settings visible
- ✅ Company Profile visible
- ✅ User Management visible
- ✅ Voucher Settings visible
- ❌ Data Management NOT visible
- ❌ Factory Reset NOT visible
- ❌ Add User NOT visible
- ❌ Advanced User Management NOT visible

#### Test 1.2: Organization Superadmin - Settings Menu
**User:** Organization Superadmin  
**Steps:**
1. Login as organization superadmin
2. Click Settings in mega menu
3. Verify menu items visible

**Expected Results:**
- ✅ General Settings visible
- ✅ Company Profile visible
- ✅ User Management visible
- ✅ Voucher Settings visible
- ❌ Data Management NOT visible
- ❌ Factory Reset NOT visible

#### Test 1.3: App-Level Superadmin - Settings Menu
**User:** App-Level Superadmin  
**Steps:**
1. Login as app-level superadmin (no organization)
2. Click Settings in mega menu
3. Verify menu items visible

**Expected Results:**
- ✅ General Settings visible
- ✅ Company Profile visible
- ✅ User Management visible
- ✅ Voucher Settings visible
- ❌ Data Management NOT visible
- ❌ Factory Reset NOT visible

#### Test 1.4: God Superadmin - Settings Menu
**User:** God Superadmin (naughtyfruit53@gmail.com)  
**Steps:**
1. Login as god superadmin
2. Click Settings in mega menu
3. Verify ALL menu items visible

**Expected Results:**
- ✅ General Settings visible
- ✅ Company Profile visible
- ✅ User Management visible
- ✅ Voucher Settings visible
- ✅ Data Management visible
- ✅ Factory Reset visible

### 2. License Management Access Tests

#### Test 2.1: Organization User - License Management
**User:** Organization User  
**Steps:**
1. Navigate to `/admin/license-management`

**Expected Results:**
- ❌ Access Restricted error page
- ✅ Message: "License management is only available to platform super administrators"
- ✅ Return to Dashboard button

#### Test 2.2: Organization Superadmin - License Management
**User:** Organization Superadmin  
**Steps:**
1. Navigate to `/admin/license-management`

**Expected Results:**
- ❌ Access Restricted error page
- ✅ Message: "Organization-level administrators cannot access this feature"

#### Test 2.3: App-Level Superadmin - License Management
**User:** App-Level Superadmin  
**Steps:**
1. Navigate to `/admin/license-management`
2. Verify page loads successfully

**Expected Results:**
- ✅ License Management page loads
- ✅ Can view all organizations
- ✅ Can create new licenses
- ✅ Can reset organization passwords

#### Test 2.4: License Management Not in Org Admin Menu
**User:** Organization Superadmin  
**Steps:**
1. Navigate to `/admin`
2. Check for License Management card

**Expected Results:**
- ❌ License Management card NOT visible

### 3. Data Management Access Tests

#### Test 3.1: Organization User - Data Management
**User:** Organization User  
**Steps:**
1. Navigate to `/settings/DataManagement`

**Expected Results:**
- ❌ Access Restricted error page
- ✅ Message: "Data management and factory reset operations are only available to the god superadmin account"
- ✅ Return to Dashboard button

#### Test 3.2: App-Level Superadmin - Data Management
**User:** App-Level Superadmin  
**Steps:**
1. Navigate to `/settings/DataManagement`

**Expected Results:**
- ❌ Access Restricted error page
- ✅ Restricted to god superadmin only

#### Test 3.3: God Superadmin - Data Management
**User:** God Superadmin (naughtyfruit53@gmail.com)  
**Steps:**
1. Navigate to `/settings/DataManagement`
2. Verify page loads successfully

**Expected Results:**
- ✅ Data Management page loads
- ✅ Warning message about factory reset
- ✅ "Factory Default - Reset Entire App" button visible
- ✅ Can perform factory reset (with confirmation)

### 4. Factory Reset Access Tests

#### Test 4.1: Organization Superadmin - Factory Reset
**User:** Organization Superadmin  
**Steps:**
1. Navigate to `/settings/FactoryReset`

**Expected Results:**
- ✅ Page loads showing organization data reset option
- ❌ Factory Default option NOT visible

#### Test 4.2: App-Level Superadmin - Factory Reset
**User:** App-Level Superadmin  
**Steps:**
1. Navigate to `/settings/FactoryReset`

**Expected Results:**
- ❌ Factory Default option NOT visible (only for god superadmin)

#### Test 4.3: God Superadmin - Factory Reset
**User:** God Superadmin (naughtyfruit53@gmail.com)  
**Steps:**
1. Navigate to `/settings/FactoryReset`
2. Verify Factory Default option visible

**Expected Results:**
- ✅ Factory Default card visible
- ✅ Can perform factory reset
- ✅ Confirmation dialog appears

### 5. Voucher Settings Access Tests

#### Test 5.1: Organization User - Voucher Settings
**User:** Organization User  
**Steps:**
1. Navigate to Settings menu
2. Click Voucher Settings

**Expected Results:**
- ✅ Voucher Settings page loads at `/settings/voucher-settings`
- ✅ Can view voucher settings
- ✅ Can modify settings if permitted

### 6. RBAC Backend Validation Tests

#### Test 6.1: Invalid organization_id - Create Role
**API:** `POST /api/v1/rbac/organizations/{organization_id}/roles`  
**Test Data:**
```json
{
  "organization_id": 0,
  "name": "admin",
  "display_name": "Admin Role"
}
```

**Expected Results:**
- ❌ HTTP 400 Bad Request
- ✅ Error message: "Invalid organization_id. Must be a positive integer."

#### Test 6.2: Invalid organization_id - Get Roles
**API:** `GET /api/v1/rbac/organizations/0/roles`

**Expected Results:**
- ❌ HTTP 400 Bad Request
- ✅ Error message: "Invalid organization_id. Must be a positive integer."

#### Test 6.3: Invalid Module - Get Permissions
**API:** `GET /api/v1/rbac/permissions?module=sticky_notes`

**Expected Results:**
- ❌ HTTP 400 Bad Request
- ✅ Error message: "Invalid module 'sticky_notes'"
- ✅ Lists valid modules

#### Test 6.4: Invalid Action - Get Permissions
**API:** `GET /api/v1/rbac/permissions?action=invalid_action`

**Expected Results:**
- ❌ HTTP 400 Bad Request
- ✅ Error message: "Invalid action 'invalid_action'"
- ✅ Lists valid actions

#### Test 6.5: Permission Filtering - Invalid Module in Database
**Setup:** Create permission with invalid module in database  
**API:** `GET /api/v1/rbac/permissions`

**Expected Results:**
- ✅ HTTP 200 OK
- ✅ Invalid permissions filtered out
- ✅ Only valid permissions returned
- ✅ Warning logged: "Filtering out permission with invalid module/action"

### 7. God Account Consistency Tests

#### Test 7.1: Admin Dashboard - God Account Check
**User:** God Superadmin (naughtyfruit53@gmail.com)  
**Steps:**
1. Navigate to `/admin`
2. Check for App User Management card

**Expected Results:**
- ✅ App User Management card visible
- ✅ Labeled as "Restricted"
- ✅ Only visible to god account

#### Test 7.2: Admin Dashboard - Non-God Superadmin
**User:** App-Level Superadmin (not god account)  
**Steps:**
1. Navigate to `/admin`
2. Check for App User Management card

**Expected Results:**
- ❌ App User Management card NOT visible

#### Test 7.3: App User Management Page - God Account
**User:** God Superadmin (naughtyfruit53@gmail.com)  
**Steps:**
1. Navigate to `/admin/app-user-management`
2. Check god account shield icon

**Expected Results:**
- ✅ Page loads successfully
- ✅ God account (naughtyfruit53@gmail.com) has gold shield icon
- ✅ God account cannot be deleted

### 8. Documentation Tests

#### Test 8.1: Verify FEATURE_ACCESS_MAPPING.md
**Steps:**
1. Open `docs/FEATURE_ACCESS_MAPPING.md`
2. Verify Settings section

**Expected Results:**
- ✅ Voucher Settings listed
- ✅ Data Management marked as "God Super Admin" only
- ✅ Factory Reset marked as "God Super Admin" only
- ✅ License Management marked as "App Super Admin (app-level only)"

## Regression Tests

### Test 9.1: Existing RBAC Functionality
**Steps:**
1. Create new service role
2. Assign permissions to role
3. Assign role to user
4. Verify user can access features

**Expected Results:**
- ✅ All existing RBAC operations work correctly
- ✅ No breaking changes

### Test 9.2: Menu Navigation
**Steps:**
1. Navigate through all menu items
2. Verify all paths work correctly

**Expected Results:**
- ✅ All menu items navigate correctly
- ✅ No broken routes
- ✅ All pages load successfully

## Performance Tests

### Test 10.1: Permission Filtering Performance
**API:** `GET /api/v1/rbac/permissions`  
**Setup:** Database with 1000+ permissions, some invalid

**Expected Results:**
- ✅ Response time < 2 seconds
- ✅ Invalid permissions filtered efficiently
- ✅ No memory issues

## Test Execution Checklist

- [ ] All menu visibility tests passed
- [ ] All access control tests passed
- [ ] All RBAC validation tests passed
- [ ] All god account tests passed
- [ ] Documentation updated and verified
- [ ] Regression tests passed
- [ ] Performance tests passed
- [ ] No console errors
- [ ] No TypeScript errors
- [ ] No Python errors
- [ ] Code reviewed
- [ ] PR description updated

## Known Limitations

1. God superadmin email is hardcoded (`naughtyfruit53@gmail.com`)
2. Menu filtering happens client-side (consider server-side for better security)
3. No automated tests created yet (manual testing required)

## Next Steps

1. Create automated test suite for RBAC
2. Add integration tests for menu visibility
3. Add E2E tests for access control flows
4. Consider making god superadmin email configurable
5. Add audit logging for god superadmin actions
