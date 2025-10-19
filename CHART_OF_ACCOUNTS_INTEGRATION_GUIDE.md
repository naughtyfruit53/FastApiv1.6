# Chart of Accounts Universal Integration Guide

## Overview

This document describes the comprehensive Chart of Accounts (COA) integration across all modules in the FastAPI v1.6 ERP system. The integration ensures that all financial transactions, entities, and operations are properly mapped to accounting categories for unified financial management.

## What Was Implemented

### 1. Model Enhancements

#### Customer Model
- **New Field**: `receivable_account_id` (Foreign Key to ChartOfAccounts)
- **Relationship**: `receivable_account` (Links to the COA account for tracking receivables)
- **Default Account**: Automatically linked to "Accounts Receivable" (Code: 1120)

```python
class Customer(Base):
    # ... existing fields ...
    receivable_account_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("chart_of_accounts.id"), nullable=True, index=True
    )
    receivable_account: Mapped[Optional["ChartOfAccounts"]] = relationship(
        "ChartOfAccounts", foreign_keys=[receivable_account_id]
    )
```

#### Vendor Model
- **New Field**: `payable_account_id` (Foreign Key to ChartOfAccounts)
- **Relationship**: `payable_account` (Links to the COA account for tracking payables)
- **Default Account**: Automatically linked to "Accounts Payable" (Code: 2110)

```python
class Vendor(Base):
    # ... existing fields ...
    payable_account_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("chart_of_accounts.id"), nullable=True, index=True
    )
    payable_account: Mapped[Optional["ChartOfAccounts"]] = relationship(
        "ChartOfAccounts", foreign_keys=[payable_account_id]
    )
```

#### FreightRate Model
- **New Field**: `freight_expense_account_id` (Foreign Key to ChartOfAccounts)
- **Relationship**: `freight_expense_account` (Links to the COA account for freight expenses)
- **Default Account**: Automatically linked to "Freight Expense" (Code: 5210)

```python
class FreightRate(Base):
    # ... existing fields ...
    freight_expense_account_id = Column(
        Integer, ForeignKey("chart_of_accounts.id"), nullable=True, index=True
    )
    freight_expense_account = relationship(
        "ChartOfAccounts", foreign_keys=[freight_expense_account_id]
    )
```

### 2. Schema Updates

All Create, Update, and Response schemas have been updated to include COA fields:

- `CustomerCreate`, `CustomerUpdate`, `CustomerInDB` - Added `receivable_account_id`
- `VendorCreate`, `VendorUpdate`, `VendorInDB` - Added `payable_account_id`
- `ChartOfAccountMinimal` - New minimal schema for nested COA references
- `CustomerWithCOA`, `VendorWithCOA`, `FreightRateWithCOA` - Enhanced response schemas showing COA relationships

### 3. Default Chart of Accounts

A comprehensive seeding script creates 35 default accounts organized in a hierarchical structure:

#### Assets (1000)
- Current Assets (1100)
  - Cash and Cash Equivalents (1110)
    - Cash in Hand (1111)
    - Cash at Bank (1112)
  - Accounts Receivable (1120) ← **Used by Customers**
  - Inventory (1130)
- Fixed Assets (1200)
  - Property, Plant & Equipment (1210)

#### Liabilities (2000)
- Current Liabilities (2100)
  - Accounts Payable (2110) ← **Used by Vendors**
  - GST Payable (2120)
  - Payroll Payable (2130)

#### Equity (3000)
- Capital (3100)
- Retained Earnings (3200)

#### Income (4000)
- Sales Income (4100)
- Service Income (4200)
- Other Income (4300)
- Discount Income (4400)

#### Expenses (5000)
- Cost of Goods Sold (5100)
  - Purchase Expense (5110)
- Operating Expenses (5200)
  - Freight Expense (5210) ← **Used by FreightRates**
  - Salary Expense (5220)
  - Rent Expense (5230)
  - Utilities Expense (5240)
  - Discount Expense (5250)
  - GST Expense (5260)

### 4. Database Migrations

#### Migration 1: coa_integration_001_add_coa_to_entities.py
Adds COA foreign key columns to Customer, Vendor, and FreightRate tables:
- `vendors.payable_account_id`
- `customers.receivable_account_id`
- `freight_rates.freight_expense_account_id`

#### Migration 2: coa_integration_002_backfill_coa_references.py
Backfills existing records with default COA account references:
- Links all existing vendors to the default "Accounts Payable" account
- Links all existing customers to the default "Accounts Receivable" account
- Links all existing freight rates to the default "Freight Expense" account

### 5. API Enhancements

#### Auto-Assignment of COA Accounts

When creating new entities, the API automatically assigns default COA accounts if not explicitly provided:

**Customer Creation** (`POST /api/customers/`)
```python
# Auto-assigns Accounts Receivable (1120) if receivable_account_id not provided
if not customer_data.get('receivable_account_id'):
    default_receivable = await db.query(ChartOfAccounts).filter(
        ChartOfAccounts.organization_id == org_id,
        ChartOfAccounts.account_code == '1120'
    ).first()
    if default_receivable:
        customer_data['receivable_account_id'] = default_receivable.id
```

**Vendor Creation** (`POST /api/vendors/`)
```python
# Auto-assigns Accounts Payable (2110) if payable_account_id not provided
if not vendor_data.get('payable_account_id'):
    default_payable = await db.query(ChartOfAccounts).filter(
        ChartOfAccounts.organization_id == org_id,
        ChartOfAccounts.account_code == '2110'
    ).first()
    if default_payable:
        vendor_data['payable_account_id'] = default_payable.id
```

#### New Endpoint: COA Entity Links

**GET** `/api/v1/erp/chart-of-accounts/{account_id}/entity-links`

Returns all entities (customers, vendors, freight rates) linked to a specific COA account.

**Response:**
```json
{
  "account_id": 123,
  "account_code": "1120",
  "account_name": "Accounts Receivable",
  "account_type": "ASSET",
  "entity_links": [
    {
      "entity_type": "Customer",
      "entity_id": 1,
      "entity_name": "ABC Corp",
      "link_type": "receivable"
    },
    {
      "entity_type": "Customer",
      "entity_id": 2,
      "entity_name": "XYZ Ltd",
      "link_type": "receivable"
    }
  ],
  "total_links": 2
}
```

## Usage Examples

### Creating a Customer with Custom COA Account

```python
# Option 1: Let the system auto-assign the default account
customer_data = {
    "name": "New Customer",
    "contact_number": "1234567890",
    "email": "customer@example.com",
    "address1": "123 Main St",
    "city": "Mumbai",
    "state": "Maharashtra",
    "pin_code": "400001",
    "state_code": "MH"
}

# Option 2: Explicitly specify a COA account
customer_data = {
    # ... same fields as above ...
    "receivable_account_id": 456  # Custom COA account
}
```

### Creating a Vendor with Custom COA Account

```python
vendor_data = {
    "name": "Supplier Co",
    "contact_number": "9876543210",
    "address1": "456 Market St",
    "city": "Delhi",
    "state": "Delhi",
    "pin_code": "110001",
    "state_code": "DL",
    "payable_account_id": 789  # Optional: custom COA account
}
```

### Viewing COA Account Usage

```bash
# Get all entities using a specific COA account
GET /api/v1/erp/chart-of-accounts/123/entity-links
```

## Seeding Default Accounts

To create default COA accounts for all organizations:

```bash
python -m app.scripts.seed_default_coa_accounts
```

To create default accounts for a specific organization (programmatically):

```python
from app.scripts.seed_default_coa_accounts import create_default_accounts
from app.core.database import SessionLocal

db = SessionLocal()
organization_id = 1
user_id = 1  # Optional

create_default_accounts(db, organization_id, user_id)
db.close()
```

## Running Migrations

```bash
# Apply the COA integration migrations
alembic upgrade head

# Or apply specific migrations
alembic upgrade coa_integration_001
alembic upgrade coa_integration_002
```

## Testing

Run the comprehensive COA integration tests:

```bash
pytest tests/test_coa_integration.py -v
```

Test coverage includes:
- Default account creation
- Customer COA linkage
- Vendor COA linkage
- FreightRate COA linkage
- Auto-assignment logic
- Entity links API endpoint

## Benefits

1. **Unified Financial Management**: All entities are mapped to proper accounting categories
2. **Automatic Account Assignment**: New entities get default accounts automatically
3. **Flexible Configuration**: Organizations can customize account mappings
4. **Comprehensive Reporting**: All transactions can be traced through COA
5. **Audit Trail**: Clear visibility of which entities use which accounts
6. **Financial Accuracy**: Ensures all transactions are properly categorized

## Future Enhancements

The following entities are planned for COA integration in future releases:

- **GST/Tax Models**: Link tax codes to COA accounts (partially implemented)
- **Purchase Orders**: Link to purchase expense accounts
- **Sales Orders**: Link to sales income accounts
- **Inventory**: Link to inventory asset accounts
- **Assets**: Link to fixed asset accounts
- **Manufacturing**: Link to WIP and cost accounts
- **Payroll**: Link to salary expense and payroll payable accounts

## Troubleshooting

### Issue: Entities not getting auto-assigned COA accounts

**Solution**: Ensure default accounts exist by running the seeding script:
```bash
python -m app.scripts.seed_default_coa_accounts
```

### Issue: Migration fails with foreign key constraint error

**Solution**: Ensure ChartOfAccounts table exists and has the required accounts before running backfill migration.

### Issue: Cannot find linked entities for COA account

**Solution**: Verify the account ID is correct and belongs to the current organization. Use the entity links API endpoint to debug.

## API Reference

### Customer Endpoints
- `GET /api/customers/` - List customers (includes `receivable_account_id` in response)
- `POST /api/customers/` - Create customer (auto-assigns receivable account)
- `PUT /api/customers/{id}` - Update customer (can change receivable account)
- `GET /api/customers/{id}` - Get customer details (includes COA relationship)

### Vendor Endpoints
- `GET /api/vendors/` - List vendors (includes `payable_account_id` in response)
- `POST /api/vendors/` - Create vendor (auto-assigns payable account)
- `PUT /api/vendors/{id}` - Update vendor (can change payable account)
- `GET /api/vendors/{id}` - Get vendor details (includes COA relationship)

### COA Endpoints
- `GET /api/v1/erp/chart-of-accounts` - List all COA accounts
- `GET /api/v1/erp/chart-of-accounts/{id}` - Get COA account details
- `GET /api/v1/erp/chart-of-accounts/{id}/entity-links` - Get entities using this account
- `POST /api/v1/erp/chart-of-accounts` - Create new COA account
- `PUT /api/v1/erp/chart-of-accounts/{id}` - Update COA account

## Security Considerations

- All COA operations are organization-scoped
- Users can only access accounts within their organization
- Foreign key constraints ensure data integrity
- Soft deletes prevent orphaned references

## Performance Considerations

- Indexes created on all COA foreign key columns
- Entity links endpoint uses efficient queries
- Backfill migration processes in batches
- Default account queries are cached where possible

---

**Last Updated**: January 19, 2025
**Version**: 1.0
**Author**: FastAPI v1.6 Development Team
