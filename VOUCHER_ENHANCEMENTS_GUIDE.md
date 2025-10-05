# Voucher System Enhancements Guide

This document describes the new features added to the voucher system.

## Table of Contents
1. [Privacy-Enhanced Email System](#1-privacy-enhanced-email-system)
2. [Auto-filled Email Templates](#2-auto-filled-email-templates)
3. [AI Chatbot Assistant](#3-ai-chatbot-assistant)
4. [Enhanced Email Attachments UI](#4-enhanced-email-attachments-ui)
5. [Voucher Number Prefix](#5-voucher-number-prefix)
6. [Voucher Counter Reset Periods](#6-voucher-counter-reset-periods)
7. [Voucher Format Templates](#7-voucher-format-templates)

---

## 1. Privacy-Enhanced Email System

### Overview
Voucher emails are now sent exclusively through user-connected email accounts (Gmail, Outlook) via OAuth2. System email fallback has been removed for privacy and compliance.

### Changes
- **Before**: Voucher emails would fall back to system email if user email was unavailable
- **After**: Voucher emails require user email account connection; explicit error if unavailable

### Implementation Details
- Modified `send_voucher_email()` in `app/services/system_email_service.py`
- Removed fallback logic to `system_email_service._send_email()`
- Returns clear error message: "No active email account found for user X. Please connect an email account to send vouchers."

### User Impact
- **Action Required**: Users must connect their email accounts (Gmail/Outlook) before sending voucher emails
- **Benefits**: Enhanced privacy, emails sent from user's actual address, better deliverability

---

## 2. Auto-filled Email Templates

### Overview
After creating or downloading a voucher, users are prompted to send it via email with subject and body auto-filled based on voucher type and entity type.

### Features
- Automatic prompt after voucher PDF generation
- Pre-filled subject and body templates
- Customizable per voucher type (PO, SO, Invoice, etc.) and entity type (customer/vendor)
- Organization-level template customization

### API Endpoints
```
GET  /api/v1/voucher-email-templates/
GET  /api/v1/voucher-email-templates/{id}
POST /api/v1/voucher-email-templates/
PUT  /api/v1/voucher-email-templates/{id}
DELETE /api/v1/voucher-email-templates/{id}
GET  /api/v1/voucher-email-templates/default/{voucher_type}/{entity_type}
```

### Template Variables
Templates support the following variables:
- `{voucher_number}` - Voucher number
- `{voucher_date}` - Voucher date
- `{total_amount}` - Total amount
- `{vendor_name}` - Vendor name (for vendor-related vouchers)
- `{customer_name}` - Customer name (for customer-related vouchers)
- `{organization_name}` - Your organization name

### Default Templates
| Voucher Type | Entity Type | Subject Template |
|--------------|-------------|------------------|
| purchase_order | vendor | Purchase Order {voucher_number} - {organization_name} |
| sales_order | customer | Sales Order {voucher_number} - {organization_name} |
| purchase_voucher | vendor | Purchase Invoice {voucher_number} - {organization_name} |
| sales_voucher | customer | Invoice {voucher_number} - {organization_name} |
| quotation | customer | Quotation {voucher_number} - {organization_name} |

### Usage
1. Create/view a voucher
2. Click "Download PDF" or "Preview PDF"
3. Email dialog automatically appears with pre-filled content
4. Edit if needed and send

---

## 3. AI Chatbot Assistant

### Overview
A floating chatbot assistant in the bottom-right corner helps users navigate, create records, and perform common tasks.

### Features
- **Navigation**: "Open vendors", "Go to purchase orders", etc.
- **Creation**: "Add new vendor", "Create customer", etc.
- **Reports**: "Show low stock items", "Generate sales report"
- **Actions**: "Repeat purchase order", "View pending GRNs"

### Example Commands
```
"open vendors" → Navigates to vendors page
"add new customer" → Opens customer creation form
"show low stock items" → Shows items with low inventory
"repeat purchase order" → Goes to PO list to select order to repeat
"generate sales report" → Opens sales report
```

### Technical Details
- Component: `frontend/src/components/ChatbotNavigator.tsx`
- Position: Fixed bottom-right (z-index: 1300)
- State: Expandable/collapsible
- Integration: Added to `_app.tsx` for global availability

---

## 4. Enhanced Email Attachments UI

### Overview
Improved email attachment display showing exact count, file details, and easy download functionality.

### Features
- **Exact Count**: Shows "2 attachments" instead of just an icon
- **File Details**: Display filename, size, and type
- **Dropdown List**: Click to see all attachments in a menu
- **Click to Download**: Single click to download any attachment
- **File Icons**: Visual indicators for PDF, images, documents, etc.

### Component Usage
```tsx
import EmailAttachmentDisplay from '../components/EmailAttachmentDisplay';

<EmailAttachmentDisplay
  attachments={email.attachments}
  onDownload={(attachment) => downloadFile(attachment)}
  variant="button" // or "chip" or "compact"
/>
```

### Variants
- **button**: Full button with count and dropdown (default)
- **chip**: Compact chip style
- **compact**: Inline text with dropdown icon

---

## 5. Voucher Number Prefix

### Overview
Add organization-level prefix (up to 5 characters) to all voucher numbers.

### Configuration
Navigate to: **Settings → Voucher Settings**

- **Enable Prefix**: Toggle to enable/disable
- **Prefix Value**: Enter up to 5 characters (auto-converted to uppercase)
- **Preview**: See live preview of voucher number format

### Examples
| Prefix | Sample Voucher Number |
|--------|----------------------|
| PM | PM-PO/2526/00001 |
| ACME | ACME-SV/2526/00001 |
| NYC | NYC-PO/2526/00001 |

### Database
- Field: `organization_settings.voucher_prefix` (VARCHAR(5))
- Field: `organization_settings.voucher_prefix_enabled` (BOOLEAN)

---

## 6. Voucher Counter Reset Periods

### Overview
Choose how often voucher numbers reset: never, monthly, quarterly, or annually.

### Options

#### Never
Continuous numbering across all periods.
```
PO/2526/00001
PO/2526/00002
...
```

#### Annually (Default)
Resets each fiscal year.
```
PO/2526/00001  (FY 2025-26)
PO/2627/00001  (FY 2026-27)
```

#### Quarterly
Resets each quarter.
```
PO/2526/Q1/00001  (Apr-Jun)
PO/2526/Q2/00001  (Jul-Sep)
PO/2526/Q3/00001  (Oct-Dec)
PO/2526/Q4/00001  (Jan-Mar)
```

#### Monthly
Resets each month.
```
PO/2526/APR/00001
PO/2526/MAY/00001
PO/2526/JUN/00001
```

### Configuration
Navigate to: **Settings → Voucher Settings → Counter Reset Period**

Select your preferred option via radio buttons.

### Database
- Field: `organization_settings.voucher_counter_reset_period` (ENUM)
- Values: `never`, `annually`, `quarterly`, `monthly`

---

## 7. Voucher Format Templates

### Overview
Multiple PDF/email format templates with preview and organization-level selection.

### Features
- **System Templates**: Pre-built professional templates
- **Custom Templates**: Create organization-specific templates
- **Preview**: View template before selection
- **Template Config**: JSON-based configuration for layout, styles, fonts, colors

### API Endpoints
```
GET  /api/v1/voucher-format-templates/
GET  /api/v1/voucher-format-templates/{id}
POST /api/v1/voucher-format-templates/
PUT  /api/v1/voucher-format-templates/{id}
DELETE /api/v1/voucher-format-templates/{id}
GET  /api/v1/voucher-format-templates/system/defaults
```

### Template Configuration Structure
```json
{
  "layout": "modern",
  "header": {
    "show_logo": true,
    "show_company_details": true,
    "alignment": "left"
  },
  "colors": {
    "primary": "#2563eb",
    "secondary": "#64748b",
    "accent": "#10b981"
  },
  "fonts": {
    "heading": "Helvetica-Bold",
    "body": "Helvetica",
    "size_heading": 16,
    "size_body": 10
  },
  "sections": {
    "show_items_table": true,
    "show_terms": true,
    "show_signature": true
  }
}
```

### Configuration
Navigate to: **Settings → Voucher Settings → Voucher Format Template**

Select from dropdown of available templates.

### Database
- Table: `voucher_format_templates`
- Field: `organization_settings.voucher_format_template_id` (FK)

---

## Migration

Run the database migration:
```bash
alembic upgrade head
```

This creates:
- `voucher_email_templates` table
- `voucher_format_templates` table
- New columns in `organization_settings`

---

## Testing

### Manual Testing Checklist

#### 1. Email Privacy
- [ ] Try sending voucher email without connected email account
- [ ] Verify error message appears
- [ ] Connect email account
- [ ] Send voucher email successfully
- [ ] Verify email arrives from user's address

#### 2. Email Templates
- [ ] Create voucher
- [ ] Download PDF
- [ ] Verify email prompt appears
- [ ] Check subject and body are auto-filled
- [ ] Edit template in settings
- [ ] Verify changes reflect in new vouchers

#### 3. Chatbot
- [ ] Click chatbot icon (bottom-right)
- [ ] Type "open vendors"
- [ ] Verify navigation
- [ ] Try other commands
- [ ] Test creation shortcuts

#### 4. Attachments UI
- [ ] View email with attachments
- [ ] Verify count is shown
- [ ] Click attachment dropdown
- [ ] Download attachment
- [ ] Verify all file types have correct icons

#### 5. Voucher Prefix
- [ ] Go to Settings → Voucher Settings
- [ ] Enable prefix
- [ ] Enter "TEST"
- [ ] Create new voucher
- [ ] Verify number: TEST-PO/2526/00001

#### 6. Counter Reset
- [ ] Go to Settings → Voucher Settings
- [ ] Select "Monthly"
- [ ] Check preview shows month
- [ ] Create voucher
- [ ] Verify format includes month

#### 7. Format Templates
- [ ] Go to Settings → Voucher Settings
- [ ] Select different template
- [ ] Generate PDF
- [ ] Verify PDF uses selected template

---

## Troubleshooting

### Email not sending
- **Issue**: "No active email account found"
- **Solution**: Navigate to Email Settings and connect Gmail or Outlook account

### Chatbot not appearing
- **Issue**: Chatbot icon not visible
- **Solution**: Check you're logged in and not on login page

### Prefix not applying
- **Issue**: Voucher numbers don't include prefix
- **Solution**: Ensure "Enable Prefix" is toggled on in Voucher Settings

### Counter reset not working
- **Issue**: Numbers not resetting as expected
- **Solution**: Verify counter reset period setting, check fiscal year calculation

---

## API Reference

### Voucher Email Templates

#### List Templates
```http
GET /api/v1/voucher-email-templates/
?voucher_type=purchase_order&entity_type=vendor
```

#### Get Default Template
```http
GET /api/v1/voucher-email-templates/default/{voucher_type}/{entity_type}
```

#### Create Template
```http
POST /api/v1/voucher-email-templates/
Content-Type: application/json

{
  "organization_id": 1,
  "voucher_type": "purchase_order",
  "entity_type": "vendor",
  "subject_template": "PO {voucher_number} - {organization_name}",
  "body_template": "Dear {vendor_name}...",
  "is_active": true
}
```

### Voucher Format Templates

#### List Templates
```http
GET /api/v1/voucher-format-templates/
?include_system=true
```

#### Get System Templates
```http
GET /api/v1/voucher-format-templates/system/defaults
```

### Organization Settings

#### Get Settings
```http
GET /api/v1/organizations/settings
```

#### Update Settings
```http
PUT /api/v1/organizations/settings
Content-Type: application/json

{
  "voucher_prefix": "ACME",
  "voucher_prefix_enabled": true,
  "voucher_counter_reset_period": "quarterly",
  "voucher_format_template_id": 1
}
```

---

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review API documentation
3. Contact system administrator
4. Create a support ticket

---

## Future Enhancements

Potential future improvements:
- AI-powered email content suggestions
- More chatbot actions (create PO, check stock, etc.)
- Advanced template editor with WYSIWYG
- Multi-language template support
- Email analytics and tracking
- Bulk email sending
- Email scheduling

---

Last Updated: 2024-01-15
Version: 1.0
