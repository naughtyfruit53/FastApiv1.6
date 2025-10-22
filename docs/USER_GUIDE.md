# Comprehensive ERP System User Guide

## Table of Contents

1. [Getting Started](#getting-started)
2. [Dashboard Overview](#dashboard-overview)
3. [Master Data Management](#master-data-management)
4. [Inventory Management](#inventory-management)
5. [Voucher Management](#voucher-management)
6. [Manufacturing](#manufacturing)
7. [Finance & Accounting](#finance--accounting)
8. [Sales & Marketing](#sales--marketing)
9. [Service Management](#service-management)
10. [HR Management](#hr-management)
11. [Reports & Analytics](#reports--analytics)
12. [Settings & Configuration](#settings--configuration)
13. [Troubleshooting](#troubleshooting)

---

## Getting Started

### First Time Login

1. **Access the System**: Navigate to your organization's ERP URL
2. **Login**: Enter your username and password
3. **Dashboard**: You'll be directed to your personalized dashboard

### Navigation

- **Mega Menu**: Click the menu button in the top navigation to access all modules
- **Quick Search**: Use the search bar to quickly find features and pages
- **Breadcrumbs**: Track your location within the system
- **User Menu**: Access your profile and settings from the top-right corner

---

## Dashboard Overview

The dashboard provides a quick overview of your organization's key metrics:

- **Sales Overview**: Current month sales, trends, and comparisons
- **Inventory Alerts**: Low stock warnings and reorder notifications
- **Pending Tasks**: Outstanding approvals and actions
- **Quick Actions**: Shortcuts to frequently used features

### Customizing Your Dashboard

1. Navigate to **Settings** > **Dashboard Preferences**
2. Select which widgets to display
3. Arrange widgets by dragging and dropping
4. Save your preferences

---

## Master Data Management

Master data forms the foundation of your ERP system. Maintain accurate master data for smooth operations.

### Managing Vendors

**Create a New Vendor:**
1. Go to **Master Data** > **Vendors**
2. Click **Add Vendor**
3. Fill in required details:
   - Vendor name
   - Contact information
   - GST number (if applicable)
   - Payment terms
4. Click **Save**

**Tips:**
- Always verify GST numbers before saving
- Set default payment terms for faster voucher creation
- Add multiple contacts for better communication

### Managing Customers

**Create a New Customer:**
1. Navigate to **Master Data** > **Customers**
2. Click **Add Customer**
3. Enter customer details:
   - Name and contact information
   - Billing address
   - Shipping address (if different)
   - Credit limit
   - GST details
4. Save the record

**Best Practices:**
- Maintain accurate shipping addresses for smooth delivery
- Set appropriate credit limits
- Regular customer data cleanup

### Managing Products

**Add Products:**
1. Go to **Master Data** > **Products**
2. Click **New Product**
3. Fill in:
   - Product name and description
   - HSN/SAC code
   - Unit of measurement
   - Opening stock
   - Minimum stock level
   - GST rate
4. Save product

**Product Categories:**
- Organize products into categories for easy management
- Use consistent naming conventions
- Set reorder levels to avoid stockouts

### Chart of Accounts

**Understanding CoA:**
- The Chart of Accounts is the backbone of your financial system
- Organized into Assets, Liabilities, Income, Expenses, and Equity

**Creating Accounts:**
1. Navigate to **Master Data** > **Chart of Accounts**
2. Select parent account group
3. Enter account name and code
4. Set account type and nature
5. Save

---

## Inventory Management

### Current Stock View

**Check Stock Levels:**
1. Go to **Inventory** > **Current Stock**
2. View real-time stock levels across all locations
3. Filter by category, warehouse, or product
4. Export to Excel for analysis

### Stock Movements

**Track Inventory Transactions:**
- All stock ins and outs are automatically recorded
- View movement history for any product
- Identify trends and patterns

### Low Stock Alerts

**Set Minimum Levels:**
1. Edit product master data
2. Set minimum stock level
3. System will alert when stock falls below threshold

---

## Voucher Management

### Voucher Types

The system supports multiple voucher types:

#### Purchase Vouchers
- **Purchase Orders**: Create orders for vendors
- **Purchase Invoices**: Record vendor bills
- **Purchase Returns**: Return goods to vendors
- **GRN (Goods Receipt Note)**: Record receipt of goods

#### Sales Vouchers
- **Quotations**: Send quotes to customers
- **Proforma Invoices**: Pro forma billing
- **Sales Orders**: Customer orders
- **Sales Invoices**: Final invoices
- **Delivery Challan**: Goods dispatch documents
- **Sales Returns**: Customer returns

#### Financial Vouchers
- **Payment Vouchers**: Record payments
- **Receipt Vouchers**: Record receipts
- **Journal Vouchers**: Adjustments
- **Contra Vouchers**: Cash/bank transfers

### Creating a Purchase Voucher

**Step-by-Step:**
1. Navigate to **Vouchers** > **Purchase Vouchers**
2. Click **New Purchase Voucher**
3. Select vendor
4. Enter voucher date and due date
5. Add line items:
   - Select product
   - Enter quantity and rate
   - GST is calculated automatically
6. Add any additional charges (freight, insurance, etc.)
7. Review totals
8. **Save** or **Save & Print**

### Creating a Sales Invoice

**Process:**
1. Go to **Vouchers** > **Sales Invoices**
2. Click **New Sales Invoice**
3. Select customer
4. Choose billing and shipping addresses
5. Add products with quantities
6. System calculates:
   - Line totals
   - GST (CGST/SGST for intra-state, IGST for inter-state)
   - Round-off
   - Grand total
7. Review and save
8. Generate PDF or email to customer

### PDF Templates

**Choose Template Style:**
1. Go to **Settings** > **Voucher Settings**
2. Select from three template styles:
   - **Standard**: Professional with clean borders
   - **Modern**: Contemporary gradient design
   - **Classic**: Traditional serif fonts
   - **Minimal**: Clean minimalist layout
3. Click on a template to preview
4. Save your selection

**What's Included:**
- Company logo and details
- Customer/vendor information
- Itemized product list with HSN codes
- Tax calculations
- **Bank details** for payments
- **Terms & conditions** specific to voucher type
- Authorized signature section

### Terms & Conditions

**Configure Terms:**
1. Navigate to **Settings** > **Voucher Settings**
2. Scroll to **Terms & Conditions**
3. Set terms for each voucher type:
   - Purchase orders
   - Sales invoices
   - Quotations
   - Delivery challans
   - GRNs
4. Terms automatically appear on PDFs

---

## Manufacturing

### Production Planning

**Create Production Orders:**
1. Go to **Manufacturing** > **Production Order**
2. Select finished product
3. Enter quantity to produce
4. System shows required raw materials (BOM-based)
5. Schedule production
6. Save order

### Bill of Materials (BOM)

**Manage BOMs:**
1. Navigate to **Master Data** > **Bill of Materials**
2. Create BOM for each finished product
3. Add raw material components with quantities
4. Set wastage percentage if applicable

### Work Orders

Track manufacturing progress with work orders:
- Assign to specific work centers
- Monitor status (Pending, In Progress, Completed)
- Record actual consumption and output

---

## Finance & Accounting

### Accounts Payable

**Monitor Vendor Payables:**
1. Go to **Finance** > **Accounts Payable**
2. View summary cards:
   - Total payable
   - Overdue amounts
   - Due this week
   - Due this month
3. Review vendor bill list
4. Click **Make Payment** to settle bills

**Features:**
- Track all vendor bills in one place
- Identify overdue payments
- Plan cash flow effectively

### Cost Centers

**Manage Cost Centers:**
1. Navigate to **Finance** > **Cost Centers**
2. Click **New Cost Center**
3. **Auto-generate code** or enter manually
4. **Choose from standard names**:
   - Administration
   - Sales & Marketing
   - Production
   - R&D
   - IT
   - HR
   - Finance & Accounting
   - Operations
   - Maintenance
   - Logistics
   - Customer Service
   - Legal & Compliance
5. Set budget amount
6. Save

**Benefits:**
- Department-wise expense tracking
- Budget vs. actual comparisons
- Variance analysis

### Budget Management

**Create and Track Budgets:**
1. Go to **Finance** > **Budget Management**
2. View budget summary:
   - Total budget
   - Allocated amount
   - Total spent
   - Remaining budget
3. Click **Create Budget** to add new
4. Select department and fiscal year
5. Enter budget amount
6. Monitor utilization with progress bars

**Budget Status:**
- **Active**: Within budget
- **Exceeded**: Over budget (requires attention)

### Cost Analysis

**Get Smart Insights:**
1. Navigate to **Finance** > **Cost Analysis**
2. View AI-powered insights:
   - Budget overruns
   - Underutilized budgets
   - Cost center comparisons
   - Spending trends
3. Review recommendations:
   - **High Priority**: Immediate action required
   - **Medium Priority**: Monitor closely
   - **Low Priority**: General information

**Actionable Insights:**
- Identifies inefficiencies automatically
- Suggests budget reallocation opportunities
- Highlights top spending areas
- Recommends cost optimization strategies

---

## Sales & Marketing

### CRM (Customer Relationship Management)

**Manage Customer Interactions:**
- Track leads and opportunities
- Record customer communications
- Schedule follow-ups
- Monitor sales pipeline

### Marketing Campaigns

**Create Campaigns:**
1. Go to **Marketing** > **Campaigns**
2. Define target audience
3. Set campaign goals
4. Track performance metrics

---

## Service Management

### Service Tickets

**Create Service Requests:**
1. Navigate to **Service** > **Service Desk**
2. Click **New Ticket**
3. Enter customer details
4. Describe issue
5. Assign priority
6. Assign to technician
7. Track resolution

### SLA Management

**Service Level Agreements:**
- Define response times
- Set resolution targets
- Monitor SLA compliance
- Get alerts for SLA breaches

### Website Agent

The Website Agent allows you to create and manage customer websites from within the service module.

**Creating a Website Project:**
1. Navigate to **Service** > **Website Agent**
2. Click **Create Website**
3. Follow the wizard steps:
   - **Step 1: Basic Info**
     - Enter project name
     - Select project type (Landing Page, E-Commerce, Corporate, Blog, Portfolio)
     - Optionally link to a customer
   - **Step 2: Design**
     - Choose a theme (Modern, Classic, Minimal, Bold)
     - Set primary and secondary colors
     - Upload logo and favicon
   - **Step 3: Content**
     - Enter site title and description
     - Default pages (Home, About, Contact) are auto-generated
   - **Step 4: Integration**
     - Enable AI Chatbot integration
     - Enable analytics tracking
     - Enable SEO optimization
4. Click **Create Project**

**Managing Projects:**
- View all website projects in the main dashboard
- Click on a project to view details, deployments, and maintenance logs
- Use the menu (⋮) to edit, deploy, or delete projects

**Deploying Websites:**
1. Select a project from the list
2. Click the **Deploy** button
3. The system will create a new deployment
4. View deployment history in the **Deployments** tab

**Managing Pages:**
1. Select a project
2. Navigate to the project details
3. Add, edit, or delete pages as needed
4. Set page order and publish status

**Maintenance Logs:**
- Track all updates and changes to your websites
- View automated maintenance activities
- Monitor security patches and performance optimizations

**Integration with Service Chatbot:**
- When chatbot integration is enabled, your service chatbot is automatically embedded on the website
- Customers can get instant support while browsing
- Conversations can be escalated to human agents as needed

---

## HR Management

### Employee Management

**Manage Employee Records:**
1. Go to **HR** > **Employees**
2. Add new employee
3. Maintain:
   - Personal details
   - Contact information
   - Employment history
   - Documents
   - Payroll details

### Payroll

**Process Payroll:**
1. Navigate to **HR** > **Payroll**
2. Select pay period
3. Review employee salaries
4. Calculate deductions
5. Generate pay slips
6. Process payments

---

## Reports & Analytics

### Financial Reports

**Generate Reports:**
1. Go to **Reports** > **Financial Reports**
2. Select report type:
   - Profit & Loss
   - Balance Sheet
   - Trial Balance
   - Cash Flow Statement
3. Choose date range
4. Click **Generate**
5. Export to PDF or Excel

### Inventory Reports

**Stock Reports:**
- Current stock levels
- Stock movement summary
- Aging analysis
- Reorder reports

### Sales Reports

**Analyze Sales:**
- Sales by customer
- Sales by product
- Sales trends
- Outstanding receivables

---

## Settings & Configuration

### General Settings

**Organization Setup:**
1. Navigate to **Settings** > **General Settings**
2. Update organization details
3. Configure modules
4. Set date formats
5. Save changes

### User Management

**Add/Remove Users:**
1. Go to **Settings** > **User Management**
2. Click **Add User**
3. Enter user details
4. Assign roles and permissions
5. Send invite

**Role-Based Access Control (RBAC):**
- Define custom roles
- Set granular permissions
- Control access to sensitive data

### Voucher Settings

**Configure Voucher System:**
1. Navigate to **Settings** > **Voucher Settings**
2. Set voucher prefix (optional)
3. Choose counter reset period:
   - Never
   - Monthly
   - Quarterly
   - Annually
4. Select PDF template style
5. Configure terms & conditions
6. Save settings

### Tally Integration

**Connect to Tally ERP:**
1. Go to **Settings** > **General Settings**
2. Scroll to **Tally Integration**
3. Enable Tally sync
4. Click **Configure Connection**
5. Enter:
   - Tally server host (e.g., localhost)
   - Port (default: 9000)
   - Company name (exact match from Tally)
6. Click **Test Connection**
7. If successful, click **Save**

**Using Tally Integration:**
- **Sync Now**: Real-time bi-directional sync
- **Import from Tally**: Pull data from Tally to ERP
- **Export to Tally**: Push data from ERP to Tally

**Prerequisites:**
- Tally ERP 9 running on local network
- ODBC server enabled in Tally (F12 → Configure → Enable ODBC Server)
- Network connectivity between systems

---

## Troubleshooting

### Common Issues

#### Cannot Login
**Solution:**
1. Verify username and password
2. Check internet connection
3. Clear browser cache
4. Try incognito/private mode
5. Contact administrator if issue persists

#### PDF Not Generating
**Solution:**
1. Check browser pop-up settings
2. Ensure voucher has all required data
3. Try different browser
4. Contact support

#### Tally Sync Failing
**Solution:**
1. Verify Tally is running
2. Check ODBC server is enabled
3. Confirm company name matches exactly
4. Test connection from configuration dialog
5. Check firewall settings

#### Stock Discrepancy
**Solution:**
1. Review recent stock movements
2. Check for unrecorded transactions
3. Perform physical stock verification
4. Reconcile with system stock
5. Make stock adjustment if needed

#### Website Deployment Failing
**Solution:**
1. Check project status is not "archived"
2. Verify all required fields are filled (site title, theme)
3. Ensure at least one page is published
4. Check deployment provider configuration
5. Review deployment logs in the Deployments tab
6. Try redeploying with a new version
7. Contact support if issue persists

#### Website Not Displaying Correctly
**Solution:**
1. Clear browser cache and reload
2. Check if deployment completed successfully
3. Verify page content is properly formatted
4. Check theme and color settings
5. Test in different browsers
6. Review maintenance logs for recent changes

#### Chatbot Not Showing on Website
**Solution:**
1. Verify chatbot integration is enabled for the project
2. Check chatbot configuration settings
3. Ensure website is deployed after enabling chatbot
4. Clear browser cache
5. Check browser console for JavaScript errors
6. Verify service chatbot is active in Service Desk settings

### Getting Help

**Support Channels:**
1. **In-App Help**: Click Help icon in navigation
2. **User Guide**: This document
3. **Email Support**: support@tritiq.com
4. **Phone Support**: Contact your administrator for support number
5. **Video Tutorials**: Available in Help section

### Best Practices

1. **Regular Backups**: Ensure data is backed up regularly
2. **Data Entry**: Double-check important data before saving
3. **User Training**: Train new users on system basics
4. **Security**: Never share passwords, change them regularly
5. **Updates**: Keep the system updated for latest features
6. **Clean Data**: Regularly review and clean master data
7. **Reconciliation**: Reconcile accounts monthly
8. **Reporting**: Generate and review reports regularly

---

## Keyboard Shortcuts

Improve productivity with keyboard shortcuts:

- `Ctrl + S`: Save current form
- `Ctrl + P`: Print current document
- `Ctrl + F`: Search/Find
- `Esc`: Close dialog/modal
- `Alt + N`: New record (context-dependent)
- `Alt + E`: Edit record
- `/`: Focus search bar

---

## CRM Module

### Overview

The CRM (Customer Relationship Management) module helps you manage leads, opportunities, contacts, accounts, and customer analytics.

### Lead Management

**Creating a Lead:**
1. Navigate to **CRM** > **Leads**
2. Click **Add Lead**
3. Enter lead information:
   - Contact details (name, email, phone)
   - Company information
   - Lead source (website, referral, etc.)
   - Status (new, contacted, qualified, etc.)
4. Assign to a sales representative (optional)
5. Click **Save**

**Lead Ownership:**
- **Regular Users**: See only leads assigned to them or created by them
- **Managers/Admins**: See all leads in the organization with owner names displayed
- Leads are automatically filtered based on your permissions

**Converting Leads:**
1. Open a qualified lead
2. Click **Convert to Opportunity**
3. System creates:
   - Customer record (if new)
   - Opportunity record linked to the lead
4. Lead status updates to "Converted"

### Commission Tracking

**Recording Commissions:**
1. Go to **CRM** > **Commissions**
2. Click **Add Commission**
3. Fill in details:
   - **Person Type**: Internal (employee) or External (partner/agent)
   - **Person Name**: Name of the sales person
   - **Commission Type**: Percentage, fixed amount, tiered, or bonus
   - **Base Amount**: Deal value for calculation
   - **Commission Rate/Amount**: Based on type selected
   - **Payment Status**: Pending, approved, paid, etc.
4. Click **Submit**

**Viewing Commission Reports:**
- Filter by status, date range, or person
- Export to Excel or PDF
- Track payment history

### Customer Analytics

**Accessing Analytics:**
- From **CRM** > **Customer Analytics**
- From **Sales Dashboard** > **Analytics** button
- Direct URL: `/sales/customer-analytics`

**Key Metrics:**
- Total customers and active customers
- New customers in period
- Customer lifetime value (CLV)
- Revenue analytics
- Top customers by revenue
- Retention rate

**Using Analytics:**
1. Select date range (period start and end)
2. View summary cards with key metrics
3. Analyze customer segments
4. Review top customers table
5. Export reports as needed

### Exhibition Mode

**Managing Exhibition Events:**
1. Go to **Exhibition Mode**
2. Click **Create Event**
3. Enter event details:
   - Event name and description
   - Location and venue
   - Start and end dates
   - Status (planned, active, completed)
4. Save the event

**Scanning Business Cards:**
1. Select an active event
2. Click **Scan Card** or switch to **Card Scans** tab
3. Upload business card image
4. System extracts information using AI:
   - Name, company, designation
   - Email, phone
   - Confidence score displayed
5. Validate and save the scan

**Managing Prospects:**
1. Switch to **Prospects** tab
2. View all prospects from the event
3. Qualify prospects:
   - Mark as hot, warm, or cold
   - Convert to leads
   - Schedule follow-ups
4. Track conversion metrics

---

## AI Chatbot

### Overview

The AI Chatbot provides intelligent assistance for navigation, business advice, and task execution.

### Accessing the Chatbot

- Click the **chat icon** in the bottom-right corner
- Type your query or question
- Chatbot responds with helpful information and action buttons

### Features

**Business Advice:**
- Ask: "How can I improve inventory management?"
- Ask: "What's the best way to manage cash flow?"
- Ask: "How do I grow my sales?"
- Receive actionable recommendations and quick links

**Navigation Assistance:**
- Say: "Take me to sales reports"
- Say: "Show me customer list"
- Say: "I want to create an invoice"
- Chatbot provides direct navigation links

**Voucher Creation:**
- Say: "Create a sales invoice"
- Say: "Make a purchase order"
- Chatbot guides you to the correct voucher form

**Analytics Queries:**
- Ask: "Show me sales trends"
- Ask: "Who are my top customers?"
- Access analytics dashboards directly

### Tips for Using the Chatbot

1. **Be specific**: "Show low stock items" works better than "stock"
2. **Use natural language**: Ask questions as you would to a colleague
3. **Follow suggestions**: Chatbot provides related actions
4. **Provide context**: Include relevant details in your queries

### Chatbot Integration (For Developers)

To integrate the chatbot into your customer-facing website:

1. Review the complete integration guide: `/docs/CHATBOT_INTEGRATION.md`
2. Choose integration method:
   - Direct script injection (simplest)
   - NPM package (for React/Vue/Angular)
   - iframe embedding
3. Configure with your API credentials
4. Customize theme and features
5. Deploy to your website

**Quick Start Script:**
```html
<script>
  (function() {
    var config = {
      apiUrl: 'https://your-erp-domain.com/api/v1',
      organizationId: 'YOUR_ORG_ID',
      apiKey: 'YOUR_API_KEY',
      theme: {
        primaryColor: '#1976d2',
        headerText: 'Chat with us'
      }
    };
    // ... rest of integration script
  })();
</script>
```

See full documentation for complete implementation details.

---

## AI Analytics & Business Insights

### Overview

AI Analytics provides intelligent insights, predictions, and recommendations based on your business data.

### Accessing AI Analytics

1. Navigate to **Analytics** > **AI Insights**
2. Select the type of analysis:
   - Sales forecasting
   - Customer segmentation
   - Inventory optimization
   - Cash flow prediction
3. Set parameters and time ranges
4. View AI-generated insights

### Features

**Predictive Analytics:**
- Sales forecasting based on historical data
- Demand prediction for inventory planning
- Customer churn risk analysis
- Revenue projections

**Smart Recommendations:**
- Optimal stock levels
- Pricing suggestions
- Customer targeting
- Resource allocation

**Automated Alerts:**
- Low stock warnings
- Payment due reminders
- Unusual transaction alerts
- Performance anomalies

### Using AI Insights

**Sales Forecasting:**
1. Go to **Analytics** > **Sales Forecast**
2. Select forecast period (monthly, quarterly)
3. Review prediction accuracy score
4. View trend charts and confidence intervals
5. Export forecasts for planning

**Customer Insights:**
1. Navigate to **Analytics** > **Customer Insights**
2. View customer segments:
   - High value customers
   - At-risk customers
   - Growth opportunities
3. Review recommended actions
4. Track segment performance

**Inventory Optimization:**
1. Access **Analytics** > **Inventory AI**
2. Review stock level recommendations
3. Identify slow-moving items
4. Plan reorder quantities
5. Optimize warehouse space

---

## Glossary

**Terms and Definitions:**

### Core ERP Terms
- **BOM**: Bill of Materials - list of raw materials for a finished product
- **CoA**: Chart of Accounts - hierarchical list of all ledger accounts
- **CGST**: Central Goods and Services Tax
- **SGST**: State Goods and Services Tax
- **IGST**: Integrated Goods and Services Tax (for inter-state transactions)
- **GRN**: Goods Receipt Note - document for received goods
- **HSN**: Harmonized System of Nomenclature - product classification code
- **SAC**: Services Accounting Code - service classification code
- **SLA**: Service Level Agreement
- **Voucher**: Accounting transaction document
- **Master Data**: Core business data (customers, vendors, products, etc.)

### CRM Terms
- **Lead**: Potential customer who has shown interest
- **Opportunity**: Qualified sales prospect with defined value
- **Lead Qualification**: Process of determining if a lead is worth pursuing
- **Lead Ownership**: Assignment of leads to specific sales representatives
- **CLV**: Customer Lifetime Value - total revenue expected from a customer
- **Conversion Rate**: Percentage of leads that become customers
- **Commission**: Payment to sales person based on sales performance
- **Prospect**: Potential customer identified at an exhibition or event

### AI & Analytics Terms
- **AI Chatbot**: Artificial intelligence-powered conversational assistant
- **Intent Classification**: AI's understanding of user's purpose
- **Confidence Score**: AI's certainty level in its prediction (0-100%)
- **Predictive Analytics**: Using historical data to forecast future outcomes
- **Customer Segmentation**: Grouping customers by characteristics
- **Churn Rate**: Percentage of customers who stop doing business
- **ARPU**: Average Revenue Per User
- **Retention Rate**: Percentage of customers who continue purchasing

### RBAC Terms
- **RBAC**: Role-Based Access Control - permission system
- **Admin Access**: Full access to all organization data
- **Manager Role**: Can view and manage team's data
- **User Role**: Limited access to owned/assigned items
- **Permission**: Specific action a user can perform
- **Organization Scope**: Data limited to user's organization

---

## Appendix

### Quick Reference Card

**Most Used Features:**
1. Create Sales Invoice: Vouchers → Sales Vouchers → New
2. Check Stock: Inventory → Current Stock
3. Generate Report: Reports → Select Type → Generate
4. Add Customer: Master Data → Customers → Add
5. Make Payment: Vouchers → Payment Vouchers → New

### Sample Workflows

**End-to-End Sales Process:**
1. Receive inquiry from customer
2. Create quotation
3. Convert to sales order (if approved)
4. Generate delivery challan
5. Create sales invoice
6. Record payment received

**End-to-End Purchase Process:**
1. Identify need
2. Create purchase order
3. Send to vendor
4. Receive goods (GRN)
5. Verify bill
6. Create purchase voucher
7. Make payment

---

## Version History

### v1.6.1 - CRM, AI & Chatbot Enhancement Release (Latest)
**Released: October 2024**

**New Features:**
- ✨ Lead ownership & RBAC filtering
- 🤖 AI Chatbot with business advice and navigation
- 💼 Commission tracking with internal/external selector
- 📊 Enhanced customer analytics with CLV and retention metrics
- 🎪 Exhibition Mode with business card scanning
- 💱 Multi-currency support (₹ default)
- 🔒 Role-based data access control
- 📱 Chatbot website integration

**Improvements:**
- Removed all mock data from reports
- Added empty state handling across all modules
- Enhanced currency utility with organization support
- Improved customer and lead management UX
- Updated tax code activation/deactivation

**Bug Fixes:**
- Fixed SalesVoucher.date field usage in analytics
- Corrected lead ownership filtering logic
- Improved modal validation and error handling

### v1.6 - Core Features
- PDF templates, budget management, cost analysis
- Last Updated: September 2024

**Check Latest Updates:** Help → What's New

---

**Need More Help?**

Contact your system administrator or reach out to our support team at support@tritiq.com

*This guide is maintained by the development team and updated regularly. For the latest version, visit the Help section in the application.*
