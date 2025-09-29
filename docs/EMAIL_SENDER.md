# Enhanced Brevo Email Sender Documentation

## Overview

The Enhanced Brevo Email Sender provides robust transactional email capabilities with fallback providers, retry logic, audit logging, and comprehensive monitoring for the TRITIQ ERP system.

## Features

### Primary Provider: Brevo (SendinBlue)
- Modern Brevo API integration with enhanced error handling
- Configurable via `BREVO_API_KEY` and `BREVO_FROM_EMAIL`
- Support for both HTML and plain text emails
- Provider response tracking and message ID capture

### Fallback Providers
- **SMTP**: Traditional SMTP fallback with TLS support
- **Gmail API**: OAuth-based Gmail sending (future enhancement)
- **Outlook Graph API**: OAuth-based Outlook sending (future enhancement)

### Retry & Resilience
- Configurable retry attempts (default: 3)
- Exponential backoff retry strategy
- Automatic fallback from Brevo to SMTP on failure
- Provider-specific error handling and logging

### Audit & Monitoring
- Complete email send audit trail in `email_sends` table
- Provider response tracking (sensitive data redacted)
- Retry count and error message logging
- Admin dashboard at `/api/v1/admin/email-logs` (RBAC protected)

### Feature Flags
- `ENABLE_BREVO_EMAIL`: Enable/disable Brevo per deployment
- `EMAIL_FALLBACK_ENABLED`: Enable/disable SMTP fallback
- `EMAIL_RETRY_ATTEMPTS`: Configure retry count
- `EMAIL_RETRY_DELAY_SECONDS`: Configure retry delay

## Email Types

The system supports the following email types:
- `USER_INVITE`: New user account invitations
- `PASSWORD_RESET`: Password reset notifications  
- `USER_CREATION`: Welcome emails for new users
- `OTP`: One-time password delivery
- `NOTIFICATION`: System notifications
- `MARKETING`: Marketing campaigns
- `TRANSACTIONAL`: General transactional emails

## Password Reset Flow

### Token-Based Password Reset
1. **Request Reset**: `POST /api/v1/mail/password/request-reset`
   - Generates secure single-use token (32 bytes, URL-safe)
   - Token expires after 1 hour
   - Sends email with reset link
   
2. **Confirm Reset**: `POST /api/v1/mail/password/confirm-reset`
   - Validates token (single-use, TTL checked)
   - Updates password and invalidates token
   - Returns new JWT access token

### Legacy OTP-Based Reset
- Still supported via existing `/api/v1/password/forgot` and `/api/v1/password/reset`
- Uses OTP verification for backward compatibility

## Configuration

### Environment Variables

```env
# Primary Provider (Brevo)
BREVO_API_KEY=your-brevo-api-key
BREVO_FROM_EMAIL=your-email@domain.com
BREVO_FROM_NAME=TRITIQ ERP

# Feature Flags
ENABLE_BREVO_EMAIL=true
EMAIL_FALLBACK_ENABLED=true
EMAIL_RETRY_ATTEMPTS=3
EMAIL_RETRY_DELAY_SECONDS=5

# SMTP Fallback
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAILS_FROM_EMAIL=your-email@gmail.com
EMAILS_FROM_NAME=TRITIQ ERP

# OAuth2 Configuration (Future)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
MICROSOFT_CLIENT_ID=your-microsoft-client-id
MICROSOFT_CLIENT_SECRET=your-microsoft-client-secret
```

## API Endpoints

### Password Reset Endpoints

#### Request Password Reset
```http
POST /api/v1/mail/password/request-reset
Content-Type: application/json

{
  "email": "user@example.com"
}
```

Response:
```json
{
  "message": "If the email exists in our system, a password reset link has been sent.",
  "email": "user@example.com"
}
```

#### Confirm Password Reset
```http
POST /api/v1/mail/password/confirm-reset
Content-Type: application/json

{
  "email": "user@example.com",
  "token": "secure-token-here",
  "new_password": "NewSecurePassword123!"
}
```

Response:
```json
{
  "message": "Password reset successfully",
  "access_token": "jwt-token-here",
  "token_type": "bearer"
}
```

### Admin Email Logs
```http
GET /api/v1/admin/email-logs?organization_id=1&status=sent&limit=50
Authorization: Bearer {admin-jwt-token}
```

Query Parameters:
- `organization_id`: Filter by organization (optional)
- `email_type`: Filter by email type (optional)
- `status`: Filter by send status (optional)
- `provider`: Filter by email provider (optional)
- `limit`: Number of records to return (default: 100)
- `offset`: Pagination offset (default: 0)

## Database Schema

### EmailSend Table
```sql
CREATE TABLE email_sends (
    id SERIAL PRIMARY KEY,
    to_email VARCHAR(255) NOT NULL,
    from_email VARCHAR(255) NOT NULL,
    subject VARCHAR(500) NOT NULL,
    email_type emailtype NOT NULL,
    provider_used emailprovider NOT NULL,
    status emailstatus NOT NULL DEFAULT 'pending',
    organization_id INTEGER REFERENCES organizations(id),
    user_id INTEGER REFERENCES users(id),
    provider_response JSONB,
    provider_message_id VARCHAR(255),
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    sent_at TIMESTAMP WITH TIME ZONE,
    delivered_at TIMESTAMP WITH TIME ZONE,
    failed_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE,
    is_brevo_enabled BOOLEAN DEFAULT true
);
```

### User Reset Token Fields
```sql
ALTER TABLE users ADD COLUMN reset_token VARCHAR;
ALTER TABLE users ADD COLUMN reset_token_expires TIMESTAMP WITH TIME ZONE;
ALTER TABLE users ADD COLUMN reset_token_used BOOLEAN DEFAULT false;
```

## Email Templates

Email templates are located in `app/templates/email/`:
- `password_reset.html`: Password reset notification (admin-initiated)
- `user_creation.html`: New user welcome email
- `factory_reset_otp.html`: Factory reset OTP email

Template variables are replaced using simple string substitution:
```html
<p>Dear {{user_name}},</p>
<p>Your new password is: {{new_password}}</p>
```

## Testing

### Mock Providers for Testing
```python
# In test settings
ENABLE_BREVO_EMAIL = False
EMAIL_FALLBACK_ENABLED = False
# This will cause emails to "fail" and be logged without actually sending
```

### Verify Audit Trail
```python
from app.models import EmailSend, EmailStatus

# Check email was logged
email_log = db.query(EmailSend).filter(
    EmailSend.to_email == "test@example.com"
).first()

assert email_log.status == EmailStatus.SENT
assert email_log.provider_used == EmailProvider.BREVO
```

## Security Considerations

### Token Security
- Reset tokens are hashed using bcrypt before storage
- Tokens are single-use and automatically invalidated after use
- 1-hour expiry time prevents token reuse attacks

### Data Protection
- Provider API responses are redacted before logging
- Sensitive fields (api_key, password, etc.) are replaced with "[REDACTED]"
- Email content is not stored in audit logs

### Rate Limiting
- Consider implementing rate limiting on reset endpoints
- Monitor for abuse via admin email logs dashboard

## Monitoring & Alerting

### Metrics to Monitor
- Email send success rate by provider
- Average retry count before success
- Failed email count by organization
- Provider response times

### Log Analysis
- All email operations are logged with structured data
- Use `EmailSend` table for detailed analytics
- Admin logs endpoint provides real-time monitoring

## Troubleshooting

### Common Issues
1. **Brevo API failures**: Check API key and rate limits
2. **SMTP authentication**: Verify credentials and app passwords
3. **Template not found**: Ensure templates exist in `app/templates/email/`
4. **Token expiry**: Reset tokens expire after 1 hour

### Debug Logging
```python
import logging
logging.getLogger('app.services.email_service').setLevel(logging.DEBUG)
```

This will provide detailed logs of the email sending process including provider attempts, retries, and error details.