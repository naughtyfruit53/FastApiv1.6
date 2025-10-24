# Frontend Voucher Forms Update Guide

## Overview
All 29+ voucher forms need to be updated to support date-based voucher numbering with conflict detection. This guide provides a systematic approach and example implementation.

## Files to Update

### Financial Vouchers (7 forms)
1. `/frontend/src/pages/vouchers/Financial-Vouchers/payment-voucher.tsx`
2. `/frontend/src/pages/vouchers/Financial-Vouchers/receipt-voucher.tsx`
3. `/frontend/src/pages/vouchers/Financial-Vouchers/journal-voucher.tsx`
4. `/frontend/src/pages/vouchers/Financial-Vouchers/contra-voucher.tsx`
5. `/frontend/src/pages/vouchers/Financial-Vouchers/debit-note.tsx`
6. `/frontend/src/pages/vouchers/Financial-Vouchers/credit-note.tsx`
7. `/frontend/src/pages/vouchers/Financial-Vouchers/non-sales-credit-note.tsx`

### Pre-Sales Vouchers (3 forms)
8. `/frontend/src/pages/vouchers/Pre-Sales-Voucher/quotation.tsx`
9. `/frontend/src/pages/vouchers/Pre-Sales-Voucher/sales-order.tsx`
10. `/frontend/src/pages/vouchers/Pre-Sales-Voucher/proforma-invoice.tsx`

### Sales Vouchers (3 forms)
11. `/frontend/src/pages/vouchers/Sales-Vouchers/sales-voucher.tsx`
12. `/frontend/src/pages/vouchers/Sales-Vouchers/delivery-challan.tsx`
13. `/frontend/src/pages/vouchers/Sales-Vouchers/sales-return.tsx`

### Purchase Vouchers (4 forms)
14. `/frontend/src/pages/vouchers/Purchase-Vouchers/purchase-voucher.tsx`
15. `/frontend/src/pages/vouchers/Purchase-Vouchers/purchase-order.tsx`
16. `/frontend/src/pages/vouchers/Purchase-Vouchers/purchase-return.tsx`
17. `/frontend/src/pages/vouchers/Purchase-Vouchers/grn.tsx`

### Manufacturing Vouchers (8+ forms)
18. `/frontend/src/pages/vouchers/Manufacturing-Vouchers/work-order.tsx`
19. `/frontend/src/pages/vouchers/Manufacturing-Vouchers/stock-journal.tsx`
20. `/frontend/src/pages/vouchers/Manufacturing-Vouchers/material-receipt.tsx`
21. `/frontend/src/pages/vouchers/Manufacturing-Vouchers/job-card.tsx`
22. `/frontend/src/pages/vouchers/Manufacturing-Vouchers/manufacturing-journal.tsx`
23. `/frontend/src/pages/vouchers/Manufacturing-Vouchers/material-requisition.tsx`
24. `/frontend/src/pages/vouchers/Manufacturing-Vouchers/finished-good-receipt.tsx`
25. `/frontend/src/pages/vouchers/Manufacturing-Vouchers/production-order.tsx`

### Other Vouchers (3+ forms)
26. `/frontend/src/pages/vouchers/Others/rfq.tsx`
27. `/frontend/src/pages/vouchers/Others/dispatch-details.tsx`
28. `/frontend/src/pages/vouchers/Others/inter-department-voucher.tsx`

## Implementation Pattern

### Step 1: Import Required Components and Hooks
```typescript
import { useState, useEffect } from 'react';
import VoucherDateConflictModal from '../../../components/VoucherDateConflictModal';
import axios from 'axios';
```

### Step 2: Add State Variables
Add these state variables to your component:
```typescript
const [conflictInfo, setConflictInfo] = useState<any>(null);
const [showConflictModal, setShowConflictModal] = useState(false);
const [pendingDate, setPendingDate] = useState<string | null>(null);
```

### Step 3: Fetch Voucher Number When Date Changes
Add a useEffect to automatically fetch voucher number when date changes:
```typescript
useEffect(() => {
  const fetchVoucherNumber = async () => {
    const currentDate = watch('date');
    if (currentDate && mode === 'create') {
      try {
        // Fetch new voucher number based on date
        const response = await axios.get(
          `/api/v1/[voucher-endpoint]/next-number?voucher_date=${currentDate}`
        );
        setValue('voucher_number', response.data);
        
        // Check for backdated conflicts
        const conflictResponse = await axios.get(
          `/api/v1/[voucher-endpoint]/check-backdated-conflict?voucher_date=${currentDate}`
        );
        
        if (conflictResponse.data.has_conflict) {
          setConflictInfo(conflictResponse.data);
          setShowConflictModal(true);
          setPendingDate(currentDate);
        }
      } catch (error) {
        console.error('Error fetching voucher number:', error);
      }
    }
  };
  
  fetchVoucherNumber();
}, [watch('date'), mode]);
```

### Step 4: Add Conflict Modal Handlers
```typescript
const handleChangeDateToSuggested = () => {
  if (conflictInfo?.suggested_date) {
    setValue('date', conflictInfo.suggested_date.split('T')[0]);
    setShowConflictModal(false);
    setPendingDate(null);
  }
};

const handleProceedAnyway = () => {
  setShowConflictModal(false);
  // Keep the current date
};

const handleCancelConflict = () => {
  setShowConflictModal(false);
  if (pendingDate) {
    // Revert to previous date or clear
    setValue('date', '');
  }
  setPendingDate(null);
};
```

### Step 5: Add VoucherDateConflictModal Component
Add this near the end of your JSX, before the closing tags:
```typescript
<VoucherDateConflictModal
  open={showConflictModal}
  onClose={handleCancelConflict}
  conflictInfo={conflictInfo}
  onChangeDateToSuggested={handleChangeDateToSuggested}
  onProceedAnyway={handleProceedAnyway}
  voucherType="[Voucher Type Name]"
/>
```

### Step 6: Update Form Layout
Ensure date and voucher number fields are side by side (already implemented in most forms):
```typescript
<Grid container spacing={1}>
  <Grid item xs={6}>
    <TextField
      {...control.register('date')}
      label="Date"
      type="date"
      fullWidth
      InputLabelProps={{ shrink: true }}
    />
  </Grid>
  <Grid item xs={6}>
    <TextField
      {...control.register('voucher_number')}
      label="Voucher Number"
      fullWidth
      disabled
    />
  </Grid>
</Grid>
```

## Example Implementation for Payment Voucher

Here's a complete example for payment-voucher.tsx:

```typescript
// Add to imports
import VoucherDateConflictModal from '../../../components/VoucherDateConflictModal';
import axios from 'axios';

// Add state variables (inside component)
const [conflictInfo, setConflictInfo] = useState<any>(null);
const [showConflictModal, setShowConflictModal] = useState(false);
const [pendingDate, setPendingDate] = useState<string | null>(null);

// Add useEffect for date-based voucher number fetching
useEffect(() => {
  const fetchVoucherNumber = async () => {
    const currentDate = watch('date');
    if (currentDate && mode === 'create') {
      try {
        const response = await axios.get(
          `/api/v1/payment-vouchers/next-number?voucher_date=${currentDate}`
        );
        setValue('voucher_number', response.data);
        
        const conflictResponse = await axios.get(
          `/api/v1/payment-vouchers/check-backdated-conflict?voucher_date=${currentDate}`
        );
        
        if (conflictResponse.data.has_conflict) {
          setConflictInfo(conflictResponse.data);
          setShowConflictModal(true);
          setPendingDate(currentDate);
        }
      } catch (error) {
        console.error('Error fetching voucher number:', error);
      }
    }
  };
  
  fetchVoucherNumber();
}, [watch('date'), mode]);

// Add conflict handlers
const handleChangeDateToSuggested = () => {
  if (conflictInfo?.suggested_date) {
    setValue('date', conflictInfo.suggested_date.split('T')[0]);
    setShowConflictModal(false);
    setPendingDate(null);
  }
};

const handleProceedAnyway = () => {
  setShowConflictModal(false);
};

const handleCancelConflict = () => {
  setShowConflictModal(false);
  if (pendingDate) {
    setValue('date', '');
  }
  setPendingDate(null);
};

// Add modal component before closing return statement
return (
  <VoucherLayout>
    {/* ... existing form content ... */}
    
    <VoucherDateConflictModal
      open={showConflictModal}
      onClose={handleCancelConflict}
      conflictInfo={conflictInfo}
      onChangeDateToSuggested={handleChangeDateToSuggested}
      onProceedAnyway={handleProceedAnyway}
      voucherType="Payment Voucher"
    />
  </VoucherLayout>
);
```

## API Endpoint Mapping

| Form | API Endpoint |
|------|--------------|
| payment-voucher | /api/v1/payment-vouchers |
| receipt-voucher | /api/v1/receipt-vouchers |
| journal-voucher | /api/v1/journal-vouchers |
| contra-voucher | /api/v1/contra-vouchers |
| debit-note | /api/v1/debit-notes |
| credit-note | /api/v1/credit-notes |
| quotation | /api/v1/quotations |
| sales-order | /api/v1/sales-orders |
| proforma-invoice | /api/v1/proforma-invoices |
| sales-voucher | /api/v1/sales-vouchers |
| delivery-challan | /api/v1/delivery-challans |
| sales-return | /api/v1/sales-returns |
| purchase-voucher | /api/v1/purchase-vouchers |
| purchase-order | /api/v1/purchase-orders |
| purchase-return | /api/v1/purchase-returns |
| grn | /api/v1/goods-receipt-notes |
| inter-department-voucher | /api/v1/inter-department-vouchers |

## Testing Checklist

For each form, verify:
- [ ] Date field triggers voucher number update
- [ ] Backdated entries show conflict modal
- [ ] "Use Suggested Date" button works
- [ ] "Proceed Anyway" button works
- [ ] "Cancel & Review" button works
- [ ] Voucher number is read-only
- [ ] Date and voucher number are side by side
- [ ] No errors in console
- [ ] Proper error handling for API failures

## Notes
- The VoucherDateConflictModal component is already implemented and styled
- The backend endpoints are all ready and tested
- Each form may have slight variations - adapt the pattern as needed
- Always test in create mode first, then edit mode
- Check for any custom date field names (e.g., 'grn_date' in GRN forms)
