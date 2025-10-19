# Chart of Accounts Integration - Quick Reference

## 🚀 Quick Start

### 1. Run Migrations
```bash
alembic upgrade head
```

### 2. Seed Default Accounts
```bash
python -m app.scripts.seed_default_coa_accounts
```

### 3. Done! 
All new customers, vendors, and freight rates will auto-link to COA accounts.

---

## 📋 Default Accounts Reference

| Code | Account Name | Type | Used By |
|------|--------------|------|---------|
| 1120 | Accounts Receivable | ASSET | Customers |
| 2110 | Accounts Payable | LIABILITY | Vendors |
| 5210 | Freight Expense | EXPENSE | Freight Rates |
| 4100 | Sales Income | INCOME | Sales Orders* |
| 5110 | Purchase Expense | EXPENSE | Purchase Orders* |
| 1130 | Inventory | ASSET | Stock* |

\* Future integration

---

## 🔧 API Usage

### Creating Entities

#### Customer (Auto-assigned)
```python
POST /api/customers/
{
  "name": "ABC Corp",
  "contact_number": "1234567890",
  # ... other fields ...
  # receivable_account_id: auto-assigned to 1120
}
```

#### Customer (Custom Account)
```python
POST /api/customers/
{
  "name": "ABC Corp",
  "receivable_account_id": 456  # Custom account
  # ... other fields ...
}
```

#### Vendor (Auto-assigned)
```python
POST /api/vendors/
{
  "name": "Supplier Inc",
  "contact_number": "9876543210",
  # ... other fields ...
  # payable_account_id: auto-assigned to 2110
}
```

### Viewing COA Links

```python
# Get all entities using a specific COA account
GET /api/v1/erp/chart-of-accounts/{account_id}/entity-links

# Response:
{
  "account_code": "1120",
  "account_name": "Accounts Receivable",
  "entity_links": [
    {
      "entity_type": "Customer",
      "entity_id": 1,
      "entity_name": "ABC Corp",
      "link_type": "receivable"
    }
  ],
  "total_links": 1
}
```

---

## 🔍 Model Fields Reference

### Customer
```python
receivable_account_id: Optional[int]  # FK to chart_of_accounts.id
receivable_account: ChartOfAccounts   # Relationship
```

### Vendor
```python
payable_account_id: Optional[int]     # FK to chart_of_accounts.id
payable_account: ChartOfAccounts      # Relationship
```

### FreightRate
```python
freight_expense_account_id: int       # FK to chart_of_accounts.id
freight_expense_account: ChartOfAccounts  # Relationship
```

---

## 📊 Schema Reference

### Request Schemas
```python
CustomerCreate(receivable_account_id: Optional[int])
CustomerUpdate(receivable_account_id: Optional[int])
VendorCreate(payable_account_id: Optional[int])
VendorUpdate(payable_account_id: Optional[int])
```

### Response Schemas
```python
CustomerInDB(receivable_account_id: Optional[int])
VendorInDB(payable_account_id: Optional[int])
CustomerWithCOA(receivable_account: ChartOfAccountMinimal)
VendorWithCOA(payable_account: ChartOfAccountMinimal)
```

---

## 🧪 Testing

### Run COA Integration Tests
```bash
pytest tests/test_coa_integration.py -v
```

### Test Individual Functions
```python
# Test default account creation
pytest tests/test_coa_integration.py::test_create_default_coa_accounts -v

# Test customer COA integration
pytest tests/test_coa_integration.py::test_customer_coa_integration -v

# Test vendor COA integration
pytest tests/test_coa_integration.py::test_vendor_coa_integration -v
```

---

## 🐛 Troubleshooting

### Issue: Entities not auto-assigned COA accounts

**Solution**: Ensure default accounts exist
```bash
python -m app.scripts.seed_default_coa_accounts
```

### Issue: Migration fails

**Solution**: Check if ChartOfAccounts table exists
```sql
SELECT * FROM chart_of_accounts LIMIT 1;
```

### Issue: Foreign key constraint error

**Solution**: Ensure migrations run in order
```bash
alembic upgrade coa_integration_001
alembic upgrade coa_integration_002
```

---

## 📖 Full Documentation

- **Complete Guide**: `CHART_OF_ACCOUNTS_INTEGRATION_GUIDE.md`
- **Visual Summary**: `COA_INTEGRATION_VISUAL_SUMMARY.md`
- **Test Suite**: `tests/test_coa_integration.py`

---

## 🎯 Key Takeaways

1. ✅ COA accounts auto-assigned on entity creation
2. ✅ Custom accounts can be specified if needed
3. ✅ All operations are organization-scoped
4. ✅ Entity → COA links are queryable via API
5. ✅ Backwards compatible (no breaking changes)

---

**Last Updated**: January 19, 2025
**Version**: 1.0
