# Voucher PDF & OAuth Token Management Improvements

## Summary

This PR implements comprehensive improvements to voucher PDF generation and OAuth token management as requested. The changes ensure better reliability and maintainability of the system.

---

## 1. Voucher PDF Generation Enhancements

### New PDF Endpoints Added

Added PDF generation endpoints to the following voucher types to replicate the quotation PDF format:

1. **Purchase Order** (`app/api/v1/vouchers/purchase_order.py`)
   - Endpoint: `GET /api/v1/purchase-orders/{invoice_id}/pdf`
   - Generates PDF with company branding, itemized details, and additional charges

2. **Purchase Voucher** (`app/api/v1/vouchers/purchase_voucher.py`)
   - Endpoint: `GET /api/v1/purchase-vouchers/{invoice_id}/pdf`
   - Includes vendor details, GST calculations, and additional charges

3. **Sales Return** (`app/api/v1/vouchers/sales_return.py`)
   - Endpoint: `GET /api/v1/sales-returns/{invoice_id}/pdf`
   - Customer details with return calculations and additional charges

4. **Purchase Return** (`app/api/v1/vouchers/purchase_return.py`)
   - Endpoint: `GET /api/v1/purchase-returns/{invoice_id}/pdf`
   - Vendor details with return calculations and additional charges

### Implementation Details

Each PDF endpoint:
- Uses the existing `pdf_generator.generate_voucher_pdf()` service
- Includes proper authentication and authorization
- Returns streaming response with appropriate filename
- Handles errors with comprehensive logging
- Supports additional charges rendering (already implemented in PDF service)

### Missing Import Fixes

Fixed missing `func` import in:
- `app/api/v1/vouchers/proforma_invoice.py` - Added `func` from sqlalchemy
- `app/api/v1/vouchers/sales_order.py` - Added `func`, `asc`, and `desc` from sqlalchemy

These imports are required for revision numbering queries using `func.max()`.

### Numbering System

**Proforma Invoice Revision System:**
- Already implemented (similar to quotation.py)
- Uses `func.max()` to get latest revision number
- Format: `{parent.voucher_number} Rev {revision_number}`
- Only applies to proforma invoice with parent_id

---

## 2. OAuth Token Management Improvements

### Enhanced Token Validation

**Prevent Reuse of Broken Tokens:**

Modified `OAuth2Service.get_valid_token()` to prevent reuse of:
- `REFRESH_FAILED` tokens - tokens that previously failed to refresh
- `REVOKED` tokens - tokens that have been explicitly revoked
- Tokens with any non-ACTIVE status

**Implementation in Both Async and Sync Versions:**
- `async def get_valid_token()` - Used by async endpoints
- `def sync_get_valid_token()` - Used by synchronous IMAP workers

### Enhanced Error Handling and Logging

**Improved `refresh_token()` Method:**

1. **Better Error Messages:**
   ```python
   error_msg = (
       "No refresh token available. User must revoke app access in their account "
       "settings and re-authorize the application with offline access permissions."
   )
   ```

2. **Comprehensive Logging:**
   - Logs email address and provider for all operations
   - Logs token expiry times and refresh counts
   - Logs detailed error messages with remediation steps

3. **Clear Status Updates:**
   - Sets `token.status = TokenStatus.REFRESH_FAILED` on failure
   - Sets `token.last_sync_error` with detailed error message
   - Clears `last_sync_error` on successful refresh

4. **Structured Remediation Steps:**
   ```
   Remediation: User must revoke app access in their {provider} account 
   settings and re-authorize the application to grant offline access.
   ```

### Admin Tools (Already Implemented)

The following admin endpoints already exist in `app/api/v1/oauth.py`:

1. **View Tokens:** `GET /api/v1/oauth/tokens`
   - Lists all tokens for current user with status details

2. **View Token Details:** `GET /api/v1/oauth/tokens/{token_id}`
   - Shows comprehensive token information including errors

3. **Force Refresh Token:** `POST /api/v1/oauth/tokens/{token_id}/refresh`
   - Manually triggers token refresh

4. **Delete Token:** `DELETE /api/v1/oauth/tokens/{token_id}`
   - Revokes and removes OAuth token

5. **Update Token Settings:** `PUT /api/v1/oauth/tokens/{token_id}`
   - Updates sync settings and other token parameters

---

## 3. Additional Charges in PDFs

### Verification

Additional charges are already properly implemented in the PDF generation service:

**File:** `app/services/pdf_generation_service.py` (lines 429-478)

```python
# Process additional charges and append as special items
additional_charges = voucher_data.get('additional_charges', {})
if isinstance(additional_charges, str):
    additional_charges = json.loads(additional_charges)
    
if isinstance(additional_charges, dict):
    for name, amount in additional_charges.items():
        if amount > 0:
            # Creates charge item with GST calculations
            processed_item = {
                'product_name': name.capitalize() + ' Charge',
                'gst_rate': 18.0,  # Default GST rate
                # ... full item details
                'is_charge': True
            }
            processed_items.append(processed_item)
```

**Features:**
- Parses JSON or dict additional_charges
- Calculates GST for charges (default 18%)
- Adds charges as items in the PDF
- Flags charges with `is_charge: True` for templates
- Includes charges in total calculations

---

## 4. Testing

### New Test File

Created `tests/test_voucher_pdf_oauth_improvements.py` with:

1. **Voucher PDF Endpoint Tests:**
   - Verifies all new PDF endpoints exist
   - Smoke tests for route registration

2. **OAuth Token Management Tests:**
   - Tests prevention of REFRESH_FAILED token reuse
   - Tests prevention of REVOKED token reuse
   - Tests token status marking on refresh failure
   - Tests successful token handling
   - Tests both async and sync versions

3. **Import Verification Tests:**
   - Verifies func import in proforma_invoice.py
   - Verifies func import in sales_order.py

### Test Coverage

All critical paths are covered:
- New PDF endpoints existence
- Token validation logic
- Error handling in token refresh
- Status transitions (ACTIVE → REFRESH_FAILED)

---

## 5. Files Modified

### Voucher API Files (7 files)
1. `app/api/v1/vouchers/proforma_invoice.py` - Added func import
2. `app/api/v1/vouchers/sales_order.py` - Added func, asc, desc imports
3. `app/api/v1/vouchers/purchase_order.py` - Added PDF endpoint + imports
4. `app/api/v1/vouchers/purchase_voucher.py` - Added PDF endpoint + imports
5. `app/api/v1/vouchers/sales_return.py` - Added PDF endpoint + imports
6. `app/api/v1/vouchers/purchase_return.py` - Added PDF endpoint + imports

### OAuth Service (1 file)
7. `app/services/oauth_service.py` - Enhanced token validation and error handling

### Tests (1 file)
8. `tests/test_voucher_pdf_oauth_improvements.py` - New comprehensive tests

---

## 6. Breaking Changes

**None.** All changes are backward compatible:
- New endpoints added without modifying existing ones
- Token validation is stricter but follows expected OAuth patterns
- Additional error logging does not affect functionality

---

## 7. Deployment Notes

### No Database Migrations Required
All features use existing database schema.

### Configuration
No new configuration required. Uses existing:
- OAuth client credentials (GOOGLE_CLIENT_ID, MICROSOFT_CLIENT_ID, etc.)
- PDF generation settings
- Database connections

### Logging
Enhanced logging will produce more detailed messages. Review log levels if log volume is a concern.

---

## 8. Usage Examples

### Generate PDF for Purchase Order

```bash
GET /api/v1/purchase-orders/123/pdf
Authorization: Bearer {token}

# Response: PDF file download
Content-Type: application/pdf
Content-Disposition: attachment; filename="purchase_order_PO-2024-001.pdf"
```

### Check OAuth Token Status

```bash
GET /api/v1/oauth/tokens
Authorization: Bearer {token}

# Response includes:
{
  "tokens": [
    {
      "id": 1,
      "email_address": "user@example.com",
      "provider": "GOOGLE",
      "status": "ACTIVE",  # or REFRESH_FAILED, REVOKED
      "is_active": true,
      "is_expired": false,
      "last_sync_error": null,  # or error message if failed
      "refresh_count": 5
    }
  ]
}
```

### Force Refresh OAuth Token

```bash
POST /api/v1/oauth/tokens/1/refresh
Authorization: Bearer {token}

# Response:
{
  "success": true,
  "message": "Token refreshed successfully"
}

# Or on failure:
{
  "detail": "Failed to refresh token. User must revoke app access..."
}
```

---

## 9. Monitoring and Troubleshooting

### Log Messages to Watch For

**Success:**
```
Successfully refreshed Google token 123. Email: user@example.com, New expiry: 2024-01-15 10:30:00
Token 123 updated successfully. Refresh count: 5, Email: user@example.com
```

**Failures:**
```
Token 123 has REFRESH_FAILED status and cannot be reused. 
User must re-authorize the account. Email: user@example.com, Provider: GOOGLE, 
Last error: Google OAuth refresh failed: invalid_grant
```

**Remediation:**
```
Remediation: User must revoke app access in their GOOGLE account 
settings and re-authorize the application to grant offline access.
```

### Common Issues

1. **Token marked as REFRESH_FAILED**
   - **Cause:** No refresh token or expired refresh token
   - **Solution:** User must re-authorize the app after revoking access

2. **PDF generation fails**
   - **Cause:** Missing company branding or invalid voucher data
   - **Check:** Company setup and voucher data completeness

3. **Additional charges not showing in PDF**
   - **Cause:** Invalid JSON format in additional_charges field
   - **Check:** Ensure additional_charges is valid JSON dict

---

## 10. Future Enhancements

Potential improvements for future releases:

1. **PDF Templates:**
   - Multiple template options per voucher type
   - Custom branding per voucher

2. **OAuth Improvements:**
   - Automatic token refresh before expiry
   - Proactive notification of failing tokens
   - Token health dashboard

3. **Batch Operations:**
   - Generate PDFs for multiple vouchers
   - Bulk token refresh

4. **Advanced Logging:**
   - Structured logging with correlation IDs
   - Token usage analytics
   - PDF generation metrics

---

## 11. References

- **Quotation Implementation:** `app/api/v1/vouchers/quotation.py`
- **PDF Service:** `app/services/pdf_generation_service.py`
- **OAuth Service:** `app/services/oauth_service.py`
- **Token Models:** `app/models/oauth_models.py`
- **Existing Tests:** `tests/test_pdf_generation.py`, `tests/test_oauth.py`

---

## 12. Checklist

- [x] PDF endpoints added to all required voucher types
- [x] Missing imports fixed (func, asc, desc)
- [x] OAuth token validation prevents broken token reuse
- [x] Enhanced error handling and logging
- [x] Additional charges verified in PDF generation
- [x] Tests created for new functionality
- [x] Documentation updated
- [x] No breaking changes
- [x] Backward compatible

---

**Implementation Date:** 2024
**PR Branch:** copilot/fix-7497c1ad-edcf-42e3-90cf-42ce60b1ec8a
**Status:** Ready for Review
