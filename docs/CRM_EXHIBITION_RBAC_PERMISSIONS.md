# CRM, Exhibition, and Commission RBAC Permissions

This document lists all RBAC permissions required for CRM, Exhibition Mode, and Commission tracking features.

## Commission Tracking Permissions

### Commission Operations
- `crm_commission_read` - View commission records
- `crm_commission_create` - Create new commission records
- `crm_commission_update` - Update existing commission records
- `crm_commission_delete` - Delete commission records

**Notes:**
- Company admins (`is_company_admin=True`) have all permissions by default
- Commission endpoints are organization-scoped (multi-tenant)
- All commission data includes audit fields (created_by, created_at, updated_at)

## CRM Lead Management Permissions

### Lead Operations
- `crm_lead_read` - View lead records
- `crm_lead_create` - Create new leads
- `crm_lead_update` - Update existing leads
- `crm_lead_delete` - Delete leads
- `crm_lead_manage_all` - View all leads in organization (bypasses ownership filter)

**Notes:**
- Regular users without `crm_lead_manage_all` can only see leads they created or are assigned to
- Users with `crm_admin` permission can view all leads
- Company admins can view all leads

## Exhibition Mode Permissions

### Exhibition Event Operations
- `exhibition_event_read` - View exhibition events
- `exhibition_event_create` - Create new exhibition events
- `exhibition_event_update` - Update exhibition events
- `exhibition_event_delete` - Delete exhibition events

### Business Card Scanning Operations
- `exhibition_scan_read` - View business card scans
- `exhibition_scan_create` - Scan business cards (upload images, OCR processing)
- `exhibition_scan_update` - Update/validate scanned card data
- `exhibition_scan_delete` - Delete card scans

### Exhibition Prospect Operations
- `exhibition_prospect_read` - View exhibition prospects
- `exhibition_prospect_create` - Create prospects from scans or manually
- `exhibition_prospect_update` - Update prospect information, qualification status
- `exhibition_prospect_delete` - Delete prospects
- `exhibition_prospect_convert` - Convert prospects to CRM customers

**Notes:**
- All exhibition operations are organization-scoped
- Card scanning includes OCR integration for automatic data extraction
- Prospects can be assigned to sales representatives
- Analytics endpoints require read permissions

## CRM Opportunity Permissions

### Opportunity Operations
- `crm_opportunity_read` - View opportunities
- `crm_opportunity_create` - Create new opportunities
- `crm_opportunity_update` - Update opportunities
- `crm_opportunity_delete` - Delete opportunities

## CRM Analytics Permissions

- `crm_analytics_read` - View CRM analytics and reports
- `crm_customer_analytics_read` - View customer analytics (requires org_admin role by default)

## Implementation Notes

### Permission Enforcement
All endpoints check permissions using the `RBACService`:

```python
rbac = RBACService(db)
user_permissions = await rbac.get_user_service_permissions(current_user.id)
if "required_permission" not in user_permissions and not current_user.is_company_admin:
    raise HTTPException(status_code=403, detail="Insufficient permissions")
```

### Admin Bypass
Company administrators (`is_company_admin=True`) automatically bypass all permission checks.

### Multi-Tenancy
All operations are scoped to the user's organization using `require_current_organization_id()`.

### Audit Logging
All create, update, and delete operations are logged with:
- User email/ID
- Organization ID
- Timestamp
- Action performed

## Permission Assignment

Permissions should be assigned through:
1. Role-based assignments in the RBAC system
2. Direct user permission assignments
3. Organization-level default permissions

## Security Considerations

1. **Least Privilege**: Assign minimum permissions required for user roles
2. **Data Isolation**: Organization-scoping prevents cross-tenant data access
3. **Audit Trail**: All operations are logged for compliance and debugging
4. **Validation**: Input validation prevents injection and malformed data
5. **Rate Limiting**: Consider implementing rate limits for bulk operations

## API Endpoints Summary

### Commission Endpoints
- `GET /api/v1/crm/commissions` - List commissions (filtered by org)
- `GET /api/v1/crm/commissions/{id}` - Get single commission
- `POST /api/v1/crm/commissions` - Create commission
- `PUT /api/v1/crm/commissions/{id}` - Update commission
- `DELETE /api/v1/crm/commissions/{id}` - Delete commission

### Exhibition Endpoints
- `GET /api/v1/exhibition/events` - List exhibition events
- `POST /api/v1/exhibition/events` - Create event
- `GET /api/v1/exhibition/events/{id}` - Get event details
- `PUT /api/v1/exhibition/events/{id}` - Update event
- `DELETE /api/v1/exhibition/events/{id}` - Delete event
- `POST /api/v1/exhibition/events/{id}/scan-card` - Scan business card
- `GET /api/v1/exhibition/card-scans` - List card scans
- `GET /api/v1/exhibition/card-scans/{id}` - Get scan details
- `PUT /api/v1/exhibition/card-scans/{id}` - Update/validate scan
- `GET /api/v1/exhibition/prospects` - List prospects
- `POST /api/v1/exhibition/prospects` - Create prospect
- `GET /api/v1/exhibition/prospects/{id}` - Get prospect details
- `PUT /api/v1/exhibition/prospects/{id}` - Update prospect
- `POST /api/v1/exhibition/prospects/{id}/convert-to-customer` - Convert to customer
- `GET /api/v1/exhibition/analytics` - Exhibition analytics
- `GET /api/v1/exhibition/events/{id}/metrics` - Event metrics
- `POST /api/v1/exhibition/events/{id}/bulk-scan` - Bulk scan cards

### Lead Endpoints
- `GET /api/v1/crm/leads` - List leads (filtered by ownership/permissions)
- `POST /api/v1/crm/leads` - Create lead
- `GET /api/v1/crm/leads/{id}` - Get lead details
- `PUT /api/v1/crm/leads/{id}` - Update lead
- `DELETE /api/v1/crm/leads/{id}` - Delete lead

## Testing Permissions

To test permission enforcement:

1. Create test users with different permission sets
2. Attempt operations with insufficient permissions (should return 403)
3. Verify admin users can perform all operations
4. Test cross-organization access (should be blocked)
5. Verify audit logs are created correctly

## Migration Required

Before deploying, ensure the `commissions` table migration is applied:

```bash
alembic upgrade head
```

The migration file: `migrations/versions/add_commissions_table_20251022.py`
