# Remaining Voucher Endpoint Updates Guide

## Files Still Need Manual Completion

The following files have datetime imports added but need the implementation updates completed:

1. **proforma_invoice.py**
2. **sales_order.py**
3. **sales_return.py**
4. **purchase_voucher.py**
5. **purchase_return.py**

## Required Changes for Each File

### Step 1: Update get_next_*_number endpoint

Replace the docstring and implementation:

```python
"""Get the next available [voucher_name] number for a given date"""
# Parse the voucher_date if provided
date_to_use = None
if voucher_date:
    try:
        date_to_use = date_parser.parse(voucher_date)
    except Exception:
        pass

return await VoucherNumberService.generate_voucher_number_async(
    db, "[PREFIX]", current_user.organization_id, [ModelName], voucher_date=date_to_use
)
```

### Step 2: Add check-backdated-conflict endpoint

Add after the next-number endpoint:

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
            db, "[PREFIX]", current_user.organization_id, [ModelName], parsed_date
        )
        return conflict_info
    except Exception as e:
        logger.error(f"Error checking backdated conflict: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
```

### Step 3: Update create_*_voucher function

Add voucher_date extraction after organization_id assignment:

```python
# Get the voucher date for numbering
voucher_date = None
if 'date' in voucher_data and voucher_data['date']:
    voucher_date = voucher_data['date'] if hasattr(voucher_data['date'], 'year') else None
```

Update all `generate_voucher_number_async` calls to include `voucher_date=voucher_date`:

```python
VoucherNumberService.generate_voucher_number_async(
    db, "[PREFIX]", current_user.organization_id, [ModelName], voucher_date=voucher_date
)
```

## Prefix Mappings

- proforma_invoice.py: PREFIX="PRO", Model=ProformaInvoice
- sales_order.py: PREFIX="SO", Model=SalesOrder
- sales_return.py: PREFIX="SR", Model=SalesReturn
- purchase_voucher.py: PREFIX="PV", Model=PurchaseVoucher
- purchase_return.py: PREFIX="PR", Model=PurchaseReturn

## Verification

After updating, verify each file has:
1. datetime and dateutil imports
2. voucher_date parameter in next-number endpoint
3. check-backdated-conflict endpoint
4. voucher_date extraction in create function
5. voucher_date parameter passed to all generate_voucher_number_async calls
