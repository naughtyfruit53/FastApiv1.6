# OAuth2 Email Integration Setup Guide

This guide explains how to set up and use the OAuth2 email integration functionality for Google and Microsoft email accounts.

## Features

### Frontend Features
- **OAuth2 Login Buttons**: Secure login for Google/Microsoft accounts
- **Email Compose**: Rich email composition with HTML support  
- **Email Reader**: View emails with attachments and reply functionality
- **Token Management**: View and manage connected email accounts

### Backend Features
- **OAuth2 Endpoints**: Complete OAuth2 flow for Google/Microsoft
- **Encrypted Token Storage**: Secure storage of OAuth tokens using field-level encryption
- **Automatic Token Refresh**: Seamless token renewal when expired
- **Email API Integration**: Gmail API and Microsoft Graph integration
- **Security Best Practices**: HTTPS enforcement, limited scopes, encrypted secrets

## Prerequisites

### 1. Google Cloud Console Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing project
3. Enable the Gmail API:
   - Go to "APIs & Services" > "Library"
   - Search for "Gmail API" and enable it
4. Create OAuth2 credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth 2.0 Client IDs"
   - Set application type to "Web application"
   - Add authorized redirect URIs:
     - `http://localhost:3000/auth/callback` (development)
     - `https://yourdomain.com/auth/callback` (production)
5. Note down the Client ID and Client Secret

### 2. Microsoft Azure App Registration

1. Go to [Azure Portal](https://portal.azure.com/)
2. Navigate to "Azure Active Directory" > "App registrations"
3. Click "New registration"
4. Configure:
   - Name: Your app name
   - Supported account types: "Accounts in any organizational directory and personal Microsoft accounts"
   - Redirect URI: Web - `http://localhost:3000/auth/callback`
5. After creation, note down:
   - Application (client) ID
   - Directory (tenant) ID
6. Create a client secret:
   - Go to "Certificates & secrets"
   - Click "New client secret"
   - Note down the secret value (shown only once)
7. Configure API permissions:
   - Go to "API permissions"
   - Add permissions for Microsoft Graph:
     - `Mail.Read`
     - `Mail.Send` 
     - `Mail.ReadWrite`
     - `User.Read`

## Environment Configuration

Add the following environment variables to your `.env` file:

```bash
# Google OAuth2
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

# Microsoft OAuth2  
MICROSOFT_CLIENT_ID=your_microsoft_client_id
MICROSOFT_CLIENT_SECRET=your_microsoft_client_secret
MICROSOFT_TENANT_ID=common

# OAuth2 Redirect URI
OAUTH_REDIRECT_URI=http://localhost:3000/auth/callback

# Encryption Keys (generate using the command below)
ENCRYPTION_KEY_PII=your_base64_encoded_encryption_key
```

### Generate Encryption Keys

```bash
# Generate encryption key for PII data
python -c "from cryptography.fernet import Fernet; import base64; print(f'ENCRYPTION_KEY_PII={base64.b64encode(Fernet.generate_key()).decode()}')"
```

## Database Setup

Run the SQL script to create the required tables:

```bash
# Connect to your PostgreSQL database and run:
psql -d your_database -f sql/oauth_tables.sql
```

This creates:
- `user_email_tokens` table for encrypted OAuth token storage
- `oauth_states` table for temporary OAuth state management
- Proper indexes and constraints for security and performance
- Cleanup functions for expired states

## Frontend Integration

### 1. OAuth Login Button

```tsx
import OAuthLoginButton from '../components/OAuthLoginButton';

// In your component
<OAuthLoginButton 
  variant="button"
  onSuccess={(result) => {
    console.log('OAuth success:', result);
    // Refresh email accounts or redirect
  }}
  onError={(error) => {
    console.error('OAuth error:', error);
    // Handle error
  }}
/>
```

### 2. Email Compose

```tsx
import EmailCompose from '../components/EmailCompose';

const [showCompose, setShowCompose] = useState(false);

<EmailCompose
  open={showCompose}
  onClose={() => setShowCompose(false)}
  onSuccess={() => {
    // Email sent successfully
    setShowCompose(false);
  }}
/>
```

### 3. Email Reader

```tsx
import EmailReader from '../components/EmailReader';

<EmailReader
  tokenId={selectedTokenId}
  messageId={selectedMessageId}
  onReply={(messageId, subject, sender) => {
    // Handle reply action
  }}
/>
```

## Backend API Usage

### 1. OAuth2 Flow

```bash
# 1. Get available providers
GET /api/v1/oauth/providers

# 2. Initiate OAuth flow
POST /api/v1/oauth/login/google
# Returns authorization_url - redirect user to this URL

# 3. Handle callback (automatic)
POST /api/v1/oauth/callback/google?code=...&state=...
```

### 2. Token Management

```bash
# List user's tokens
GET /api/v1/oauth/tokens

# Get token details
GET /api/v1/oauth/tokens/{token_id}

# Update token settings
PUT /api/v1/oauth/tokens/{token_id}

# Refresh token
POST /api/v1/oauth/tokens/{token_id}/refresh

# Revoke token
DELETE /api/v1/oauth/tokens/{token_id}
```

### 3. Email Operations

```bash
# List emails
GET /api/v1/email/tokens/{token_id}/emails?folder=INBOX&limit=50

# Get email detail
GET /api/v1/email/tokens/{token_id}/emails/{message_id}

# Send email
POST /api/v1/email/tokens/{token_id}/emails/send
{
  "to": ["recipient@example.com"],
  "subject": "Test Subject",
  "body": "Email content",
  "html_body": "<p>HTML content</p>"
}

# Mark email as read/unread
POST /api/v1/email/tokens/{token_id}/emails/{message_id}/mark-read
POST /api/v1/email/tokens/{token_id}/emails/{message_id}/mark-unread
```

## Security Considerations

### 1. Encryption
- All OAuth tokens are encrypted using field-level encryption
- Uses separate encryption keys for different data types
- Tokens are never stored in plain text

### 2. Token Security
- Tokens automatically refresh when expired
- Failed refresh attempts are logged and tracked
- Revoked tokens cannot be used

### 3. Scope Limitations
- **Google**: Only requests Gmail read/send permissions
- **Microsoft**: Only requests Mail read/write and basic user info
- No access to contacts, calendar, or other sensitive data

### 4. Transport Security
- All OAuth flows use HTTPS in production
- State parameters prevent CSRF attacks
- PKCE used for additional security

## Testing

Run the OAuth tests:

```bash
# Run OAuth-specific tests
python -m pytest tests/test_oauth.py -v

# Run all tests
python -m pytest tests/ -v
```

## Troubleshooting

### Common Issues

1. **"OAuth2 not configured"**
   - Check that `GOOGLE_CLIENT_ID` or `MICROSOFT_CLIENT_ID` are set
   - Verify environment variables are loaded correctly

2. **"Invalid redirect URI"**
   - Ensure redirect URI in OAuth provider matches `OAUTH_REDIRECT_URI`
   - Check that URI is properly registered in Google/Microsoft console

3. **"Token refresh failed"**
   - Check that refresh token is valid
   - Verify OAuth app permissions haven't changed
   - User may need to re-authenticate

4. **"Encryption failed"**
   - Ensure `ENCRYPTION_KEY_PII` is properly set
   - Verify encryption key is valid base64-encoded Fernet key

### Debug Mode

Enable debug logging:

```bash
# In your .env file
DEBUG=true
LOG_LEVEL=DEBUG
```

### Health Checks

```bash
# Check OAuth providers
curl http://localhost:8000/api/v1/oauth/providers

# Check token status
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     http://localhost:8000/api/v1/oauth/tokens
```

## Production Deployment

### 1. Environment Variables
- Use proper production OAuth redirect URIs
- Generate strong encryption keys
- Set secure database connection strings

### 2. Database
- Run database migrations
- Set up regular cleanup of expired OAuth states
- Monitor token refresh rates

### 3. Monitoring
- Monitor OAuth success/failure rates
- Track token refresh patterns
- Set up alerts for encryption failures

### 4. Backup
- Backup encryption keys securely
- Regular database backups including encrypted token data
- Test restore procedures

## API Reference

For complete API documentation, visit `/docs` when the server is running to see the interactive Swagger documentation.

## Support

For issues or questions:
1. Check the logs for specific error messages
2. Verify environment configuration
3. Test with a fresh OAuth flow
4. Check provider (Google/Microsoft) service status