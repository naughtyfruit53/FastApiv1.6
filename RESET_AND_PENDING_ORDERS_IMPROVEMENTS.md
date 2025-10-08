# Reset Service and Pending Orders Improvements

This document describes the improvements made to the system reset service and the pending orders functionality.

## 1. Reset Service Refactoring (`app/services/reset_service.py`)

### Changes Made

#### 1.1 Comprehensive Table Deletion
- **Added deletion of custom raw SQL tables**: oauth_states, user_email_tokens, bank_accounts, chart_of_accounts, snappymail_configs, email_attachments, emails, mail_accounts
- **Defined `CUSTOM_RAW_SQL_TABLES` constant** at module level for easy maintenance
- Tables are deleted using raw SQL via `text()` function with proper error handling

#### 1.2 Transaction Safety and Atomicity
- **Improved error handling**: All database operations wrapped in try-except with rollback on failure
- **Atomic operations**: Either all deletions succeed or all are rolled back
- **Clear error messages**: Added detailed logging for transaction rollback

#### 1.3 Enhanced Logging
- **Step-by-step logging**: Each deletion step is logged with step number (Step 1, Step 2, etc.)
- **Deletion counts**: Each step logs the number of records deleted
- **Error tracking**: Errors are collected in `result["errors"]` array for audit purposes
- **Summary logging**: Final summary of all deletions and any errors encountered

#### 1.4 Robust Supabase Auth Deletion
- **Individual user deletion with error handling**: Each Supabase user deletion is wrapped in try-except
- **Graceful failure**: If Supabase is unavailable or has errors, the operation continues
- **Error collection**: Supabase errors are logged and added to the errors array
- **Partial success reporting**: Reports how many users were successfully deleted out of total

#### 1.5 Sequence Reset
- **Extended sequence list**: Added more sequences to reset including companies_id_seq, customers_id_seq, vendors_id_seq, products_id_seq, stock_id_seq, payment_terms_id_seq
- **Error handling for sequences**: Each sequence reset is wrapped in try-except

### Key Features

1. **Authorization**: Restricted to god superadmin (naughtyfruit53@gmail.com) only
2. **Atomic transactions**: All or nothing - transaction rolls back on any error
3. **Comprehensive deletion**: Includes ORM models and custom raw SQL tables
4. **Detailed audit trail**: Complete logging of all operations and errors
5. **Graceful degradation**: External service failures (Supabase) don't stop the operation

### Example Result Structure

```python
{
    "message": "System factory reset completed",
    "deleted": {
        "user_service_roles": 10,
        "service_role_permissions": 20,
        "service_roles": 5,
        # ... more counts
        "oauth_states": 3,
        "user_email_tokens": 7,
        "supabase_auth_users": 8
    },
    "errors": [
        "Failed to delete bank_accounts: table does not exist",
        "Failed to delete Supabase user abc123: connection timeout"
    ]
}
```

## 2. Pending Orders Backend Fix (`app/api/reports.py`)

### Changes Made

#### 2.1 Improved Query Logic
- **Fixed PO filtering**: Now uses `pending_quantity` from items to determine if PO is truly pending
- **Skip empty POs**: POs without items are excluded from results
- **Accurate calculations**: Uses `pending_quantity` directly instead of recalculating from GRN items

#### 2.2 Color Coding Implementation
- **Red**: No tracking details (neither transporter_name nor tracking_number)
- **Yellow**: Has tracking but GRN still pending
- **Green**: All items received (excluded from pending list)

#### 2.3 Enhanced Documentation
- Added comprehensive docstring explaining:
  - What POs are included
  - Color coding logic
  - Expected behavior

### Example Response

```python
{
    "orders": [
        {
            "id": 123,
            "voucher_number": "PO-001",
            "color_status": "red",  # No tracking
            "has_tracking": False,
            "pending_qty": 100.0,
            # ... more fields
        },
        {
            "id": 124,
            "voucher_number": "PO-002",
            "color_status": "yellow",  # Has tracking
            "has_tracking": True,
            "transporter_name": "Blue Dart",
            "tracking_number": "BD123456",
            "pending_qty": 50.0,
            # ... more fields
        }
    ],
    "summary": {
        "total_orders": 2,
        "total_value": 150000.50,
        "with_tracking": 1,
        "without_tracking": 1
    }
}
```

## 3. Purchase Order List Color Coding (`app/api/v1/vouchers/purchase_order.py`)

### Changes Made

#### 3.1 Color Status Calculation
- **Added color_status field** to each PO in list response
- **Logic**: 
  - Green: All items received (pending_quantity = 0 for all items)
  - Yellow: Has tracking but items still pending
  - Red: No tracking and items pending

#### 3.2 GRN Status Enhancement
- Maintained existing grn_status field ("pending", "partial", "complete")
- Added color_status for UI highlighting

### Code Example

```python
# Set color_status for UI highlighting
has_tracking = bool(po.tracking_number or po.transporter_name)

if all_items_received:
    po.color_status = "green"
elif has_tracking:
    po.color_status = "yellow"
else:
    po.color_status = "red"
```

## 4. Schema Updates (`app/schemas/vouchers.py`)

### Changes Made

#### 4.1 PurchaseOrderInDB Schema
- **Added `grn_status`**: Optional[str] - GRN completion status
- **Added `color_status`**: Optional[str] - Color coding for UI
- **Added tracking fields to schema**:
  - `transporter_name`: Optional[str]
  - `tracking_number`: Optional[str]
  - `tracking_link`: Optional[str]

### Example Schema

```python
class PurchaseOrderInDB(VoucherInDBBase):
    # ... existing fields
    grn_status: Optional[str] = None  # "pending", "partial", "complete"
    color_status: Optional[str] = None  # "red", "yellow", "green"
    transporter_name: Optional[str] = None
    tracking_number: Optional[str] = None
    tracking_link: Optional[str] = None
```

## 5. Frontend Updates (`frontend/src/components/VoucherListModal.tsx`)

### Changes Made

#### 5.1 Color Coding Display
- **Added border coloring** based on color_status
- **Visual indicators**:
  - Green border (#4caf50): GRN complete
  - Yellow border (#ff9800): Tracking present, GRN pending
  - Red border (#f44336): No tracking
  - No border: No color status (for non-PO vouchers)

### Code Example

```typescript
const colorStatus = voucher.color_status;
const borderColor = colorStatus === 'green' ? '#4caf50' : 
                   colorStatus === 'yellow' ? '#ff9800' : 
                   colorStatus === 'red' ? '#f44336' : 
                   'transparent';

<TableRow
  sx={{
    borderLeft: colorStatus ? `4px solid ${borderColor}` : 'none',
  }}
>
```

## 6. Testing

### Test Coverage

Created comprehensive test suite (`tests/test_reset_service_improvements.py`) covering:

1. **Custom raw SQL tables definition**
2. **God superadmin authorization**
3. **Transaction rollback on error**
4. **Custom table deletion attempts**
5. **Graceful Supabase error handling**
6. **Color status logic validation**

### Running Tests

```bash
# Run reset service tests
pytest tests/test_reset_service_improvements.py -v

# Run all tests
pytest tests/ -v
```

## 7. Benefits

### Reset Service
1. **Data Integrity**: Atomic transactions ensure consistent state
2. **Auditability**: Complete logging and error tracking
3. **Reliability**: Graceful handling of external service failures
4. **Completeness**: All tables including custom SQL tables are cleaned up

### Pending Orders
1. **Accuracy**: Correct identification of pending POs using pending_quantity
2. **Visibility**: Clear color coding shows status at a glance
3. **Efficiency**: Quick identification of POs needing attention
4. **Consistency**: Same color coding across pending orders page and PO list

## 8. Migration Notes

### No Database Schema Changes Required
- All model fields (tracking_number, transporter_name, tracking_link) already exist
- color_status and grn_status are computed fields, not persisted

### No Breaking Changes
- All changes are backward compatible
- Existing API contracts maintained
- New fields are optional

## 9. Future Enhancements

### Potential Improvements
1. Add email notifications for POs without tracking after X days
2. Implement batch tracking updates
3. Add tracking status webhook integration with shipping providers
4. Create dashboard widget for pending orders summary
5. Add automated GRN creation from tracking confirmations

## 10. Summary

This implementation delivers:

✅ Robust, atomic system reset with comprehensive table deletion  
✅ Complete audit trail with detailed logging  
✅ Accurate pending orders identification using pending_quantity  
✅ Clear color coding for purchase order status  
✅ Consistent UI highlighting across pages  
✅ Comprehensive test coverage  
✅ Zero breaking changes  
✅ Enhanced error handling and graceful degradation  

All requirements from the problem statement have been addressed.
