# Inward Material Quality Check (QC) Integration Guide

## Overview
This document outlines the plan for integrating an Inward Material Quality Check (QC) modal into the GRN (Goods Receipt Note) workflow. This feature will allow users to perform quality checks on received items before accepting them.

## Current Implementation Status

### Completed (Current PR)
- ✅ UI button/hook added to GRN page for triggering QC modal
- ✅ Button is disabled in view mode
- ✅ Button location: In the "Edit" column of the GRN items table
- ✅ Backend already supports received_quantity, accepted_quantity, and rejected_quantity fields

### Location of QC Button
**File:** `/frontend/src/pages/vouchers/Purchase-Vouchers/grn.tsx`
**Line:** Approximately line 784-800 in the items table
```tsx
<Button
  size="small"
  variant="outlined"
  disabled={mode === 'view'}
  onClick={() => {
    // TODO: Trigger Inward Material QC modal for this item
    // This will be implemented in a future PR
    alert('QC Modal will be implemented in a future PR');
  }}
  sx={{ fontSize: 10, minWidth: 40, px: 1 }}
  title="Quality Check (Coming Soon)"
>
  QC
</Button>
```

## Future Implementation Plan

### 1. QC Modal Component
**File to Create:** `/frontend/src/components/InwardMaterialQCModal.tsx`

**Features:**
- Display item details (product name, ordered quantity, received quantity)
- Input fields for:
  - Accepted Quantity
  - Rejected Quantity
  - Rejection Reason (text area)
  - Quality Check Notes
  - QC Inspector Name
  - QC Date/Time (auto-filled)
- Photo upload capability for defects
- Pass/Fail status indicator
- Auto-validation: Accepted + Rejected ≤ Received

**Props:**
```typescript
interface InwardMaterialQCModalProps {
  open: boolean;
  onClose: () => void;
  itemData: {
    product_id: number;
    product_name: string;
    ordered_quantity: number;
    received_quantity: number;
    accepted_quantity: number;
    rejected_quantity: number;
    unit: string;
  };
  onSave: (qcData: QCData) => void;
}
```

### 2. Backend QC Data Model
**File to Create/Modify:** `/app/models/quality_check.py`

```python
class QualityCheckRecord(Base):
    __tablename__ = "quality_check_records"
    
    id = Column(Integer, primary_key=True)
    grn_id = Column(Integer, ForeignKey("goods_receipt_notes.id"))
    grn_item_id = Column(Integer, ForeignKey("goods_receipt_note_items.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    inspector_name = Column(String(255))
    inspection_date = Column(DateTime, default=datetime.utcnow)
    received_quantity = Column(Float)
    accepted_quantity = Column(Float)
    rejected_quantity = Column(Float)
    rejection_reason = Column(Text)
    qc_notes = Column(Text)
    qc_status = Column(String(50))  # "passed", "failed", "partial"
    defect_images = Column(JSON)  # Array of image URLs
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
```

### 3. Backend API Endpoint
**File to Create:** `/app/api/v1/quality_check.py`

**Endpoints:**
- `POST /quality-checks/` - Create QC record
- `GET /quality-checks/{grn_id}` - Get QC records for a GRN
- `PUT /quality-checks/{qc_id}` - Update QC record
- `GET /quality-checks/item/{item_id}` - Get QC record for specific item

### 4. Integration Points

#### GRN Page Integration
1. Replace the placeholder alert with actual modal opening
2. Pass item data to the QC modal
3. Update GRN item with QC results
4. Show QC status indicator on items that have been checked

#### Workflow Changes
1. **Optional QC**: QC can be performed but is not mandatory
2. **Pre-fill Quantities**: If QC is performed, auto-fill accepted/rejected quantities in GRN
3. **QC History**: Allow viewing QC records for any GRN item
4. **Notifications**: Send notifications when items are rejected

### 5. Reporting Requirements
- QC Dashboard showing rejection rates
- Product-wise rejection analysis
- Vendor quality score based on QC results
- Trend analysis of quality over time

### 6. Configuration Options
**File to Create/Modify:** Organization settings

Add settings for:
- Enable/Disable QC module
- Make QC mandatory or optional
- Set rejection thresholds
- Configure notification recipients for rejections

## Migration Plan

### Phase 1: Basic QC Modal (Future PR #1)
- Create QC modal component
- Basic QC data capture
- Save QC data to database
- Display QC status on GRN items

### Phase 2: Enhanced QC Features (Future PR #2)
- Photo upload for defects
- QC history view
- QC reports and analytics
- Vendor quality scoring

### Phase 3: Advanced QC Integration (Future PR #3)
- Automated quality rules
- Integration with vendor management
- QC mobile app for inspectors
- Real-time QC notifications

## Testing Requirements

### Unit Tests
- QC modal component rendering
- Validation rules (accepted + rejected ≤ received)
- QC data save/update operations

### Integration Tests
- QC modal integration with GRN page
- QC data flow from frontend to backend
- QC status display on GRN items

### E2E Tests
- Complete QC workflow from GRN creation to QC completion
- Photo upload and storage
- QC report generation

## Security Considerations
- Only authorized users can perform QC
- QC records are immutable (can be amended but not deleted)
- Audit trail for all QC operations
- Secure photo storage and access

## Notes for Implementation Team
1. The QC button is already present in the GRN items table
2. The backend already supports received_quantity, accepted_quantity, and rejected_quantity
3. The implementation should be backward compatible - GRNs without QC should work as before
4. Consider making QC optional initially, with ability to make it mandatory via settings
5. Ensure proper organization context isolation for QC data

## Related Files
- `/frontend/src/pages/vouchers/Purchase-Vouchers/grn.tsx` - GRN page with QC button
- `/app/api/v1/vouchers/goods_receipt_note.py` - GRN backend API
- `/app/models/vouchers/purchase.py` - GRN data models

## Contact
For questions or clarifications about this integration, refer to this document and the existing GRN implementation.
