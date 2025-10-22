# CRM, Exhibition, and Commission Testing Guide

This document provides a comprehensive testing guide for the CRM, Exhibition Mode, and Commission tracking features.

## Pre-Testing Setup

### 1. Database Migration
```bash
# Apply the commissions table migration
alembic upgrade head

# Verify tables exist
psql -d your_database -c "SELECT tablename FROM pg_tables WHERE tablename IN ('commissions', 'leads', 'opportunities', 'exhibition_events', 'business_card_scans', 'exhibition_prospects');"
```

### 2. Test User Setup
Create test users with different permission levels:
- **Admin User**: `is_company_admin=True`
- **Manager User**: Has `crm_lead_manage_all`, `crm_commission_read` permissions
- **Sales Rep User**: Has `crm_lead_read`, `crm_lead_create` permissions only
- **Exhibition User**: Has exhibition permissions but no CRM permissions

### 3. Test Data Setup
- Create at least 2 organizations for multi-tenancy testing
- Create test leads assigned to different users
- Create test opportunities
- Create test commission records

## Commission Tracking Tests

### Test 1: Create Commission (Percentage Type)
**Endpoint**: `POST /api/v1/crm/commissions`

**Request Body**:
```json
{
  "sales_person_id": 1,
  "sales_person_name": "John Doe",
  "person_type": "internal",
  "commission_type": "percentage",
  "commission_rate": 5.0,
  "base_amount": 10000.0,
  "commission_date": "2025-10-22",
  "payment_status": "pending"
}
```

**Expected**: 
- Status 201
- Commission created with calculated values
- `created_by_id` set to current user

**Validation Tests**:
- Invalid `person_type` (e.g., "contractor") → 400 error
- Invalid `commission_type` → 400 error
- Invalid `payment_status` → 400 error
- `commission_rate` > 100 → 400 error
- Negative `base_amount` → 400 error

### Test 2: Create Commission (Fixed Amount Type)
**Request Body**:
```json
{
  "sales_person_id": 1,
  "sales_person_name": "Jane Smith",
  "person_type": "external",
  "commission_type": "fixed_amount",
  "commission_amount": 500.0,
  "base_amount": 10000.0,
  "commission_date": "2025-10-22",
  "payment_status": "pending"
}
```

**Expected**: Status 201, commission created

### Test 3: List Commissions with Filters
**Endpoint**: `GET /api/v1/crm/commissions?person_type=internal&payment_status=pending`

**Expected**:
- Returns only internal commissions with pending status
- Organization-scoped results only
- Sorted by `commission_date` DESC

### Test 4: Update Commission Payment Status
**Endpoint**: `PUT /api/v1/crm/commissions/{id}`

**Request Body**:
```json
{
  "payment_status": "paid",
  "payment_date": "2025-10-23"
}
```

**Expected**:
- Status 200
- Payment status updated
- `updated_at` timestamp updated

### Test 5: Delete Commission
**Endpoint**: `DELETE /api/v1/crm/commissions/{id}`

**Expected**:
- Status 204
- Commission deleted
- Subsequent GET returns 404

### Test 6: RBAC - Insufficient Permissions
**Test with user lacking `crm_commission_create`**:
- Attempt `POST /api/v1/crm/commissions`
- **Expected**: Status 403, "Insufficient permissions" error

### Test 7: Multi-Tenancy Isolation
- Create commission in Org A
- Switch to user in Org B
- Attempt `GET /api/v1/crm/commissions/{org_a_commission_id}`
- **Expected**: Status 404 (not visible to other orgs)

## Lead Management Tests

### Test 8: Create Lead
**Endpoint**: `POST /api/v1/crm/leads`

**Request Body**:
```json
{
  "first_name": "Alice",
  "last_name": "Johnson",
  "email": "alice@example.com",
  "phone": "+1234567890",
  "company": "Tech Corp",
  "status": "new",
  "source": "website",
  "score": 75,
  "assigned_to_id": 2
}
```

**Expected**:
- Status 201
- Unique `lead_number` generated (format: LD######)
- `created_by_id` set to current user

### Test 9: List Leads - Regular User (Ownership Filter)
**Test with regular user (no admin permissions)**:
- **Endpoint**: `GET /api/v1/crm/leads`
- **Expected**: Only see leads where `assigned_to_id` or `created_by_id` equals current user

### Test 10: List Leads - Admin User
**Test with admin user**:
- **Endpoint**: `GET /api/v1/crm/leads`
- **Expected**: See ALL leads in organization

### Test 11: List Leads - Manager with manage_all Permission
**Test with user having `crm_lead_manage_all`**:
- **Expected**: See ALL leads in organization

### Test 12: Update Lead Status
**Endpoint**: `PUT /api/v1/crm/leads/{id}`

**Request Body**:
```json
{
  "status": "qualified",
  "score": 85,
  "qualification_notes": "High-value prospect, interested in enterprise plan"
}
```

**Expected**:
- Status 200
- Fields updated
- `updated_at` timestamp updated

### Test 13: Search Leads
**Endpoint**: `GET /api/v1/crm/leads?search=alice`

**Expected**: Returns leads matching "alice" in first_name, last_name, email, or company

### Test 14: Filter Leads by Status and Source
**Endpoint**: `GET /api/v1/crm/leads?status=qualified&source=website`

**Expected**: Returns only qualified leads from website source

## Exhibition Mode Tests

### Test 15: Create Exhibition Event
**Endpoint**: `POST /api/v1/exhibition/events`

**Request Body**:
```json
{
  "name": "Tech Conference 2025",
  "description": "Annual technology conference",
  "location": "San Francisco, CA",
  "venue": "Convention Center Hall A",
  "start_date": "2025-11-01T09:00:00Z",
  "end_date": "2025-11-03T18:00:00Z",
  "status": "planned",
  "auto_send_intro_email": true
}
```

**Expected**:
- Status 201
- Event created with unique ID
- `created_by_id` set to current user

### Test 16: Upload Business Card (Scan)
**Endpoint**: `POST /api/v1/exhibition/events/{event_id}/scan-card`

**Request**: 
- Multipart form data with image file
- Supported formats: JPEG, PNG

**Expected**:
- Status 200
- Scan record created
- OCR processing initiated
- If confidence > 0.7, prospect auto-created

### Test 17: List Business Card Scans
**Endpoint**: `GET /api/v1/exhibition/card-scans?event_id={event_id}&processing_status=processed`

**Expected**:
- Returns scans for specified event
- Filtered by processing status
- Sorted by `created_at` DESC

### Test 18: Validate/Update Card Scan
**Endpoint**: `PUT /api/v1/exhibition/card-scans/{scan_id}`

**Request Body**:
```json
{
  "full_name": "Bob Williams",
  "company_name": "Acme Corp",
  "email": "bob@acme.com",
  "validation_status": "validated"
}
```

**Expected**:
- Status 200
- Scan data corrected
- `validated_by_id` set to current user

### Test 19: Create Prospect Manually
**Endpoint**: `POST /api/v1/exhibition/prospects`

**Request Body**:
```json
{
  "exhibition_event_id": 1,
  "full_name": "Carol Davis",
  "company_name": "Global Industries",
  "email": "carol@globalind.com",
  "phone": "+1987654321",
  "interest_level": "high",
  "notes": "Interested in enterprise solutions"
}
```

**Expected**:
- Status 201
- Prospect created
- Default values set (status="new", lead_score=0.0)

### Test 20: List Prospects with Filters
**Endpoint**: `GET /api/v1/exhibition/prospects?event_id={event_id}&status=qualified&assigned_to_id={user_id}`

**Expected**: Returns filtered prospects

### Test 21: Update Prospect Qualification
**Endpoint**: `PUT /api/v1/exhibition/prospects/{prospect_id}`

**Request Body**:
```json
{
  "qualification_status": "hot",
  "lead_score": 90.0,
  "status": "qualified",
  "assigned_to_id": 3,
  "follow_up_date": "2025-10-25T10:00:00Z"
}
```

**Expected**: Status 200, prospect updated

### Test 22: Convert Prospect to Customer
**Endpoint**: `POST /api/v1/exhibition/prospects/{prospect_id}/convert-to-customer`

**Expected**:
- Status 200
- Customer created in CRM
- Prospect's `crm_customer_id` updated
- `conversion_status` set to "customer"

### Test 23: Bulk Card Scan
**Endpoint**: `POST /api/v1/exhibition/events/{event_id}/bulk-scan`

**Request**: 
- Multipart form data with multiple image files

**Expected**:
- Status 200
- Response includes:
  - `successful_scans` count
  - `failed_scans` count
  - `created_prospects` count
  - `errors` array with failure details

### Test 24: Exhibition Analytics
**Endpoint**: `GET /api/v1/exhibition/analytics`

**Expected**:
- Status 200
- Returns aggregated analytics:
  - Total events, scans, prospects
  - Conversion rates
  - Top companies
  - Lead quality distribution

### Test 25: Event Metrics
**Endpoint**: `GET /api/v1/exhibition/events/{event_id}/metrics`

**Expected**:
- Status 200
- Event-specific metrics:
  - Total scans, validated scans
  - Prospects created, emails sent
  - Qualified leads, converted customers

## RBAC Permission Tests

### Test 26: Commission Permissions
Test each permission independently:
- `crm_commission_read` - Can list and view
- `crm_commission_create` - Can create
- `crm_commission_update` - Can update
- `crm_commission_delete` - Can delete

### Test 27: Lead Permissions
- `crm_lead_read` - Can view own leads
- `crm_lead_manage_all` - Can view all leads
- Without `crm_lead_manage_all` - See only owned/assigned leads

### Test 28: Exhibition Permissions
- `exhibition_event_create` - Can create events
- `exhibition_scan_create` - Can scan cards
- `exhibition_prospect_create` - Can create prospects
- `exhibition_prospect_convert` - Can convert to customer

## Edge Cases and Error Handling

### Test 29: Empty States
- List commissions when none exist → Empty array, 200
- List leads when none exist → Empty array, 200
- List prospects when none exist → Empty array, 200

### Test 30: Invalid IDs
- GET with non-existent ID → 404
- UPDATE with non-existent ID → 404
- DELETE with non-existent ID → 404

### Test 31: Validation Errors
- Missing required fields → 422
- Invalid enum values → 422
- Out-of-range values → 422

### Test 32: File Upload Errors
- Upload non-image file → 400
- Upload file > max size → 413
- Missing file in scan request → 422

### Test 33: Database Constraints
- Duplicate lead_number → Should be prevented (unique generation)
- Invalid foreign keys → 400 or 404

### Test 34: Concurrent Updates
- Two users update same commission simultaneously
- Verify last write wins or optimistic locking

## Performance Tests

### Test 35: Large Dataset Performance
- Create 1000+ leads
- List leads with pagination → Response time < 500ms
- Filter/search operations → Response time < 1s

### Test 36: Bulk Operations
- Bulk scan 50 cards → All processed or partial success with errors

## Integration Tests

### Test 37: Lead to Opportunity Conversion
- Create lead → Qualify → Convert to opportunity
- Verify all data transferred correctly

### Test 38: Prospect to Customer Flow
- Scan card → Validate → Create prospect → Convert to customer
- Verify CRM integration

### Test 39: Commission Calculation
- Close opportunity → Create commission
- Verify calculations based on commission type

## Frontend Integration Tests

### Test 40: Commission UI
- Open commission page → Empty state shown if no data
- Create commission via modal → Appears in list
- Update payment status → UI updates
- Filter by status → List updates

### Test 41: Exhibition Mode UI
- Open exhibition mode → Empty state for events
- Create event → Event appears in list
- Scan card → Scan appears in event
- View prospects → Filtered by event

### Test 42: Lead Management UI
- Open leads page → Ownership filtering applied
- Admin sees all leads → Regular user sees limited
- Search functionality → Results filtered
- Update lead → Changes reflected

## Security Tests

### Test 43: Cross-Organization Access
- User from Org A tries to access Org B's data
- **Expected**: 404 or 403 (depending on endpoint)

### Test 44: SQL Injection
- Try SQL injection in search parameters
- **Expected**: No SQL errors, parameters properly escaped

### Test 45: XSS Prevention
- Submit data with HTML/JavaScript
- **Expected**: Data escaped in responses

## Logging and Audit Tests

### Test 46: Audit Trail
- Verify all operations logged:
  - User email/ID
  - Organization ID
  - Timestamp
  - Action performed

### Test 47: Error Logging
- Trigger various errors
- Verify errors logged with context

## Test Execution Checklist

### Before Testing
- [ ] Database migration applied
- [ ] Test users created
- [ ] Test organizations created
- [ ] Backend server running
- [ ] Frontend build deployed (if testing UI)

### During Testing
- [ ] Document all bugs found
- [ ] Note performance issues
- [ ] Verify all RBAC scenarios
- [ ] Test edge cases thoroughly
- [ ] Verify multi-tenancy isolation

### After Testing
- [ ] All critical bugs fixed
- [ ] Performance acceptable
- [ ] Security verified
- [ ] Documentation updated
- [ ] Sign-off obtained

## Test Data Cleanup

After testing, clean up test data:
```sql
DELETE FROM commissions WHERE organization_id IN (test_org_ids);
DELETE FROM exhibition_prospects WHERE organization_id IN (test_org_ids);
DELETE FROM business_card_scans WHERE organization_id IN (test_org_ids);
DELETE FROM exhibition_events WHERE organization_id IN (test_org_ids);
DELETE FROM leads WHERE organization_id IN (test_org_ids);
```

## Automated Testing

Consider creating automated tests using:
- **Backend**: pytest with FastAPI TestClient
- **Frontend**: Jest/Vitest for unit tests, Playwright for E2E
- **API**: Postman/Newman for API testing
- **Load**: Apache JMeter or Locust for load testing

## Success Criteria

Testing is complete when:
- [x] All API endpoints return expected responses
- [x] RBAC permissions enforced correctly
- [x] Multi-tenancy isolation verified
- [x] Validation catches all invalid inputs
- [x] Error handling provides useful messages
- [x] Performance meets requirements
- [x] Frontend-backend integration works
- [x] Empty states display correctly
- [x] Audit logging functional
- [x] Security vulnerabilities addressed
