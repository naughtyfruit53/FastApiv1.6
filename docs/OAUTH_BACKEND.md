# OAuth2 Backend Implementation Guide

## Overview

This document describes the backend implementation of OAuth2 authentication for Google and Microsoft email accounts, including IMAP/SMTP XOAUTH2 support, token management, and security features.

## Architecture

### Components

1. **OAuth Service** (`app/services/oauth_service.py`)
   - Handles OAuth2 authorization flows
   - Token storage and refresh
   - Provider-specific configurations

2. **Email Sync Service** (`app/services/email_sync_service.py`)
   - IMAP/SMTP connection management
   - XOAUTH2 authentication
   - Email synchronization with exponential backoff retry

3. **Encryption Utilities**
   - Fernet encryption (`app/utils/encryption.py`)
   - AES-GCM encryption (`app/utils/crypto_aes_gcm.py`)

4. **API Endpoints**
   - OAuth flow endpoints (`app/api/v1/oauth.py`)
   - Health check endpoints (`app/api/v1/health.py`)

5. **CLI Tools**
   - Bulk token refresh (`scripts/refresh_oauth_tokens.py`)

## OAuth2 Flow

### 1. Authorization Request

```
GET /api/v1/oauth/login/{provider}
```

Creates an authorization URL and redirects user to provider's consent screen.

**Supported Providers:**
- `google` - Gmail/Google Workspace
- `microsoft` - Outlook/Office 365

**Security Features:**
- PKCE (Proof Key for Code Exchange) for Google
- Cryptographically secure state parameter
- Time-limited state validation (10 minutes)

### 2. Authorization Callback

```
GET /api/v1/oauth/callback/{provider}?code={code}&state={state}
```

Exchanges authorization code for access and refresh tokens.

**Process:**
1. Validates state parameter
2. Exchanges authorization code for tokens
3. Encrypts tokens using AES-GCM or Fernet
4. Stores in `user_email_tokens` table
5. Creates or updates associated `mail_accounts` entry
6. Triggers initial email sync

### 3. Token Storage

Tokens are stored in the `user_email_tokens` table with encryption:

```sql
CREATE TABLE user_email_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    organization_id INTEGER,
    provider VARCHAR(50) NOT NULL,
    email_address VARCHAR(255) NOT NULL,
    access_token_encrypted TEXT NOT NULL,
    refresh_token_encrypted TEXT,
    expires_at TIMESTAMP,
    status VARCHAR(50) NOT NULL,
    ...
);
```

**Encryption:**
- Access tokens: AES-GCM or Fernet encryption
- Refresh tokens: Separate encryption key
- PII data: Uses PII encryption key

### 4. Token Refresh

Tokens are automatically refreshed when:
- Expired and refresh token available
- Requested via API
- Bulk refresh CLI tool

**Exponential Backoff:**
- 3 retry attempts
- Base delay: 2 seconds
- Backoff: 2^attempt seconds (2s, 4s, 8s)

## IMAP/SMTP Authentication

### XOAUTH2 Authentication

The service uses standard XOAUTH2 authentication for Gmail and Outlook:

```python
# Auth string format
auth_string = f"user={email}\x01auth=Bearer {access_token}\x01\x01"

# Base64 encode for IMAP
auth_bytes = base64.b64encode(auth_string.encode('utf-8'))

# Authenticate
imap.authenticate('XOAUTH2', lambda x: auth_bytes)
```

### Connection Implementation

**Previous Issue (FIXED):**
- Custom `PreConnectedIMAP` class had `AttributeError: 'tagre'`
- Missing IMAP4 protocol attributes

**Current Implementation:**
- Uses standard `imaplib.IMAP4_SSL`
- Proper SSL context configuration
- TLS 1.2+ enforcement

```python
# Create SSL context
context = ssl.create_default_context()
context.check_hostname = True
context.verify_mode = ssl.CERT_REQUIRED
context.minimum_version = ssl.TLSVersion.TLSv1_2

# Connect
imap = imaplib.IMAP4_SSL(
    host=account.incoming_server,
    port=port,
    ssl_context=context,
    timeout=30
)
```

### Retry Logic

Email sync includes exponential backoff:

```python
max_retries = 3
base_delay = 2  # seconds

for attempt in range(max_retries):
    try:
        # Attempt sync
        ...
        break
    except Exception as e:
        if attempt < max_retries - 1:
            delay = base_delay * (2 ** attempt)
            time.sleep(delay)
```

## Encryption

### AES-GCM Encryption

New AES-GCM encryption provides:
- Confidentiality (encryption)
- Integrity (authentication tag)
- Additional Authenticated Data (AAD) support

```python
from app.utils.crypto_aes_gcm import encrypt_aes_gcm, decrypt_aes_gcm

# Encrypt with AAD
encrypted = encrypt_aes_gcm(
    access_token,
    key_id="oauth",
    aad=f"user:{user_id}"
)

# Decrypt with same AAD
decrypted = decrypt_aes_gcm(
    encrypted,
    key_id="oauth", 
    aad=f"user:{user_id}"
)
```

### Fernet Encryption

Existing Fernet encryption still supported:

```python
from app.utils.encryption import encrypt_field, decrypt_field, EncryptionKeys

encrypted = encrypt_field(value, EncryptionKeys.PII)
decrypted = decrypt_field(encrypted, EncryptionKeys.PII)
```

## API Endpoints

### OAuth Endpoints

#### Initiate OAuth Flow
```
GET /api/v1/oauth/login/{provider}
```

#### OAuth Callback
```
GET /api/v1/oauth/callback/{provider}?code={code}&state={state}
```

#### List User Tokens
```
GET /api/v1/oauth/tokens
```

#### Refresh Token
```
POST /api/v1/oauth/tokens/{token_id}/refresh
```

#### Revoke Token
```
POST /api/v1/oauth/tokens/{token_id}/revoke
```

### Health Endpoints

#### Email Sync Health
```
GET /api/v1/health/email-sync
```

Returns:
- Total/active/error account counts
- Recent sync activity (24h)
- Success rate

#### OAuth Token Health
```
GET /api/v1/health/oauth-tokens
```

Returns:
- Total/active/expired token counts
- Tokens expiring soon
- Refresh failure count

## CLI Tools

### Bulk Token Refresh

```bash
# List all tokens
python scripts/refresh_oauth_tokens.py --list

# Refresh all tokens expiring within 7 days
python scripts/refresh_oauth_tokens.py --refresh-all

# Refresh Google tokens only
python scripts/refresh_oauth_tokens.py --refresh-all --provider google

# Dry run (no changes)
python scripts/refresh_oauth_tokens.py --refresh-all --dry-run

# Refresh specific token
python scripts/refresh_oauth_tokens.py --token-id 123

# Refresh tokens expiring within 3 days
python scripts/refresh_oauth_tokens.py --refresh-all --days 3
```

## Environment Variables

### Required Variables

```bash
# Google OAuth2
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret

# Microsoft OAuth2
MICROSOFT_CLIENT_ID=your_client_id
MICROSOFT_CLIENT_SECRET=your_client_secret
MICROSOFT_TENANT_ID=common

# Encryption Keys
ENCRYPTION_KEY_PII=base64_encoded_key
ENCRYPTION_KEY_OAUTH_AES_GCM=base64_encoded_key

# OAuth Redirect
OAUTH_REDIRECT_URI=http://localhost:3000/auth/callback
```

### Generate Encryption Keys

```bash
# Fernet key (for PII)
python -c "from cryptography.fernet import Fernet; import base64; print(f'ENCRYPTION_KEY_PII={base64.b64encode(Fernet.generate_key()).decode()}')"

# AES-GCM key (for OAuth)
python -c "from cryptography.hazmat.primitives.ciphers.aead import AESGCM; import base64; print(f'ENCRYPTION_KEY_OAUTH_AES_GCM={base64.b64encode(AESGCM.generate_key(bit_length=256)).decode()}')"
```

## Security Best Practices

### Token Security
1. All tokens encrypted at rest
2. Separate encryption keys for different data types
3. Automatic token refresh before expiry
4. Revoked tokens cannot be used
5. Failed refresh attempts tracked and logged

### Network Security
1. TLS 1.2+ for all connections
2. Certificate verification enabled
3. HTTPS enforced in production
4. State parameter prevents CSRF

### Scope Limitations
- **Google**: Only `https://mail.google.com/` and user info
- **Microsoft**: Only `Mail.ReadWrite`, `Mail.Send`, and `User.Read`
- No calendar, contacts, or other data access

## Monitoring

### Health Checks

Check email sync health:
```bash
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/health/email-sync
```

Check OAuth token health:
```bash
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/health/oauth-tokens
```

### Logs

Key log events:
- OAuth authorization attempts
- Token refresh success/failure
- IMAP connection errors
- Authentication failures
- Sync operation results

### Metrics

Track:
- Token refresh success rate
- Email sync success rate
- Average sync duration
- Active vs. error accounts
- Tokens expiring soon

## Troubleshooting

### Common Issues

#### "Failed to connect to IMAP server"
- Check server/port configuration
- Verify firewall/network access
- Check SSL certificate validity
- Review logs for specific error

#### "OAuth authentication failed"
- Verify token not expired
- Check token status in database
- Try manual refresh
- Verify provider credentials

#### "Token refresh failed"
- Check refresh token validity
- Verify client credentials
- Check provider API status
- Review OAuth consent scope

### Debug Mode

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Testing

### Unit Tests

```bash
# Run all OAuth tests
pytest tests/test_oauth.py -v

# Run XOAUTH2 tests
pytest tests/test_xoauth2.py -v

# Run crypto tests
pytest tests/test_crypto_aes_gcm.py -v
```

### Integration Tests

Test IMAP connection:
```python
from app.services.email_sync_service import EmailSyncService
from app.models.email import MailAccount

service = EmailSyncService()
account = db.query(MailAccount).filter_by(id=1).first()
connection = service.get_imap_connection(account, db)

if connection:
    print("✓ IMAP connection successful")
    connection.logout()
else:
    print("✗ IMAP connection failed")
```

## Rollback Procedure

If issues occur after deployment:

1. **Disable OAuth Authentication:**
   ```sql
   UPDATE mail_accounts SET incoming_auth_method = 'password' WHERE incoming_auth_method IN ('oauth', 'oauth2', 'xoauth2');
   ```

2. **Stop Email Sync:**
   ```sql
   UPDATE mail_accounts SET sync_enabled = false;
   ```

3. **Revert Code:**
   ```bash
   git revert <commit_hash>
   git push
   ```

4. **Restart Services:**
   ```bash
   systemctl restart fastapi-app
   ```

5. **Monitor Logs:**
   ```bash
   tail -f /var/log/fastapi-app.log
   ```

## Future Enhancements

- [ ] Add support for Yahoo Mail
- [ ] Implement token rotation
- [ ] Add monitoring dashboard
- [ ] Support for shared mailboxes
- [ ] OAuth token caching layer
- [ ] Webhook for real-time sync
- [ ] Multi-factor authentication support

## References

- [Google OAuth2 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Microsoft OAuth2 Documentation](https://docs.microsoft.com/en-us/azure/active-directory/develop/v2-oauth2-auth-code-flow)
- [IMAP XOAUTH2 Specification](https://developers.google.com/gmail/imap/xoauth2-protocol)
- [AES-GCM Encryption](https://cryptography.io/en/latest/hazmat/primitives/aead/)
