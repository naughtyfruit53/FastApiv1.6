# Exhibition Mode - User Guide

## Overview

Exhibition Mode helps you capture and manage leads at trade shows, exhibitions, and events. The module allows you to scan business cards, create prospects, and convert them to leads or customers.

## Features

### 1. Event Management (`/api/v1/exhibition/events`)

**Create and Manage Exhibition Events:**
- Track upcoming, ongoing, and completed events
- Store event details (name, location, dates, description)
- Link prospects and scans to specific events
- Monitor event ROI and success metrics

**API Endpoints:**
- `GET /api/v1/exhibition/events` - List all events
- `POST /api/v1/exhibition/events` - Create a new event
- `GET /api/v1/exhibition/events/{id}` - Get event details
- `PUT /api/v1/exhibition/events/{id}` - Update an event
- `DELETE /api/v1/exhibition/events/{id}` - Delete an event

**Creating an Event:**
1. Navigate to Exhibition Mode
2. Click "Create Event"
3. Fill in event details:
   - Event Name
   - Location
   - Start and End Dates
   - Description
   - Status (upcoming, ongoing, completed)
4. Click "Create Event"

### 2. Business Card Scanning (`/api/v1/exhibition/events/{id}/scan-card`)

**Scan Business Cards:**
- Upload business card images
- Automatic OCR extraction of contact information
- Manual validation and correction
- Bulk scanning support

**How to Scan a Business Card:**
1. Select an active event
2. Click "Scan Card" or use camera/upload
3. Upload the business card image
4. Review extracted information:
   - Full Name
   - Company Name
   - Job Title/Designation
   - Email
   - Phone/Mobile
   - Website
   - Address
5. Validate and correct any errors
6. Save the scan

**API Endpoints:**
- `POST /api/v1/exhibition/events/{id}/scan-card` - Scan a business card
- `GET /api/v1/exhibition/card-scans` - List all scans
- `GET /api/v1/exhibition/card-scans/{id}` - Get scan details
- `PUT /api/v1/exhibition/card-scans/{id}` - Update/validate a scan
- `POST /api/v1/exhibition/events/{id}/bulk-scan` - Bulk scan multiple cards

**Validation Status:**
- `pending` - Awaiting validation
- `validated` - Information verified and correct
- `corrected` - Information was corrected manually
- `invalid` - Scan rejected or incomplete

### 3. Prospect Management (`/api/v1/exhibition/prospects`)

**Manage Exhibition Prospects:**
- Create prospects from scanned cards or manually
- Track prospect qualification status
- Assign prospects to sales team
- Convert prospects to CRM leads or customers

**API Endpoints:**
- `GET /api/v1/exhibition/prospects` - List all prospects
- `POST /api/v1/exhibition/prospects` - Create a new prospect
- `GET /api/v1/exhibition/prospects/{id}` - Get prospect details
- `PUT /api/v1/exhibition/prospects/{id}` - Update a prospect
- `POST /api/v1/exhibition/prospects/{id}/convert-to-customer` - Convert to customer

**Prospect Workflow:**
1. **Create from Scan**: Business card scans automatically create prospects
2. **Qualify**: Review and qualify prospects (hot, warm, cold, not interested)
3. **Assign**: Assign qualified prospects to sales team members
4. **Follow-up**: Track follow-up actions and notes
5. **Convert**: Convert qualified prospects to CRM leads or customers

**Qualification Status:**
- `hot` - Immediate interest, high priority
- `warm` - Interested but not urgent
- `cold` - Minimal interest
- `not_interested` - No interest

### 4. Analytics and Reporting

**Exhibition Analytics (`/api/v1/exhibition/analytics`)**
- Total events organized
- Total cards scanned
- Total prospects created
- Conversion rates
- Top performing events
- ROI metrics

**Event Metrics (`/api/v1/exhibition/events/{id}/metrics`)**
- Cards scanned at event
- Prospects generated
- Conversion rate
- Follow-up completion rate
- Revenue attributed to event

### 5. Bulk Operations

**Bulk Card Scanning:**
```bash
POST /api/v1/exhibition/events/{id}/bulk-scan
```

Upload multiple business card images at once. The system will:
- Process all cards in parallel
- Extract information using OCR
- Create prospects automatically
- Return summary of successful/failed scans

**Export Event Data:**
```bash
GET /api/v1/exhibition/events/{id}/export?format=csv
```

Export all prospects, scans, and event data in CSV, Excel, or JSON format.

## Permissions

Required permissions for Exhibition Mode:

- `exhibition_event_create` - Create events
- `exhibition_event_read` - View events
- `exhibition_scan_create` - Scan business cards
- `exhibition_prospect_create` - Create prospects
- `exhibition_prospect_read` - View prospects

Contact your administrator if you need these permissions.

## Best Practices

1. **Pre-Event Setup**:
   - Create event in system before the exhibition
   - Brief team on how to use the scanning feature
   - Test scanning functionality beforehand

2. **During Event**:
   - Scan cards immediately after receiving them
   - Add quick notes about conversation context
   - Qualify prospects on-site when possible

3. **Post-Event**:
   - Validate all scans within 24 hours
   - Assign prospects to appropriate sales reps
   - Send follow-up emails within 48 hours
   - Convert hot leads to CRM immediately

4. **Data Quality**:
   - Always validate OCR-extracted information
   - Correct any errors or missing fields
   - Add context notes for better follow-up

5. **Follow-up**:
   - Prioritize hot prospects
   - Schedule follow-ups within one week
   - Track all communication in the system

## Mobile Usage

Exhibition Mode is optimized for mobile devices:

1. **Camera Integration**: Use device camera to scan cards directly
2. **Offline Support**: Cards can be scanned offline and synced later
3. **Touch-Optimized**: Easy to use on tablets and phones
4. **Quick Actions**: Fast qualification and note-taking

## Troubleshooting

**Issue: OCR not extracting information correctly**
- Ensure good lighting when taking photos
- Keep business card flat and in focus
- Use manual validation and correction
- Report consistent OCR issues to administrator

**Issue: Cannot create prospects**
- Verify you have `exhibition_prospect_create` permission
- Check that event is active
- Ensure all required fields are filled

**Issue: Cannot scan business cards**
- Verify you have `exhibition_scan_create` permission
- Check that image file is valid (JPEG, PNG)
- Ensure file size is under 5MB
- Try re-uploading the image

**Issue: Analytics not loading**
- Verify you have org_admin role or analytics permissions
- Check that events exist in the system
- Ensure backend API is running

## Integration with CRM

Exhibition prospects can be seamlessly converted to CRM:

1. **Convert to Lead**: Creates a new CRM lead with all prospect information
2. **Convert to Customer**: Directly creates a customer account
3. **Link to Existing**: Associate with existing customer/account
4. **Transfer Data**: All notes, activities, and qualifications carry over

## Support

For additional help or feature requests, contact your system administrator or refer to the [API Documentation](/docs).
