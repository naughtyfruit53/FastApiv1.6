# Voucher Form Reset Fix - Test Plan

## Summary
This document outlines the test plan for verifying the interstate/intrastate voucher creation fix.

## Issue Fixed
- **Problem**: Form resets when switching between interstate and intrastate vendors/customers
- **Root Cause**: `isIntrastate` memo dependency and effect dependency issues
- **Solution**: Cleaned up memo dependencies to prevent cascading re-renders

## Code Changes Summary
1. Removed `voucherData` from `isIntrastate` memo dependencies (line 302)
2. Removed `isIntrastate` from voucher data loading effect dependencies (line 862)
3. Removed static CGST/SGST/IGST rate setting during item loading (line 838-840)
4. Tax rates now computed dynamically in `computedItems` memo

## Test Scenarios

### 1. Create Mode - Intrastate Transaction (CGST + SGST)

**Setup:**
- Log in to the application
- Navigate to Sales Voucher or Purchase Voucher page
- Ensure mode is "Create" (new voucher)

**Test Steps:**
1. Verify voucher number is auto-populated (should be "SV-XXXX" or "PV-XXXX")
2. Select a customer/vendor from the SAME state as the company
3. Add a product to the items table
4. Add quantity and price

**Expected Results:**
- ✅ Form should NOT reset after selecting vendor/customer
- ✅ Voucher number should remain visible and unchanged
- ✅ CGST rate should be 9% (half of 18%)
- ✅ SGST rate should be 9% (half of 18%)
- ✅ IGST rate should be 0%
- ✅ Console should log: "Transaction is intrastate"

---

### 2. Create Mode - Interstate Transaction (IGST)

**Setup:**
- Log in to the application
- Navigate to Sales Voucher or Purchase Voucher page
- Ensure mode is "Create" (new voucher)

**Test Steps:**
1. Verify voucher number is auto-populated (should be "SV-XXXX" or "PV-XXXX")
2. Select a customer/vendor from a DIFFERENT state than the company
3. Add a product to the items table
4. Add quantity and price

**Expected Results:**
- ✅ Form should NOT reset after selecting vendor/customer
- ✅ Voucher number should remain visible and unchanged
- ✅ CGST rate should be 0%
- ✅ SGST rate should be 0%
- ✅ IGST rate should be 18%
- ✅ Console should log: "Transaction is interstate"

---

### 3. Switch Between Intrastate and Interstate

**Setup:**
- Log in to the application
- Navigate to Sales Voucher or Purchase Voucher page
- Mode: "Create"

**Test Steps:**
1. Verify voucher number is auto-populated
2. Select an INTRASTATE vendor/customer (same state)
3. Add 2-3 items with quantities and prices
4. Fill in notes or reference fields
5. Switch to an INTERSTATE vendor/customer (different state)
6. Observe the form

**Expected Results:**
- ✅ Form should NOT reset (all items should remain)
- ✅ Voucher number should remain unchanged
- ✅ Notes and reference fields should remain filled
- ✅ Item quantities and prices should remain unchanged
- ✅ Tax rates should update automatically:
  - From: CGST 9% + SGST 9%
  - To: IGST 18%
- ✅ Total amounts should recalculate correctly

---

### 4. Switch Back from Interstate to Intrastate

**Setup:**
- Continue from Test 3, with interstate vendor selected

**Test Steps:**
1. Switch back to an INTRASTATE vendor/customer
2. Observe the form

**Expected Results:**
- ✅ Form should NOT reset
- ✅ All items, quantities, prices remain
- ✅ Tax rates should update:
  - From: IGST 18%
  - To: CGST 9% + SGST 9%
- ✅ Total amounts recalculate correctly

---

### 5. Edit Mode - Load and Modify

**Setup:**
- Create a voucher (either interstate or intrastate)
- Navigate to edit mode for that voucher

**Test Steps:**
1. Open existing voucher in edit mode
2. Verify all data loads correctly
3. Change vendor/customer to different state type
4. Add/modify items

**Expected Results:**
- ✅ All existing data loads correctly
- ✅ Changing vendor doesn't reset other fields
- ✅ Tax rates update correctly
- ✅ Can save successfully

---

### 6. Financial Vouchers (Payment/Receipt)

**Setup:**
- Navigate to Payment Voucher or Receipt Voucher page
- Mode: "Create"

**Test Steps:**
1. Verify voucher number is populated
2. Select entity (could be Vendor, Customer, or Employee)
3. Enter amount
4. Switch entity type or entity

**Expected Results:**
- ✅ Form should NOT reset
- ✅ Voucher number remains
- ✅ Amount field remains filled
- ✅ Can successfully create voucher

---

### 7. Manufacturing Vouchers (Job Card)

**Setup:**
- Navigate to Job Card page
- Mode: "Create"

**Test Steps:**
1. Select vendor
2. Select manufacturing order
3. Add received outputs
4. Switch vendor

**Expected Results:**
- ✅ Form should NOT reset
- ✅ Manufacturing order selection remains
- ✅ Received outputs remain
- ✅ Can successfully create job card

---

## Browser Console Checks

Open browser console and verify the following logs appear:

1. When selecting intrastate entity:
   ```
   [useVoucherPage] Transaction is intrastate {
     companyStateCode: "XX",
     entityStateCode: "XX",
     entity: "Entity Name"
   }
   ```

2. When selecting interstate entity:
   ```
   [useVoucherPage] Transaction is interstate {
     companyStateCode: "XX",
     entityStateCode: "YY",
     entity: "Entity Name"
   }
   ```

3. Should NOT see repeated form reset logs

---

## Edge Cases to Test

### 8. Entity Without State Code

**Test Steps:**
1. Select a vendor/customer that has NO state_code
2. Observe behavior

**Expected Results:**
- ✅ Should NOT crash
- ✅ Should log error: "Entity state code or GST number is not available."
- ✅ Should default to intrastate (safe fallback)

---

### 9. Company Without State Code

**Test Steps:**
1. Ensure company state code is not set (edge case)
2. Try to create voucher

**Expected Results:**
- ✅ Should NOT crash
- ✅ Should log error: "Company state code is not available."
- ✅ Should default to intrastate (safe fallback)

---

### 10. Rapid Entity Switching

**Test Steps:**
1. Rapidly switch between 5-6 different vendors
2. Mix of intrastate and interstate
3. Observe performance and stability

**Expected Results:**
- ✅ No form resets
- ✅ No console errors
- ✅ Tax rates update correctly each time
- ✅ No performance degradation

---

## Success Criteria

All of the following must be true:

- ✅ No form resets when switching vendors/customers
- ✅ Voucher number always visible and persistent
- ✅ Tax rates (CGST/SGST/IGST) calculate correctly based on entity state
- ✅ All form data persists during entity changes
- ✅ No console errors during normal operation
- ✅ Can successfully create both intrastate and interstate vouchers
- ✅ Edit mode works correctly
- ✅ Financial vouchers work correctly
- ✅ Manufacturing vouchers work correctly

---

## Regression Testing

Ensure existing functionality still works:

- ✅ Voucher list displays correctly
- ✅ View mode shows voucher details
- ✅ Delete functionality works
- ✅ PDF generation works
- ✅ Search and filter work
- ✅ Pagination works
- ✅ Reference document selection works
- ✅ Discount calculations work

---

## Performance Validation

Monitor the following:

- Number of re-renders during entity selection (should be minimal)
- Console logs (should not have excessive logging)
- Memory usage (should remain stable)
- UI responsiveness (should remain smooth)

---

## Notes for Testers

1. **Test with real data**: Use actual vendors/customers with valid state codes
2. **Test all voucher types**: Sales, Purchase, Financial, Manufacturing
3. **Test on different browsers**: Chrome, Firefox, Safari, Edge
4. **Test on mobile**: Ensure responsive behavior works
5. **Check network tab**: Ensure no unnecessary API calls during entity switching

---

## Known Limitations

- This fix does not address backend validation issues
- This fix does not address duplicate voucher number issues
- This fix is frontend-only and assumes backend APIs work correctly

---

## Rollback Plan

If issues are found:

1. Revert commits 22aaaf6 and 2fd1c7b
2. Cherry-pick any other unrelated changes
3. Re-analyze the issue with additional logging

---

## Sign-off

**Tested By:** _________________  
**Date:** _________________  
**Result:** [ ] Pass [ ] Fail  
**Notes:** _________________________________________________
