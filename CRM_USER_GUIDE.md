# CRM Module - User Guide

## Overview

The CRM (Customer Relationship Management) module helps you manage leads, opportunities, contacts, and accounts to drive sales and maintain customer relationships.

## Features

### 1. Dashboard
- **Analytics Overview**: View key metrics including leads, opportunities, pipeline value, and conversion rates
- **Date Range Selection**: Last 30 days by default, customizable
- **Quick Actions**: Add new leads or opportunities directly from the dashboard

### 2. Lead Management (`/api/v1/crm/leads`)

**What is a Lead?**
A lead is a potential customer who has shown interest in your products or services.

**Features:**
- Create, read, update, and delete leads
- Track lead status (new, contacted, qualified, converted, lost, nurturing)
- Assign leads to team members
- Track lead source (website, referral, social media, etc.)
- Convert leads to customers and opportunities

**API Endpoints:**
- `GET /api/v1/crm/leads` - List all leads with filters
- `POST /api/v1/crm/leads` - Create a new lead
- `GET /api/v1/crm/leads/{id}` - Get lead details
- `PUT /api/v1/crm/leads/{id}` - Update a lead
- `DELETE /api/v1/crm/leads/{id}` - Delete a lead
- `POST /api/v1/crm/leads/{id}/convert` - Convert lead to customer/opportunity

### 3. Opportunity Management (`/api/v1/crm/opportunities`)

**What is an Opportunity?**
An opportunity is a qualified lead with a defined sales potential and expected close date.

**Features:**
- Track opportunities through sales pipeline stages
- Manage expected revenue and probability
- Link opportunities to customers and leads
- Track opportunity stage (prospecting, qualification, proposal, negotiation, closed won/lost)

**API Endpoints:**
- `GET /api/v1/crm/opportunities` - List all opportunities
- `POST /api/v1/crm/opportunities` - Create a new opportunity
- `GET /api/v1/crm/opportunities/{id}` - Get opportunity details
- `PUT /api/v1/crm/opportunities/{id}` - Update an opportunity
- `DELETE /api/v1/crm/opportunities/{id}` - Delete an opportunity

### 4. Contact Management (`/api/v1/contacts`)

**What is a Contact?**
A contact is an individual person associated with your business, such as a customer representative or lead.

**Features:**
- Store detailed contact information (name, email, phone, job title, department)
- Track contact status (active, inactive, lead)
- Link contacts to companies/accounts
- Record contact source and notes
- Manage address and communication details

**API Endpoints:**
- `GET /api/v1/contacts` - List all contacts
- `POST /api/v1/contacts` - Create a new contact
- `GET /api/v1/contacts/{id}` - Get contact details
- `PUT /api/v1/contacts/{id}` - Update a contact
- `DELETE /api/v1/contacts/{id}` - Delete a contact

**Creating a Contact:**
1. Navigate to Sales > Contacts
2. Click "Add Contact" button
3. Fill in the required fields:
   - First Name* (required)
   - Last Name* (required)
   - Email
   - Phone/Mobile
   - Job Title
   - Company
   - Address details
4. Select source and status
5. Add notes if needed
6. Click "Add Contact"

### 5. Account Management (`/api/v1/accounts`)

**What is an Account?**
An account is a company or organization that you do business with or want to do business with.

**Features:**
- Store company information (name, industry, size, revenue)
- Track account type (customer, prospect, partner, vendor)
- Manage primary contacts and contact information
- Record website, address, and description
- Track account status

**API Endpoints:**
- `GET /api/v1/accounts` - List all accounts
- `POST /api/v1/accounts` - Create a new account
- `GET /api/v1/accounts/{id}` - Get account details
- `PUT /api/v1/accounts/{id}` - Update an account
- `DELETE /api/v1/accounts/{id}` - Delete an account

**Creating an Account:**
1. Navigate to Sales > Accounts
2. Click "Add Account" button
3. Fill in the required fields:
   - Account Name* (required)
   - Account Type (customer, prospect, partner, vendor)
   - Industry
   - Company Size
   - Annual Revenue
   - Number of Employees
   - Contact Person
   - Email, Phone, Website
   - Address details
4. Add description if needed
5. Click "Add Account"

### 6. Analytics

**CRM Analytics (`/api/v1/crm/analytics`)**
- Total leads and opportunities
- Leads by status and source
- Opportunities by stage
- Pipeline value (total and weighted)
- Conversion rate
- Average deal size
- Sales cycle days
- Win rate

**Customer Analytics (`/api/v1/crm/customer-analytics`)**
- Total, active, new, and churned customers
- Total revenue and average lifetime value
- Customer retention rate
- ARPU (Average Revenue Per User)
- Top customers by revenue
- Customers by segment

## Permissions

The CRM module uses role-based access control (RBAC). Required permissions:

- `crm_lead_read` - View leads
- `crm_lead_create` - Create leads
- `crm_lead_update` - Update leads
- `crm_lead_delete` - Delete leads
- `crm_lead_convert` - Convert leads to customers/opportunities
- `crm_opportunity_read` - View opportunities
- `crm_opportunity_create` - Create opportunities
- `crm_opportunity_update` - Update opportunities
- `crm_opportunity_delete` - Delete opportunities
- `crm_analytics_read` - View CRM analytics
- `crm_customer_analytics_read` - View customer analytics

Contact your administrator if you need these permissions.

## Best Practices

1. **Lead Qualification**: Regularly review and qualify leads to maintain data quality
2. **Follow-up Activities**: Record all interactions with leads and opportunities
3. **Status Updates**: Keep lead and opportunity statuses up to date
4. **Data Completeness**: Fill in as much information as possible for better insights
5. **Source Tracking**: Always record the source of leads for marketing analysis
6. **Regular Reviews**: Review analytics regularly to identify trends and opportunities

## Troubleshooting

**Issue: Cannot see leads/opportunities**
- Check that you have the required read permissions
- Verify that you are filtering with the correct criteria
- Non-admin users only see leads assigned to them or created by them

**Issue: Analytics not loading**
- Ensure you have `crm_analytics_read` or org_admin role
- Check that the date range is valid
- Verify backend API is running

**Issue: Cannot create contacts/accounts**
- Verify you have access token (logged in)
- Check that all required fields are filled
- Ensure backend API `/api/v1/contacts` and `/api/v1/accounts` are registered

## Support

For additional help or feature requests, contact your system administrator or refer to the [API Documentation](/docs).
