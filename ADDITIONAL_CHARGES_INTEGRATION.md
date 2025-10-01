# Additional Charges Integration Guide

## Overview

This guide explains how to integrate the `AdditionalCharges` component with vouchers (except GRN and Delivery Challan).

## Component Location

- Component: `/frontend/src/components/AdditionalCharges.tsx`
- Utility Functions: `/frontend/src/utils/voucherUtils.ts` (updated `calculateVoucherTotals`)
- Totals Display: `/frontend/src/components/VoucherFormTotals.tsx` (updated to display additional charges)

## Integration Steps

### 1. Import Required Components and Types

```typescript
import AdditionalCharges, { AdditionalChargesData } from '../../../components/AdditionalCharges';
```

### 2. Add State for Additional Charges

In your voucher component, add state to manage additional charges:

```typescript
const [additionalCharges, setAdditionalCharges] = useState<AdditionalChargesData>({
  freight: 0,
  installation: 0,
  packing: 0,
  insurance: 0,
  loading: 0,
  unloading: 0,
  miscellaneous: 0,
});
```

### 3. Update Totals Calculation

When calculating totals, pass the additional charges to `calculateVoucherTotals`:

```typescript
const totals = useMemo(() => {
  const items = watch("items") || [];
  return calculateVoucherTotals(
    items,
    isIntrastate,
    lineDiscountType,
    totalDiscountType,
    watch("total_discount") || 0,
    additionalCharges  // Pass additional charges here
  );
}, [watch("items"), isIntrastate, lineDiscountType, totalDiscountType, watch("total_discount"), additionalCharges]);
```

### 4. Add Component to Form

Place the `AdditionalCharges` component in your form layout (typically after the items table and before totals):

```typescript
{/* Additional Charges Section - Only show in edit/create mode */}
{(mode === "edit" || mode === "create") && (
  <AdditionalCharges
    charges={additionalCharges}
    onChange={setAdditionalCharges}
    mode={mode}
  />
)}
```

### 5. Update VoucherFormTotals Props

Pass the total additional charges to the totals component:

```typescript
<VoucherFormTotals
  totalSubtotal={totals.totalSubtotal}
  totalCgst={totals.totalCgst}
  totalSgst={totals.totalSgst}
  totalIgst={totals.totalIgst}
  totalAmount={totals.totalAmount}
  totalRoundOff={totals.totalRoundOff}
  totalAdditionalCharges={totals.totalAdditionalCharges}  // Add this prop
  isIntrastate={isIntrastate}
  totalDiscountEnabled={totalDiscountEnabled}
  totalDiscountType={totalDiscountType}
  mode={mode}
  watch={watch}
  control={control}
  setValue={setValue}
  handleToggleTotalDiscount={handleToggleTotalDiscount}
  getAmountInWords={getAmountInWords}
/>
```

### 6. Save Additional Charges with Voucher

When submitting the form, include additional charges in the payload:

```typescript
const onSubmit = async (data: any) => {
  const payload = {
    ...data,
    additional_charges: additionalCharges,
    // ... other fields
  };
  // Submit to backend
};
```

### 7. Load Additional Charges when Viewing/Editing

When loading an existing voucher, restore the additional charges state:

```typescript
const handleVoucherClick = (voucher: any) => {
  setMode("view");
  reset({
    ...voucher,
    // ... other fields
  });
  
  // Load additional charges if they exist
  if (voucher.additional_charges) {
    setAdditionalCharges(voucher.additional_charges);
  } else {
    // Reset to default
    setAdditionalCharges({
      freight: 0,
      installation: 0,
      packing: 0,
      insurance: 0,
      loading: 0,
      unloading: 0,
      miscellaneous: 0,
    });
  }
};
```

## How It Works

### Calculation Logic

1. **Products Subtotal**: Sum of all items after line discounts
2. **Total Discount**: Applied to products subtotal
3. **Additional Charges**: Added to taxable amount (products after discount)
4. **GST Calculation**: Applied to (products + additional charges)
5. **Final Total**: Products + Additional Charges + GST + Round Off

### Formula

```
Products Subtotal = Σ(quantity × unit_price) - line discounts
After Total Discount = Products Subtotal - total discount
Taxable Amount = After Total Discount + Additional Charges
GST Amount = Taxable Amount × GST Rate
Final Total = Taxable Amount + GST + Round Off
```

### GST on Additional Charges

The system calculates GST on additional charges using a weighted average GST rate from the products in the voucher. This ensures that additional charges are taxed appropriately based on the product mix.

## Vouchers to Integrate

Apply additional charges to all vouchers **EXCEPT**:
- GRN (Goods Receipt Note) - `/frontend/src/pages/vouchers/Purchase-Vouchers/grn.tsx`
- Delivery Challan - `/frontend/src/pages/vouchers/Sales-Vouchers/delivery-challan.tsx`

### Recommended Vouchers for Integration

**Pre-Sales:**
- Quotation
- Proforma Invoice
- Sales Order

**Sales:**
- Sales Voucher
- Sales Return

**Purchase:**
- Purchase Order
- Purchase Voucher
- Purchase Return

**Financial:**
- Credit Note
- Debit Note

**Manufacturing:**
- Production Order
- Finished Good Receipt
- Material Receipt

## Backend Integration

### Database Schema

Add a JSON field to store additional charges:

```sql
ALTER TABLE quotations ADD COLUMN additional_charges JSONB DEFAULT '{}';
ALTER TABLE sales_vouchers ADD COLUMN additional_charges JSONB DEFAULT '{}';
-- ... repeat for other voucher tables
```

### API Updates

Ensure your backend API accepts and stores the `additional_charges` field:

```python
# In your voucher model
additional_charges = Column(JSON, default={})

# In your API endpoint
@router.post("/quotations")
async def create_quotation(data: QuotationCreate, ...):
    voucher = Quotation(
        # ... other fields
        additional_charges=data.additional_charges,
    )
    # ... save to database
```

## Testing Checklist

- [ ] Additional charges are saved when creating a voucher
- [ ] Additional charges are loaded when viewing a voucher
- [ ] Additional charges are preserved when editing a voucher
- [ ] GST is calculated correctly with additional charges
- [ ] Totals display correctly with additional charges
- [ ] Additional charges appear in PDF/print output (if applicable)
- [ ] Additional charges are excluded from GRN and Delivery Challan

## Notes

- Additional charges are added to the taxable amount before GST calculation
- They do not affect the individual product line items
- The component provides a clean UI with checkboxes to enable/disable specific charge types
- All charge types are optional and default to 0
- In view mode, only non-zero charges are displayed

## Example Screenshot Location

See `/docs/screenshots/additional-charges-example.png` for UI reference (to be added).
