# API v1 Migration Guide

## Overview

All API routes have been moved from `app/api/` to `app/api/v1/` to implement proper API versioning. This change affects all API endpoints and requires updating client code to use the new paths.

## Changes Made

### File Relocations

The following files were moved from `app/api/` to `app/api/v1/`:

1. `companies.py` → `app/api/v1/companies.py`
2. `customer_analytics.py` → `app/api/v1/customer_analytics.py`
3. `management_reports.py` → `app/api/v1/management_reports.py`
4. `notifications.py` → `app/api/v1/notifications.py`
5. `pincode.py` → `app/api/v1/pincode.py`
6. `platform.py` → `app/api/v1/platform.py`
7. `settings.py` → `app/api/v1/settings.py`

### New Files

1. `org_user_management.py` - New organization user management API for 4-role system

### Files Already in v1

These files were already in the correct location:
- `auth.py`
- `password.py`
- `health.py`
- `user.py`
- `rbac.py`
- `debug.py`
- `organizations/`
- `vendors.py`
- `customers.py`
- `inventory.py`
- `stock.py`
- All voucher-related files
- All other module-specific files

## URL Mapping

### Before (Old URLs)

```
/api/companies/
/api/vendors/
/api/customers/
/api/pincode/lookup
/api/settings/
/api/notifications/
```

### After (New URLs)

```
/api/v1/companies/
/api/v1/vendors/
/api/v1/customers/
/api/v1/pincode/lookup
/api/v1/settings/
/api/v1/notifications/
/api/v1/customer-analytics/
/api/v1/management-reports/
/api/v1/platform/
```

## Frontend Migration

### Update API Base URL

**Before:**
```javascript
const API_BASE_URL = 'https://api.example.com/api';
```

**After:**
```javascript
const API_BASE_URL = 'https://api.example.com/api/v1';
```

### Update Individual Endpoints

**Before:**
```javascript
fetch('/api/companies/', {
  method: 'GET',
  headers: {...}
})
```

**After:**
```javascript
fetch('/api/v1/companies/', {
  method: 'GET',
  headers: {...}
})
```

### Update Axios Base URL

**Before:**
```javascript
const api = axios.create({
  baseURL: '/api'
});
```

**After:**
```javascript
const api = axios.create({
  baseURL: '/api/v1'
});
```

## Backend Changes

### main.py Updates

Import statements updated from:
```python
from app.api.companies import router as companies_router
from app.api.vendors import router as vendors_router
```

To:
```python
from app.api.v1.companies import router as companies_router
from app.api.v1.vendors import router as vendors_router
```

### v1/__init__.py Updates

Added new router registrations:
```python
# Customer Analytics API
from .customer_analytics import router as customer_analytics_router
api_v1_router.include_router(customer_analytics_router, prefix="/customer-analytics", tags=["Customer Analytics"])

# Management Reports API
from .management_reports import router as management_reports_router
api_v1_router.include_router(management_reports_router, prefix="/management-reports", tags=["Management Reports"])

# Notifications API
from .notifications import router as notifications_router
api_v1_router.include_router(notifications_router, prefix="/notifications", tags=["Notifications"])

# Platform API
from .platform import router as platform_router
api_v1_router.include_router(platform_router, prefix="/platform", tags=["Platform"])

# Settings API
from .settings import router as settings_router
api_v1_router.include_router(settings_router, prefix="/settings", tags=["Settings"])

# Organization User Management API (NEW)
from .org_user_management import router as org_user_mgmt_router
api_v1_router.include_router(org_user_mgmt_router, prefix="/org", tags=["Organization User Management"])
```

Changed pincode import from parent to local:
```python
# Before
from ..pincode import router as pincode_router

# After
from .pincode import router as pincode_router
```

## Testing the Migration

### Check Available Routes

Access the routes endpoint to verify all routes are properly registered:
```
GET /routes
```

### Test Each Endpoint

1. Test old URLs to ensure they fail with 404 (no backward compatibility maintained)
2. Test new v1 URLs to ensure they work correctly

### Example Test Script

```bash
#!/bin/bash

BASE_URL="http://localhost:8000"

# Test new v1 endpoints
echo "Testing /api/v1/health"
curl -X GET "$BASE_URL/api/v1/health"

echo "Testing /api/v1/companies"
curl -X GET "$BASE_URL/api/v1/companies" -H "Authorization: Bearer $TOKEN"

echo "Testing /api/v1/settings/menu-visibility"
curl -X GET "$BASE_URL/api/v1/settings/menu-visibility" -H "Authorization: Bearer $TOKEN"
```

## Backward Compatibility

**Important**: No backward compatibility is maintained. Old URLs will return 404 errors.

All clients must update to use the new `/api/v1/` prefix.

## New Endpoints

### Organization User Management

```
POST   /api/v1/org/users                    - Create new org user
GET    /api/v1/org/available-modules/{role} - Get available modules for role
GET    /api/v1/org/users/{id}/permissions   - Get user permissions
PUT    /api/v1/org/users/{id}/modules       - Update manager modules
PUT    /api/v1/org/users/{id}/submodules    - Update executive submodules
GET    /api/v1/org/managers                 - Get all managers
```

### Settings Menu

```
GET    /api/v1/settings/menu-visibility     - Get settings menu visibility
```

## OpenAPI Documentation

Updated OpenAPI URL:
```
/api/v1/openapi.json
```

Swagger UI remains at:
```
/docs
```

## Environment Variables

No environment variable changes required for API versioning.

## Deployment Checklist

- [ ] Update frontend API base URL configuration
- [ ] Update all API calls to use `/api/v1/` prefix
- [ ] Run database migrations (for role system changes)
- [ ] Test all API endpoints
- [ ] Update API documentation
- [ ] Update mobile app API URLs
- [ ] Update third-party integrations
- [ ] Monitor logs for 404 errors on old URLs
- [ ] Update load balancer/reverse proxy rules if needed

## Rollback Plan

If rollback is needed:

1. Revert the following commits:
   - Part 1: Role system and API v1 migration
   - Part 2: Org user management and permission enforcement

2. Restart the application

3. Frontend will continue working with old API URLs

## Support

For questions or issues with the migration:
- Check the logs for specific errors
- Verify all imports are correct
- Ensure database migrations have run
- Test with Postman/curl before integrating with frontend

## Benefits of v1 Structure

1. **Clear Versioning**: Easy to add v2 APIs alongside v1
2. **Better Organization**: All v1 APIs in one directory
3. **Future-Proof**: Can deprecate v1 while maintaining v2
4. **API Gateway Ready**: Standard structure for API management
5. **Consistent URLs**: All endpoints follow same pattern

## Next Steps

1. Test all migrated endpoints thoroughly
2. Update integration tests
3. Deploy to staging environment
4. Perform end-to-end testing
5. Update client applications
6. Deploy to production
7. Monitor for any issues
