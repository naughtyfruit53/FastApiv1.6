# Voucher Integration Example for Additional Charges

## Quick Integration Template

This is a simplified example showing the key changes needed to integrate AdditionalCharges into any voucher.

### Step 1: Add Import

```typescript
import AdditionalCharges, { AdditionalChargesData } from '../../../components/AdditionalCharges';
```

### Step 2: Add State (After existing state declarations)

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

### Step 3: Modify the useVoucherPage Hook Call

If your voucher uses `useVoucherPage` hook, you need to pass additional charges. The hook will need to be updated to accept and use additional charges in its calculations. Since this requires modifying the shared hook, an alternative approach is to override the calculated totals locally.

### Alternative Approach: Local Totals Override

```typescript
// After the useVoucherPage hook
const {
  // ... all existing destructured values
  computedItems,
  totalAmount,
  totalSubtotal,
  totalCgst,
  totalSgst,
  totalIgst,
  // ... other values
} = useVoucherPage(config);

// Override totals with additional charges
const totalsWithAdditionalCharges = useMemo(() => {
  const items = watch("items") || [];
  return calculateVoucherTotals(
    items,
    isIntrastate,
    lineDiscountType,
    totalDiscountType,
    watch("total_discount") || 0,
    additionalCharges  // Add additional charges here
  );
}, [watch("items"), isIntrastate, lineDiscountType, totalDiscountType, watch("total_discount"), additionalCharges]);

// Use these values instead of the ones from useVoucherPage
const finalTotalAmount = totalsWithAdditionalCharges.totalAmount;
const finalTotalAdditionalCharges = totalsWithAdditionalCharges.totalAdditionalCharges;
```

### Step 4: Add Component to Form (Between VoucherItemTable and VoucherFormTotals)

```typescript
{/* Additional Charges Section */}
{(mode === "edit" || mode === "create") && (
  <Grid size={12}>
    <AdditionalCharges
      charges={additionalCharges}
      onChange={setAdditionalCharges}
      mode={mode}
    />
  </Grid>
)}
```

### Step 5: Update VoucherFormTotals Props

```typescript
<VoucherFormTotals
  totalSubtotal={totalsWithAdditionalCharges.totalSubtotal}
  totalCgst={totalsWithAdditionalCharges.totalCgst}
  totalSgst={totalsWithAdditionalCharges.totalSgst}
  totalIgst={totalsWithAdditionalCharges.totalIgst}
  totalAmount={totalsWithAdditionalCharges.totalAmount}
  totalRoundOff={totalsWithAdditionalCharges.totalRoundOff}
  totalAdditionalCharges={totalsWithAdditionalCharges.totalAdditionalCharges}  // Add this
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

### Step 6: Update Amount in Words Field

```typescript
<TextField
  fullWidth
  label="Amount in Words"
  value={getAmountInWords(finalTotalAmount)}  // Use the final total with additional charges
  disabled
  InputLabelProps={{ shrink: true, style: { fontSize: 12 } }}
  inputProps={{ style: { fontSize: 14 } }}
  size="small"
  sx={{ mt: 2 }}
/>
```

### Step 7: Update onSubmit to Include Additional Charges

```typescript
const onSubmit = async (data: any) => {
  const payload = {
    ...data,
    additional_charges: additionalCharges,  // Add this
    total_amount: finalTotalAmount,  // Use updated total
    // ... other fields
  };
  
  // Continue with existing submit logic
  // ...
};
```

### Step 8: Load Additional Charges When Viewing/Editing

```typescript
const handleVoucherClick = (voucher: any) => {
  setMode("view");
  reset({
    ...voucher,
    date: voucher.date ? new Date(voucher.date).toISOString().split('T')[0] : '',
    items: voucher.items.map((item: any) => ({
      ...item,
      // ... existing mapping
    })),
  });
  
  // Load additional charges
  if (voucher.additional_charges) {
    setAdditionalCharges(voucher.additional_charges);
  } else {
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

// Apply same logic to handleEditWithData, handleReviseWithData, handleViewWithData
```

### Step 9: Update handleFinalSubmit Call

If your voucher uses `handleFinalSubmit` utility, you need to pass additional charges:

```typescript
handleFinalSubmit(
  submitData, 
  watch, 
  computedItems, 
  isIntrastate, 
  finalTotalAmount,  // Use updated total
  totalRoundOff, 
  lineDiscountEnabled, 
  lineDiscountType, 
  totalDiscountEnabled, 
  totalDiscountType, 
  createMutation, 
  updateMutation, 
  mode, 
  handleGeneratePDF, 
  refreshMasterData, 
  config,
  additionalCharges  // Add this parameter
);
```

**Note:** The `handleFinalSubmit` utility function may need to be updated to accept and handle additional charges.

## Complete Example Location

For a complete working example, refer to:
- `/frontend/src/pages/vouchers/Pre-Sales-Voucher/quotation.tsx` (will be updated as reference)

## Testing

After integration, test:
1. Create a voucher with additional charges
2. Save and verify charges are stored
3. Edit the voucher and verify charges load correctly
4. View the voucher and verify charges display correctly
5. Generate PDF and verify charges appear
6. Check GST calculations include additional charges

## Notes

- The AdditionalCharges component handles its own UI and state
- Calculations are handled in `calculateVoucherTotals` utility
- All charge types are optional
- Charges are added to taxable amount before GST calculation
- GRN and Delivery Challan should NOT include this component
