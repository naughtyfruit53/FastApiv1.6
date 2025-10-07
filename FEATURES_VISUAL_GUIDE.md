# Visual Guide: New Features

This document provides a visual walkthrough of all implemented features.

## 🎯 Feature Overview

```
┌─────────────────────────────────────────────────────────────┐
│         7 Features Implemented in This PR                   │
├─────────────────────────────────────────────────────────────┤
│ 1. ✅ PDF File Naming (voucher numbers)                    │
│ 2. ✅ Org Super Admin Factory Reset (OTP-based)            │
│ 3. ✅ PO Kebab Menu - GRN Creation                         │
│ 4. ✅ Material Tracking for PO & Delivery Challan          │
│ 5. ✅ Inventory > Pending Orders UI                        │
│ 6. ✅ PO Index Color Coding                                │
│ 7. ✅ BOM Import/Export                                    │
└─────────────────────────────────────────────────────────────┘
```

---

## 1. PDF File Naming

### Before:
```
purchase_order_PO/2526/00004.pdf
```

### After:
```
PO-2526-00004.pdf
```

**Key Changes:**
- Uses voucher number directly
- Replaces slashes with dashes
- Cleaner, more professional filenames

---

## 2. Factory Reset (Already Implemented)

### Flow:
```
┌─────────────────┐
│ Org Super Admin │
└────────┬────────┘
         │
         ▼
┌──────────────────────┐
│ Settings > Reset Org │
└──────────┬───────────┘
           │
           ▼
┌─────────────────────┐
│ Request OTP (Email) │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Enter OTP Code     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Data Deleted ✓     │
└─────────────────────┘
```

---

## 3. PO Kebab Menu - GRN Creation

### Visual:
```
Purchase Order List
┌────────────────────────────────────┐
│ PO-2526-00001  │ Jan 15  │ ₹50,000 │ ⋮
│                                     │ │
│ PO-2526-00002  │ Jan 16  │ ₹75,000 │ ⋮
└────────────────────────────────────┘
                                       │
                Click ⋮ opens menu:   │
                                       ▼
              ┌──────────────────────────┐
              │ 📄 View Purchase Order   │
              │ ✏️  Edit Purchase Order   │
              │ 🗑️  Delete               │
              │ 🖨️  Print                │
              │ ✅ Create GRN  ← NEW!    │
              │ 🚚 Add Tracking ← NEW!   │
              └──────────────────────────┘
```

### Flow:
```
PO Kebab Menu → Create GRN → Navigate to GRN Page
                              (with po_id prefilled)
```

---

## 4. Material Tracking

### Tracking Dialog:
```
┌────────────────────────────────────────────┐
│ Add/Edit Tracking Details                  │
│ Purchase Order: PO-2526-00001              │
├────────────────────────────────────────────┤
│                                            │
│ Transporter/Courier Name:                 │
│ ┌────────────────────────────────────┐    │
│ │ Blue Dart                          │    │
│ └────────────────────────────────────┘    │
│                                            │
│ Tracking Number:                          │
│ ┌────────────────────────────────────┐    │
│ │ BD12345678                         │    │
│ └────────────────────────────────────┘    │
│                                            │
│ Tracking Link (Optional):                 │
│ ┌────────────────────────────────────┐    │
│ │ https://track.aftership.com/...   │    │
│ └────────────────────────────────────┘    │
│                                            │
│ [Generate AfterShip Tracking Link]        │
│                                            │
│              [Cancel]  [Save]              │
└────────────────────────────────────────────┘
```

### Database Schema:
```
purchase_orders
├── id
├── voucher_number
├── ...
├── transporter_name  ← NEW
├── tracking_number   ← NEW
└── tracking_link     ← NEW

delivery_challans
├── id
├── voucher_number
├── ...
├── transporter_name  ← NEW
├── tracking_number   ← NEW
└── tracking_link     ← NEW
```

---

## 5. Inventory > Pending Orders UI

### Page Layout:
```
┌─────────────────────────────────────────────────────────────┐
│ Pending Orders                                     🔄       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ Total    │  │ Total    │  │ With     │  │ Without  │  │
│  │ Orders   │  │ Value    │  │ Tracking │  │ Tracking │  │
│  │   10     │  │ ₹500K    │  │    7     │  │    3     │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
│                                                             │
│  Legend:                                                   │
│  🔴 No Tracking  🟡 Tracking Present, GRN Pending         │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ PO Number  │ Date    │ Vendor     │ Amount  │ Tracking │ ⚙ │
├─────────────────────────────────────────────────────────────┤
│🔴 PO-001   │ Jan 15  │ ABC Corp   │ ₹50,000 │ Not set  │ 🚚│
│🟡 PO-002   │ Jan 16  │ XYZ Ltd    │ ₹75,000 │ Blue Dart│ 🚚│
│🟡 PO-003   │ Jan 17  │ DEF Inc    │ ₹60,000 │ FedEx    │ 🚚│
│🔴 PO-004   │ Jan 18  │ GHI Co     │ ₹45,000 │ Not set  │ 🚚│
└─────────────────────────────────────────────────────────────┘
```

### Color Coding Logic:
```javascript
if (no_tracking_details) {
  color = RED    // 🔴 Urgent: Add tracking
}
else if (has_tracking && grn_pending) {
  color = YELLOW // 🟡 In transit: Create GRN when received
}
else if (grn_complete) {
  color = GREEN  // 🟢 Complete (excluded from this page)
}
```

---

## 6. PO Index Color Coding

### Before:
```
┌────────────────────────────────────┐
│ Voucher No. │ Date    │ Amount    │
├────────────────────────────────────┤
│ PO-001      │ Jan 15  │ ₹50,000   │
│ PO-002      │ Jan 16  │ ₹75,000   │
│ PO-003      │ Jan 17  │ ₹60,000   │
└────────────────────────────────────┘
```

### After (with color borders):
```
┌────────────────────────────────────┐
│ Voucher No. │ Date    │ Amount    │
├────────────────────────────────────┤
│🔴 PO-001    │ Jan 15  │ ₹50,000   │ ← Red border
│🟡 PO-002    │ Jan 16  │ ₹75,000   │ ← Yellow border
│🟢 PO-003    │ Jan 17  │ ₹60,000   │ ← Green border
└────────────────────────────────────┘
```

### Border Color Meanings:
- 🔴 **Red**: No tracking information
- 🟡 **Yellow**: Has tracking, GRN pending
- 🟢 **Green**: Complete/Closed

---

## 7. BOM Import/Export

### UI Layout:
```
┌─────────────────────────────────────────────────────────────┐
│ Bill of Materials (BOM)                                     │
│                                                             │
│ [Template] [Import] [Export] [+ Create BOM]                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  BOM Name  │ Version │ Output Item │ Qty │ Cost │ Status  │
├─────────────────────────────────────────────────────────────┤
│  Widget A  │  1.0    │ PROD-001    │  1  │ 1000 │ Active  │
│  Widget B  │  1.0    │ PROD-002    │  1  │1500  │ Active  │
│  Widget C  │  2.0    │ PROD-003    │  1  │ 2000 │ Active  │
└─────────────────────────────────────────────────────────────┘
```

### Excel Template Structure:
```
┌─────────────┬──────────────┬──────────┬─────────┬────────────┐
│ BOM Name    │ Output Item  │ Output   │ Version │ Component  │
│             │ Code/Name    │ Quantity │         │ Item       │
├─────────────┼──────────────┼──────────┼─────────┼────────────┤
│ Widget A    │ PROD-001     │    1     │   1.0   │ COMP-001   │
│ Widget A    │ PROD-001     │    1     │   1.0   │ COMP-002   │
│ Widget B    │ PROD-002     │    1     │   1.0   │ COMP-003   │
└─────────────┴──────────────┴──────────┴─────────┴────────────┘
```

### Import Flow:
```
1. Download Template
   ↓
2. Fill Excel with BOM data
   ↓
3. Click Import → Select file
   ↓
4. System validates:
   - Product references exist
   - No duplicate BOM names
   - All required fields present
   ↓
5. Success: BOMs created
   Or: Error list shown
```

### Export Result:
```
Downloaded file: BOM_Export.xlsx

Contains:
- All BOM headers
- All component details
- One row per component
- Ready to edit and re-import
```

---

## API Endpoints Summary

### Tracking APIs:
```
PUT  /api/v1/purchase-orders/{id}/tracking
GET  /api/v1/purchase-orders/{id}/tracking
PUT  /api/v1/delivery-challans/{id}/tracking
GET  /api/v1/delivery-challans/{id}/tracking
```

### BOM APIs:
```
GET  /api/v1/bom/export/template
POST /api/v1/bom/import
GET  /api/v1/bom/export
```

### Reports APIs:
```
GET  /api/v1/reports/pending-purchase-orders-with-grn-status
```

---

## User Journey Examples

### Journey 1: Adding Tracking to PO
```
1. User opens Purchase Order list
2. Clicks kebab menu (⋮) on a PO
3. Selects "Add/Edit Tracking Details"
4. Dialog opens
5. Enters: Transporter = "Blue Dart"
         Tracking No = "BD12345678"
6. Clicks "Generate AfterShip Tracking Link"
7. Link auto-populated
8. Clicks Save
9. Tracking now visible in:
   - PO list (color changes to yellow)
   - Pending orders page
   - Tracking link clickable
```

### Journey 2: Creating GRN from PO
```
1. User opens Purchase Order list
2. Clicks kebab menu (⋮) on a PO
3. Selects "Create GRN"
4. Redirected to GRN page
5. PO details pre-filled
6. User enters received quantities
7. Saves GRN
8. PO color changes to green (complete)
```

### Journey 3: Importing BOMs
```
1. User navigates to BOM page
2. Clicks "Template" button
3. Downloads BOM_Import_Template.xlsx
4. Opens in Excel
5. Fills in BOM data:
   - BOM Name: "Widget Assembly"
   - Output Item: "PROD-001"
   - Components: COMP-001, COMP-002, etc.
6. Saves Excel file
7. Returns to BOM page
8. Clicks "Import"
9. Selects filled Excel file
10. Success message: "Successfully imported 3 BOMs"
11. BOMs appear in table
```

### Journey 4: Viewing Pending Orders
```
1. User navigates to Inventory > Pending Orders
2. Sees summary cards:
   - 10 total orders
   - ₹500K total value
   - 7 with tracking
   - 3 without tracking
3. Scans table:
   - Red rows = needs tracking
   - Yellow rows = in transit
4. For red row:
   - Clicks 🚚 icon
   - Adds tracking details
   - Row turns yellow
5. For yellow row:
   - Clicks tracking link
   - Checks shipment status
   - When received, creates GRN
```

---

## Color Coding Reference

### Status Colors:
```
🔴 RED (#f44336)
   └─ No tracking information
   └─ Action needed: Add tracking details

🟡 YELLOW (#ff9800)
   └─ Has tracking information
   └─ GRN pending
   └─ Action needed: Create GRN when received

🟢 GREEN (#4caf50)
   └─ Complete/Closed
   └─ No action needed
```

---

## Quick Reference Commands

### Database Migration:
```bash
alembic upgrade head
```

### Check Tracking Field:
```sql
SELECT voucher_number, transporter_name, tracking_number
FROM purchase_orders
WHERE tracking_number IS NOT NULL;
```

### API Test (Add Tracking):
```bash
curl -X PUT "http://localhost:8000/api/v1/purchase-orders/123/tracking" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d "transporter_name=Blue Dart&tracking_number=BD12345678"
```

### API Test (Get Pending Orders):
```bash
curl -X GET "http://localhost:8000/api/v1/reports/pending-purchase-orders-with-grn-status" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Feature Interactions

```
┌──────────────────────────────────────────────────────────┐
│                    Feature Map                           │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Purchase Order                                          │
│       │                                                  │
│       ├─→ Create GRN ────────→ GRN Page                │
│       │                                                  │
│       ├─→ Add Tracking ───┐                             │
│       │                   │                             │
│       │                   ▼                             │
│       │          Tracking Dialog                        │
│       │                   │                             │
│       │                   ▼                             │
│       └─→ Shows in: ─────→ Pending Orders Page         │
│                           │                             │
│                           └─→ Color Coding              │
│                                                          │
│  BOM Management                                          │
│       │                                                  │
│       ├─→ Download Template                             │
│       │                                                  │
│       ├─→ Import Excel ──→ Validate ──→ Create BOMs    │
│       │                                                  │
│       └─→ Export Excel ──→ Download                     │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

---

## Success Metrics

✅ **All 7 features implemented**
✅ **Backend APIs created and tested**
✅ **Frontend UI components built**
✅ **Database migration prepared**
✅ **Documentation complete**
✅ **Color coding visible**
✅ **Excel import/export working**
✅ **Tracking integration functional**

---

## Next Steps for Users

1. **Run Migration**: Apply database changes
2. **Test Tracking**: Add tracking to a few POs
3. **View Pending Orders**: Check the new page
4. **Try BOM Import**: Download template and import
5. **Verify Color Coding**: Check PO index page
6. **Create GRN**: Use the new menu option

---

🎉 **All features ready for production use!**
