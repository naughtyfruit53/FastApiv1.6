# Sales CRM Usage Guide

## Overview
The Sales CRM module provides comprehensive customer relationship management capabilities including lead tracking, opportunity management, sales pipeline visualization, and customer analytics.

## Features

### 1. Lead Management (`/sales/leads`)
Track and manage sales leads from initial contact to conversion.

**Key Features:**
- Create, view, edit, and delete leads
- Filter leads by status and source
- Search leads by name, email, or company
- Track lead scoring and estimated value
- Import leads from Excel/CSV files
- Export leads to Excel format

**Import/Export:**
- **Supported Formats:** .xlsx, .xls, .csv
- **Template Download:** Click "Import/Export" > "Download Template" for a sample file
- **Import Process:**
  1. Click "Import/Export" button
  2. Select "Import Leads"
  3. Choose your file (.xlsx, .xls, or .csv)
  4. System validates and imports leads
  5. View imported leads in the table

**Required Fields for Import:**
- `first_name` - Lead's first name
- `last_name` - Lead's last name
- `email` - Contact email (must be valid)
- `phone` - Contact phone number
- `company` - Company name
- `source` - Lead source (e.g., website, referral, campaign)
- `status` - Lead status (new, contacted, qualified, etc.)

### 2. Opportunity Management (`/sales/opportunities`)
Track sales opportunities and their progress through the sales cycle.

**Key Features:**
- View all active opportunities
- Track opportunity value and probability
- Monitor close dates and stages
- Filter by stage and search by name/account
- Calculate total and weighted pipeline value

**Opportunity Stages:**
- Prospecting
- Qualification
- Needs Analysis
- Proposal
- Negotiation
- Closed Won
- Closed Lost

### 3. Sales Pipeline (`/sales/pipeline`)
Visual representation of opportunities organized by stage.

**Key Features:**
- Kanban-style pipeline view
- Drag-and-drop opportunity movement (coming soon)
- Stage-based opportunity grouping
- Real-time pipeline value calculation
- Probability-weighted forecasting

**Pipeline Stages:**
- **Qualification** (10% probability)
- **Needs Analysis** (25% probability)
- **Proposal** (50% probability)
- **Negotiation** (75% probability)
- **Closed Won** (100% probability)
- **Closed Lost** (0% probability)

### 4. Customer Database (`/sales/customers`)
Integrated customer records linked to master data.

**Key Features:**
- View all customers from master database
- Search by name, email, or company
- Filter by status (active/inactive)
- Link to customer analytics
- Track customer creation date

### 5. CRM Dashboard (`/sales/dashboard`)
High-level overview of CRM metrics and KPIs.

**Key Metrics:**
- **Revenue:** Total value of closed won deals (displayed in ₹)
- **Active Opportunities:** Count of open opportunities
- **New Leads:** Count of leads with "new" status
- **Conversion Rate:** Percentage of leads converted to customers

## API Endpoints

### Authentication
All CRM endpoints require authentication via Bearer token in the Authorization header.

```bash
Authorization: Bearer <access_token>
```

The access token is automatically managed by the frontend application.

### Lead Endpoints
```
GET    /api/v1/crm/leads                    - Get all leads
POST   /api/v1/crm/leads                    - Create new lead
GET    /api/v1/crm/leads/{id}               - Get lead by ID
PUT    /api/v1/crm/leads/{id}               - Update lead
DELETE /api/v1/crm/leads/{id}               - Delete lead
POST   /api/v1/crm/leads/{id}/convert       - Convert lead to opportunity
GET    /api/v1/crm/leads/{id}/activities    - Get lead activities
POST   /api/v1/crm/leads/{id}/activities    - Create lead activity
```

### Opportunity Endpoints
```
GET    /api/v1/crm/opportunities             - Get all opportunities
POST   /api/v1/crm/opportunities             - Create new opportunity
GET    /api/v1/crm/opportunities/{id}        - Get opportunity by ID
PUT    /api/v1/crm/opportunities/{id}        - Update opportunity
DELETE /api/v1/crm/opportunities/{id}        - Delete opportunity
```

### Analytics Endpoint
```
GET    /api/v1/crm/analytics                 - Get CRM analytics data
```

## Troubleshooting

### Authentication Issues

**Problem:** Getting 401 Unauthorized errors when accessing CRM pages

**Solution:**
1. Check that you're logged in (refresh the page if needed)
2. Open browser dev tools > Application > Local Storage
3. Verify `access_token` exists and is not expired
4. Check browser console for auth errors with `[API]` prefix
5. Try logging out and logging back in

**Problem:** Infinite redirect loop between login and dashboard

**Solution:**
This should be fixed in v1.6.1. If you still experience this:
1. Clear browser local storage
2. Clear browser cache
3. Log in again

### CRM Data Issues

**Problem:** CRM pages show "Failed to load" errors

**Solution:**
1. Check browser console for specific error messages
2. Verify backend API is running (`/api/v1/crm/` endpoints)
3. Check network tab for failed requests and their response codes
4. Verify organization context is properly set (check `/api/v1/organizations/current`)

**Problem:** Import fails with validation errors

**Solution:**
1. Download the template file for correct format
2. Ensure all required fields are present
3. Check that email addresses are valid
4. Verify date fields use YYYY-MM-DD format
5. Check for special characters that might cause issues

**Problem:** Pipeline shows no data even though opportunities exist

**Solution:**
1. Check that opportunities have a valid `stage` field
2. Verify stage values match pipeline stage IDs:
   - qualification
   - needs_analysis
   - proposal
   - negotiation
   - closed_won
   - closed_lost
3. Check browser console for errors with `[Pipeline]` prefix

### Revenue Symbol Issues

**Problem:** Revenue shows $ instead of ₹

**Solution:**
This is fixed in the dashboard. The ₹ symbol is hardcoded on line 105 of `dashboard.tsx`. If you still see $:
1. Clear browser cache
2. Hard refresh (Ctrl+Shift+R or Cmd+Shift+R)
3. Check that you're on the latest version

## Best Practices

### Lead Management
1. **Consistent Data Entry:** Use standardized values for source and status
2. **Regular Updates:** Update lead status as soon as there's progress
3. **Lead Scoring:** Assign scores based on your qualification criteria
4. **Timely Follow-up:** Set and track expected close dates

### Opportunity Management
1. **Accurate Values:** Enter realistic estimated values
2. **Update Probabilities:** Adjust probability as opportunities progress
3. **Stage Progression:** Move opportunities through stages systematically
4. **Close Date Management:** Keep close dates current and realistic

### Pipeline Management
1. **Regular Review:** Review pipeline weekly for stuck opportunities
2. **Stage Duration:** Monitor how long opportunities stay in each stage
3. **Forecasting:** Use weighted pipeline value for revenue forecasting
4. **Pipeline Hygiene:** Remove or close lost opportunities promptly

### Import/Export
1. **Use Templates:** Always start with the provided template
2. **Data Validation:** Validate data in Excel before importing
3. **Backup First:** Export current data before bulk imports
4. **Test Small:** Test with a few records before bulk import
5. **Error Handling:** Review any import errors and fix source data

## Data Fields Reference

### Lead Fields
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| first_name | String | Yes | Lead's first name |
| last_name | String | Yes | Lead's last name |
| email | Email | Yes | Contact email address |
| phone | String | No | Contact phone number |
| company | String | No | Company name |
| job_title | String | No | Job title |
| source | String | Yes | Lead source (website, referral, etc.) |
| status | String | Yes | Lead status (new, contacted, etc.) |
| score | Number | No | Lead score (0-100) |
| estimated_value | Number | No | Estimated deal value |
| expected_close_date | Date | No | Expected close date (YYYY-MM-DD) |

### Opportunity Fields
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| title | String | Yes | Opportunity title |
| stage | String | Yes | Current stage |
| amount | Number | Yes | Opportunity value |
| probability | Number | Yes | Win probability (0-100) |
| expected_close_date | Date | Yes | Expected close date |
| description | String | No | Opportunity description |

## Support

For additional support:
1. Check browser console logs for detailed error messages
2. Review the API documentation at `/api/v1/docs`
3. Check the main README.md for system-wide troubleshooting
4. Contact your system administrator

## Version History

### v1.6.1 (Current)
- Fixed authentication loop issue
- Standardized token storage
- Fixed pipeline to use real API data
- Fixed opportunities page state management
- Enhanced error handling and logging
- Updated import/export documentation

### v1.6.0
- Initial CRM module release
- Lead management
- Opportunity tracking
- Sales pipeline visualization
- Customer database integration
- CRM analytics dashboard
