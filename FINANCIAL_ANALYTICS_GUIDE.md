# Financial Analytics and Reports Implementation Guide

## Overview

This document describes the financial analytics and reporting features implemented in the FastAPI ERP system, including API endpoints, frontend pages, and usage guidelines.

## Features Implemented

### 1. Financial Reports
- **Profit & Loss Statement**: Comprehensive income and expense reporting
- **Balance Sheet**: Asset, liability, and equity reporting  
- **Cash Flow Statement**: Operating, investing, and financing activities
- **Trial Balance**: Account-level debit and credit balances

### 2. Financial Analytics
- **Vendor Aging Report**: Tracks overdue payables by aging buckets
- **Customer Aging Report**: Tracks overdue receivables by aging buckets
- **Budget Management**: Cost center budget vs actual analysis
- **Cash Flow Forecast**: Multi-period cash flow projections
- **Financial KPIs**: Key performance indicators dashboard
- **Expense Analysis**: Category-wise expense breakdown

### 3. Accounts Receivable
- Updated to provide full customer invoice and payment tracking functionality
- Removed "under development" message
- Integrated with customer aging and payment workflow

## API Endpoints

### Financial Reports

#### Profit & Loss Statement
```
GET /api/v1/erp/profit-loss
```
**Parameters:**
- `from_date` (required): Start date for report (YYYY-MM-DD)
- `to_date` (required): End date for report (YYYY-MM-DD)

**Response:**
```json
{
  "income": [
    {
      "account_code": "4001",
      "account_name": "Sales Revenue",
      "amount": 100000.00
    }
  ],
  "expenses": [
    {
      "account_code": "5001",
      "account_name": "Cost of Goods Sold",
      "amount": 60000.00
    }
  ],
  "total_income": 100000.00,
  "total_expenses": 60000.00,
  "net_profit_loss": 40000.00,
  "from_date": "2025-01-01",
  "to_date": "2025-01-31"
}
```

#### Balance Sheet
```
GET /api/v1/erp/balance-sheet
```
**Parameters:**
- `as_of_date` (required): Report date (YYYY-MM-DD)

**Response:**
```json
{
  "assets": [...],
  "liabilities": [...],
  "equity": [...],
  "total_assets": 500000.00,
  "total_liabilities": 200000.00,
  "total_equity": 300000.00,
  "as_of_date": "2025-01-31"
}
```

#### Cash Flow Statement
```
GET /api/v1/erp/cash-flow
```
**Parameters:**
- `from_date` (required): Start date (YYYY-MM-DD)
- `to_date` (required): End date (YYYY-MM-DD)

**Response:**
```json
{
  "operating_activities": [...],
  "investing_activities": [...],
  "financing_activities": [...],
  "net_operating_cash": 50000.00,
  "net_investing_cash": -20000.00,
  "net_financing_cash": 10000.00,
  "net_cash_flow": 40000.00,
  "opening_cash": 100000.00,
  "closing_cash": 140000.00,
  "from_date": "2025-01-01",
  "to_date": "2025-01-31"
}
```

### Financial Analytics

#### Vendor Aging
```
GET /api/v1/finance/analytics/vendor-aging
```
**Parameters:**
- `aging_periods` (optional): List of aging period days (default: [30, 60, 90])

**Response:**
```json
{
  "as_of_date": "2025-01-31",
  "aging_buckets": {
    "current": {"amount": 50000, "count": 10, "vendors": 5},
    "30_days": {"amount": 30000, "count": 8, "vendors": 4},
    "60_days": {"amount": 20000, "count": 5, "vendors": 3},
    "90_days": {"amount": 10000, "count": 3, "vendors": 2},
    "over_90": {"amount": 5000, "count": 2, "vendors": 1}
  },
  "total_outstanding": 115000,
  "summary": {
    "total_vendors": 15,
    "total_invoices": 28,
    "total_outstanding": 115000
  }
}
```

#### Customer Aging
```
GET /api/v1/finance/analytics/customer-aging
```
Similar structure to vendor aging, with customer-specific fields.

#### Budget Management
```
GET /api/v1/finance/analytics/budgets
```
**Parameters:**
- `budget_year` (optional): Year for budget data (default: current year)

**Response:**
```json
{
  "budget_year": 2025,
  "cost_centers": [
    {
      "cost_center_id": 1,
      "cost_center_name": "Marketing",
      "cost_center_code": "MKT001",
      "budget_amount": 100000,
      "actual_amount": 95000,
      "variance": -5000,
      "variance_percent": -5.0,
      "status": "under_budget"
    }
  ],
  "summary": {
    "total_budget": 500000,
    "total_actual": 480000,
    "total_variance": -20000,
    "variance_percent": -4.0
  }
}
```

#### Financial KPIs
```
GET /api/v1/finance/analytics/financial-kpis
```
**Parameters:**
- `period_months` (optional): Number of months for analysis (default: 3)

**Response:**
```json
{
  "period": {
    "start_date": "2024-11-01",
    "end_date": "2025-01-31"
  },
  "kpis": [
    {
      "kpi_code": "CURRENT_RATIO",
      "kpi_name": "Current Ratio",
      "kpi_category": "Liquidity",
      "value": 2.5,
      "target": 2.0,
      "variance": 25.0,
      "period_end": "2025-01-31",
      "status": "on_track"
    }
  ],
  "financial_ratios": {
    "current_ratio": 2.5,
    "debt_to_equity": 0.67,
    "working_capital": 150000,
    "total_assets": 500000,
    "total_liabilities": 200000,
    "total_equity": 300000
  },
  "summary": {
    "total_kpis": 10,
    "on_track_count": 7,
    "needs_attention_count": 3
  }
}
```

#### Expense Analysis
```
GET /api/v1/finance/analytics/expense-analysis
```
**Parameters:**
- `period_months` (optional): Number of months for analysis (default: 6)

**Response:**
```json
{
  "period": {
    "start_date": "2024-08-01",
    "end_date": "2025-01-31"
  },
  "expenses": [
    {
      "account_code": "5001",
      "account_name": "Cost of Goods Sold",
      "amount": 60000,
      "parent_account": "Root",
      "percentage": 40.0
    }
  ],
  "summary": {
    "total_expenses": 150000,
    "expense_count": 15,
    "top_expense": {
      "account_code": "5001",
      "account_name": "Cost of Goods Sold",
      "amount": 60000,
      "percentage": 40.0
    }
  }
}
```

## Frontend Pages

### Navigation
All pages are accessible through the MegaMenu under the **Finance** section:

- **Accounts Payable** → Vendor Aging
- **Accounts Receivable** → Customer Aging, Customer Invoices
- **Cost Management** → Budget Management
- **Financial Reports** → Cash Flow Forecast, Financial Reports Hub
- **Analytics & KPIs** → Finance Dashboard, Financial KPIs, Expense Analysis

### Page Features

#### Vendor Aging (`/vendor-aging`)
- Visual pie chart showing aging distribution
- Summary table with aging buckets
- Export and print functionality
- Summary cards showing total outstanding, vendors, and invoices

#### Customer Aging (`/customer-aging`)
- Similar to vendor aging with customer-specific data
- Helps track collection efficiency
- Identifies high-risk receivables

#### Budget Management (`/budgets`)
- Year selector for viewing different budget periods
- Budget vs Actual comparison charts
- Cost center performance table
- Variance analysis with status indicators

#### Cash Flow Forecast (`/cash-flow-forecast`)
- Multi-period cash flow projections
- Trend line charts for inflow/outflow
- Configurable forecast period
- Summary cards for key metrics

#### Financial KPIs (`/financial-kpis`)
- Key financial ratio cards
- KPI performance table with variance tracking
- Status indicators (on track, needs attention)
- Period selector for historical analysis

#### Expense Analysis (`/expense-analysis`)
- Pie and bar charts for top expenses
- Detailed expense breakdown table
- Category-wise percentage distribution
- Period selector for time-based analysis

#### Accounts Receivable (`/accounts-receivable`)
- Customer invoice list
- Payment status tracking
- Quick actions for viewing and receiving payments
- Summary cards for total/outstanding amounts

## Usage Guide

### Getting Started

1. **Access Reports**: Navigate to the Finance section in the MegaMenu
2. **Select Report**: Choose the desired report or analytics page
3. **Configure Parameters**: Set date ranges, periods, or filters as needed
4. **Generate Report**: Click the generate or refresh button
5. **Export/Print**: Use the export or print buttons to save or share reports

### Best Practices

1. **Regular Monitoring**: Review aging reports weekly to manage cash flow
2. **Budget Reviews**: Conduct monthly budget vs actual reviews
3. **KPI Tracking**: Monitor financial KPIs daily or weekly
4. **Expense Control**: Analyze expenses monthly to identify cost-saving opportunities
5. **Cash Flow Planning**: Use forecasts for proactive financial planning

### Troubleshooting

#### No Data Displayed
- Ensure organization has been set up properly
- Verify chart of accounts is configured
- Check that transactions have been recorded
- Confirm user has appropriate permissions

#### Incorrect Balances
- Verify journal entries are posted correctly
- Check account types are configured properly
- Ensure opening balances are set
- Review reconciliation status

## Integration

### With Existing Modules
- **Chart of Accounts**: All reports pull data from configured accounts
- **Journal Entries**: Transaction data flows to reports automatically
- **Vouchers**: Financial vouchers update reports in real-time
- **Cost Centers**: Budget data integrates with cost center management

### Data Flow
1. Transactions entered via vouchers or journal entries
2. Posted to general ledger and account balances updated
3. Reports query current balances and transactions
4. Analytics calculate KPIs and trends
5. Frontend displays formatted data with visualizations

## Security

All endpoints require:
- Valid authentication token
- Current organization context
- Appropriate user permissions
- Company setup validation

## Performance Considerations

- Reports are generated on-demand
- Large date ranges may take longer to process
- Consider caching for frequently accessed reports
- Use pagination for detailed transaction listings

## Future Enhancements

Planned improvements:
- Scheduled report generation
- Email delivery of reports
- Advanced filtering options
- Comparative period analysis
- Drill-down capabilities
- Custom report builder
- Real-time dashboard widgets
