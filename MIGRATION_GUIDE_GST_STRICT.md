# Migration Guide: GST Strict State Code Enforcement

## Overview

This guide helps you migrate to the new strict GST state code enforcement system in FastAPI v1.6. The system now requires valid state codes for all GST-relevant voucher operations with **NO FALLBACK** logic.

## What Changed?

### Before (v1.5 and earlier)
- Missing organization state code would default to "27" (Maharashtra)
- Missing customer/vendor state codes would be ignored
- System would create vouchers even without proper GST state information
- GST calculations might be incorrect for inter-state transactions

### After (v1.6+)
- **STRICT ENFORCEMENT**: All state codes are required
- **NO FALLBACK**: System will NOT use default values
- **VALIDATION**: Voucher creation fails with HTTP 400 if state codes are missing
- **AUDIT LOGGING**: All GST calculations are logged with full context
- **CLEAR ERRORS**: Informative error messages guide users to fix data

## Affected Voucher Types

The following voucher types now require strict state code enforcement:

### Sales-Related (require customer state code)
- Sales Voucher, Quotation, Proforma Invoice
- Sales Order, Sales Return

### Purchase-Related (require vendor state code)
- Purchase Voucher, Purchase Order, Purchase Return

### Not Affected (no GST calculations)
- Financial vouchers: Payment, Receipt, Journal, Contra
- Movement vouchers: Delivery Challan, GRN
- Notes: Credit Note, Debit Note

## Pre-Migration Steps

### 1. Audit Your Database

```sql
-- Find records with missing state codes
SELECT COUNT(*) FROM organizations WHERE state_code IS NULL OR TRIM(state_code) = '';
SELECT COUNT(*) FROM customers WHERE state_code IS NULL OR TRIM(state_code) = '';
SELECT COUNT(*) FROM vendors WHERE state_code IS NULL OR TRIM(state_code) = '';
```

### 2. Update Missing State Codes

```sql
-- Update based on state name or GST number
UPDATE customers 
SET state_code = SUBSTRING(gst_number FROM 1 FOR 2)
WHERE gst_number IS NOT NULL AND LENGTH(gst_number) >= 15;
```

See `GST_CALCULATION_IMPROVEMENTS.md` for complete list of valid state codes (01-38, 97).

## Deployment

1. Backup database
2. Update all state codes
3. Deploy v1.6 code
4. Run migration: `alembic upgrade head`
5. Test voucher creation

## Error Handling

Expected HTTP 400 errors with clear messages:
- "Organization state code is required for GST calculation..."
- "Customer state code is required for GST calculation..."
- "Vendor state code is required for GST calculation..."

## Support

See `GST_CALCULATION_IMPROVEMENTS.md` for technical details and FAQ.
