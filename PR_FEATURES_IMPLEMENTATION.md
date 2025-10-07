# PR Features Implementation Guide

This document provides implementation details for the 7 features added in this PR.

## Feature Summary

### 1. PDF File Naming for Vouchers ✅
**Status:** Already implemented  
**Location:** Backend PDF generation service  
**Implementation:** PDF filenames use voucher numbers with slashes replaced by dashes (e.g., `OES-PO-2526-OCT-00001.pdf`). The backend sets the `Content-Disposition` header with the safe filename.

**Files:**
- `app/services/pdf_generation_service.py`
- `frontend/src/components/VoucherPDFButton.tsx`

---

### 2. Org Super Admin Factory Reset ✅
**Status:** Already implemented  
**Location:** Settings API  
**Implementation:** Organization super admin can trigger factory reset for their organization with OTP confirmation via system email.

**Files:**
- `app/api/settings.py`
- `app/services/reset_service.py`
- `app/services/otp_service.py`

**API Endpoints:**
- `POST /api/v1/settings/factory-reset/request-otp`
- `POST /api/v1/settings/factory-reset/confirm`

---

### 3. PO Kebab Menu - GRN Creation ✅
**Status:** Newly implemented  
**Implementation:** Added "Create GRN" option in Purchase Order kebab menu. Clicking navigates to GRN page with `po_id` query parameter for pre-filling.

**Files:**
- `frontend/src/components/VoucherContextMenu.tsx`
- `frontend/src/pages/vouchers/Purchase-Vouchers/purchase-order.tsx`

**Usage:**
```typescript
// Navigates to: /vouchers/Purchase-Vouchers/grn?po_id=123
router.push({
  pathname: '/vouchers/Purchase-Vouchers/grn',
  query: { po_id: voucher.id }
});
```

---

### 4. Material Tracking for PO and Delivery Challan ✅
**Status:** Newly implemented  
**Implementation:** Full tracking system with database fields, API endpoints, and UI dialog.

**Database Fields (both PurchaseOrder and DeliveryChallan models):**
- `transporter_name` (String)
- `tracking_number` (String)
- `tracking_link` (String)

**API Endpoints:**
```
PUT /api/v1/purchase-orders/{id}/tracking
GET /api/v1/purchase-orders/{id}/tracking
PUT /api/v1/delivery-challans/{id}/tracking
GET /api/v1/delivery-challans/{id}/tracking
```

**Files:**
- Backend:
  - `app/models/vouchers/purchase.py`
  - `app/models/vouchers/sales.py`
  - `app/api/v1/vouchers/purchase_order.py`
  - `app/api/v1/vouchers/delivery_challan.py`
  - `migrations/versions/add_tracking_fields_to_vouchers.py`
- Frontend:
  - `frontend/src/components/TrackingDetailsDialog.tsx`
  - `frontend/src/pages/vouchers/Purchase-Vouchers/purchase-order.tsx`
  - `frontend/src/pages/vouchers/Sales-Vouchers/delivery-challan.tsx`

**AfterShip Integration:**
The dialog includes a button to generate AfterShip tracking links using the pattern:
```
https://track.aftership.com/{courier-slug}/{tracking-number}
```

**Usage Example:**
```typescript
// Update tracking
await api.put(`/api/v1/purchase-orders/${id}/tracking`, null, {
  params: {
    transporter_name: "Blue Dart",
    tracking_number: "BD12345678",
    tracking_link: "https://track.aftership.com/blue-dart/BD12345678"
  }
});
```

---

### 5. Inventory > Pending Orders UI ✅
**Status:** Newly implemented  
**Implementation:** New page showing all POs where GRN is pending with color coding and summary cards.

**Color Coding:**
- 🔴 Red: No tracking details
- 🟡 Yellow: Has tracking, GRN pending
- 🟢 Green: Complete (excluded from this view)

**API Endpoint:**
```
GET /api/v1/reports/pending-purchase-orders-with-grn-status
```

**Response Schema:**
```json
{
  "orders": [
    {
      "id": 123,
      "voucher_number": "PO-2526-00001",
      "date": "2024-01-15",
      "vendor_name": "ABC Suppliers",
      "total_amount": 50000.00,
      "total_ordered_qty": 100,
      "total_received_qty": 50,
      "pending_qty": 50,
      "grn_count": 1,
      "has_tracking": true,
      "transporter_name": "Blue Dart",
      "tracking_number": "BD12345678",
      "tracking_link": "https://...",
      "color_status": "yellow",
      "days_pending": 5
    }
  ],
  "summary": {
    "total_orders": 10,
    "total_value": 500000.00,
    "with_tracking": 7,
    "without_tracking": 3
  }
}
```

**Files:**
- Backend: `app/api/reports.py`
- Frontend: `frontend/src/pages/inventory/pending-orders.tsx`

**Navigation:**
Access via: `/inventory/pending-orders`

---

### 6. PO Index Color Coding ✅
**Status:** Newly implemented  
**Implementation:** Purchase Order index table rows have colored left borders based on tracking and GRN status.

**Color Logic:**
```typescript
const getPOColorStatus = (voucher: any) => {
  if (voucher.status === 'completed' || voucher.status === 'closed') {
    return 'green'; // Complete
  } else if (voucher.tracking_number || voucher.transporter_name) {
    return 'yellow'; // Has tracking
  } else {
    return 'red'; // No tracking
  }
};
```

**Files:**
- `frontend/src/pages/vouchers/Purchase-Vouchers/purchase-order.tsx`

---

### 7. BOM Import/Export ✅
**Status:** Newly implemented  
**Implementation:** Excel-based import/export for Bill of Materials with template download.

**API Endpoints:**
```
GET /api/v1/bom/export/template  - Download sample template
POST /api/v1/bom/import          - Import BOMs from Excel
GET /api/v1/bom/export           - Export all BOMs to Excel
```

**Excel Template Columns:**
- BOM Name
- Output Item Code/Name
- Output Quantity
- Version
- Description
- Material Cost
- Labor Cost
- Overhead Cost
- Component Item Code/Name
- Quantity Required
- Unit
- Unit Cost
- Wastage %
- Is Optional
- Sequence
- Notes

**Files:**
- Backend: `app/api/v1/bom.py`
- Frontend: `frontend/src/pages/masters/bom.tsx`

**Import Process:**
1. Click "Template" to download sample Excel
2. Fill in BOM data following the template
3. Click "Import" and select your Excel file
4. System validates and imports BOMs
5. Success message shows count and any errors

**Export Process:**
1. Click "Export" button
2. Downloads Excel file with all BOMs
3. File named: `BOM_Export.xlsx`

**Technologies:**
- Backend: pandas, openpyxl
- Frontend: File upload with progress indication

---

## Database Migration

To apply the tracking fields migration:

```bash
cd /home/runner/work/FastApiv1.6/FastApiv1.6
alembic upgrade head
```

Or manually run:
```sql
ALTER TABLE purchase_orders ADD COLUMN transporter_name VARCHAR;
ALTER TABLE purchase_orders ADD COLUMN tracking_number VARCHAR;
ALTER TABLE purchase_orders ADD COLUMN tracking_link VARCHAR;

ALTER TABLE delivery_challans ADD COLUMN transporter_name VARCHAR;
ALTER TABLE delivery_challans ADD COLUMN tracking_number VARCHAR;
ALTER TABLE delivery_challans ADD COLUMN tracking_link VARCHAR;
```

---

## Testing Checklist

### 1. PDF Naming
- [ ] Download a PO PDF and verify filename is the voucher number
- [ ] Check that slashes are replaced with dashes

### 2. Factory Reset
- [ ] Login as org super admin
- [ ] Navigate to organization settings
- [ ] Request factory reset OTP
- [ ] Verify OTP email received
- [ ] Confirm reset with OTP
- [ ] Verify organization data deleted

### 3. PO Kebab Menu
- [ ] Open PO index page
- [ ] Click kebab menu on any PO
- [ ] Verify "Create GRN" option appears
- [ ] Click it and verify navigation to GRN page

### 4. Tracking Details
- [ ] Open PO kebab menu
- [ ] Click "Add/Edit Tracking Details"
- [ ] Enter transporter name and tracking number
- [ ] Click "Generate AfterShip Tracking Link"
- [ ] Verify link generated
- [ ] Save and verify tracking appears in PO list

### 5. Pending Orders
- [ ] Navigate to `/inventory/pending-orders`
- [ ] Verify summary cards show correct counts
- [ ] Verify POs with tracking are yellow
- [ ] Verify POs without tracking are red
- [ ] Click tracking link and verify it opens
- [ ] Click "Add/Edit Tracking" icon

### 6. PO Color Coding
- [ ] Open PO index page
- [ ] Verify colored borders on table rows
- [ ] Verify color matches tracking status

### 7. BOM Import/Export
- [ ] Navigate to BOM page
- [ ] Click "Template" and verify download
- [ ] Open template and add sample data
- [ ] Click "Import" and select file
- [ ] Verify success message
- [ ] Verify BOMs appear in table
- [ ] Click "Export" and verify download
- [ ] Open exported file and verify data

---

## API Documentation

### Tracking Endpoints

#### Update Purchase Order Tracking
```http
PUT /api/v1/purchase-orders/{id}/tracking
```

**Query Parameters:**
- `transporter_name` (optional): Name of courier/transporter
- `tracking_number` (optional): Tracking number
- `tracking_link` (optional): Full tracking URL

**Response:**
```json
{
  "message": "Tracking details updated successfully",
  "transporter_name": "Blue Dart",
  "tracking_number": "BD12345678",
  "tracking_link": "https://..."
}
```

#### Get Purchase Order Tracking
```http
GET /api/v1/purchase-orders/{id}/tracking
```

**Response:**
```json
{
  "transporter_name": "Blue Dart",
  "tracking_number": "BD12345678",
  "tracking_link": "https://..."
}
```

### BOM Endpoints

#### Download BOM Template
```http
GET /api/v1/bom/export/template
```

**Response:** Excel file download

#### Import BOMs
```http
POST /api/v1/bom/import
```

**Body:** `multipart/form-data`
- `file`: Excel file (.xlsx or .xls)

**Response:**
```json
{
  "message": "Successfully imported 5 BOMs",
  "imported_count": 5,
  "errors": []
}
```

#### Export BOMs
```http
GET /api/v1/bom/export
```

**Response:** Excel file download

---

## Security Considerations

1. **Tracking Details**: Only authenticated users in the same organization can view/edit tracking
2. **Factory Reset**: Requires OTP confirmation and org super admin role
3. **BOM Import**: Validates all references to products exist in the organization
4. **Pending Orders**: Filtered by organization context

---

## Performance Notes

1. **Pending Orders API**: Fetches all POs and checks GRN status - may be slow for large datasets. Consider pagination if needed.
2. **BOM Import**: Processes Excel file in memory - large files (>1000 rows) may require optimization.
3. **Color Coding**: Currently fetches tracking status on page load - no real-time updates.

---

## Future Enhancements

1. **Real-time Tracking**: Integrate AfterShip API for automatic status updates
2. **Webhook Support**: Get notified when shipment status changes
3. **Bulk Tracking**: Update tracking for multiple POs at once
4. **Advanced Filters**: Filter pending orders by vendor, date range, etc.
5. **Email Notifications**: Auto-notify when tracking is added or shipment delivered
6. **BOM Versioning**: Track changes to BOMs over time

---

## Support

For issues or questions:
1. Check API logs: `tail -f /var/log/fastapi.log`
2. Check database migrations: `alembic current`
3. Verify permissions: Ensure user has required role
4. Test API directly: Use Postman or curl

---

## Credits

Implementation by GitHub Copilot for naughtyfruit53/FastApiv1.6
