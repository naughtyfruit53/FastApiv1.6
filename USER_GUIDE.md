# TritIQ Business Suite - User Guide

Complete guide for using TritIQ Business Suite, including all new features from recent releases.

## Table of Contents

1. [Quick Start](#quick-start)
2. [New Features Overview](#new-features-overview)
3. [Currency Utility Usage](#currency-utility-usage)
4. [Voucher System](#voucher-system)
5. [Demo Mode & OTP User Flow](#demo-mode--otp-user-flow)
6. [HR Module (Phase 1)](#hr-module-phase-1)
7. [AI Chatbot](#ai-chatbot)
8. [Exhibition Module](#exhibition-module)
9. [Role-Based Dashboards](#role-based-dashboards)
10. [Mobile Experience](#mobile-experience)
11. [GRN PDF Generation](#grn-pdf-generation)
12. [Database Reset Workflow](#database-reset-workflow)
13. [Migration Guide](#migration-guide)
14. [Seeding Baseline Data](#seeding-baseline-data)
15. [User Onboarding](#user-onboarding)
16. [Troubleshooting](#troubleshooting)
17. [Advanced Operations](#advanced-operations)

---

## Quick Start

### Prerequisites

```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Set up environment variables
cp .env.example .env
# Edit .env with your database credentials

# 3. Ensure PostgreSQL/Supabase is running
```

### First Time Setup

```bash
# 1. Run database migrations
alembic upgrade head

# 2. Start the application (auto-seeding will run on first boot)
uvicorn app.main:app --reload

# That's it! The system will automatically seed baseline data.
```

### Default Credentials

After first boot, you can login with:
- **Email**: `naughtyfruit53@gmail.com`
- **Password**: `123456`
- **⚠️ IMPORTANT**: Change this password immediately after first login!

---

## New Features Overview

This section covers all new features from the last 7-8 PRs:

| Feature | Description | Status |
|---------|-------------|--------|
| Currency Utilities | Multi-currency formatting with locale support | ✅ Active |
| Voucher Fields | Vendor/Customer voucher numbers, backdated numbering | ✅ Active |
| Demo OTP Sessions | 30-minute ephemeral demo sessions with OTP | ✅ Active |
| HR Module Phase 1 | Departments, positions, shifts, holidays, attendance | ✅ Active |
| AI Chatbot Streaming | Real-time AI chat with SSE streaming | ✅ Active |
| Exhibition Module | CRM exhibitions and commissions | ✅ Active |
| GRN PDF Improvements | Enhanced GRN with vendor invoice, batch dates, SKU | ✅ Active |
| Mobile Parity | Full mobile support for all modules | ✅ Active |

---

## Currency Utility Usage

The application provides comprehensive currency formatting utilities supporting multiple currencies and locales.

### Supported Currencies

| Currency | Symbol | Locale | Decimals |
|----------|--------|--------|----------|
| INR | ₹ | en-IN | 2 |
| USD | $ | en-US | 2 |
| EUR | € | de-DE | 2 |
| GBP | £ | en-GB | 2 |
| JPY | ¥ | ja-JP | 0 |
| AUD | A$ | en-AU | 2 |
| CAD | C$ | en-CA | 2 |
| CHF | Fr | de-CH | 2 |
| CNY | ¥ | zh-CN | 2 |
| SAR | ر.س | ar-SA | 2 |
| AED | د.إ | ar-AE | 2 |
| ZAR | R | en-ZA | 2 |
| MXN | $ | es-MX | 2 |
| BRL | R$ | pt-BR | 2 |
| RUB | ₽ | ru-RU | 2 |

### Usage Examples

```typescript
import { formatCurrency, formatCurrencyCompact, getCurrencySymbol } from '@/utils/currencyUtils';

// Basic formatting (defaults to INR)
formatCurrency(10000); // "₹10,000.00"

// Specific currency
formatCurrency(10000, 'USD'); // "$10,000.00"
formatCurrency(10000, 'EUR'); // "10.000,00 €"
formatCurrency(10000, 'JPY'); // "¥10,000"

// Compact notation for large numbers
formatCurrencyCompact(1500000); // "₹15L" (Indian locale)
formatCurrencyCompact(1500000, 'USD'); // "$1.5M"

// Get currency symbol
getCurrencySymbol('INR'); // "₹"
getCurrencySymbol('USD'); // "$"
```

### Setting Organization Currency

1. Navigate to **Settings** → **Company Settings**
2. Select your preferred currency from the dropdown
3. All vouchers and reports will use this currency

---

## Voucher System

### Voucher Number Fields

The voucher system now supports additional reference fields:

| Field | Description | Usage |
|-------|-------------|-------|
| **Vendor Voucher Number** | External reference from vendor | Track vendor's invoice/PO numbers |
| **Customer Voucher Number** | Customer's reference number | Track customer's PO/order numbers |
| **Backdated Voucher Number** | Manual numbering for backdated entries | Maintain proper audit trail |

### How to Use Voucher Fields

1. **When Creating a Voucher:**
   - Enter the **Voucher Date** (current or backdated)
   - If backdating, the system will prompt for manual voucher number entry
   - Enter **Vendor Voucher Number** for purchases (supplier's invoice number)
   - Enter **Customer Voucher Number** for sales (customer's PO number)

2. **Backdated Numbering Behavior:**
   ```
   Current Date Entry: Auto-generated voucher number (e.g., INV/2024/00123)
   Backdated Entry: Manual entry required (respects existing sequence)
   ```

3. **Searching by Reference Numbers:**
   - Use the search bar in voucher lists
   - Search by vendor voucher number, customer voucher number, or internal voucher number

---

## Demo Mode & OTP User Flow

The Demo Mode allows potential users to experience the application with temporary 30-minute sessions.

### Starting a Demo Session

1. **Access Demo Page:**
   - Navigate to `/demo` or click "Try Demo" on the login page

2. **Initiate Session:**
   - Optionally enter phone number for WhatsApp OTP
   - Click "Start Demo"
   - System generates a demo email and 6-digit OTP

3. **Verify OTP:**
   - Enter the 6-digit OTP
   - Click "Verify"
   - Session starts (30-minute duration)

### Demo Session Features

| Feature | Description |
|---------|-------------|
| **Session Duration** | 30 minutes (auto-expires) |
| **Temporary Data** | All data created is ephemeral |
| **Full Access** | Explore all modules and features |
| **No Org Context** | Uses demo organization |
| **Audit Logging** | All actions are logged for security |

### Session Information

During a demo session, you can:
- View remaining time in the session info panel
- Manually logout (purges temporary data)
- Extend session by re-verifying OTP

### Data Purge on Logout/Expiry

When a demo session ends:
1. All temporary vouchers are deleted
2. All temporary settings are cleared
3. Audit logs are retained for compliance
4. Session token is invalidated

---

## HR Module (Phase 1)

The HR module provides basic human resources management capabilities.

### Available Features

#### 1. Department Management

Navigate to: **HR** → **Departments**

| Action | Description |
|--------|-------------|
| Create | Add new departments with hierarchy |
| Edit | Update department details |
| Assign Manager | Link department head |
| Cost Center | Map to financial cost center |

**Department Hierarchy:**
```
Organization
├── Operations
│   ├── Production
│   └── Quality
├── Sales
│   ├── Domestic
│   └── Export
└── Admin
    ├── HR
    └── Finance
```

#### 2. Position/Designation Management

Navigate to: **HR** → **Positions**

| Field | Description |
|-------|-------------|
| Title | Position name (e.g., "Senior Developer") |
| Code | Unique position code |
| Department | Associated department |
| Level | Job level (Junior, Mid, Senior, Lead, etc.) |
| Grade | Pay grade (A, B, C, etc.) |
| Salary Range | Min/max salary for position |

#### 3. Work Shift Management

Navigate to: **HR** → **Shifts**

| Field | Description |
|-------|-------------|
| Name | Shift name (e.g., "General Shift") |
| Code | Unique shift code |
| Start Time | Shift start time |
| End Time | Shift end time |
| Break Duration | Total break time (minutes) |
| Working Days | Days shift is active |

**Example Shifts:**
```
General Shift: 09:00 - 18:00 (60 min break)
Morning Shift: 06:00 - 14:00 (30 min break)
Night Shift: 22:00 - 06:00 (45 min break)
```

#### 4. Holiday Calendar

Navigate to: **HR** → **Holidays**

| Field | Description |
|-------|-------------|
| Date | Holiday date |
| Name | Holiday name |
| Type | public, optional, restricted |
| Year | Calendar year |

**Holiday Types:**
- **Public:** Office closed, paid leave
- **Optional:** Employee choice
- **Restricted:** Limited staff required

#### 5. Attendance Clock-In/Out

Navigate to: **HR** → **Attendance**

**Clock-In:**
1. Select employee
2. Choose work type (office, remote, field)
3. Optional: Add location, device info
4. Click "Clock In"

**Clock-Out:**
1. Select employee
2. Optional: Add remarks
3. Click "Clock Out"
4. System calculates total hours automatically

**Attendance Status Types:**
- present, absent, half_day, late, early_leave, on_leave

---

## HR Module (Phase 2 - Advanced Features)

Phase 2 introduces advanced payroll, attendance policies, and employee self-service capabilities.

### Employee Self-Service Portal

Navigate to: **HR** → **Self-Service**

Employees can access their own information through the self-service portal:

#### Leave Requests

| Feature | Description |
|---------|-------------|
| Apply Leave | Submit new leave applications |
| View History | See past leave requests and status |
| Check Balance | View available leave balances |
| Track Status | Monitor approval status |

**Applying for Leave:**
1. Click "Apply Leave" button
2. Select leave type from dropdown
3. Enter start and end dates
4. Provide reason for leave
5. Submit for approval

#### Attendance Self-Service

| Feature | Description |
|---------|-------------|
| Clock In/Out | Self-service attendance marking |
| View Records | See attendance history |
| Request Corrections | Submit attendance correction requests |
| Export Data | Download attendance reports |

**Clock In/Out Process:**
1. Navigate to Self-Service → Attendance
2. Click "Clock In" to start your work day
3. Clock shows current status and time
4. Click "Clock Out" when leaving
5. System calculates hours automatically

#### Payslip Downloads

| Feature | Description |
|---------|-------------|
| View Payslips | Access monthly payslips |
| Download PDF | Generate PDF payslip |
| View History | Access past payslips |
| Year-to-Date | View cumulative earnings |

### Advanced Payroll (HR Admins)

#### Salary Structure Management

Navigate to: **HR** → **Payroll** → **Salary Structures**

| Component | Description |
|-----------|-------------|
| Basic Salary | Core monthly salary |
| HRA | House Rent Allowance |
| Transport | Travel allowance |
| Medical | Medical benefits |
| Special | Special allowances |
| Variable | Performance-based pay |

#### Payroll Processing

**Monthly Payroll Workflow:**
1. **Create Period** - Define payroll period (e.g., "January 2024")
2. **Process Attendance** - Import attendance data
3. **Apply Deductions** - Calculate PF, PT, TDS
4. **Generate Payslips** - Create individual payslips
5. **Review & Approve** - Multi-level approval workflow
6. **Disburse** - Generate bank payment files

#### Statutory Deductions

The system supports Indian statutory deductions:

| Deduction | Rate | Details |
|-----------|------|---------|
| Provident Fund (PF) | 12% | On basic salary up to ₹15,000 |
| Professional Tax (PT) | Fixed | State-specific (₹200/month typical) |
| TDS | Slab-based | Income tax deduction |
| ESI | 0.75% | For gross salary < ₹21,000 |

#### Loans and Advances

Navigate to: **HR** → **Payroll** → **Loans**

| Loan Type | Description |
|-----------|-------------|
| Salary Advance | Short-term advance |
| Personal Loan | Employee loan with EMI |
| Emergency Loan | Emergency financial support |

**Loan Workflow:**
1. Employee submits loan application
2. HR reviews and approves
3. Finance disburses amount
4. EMI deducted from monthly payroll
5. Loan closes when fully repaid

### Attendance Policies

Navigate to: **HR** → **Settings** → **Attendance Policies**

#### Accrual Rules

| Setting | Description |
|---------|-------------|
| Accrual Type | Monthly, annual, or per pay period |
| Accrual Rate | Days accrued per period |
| Maximum Accrual | Cap on accrued days |

#### Carry Forward Rules

| Setting | Description |
|---------|-------------|
| Enabled | Allow carry forward |
| Max Days | Maximum days to carry |
| Expiry | Months until carried leave expires |

#### Overtime Calculation

| Setting | Description |
|---------|-------------|
| Threshold | Hours before overtime kicks in |
| Multiplier | Regular overtime rate (e.g., 1.5x) |
| Weekend Rate | Weekend overtime rate (e.g., 2x) |
| Holiday Rate | Holiday overtime rate (e.g., 2.5x) |

### Timesheets (Feature-Flagged)

Navigate to: **HR** → **Timesheets**

Weekly/monthly timesheet tracking for detailed time allocation:

| Field | Description |
|-------|-------------|
| Period | Timesheet week/month |
| Daily Hours | Hours logged per day |
| Project | Project allocation |
| Overtime | Extra hours worked |
| Status | Draft, Submitted, Approved |

**Timesheet Workflow:**
1. Employee enters daily hours
2. Submits timesheet for approval
3. Manager reviews and approves/rejects
4. Approved timesheets feed into payroll

### Arrears and Retro Adjustments

Navigate to: **HR** → **Payroll** → **Arrears**

Handle salary revisions and backdated adjustments:

| Type | Description |
|------|-------------|
| Salary Revision | Backdated salary increase |
| Bonus | One-time payment |
| Allowance | Additional allowance |
| Deduction | Recovery or correction |

### Bank Payment Export

Generate payment files for bulk salary disbursement:

| Format | Bank |
|--------|------|
| NEFT/RTGS | All banks |
| CSV | Generic format |
| Bank-Specific | HDFC, ICICI, SBI, etc. |

### Approval Workflows

Multi-level approval for payroll:

| Level | Role | Action |
|-------|------|--------|
| 1 | HR Manager | Initial review |
| 2 | Finance Head | Budget approval |
| 3 | CFO/Director | Final approval |

---

## Phase 4 Features (Scaffolding - Feature-Flagged)

The following features are available as scaffolding with feature flags:

### HR Analytics Dashboard

Navigate to: **HR** → **Analytics** (when enabled)

| Metric | Description |
|--------|-------------|
| Headcount | Total and active employees |
| Attrition Rate | Employee turnover percentage |
| Average Tenure | Mean employment duration |
| Payroll Cost | Total compensation expense |
| Department Breakdown | Headcount by department |

### Position Budgeting

Navigate to: **HR** → **Planning** → **Position Budget** (when enabled)

| Field | Description |
|-------|-------------|
| Fiscal Year | Budget year |
| Position | Job position |
| Budgeted Headcount | Planned positions |
| Actual Headcount | Current filled positions |
| Salary Budget | Allocated salary cost |

### Transfer History

Navigate to: **HR** → **Planning** → **Transfers** (when enabled)

Track employee movements:

| Transfer Type | Description |
|---------------|-------------|
| Department | Move between departments |
| Location | Office/location change |
| Position | Role change |
| Promotion | Advancement with salary change |

### Integration Adapters (Configuration)

Navigate to: **Settings** → **Integrations** → **HR Adapters** (when enabled)

| Adapter Type | Examples |
|--------------|----------|
| SSO/IdP | Okta, Azure AD, Auth0 |
| Payroll Provider | ADP, Greythr |
| Attendance Hardware | Biometric devices, Access cards |
| ERP | SAP, Oracle |

---

## AI Chatbot

The AI Chatbot provides intelligent assistance throughout the application.

### Accessing the Chatbot

- **Location:** Bottom-right corner of every page
- **Icon:** Chat bubble icon
- **Visibility:** Always visible when logged in

### Using the Chatbot

1. **Click the chat icon** to open the chat panel
2. **Type your question** in the input field
3. **Press Enter** or click Send
4. **View streaming response** in real-time

### Chatbot Capabilities

| Category | Examples |
|----------|----------|
| **Navigation** | "How do I create a sales invoice?" |
| **Reports** | "Show me how to view balance sheet" |
| **Features** | "What can the HR module do?" |
| **Business** | "How do I set up tax codes?" |
| **Analytics** | "Explain my sales trends" |

### Streaming Responses

The chatbot uses Server-Sent Events (SSE) for real-time responses:
- Text appears character-by-character
- No waiting for full response
- Can be interrupted by new messages

### Tips for Better Responses

1. Be specific in your questions
2. Provide context when needed
3. Ask follow-up questions for clarity
4. Use the chatbot for guidance, not data entry

---

## Exhibition Module

The Exhibition module manages CRM exhibitions and commission tracking.

### Creating an Exhibition

Navigate to: **CRM** → **Exhibitions** → **Create**

| Field | Description |
|-------|-------------|
| Name | Exhibition name |
| Location | Venue details |
| Start Date | Exhibition start |
| End Date | Exhibition end |
| Budget | Allocated budget |
| Expected Leads | Target lead count |

### Managing Leads from Exhibition

1. **During Exhibition:**
   - Capture leads directly in the mobile app
   - Scan business cards (if integrated)
   - Add notes and requirements

2. **Post-Exhibition:**
   - Convert leads to opportunities
   - Assign to sales team
   - Track conversion rate

### Commission Tracking

Navigate to: **CRM** → **Commissions**

| Feature | Description |
|---------|-------------|
| Commission Plans | Create tiered commission structures |
| Sales Attribution | Link sales to exhibitions |
| Commission Calculation | Automatic calculation |
| Payout Tracking | Manage commission payments |

---

## Role-Based Dashboards

Different users see different dashboards based on their role.

### Dashboard Types

| Role | Dashboard | Key Widgets |
|------|-----------|-------------|
| **Super Admin** | App-wide metrics | Organizations, Users, System Health |
| **Org Admin** | Organization dashboard | Sales, Inventory, Finance overview |
| **Sales Manager** | Sales dashboard | Pipeline, Opportunities, Targets |
| **Accountant** | Finance dashboard | P&L, Cash flow, Receivables |
| **HR Manager** | HR dashboard | Attendance, Leave, Headcount |
| **Warehouse** | Inventory dashboard | Stock levels, Movements |

### Recent Activity Widget

Each dashboard includes a recent activity panel showing:
- Last 10 actions by the user
- Important notifications
- Pending approvals
- Upcoming tasks

### Customizing Your Dashboard

1. Navigate to **Dashboard** → **Customize**
2. Drag and drop widgets
3. Resize as needed
4. Click **Save Layout**

---

## Mobile Experience

The application provides full mobile support with dedicated optimized pages.

### Mobile Pages

Access any page with `/mobile/` prefix:
- `/mobile/login` - Mobile login
- `/mobile/dashboard` - Mobile dashboard
- `/mobile/sales` - Sales module
- `/mobile/inventory` - Inventory management
- `/mobile/hr` - HR functions
- `/mobile/ai-chatbot` - AI assistance

### Mobile Features

| Feature | Description |
|---------|-------------|
| **Responsive Design** | Adapts to screen size |
| **Touch Optimized** | Large touch targets |
| **Offline Capable** | PWA support (partial) |
| **Camera Integration** | Barcode scanning |
| **GPS Location** | Field service tracking |

### Error Handling on Mobile

Mobile pages have enhanced error handling:
- Clear error messages
- Retry options
- Offline indicators
- Network status alerts

---

## GRN PDF Generation

The Goods Receipt Note (GRN) PDF has been enhanced with additional fields and improved formatting.

### New GRN Fields

| Field | Description |
|-------|-------------|
| **Vendor Invoice Number** | Supplier's invoice reference |
| **Vendor Invoice Date** | Date of supplier invoice |
| **E-Way Bill Number** | GST transport document number |
| **Manufacturing Date** | Product manufacturing date |
| **Expiry Date** | Product expiry date |
| **SKU** | Stock Keeping Unit code |
| **Lot Number** | Batch/lot identifier |

### GRN PDF Layout

```
┌─────────────────────────────────────────────────┐
│                GOODS RECEIPT NOTE                │
├─────────────────────────────────────────────────┤
│ GRN Details              │ Vendor Details        │
│ - GRN Number            │ - Vendor Name         │
│ - GRN Date              │ - Address             │
│ - Challan No.           │ - GSTIN               │
│ - Vendor Invoice No.    │                       │
│ - E-Way Bill No.        │                       │
├─────────────────────────────────────────────────┤
│ Items Table                                     │
│ Sr | Product | HSN | Batch | Ord | Rcv | Acc   │
│    | (SKU)   |     | Mfg/Exp|     |     | Rej  │
├─────────────────────────────────────────────────┤
│ Totals      │ QC Summary     │                  │
│             │ Acceptance: 98%│                  │
├─────────────────────────────────────────────────┤
│ Signatures: Received By | QC | Store | Auth    │
├─────────────────────────────────────────────────┤
│ Page 1 | Generated: 30/11/2025 19:00           │
└─────────────────────────────────────────────────┘
```

### Color-Coded Acceptance Rates

| Rate | Color | Meaning |
|------|-------|---------|
| ≥95% | Green | Excellent quality |
| 80-94% | Orange | Acceptable quality |
| <80% | Red | Quality concern |

### Generating GRN PDF

1. Navigate to the GRN voucher
2. Click **Print** or **Download PDF**
3. Select print options
4. Generate PDF

---

## Database Reset Workflow

### Complete Fresh Start

When you need to completely reset the database:

#### Step 1: Backup Current Data (Optional)

```bash
# Create a backup before dropping everything
pg_dump -U postgres -d your_database > backup_$(date +%Y%m%d_%H%M%S).sql
```

#### Step 2: Drop All Tables

```bash
# Option A: Using SQL script (RECOMMENDED)
psql -U postgres -d your_database

# In psql, edit the safety check in the SQL file first:
\e sql/drop_all_tables.sql
# Comment out the safety check line, then run:
\i sql/drop_all_tables.sql

# Option B: Drop and recreate database
psql -U postgres -c "DROP DATABASE IF EXISTS your_database;"
psql -U postgres -c "CREATE DATABASE your_database;"
```

#### Step 3: Run Migrations

```bash
# Apply all migrations to create fresh schema
alembic upgrade head

# Verify migrations applied successfully
alembic current
alembic history
```

#### Step 4: Seed Baseline Data

```bash
# Option A: Let the app auto-seed on startup (RECOMMENDED)
uvicorn app.main:app --reload
# The app will detect missing baseline data and seed automatically

# Option B: Manual seeding
python scripts/seed_all.py

# Option C: Force re-seed even if data exists
python scripts/seed_all.py --skip-check
```

#### Step 5: Verify Setup

```bash
# Start the application
uvicorn app.main:app --reload

# In another terminal, test the API
curl http://localhost:8000/health

# Test login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "naughtyfruit53@gmail.com", "password": "123456"}'
```

---

## Migration Guide

### Understanding Migrations

Alembic manages database schema changes. Each migration is a versioned script that can upgrade or downgrade your database schema.

### Common Migration Commands

```bash
# Show current migration version
alembic current

# Show migration history
alembic history --verbose

# Upgrade to latest version
alembic upgrade head

# Upgrade one version at a time
alembic upgrade +1

# Downgrade one version
alembic downgrade -1

# Downgrade to specific version
alembic downgrade <revision_id>

# Stamp database at current version (without running migrations)
alembic stamp head
```

### Creating New Migrations

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "Add new field to users table"

# Create empty migration for custom logic
alembic revision -m "Custom data migration"

# Edit the generated file in migrations/versions/
# Add upgrade() and downgrade() logic
```

### Migration Troubleshooting

#### Issue: "Can't locate revision"

```bash
# Check migration files exist
ls migrations/versions/

# Reset alembic version table
psql -U postgres your_database -c "DELETE FROM alembic_version;"
alembic stamp head
```

#### Issue: Migration fails mid-way

```bash
# Downgrade to previous version
alembic downgrade -1

# Fix the issue in code or migration script
# Try again
alembic upgrade +1
```

#### Issue: Migrations out of sync

```bash
# Mark current state as head without running migrations
alembic stamp head
```

---

## Seeding Baseline Data

### What Gets Seeded

The unified seeding script (`scripts/seed_all.py`) creates:

1. **Super Admin User**
   - Platform-level admin account
   - Email: naughtyfruit53@gmail.com
   - Full system access

2. **Module Taxonomy**
   - All system modules (Sales, Inventory, Manufacturing, etc.)
   - Submodules for granular entitlements
   - Module metadata and configuration

3. **RBAC Permissions**
   - Default service permissions
   - Default roles (org_admin, etc.)
   - Role-permission mappings

4. **Chart of Accounts**
   - Standard CoA structure
   - Default account categories
   - Basic financial setup

5. **Voucher Templates**
   - System voucher format templates
   - Standard, Modern, Classic, Minimal styles

6. **Organization Defaults**
   - Default enabled modules for organizations
   - Basic organization configuration

### Manual Seeding

```bash
# Run the unified seeding script
python scripts/seed_all.py

# The script is idempotent - it checks for existing data before seeding
# To force re-seed (not recommended unless you know what you're doing):
python scripts/seed_all.py --skip-check
```

### Auto-Seeding on First Boot

The system automatically checks for baseline data on startup and seeds if needed:

1. Checks for super admin user
2. Checks for module taxonomy
3. Checks for RBAC permissions
4. Checks for voucher templates
5. If any are missing, runs unified seeding automatically

**This means you typically don't need to run seeding manually!**

### Seeding Test/Demo Data

For development or demonstration purposes, additional demo data can be seeded:

```bash
# These scripts create sample business data (not essential for operation)
python scripts/archive/demo/seed_hr_data.py
python scripts/archive/demo/seed_crm_marketing_service_data.py
python scripts/archive/demo/seed_asset_transport_data.py
```

⚠️ **Note**: Demo data scripts are in the archive and are optional.

---

## User Onboarding

### Organization Setup

#### 1. Create Organization

After logging in as super admin:

```bash
# Via API
curl -X POST http://localhost:8000/api/v1/organizations \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Your Company Name",
    "subdomain": "yourcompany",
    "enabled_modules": {
      "sales": true,
      "inventory": true,
      "manufacturing": true
    }
  }'
```

Or use the frontend UI: Settings → Organizations → Create New

#### 2. Create Admin User

```bash
# Via API
curl -X POST http://localhost:8000/api/v1/users \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@yourcompany.com",
    "full_name": "Admin User",
    "role": "admin",
    "organization_id": 1,
    "password": "secure_password"
  }'
```

#### 3. Assign Modules and Permissions

Navigate to: Settings → Entitlements → Assign Modules

Or via API:
```bash
curl -X POST http://localhost:8000/api/v1/organizations/1/entitlements \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "modules": ["sales", "inventory", "manufacturing"],
    "license_tier": "professional"
  }'
```

### Adding New Users

#### Standard User Creation

```bash
curl -X POST http://localhost:8000/api/v1/users \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@yourcompany.com",
    "full_name": "New User",
    "role": "manager",
    "organization_id": 1,
    "password": "initial_password"
  }'
```

#### Assign RBAC Roles

```bash
curl -X POST http://localhost:8000/api/v1/rbac/users/{user_id}/roles \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "role_id": 1
  }'
```

### Module Access Control

The system uses a 3-layer security model:

1. **Organization Entitlements** - What modules the organization has access to
2. **User Roles** - What permissions users have within allowed modules
3. **RBAC Permissions** - Granular action-level permissions

Example workflow:
1. Enable modules for organization in entitlements
2. Create roles with specific permissions
3. Assign roles to users

---

## Troubleshooting

### Database Connection Issues

```bash
# Check PostgreSQL is running
pg_isready -h localhost -p 5432

# Test connection with psql
psql -U postgres -d your_database -c "SELECT 1;"

# Check DATABASE_URL in .env
echo $DATABASE_URL
```

### Migration Issues

```bash
# Check alembic version
alembic current

# If stuck, reset alembic state
psql -U postgres your_database -c "DELETE FROM alembic_version;"
alembic stamp head

# Then try migration again
alembic upgrade head
```

### Seeding Issues

```bash
# Check if super admin exists
python -c "
from app.core.database import SessionLocal
from app.models.user_models import User
db = SessionLocal()
admin = db.query(User).filter(User.is_super_admin == True).first()
print(f'Super admin exists: {admin is not None}')
"

# Force re-seed if needed
python scripts/seed_all.py --skip-check
```

### Authentication Issues

```bash
# Test login endpoint
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "naughtyfruit53@gmail.com", "password": "123456"}'

# Check user exists
psql -U postgres your_database -c "SELECT id, email, role FROM users LIMIT 5;"
```

### Permission Denied Errors

```bash
# Check organization enabled_modules
psql -U postgres your_database -c "SELECT id, name, enabled_modules FROM organizations;"

# Check user roles
psql -U postgres your_database -c "
  SELECT u.email, r.name as role_name 
  FROM users u 
  JOIN user_service_roles usr ON u.id = usr.user_id 
  JOIN service_roles r ON usr.role_id = r.id;
"

# Check RBAC permissions
curl -X GET http://localhost:8000/api/v1/rbac/users/{user_id}/permissions \
  -H "Authorization: Bearer <token>"
```

---

## Advanced Operations

### Environment-Specific Configuration

```bash
# Development
export DATABASE_URL="postgresql://user:pass@localhost/dev_db"
export DEBUG=True

# Production
export DATABASE_URL="postgresql://user:pass@prod.server/prod_db"
export DEBUG=False
export SECRET_KEY="your-production-secret-key"
```

### Backup and Restore

```bash
# Backup
pg_dump -U postgres your_database > backup.sql

# Restore
psql -U postgres your_database < backup.sql
```

### Performance Monitoring

```bash
# Check slow queries
psql -U postgres your_database -c "
  SELECT query, calls, total_time, mean_time 
  FROM pg_stat_statements 
  ORDER BY mean_time DESC 
  LIMIT 10;
"

# Check connection pool
curl http://localhost:8000/api/v1/debug/db-stats
```

### Database Maintenance

```bash
# Vacuum database
psql -U postgres your_database -c "VACUUM ANALYZE;"

# Reindex
psql -U postgres your_database -c "REINDEX DATABASE your_database;"

# Check table sizes
psql -U postgres your_database -c "
  SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
  FROM pg_tables
  WHERE schemaname = 'public'
  ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
"
```

---

## Additional Resources

- **RBAC Documentation**: See `RBAC_COMPREHENSIVE_GUIDE.md` for detailed RBAC setup
- **Entitlement Guide**: See `MODULE_ENTITLEMENT_RESTRICTIONS_GUIDE.md` for module access control
- **Database Reset**: See `DATABASE_RESET_GUIDE.md` for detailed reset procedures
- **API Documentation**: Access `/docs` when the app is running
- **Testing Guide**: See `TESTING_GUIDE.md` for testing procedures

---

## Support and Contact

For issues, questions, or contributions:
- Create an issue on GitHub
- Review `CONTRIBUTING.md` for contribution guidelines
- Check existing documentation in the `docs/` directory
- **Frontend-Backend Linkage Report**: See `docs/FRONTEND_BACKEND_LINKAGE_REPORT.md`

---

**Last Updated**: 2025-11-30  
**Version**: 1.6.1  
**Status**: Production Ready
