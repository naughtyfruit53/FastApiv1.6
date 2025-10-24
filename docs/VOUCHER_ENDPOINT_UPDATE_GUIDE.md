# Voucher Endpoint Update Implementation Guide

This document provides step-by-step instructions to update the remaining voucher endpoints for date-based numbering.

## Summary

**Core Changes Completed:**
- ✅ `VoucherNumberService` updated with `voucher_date` parameter
- ✅ `check_backdated_voucher_conflict` method added
- ✅ Purchase Order endpoint fully updated (reference implementation)
- ✅ Sales Voucher endpoint fully updated
- ✅ Tests created for date-based numbering logic

**Endpoints Updated (3/18):**
1. ✅ Purchase Order (`purchase_order.py`)
2. ✅ Sales Voucher (`sales_voucher.py`)
3. ⏳ Quotation (`quotation.py`) - Partially updated

**Endpoints Pending (15/18):**
1. ❌ Sales Order (`sales_order.py`)
2. ❌ Proforma Invoice (`proforma_invoice.py`)
3. ❌ Purchase Voucher (`purchase_voucher.py`)
4. ❌ Purchase Return (`purchase_return.py`)
5. ❌ Sales Return (`sales_return.py`)
6. ❌ Goods Receipt Note (`goods_receipt_note.py`)
7. ❌ Delivery Challan (`delivery_challan.py`)
8. ❌ Payment Voucher (`payment_voucher.py`)
9. ❌ Receipt Voucher (`receipt_voucher.py`)
10. ❌ Journal Voucher (`journal_voucher.py`)
11. ❌ Debit Note (`debit_note.py`)
12. ❌ Credit Note (`credit_note.py`)
13. ❌ Contra Voucher (`contra_voucher.py`)
14. ❌ Inter Department Voucher (`inter_department_voucher.py`)
15. ❌ Quotation (`quotation.py`) - Complete the update

---

## Implementation Steps for Each Voucher Endpoint

### Step 1: Add Import for dateutil parser

**Location:** Top of file, after other datetime imports

```python
from datetime import datetime
from dateutil import parser as date_parser
```

### Step 2: Update next-number Endpoint

**Find:** The `get_next_<voucher>_number` function

**Replace:**
```python
@router.get("/next-number", response_model=str)
async def get_next_<voucher>_number(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get the next available <voucher> number"""
    return await VoucherNumberService.generate_voucher_number_async(
        db, "<PREFIX>", current_user.organization_id, <VoucherModel>
    )
```

**With:**
```python
@router.get("/next-number", response_model=str)
async def get_next_<voucher>_number(
    voucher_date: Optional[str] = Query(None, description="Optional voucher date (ISO format) to generate number for specific period"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get the next available <voucher> number for a given date"""
    # Parse the voucher_date if provided
    date_to_use = None
    if voucher_date:
        try:
            date_to_use = date_parser.parse(voucher_date)
        except Exception:
            pass
    
    return await VoucherNumberService.generate_voucher_number_async(
        db, "<PREFIX>", current_user.organization_id, <VoucherModel>, voucher_date=date_to_use
    )
```

### Step 3: Add Conflict Check Endpoint

**Add immediately after the next-number endpoint:**

```python
@router.get("/check-backdated-conflict")
async def check_backdated_conflict(
    voucher_date: str = Query(..., description="Voucher date (ISO format) to check for conflicts"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Check if creating a voucher with the given date would create conflicts"""
    try:
        parsed_date = date_parser.parse(voucher_date)
        conflict_info = await VoucherNumberService.check_backdated_voucher_conflict(
            db, "<PREFIX>", current_user.organization_id, <VoucherModel>, parsed_date
        )
        return conflict_info
    except Exception as e:
        logger.error(f"Error checking backdated conflict: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
```

### Step 4: Update Create Endpoint

**In the create function, after extracting invoice_data/voucher_data:**

**Find:**
```python
        invoice_data = invoice.dict(exclude={'items'})
        invoice_data['created_by'] = current_user.id
        invoice_data['organization_id'] = current_user.organization_id
        
        if not invoice_data.get('voucher_number') or invoice_data['voucher_number'] == '':
            invoice_data['voucher_number'] = await VoucherNumberService.generate_voucher_number_async(
                db, "<PREFIX>", current_user.organization_id, <VoucherModel>
            )
```

**Replace with:**
```python
        invoice_data = invoice.dict(exclude={'items'})
        invoice_data['created_by'] = current_user.id
        invoice_data['organization_id'] = current_user.organization_id
        
        # Get the voucher date for numbering
        voucher_date = None
        if 'date' in invoice_data and invoice_data['date']:
            voucher_date = invoice_data['date'] if hasattr(invoice_data['date'], 'year') else None
        
        if not invoice_data.get('voucher_number') or invoice_data['voucher_number'] == '':
            # Generate voucher number based on the entered date
            invoice_data['voucher_number'] = await VoucherNumberService.generate_voucher_number_async(
                db, "<PREFIX>", current_user.organization_id, <VoucherModel>, voucher_date=voucher_date
            )
```

**Also update the duplicate check branch:**
```python
            if existing:
                invoice_data['voucher_number'] = await VoucherNumberService.generate_voucher_number_async(
                    db, "<PREFIX>", current_user.organization_id, <VoucherModel>, voucher_date=voucher_date
                )
```

---

## Voucher Prefix Reference

| Voucher Type | Prefix | Model Name |
|--------------|--------|------------|
| Purchase Order | PO | PurchaseOrder |
| Sales Voucher | SV | SalesVoucher |
| Quotation | QT | Quotation |
| Sales Order | SO | SalesOrder |
| Proforma Invoice | PI | ProformaInvoice |
| Purchase Voucher | PV | PurchaseVoucher |
| Purchase Return | PR | PurchaseReturn |
| Sales Return | SR | SalesReturn |
| Goods Receipt Note | GRN | GoodsReceiptNote |
| Delivery Challan | DC | DeliveryChallan |
| Payment Voucher | PAY | PaymentVoucher |
| Receipt Voucher | REC | ReceiptVoucher |
| Journal Voucher | JV | JournalVoucher |
| Debit Note | DN | DebitNote |
| Credit Note | CN | CreditNote |
| Contra Voucher | CV | ContraVoucher |
| Inter Department | IDV | InterDepartmentVoucher |

---

## Testing Each Update

After updating each endpoint, test with:

```bash
# Test next-number with date
curl -X GET "http://localhost:8000/api/v1/<voucher-endpoint>/next-number?voucher_date=2025-09-15" \
  -H "Authorization: Bearer <token>"

# Test conflict check
curl -X GET "http://localhost:8000/api/v1/<voucher-endpoint>/check-backdated-conflict?voucher_date=2025-09-15" \
  -H "Authorization: Bearer <token>"

# Test create with backdated voucher
curl -X POST "http://localhost:8000/api/v1/<voucher-endpoint>/" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2025-09-15T10:00:00Z",
    "customer_id": 1,
    "items": [...]
  }'
```

---

## Frontend Updates Needed

### 1. Swap Date/Number Positions in Forms

**Current Layout (Example):**
```
[Voucher Number] [Date Picker]
```

**New Layout:**
```
[Date Picker] [Voucher Number]
```

Files to update:
- `frontend/src/pages/vouchers/Purchase-Vouchers/purchase-order.tsx`
- `frontend/src/pages/vouchers/Sales-Vouchers/sales-voucher.tsx`
- ... (all voucher form pages)

**Implementation:**
```tsx
// In the form grid, swap the order:
<Grid container spacing={2}>
  {/* Date first */}
  <Grid item xs={12} md={6}>
    <TextField
      label="Date"
      type="date"
      value={date}
      onChange={handleDateChange}
      fullWidth
    />
  </Grid>
  
  {/* Voucher number second */}
  <Grid item xs={12} md={6}>
    <TextField
      label="Voucher Number"
      value={voucherNumber}
      disabled
      fullWidth
    />
  </Grid>
</Grid>
```

### 2. Add Conflict Detection Hook

Create `frontend/src/hooks/useVoucherDateConflict.ts`:

```typescript
import { useState, useEffect } from 'react';
import api from '../lib/api';

export const useVoucherDateConflict = (
  voucherType: string,
  selectedDate: Date | null
) => {
  const [conflictInfo, setConflictInfo] = useState<any>(null);
  const [isChecking, setIsChecking] = useState(false);

  useEffect(() => {
    if (!selectedDate) return;

    const checkConflict = async () => {
      setIsChecking(true);
      try {
        const response = await api.get(
          `/api/v1/${voucherType}/check-backdated-conflict`,
          {
            params: {
              voucher_date: selectedDate.toISOString()
            }
          }
        );
        setConflictInfo(response.data);
      } catch (error) {
        console.error('Error checking conflict:', error);
      } finally {
        setIsChecking(false);
      }
    };

    const debounce = setTimeout(checkConflict, 500);
    return () => clearTimeout(debounce);
  }, [selectedDate, voucherType]);

  return { conflictInfo, isChecking };
};
```

### 3. Add Conflict Notification Modal

Create `frontend/src/components/VoucherDateConflictModal.tsx`:

```typescript
import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Alert,
  Box
} from '@mui/material';
import WarningIcon from '@mui/icons-material/Warning';
import { format } from 'date-fns';

interface VoucherDateConflictModalProps {
  open: boolean;
  onClose: () => void;
  conflictInfo: any;
  onChangeDateToSuggested: () => void;
  onProceedAnyway: () => void;
}

const VoucherDateConflictModal: React.FC<VoucherDateConflictModalProps> = ({
  open,
  onClose,
  conflictInfo,
  onChangeDateToSuggested,
  onProceedAnyway
}) => {
  if (!conflictInfo?.has_conflict) return null;

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>
        <Box display="flex" alignItems="center" gap={1}>
          <WarningIcon color="warning" />
          <Typography variant="h6">
            Back-dated Voucher Conflict
          </Typography>
        </Box>
      </DialogTitle>
      
      <DialogContent>
        <Alert severity="warning" sx={{ mb: 2 }}>
          You are creating a voucher with a date earlier than {conflictInfo.later_voucher_count} 
          existing voucher(s) in the same period ({conflictInfo.period}).
        </Alert>
        
        <Typography variant="body2" paragraph>
          This will create a numbering discrepancy where vouchers with later dates 
          have earlier voucher numbers.
        </Typography>
        
        <Typography variant="body2" paragraph>
          <strong>Suggested Action:</strong> Change the voucher date to{' '}
          {format(new Date(conflictInfo.suggested_date), 'MMM dd, yyyy')} 
          (the date of the last voucher in this period).
        </Typography>
        
        <Typography variant="body2" color="text.secondary">
          Or proceed with the entered date if this is intentional.
        </Typography>
      </DialogContent>
      
      <DialogActions>
        <Button onClick={onClose}>
          Cancel
        </Button>
        <Button 
          onClick={onChangeDateToSuggested}
          variant="contained"
          color="primary"
        >
          Change to Suggested Date
        </Button>
        <Button 
          onClick={onProceedAnyway}
          variant="outlined"
          color="warning"
        >
          Proceed with Current Date
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default VoucherDateConflictModal;
```

### 4. Integrate in Voucher Forms

In each voucher form component (e.g., `purchase-order.tsx`):

```typescript
import { useVoucherDateConflict } from '../../../hooks/useVoucherDateConflict';
import VoucherDateConflictModal from '../../../components/VoucherDateConflictModal';

// Inside component:
const [showConflictModal, setShowConflictModal] = useState(false);
const { conflictInfo, isChecking } = useVoucherDateConflict(
  'purchase-orders',
  watch('date')
);

// Show modal when conflict detected
useEffect(() => {
  if (conflictInfo?.has_conflict) {
    setShowConflictModal(true);
  }
}, [conflictInfo]);

// In JSX:
<VoucherDateConflictModal
  open={showConflictModal}
  onClose={() => setShowConflictModal(false)}
  conflictInfo={conflictInfo}
  onChangeDateToSuggested={() => {
    setValue('date', new Date(conflictInfo.suggested_date));
    setShowConflictModal(false);
  }}
  onProceedAnyway={() => {
    setShowConflictModal(false);
  }}
/>
```

---

## Rollout Strategy

1. **Phase 1**: Update all backend endpoints (16 remaining)
2. **Phase 2**: Update all frontend forms to swap date/number positions
3. **Phase 3**: Add conflict detection hooks and modals
4. **Phase 4**: Comprehensive testing across all voucher types
5. **Phase 5**: Deploy with feature flag (can roll back if issues)

---

## Validation Checklist

For each voucher type:
- [ ] Backend: Imports include `dateutil.parser`
- [ ] Backend: `next-number` endpoint accepts `voucher_date` parameter
- [ ] Backend: `check-backdated-conflict` endpoint exists
- [ ] Backend: Create endpoint passes `voucher_date` to numbering service
- [ ] Frontend: Date field appears before voucher number field
- [ ] Frontend: Conflict detection hook integrated
- [ ] Frontend: Conflict modal appears for back-dated entries
- [ ] Testing: Monthly period numbering works correctly
- [ ] Testing: Quarterly period numbering works correctly
- [ ] Testing: Annual period numbering works correctly
- [ ] Testing: Conflict detection identifies later vouchers
- [ ] Testing: Suggested date is correct

---

## Notes

- The core service (`VoucherNumberService`) is already fully updated and tested
- Each endpoint update is independent and can be done incrementally
- The pattern is consistent across all voucher types
- Frontend changes can be done in parallel with backend updates
- Existing vouchers are not affected (backward compatible)

---

**Last Updated**: October 24, 2025  
**Status**: 3/18 endpoints updated, Core service complete, Tests created
