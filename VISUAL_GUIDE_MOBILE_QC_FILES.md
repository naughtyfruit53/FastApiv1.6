# Visual Guide - Mobile Compatibility, QC Integration, and Product File Features

## Feature 1: Product File Attachments

### Add Product Modal - New Tab Layout

```
┌────────────────────────────────────────────────────────────┐
│  ✕  Add New Product / Edit Product                         │
├────────────────────────────────────────────────────────────┤
│  [Basic Information]  [Files]  ← New tabs                  │
├────────────────────────────────────────────────────────────┤
│                                                              │
│  Tab 1: Basic Information (Existing Form)                   │
│  ┌─────────────────┬─────────────────┐                      │
│  │ Product Name *  │ HSN Code  🔍   │                      │
│  ├─────────────────┼─────────────────┤                      │
│  │ Part Number     │ Unit *          │                      │
│  ├─────────────────┼─────────────────┤                      │
│  │ Unit Price *    │ GST Rate (%) *  │                      │
│  ├─────────────────┼─────────────────┤                      │
│  │ Reorder Level   │                 │                      │
│  ├─────────────────┴─────────────────┤                      │
│  │ Description (multiline)           │                      │
│  │                                   │                      │
│  ├─────────────────┬─────────────────┤                      │
│  │ ☐ GST Inclusive │ ☐ Manufactured  │                      │
│  └─────────────────┴─────────────────┘                      │
│                                                              │
│                                    [Cancel]  [Add Product]  │
└────────────────────────────────────────────────────────────┘
```

### Product Files Tab (Only in Edit Mode)

```
┌────────────────────────────────────────────────────────────┐
│  ✕  Edit Product                                            │
├────────────────────────────────────────────────────────────┤
│  [Basic Information]  [Files] ← Active                      │
├────────────────────────────────────────────────────────────┤
│                                                              │
│  Product Files                          🏷️ 2/5              │
│  ┌────────────────────────────────────────────────────┐    │
│  │                      ☁️                            │    │
│  │      Click to upload or drag and drop files here   │    │
│  │      Maximum file size: 10MB • Maximum 5 files     │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  Uploaded Files:                                             │
│  ┌────────────────────────────────────────────────────┐    │
│  │ 📄 Product_Specs.pdf                    ⬇️  🗑️     │    │
│  │ 156 KB • Jan 15, 2025                              │    │
│  ├────────────────────────────────────────────────────┤    │
│  │ 🖼️ Product_Image.jpg                    ⬇️  🗑️     │    │
│  │ 2.3 MB • Jan 15, 2025                              │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│                                    [Cancel]  [Update Product]│
└────────────────────────────────────────────────────────────┘
```

**Key Features:**
- ✅ Tab navigation: Basic Info | Files
- ✅ Files tab disabled for new products (save first)
- ✅ Drag-and-drop upload area
- ✅ File count indicator (X/5)
- ✅ File type icons (📄 PDF, 🖼️ Image, 📊 Excel, 📝 Word)
- ✅ Download (⬇️) and Delete (🗑️) buttons
- ✅ File size and upload date display

---

## Feature 2: Inward Material QC Modal

### GRN Page - QC Button Location

```
Items Table:
┌────────────────────────────────────────────────────────────┐
│ Product    │ Ordered │ Received │ Accepted │ Rejected │ Edit│
├────────────┼─────────┼──────────┼──────────┼──────────┼─────┤
│ Widget A   │   100   │    100   │    95    │     5    │ ✏️ QC│
│ Widget B   │   200   │    200   │   200    │     0    │ ✏️ QC│ ← QC button
└────────────┴─────────┴──────────┴──────────┴──────────┴─────┘
```

### QC Modal - Full View

```
┌──────────────────────────────────────────────────────────────┐
│  ✕  Inward Material Quality Check          ✅ PASS          │
├──────────────────────────────────────────────────────────────┤
│                                                                │
│  Item Details                                                  │
│  ┌──────────────────────────────────────────────────────────┐│
│  │ Product: Widget A                  Unit: PCS             ││
│  │ Ordered: 100    Received: 100    Pending QC: 0          ││
│  └──────────────────────────────────────────────────────────┘│
│                                                                │
│  Inspection Details                                            │
│  ┌────────────────────┬────────────────────┐                  │
│  │ Inspection Date *  │ Inspector Name *   │                  │
│  │ 2025-01-15        │ John Doe           │                  │
│  └────────────────────┴────────────────────┘                  │
│                                                                │
│  Quantities                                                    │
│  ┌────────────────────┬────────────────────┐                  │
│  │ Accepted Quantity *│ Rejected Quantity  │                  │
│  │       95          │         5          │                  │
│  └────────────────────┴────────────────────┘                  │
│                                                                │
│  QC Result (Auto-calculated)                                   │
│  ┌──────────────────────────────────────────┐                │
│  │ ⚠️ Partial (Some Rejected)   ▼         │                │
│  └──────────────────────────────────────────┘                │
│                                                                │
│  Rejection Reason * (Required when rejected > 0)               │
│  ┌──────────────────────────────────────────────────────────┐│
│  │ 5 units damaged during shipping, packaging insufficient  ││
│  └──────────────────────────────────────────────────────────┘│
│                                                                │
│  Measurements (Optional)                                       │
│  ┌──────────────────────────────────────────────────────────┐│
│  │ Dimensions checked: 10x10x10 cm (spec: 10x10x10 cm)      ││
│  └──────────────────────────────────────────────────────────┘│
│                                                                │
│  Additional Remarks                                            │
│  ┌──────────────────────────────────────────────────────────┐│
│  │ Quality otherwise acceptable, recommend better packaging  ││
│  └──────────────────────────────────────────────────────────┘│
│                                                                │
│  ────────────────────────────────────────────────────────────│
│                                                                │
│  Attach Photos/Documents (Optional, max 5 files, 5MB each)    │
│  [Upload Files]                                                │
│                                                                │
│  Uploaded Files:                                               │
│  ┌──────────────────────────────────────────────────────────┐│
│  │ 📷 damaged_items.jpg              🗑️                    ││
│  │ 523 KB                                                    ││
│  └──────────────────────────────────────────────────────────┘│
│                                                                │
│                              [Cancel]  [Save Quality Check]   │
└──────────────────────────────────────────────────────────────┘
```

**Key Features:**
- ✅ QC result chip at top (✅ PASS, ⚠️ PARTIAL, ❌ FAIL)
- ✅ Item details summary (read-only)
- ✅ Inspection date and inspector fields
- ✅ Accepted/rejected quantity inputs with validation
- ✅ Auto-calculated QC result (disabled dropdown)
- ✅ Required rejection reason when items rejected
- ✅ Optional measurements and remarks
- ✅ File upload for defect photos (up to 5 files)
- ✅ Real-time validation (quantities can't exceed received)

### QC Result Auto-Calculation Logic

```
If rejected_quantity = 0:
    QC Result = ✅ PASS (All Accepted)

Else if accepted_quantity = 0:
    QC Result = ❌ FAIL (All Rejected)

Else:
    QC Result = ⚠️ PARTIAL (Some Rejected)
```

---

## Feature 3: Mobile Compatibility

### Mobile View - Touch-Friendly Design

```
Mobile Product List (iPhone 12 - 390x844):

┌─────────────────────┐
│  ☰  Products    🔍  │
├─────────────────────┤
│                     │
│  [+ Add Product]    │← Touch target: 48px
│                     │
│  ┌─────────────────┐│
│  │ Widget A        ││
│  │ ₹100 • PCS      ││
│  │ HSN: 8471       ││
│  │        ✏️  🗑️   ││← Touch targets: 48px
│  └─────────────────┘│
│  ┌─────────────────┐│
│  │ Widget B        ││
│  │ ₹200 • KG       ││
│  │ HSN: 8472       ││
│  │        ✏️  🗑️   ││
│  └─────────────────┘│
│                     │
│  ┌─────────────────┐│
│  │ Widget C        ││
│  │ ₹150 • MTR      ││
│  │ HSN: 8473       ││
│  │        ✏️  🗑️   ││
│  └─────────────────┘│
│                     │
└─────────────────────┘
```

**Mobile-Specific Features:**
- ✅ Touch-action: manipulation (prevents double-tap zoom)
- ✅ Viewport: width=device-width, initial-scale=1
- ✅ Touch targets: Minimum 44px (recommended 48px)
- ✅ Single-column layout on mobile
- ✅ Large, touch-friendly buttons
- ✅ No horizontal scrolling
- ✅ Responsive tables adapt to mobile

### Mobile QC Modal

```
Mobile QC Modal (iPhone 12):

┌─────────────────────┐
│ ✕  QC    ⚠️ PARTIAL│
├─────────────────────┤
│                     │
│ Product: Widget A   │
│ Received: 100 PCS   │
│                     │
│ Inspection Date *   │
│ ┌─────────────────┐ │
│ │ 2025-01-15      │ │
│ └─────────────────┘ │
│                     │
│ Inspector Name *    │
│ ┌─────────────────┐ │
│ │ John Doe        │ │
│ └─────────────────┘ │
│                     │
│ Accepted Qty *      │
│ ┌─────────────────┐ │
│ │ 95             │ │← 48px tall
│ └─────────────────┘ │
│                     │
│ Rejected Qty        │
│ ┌─────────────────┐ │
│ │ 5              │ │
│ └─────────────────┘ │
│                     │
│ Rejection Reason *  │
│ ┌─────────────────┐ │
│ │ Damaged...      │ │
│ │                 │ │
│ └─────────────────┘ │
│                     │
│ [Upload Files]      │
│                     │
│ ┌─────────────────┐ │
│ │ 📷 damage.jpg   │ │
│ │ 523 KB      🗑️ │ │
│ └─────────────────┘ │
│                     │
│ [Cancel]  [Save QC] │← 48px tall
└─────────────────────┘
```

**Mobile Optimizations:**
- ✅ Full-screen modal on mobile
- ✅ Scrollable content area
- ✅ Large input fields (48px tall)
- ✅ Touch-friendly buttons
- ✅ Bottom action buttons (Cancel, Save)
- ✅ Auto-focus on first input
- ✅ Keyboard-friendly (shows number pad for quantity)

---

## Responsive Breakpoints

```
Mobile:     < 768px   (Phone)
Tablet:     768-1024px (iPad)
Desktop:    > 1024px   (Laptop/PC)

CSS Variables (mobile-theme.css):
--mobile-xs: 320px
--mobile-sm: 375px
--mobile-md: 414px
--mobile-lg: 768px
--tablet-sm: 768px
--tablet-lg: 1024px

Touch Targets:
--touch-target-min: 44px
--touch-target-recommended: 48px
--touch-target-comfortable: 56px
```

---

## Before & After Comparison

### Product Modal - Before
```
┌──────────────────────────┐
│ ✕ Add Product            │
├──────────────────────────┤
│ Product Name:            │
│ ┌──────────────────────┐ │
│ │                      │ │
│ └──────────────────────┘ │
│ ...                      │
│                          │
│         [Cancel] [Save]  │
└──────────────────────────┘

❌ No file upload option
```

### Product Modal - After
```
┌──────────────────────────┐
│ ✕ Add Product            │
├──────────────────────────┤
│ [Basic Info] [Files] ←NEW│
├──────────────────────────┤
│ Product Name:            │
│ ┌──────────────────────┐ │
│ │                      │ │
│ └──────────────────────┘ │
│ ...                      │
│                          │
│         [Cancel] [Save]  │
└──────────────────────────┘

✅ File upload tab available (when editing)
✅ Up to 5 files, 10MB each
✅ Drag-and-drop support
✅ File icons and download/delete
```

### GRN Items - Before
```
│ Product  │ Qty │ Edit │
├──────────┼─────┼──────┤
│ Widget A │ 100 │  ✏️  │

❌ No QC functionality
❌ Manual entry of accepted/rejected
```

### GRN Items - After
```
│ Product  │ Qty │ Accepted │ Rejected │ Edit │
├──────────┼─────┼──────────┼──────────┼──────┤
│ Widget A │ 100 │    95    │     5    │ ✏️ QC│

✅ QC button to open modal
✅ Structured QC workflow
✅ Inspector tracking
✅ File attachment support
✅ Auto-validation
```

---

## User Workflows

### Workflow 1: Upload Product Files
1. Go to Masters → Products
2. Click Edit on existing product
3. Click "Files" tab
4. Drag file or click "Upload Files"
5. File appears in list
6. Click ⬇️ to download, 🗑️ to delete

### Workflow 2: Perform QC on GRN
1. Go to Vouchers → Purchase → GRN
2. Create/Edit GRN with items
3. Click "QC" button on item
4. Fill inspection details
5. Enter accepted/rejected quantities
6. Add rejection reason if needed
7. Attach photos (optional)
8. Click "Save Quality Check"
9. Quantities update in GRN item

### Workflow 3: Mobile Access
1. Open app on mobile browser
2. Touch-friendly navigation
3. No zoom on double-tap
4. Forms adapt to screen size
5. Buttons are easy to tap
6. Scrolling is smooth

---

## Testing Checklist

**Mobile Testing:**
- [ ] Test on iPhone (Safari)
- [ ] Test on Android (Chrome)
- [ ] Test on iPad (Safari)
- [ ] Verify no double-tap zoom
- [ ] Check touch target sizes
- [ ] Test form inputs on mobile
- [ ] Verify modals are full-screen on mobile
- [ ] Test navigation on mobile

**Product Files Testing:**
- [ ] Upload different file types
- [ ] Upload 5 files (max limit)
- [ ] Try uploading 6th file (should fail)
- [ ] Upload large file >10MB (should fail)
- [ ] Download files
- [ ] Delete files
- [ ] Verify files persist after closing modal
- [ ] Test drag-and-drop

**QC Testing:**
- [ ] Open QC modal from GRN
- [ ] Enter accepted/rejected quantities
- [ ] Verify validation (total ≤ received)
- [ ] Test auto-calculation of QC result
- [ ] Enter rejection reason
- [ ] Upload defect photos
- [ ] Save QC data
- [ ] Verify quantities update in GRN

---

## Accessibility

**Keyboard Navigation:**
- Tab through all inputs
- Enter to submit forms
- Escape to close modals

**Screen Reader Support:**
- All inputs have labels
- Error messages are announced
- File upload status is announced
- QC result changes are announced

**Color Contrast:**
- ✅ PASS: Green chip
- ⚠️ PARTIAL: Orange chip
- ❌ FAIL: Red chip
- All meet WCAG AA standards

---

## Performance

**File Upload:**
- Client-side validation (instant)
- Progress indicator during upload
- Drag-and-drop with visual feedback

**Mobile:**
- Touch-action CSS improves responsiveness
- No unnecessary re-renders
- Smooth scrolling
- Fast page loads

**QC Modal:**
- Form controlled components
- Real-time validation
- Auto-save on submit
- No lag when typing
