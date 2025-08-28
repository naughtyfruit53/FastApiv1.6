# Finance and Accounting Suite Documentation

## Overview

The Finance and Accounting Suite is a comprehensive financial management system that provides complete financial control, reporting, and analytics capabilities for the TRITIQ ERP platform. This production-ready implementation includes all essential accounting functions with modern dashboard analytics and forecasting capabilities.

## Table of Contents

1. [Core Features](#core-features)
2. [Architecture Overview](#architecture-overview)
3. [API Reference](#api-reference)
4. [Frontend Components](#frontend-components)
5. [Database Schema](#database-schema)
6. [Installation & Setup](#installation--setup)
7. [User Guides](#user-guides)
8. [Admin Configuration](#admin-configuration)
9. [Integration Points](#integration-points)
10. [Best Practices](#best-practices)
11. [Troubleshooting](#troubleshooting)

## Core Features

### 🏦 Chart of Accounts
- Hierarchical account structure with unlimited levels
- Support for multiple account types (Assets, Liabilities, Equity, Income, Expenses, Bank, Cash)
- Opening and current balance tracking
- Account grouping and classification
- Posting controls and reconciliation flags

### 📊 General Ledger
- Double-entry bookkeeping system
- Real-time running balance calculation
- Transaction reference tracking
- Cost center allocation
- Reconciliation status management
- Comprehensive audit trail

### 💰 Cost Centers
- Departmental cost tracking
- Budget vs. actual variance analysis
- Hierarchical cost center structure
- Manager assignment and departmental grouping
- Real-time utilization reporting

### 🏪 Bank Management
- Multiple bank account support
- Multi-currency capabilities
- Auto-reconciliation features
- Default account designation
- Comprehensive account details (IFSC, SWIFT codes)

### 📈 Financial Analytics
- Real-time financial dashboards
- Cash flow forecasting
- Profit & Loss trend analysis
- Expense breakdown and categorization
- KPI tracking and variance analysis
- Cross-module analytics integration

### 📋 Financial Reporting
- Trial Balance with real-time accuracy
- Profit & Loss statements
- Balance Sheet generation
- Cash Flow statements
- Customizable date ranges
- Export and print capabilities

### 🎯 Key Performance Indicators (KPIs)
- Configurable financial metrics
- Target vs. actual tracking
- Variance percentage calculations
- Category-based KPI grouping
- Historical trend analysis

## Architecture Overview

### Backend Architecture

```
Finance Suite Backend
├── Models (SQLAlchemy ORM)
│   ├── ChartOfAccounts
│   ├── GeneralLedger
│   ├── CostCenter
│   ├── BankAccount
│   ├── BankReconciliation
│   ├── FinancialStatement
│   └── FinancialKPI
├── APIs (FastAPI)
│   ├── ERP Core API (/api/v1/erp)
│   └── Finance Analytics API (/api/v1/finance)
├── Schemas (Pydantic)
│   ├── Create/Update/Response models
│   └── Validation rules
└── Services
    ├── FinanceAnalyticsService
    └── ERPService
```

### Frontend Architecture

```
Finance Suite Frontend
├── Pages
│   ├── finance-dashboard.tsx
│   ├── general-ledger.tsx
│   ├── cost-centers.tsx
│   ├── bank-accounts.tsx
│   └── financial-reports.tsx
├── Components
│   ├── Charts (Chart.js integration)
│   ├── Tables (Material-UI DataGrid)
│   └── Forms (React Hook Form)
└── Services
    ├── API integration (Axios)
    └── State management
```

## API Reference

### ERP Core API Endpoints

#### Chart of Accounts

```http
GET /api/v1/erp/chart-of-accounts
POST /api/v1/erp/chart-of-accounts
GET /api/v1/erp/chart-of-accounts/{id}
PUT /api/v1/erp/chart-of-accounts/{id}
DELETE /api/v1/erp/chart-of-accounts/{id}
```

#### General Ledger

```http
GET /api/v1/erp/general-ledger
POST /api/v1/erp/general-ledger
GET /api/v1/erp/general-ledger/{id}
PUT /api/v1/erp/general-ledger/{id}
```

#### Cost Centers

```http
GET /api/v1/erp/cost-centers
POST /api/v1/erp/cost-centers
GET /api/v1/erp/cost-centers/{id}
PUT /api/v1/erp/cost-centers/{id}
DELETE /api/v1/erp/cost-centers/{id}
```

#### Bank Accounts

```http
GET /api/v1/erp/bank-accounts
POST /api/v1/erp/bank-accounts
GET /api/v1/erp/bank-accounts/{id}
PUT /api/v1/erp/bank-accounts/{id}
DELETE /api/v1/erp/bank-accounts/{id}
```

#### Financial KPIs

```http
GET /api/v1/erp/financial-kpis
POST /api/v1/erp/financial-kpis
GET /api/v1/erp/financial-kpis/{id}
PUT /api/v1/erp/financial-kpis/{id}
DELETE /api/v1/erp/financial-kpis/{id}
```

#### Financial Reports

```http
GET /api/v1/erp/trial-balance
GET /api/v1/erp/profit-loss
GET /api/v1/erp/balance-sheet
GET /api/v1/erp/dashboard
```

### Finance Analytics API Endpoints

#### Dashboard Analytics

```http
GET /api/v1/finance/analytics/dashboard
```

Returns comprehensive financial metrics including:
- Financial ratios (current ratio, debt-to-equity, working capital)
- Cash flow analysis (inflow, outflow, net flow)
- Accounts aging (overdue payables/receivables)
- Cost center performance
- Recent KPI trends

#### Cash Flow Forecasting

```http
GET /api/v1/finance/analytics/cash-flow-forecast
```

Provides future cash flow projections based on:
- Expected receivables by due date
- Expected payables by due date
- Current cash position
- Projected ending balance

#### Profit & Loss Trends

```http
GET /api/v1/finance/analytics/profit-loss-trend
```

Returns monthly P&L analysis including:
- Income and expense trends
- Net profit/loss calculations
- Profit margin analysis
- Comparative period data

#### Expense Analysis

```http
GET /api/v1/finance/analytics/expense-breakdown
```

Provides detailed expense categorization:
- Grouping by account, cost center, or category
- Percentage breakdown
- Period-based analysis

#### KPI Trends

```http
GET /api/v1/finance/analytics/kpi-trends
```

Returns KPI historical analysis:
- Multi-period KPI values
- Target vs. actual comparisons
- Variance trend analysis

## Frontend Components

### Finance Dashboard

**Location**: `/frontend/src/pages/finance-dashboard.tsx`

**Features**:
- Real-time financial metrics display
- Interactive charts and graphs
- Tabbed interface for different analytics views
- Responsive design with Material-UI components
- Export and print capabilities

**Key Components**:
- Financial ratio cards
- Cash flow visualization (Doughnut chart)
- Cost center performance (Bar chart)
- KPI tracking table
- Accounts aging summary

### General Ledger

**Location**: `/frontend/src/pages/general-ledger.tsx`

**Features**:
- Complete transaction listing with filtering
- Real-time balance calculations
- Transaction entry creation
- Account-based filtering
- Date range selection
- Pagination support

**Key Components**:
- Transaction table with running balances
- Create entry dialog
- Filter controls (account, date range)
- Summary cards (total debits, credits, difference)

### Cost Centers

**Location**: `/frontend/src/pages/cost-centers.tsx`

**Features**:
- Hierarchical cost center display
- Budget vs. actual variance tracking
- Visual performance indicators
- Tree view navigation
- Utilization progress bars

**Key Components**:
- Cost center hierarchy tree
- Performance table with variance calculations
- Budget utilization progress indicators
- Create/edit cost center dialogs

### Bank Accounts

**Location**: `/frontend/src/pages/bank-accounts.tsx`

**Features**:
- Multi-currency bank account management
- Default account designation
- Auto-reconciliation settings
- Security-focused account number display
- Comprehensive account details

**Key Components**:
- Bank account table with status indicators
- Account creation forms
- Currency selection
- Security features (masked account numbers)

### Financial Reports

**Location**: `/frontend/src/pages/financial-reports.tsx`

**Features**:
- Multi-report tabbed interface
- Date range selection
- Real-time report generation
- Chart visualizations
- Export and print functionality

**Reports Included**:
- Trial Balance
- Profit & Loss Statement
- Balance Sheet
- Cash Flow Statement

## Database Schema

### Core Tables

#### chart_of_accounts
```sql
CREATE TABLE chart_of_accounts (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL,
    account_code VARCHAR(50) NOT NULL,
    account_name VARCHAR(200) NOT NULL,
    account_type account_type_enum NOT NULL,
    parent_account_id INTEGER,
    level INTEGER DEFAULT 0,
    is_group BOOLEAN DEFAULT FALSE,
    opening_balance NUMERIC(15,2) DEFAULT 0.00,
    current_balance NUMERIC(15,2) DEFAULT 0.00,
    is_active BOOLEAN DEFAULT TRUE,
    can_post BOOLEAN DEFAULT TRUE,
    is_reconcilable BOOLEAN DEFAULT FALSE,
    description TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER,
    updated_by INTEGER
);
```

#### general_ledger
```sql
CREATE TABLE general_ledger (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL,
    account_id INTEGER NOT NULL,
    transaction_date DATE NOT NULL,
    transaction_number VARCHAR(100) NOT NULL,
    reference_type VARCHAR(50),
    reference_id INTEGER,
    reference_number VARCHAR(100),
    debit_amount NUMERIC(15,2) DEFAULT 0.00,
    credit_amount NUMERIC(15,2) DEFAULT 0.00,
    running_balance NUMERIC(15,2) NOT NULL,
    description TEXT,
    narration TEXT,
    cost_center_id INTEGER,
    is_reconciled BOOLEAN DEFAULT FALSE,
    reconciled_date DATE,
    reconciled_by INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER
);
```

#### cost_centers
```sql
CREATE TABLE cost_centers (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL,
    cost_center_code VARCHAR(50) NOT NULL,
    cost_center_name VARCHAR(200) NOT NULL,
    parent_cost_center_id INTEGER,
    level INTEGER DEFAULT 0,
    budget_amount NUMERIC(15,2) DEFAULT 0.00,
    actual_amount NUMERIC(15,2) DEFAULT 0.00,
    is_active BOOLEAN DEFAULT TRUE,
    department VARCHAR(100),
    manager_id INTEGER,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER
);
```

#### bank_accounts
```sql
CREATE TABLE bank_accounts (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL,
    chart_account_id INTEGER NOT NULL,
    bank_name VARCHAR(200) NOT NULL,
    branch_name VARCHAR(200),
    account_number VARCHAR(50) NOT NULL,
    ifsc_code VARCHAR(20),
    swift_code VARCHAR(20),
    account_type VARCHAR(50) NOT NULL,
    currency VARCHAR(3) DEFAULT 'INR',
    opening_balance NUMERIC(15,2) DEFAULT 0.00,
    current_balance NUMERIC(15,2) DEFAULT 0.00,
    is_active BOOLEAN DEFAULT TRUE,
    is_default BOOLEAN DEFAULT FALSE,
    auto_reconcile BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Indexes and Constraints

The schema includes comprehensive indexing for optimal performance:

- **Organizational partitioning**: All tables indexed by organization_id
- **Transaction lookups**: Compound indexes on date and account combinations
- **Reference tracking**: Indexes on reference_type and reference_id
- **Unique constraints**: Organization-scoped unique constraints for codes
- **Foreign key constraints**: Proper relationships between all tables

## Installation & Setup

### Backend Setup

1. **Install Dependencies**
```bash
pip install -r requirements.txt
```

2. **Run Database Migrations**
```bash
alembic upgrade head
```

3. **Verify Installation**
```bash
python -m pytest tests/test_finance_suite.py -v
```

### Frontend Setup

1. **Install Dependencies**
```bash
cd frontend
npm install
```

2. **Install Chart.js Dependencies**
```bash
npm install chart.js react-chartjs-2
npm install @mui/x-date-pickers @mui/x-tree-view
```

3. **Start Development Server**
```bash
npm run dev
```

### Required Environment Variables

```env
DATABASE_URL=postgresql://user:password@localhost/database
SECRET_KEY=your-secret-key
ORGANIZATION_ID=1
```

## User Guides

### Setting Up Chart of Accounts

1. **Access Chart of Accounts**
   - Navigate to Finance → Chart of Accounts
   - View existing account structure

2. **Create New Account**
   - Click "New Account" button
   - Enter account code and name
   - Select appropriate account type
   - Set parent account for hierarchy
   - Configure posting and reconciliation settings

3. **Account Types**
   - **Assets**: Current and non-current assets
   - **Liabilities**: Short-term and long-term liabilities
   - **Equity**: Owner's equity and retained earnings
   - **Income**: Revenue and other income sources
   - **Expense**: Operating and non-operating expenses
   - **Bank**: Bank account representations
   - **Cash**: Cash and cash equivalent accounts

### Managing General Ledger

1. **View Transactions**
   - Access Finance → General Ledger
   - Use filters to find specific transactions
   - Sort by date, amount, or account

2. **Create Journal Entries**
   - Click "New Entry" button
   - Select account and enter amounts
   - Ensure debits equal credits
   - Add descriptions and references

3. **Reconciliation**
   - Mark entries as reconciled
   - Track reconciliation status
   - Generate reconciliation reports

### Cost Center Management

1. **Create Cost Centers**
   - Navigate to Finance → Cost Centers
   - Create departmental cost centers
   - Set budget amounts and managers
   - Establish hierarchy relationships

2. **Monitor Performance**
   - View budget vs. actual comparisons
   - Track variance percentages
   - Generate cost center reports
   - Analyze departmental spending

### Bank Account Setup

1. **Add Bank Accounts**
   - Go to Finance → Bank Accounts
   - Enter bank details and account numbers
   - Link to chart of accounts
   - Set default accounts

2. **Configure Features**
   - Enable auto-reconciliation
   - Set currency preferences
   - Manage account status

### Financial Reporting

1. **Generate Reports**
   - Access Finance → Financial Reports
   - Select report type and date range
   - Generate real-time reports
   - Export to PDF or Excel

2. **Report Types**
   - **Trial Balance**: Verify accounting accuracy
   - **Profit & Loss**: Income and expense analysis
   - **Balance Sheet**: Financial position statement
   - **Cash Flow**: Cash movement analysis

## Admin Configuration

### System Setup

1. **Initial Configuration**
   - Set up default chart of accounts
   - Configure cost center structure
   - Establish bank accounts
   - Set fiscal year parameters

2. **User Permissions**
   - Assign finance module access
   - Configure role-based permissions
   - Set approval workflows
   - Manage audit settings

3. **Integration Setup**
   - Configure voucher posting to GL
   - Set up automatic journal entries
   - Enable cost center allocation
   - Configure bank reconciliation

### Performance Optimization

1. **Database Maintenance**
   - Regular index optimization
   - Archival of old transactions
   - Backup and recovery procedures

2. **Monitoring**
   - Track system performance
   - Monitor API response times
   - Review error logs

## Integration Points

### ERP Integration

- **Voucher Posting**: Automatic journal entry creation from sales/purchase vouchers
- **Inventory Costing**: Integration with inventory valuation
- **Cost Allocation**: Automatic cost center distribution

### CRM Integration

- **Customer Aging**: Real-time receivables tracking
- **Credit Management**: Customer credit limit monitoring
- **Sales Analytics**: Revenue recognition and tracking

### HR Integration

- **Payroll Posting**: Automatic salary and benefit entries
- **Employee Cost Centers**: Labor cost allocation
- **Expense Management**: Employee expense processing

## Best Practices

### Financial Data Management

1. **Data Accuracy**
   - Implement double-entry validation
   - Regular reconciliation procedures
   - Segregation of duties

2. **Security**
   - Role-based access control
   - Audit trail maintenance
   - Data encryption at rest

3. **Performance**
   - Regular database maintenance
   - Efficient query optimization
   - Proper indexing strategies

### Workflow Management

1. **Approval Processes**
   - Multi-level approval workflows
   - Automated notifications
   - Exception handling

2. **Period-End Procedures**
   - Month-end closing checklists
   - Automated reconciliations
   - Report generation schedules

## Troubleshooting

### Common Issues

1. **Trial Balance Not Balancing**
   - Check for incomplete journal entries
   - Verify account type classifications
   - Review opening balance entries

2. **Performance Issues**
   - Optimize database queries
   - Review indexing strategy
   - Check for large transaction volumes

3. **Integration Errors**
   - Verify API connectivity
   - Check authentication tokens
   - Review data mapping configurations

### Error Messages

- **"Account not found"**: Verify account ID and organization access
- **"Insufficient permissions"**: Check user role assignments
- **"Balance calculation error"**: Review transaction sequence and amounts

### Support Resources

- **Documentation**: Complete API and user documentation
- **Test Suite**: Comprehensive test coverage for validation
- **Error Logging**: Detailed error tracking and reporting
- **Performance Monitoring**: Real-time system health monitoring

---

## Conclusion

The Finance and Accounting Suite provides a complete, production-ready financial management solution for the TRITIQ ERP platform. With comprehensive features, robust architecture, and extensive documentation, it enables organizations to maintain accurate financial records, generate insightful reports, and make data-driven financial decisions.

For additional support or feature requests, please refer to the project repository or contact the development team.