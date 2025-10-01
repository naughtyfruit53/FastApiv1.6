# Email Module Documentation

## Overview

The Email Module provides comprehensive email management functionality including IMAP/SMTP synchronization, OAuth2 authentication, background processing, secure email storage, and **role-based automatic BCC** for organizational email hierarchy. This module integrates with popular email providers like Gmail and Outlook while maintaining strong security and performance standards.

## New Feature: Mail 1 Level Up

The "Mail 1 Level Up" feature provides automatic role-based BCC functionality to ensure organizational transparency and communication flow. When enabled by an organization super admin:

- **Executive emails** → Automatically BCC their assigned Manager
- **Manager emails** → Automatically BCC all Management users  
- **Management emails** → No BCC (top level)

### Configuration
- Toggle available in Organization Settings (super admin only)
- Database field: `organization_settings.mail_1_level_up_enabled`
- Respects user reporting relationships and role hierarchy
- Works with all email sending methods (Brevo API, SMTP fallback)

### API Integration
```python
from app.services.email_service import email_service

# Send email with automatic role-based BCC
success, error = email_service.send_email_with_role_bcc(
    db=db,
    to_email="customer@example.com",
    subject="Important Update",
    body="Email content here",
    sender_user=current_user  # BCC recipients determined by user's role
)
```

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
   - Email compose with automatic BCC

5. **Organization Settings** (`app/models/organization_settings.py`)
   - Mail 1 Level Up configuration
   - Organization-wide email preferences
   - Admin-controlled feature toggles

6. **Role Hierarchy Service** (`app/services/role_hierarchy_service.py`)
   - Role-based BCC recipient determination
   - User hierarchy validation
   - Organizational reporting structure support

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
- **NEW**: `POST /api/v1/email/compose` - Compose email with automatic BCC

### Organization Settings

- `GET /api/v1/organizations/settings/` - Get organization settings
- `PUT /api/v1/organizations/settings/` - Update organization settings (including Mail 1 Level Up toggle)

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

### Frontend Navigation Issues

4. **Account Selector Not Clickable**
   - **Symptom**: Email accounts are visible but not selectable/clickable
   - **Solution**: Ensure the `onAccountSelect` handler is passed to the Inbox component
   - **Fixed in**: v1.6 - Account boxes now have onClick handlers with hover effects
   - **Verification**: Click on an account in the sidebar - it should highlight and switch the active account

5. **404 Errors on Email Module Pages**
   - **Symptom**: Navigation to settings, search, or attachments returns 404
   - **Root Cause**: Missing view types in the main email module router
   - **Solution**: Views for settings, search, and attachments are now integrated in the main index.tsx
   - **Available Views**:
     - `inbox` - Email list with folder navigation (INBOX, SENT, ARCHIVED, DELETED)
     - `thread` - Thread view for email conversations
     - `compose` - Email composition interface
     - `settings` - Email account settings (click gear icon in toolbar)
     - `search` - Email search interface
     - `attachments` - Attachment management
   - **Navigation**: Use the folder sidebar in Inbox for folder-based navigation, or toolbar icons for settings

6. **Account Switching Not Working**
   - **Symptom**: Clicking on different accounts doesn't change the displayed emails
   - **Solution**: 
     - Verify `oauth_token_id` is properly set on MailAccount records
     - Check EmailContext is properly providing `selectedToken` state
     - Ensure `handleAccountSelect` maps account ID to token ID correctly
   - **Debug**:
     ```typescript
     // Check if account has oauth_token_id
     console.log('Account:', account.oauth_token_id);
     // Check selected token
     console.log('Selected Token:', selectedToken);
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

### Frontend Implementation

### Email Module Components

The frontend email module consists of three main components:

#### 1. Inbox Component (`frontend/src/pages/email/Inbox.tsx`)

The main email list interface with:
- Email list with pagination and filtering
- Folder navigation (Inbox, Sent, Archived, Trash)
- Real-time sync functionality
- OAuth account integration
- Search and status filtering

**Usage:**
```tsx
import Inbox from '../pages/email/Inbox';

<Inbox
  selectedAccount={selectedAccount}
  onEmailSelect={(email) => handleEmailClick(email)}
  onThreadSelect={(threadId) => handleThreadView(threadId)}
  onCompose={() => handleCompose()}
/>
```

#### 2. ThreadView Component (`frontend/src/pages/email/ThreadView.tsx`)

Email conversation interface with:
- Expandable email messages in conversation
- Attachment preview and download
- Reply/Reply All/Forward actions
- Email status management
- HTML content sanitization

**Usage:**
```tsx
import ThreadView from '../pages/email/ThreadView';

<ThreadView
  threadId={threadId}
  onBack={() => setView('inbox')}
  onReply={(email) => handleReply(email)}
  onReplyAll={(email) => handleReplyAll(email)}
  onForward={(email) => handleForward(email)}
/>
```

#### 3. Composer Component (`frontend/src/pages/email/Composer.tsx`)

## ERP Integrations & Advanced Features

### Voucher Email Integration

The email module integrates seamlessly with ERP voucher workflows:

```python
from app.services.email_service import send_voucher_email

# Send voucher email
success, error = send_voucher_email(
    voucher_type="purchase_voucher",
    voucher_id=123,
    recipient_email="vendor@example.com",
    recipient_name="Vendor Name",
    organization_id=1,
    user_id=1
)
```

**Supported Voucher Types:**
- Purchase Vouchers
- Sales Vouchers  
- Purchase Orders
- Sales Orders
- Quotations
- Delivery Challans
- And more...

### Calendar and Task Sync (.ics Integration)

Parse and sync calendar events and tasks from .ics files:

```python
from app.services.calendar_sync_service import calendar_sync_service

# Parse .ics attachment
result = calendar_sync_service.parse_ics_attachment(attachment_id, organization_id)

if result["success"]:
    events = result["events"]
    tasks = result["tasks"]
    
    # Sync to database
    calendar_sync_service.sync_events_to_database(events, user_id)
    calendar_sync_service.sync_tasks_to_database(tasks, user_id)
```

**API Endpoints:**
- `POST /api/v1/email/attachments/{attachment_id}/parse-calendar` - Parse .ics file
- `POST /api/v1/email/calendar/sync-events` - Sync events to calendar
- `POST /api/v1/email/calendar/sync-tasks` - Sync tasks to task management

### Customer/Vendor Email Linking

Automatically link emails to customers and vendors:

```python
from app.services.email_service import link_email_to_customer_vendor, auto_link_emails_by_sender

# Manual linking
success, error = link_email_to_customer_vendor(
    email_id=123,
    customer_id=456,
    user_id=1
)

# Auto-linking by sender email
result = auto_link_emails_by_sender(organization_id, limit=100)
```

**API Endpoints:**
- `POST /api/v1/email/emails/{email_id}/link` - Link email to customer/vendor
- `POST /api/v1/email/auto-link` - Auto-link emails by sender addresses

### Advanced Full-Text Search

PostgreSQL tsvector-powered search across email content:

```python
from app.services.email_search_service import email_search_service

# Full-text search
result = email_search_service.full_text_search(
    query="invoice payment terms",
    organization_id=1,
    customer_id=123,  # Optional filter
    date_from="2024-01-01",  # Optional filter
    has_attachments=True,  # Optional filter
    limit=50
)
```

**Search Features:**
- Full-text search across subject, body, sender information
- Customer/vendor filtering
- Date range filtering
- Attachment presence filtering
- Search ranking and snippets
- Search term suggestions

**API Endpoints:**
- `GET /api/v1/email/search` - Full-text email search
- `GET /api/v1/email/search/attachments` - Search attachments
- `GET /api/v1/email/search/by-customer-vendor` - Search by linked entities

### OCR Processing for Attachments

Extract text from email attachments using OCR:

```python
from app.services.ocr_service import email_attachment_ocr_service

# Process single attachment
result = await email_attachment_ocr_service.process_email_attachment(attachment_id)

# Batch processing
result = await email_attachment_ocr_service.batch_process_attachments([id1, id2, id3])
```

**Supported Formats:**
- Images: JPG, PNG, TIFF, BMP
- Documents: PDF (with fallback OCR for scanned content)

**API Endpoints:**
- `POST /api/v1/email/attachments/{attachment_id}/ocr` - Process single attachment
- `POST /api/v1/email/attachments/batch-ocr` - Batch OCR processing

### AI-Powered Features

Intelligent email analysis and assistance:

```python
from app.services.email_ai_service import email_ai_service

# Generate email summary
summary = email_ai_service.generate_email_summary(email_id)

# Get reply suggestions
suggestions = email_ai_service.generate_reply_suggestions(email_id, context="urgent")

# Extract action items
actions = email_ai_service.extract_action_items(email_id)

# Batch categorization
categories = email_ai_service.categorize_email_batch([email1, email2, email3])
```

**AI Capabilities:**
- Email summarization with key points extraction
- Sentiment analysis (positive/negative/neutral)
- Automatic categorization (finance, procurement, support, etc.)
- Reply suggestions based on email type and context
- Action item and deadline extraction
- Urgency level assessment
- Task creation suggestions

**API Endpoints:**
- `GET /api/v1/email/ai/summary/{email_id}` - Get AI-powered email summary
- `GET /api/v1/email/ai/reply-suggestions/{email_id}` - Get reply suggestions
- `POST /api/v1/email/ai/categorize-batch` - Batch email categorization
- `GET /api/v1/email/ai/action-items/{email_id}` - Extract action items

### Shared Inboxes & Role-Based Access

Implement shared inbox functionality with RBAC:

```python
# RBAC Permissions
ADMIN_PERMISSIONS = ["email:admin"]           # Full access
MANAGER_PERMISSIONS = ["email:manage"]        # Manage accounts and emails  
USER_PERMISSIONS = ["email:read"]             # Read-only access

# Shared inbox configuration
mail_account.is_shared = True  # Make account accessible to team
```

**Access Control:**
- Organization-level multi-tenancy
- Role-based permissions (admin, manager, user)
- Shared inbox support
- User assignment for shared accounts

**API Endpoints:**
- `GET /api/v1/email/shared-inboxes` - List accessible shared inboxes

## Advanced Configuration

### PostgreSQL Full-Text Search Setup

For optimal search performance, create tsvector indexes:

```sql
-- Create tsvector index for email search
CREATE INDEX idx_email_search_vector ON emails 
USING gin(to_tsvector('english', coalesce(subject, '') || ' ' || coalesce(body_text, '')));

-- Create index for attachment search (if OCR text is stored)
CREATE INDEX idx_attachment_search_vector ON email_attachments 
USING gin(to_tsvector('english', coalesce(extracted_text, '')));
```

### Calendar Integration Setup

1. Install required dependencies:
```bash
pip install icalendar==6.0.1 python-dateutil==2.8.2
```

2. Configure external_id fields for sync tracking:
```python
# Add external_id fields to models for calendar sync
task.external_id = "calendar-task-uuid"
event.external_id = "calendar-event-uuid"
```

### OCR Setup

1. Install Tesseract OCR engine:
```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# macOS
brew install tesseract
```

2. Install Python dependencies:
```bash
pip install pytesseract==0.3.13 pymupdf==1.26.4
```

### AI Integration

The current implementation uses rule-based approaches with hooks for AI integration:

- **Sentiment Analysis:** Keyword-based positive/negative detection
- **Categorization:** Pattern matching for ERP categories
- **Reply Suggestions:** Template-based responses by email type
- **Action Items:** Regex pattern extraction

For production AI integration, consider:
- OpenAI GPT API for advanced text analysis
- Local LLM models for privacy-sensitive deployments
- Custom trained models for domain-specific categorization

## API Integration Examples

### Frontend Integration

```typescript
// Email search with advanced filters
const searchEmails = async (query: string, filters: SearchFilters) => {
  const response = await api.get('/api/v1/email/search', {
    params: { query, ...filters }
  });
  return response.data;
};

// Parse calendar attachment
const parseCalendar = async (attachmentId: number) => {
  const response = await api.post(`/api/v1/email/attachments/${attachmentId}/parse-calendar`);
  return response.data;
};

// Get AI summary
const getEmailSummary = async (emailId: number) => {
  const response = await api.get(`/api/v1/email/ai/summary/${emailId}`);
  return response.data;
};
```

### Workflow Integration

```python
# Example: Auto-process new purchase order emails
async def process_purchase_order_email(email_id: int):
    # 1. Categorize email
    category = email_ai_service.categorize_email_batch([email_id])
    
    if category == "procurement":
        # 2. Extract action items
        actions = email_ai_service.extract_action_items(email_id)
        
        # 3. Process attachments with OCR
        if email.has_attachments:
            attachments = get_email_attachments(email_id)
            for attachment in attachments:
                if attachment.filename.endswith('.pdf'):
                    ocr_result = await email_attachment_ocr_service.process_email_attachment(attachment.id)
        
        # 4. Auto-link to vendor
        auto_link_result = auto_link_emails_by_sender(email.organization_id, limit=1)
        
        # 5. Create follow-up tasks
        for action in actions["suggested_tasks"]:
            create_task(action)
```

## Performance Considerations

### Database Optimization

1. **Indexes:** Ensure proper indexing for search and filtering
2. **Partitioning:** Consider partitioning large email tables by date
3. **Archival:** Implement email archival strategy for old messages

### Search Performance

1. **tsvector Indexes:** Use GIN indexes for full-text search
2. **Search Caching:** Cache frequent search queries
3. **Pagination:** Implement proper pagination for large result sets

### OCR Processing

1. **Async Processing:** Process OCR in background tasks
2. **File Size Limits:** Implement reasonable file size limits
3. **Format Validation:** Validate file formats before processing

## Troubleshooting

### Common Issues

1. **Database Connection Errors:**
   - Ensure DATABASE_URL is properly configured
   - For development with SQLite, use: `sqlite+aiosqlite:///./test.db`
   - For production with PostgreSQL, use: `postgresql+asyncpg://user:pass@host/db`

2. **OCR Processing Failures:**
   - Verify Tesseract is installed: `tesseract --version`
   - Check file permissions for temporary directory
   - Ensure supported file formats

3. **Search Not Working:**
   - Verify PostgreSQL full-text search extensions
   - Check tsvector indexes are created
   - For SQLite, search functionality is limited

4. **Calendar Sync Issues:**
   - Validate .ics file format
   - Check timezone handling
   - Verify external_id uniqueness

### Monitoring and Logging

Enable detailed logging for troubleshooting:

```python
import logging
logging.getLogger('app.services.email_search_service').setLevel(logging.DEBUG)
logging.getLogger('app.services.calendar_sync_service').setLevel(logging.DEBUG)
logging.getLogger('app.services.email_ai_service').setLevel(logging.DEBUG)
```

## Future Enhancements

### Planned Features

1. **Advanced AI Integration:**
   - Integration with OpenAI GPT models
   - Custom email classification models
   - Automatic email routing

2. **Enhanced Search:**
   - Elasticsearch integration
   - Advanced search filters
   - Search analytics

3. **Calendar Improvements:**
   - Two-way calendar sync
   - Meeting room booking integration
   - Calendar conflict detection

4. **Mobile Support:**
   - Mobile-optimized email interface
   - Push notifications
   - Offline email access

5. **Integration Enhancements:**
   - Microsoft Graph API integration
   - Google Workspace integration
   - Webhook support for real-time updates

### Contributing

To contribute to the email module:

1. Follow the existing code patterns
2. Add comprehensive tests for new features
3. Update documentation for any API changes
4. Ensure RBAC compliance for new endpoints
5. Consider performance implications for large datasets

Email composition interface with:
- Rich text editor with formatting
- Attachment upload and management
- Template integration for vouchers
- Priority settings and delivery options
- Reply/Forward prefilling

**Usage:**
```tsx
import Composer from '../pages/email/Composer';

<Composer
  mode="new" // or "reply", "replyAll", "forward"
  originalEmail={originalEmail} // for replies/forwards
  selectedAccount={selectedAccount}
  onClose={() => setView('inbox')}
  onSent={(emailId) => handleEmailSent(emailId)}
/>
```

### Email Service Integration

The enhanced email service (`frontend/src/services/emailService.ts`) provides:

#### Core Operations
```tsx
import { emailService } from '../services/emailService';

// Fetch mail accounts
const accounts = await emailService.getMailAccounts();

// Get emails for account
const emailsResponse = await emailService.getEmails(
  accountId,
  'INBOX', // folder
  50,      // limit
  0,       // offset
  'unread' // status filter
);

// Send composed email
const result = await emailService.composeEmail(emailData, accountId);

// Update email status
await emailService.updateEmailStatus(emailId, 'read');

// Trigger manual sync
await emailService.triggerSync(accountId);
```

#### Template Integration
```tsx
// Get available templates
const templates = await emailService.getEmailTemplates();

// Apply template with data
const rendered = await emailService.applyTemplate(templateId, {
  customer_name: 'John Doe',
  invoice_number: 'INV-001',
  amount: 1000
});
```

### OAuth Integration Setup

#### Frontend OAuth Flow

1. **Initialize OAuth Flow**
```tsx
import { useOAuth } from '../hooks/useOAuth';

const { initiateOAuthFlow, getProviders } = useOAuth();

// Get available providers
const providers = await getProviders();

// Start OAuth flow
await initiateOAuthFlow('google');
// This redirects to provider, then back to callback
```

2. **OAuth Callback Handling**
```tsx
// In your OAuth callback page
const { handleOAuthCallback } = useOAuth();

const handleCallback = async () => {
  const urlParams = new URLSearchParams(window.location.search);
  const code = urlParams.get('code');
  const state = urlParams.get('state');
  const provider = localStorage.getItem(`oauth_provider_${state}`);

  if (code && state && provider) {
    try {
      await handleOAuthCallback(provider, code, state);
      // Redirect to email module
      router.push('/email');
    } catch (error) {
      console.error('OAuth callback failed:', error);
    }
  }
};
```

3. **OAuth Login Button**
```tsx
import OAuthLoginButton from '../components/OAuthLoginButton';

<OAuthLoginButton
  variant="button" // or "list"
  onError={(error) => setError(error)}
/>
```

### Navigation Integration

The email module is integrated into the main navigation:

```tsx
// In menuConfig.tsx
email: {
  title: 'Email',
  icon: <Email />,
  sections: [
    {
      title: 'Email Management',
      items: [
        { name: 'Inbox', path: '/email', icon: <Email /> },
        { name: 'Compose', path: '/email?compose=true', icon: <NoteAdd /> },
        { name: 'Account Settings', path: '/email/accounts', icon: <Settings /> }
      ]
    }
  ]
}
```

### Testing

#### Unit Tests

```bash
# Run email module tests
npm test -- --testPathPattern=email

# Run specific test files
npm test emailService.test.ts
npm test Inbox.test.tsx
```

#### E2E Test Structure

```tsx
// Example E2E test for email workflow
describe('Email Module E2E', () => {
  it('should complete email workflow', async () => {
    // 1. OAuth login
    await page.goto('/email');
    await page.click('[data-testid="oauth-login-button"]');
    
    // 2. Select provider and authenticate
    await page.click('text=Connect Google');
    // Handle OAuth flow...
    
    // 3. Verify inbox loads
    await page.waitForSelector('[data-testid="email-list"]');
    
    // 4. Compose and send email
    await page.click('text=Compose');
    await page.fill('[placeholder="Enter email addresses"]', 'test@example.com');
    await page.fill('[placeholder="Subject"]', 'Test Email');
    await page.fill('.ql-editor', 'Test email content');
    await page.click('text=Send');
    
    // 5. Verify email sent
    await page.waitForSelector('text=Email sent successfully');
  });
});
```

### Attachment Handling

#### Upload Attachments
```tsx
const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
  const files = event.target.files;
  if (files) {
    const newAttachments = Array.from(files).map(file => 
      Object.assign(file, { id: generateId() })
    );
    setAttachments([...attachments, ...newAttachments]);
  }
};
```

#### Download Attachments
```tsx
const handleDownload = async (attachmentId: number) => {
  try {
    const response = await emailService.downloadAttachment(attachmentId);
    // Handle download response
    console.log('Download started:', response.filename);
  } catch (error) {
    console.error('Download failed:', error);
  }
};
```

### Inline Images and Rich Content

The composer uses ReactQuill for rich text editing:

```tsx
const quillModules = {
  toolbar: [
    [{ 'header': '1'}, {'header': '2'}],
    ['bold', 'italic', 'underline', 'strike'],
    [{'list': 'ordered'}, {'list': 'bullet'}],
    ['link', 'image'],
    ['clean']
  ]
};

<ReactQuill
  value={body}
  onChange={setBody}
  modules={quillModules}
  style={{ height: '200px' }}
/>
```

### Mobile Responsiveness

The email components are built with mobile-first responsive design:

```tsx
// Mobile-responsive inbox layout
<Box sx={{ 
  display: 'flex', 
  flexDirection: { xs: 'column', md: 'row' },
  height: '100%' 
}}>
  <Box sx={{ 
    width: { xs: '100%', md: 240 },
    borderRight: { md: 1 },
    borderColor: 'divider'
  }}>
    {/* Sidebar */}
  </Box>
  <Box sx={{ flex: 1 }}>
    {/* Main content */}
  </Box>
</Box>
```

### Error Handling

Comprehensive error handling throughout the email module:

```tsx
// Service-level error handling
try {
  const result = await emailService.getEmails(accountId);
  return result;
} catch (error) {
  if (error.response?.status === 401) {
    // Handle authentication error
    redirectToLogin();
  } else if (error.response?.status === 403) {
    // Handle permission error
    showPermissionError();
  } else {
    // Handle general error
    showErrorMessage(error.message);
  }
  throw error;
}

// Component-level error boundaries
const { data, error, isLoading } = useQuery({
  queryKey: ['emails'],
  queryFn: () => emailService.getEmails(accountId),
  onError: (error) => {
    console.error('Failed to load emails:', error);
    setErrorMessage('Failed to load emails. Please try again.');
  }
});
```

## Contributing

To contribute improvements:

1. Follow existing code patterns
2. Add comprehensive tests
3. Update documentation
4. Consider security implications
5. Test with multiple providers