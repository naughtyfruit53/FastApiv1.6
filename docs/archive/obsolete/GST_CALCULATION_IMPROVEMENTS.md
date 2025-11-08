# Smart GST Calculation Implementation

## Overview

This document describes the implementation of intelligent GST (Goods and Services Tax) calculation in the FastAPI v1.6 Business Suite. The system now automatically determines whether to apply CGST+SGST (for intra-state transactions) or IGST (for inter-state transactions) based on the state codes of the parties involved.

## Background

### Previous Implementation
- **Problem**: GST calculation was hardcoded to always apply CGST+SGST (intra-state)
- **Limitation**: Could not handle inter-state transactions correctly
- **Issue**: Manual adjustments were required for inter-state sales/purchases

### New Implementation
- **Solution**: Dynamic GST calculation based on state codes
- **Feature**: Automatically determines transaction type (intra-state vs inter-state)
- **Benefit**: Accurate tax calculation without manual intervention

## GST Rules in India

### Intra-State Transaction
When seller and buyer are in the **same state**:
- **CGST**: Central GST (50% of total GST rate)
- **SGST**: State GST (50% of total GST rate)
- **Example**: 18% GST = 9% CGST + 9% SGST

### Inter-State Transaction
When seller and buyer are in **different states**:
- **IGST**: Integrated GST (100% of total GST rate)
- **Example**: 18% GST = 18% IGST

## Implementation Details

### Core Component: GST Calculator

**File**: `app/utils/gst_calculator.py`

#### Key Function: `calculate_gst_amounts()`

```python
def calculate_gst_amounts(
    taxable_amount: float,
    gst_rate: float,
    company_state_code: str,
    customer_state_code: Optional[str] = None
) -> Dict[str, float]:
    """
    Calculate GST amounts based on state codes.
    
    Returns:
        {
            "cgst_amount": float,
            "sgst_amount": float,
            "igst_amount": float,
            "is_inter_state": bool
        }
    """
```

#### Logic Flow

1. **Normalize State Codes**: Convert to uppercase for comparison
2. **Determine Transaction Type**:
   - If `customer_state_code` is None or same as `company_state_code` → Intra-state
   - If `customer_state_code` differs from `company_state_code` → Inter-state
3. **Calculate Tax Amounts**:
   - **Intra-state**: CGST = SGST = (GST Rate / 2) × Taxable Amount
   - **Inter-state**: IGST = GST Rate × Taxable Amount
4. **Return Results**: Including inter-state flag for reference

### Integration Points

#### 1. Sales Voucher

**File**: `app/api/v1/vouchers/sales_voucher.py`

**Implementation**:
```python
# Get organization's state code
org_result = await db.execute(
    select(Organization.state_code).where(Organization.id == org_id)
)
company_state_code = org_result.scalar_one_or_none() or "27"

# Get customer's state code
customer_result = await db.execute(
    select(Customer.state_code).where(Customer.id == customer_id)
)
customer_state_code = customer_result.scalar_one_or_none()

# Calculate GST
gst_amounts = calculate_gst_amounts(
    taxable_amount=taxable,
    gst_rate=gst_rate,
    company_state_code=company_state_code,
    customer_state_code=customer_state_code
)
```

#### 2. Purchase Voucher

**File**: `app/api/v1/vouchers/purchase_voucher.py`

**Implementation**: Similar to sales voucher, but uses vendor state code instead of customer

```python
# Get vendor's state code
vendor_result = await db.execute(
    select(Vendor.state_code).where(Vendor.id == vendor_id)
)
vendor_state_code = vendor_result.scalar_one_or_none()

# Calculate GST (vendor is the "other party" in purchase)
gst_amounts = calculate_gst_amounts(
    taxable_amount=taxable,
    gst_rate=gst_rate,
    company_state_code=company_state_code,
    customer_state_code=vendor_state_code
)
```

## Data Requirements

### Organization Model
**Field**: `state_code` (String, Optional)
- Two-digit state code as per GST rules
- Example: "27" for Maharashtra, "29" for Karnataka

### Customer Model
**Field**: `state_code` (String, Required)
- Stored in customer address information
- Used for sales voucher GST calculation

### Vendor Model
**Field**: `state_code` (String, Required)
- Stored in vendor address information
- Used for purchase voucher GST calculation

## State Code Reference

The system includes validation for all Indian state codes:

| Code | State/UT |
|------|----------|
| 01 | Jammu and Kashmir |
| 02 | Himachal Pradesh |
| 03 | Punjab |
| 04 | Chandigarh |
| 05 | Uttarakhand |
| 06 | Haryana |
| 07 | Delhi |
| 08 | Rajasthan |
| 09 | Uttar Pradesh |
| 10 | Bihar |
| 11 | Sikkim |
| 12 | Arunachal Pradesh |
| 13 | Nagaland |
| 14 | Manipur |
| 15 | Mizoram |
| 16 | Tripura |
| 17 | Meghalaya |
| 18 | Assam |
| 19 | West Bengal |
| 20 | Jharkhand |
| 21 | Odisha |
| 22 | Chhattisgarh |
| 23 | Madhya Pradesh |
| 24 | Gujarat |
| 26 | Dadra and Nagar Haveli and Daman and Diu |
| 27 | Maharashtra |
| 29 | Karnataka |
| 30 | Goa |
| 31 | Lakshadweep |
| 32 | Kerala |
| 33 | Tamil Nadu |
| 34 | Puducherry |
| 35 | Andaman and Nicobar Islands |
| 36 | Telangana |
| 37 | Andhra Pradesh |
| 38 | Ladakh |
| 97 | Other Territory |

## Examples

### Example 1: Intra-State Transaction
**Scenario**: Mumbai company (Maharashtra - 27) sells to Pune customer (Maharashtra - 27)

**Input**:
- Taxable Amount: ₹10,000
- GST Rate: 18%
- Company State: 27
- Customer State: 27

**Output**:
- CGST: ₹900 (9%)
- SGST: ₹900 (9%)
- IGST: ₹0
- Total Tax: ₹1,800

### Example 2: Inter-State Transaction
**Scenario**: Mumbai company (Maharashtra - 27) sells to Bangalore customer (Karnataka - 29)

**Input**:
- Taxable Amount: ₹10,000
- GST Rate: 18%
- Company State: 27
- Customer State: 29

**Output**:
- CGST: ₹0
- SGST: ₹0
- IGST: ₹1,800 (18%)
- Total Tax: ₹1,800

### Example 3: Customer State Not Specified
**Scenario**: Company creates invoice without customer details (walk-in sale)

**Input**:
- Taxable Amount: ₹10,000
- GST Rate: 18%
- Company State: 27
- Customer State: None

**Output** (Defaults to intra-state):
- CGST: ₹900 (9%)
- SGST: ₹900 (9%)
- IGST: ₹0
- Total Tax: ₹1,800

## Utility Functions

### State Code Validation
```python
from app.utils.gst_calculator import validate_state_code

is_valid = validate_state_code("27")  # Returns True
is_valid = validate_state_code("99")  # Returns False
```

### State Name Lookup
```python
from app.utils.gst_calculator import get_state_name_from_code

state_name = get_state_name_from_code("27")  # Returns "Maharashtra"
```

### GST Summary for Multiple Items
```python
from app.utils.gst_calculator import get_gst_summary

items = [
    {"taxable_amount": 5000, "gst_rate": 18, "customer_state_code": "27"},
    {"taxable_amount": 3000, "gst_rate": 12, "customer_state_code": "29"}
]

summary = get_gst_summary(items, company_state_code="27")
# Returns:
# {
#     "total_cgst": 450.0,
#     "total_sgst": 450.0,
#     "total_igst": 360.0,
#     "has_mixed_transactions": True
# }
```

## Configuration

### Strict State Code Enforcement (v1.6+)
**BREAKING CHANGE**: As of version 1.6, state code enforcement is now **STRICT**:
- **NO FALLBACK**: System will NOT default to "27" (Maharashtra) or any other state code
- **REQUIRED**: Organization state_code MUST be set before creating any GST vouchers
- **VALIDATION**: All voucher endpoints validate state_code presence and return HTTP 400 if missing
- **AUDIT LOGGING**: All GST calculations log state_code usage for compliance tracking

### Enabling Company Profile Settings
The company profile (state_code) is part of the Organization model and is:
- **REQUIRED**: state_code field is NOT NULL in the database
- **Always enabled**: No entitlement check required
- **Accessible to**: Org Admin and Management roles
- **Editable via**: Organization settings API
- **Frontend Warning**: Banner displays on all voucher forms if state_code is missing

## Migration Path

### For Existing Organizations
1. **Audit**: Review organizations without state_code set
2. **Update**: Populate state_code from existing address data or GST number
3. **Validate**: Ensure all customers and vendors have state_code

### For Existing Vouchers
- **Historical Data**: No retroactive changes needed
- **New Vouchers**: Will automatically use smart GST calculation
- **Mixed Scenario**: Old vouchers remain unchanged, new vouchers benefit from improvement

## Testing

### Unit Tests
Test cases should cover:
1. Intra-state transaction (same state codes)
2. Inter-state transaction (different state codes)
3. Customer state code not provided (defaults to intra-state)
4. Invalid state codes (validation)
5. Edge cases (zero taxable amount, zero GST rate)

### Integration Tests
1. Create sales voucher with intra-state customer
2. Create sales voucher with inter-state customer
3. Create purchase voucher with intra-state vendor
4. Create purchase voucher with inter-state vendor
5. Verify PDF generation includes correct GST breakdown

## Benefits

### 1. Compliance
- **Accurate Tax Calculation**: Ensures compliance with Indian GST regulations
- **Automatic Determination**: Reduces errors from manual entry

### 2. User Experience
- **Simplified Process**: No need to manually select CGST/SGST vs IGST
- **Faster Invoicing**: Automatic calculation speeds up voucher creation

### 3. Reporting
- **Accurate Reports**: GST reports reflect actual transaction types
- **GSTR Compliance**: Data ready for GST return filing

### 4. Scalability
- **Multi-State Operations**: Supports businesses operating across multiple states
- **Branch Networks**: Handles complex scenarios with multiple locations

## Future Enhancements

### Potential Improvements

1. **SEZ Transactions**: Special handling for Special Economic Zones
2. **Export/Import**: Zero-rated GST for international transactions
3. **Composition Scheme**: Support for businesses under composition scheme
4. **Reverse Charge**: Implement reverse charge mechanism
5. **Place of Supply**: Consider place of supply for services
6. **E-Way Bill Integration**: Auto-generate e-way bills for inter-state shipments
7. **GSTIN Validation**: Validate GST numbers online
8. **Auto-State Detection**: Detect state from PIN code or GST number

## Support

### Common Issues

**Q: What if organization state code is not set?**
A: ⚠️ **STRICT ENFORCEMENT**: Voucher creation will FAIL with HTTP 400 error. You MUST update organization settings to set correct state code before creating any GST vouchers. Frontend displays a prominent warning banner.

**Q: What if customer/vendor doesn't have state code?**
A: ⚠️ **STRICT ENFORCEMENT**: Voucher creation will FAIL with HTTP 400 error. You MUST update customer/vendor master data before creating vouchers with them. Frontend displays a prominent warning banner.

**Q: Can I override the automatic calculation?**
A: Yes, if CGST/SGST/IGST amounts are explicitly provided in the API request, they are used as-is. However, state_code validation still applies.

**Q: Does this apply to all voucher types?**
A: Yes, as of v1.6, ALL GST-relevant voucher types enforce strict state_code requirements:
  - Sales vouchers, Purchase vouchers
  - Quotations, Proforma invoices
  - Sales orders, Purchase orders
  - Sales returns, Purchase returns
  - Delivery challans, Goods receipt notes
  - Credit notes, Debit notes
  - Payment/Receipt/Journal/Contra vouchers (where GST applies)

### Documentation References
- GST Calculator: `app/utils/gst_calculator.py`
- All Voucher Endpoints: `app/api/v1/vouchers/*.py`
- Audit Logging: `app/models/audit_log.py`
- Frontend Banner: `frontend/src/components/CompanyStateCodeBanner.tsx` (if applicable)

### Audit Trail
All GST calculations are now logged with:
- Timestamp of calculation
- Organization ID and state_code used
- Customer/Vendor ID and state_code used
- Transaction type (intra-state vs inter-state)
- Calculated CGST/SGST/IGST amounts
- Any validation errors or warnings

---

**Last Updated**: 2024-11-03
**Version**: 1.6.0
**Status**: Strict Enforcement Active - NO FALLBACK
