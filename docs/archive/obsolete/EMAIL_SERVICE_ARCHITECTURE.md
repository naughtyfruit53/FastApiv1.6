# Email Service Architecture

## Overview Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    FastAPI v1.6 Email Services                  │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────────────┐      ┌──────────────────────────────┐
│  system_email_service    │      │  user_email_service          │
│  (App/System Level)      │      │  (Organization Level)        │
├──────────────────────────┤      ├──────────────────────────────┤
│                          │      │                              │
│  • Uses Brevo API        │      │  • Uses OAuth tokens         │
│  • SMTP fallback         │      │  • Gmail/Outlook APIs        │
│  • System sender         │      │  • User's actual email       │
│                          │      │                              │
│  Use Cases:              │      │  Use Cases:                  │
│  ✓ Password resets       │      │  ✓ Voucher emails            │
│  ✓ Account creation      │      │  ✓ Customer comms            │
│  ✓ License creation      │      │  ✓ Vendor comms              │
│  ✓ OTP emails            │      │  ✓ Team notifications        │
│  ✓ System alerts         │      │  ✓ Business correspondence   │
│                          │      │                              │
└──────────────────────────┘      └──────────────────────────────┘
         │                                      │
         └──────────────┬───────────────────────┘
                        │
         ┌──────────────▼──────────────┐
         │   send_voucher_email()      │
         │   (Hybrid Approach)         │
         ├─────────────────────────────┤
         │                             │
         │  1. Try user's email ──┐    │
         │                        │    │
         │  2. Fallback to system │    │
         │                        │    │
         └────────────────────────┘    │
                                       │
                ┌──────────────────────┘
                │
                ▼
         Ensures Delivery!
```

## Email Flow for Vouchers

```
┌─────────────────────────────────────────────────────────────────┐
│                     Voucher Email Workflow                      │
└─────────────────────────────────────────────────────────────────┘

User Action: Generate Voucher PDF
         │
         ▼
┌─────────────────────┐
│  Frontend           │
│  VoucherPDFButton   │
└─────────┬───────────┘
          │
          │ POST /pdf-generation/voucher/{type}/{id}/download
          │
          ▼
┌─────────────────────┐
│  Backend API        │
│  pdf_generation.py  │
└─────────┬───────────┘
          │
          │ Generate PDF with voucher number
          │ Filename: PO-2526-00004.pdf (sanitized)
          │
          ▼
┌─────────────────────┐
│  Return PDF         │
│  to Frontend        │
└─────────┬───────────┘
          │
          │ Automatic prompt (500ms delay)
          │
          ▼
┌─────────────────────┐
│  Email Dialog       │
│  (Frontend)         │
└─────────┬───────────┘
          │
          │ User fills subject, body
          │ Detects recipient (vendor/customer)
          │
          ▼
┌─────────────────────┐
│  Send Email         │
│  via user's account │
└─────────┬───────────┘
          │
          │ POST /mail/tokens/{id}/emails/send
          │
          ▼
┌─────────────────────┐
│  user_email_service │
│  Send via Gmail/    │
│  Outlook API        │
└─────────┬───────────┘
          │
          ▼
     Recipient!
```

## Service Selection Logic

```
┌──────────────────────────────────────────────────┐
│         When to Use Which Service?               │
└──────────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ Question: Is this an app-level operation?   │
└─────────────┬───────────────────────────────┘
              │
     ┌────────┴────────┐
     │                 │
    YES               NO
     │                 │
     ▼                 ▼
┌──────────────┐  ┌──────────────┐
│ system_email │  │ user_email   │
│ _service     │  │ _service     │
└──────────────┘  └──────────────┘
     │                 │
     ▼                 ▼
Examples:         Examples:
• Password reset  • Vouchers
• New account     • Invoices
• License created • Quotations
• OTP login       • POs/SOs
• System alert    • Customer emails
                  • Vendor emails

Special Case: send_voucher_email()
┌─────────────────────────────────┐
│ Tries user_email_service first │
│ Falls back to system_email      │
└─────────────────────────────────┘
```

## Migration Path

```
OLD: email_service (non-existent)
         │
         │ Refactored to ↓
         │
         ▼
NEW: system_email_service + user_email_service
         │
         ├─→ system_email_service (app-level)
         │   • Password resets
         │   • Account creation
         │   • System notifications
         │
         └─→ user_email_service (org-level)
             • Vouchers
             • Business emails
             • User-to-user comms
```

## Code Examples

### Using system_email_service

```python
from app.services.system_email_service import system_email_service

# Password reset (app-level)
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

### Using user_email_service

```python
from app.services.user_email_service import user_email_service

# Send invoice to customer (org-level)
success, error = await user_email_service.send_email(
    db=db,
    account_id=user_mail_account.id,
    to_email="customer@example.com",
    subject="Invoice #INV-123",
    body="Please find attached your invoice.",
    html_body="<p>Invoice attached</p>"
)
```

### Using send_voucher_email (Hybrid)

```python
from app.services.system_email_service import send_voucher_email

# Send purchase order (tries user, falls back to system)
success, error = await send_voucher_email(
    voucher_type="purchase_order",
    voucher_id=123,
    recipient_email="vendor@example.com",
    recipient_name="ABC Vendors",
    organization_id=1,
    created_by_id=current_user.id
)
```

## Benefits of New Architecture

### Separation of Concerns
✅ Clear distinction between app and org emails
✅ Each service has specific responsibilities
✅ Easier to maintain and test

### Flexibility
✅ Can send from user's actual email (more personal)
✅ System fallback ensures delivery
✅ Supports multiple email providers

### Audit & Compliance
✅ Better tracking with organization_id and user_id
✅ Enhanced audit logging
✅ Compliance-ready email trails

### User Experience
✅ Emails appear from actual team members
✅ Professional business correspondence
✅ Automatic fallback prevents failures

## Configuration

```env
# System Email (Brevo)
BREVO_API_KEY=your_key
BREVO_FROM_EMAIL=noreply@tritiq.com
ENABLE_BREVO_EMAIL=true

# SMTP Fallback
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587

# User Email (OAuth)
GOOGLE_CLIENT_ID=your_id
GOOGLE_CLIENT_SECRET=your_secret
MICROSOFT_CLIENT_ID=your_id
MICROSOFT_CLIENT_SECRET=your_secret
```

## Summary

| Feature | system_email_service | user_email_service |
|---------|---------------------|-------------------|
| **Purpose** | App/system emails | Org/user emails |
| **Sender** | System/platform | User's email |
| **Provider** | Brevo + SMTP | Gmail/Outlook |
| **Use Cases** | Auth, admin | Business comms |
| **Async** | Yes | Yes |
| **Audit** | Full | Full |
| **Fallback** | SMTP | system_email |

---

*For detailed usage instructions, see [EMAIL_SERVICE_USAGE_GUIDE.md](EMAIL_SERVICE_USAGE_GUIDE.md)*
