# GRN and Purchase Order Test Plan

## Overview
This document outlines the comprehensive test plan for the GRN (Goods Receipt Note) and Purchase Order enhancements implemented in this PR.

## Changes Made

### 1. GRN Backend Fixes
- Fixed pending_quantity calculation to use cumulative delivered_quantity
- Improved error handling in GRN create and update operations

### 2. Purchase Order Backend Fixes
- Fixed grn_status calculation to use actual delivered_quantity
- Improved color-coding logic (green=complete, yellow=partial, white=pending)

### 3. GRN Frontend Enhancements
- Fixed PO dropdown to only remove fully completed POs (grn_status='complete')
- Added toast notification with link when GRN is created
- Added QC button placeholder for future QC integration
- Fixed vendor dropdown to show "Add New Vendor" at top, sorted A-Z

### 4. Purchase Order Frontend Enhancements
- Added delivered/pending quantity display in view/edit mode
- Fixed vendor dropdown to show "Add New Vendor" at top, sorted A-Z

### 5. Pending Orders Page
- Backend now never returns 500 errors
- Added proper error handling per PO
- Added org context fallback to user's organization_id

### 6. Vendor/Customer Dropdowns
- All dropdowns now show "Add New" option at the top
- All options sorted alphabetically (A-Z)

## Test Cases

### A. GRN Creation Tests

#### Test Case A1: Create GRN from Purchase Order
**Preconditions:**
- A Purchase Order exists with multiple line items
- User is logged in with appropriate permissions

**Steps:**
1. Navigate to GRN page
2. Select "Purchase Order" as voucher type
3. Select a PO from the dropdown
4. Verify items are auto-populated
5. Enter received quantities for each item
6. Enter accepted and rejected quantities
7. Verify: accepted + rejected ≤ received for each item
8. Save the GRN

**Expected Results:**
- Items are correctly populated from PO
- Validation prevents accepted + rejected > received
- Toast notification appears with link to created GRN
- PO items' delivered_quantity is updated
- PO items' pending_quantity is updated correctly

#### Test Case A2: Partial GRN from Purchase Order
**Steps:**
1. Create a GRN with partial quantities (e.g., 50 out of 100 ordered)
2. Check the PO dropdown after saving
3. Verify PO still appears in dropdown
4. Check PO color coding

**Expected Results:**
- PO should still be available in GRN dropdown (not removed)
- PO color should be yellow (partial)
- PO items show correct delivered_quantity and pending_quantity

#### Test Case A3: Complete GRN from Purchase Order
**Steps:**
1. Create a GRN with all remaining quantities
2. Check the PO dropdown after saving
3. Verify PO disappears from dropdown
4. Check PO color coding

**Expected Results:**
- PO should NOT appear in GRN dropdown (removed)
- PO color should be green (complete)
- PO items show pending_quantity = 0

#### Test Case A4: Multiple GRNs for Single PO
**Steps:**
1. Create first GRN with partial quantities (e.g., 40 out of 100)
2. Create second GRN with more quantities (e.g., 30 out of remaining 60)
3. Create third GRN with final quantities (e.g., 30 out of remaining 30)
4. Verify cumulative quantities

**Expected Results:**
- Each GRN correctly updates delivered_quantity
- Pending_quantity decreases correctly after each GRN
- Final GRN marks PO as complete (green)
- PO removed from dropdown only after complete

### B. GRN Edit Tests

#### Test Case B1: Edit Existing GRN
**Steps:**
1. Open an existing GRN in edit mode
2. Verify received_quantity and accepted_quantity are displayed
3. Modify quantities
4. Save the GRN

**Expected Results:**
- Existing quantities are displayed correctly
- Modified quantities are saved
- PO delivered_quantity is recalculated correctly
- Stock is adjusted correctly

#### Test Case B2: View GRN
**Steps:**
1. Open an existing GRN in view mode
2. Verify all quantities are displayed
3. Verify edit button is disabled

**Expected Results:**
- All quantities (ordered, received, accepted, rejected) are visible
- QC button is disabled in view mode
- All form fields are read-only

### C. Purchase Order Tests

#### Test Case C1: View PO with No GRN
**Steps:**
1. Create a new Purchase Order
2. View the PO in the list

**Expected Results:**
- PO row has white background (pending)
- grn_status = "pending"
- All items show delivered_quantity = 0
- All items show pending_quantity = ordered quantity

#### Test Case C2: View PO with Partial GRN
**Steps:**
1. Create a PO with multiple items
2. Create a GRN with partial quantities
3. View the PO in edit/view mode

**Expected Results:**
- PO row has yellow background (partial)
- grn_status = "partial"
- Items show correct delivered_quantity
- Items show correct pending_quantity (ordered - delivered)

#### Test Case C3: View PO with Complete GRN
**Steps:**
1. Create a PO
2. Create GRN(s) that fulfill all quantities
3. View the PO

**Expected Results:**
- PO row has green background (complete)
- grn_status = "complete"
- All items show pending_quantity = 0
- All items show delivered_quantity = ordered quantity

#### Test Case C4: PO Items Display in View/Edit Mode
**Steps:**
1. Open a PO with partial GRN in view or edit mode
2. Check the items table

**Expected Results:**
- Items table shows "Delivered" column
- Items table shows "Pending" column
- Values are displayed correctly with units
- Values match backend data

### D. Pending Orders Page Tests

#### Test Case D1: Display Pending Orders
**Steps:**
1. Navigate to Pending Orders page
2. Verify orders are displayed

**Expected Results:**
- Page never returns 500 error
- All pending POs are listed
- Each order shows: Product, Pending Qty, PO Number, PO Date
- Pending qty is calculated correctly (ordered - delivered across all GRNs)

#### Test Case D2: Error Handling in Pending Orders
**Steps:**
1. Create some invalid data (if possible)
2. Navigate to Pending Orders page

**Expected Results:**
- Page handles errors gracefully
- Returns empty result instead of 500 error
- Shows appropriate message to user
- Does not break due to single bad PO

#### Test Case D3: Organization Context
**Steps:**
1. Login as user in Organization A
2. Navigate to Pending Orders
3. Login as user in Organization B
4. Navigate to Pending Orders

**Expected Results:**
- Each user sees only their organization's pending orders
- No 500 errors due to missing org context
- Fallback to user's organization_id works correctly

### E. Vendor/Customer Dropdown Tests

#### Test Case E1: GRN Vendor Dropdown
**Steps:**
1. Open GRN page in create mode
2. Click on Vendor dropdown

**Expected Results:**
- "Add New Vendor..." appears at the top
- All other vendors are sorted alphabetically (A-Z)
- Clicking "Add New Vendor..." opens the vendor modal

#### Test Case E2: Purchase Order Vendor Dropdown
**Steps:**
1. Open Purchase Order page in create mode
2. Click on Vendor dropdown

**Expected Results:**
- "Add New Vendor..." appears at the top
- All other vendors are sorted alphabetically (A-Z)
- Clicking "Add New Vendor..." opens the vendor modal

#### Test Case E3: Customer Dropdowns (Sales Vouchers)
**Steps:**
1. Open any sales voucher page
2. Click on Customer dropdown/autocomplete

**Expected Results:**
- "Add Customer" option appears at the top
- All other customers are sorted alphabetically (A-Z)
- Clicking "Add Customer" opens the customer modal

### F. Add Vendor Modal Tests

#### Test Case F1: GST Search
**Steps:**
1. Open Add Vendor modal
2. Enter valid GSTIN
3. Click search button

**Expected Results:**
- Vendor details are auto-populated
- No silent failures
- Error messages displayed if search fails
- Toast notification on error

#### Test Case F2: Pincode Lookup
**Steps:**
1. Open Add Vendor modal
2. Enter valid 6-digit pincode

**Expected Results:**
- City, state, and state code are auto-populated
- No silent failures
- Error messages displayed if lookup fails

#### Test Case F3: Save Vendor
**Steps:**
1. Fill all required fields
2. Click Save

**Expected Results:**
- Vendor is saved successfully
- Toast notification confirms save
- Vendor appears in dropdown immediately
- No silent failures
- Error messages displayed if save fails

### G. Stock Display Tests

#### Test Case G1: Stock Display on Vouchers
**Steps:**
1. Open any voucher page (PO, Sales Order, etc.)
2. Add a product line item
3. Check stock display

**Expected Results:**
- Actual inventory stock is fetched from backend
- Stock is displayed with correct unit
- Stock color indicates level (red=below reorder, green=adequate)
- Stock is organization-specific

#### Test Case G2: Stock Display with Multiple Organizations
**Steps:**
1. Login as user in Org A
2. Check stock for a product
3. Login as user in Org B
4. Check stock for same product

**Expected Results:**
- Each organization sees only their own stock
- No mixing of stock data between organizations

### H. QC Integration Prep Tests

#### Test Case H1: QC Button Display
**Steps:**
1. Open GRN page in create mode
2. Add items from PO
3. Check items table

**Expected Results:**
- QC button is visible in Edit column
- Button is enabled in create/edit mode
- Button is disabled in view mode

#### Test Case H2: QC Button Click
**Steps:**
1. Open GRN in create mode
2. Click QC button

**Expected Results:**
- Alert shows "QC Modal will be implemented in a future PR"
- No errors or crashes
- Form remains functional

### I. Regression Tests

#### Test Case I1: Existing GRN Functionality
**Steps:**
1. Test all existing GRN operations
2. Verify no breaking changes

**Expected Results:**
- Create, edit, view, delete operations work correctly
- PDF generation works
- Email functionality works (if configured)

#### Test Case I2: Existing PO Functionality
**Steps:**
1. Test all existing PO operations
2. Verify no breaking changes

**Expected Results:**
- Create, edit, view, delete operations work correctly
- PDF generation works
- Email functionality works (if configured)
- Create GRN from PO workflow works

#### Test Case I3: Vendor/Customer Master Data
**Steps:**
1. Test vendor CRUD operations
2. Test customer CRUD operations

**Expected Results:**
- All operations work correctly
- Dropdowns update immediately
- Sorting and filtering work correctly

## Test Data Setup

### Required Test Data
1. **Organizations**: At least 2 organizations for isolation testing
2. **Users**: Users with different roles (admin, org_admin, standard_user)
3. **Vendors**: At least 10 vendors with varied names (for A-Z sorting test)
4. **Products**: Products with different stock levels
5. **Purchase Orders**: 
   - PO with no GRN
   - PO with partial GRN
   - PO with complete GRN
   - PO with multiple GRNs

## Performance Tests

### Test Case P1: Large Dataset Performance
**Steps:**
1. Create 100+ POs
2. Create 500+ GRNs
3. Navigate to pending orders page
4. Check PO dropdown in GRN page

**Expected Results:**
- Page loads within acceptable time (< 3 seconds)
- Dropdowns are responsive
- No memory leaks
- Pagination works correctly

## Browser Compatibility
Test on:
- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Mobile Responsiveness
Test on:
- Mobile phones (iOS and Android)
- Tablets
- Different screen sizes

## Known Limitations
1. QC modal is placeholder only - full implementation in future PR
2. Stock display depends on backend organization context being set correctly
3. Pincode lookup requires external API (may have rate limits)
4. GST search requires external API (may have rate limits)

## Test Sign-Off

| Test Area | Tester | Date | Status | Comments |
|-----------|--------|------|--------|----------|
| GRN Creation | | | | |
| GRN Edit/View | | | | |
| Purchase Order | | | | |
| Pending Orders | | | | |
| Vendor Dropdown | | | | |
| Customer Dropdown | | | | |
| Add Vendor Modal | | | | |
| Stock Display | | | | |
| QC Prep | | | | |
| Regression | | | | |
| Performance | | | | |
| Browser Compat | | | | |

## Notes
- All tests should be performed in both development and staging environments
- Document any deviations from expected results
- Critical bugs should block release
- Minor issues can be tracked as follow-up tasks
