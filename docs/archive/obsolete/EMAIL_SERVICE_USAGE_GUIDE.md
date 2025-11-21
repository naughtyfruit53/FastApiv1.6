# Email Service Usage Guide

## Overview

The application uses two separate email services to handle different types of email communications:

1. **`system_email_service`** - For app/system-level emails
2. **`user_email_service`** - For organization/user-level emails

## Service Descriptions

### System Email Service (`system_email_service`)

**Purpose**: Handle application-level email communications that are not specific to any organization.

**Location**: `app/services/system_email_service.py`

**Usage Pattern**:
```python
from app.services.system_email_service import system_email_service

# All methods are async and return tuple[bool, Optional[str]]
success, error = await system_email_service.send_password_reset_email(
    user_email="user@example.com",
    user_name="John Doe",
    new_password="newpass123",
    reset_by="admin@example.com",
    organization_name="Acme Corp",
    organization_id=1,
    user_id=123
)
```

**Use Cases**:
- **Password resets**: Admin-initiated password resets for any user
- **Account creation**: New user account creation emails with temporary passwords
- **License creation**: Emails sent when a new organization license is created
- **OTP emails**: One-time password emails for authentication
- **System-wide notifications**: App-level announcements and alerts

**Key Methods**:
- `send_password_reset_email()` - Send password reset notification
- `send_user_creation_email()` - Send welcome email with credentials
- `send_license_creation_email()` - Notify about new license
- `send_otp_email()` - Send one-time password
- `_send_email()` - Internal method for generic email sending

**Important Notes**:
- Uses Brevo API (with SMTP fallback)
- All methods are async
- Includes audit logging for all email sends
- Supports BCC for role-based notifications

---

### User Email Service (`user_email_service`)

**Purpose**: Send emails from user's connected email accounts (Gmail/Outlook) for organization-level tasks.

**Location**: `app/services/user_email_service.py`

**Usage Pattern**:
```python
from app.services.user_email_service import user_email_service

# Send from user's connected account
success, error = await user_email_service.send_email(
    db=db,
    account_id=account.id,  # User's MailAccount ID
    to_email="customer@example.com",
    subject="Your Invoice",
    body="Plain text body",
    html_body="<p>HTML body</p>",
    bcc_emails=["manager@example.com"]
)
```

**Use Cases**:
- **Voucher emails**: Send purchase orders, sales invoices, quotations to vendors/customers
- **Organization user management**: Emails related to org-level user operations
- **Customer communications**: Emails to customers from sales/support team
- **Vendor communications**: Emails to vendors from procurement team
- **Organization notifications**: Internal team notifications

**Key Methods**:
- `send_email()` - Send email via user's connected account

**Important Notes**:
- Requires OAuth-connected email account (Gmail/Outlook)
- Sends from user's actual email address
- Supports BCC recipients
- Uses provider APIs (not SMTP)

---

## Hybrid Approach: Voucher Emails

The `send_voucher_email()` function in `system_email_service.py` implements a hybrid approach:

```python
from app.services.system_email_service import send_voucher_email

# Tries user's email first, falls back to system
success, error = await send_voucher_email(
    voucher_type="purchase_order",
    voucher_id=123,
    recipient_email="vendor@example.com",
    recipient_name="ABC Vendors",
    organization_id=1,
    created_by_id=456  # Creator's user ID
)
```

**How it works**:
1. If `created_by_id` is provided, looks up the creator's connected email account
2. If found, sends via `user_email_service` (from creator's email)
3. If not found or fails, falls back to `system_email_service`

**Benefits**:
- Emails appear to come from the actual user (more personal)
- Maintains proper sender identity for business communications
- Automatic fallback ensures delivery

---

## Migration from Old `email_service`

The legacy `email_service` module has been replaced. Here's how to update your code:

### For App-Level Emails (password resets, account creation):

**Before**:
```python
from app.services.email_service import email_service

email_service.send_password_reset_email(...)
```

**After**:
```python
from app.services.system_email_service import system_email_service

await system_email_service.send_password_reset_email(...)
```

### For Organization-Level Emails (vouchers, notifications):

**Before**:
```python
from app.services.email_service import send_voucher_email

send_voucher_email(...)
```

**After**:
```python
from app.services.system_email_service import send_voucher_email

await send_voucher_email(...)
```

---

## Best Practices

### 1. Choose the Right Service

- **Use `system_email_service`** when:
  - Sending system-wide emails (password resets, welcome emails)
  - No specific user context is available
  - Email should come from system/platform

- **Use `user_email_service`** when:
  - Sending from a specific user's account
  - Personalized business communication needed
  - User has connected their email account

### 2. Handle Async Properly

All email methods are async. Always await them:

```python
# Correct
success, error = await system_email_service.send_password_reset_email(...)

# Wrong
success, error = system_email_service.send_password_reset_email(...)  # Missing await
```

### 3. Pass All Required Parameters

For better audit logging and tracking:

```python
await system_email_service.send_password_reset_email(
    user_email=user.email,
    user_name=user.full_name,
    new_password=password,
    reset_by=admin.email,
    organization_name=org.name,  # Important for context
    organization_id=org.id,      # For audit trail
    user_id=user.id              # For audit trail
)
```

### 4. Handle Errors Gracefully

```python
success, error = await system_email_service.send_password_reset_email(...)
if not success:
    logger.error(f"Failed to send password reset email: {error}")
    # Show user-friendly message
    # Consider retry logic if appropriate
```

### 5. Use Voucher Email Helper

For voucher-related emails, use the helper function:

```python
from app.services.system_email_service import send_voucher_email

success, error = await send_voucher_email(
    voucher_type="sales_invoice",
    voucher_id=voucher.id,
    recipient_email=customer.email,
    recipient_name=customer.name,
    organization_id=org.id,
    created_by_id=current_user.id
)
```

---

## Testing

### Mocking in Tests

For `system_email_service`:
```python
from unittest.mock import patch

with patch('app.services.system_email_service.system_email_service') as mock_service:
    mock_service.send_password_reset_email.return_value = (True, None)
    # Your test code
```

For `user_email_service`:
```python
with patch('app.services.user_email_service.user_email_service') as mock_service:
    mock_service.send_email.return_value = (True, None)
    # Your test code
```

---

## Configuration

Email services are configured via environment variables:

```env
# Brevo (System Email)
BREVO_API_KEY=your_api_key
BREVO_FROM_EMAIL=noreply@tritiq.com
BREVO_FROM_NAME=TRITIQ BOS
ENABLE_BREVO_EMAIL=true

# SMTP Fallback
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_password

# OAuth (User Email)
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret
MICROSOFT_CLIENT_ID=your_client_id
MICROSOFT_CLIENT_SECRET=your_client_secret
```

---

## Troubleshooting

### Email not sending from user account

1. Check if user has connected email account:
   ```python
   stmt = select(MailAccount).filter(
       MailAccount.user_id == user_id,
       MailAccount.is_active == True
   )
   ```

2. Verify OAuth token is valid
3. Check if account has `sync_enabled == True`

### Async/Sync Context Issues

If calling from sync context (not recommended):
```python
import asyncio

# In sync function
try:
    success, error = asyncio.run(system_email_service.send_email(...))
except RuntimeError:
    # Already in event loop, use thread executor
    import concurrent.futures
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(asyncio.run, system_email_service.send_email(...))
        success, error = future.result()
```

---

## Summary

| Use Case | Service | Method | Notes |
|----------|---------|--------|-------|
| Password Reset | `system_email_service` | `send_password_reset_email()` | App-level |
| User Creation | `system_email_service` | `send_user_creation_email()` | App-level |
| License Creation | `system_email_service` | `send_license_creation_email()` | App-level |
| OTP Authentication | `system_email_service` | `send_otp_email()` | App-level |
| Voucher to Customer | `send_voucher_email()` | (hybrid) | Org-level, tries user first |
| Direct from User | `user_email_service` | `send_email()` | Org-level |
| Notifications | Either | Depends on context | Choose based on sender |
