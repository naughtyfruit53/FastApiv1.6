# Email Module Documentation

## Overview

The Email Module provides comprehensive email management functionality including IMAP/SMTP synchronization, OAuth2 authentication, background processing, and secure email storage. This module integrates with popular email providers like Gmail and Outlook while maintaining strong security and performance standards.

## Architecture

### Core Components

1. **Email Models** (`app/models/email.py`)
   - `MailAccount`: Email account configuration
   - `Email`: Individual email messages
   - `EmailThread`: Conversation threads
   - `EmailAttachment`: File attachments
   - `EmailSyncLog`: Sync operation logging

2. **Sync Service** (`app/services/email_sync_service.py`)
   - IMAP/SMTP connection management
   - OAuth2 authentication support
   - Email parsing and processing
   - HTML sanitization and security

3. **Background Worker** (`app/services/email_sync_worker.py`)
   - APScheduler-based sync scheduling
   - Batch processing and error handling
   - Health monitoring and cleanup

4. **API Layer** (`app/api/v1/email.py`)
   - RESTful endpoints with RBAC
   - Account management
   - Email retrieval and status updates
   - Sync control and monitoring

## Setup and Configuration

### Environment Variables

```bash
# Email Sync Configuration
EMAIL_SYNC_ENABLED=true
EMAIL_SYNC_INTERVAL_MINUTES=15
EMAIL_SYNC_MAX_WORKERS=3
EMAIL_SYNC_BATCH_SIZE=5
EMAIL_FULL_SYNC_DAYS=30

# OAuth2 Configuration
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
MICROSOFT_CLIENT_ID=your_microsoft_client_id
MICROSOFT_CLIENT_SECRET=your_microsoft_client_secret

# Database
DATABASE_URL=postgresql://user:pass@localhost/db
```

### Database Migration

Run the email module migration to create required tables:

```bash
# Apply migration
alembic upgrade head

# Or specific migration
alembic upgrade da9jdxsrvo2i
```

### Dependencies

The email module requires these additional Python packages (already in requirements.txt):

```
imaplib2==3.6
bleach>=6.0.0
beautifulsoup4>=4.12.0
apscheduler>=3.10.0
```

## OAuth2 Setup

### Google Gmail API

1. **Create Google Cloud Project**
   - Go to Google Cloud Console
   - Create new project or select existing
   - Enable Gmail API

2. **Configure OAuth2 Credentials**
   - Go to APIs & Services > Credentials
   - Create OAuth 2.0 Client ID
   - Add authorized redirect URIs:
     ```
     https://yourdomain.com/api/v1/oauth/google/callback
     ```

3. **Set Environment Variables**
   ```bash
   GOOGLE_CLIENT_ID=your_client_id
   GOOGLE_CLIENT_SECRET=your_client_secret
   ```

### Microsoft Outlook

1. **Azure AD App Registration**
   - Go to Azure Portal > Azure Active Directory
   - App registrations > New registration
   - Configure redirect URI and permissions

2. **Required Permissions**
   - Mail.Read
   - Mail.ReadWrite
   - User.Read

3. **Set Environment Variables**
   ```bash
   MICROSOFT_CLIENT_ID=your_client_id
   MICROSOFT_CLIENT_SECRET=your_client_secret
   ```

## Usage

### Creating Email Accounts

#### OAuth2 Account (Recommended)

```python
from app.services.oauth_service import OAuthService
from app.models.email import MailAccount, EmailAccountType

# First, obtain OAuth token through OAuth flow
oauth_service = OAuthService(db)
token = oauth_service.store_token(...)  # After OAuth callback

# Create email account
account = MailAccount(
    name="My Gmail Account",
    email_address="user@gmail.com",
    account_type=EmailAccountType.GMAIL_API,
    provider="google",
    oauth_token_id=token.id,
    sync_enabled=True,
    sync_frequency_minutes=15,
    sync_folders=["INBOX", "SENT"],
    organization_id=user.organization_id,
    user_id=user.id
)
db.add(account)
db.commit()
```

#### IMAP/SMTP with Password

```python
account = MailAccount(
    name="Corporate Email",
    email_address="user@company.com",
    account_type=EmailAccountType.IMAP,
    incoming_server="mail.company.com",
    incoming_port=993,
    incoming_ssl=True,
    incoming_auth_method="password",
    outgoing_server="smtp.company.com",
    outgoing_port=587,
    outgoing_ssl=True,
    username="user@company.com",
    password_encrypted=encrypt_field("password", EncryptionKeys.PII_KEY),
    sync_enabled=True,
    organization_id=user.organization_id,
    user_id=user.id
)
```

### Starting Sync Worker

```python
from app.services.email_sync_worker import start_email_sync_worker

# Start background worker
success = start_email_sync_worker()
if success:
    print("Email sync worker started successfully")
```

### Manual Sync

```python
from app.services.email_sync_service import EmailSyncService

sync_service = EmailSyncService()

# Sync specific account
success = sync_service.sync_account(account_id=1, full_sync=False)

# Or trigger via worker
from app.services.email_sync_worker import trigger_manual_sync
trigger_manual_sync(account_id=1)
```

### Retrieving Emails

```python
from app.services.email_service import email_management_service

# Get emails for account
emails = email_management_service.fetch_emails(
    account_id=1,
    folder="INBOX",
    limit=50,
    offset=0
)

# Get specific email
email_detail = email_management_service.get_email_detail(
    email_id=123,
    include_attachments=True
)
```

## API Endpoints

### Account Management

- `POST /api/v1/email/accounts` - Create email account
- `GET /api/v1/email/accounts` - List accounts
- `GET /api/v1/email/accounts/{id}` - Get account details
- `PUT /api/v1/email/accounts/{id}` - Update account
- `DELETE /api/v1/email/accounts/{id}` - Delete account

### Email Operations

- `GET /api/v1/email/accounts/{id}/emails` - Get emails
- `GET /api/v1/email/emails/{id}` - Get email details
- `PUT /api/v1/email/emails/{id}/status` - Update status
- `GET /api/v1/email/threads` - List threads
- `GET /api/v1/email/threads/{id}` - Get thread

### Sync Management

- `POST /api/v1/email/accounts/{id}/sync` - Trigger manual sync
- `GET /api/v1/email/accounts/{id}/status` - Get sync status
- `GET /api/v1/email/sync/status` - Get worker status
- `POST /api/v1/email/sync/start` - Start worker
- `POST /api/v1/email/sync/stop` - Stop worker

### OAuth Integration

- `GET /api/v1/email/oauth/tokens` - List OAuth tokens

## Security Features

### HTML Sanitization

All email HTML content is sanitized before storage:

```python
from app.utils.text_processing import sanitize_html

# Allowed tags and attributes
allowed_tags = ['p', 'br', 'div', 'span', 'strong', 'em', 'a', 'img']
allowed_attributes = {
    'a': ['href', 'title'],
    'img': ['src', 'alt', 'width', 'height']
}

clean_html = sanitize_html(raw_html, allowed_tags, allowed_attributes)
```

### RBAC Permissions

The email module implements role-based access control:

- `email:read` - Read emails and accounts
- `email:manage` - Create/update accounts and emails
- `email:admin` - Full administrative access

### Data Encryption

Sensitive data is encrypted before storage:

- Email account passwords
- OAuth tokens
- Attachment content (optional)

## Sync Cadence and Configuration

### Default Sync Settings

```python
# Account-level settings
sync_frequency_minutes = 15  # Sync every 15 minutes
sync_folders = ["INBOX"]     # Folders to sync
full_sync_completed = False  # Initial full sync status

# Worker settings
EMAIL_SYNC_INTERVAL_MINUTES = 15  # Worker check interval
EMAIL_SYNC_MAX_WORKERS = 3        # Concurrent sync operations
EMAIL_SYNC_BATCH_SIZE = 5         # Accounts per batch
```

### Sync Types

1. **Full Sync**: Complete synchronization of all emails (initial setup)
2. **Incremental Sync**: Only new messages since last sync
3. **Manual Sync**: User-triggered immediate sync

### Sync Monitoring

Monitor sync health through:

- `EmailSyncLog` table for detailed logs
- Account `sync_status` and `last_sync_error`
- Worker health check job (daily at 6 AM)
- Automatic account pausing for high error rates

## Limitations and Considerations

### Current Limitations

1. **Email Providers**
   - Full OAuth2 support for Gmail and Outlook
   - IMAP/SMTP for other providers
   - No POP3 support (security reasons)

2. **Sync Performance**
   - Batch processing limits concurrent operations
   - Large mailboxes may require extended initial sync
   - Rate limiting to avoid provider restrictions

3. **Storage**
   - Attachments stored in database (consider file storage for scale)
   - Full email content stored (consider archival strategy)
   - No automatic cleanup of old emails

4. **Search**
   - Basic database search only
   - No full-text search indexing
   - Limited search across email content

### Scalability Considerations

For production environments with high email volume:

1. **Migrate to Celery**
   ```python
   # Replace APScheduler with Celery for better scalability
   from celery import Celery
   
   app = Celery('email_sync')
   
   @app.task
   def sync_account_task(account_id):
       # Sync implementation
       pass
   ```

2. **External File Storage**
   - Use S3/MinIO for attachment storage
   - Implement file deduplication
   - Add virus scanning integration

3. **Database Optimization**
   - Implement email archival
   - Add read replicas for email retrieval
   - Consider time-based table partitioning

4. **Caching Layer**
   - Redis for frequently accessed emails
   - Cache folder hierarchies
   - Session-based pagination

## Troubleshooting

### Common Issues

1. **OAuth Token Expired**
   ```python
   # Check token status
   token_info = oauth_service.get_token_info(token_id)
   if token_info['is_expired']:
       # Token will be auto-refreshed on next use
       oauth_service.refresh_token(token_id)
   ```

2. **IMAP Connection Failed**
   ```bash
   # Check logs
   tail -f /var/log/email_sync.log
   
   # Common causes:
   # - Incorrect server/port settings
   # - Firewall blocking connection
   # - Invalid credentials
   # - Two-factor authentication required
   ```

3. **Sync Performance Issues**
   ```python
   # Reduce sync frequency for problem accounts
   account.sync_frequency_minutes = 60  # Hourly instead of 15min
   
   # Limit folder sync
   account.sync_folders = ["INBOX"]  # Skip large folders
   
   # Pause problematic accounts
   account.sync_status = EmailSyncStatus.PAUSED
   ```

### Debug Mode

Enable debug logging for troubleshooting:

```python
import logging
logging.getLogger('app.services.email_sync_service').setLevel(logging.DEBUG)
logging.getLogger('app.services.email_sync_worker').setLevel(logging.DEBUG)
```

### Health Checks

Monitor system health:

```python
from app.services.email_sync_worker import get_sync_worker_status

status = get_sync_worker_status()
print(f"Worker running: {status['running']}")
print(f"Scheduled jobs: {len(status['scheduled_jobs'])}")
```

## Migration Guide

### From Previous Email System

If migrating from an existing email system:

1. **Export existing data**
2. **Map to new schema**
3. **Run data migration script**
4. **Test sync functionality**
5. **Gradually migrate accounts**

### Schema Changes

The migration adds these tables:
- `mail_accounts` - Email account configurations
- `email_threads` - Conversation threads
- `emails` - Individual messages
- `email_attachments` - File attachments  
- `email_sync_logs` - Sync operation logs

### Rollback Plan

To rollback the email module:

1. **Stop sync worker**
   ```python
   from app.services.email_sync_worker import stop_email_sync_worker
   stop_email_sync_worker()
   ```

2. **Disable sync for all accounts**
   ```sql
   UPDATE mail_accounts SET sync_enabled = false;
   ```

3. **Revert migration**
   ```bash
   alembic downgrade abc123def456
   ```

## Performance Metrics

### Key Metrics to Monitor

1. **Sync Performance**
   - Average sync duration per account
   - Messages processed per minute
   - Error rate by provider

2. **Storage Usage**
   - Database size growth
   - Attachment storage usage
   - Archive effectiveness

3. **User Experience**
   - Email retrieval response time
   - Search query performance
   - API endpoint latency

### Monitoring Queries

```sql
-- Sync performance
SELECT 
    account_id,
    AVG(duration_seconds) as avg_duration,
    COUNT(*) as sync_count,
    SUM(CASE WHEN status = 'error' THEN 1 ELSE 0 END) as error_count
FROM email_sync_logs 
WHERE started_at >= NOW() - INTERVAL '24 hours'
GROUP BY account_id;

-- Storage usage
SELECT 
    COUNT(*) as total_emails,
    SUM(size_bytes) as total_size,
    AVG(size_bytes) as avg_email_size
FROM emails;

-- Active accounts
SELECT 
    sync_status,
    COUNT(*) as account_count
FROM mail_accounts 
GROUP BY sync_status;
```

## Support and Maintenance

### Regular Maintenance Tasks

1. **Daily**
   - Monitor sync logs for errors
   - Check worker status
   - Review storage usage

2. **Weekly** 
   - Clean up old sync logs
   - Review account health
   - Update OAuth tokens if needed

3. **Monthly**
   - Archive old emails
   - Review performance metrics
   - Update provider configurations

### Getting Help

For issues with the email module:

1. Check this documentation
2. Review application logs
3. Test with minimal configuration
4. Verify provider settings
5. Check network connectivity

### Contributing

To contribute improvements:

1. Follow existing code patterns
2. Add comprehensive tests
3. Update documentation
4. Consider security implications
5. Test with multiple providers