# Testing Guide for RBAC Frontend Integration

## Quick Frontend Testing Checklist

### 1. Test 403 Error Handling

#### Test Scenario 1: User Without Permission
```typescript
// Expected behavior:
// 1. User tries to create a voucher without 'voucher_create' permission
// 2. Backend returns 403
// 3. Frontend shows toast notification: "Access Denied: You don't have permission to perform this action on voucher..."
// 4. Error is logged to console with context
// 5. Component receives enhanced error object
```

**How to Test**:
1. Login as a user without voucher_create permission
2. Navigate to voucher creation page
3. Try to create a voucher
4. Expected: Toast notification appears with permission details
5. Expected: Console shows audit log with user context
6. Expected: Form/component receives error and can handle it

#### Test Scenario 2: Cross-Organization Access
```typescript
// Expected behavior:
// 1. User tries to access resource from different organization
// 2. Backend returns 404 (anti-enumeration, not 403)
// 3. Frontend treats as "not found"
// 4. No information leakage about other organization's data
```

**How to Test**:
1. Login as user in Organization A
2. Try to access resource ID from Organization B (if you know it)
3. Expected: 404 error, not 403
4. Expected: No information about the resource existing

### 2. Test PermissionContext

#### Test hasPermission()
```javascript
// In browser console:
const { hasPermission } = usePermissions();

// Test various permissions
console.log(hasPermission('voucher', 'read'));    // true/false
console.log(hasPermission('voucher', 'create'));  // true/false
console.log(hasPermission('admin', 'delete'));    // true/false
```

#### Test Super Admin
```javascript
// Login as super admin
// All permissions should return true
const { isSuperAdmin, hasPermission } = usePermissions();
console.log('Is Super Admin:', isSuperAdmin);  // Should be true
console.log(hasPermission('any', 'any'));      // Should be true
```

### 3. Test API Interceptor

#### Verify 403 Handling
```javascript
// Make an API call that will fail with 403
// Example: Call a protected endpoint without permission

// Check console for:
// 1. [API] Permission denied: {...}
// 2. Toast notification appears
// 3. Error object has isPermissionDenied: true
```

#### Verify Audit Logging
```javascript
// After triggering a 403 error, check console for:
console.log('Expected log format:', {
  endpoint: '/api/v1/some-endpoint',
  method: 'POST',
  requiredPermission: 'module_action',
  module: 'module',
  action: 'action',
  user: 'user@example.com',
  timestamp: '2025-10-29T...'
});
```

### 4. Test Error Propagation

#### Component Error Handling
```typescript
// In a component using API calls:
const handleCreate = async () => {
  try {
    await voucherService.create(data);
  } catch (error) {
    if (error.isPermissionDenied) {
      // Enhanced error handling
      console.log('Permission denied:', error.requiredPermission);
      console.log('Module:', error.module);
      // Show custom UI
    }
  }
};
```

## Automated Testing

### Unit Tests for 403 Handling

```typescript
// tests/api.test.ts
import { api } from '@/lib/api';
import { toast } from 'react-toastify';

jest.mock('react-toastify');

describe('API 403 Handling', () => {
  it('should show toast on 403 error', async () => {
    // Mock 403 response
    const mockError = {
      response: {
        status: 403,
        data: {
          required_permission: 'voucher_create',
          module: 'voucher',
          action: 'create'
        }
      }
    };
    
    // Trigger error
    try {
      await api.post('/some-endpoint');
    } catch (error) {
      // Verify toast was called
      expect(toast.error).toHaveBeenCalledWith(
        expect.stringContaining('Access Denied'),
        expect.any(Object)
      );
      
      // Verify enhanced error
      expect(error.isPermissionDenied).toBe(true);
      expect(error.requiredPermission).toBe('voucher_create');
    }
  });
});
```

### Integration Tests

```typescript
// tests/rbac-integration.test.ts
describe('RBAC Integration', () => {
  it('should prevent unauthorized access', async () => {
    // Login as user without permissions
    await loginAs('limited-user@test.com');
    
    // Try to access protected resource
    const response = await api.get('/api/v1/admin/users');
    
    // Should get permission denied
    expect(response.status).toBe(403);
    expect(toast.error).toHaveBeenCalled();
  });
  
  it('should allow super admin access', async () => {
    // Login as super admin
    await loginAs('admin@test.com');
    
    // Should access all resources
    const response = await api.get('/api/v1/admin/users');
    expect(response.status).toBe(200);
  });
});
```

## Manual Testing Checklist

### Prerequisites
- [ ] Backend running on http://localhost:8000
- [ ] Frontend running on http://localhost:3000
- [ ] Test users created with different permission levels
- [ ] Browser dev tools open (Console + Network tabs)

### Test Steps

#### 1. Test User Without Permissions
- [ ] Login as user without voucher_create permission
- [ ] Navigate to voucher creation
- [ ] Try to create voucher
- [ ] Verify toast notification appears
- [ ] Check console for audit log
- [ ] Verify error object has isPermissionDenied

#### 2. Test User With Permissions
- [ ] Login as user with voucher_create permission
- [ ] Navigate to voucher creation
- [ ] Create voucher successfully
- [ ] Verify no permission errors
- [ ] Check console for successful request logs

#### 3. Test Super Admin
- [ ] Login as super admin
- [ ] Access various protected resources
- [ ] Verify all actions succeed
- [ ] Check PermissionContext shows isSuperAdmin: true

#### 4. Test Cross-Organization Access
- [ ] Login as user in Org A
- [ ] Try to access resource from Org B
- [ ] Verify 404 response (not 403)
- [ ] No information leakage

#### 5. Test Permission Context
- [ ] Open browser console
- [ ] Check PermissionContext is loaded
- [ ] Verify permissions list
- [ ] Test hasPermission() function

### Expected Results

#### Console Logs
```
[PermissionContext] Loaded permissions: 15 permissions
[API] POST /api/v1/vouchers/sales
[API] Permission denied: {
  endpoint: "/api/v1/vouchers/sales",
  method: "POST",
  requiredPermission: "voucher_create",
  module: "voucher",
  action: "create",
  user: "user@example.com",
  timestamp: "2025-10-29T12:34:56.789Z"
}
```

#### Toast Notification
```
Access Denied: You don't have permission to create on voucher. 
Required permission: voucher_create. 
Please contact your administrator to request access.
```

#### Network Response
```json
// Status: 403 Forbidden
{
  "detail": "Insufficient permissions. Required: voucher_create",
  "required_permission": "voucher_create",
  "module": "voucher",
  "action": "create"
}
```

## Debugging Tips

### If Toast Doesn't Appear
1. Check that toast library is imported: `import { toast } from 'react-toastify'`
2. Verify ToastContainer is in app layout
3. Check browser console for errors
4. Verify API interceptor is being used

### If Audit Log Doesn't Appear
1. Check console.warn is not filtered in browser
2. Verify error.response.data has correct structure
3. Check API interceptor response handler
4. Look for any console filter settings

### If Permission Check Fails
1. Verify PermissionContext is loaded
2. Check permissions array in context
3. Verify user is logged in
4. Check backend /rbac/permissions/me endpoint
5. Verify token is valid

### If 403 Returns 404 Instead
This is correct behavior! Backend returns 404 for cross-org access to prevent enumeration.

## Regression Testing

### After Code Changes
- [ ] Run unit tests: `npm test`
- [ ] Run integration tests: `npm run test:integration`
- [ ] Run E2E tests: `npm run test:e2e`
- [ ] Manual smoke tests on key flows

### Before Deployment
- [ ] All tests passing
- [ ] Manual testing complete
- [ ] CodeQL scan passed
- [ ] Performance testing done
- [ ] Security review complete

## Performance Testing

### Monitor
- [ ] API response times (should be < 100ms overhead)
- [ ] Toast notification performance
- [ ] Console logging impact
- [ ] Memory usage
- [ ] Network requests

### Expected Performance
- API overhead: < 10ms for permission check
- Toast display: < 50ms
- Console logging: < 5ms
- No memory leaks

## Browser Compatibility

Test in:
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)
- [ ] Mobile browsers (iOS Safari, Chrome Mobile)

## Common Issues & Solutions

### Issue: Toast not appearing
**Solution**: Verify ToastContainer is in _app.tsx or layout component

### Issue: Permission check always returns false
**Solution**: Check PermissionContext is loaded and user has valid token

### Issue: Audit log not showing
**Solution**: Check browser console filter settings (allow warn level)

### Issue: Error not propagated to component
**Solution**: Ensure you're using try-catch or .catch() on API calls

### Issue: 403 handler not triggered
**Solution**: Verify backend is returning 403 with correct data structure

## Next Steps After Testing

1. Document any issues found
2. Create test cases for edge cases
3. Update user documentation
4. Train support team on new error messages
5. Monitor production logs for permission denials
6. Set up alerts for excessive 403 errors

---

**Last Updated**: October 29, 2025  
**Version**: 1.0  
**Status**: Ready for Testing
