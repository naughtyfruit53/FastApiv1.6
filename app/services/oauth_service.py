"""
OAuth2 Service for handling authentication with Google and Microsoft
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import Session
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.auth.exceptions import RefreshError
# from microsoftgraph.client import Client as MicrosoftGraphClient  # Commented out to avoid import error; install 'microsoftgraph-python' if needed
from app.core.config import settings
from app.models.oauth_models import UserEmailToken, OAuthProvider, TokenStatus
from app.utils.crypto_aes_gcm import encrypt_aes_gcm, decrypt_aes_gcm
from app.utils.encryption import EncryptionKeys
from app.core.database import SessionLocal
from app.utils.crypto_aes_gcm import EncryptionKeysAESGCM
import requests
from app.lib.redact import redact

logger = logging.getLogger(__name__)


class OAuth2Service:
    """OAuth2 service for handling authentication and token management"""

    def __init__(self, db: AsyncSession = None):
        self.db = db
        self.google_scopes = ['openid', 'https://mail.google.com/', 'https://www.googleapis.com/auth/userinfo.email', 'https://www.googleapis.com/auth/userinfo.profile']  # Removed 'offline_access' as it's not a scope; handled via access_type
        self.microsoft_scopes = ['Mail.ReadWrite', 'Mail.Send', 'offline_access']

    async def create_authorization_url(self, provider: OAuthProvider, user_id: int, organization_id: int, redirect_uri: str) -> tuple[str, str]:
        """Create OAuth2 authorization URL for the provider"""
        state = self._generate_state(user_id, organization_id)
        
        if provider == OAuthProvider.GOOGLE or provider == OAuthProvider.GMAIL:
            from google_auth_oauthlib.flow import Flow
            # Check if credentials are configured
            if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
                logger.error("Google OAuth credentials not configured in environment variables.")
                raise ValueError("Google OAuth credentials (GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET) are not set in .env file. Please configure them to use Google authentication.")
            flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": settings.GOOGLE_CLIENT_ID,
                        "client_secret": settings.GOOGLE_CLIENT_SECRET,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token"
                    }
                },
                scopes=self.google_scopes,
                redirect_uri=redirect_uri
            )
            auth_url, _ = flow.authorization_url(prompt='consent', state=state, access_type='offline')
            return auth_url, state
            
        elif provider == OAuthProvider.MICROSOFT or provider == OAuthProvider.OUTLOOK:
            from msal import ConfidentialClientApplication
            # Check if credentials are configured
            if not settings.MICROSOFT_CLIENT_ID or not settings.MICROSOFT_CLIENT_SECRET:
                logger.error("Microsoft OAuth credentials not configured in environment variables.")
                raise ValueError("Microsoft OAuth credentials (MICROSOFT_CLIENT_ID and MICROSOFT_CLIENT_SECRET) are not set in .env file. Please configure them to use Microsoft authentication.")
            app = ConfidentialClientApplication(
                settings.MICROSOFT_CLIENT_ID,
                authority=settings.MICROSOFT_AUTHORITY,
                client_credential=settings.MICROSOFT_CLIENT_SECRET
            )
            auth_url = app.get_authorization_request_url(
                self.microsoft_scopes,
                redirect_uri=redirect_uri,
                state=state
            )
            return auth_url, state
            
        raise ValueError(f"Unsupported provider: {provider}")

    def _generate_state(self, user_id: int, organization_id: int) -> str:
        """Generate secure state parameter with user and org info"""
        from secrets import token_urlsafe
        state_data = f"{user_id}:{organization_id}:{token_urlsafe(16)}"
        return encrypt_aes_gcm(state_data, EncryptionKeysAESGCM.OAUTH)

    def _parse_state(self, state: str) -> tuple[int, int]:
        """Parse state parameter to get user and org ID"""
        try:
            decrypted = decrypt_aes_gcm(state, EncryptionKeysAESGCM.OAUTH)
            user_id, org_id, _ = decrypted.split(':')
            return int(user_id), int(org_id)
        except Exception:
            raise ValueError("Invalid state parameter")

    async def exchange_code_for_tokens(self, provider: OAuthProvider, code: str, state: str, redirect_uri: str) -> tuple[Dict[str, Any], Dict[str, Any], int, int]:
        """Exchange authorization code for tokens"""
        user_id, organization_id = self._parse_state(state)
        
        if provider == OAuthProvider.GOOGLE or provider == OAuthProvider.GMAIL:
            from google_auth_oauthlib.flow import Flow
            # Check if credentials are configured
            if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
                logger.error("Google OAuth credentials not configured in environment variables.")
                raise ValueError("Google OAuth credentials (GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET) are not set in .env file. Please configure them to use Google authentication.")
            flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": settings.GOOGLE_CLIENT_ID,
                        "client_secret": settings.GOOGLE_CLIENT_SECRET,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token"
                    }
                },
                scopes=self.google_scopes,
                redirect_uri=redirect_uri
            )
            flow.fetch_token(code=code)
            credentials = flow.credentials
            token_response = {
                'access_token': credentials.token,
                'refresh_token': credentials.refresh_token,
                'id_token': credentials.id_token,
                'token_type': 'bearer',
                'expires_in': int((credentials.expiry - datetime.utcnow()).total_seconds()),
                'scope': ' '.join(credentials.scopes)
            }
            logger.info(f"Token response for Google: refresh_token present = {bool(credentials.refresh_token)}")
            headers = {"Authorization": f"Bearer {credentials.token}"}
            response = requests.get("https://www.googleapis.com/oauth2/v1/userinfo", headers=headers)
            if response.status_code != 200:
                logger.error(f"Failed to get Google user info: {response.text}")
                raise ValueError(f"Failed to get user info: {response.text}")
            user_info = response.json()
            
            return token_response, user_info, user_id, organization_id
            
        elif provider == OAuthProvider.MICROSOFT or provider == OAuthProvider.OUTLOOK:
            from msal import ConfidentialClientApplication
            # Check if credentials are configured
            if not settings.MICROSOFT_CLIENT_ID or not settings.MICROSOFT_CLIENT_SECRET:
                logger.error("Microsoft OAuth credentials not configured in environment variables.")
                raise ValueError("Microsoft OAuth credentials (MICROSOFT_CLIENT_ID and MICROSOFT_CLIENT_SECRET) are not set in .env file. Please configure them to use Microsoft authentication.")
            app = ConfidentialClientApplication(
                settings.MICROSOFT_CLIENT_ID,
                authority=settings.MICROSOFT_AUTHORITY,
                client_credential=settings.MICROSOFT_CLIENT_SECRET
            )
            token_response = app.acquire_token_by_authorization_code(
                code,
                scopes=self.microsoft_scopes,
                redirect_uri=redirect_uri
            )
            
            if 'error' in token_response:
                logger.error(f"Microsoft OAuth error: {token_response['error_description']}")
                raise ValueError(f"Microsoft OAuth error: {token_response['error_description']}")
            
            logger.info(f"Token response for Microsoft: refresh_token present = {bool(token_response.get('refresh_token'))}")
            # Get user info
            # client = MicrosoftGraphClient(token_response['access_token'])  # Commented out
            # user_info = client.me()  # Commented out
            user_info = {}  # Placeholder; add logic if module is installed
            
            return token_response, user_info, user_id, organization_id
            
        raise ValueError(f"Unsupported provider: {provider}")

    async def store_user_tokens(self, user_id: int, organization_id: int, provider: OAuthProvider, token_response: Dict[str, Any], user_info: Dict[str, Any]) -> UserEmailToken:
        """Store or update OAuth tokens in database"""
        # Check for refresh token
        if not token_response.get('refresh_token'):
            error_msg = "No refresh token received. Please revoke app access in your account settings and re-authorize the application to grant offline access."
            logger.error(
                f"OAuth authorization failed to obtain refresh token for user {user_id}, provider {provider}. "
                f"Error: {error_msg}"
            )
            raise ValueError(error_msg)
        
        # Check for existing token
        stmt = select(UserEmailToken).filter_by(
            user_id=user_id,
            organization_id=organization_id,
            provider=provider.name,
            email_address=user_info['email']
        )
        result = await self.db.execute(stmt)
        existing_token = result.scalar_one_or_none()
        
        # Encrypt tokens
        encrypted_access = encrypt_aes_gcm(token_response['access_token'], EncryptionKeysAESGCM.OAUTH)
        encrypted_refresh = encrypt_aes_gcm(token_response.get('refresh_token', ''), EncryptionKeysAESGCM.OAUTH) if token_response.get('refresh_token') else None
        encrypted_id = encrypt_aes_gcm(token_response.get('id_token', ''), EncryptionKeysAESGCM.OAUTH) if token_response.get('id_token') else None
        
        expires_at = datetime.utcnow() + timedelta(seconds=token_response['expires_in'])
        
        token_data = UserEmailToken(
            user_id=user_id,
            organization_id=organization_id,
            provider=provider.name,
            email_address=user_info['email'],
            display_name=user_info.get('name') or user_info.get('displayName'),
            access_token_encrypted=encrypted_access,
            refresh_token_encrypted=encrypted_refresh,
            id_token_encrypted=encrypted_id,
            scope=' '.join(token_response.get('scope', '').split()),
            token_type=token_response.get('token_type', 'bearer'),
            expires_at=expires_at,
            status=TokenStatus.ACTIVE,
            provider_metadata=user_info,
            last_sync_status='pending',
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        if existing_token:
            # Update existing token
            existing_token.access_token_encrypted = token_data.access_token_encrypted
            existing_token.refresh_token_encrypted = token_data.refresh_token_encrypted
            existing_token.id_token_encrypted = token_data.id_token_encrypted
            existing_token.scope = token_data.scope
            existing_token.token_type = token_data.token_type
            existing_token.expires_at = token_data.expires_at
            existing_token.status = token_data.status
            existing_token.provider_metadata = token_data.provider_metadata
            existing_token.updated_at = token_data.updated_at
            existing_token.refresh_count += 1
            await self.db.commit()
            return existing_token
        else:
            # Create new token
            self.db.add(token_data)
            await self.db.commit()
            return token_data

    async def get_valid_token(self, token_id: int) -> Optional[UserEmailToken]:
        """Get valid token, refresh if expired. Prevents reuse of broken tokens."""
        stmt = select(UserEmailToken).filter_by(id=token_id)
        result = await self.db.execute(stmt)
        token = result.scalar_one_or_none()
        
        if not token:
            logger.error(f"Token lookup failed: No token found for id {token_id}")
            return None
        
        # Prevent reuse of tokens that have failed refresh
        if token.status == TokenStatus.REFRESH_FAILED:
            logger.error(
                f"Token {token_id} has REFRESH_FAILED status and cannot be reused. "
                f"User must re-authorize the account. Email: {token.email_address}, "
                f"Provider: {token.provider}, Last error: {token.last_sync_error}. "
                f"Check if project is in 'Testing' mode."
            )
            return None
        
        # Prevent reuse of revoked tokens
        if token.status == TokenStatus.REVOKED:
            logger.error(
                f"Token {token_id} has been revoked and cannot be reused. "
                f"User must re-authorize the account. Email: {token.email_address}, "
                f"Provider: {token.provider}"
            )
            return None
        
        # Only ACTIVE tokens can be used or refreshed
        if token.status != TokenStatus.ACTIVE:
            logger.error(
                f"Token {token_id} has invalid status {token.status}. "
                f"Email: {token.email_address}, Provider: {token.provider}"
            )
            return None
        
        # Check if token has expired and needs refresh
        if token.is_expired():
            logger.info(
                f"Token {token_id} expired, attempting refresh. "
                f"Email: {token.email_address}, Provider: {token.provider}, "
                f"Expired at: {token.expires_at}"
            )
            success = await self.refresh_token(token_id)
            if not success:
                logger.error(
                    f"Failed to refresh token {token_id}. Token marked as REFRESH_FAILED. "
                    f"Remediation: User must revoke app access in their {token.provider} account "
                    f"settings and re-authorize the application to grant offline access. "
                    f"Email: {token.email_address}. Check if project is in 'Testing' mode."
                )
                return None
            
            # Reload token after refresh
            await self.db.refresh(token)
            logger.info(f"Successfully refreshed token {token_id}. Refresh count: {token.refresh_count}")
        
        return token if token.status == TokenStatus.ACTIVE else None

    async def refresh_token(self, token_id: int) -> bool:
        """Refresh OAuth token with enhanced error handling and logging"""
        stmt = select(UserEmailToken).filter_by(id=token_id)
        result = await self.db.execute(stmt)
        token = result.scalar_one_or_none()
        
        if not token:
            logger.error(f"Token refresh failed: No token found for id {token_id}")
            return False
        
        refresh_token = decrypt_aes_gcm(token.refresh_token_encrypted, EncryptionKeysAESGCM.OAUTH)
        if not refresh_token:
            error_msg = (
                "No refresh token available. User must revoke app access in their account "
                "settings and re-authorize the application with offline access permissions."
            )
            token.status = TokenStatus.REFRESH_FAILED
            token.last_sync_error = error_msg
            await self.db.commit()
            logger.error(
                f"Token refresh failed for token_id {token_id}: {error_msg} "
                f"Email: {token.email_address}, Provider: {token.provider}"
            )
            return False
        
        try:
            new_access_token = None
            new_expiry = None
            
            if token.provider == OAuthProvider.GOOGLE.name or token.provider == OAuthProvider.GMAIL.name:
                # Check if Google credentials are configured
                if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
                    error_msg = "Google OAuth credentials (GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET) are not set in .env file. Please configure them to use Google authentication."
                    logger.error(error_msg)
                    token.status = TokenStatus.REFRESH_FAILED
                    token.last_sync_error = error_msg
                    await self.db.commit()
                    return False
                try:
                    creds = Credentials(
                        token=None,
                        refresh_token=refresh_token,
                        client_id=settings.GOOGLE_CLIENT_ID,
                        client_secret=settings.GOOGLE_CLIENT_SECRET,
                        token_uri='https://oauth2.googleapis.com/token'
                    )
                    logger.info(f"Attempting Google refresh for token {token_id}. Client ID set: {bool(settings.GOOGLE_CLIENT_ID)}, Secret set: {bool(settings.GOOGLE_CLIENT_SECRET)}")
                    creds.refresh(Request())
                    logger.info(
                        f"After creds.refresh() for token {token_id}: "
                        f"token_set={creds.token is not None}, expiry_set={creds.expiry is not None}, "
                        f"id_token_set={creds.id_token is not None}, scopes={creds.scopes}"
                    )
                    if not creds.token:
                        raise ValueError("Refresh completed but access token is None. Check if offline access was granted or revoke and re-authorize.")
                    if not creds.expiry:
                        raise ValueError("Refresh completed but expiry is None. Possible incomplete response from Google; check app configuration.")
                    new_access_token = creds.token
                    new_expiry = creds.expiry.replace(tzinfo=None)  # Make naive to match database
                    logger.info(
                        f"Successfully refreshed Google token {token_id}. "
                        f"Email: {token.email_address}, New expiry: {new_expiry}"
                    )
                except RefreshError as re:
                    error_msg = f"Google OAuth refresh error: {str(re)}. Possible bad token or revoked access. Error details: {re.args}"
                    if 'invalid_grant' in str(re):
                        error_msg += " (invalid_grant: Likely revoked or expired refresh token. Revoke via /api/v1/email/oauth/revoke/{token_id} and re-authorize via /api/v1/oauth/login/google. If recently changed to production, the old refresh token may still expire (7-day limit from testing). Revoke and re-auth to get a permanent one.)"
                    logger.error(f"{error_msg}. Token: {token_id}, Email: {token.email_address}")
                    raise ValueError(error_msg)
                except Exception as e:
                    error_msg = f"Google OAuth refresh failed: {str(e)}. Check client ID/secret or app configuration in Google Console."
                    logger.error(f"{error_msg}. Token: {token_id}, Email: {token.email_address}")
                    raise ValueError(error_msg)
                
            elif token.provider == OAuthProvider.MICROSOFT.name or token.provider == OAuthProvider.OUTLOOK.name:
                # Check if Microsoft credentials are configured
                if not settings.MICROSOFT_CLIENT_ID or not settings.MICROSOFT_CLIENT_SECRET:
                    error_msg = "Microsoft OAuth credentials (MICROSOFT_CLIENT_ID and MICROSOFT_CLIENT_SECRET) are not set in .env file. Please configure them to use Microsoft authentication."
                    logger.error(error_msg)
                    token.status = TokenStatus.REFRESH_FAILED
                    token.last_sync_error = error_msg
                    await self.db.commit()
                    return False
                try:
                    from msal import ConfidentialClientApplication
                    app = ConfidentialClientApplication(
                        settings.MICROSOFT_CLIENT_ID,
                        authority=settings.MICROSOFT_AUTHORITY,
                        client_credential=settings.MICROSOFT_CLIENT_SECRET
                    )
                    result = app.acquire_token_by_refresh_token(
                        refresh_token,
                        scopes=token.scope.split()
                    )
                    logger.info(
                        f"Microsoft refresh result for token {token_id}: "
                        f"has_error={'error' in result}, has_access_token={'access_token' in result}, "
                        f"has_expires_in={'expires_in' in result}, result_keys={list(result.keys())}"
                    )
                    if 'error' in result:
                        error_msg = f"Microsoft OAuth error: {result.get('error_description', result.get('error'))}"
                        if 'invalid_grant' in error_msg:
                            error_msg += " (invalid_grant: Likely revoked or expired refresh token. Revoke via /api/v1/email/oauth/revoke/{token_id} and re-authorize via /api/v1/oauth/login/microsoft. If recently changed to production, the old refresh token may still expire (7-day limit from testing). Revoke and re-auth to get a permanent one.)"
                        logger.error(f"{error_msg}. Token: {token_id}, Email: {token.email_address}")
                        raise ValueError(error_msg)
                    if 'access_token' not in result:
                        raise ValueError("Refresh completed but no access_token in result")
                    if 'expires_in' not in result:
                        raise ValueError("Refresh completed but no expires_in in result")
                    new_access_token = result['access_token']
                    new_expiry = datetime.utcnow() + timedelta(seconds=result['expires_in'])
                    logger.info(
                        f"Successfully refreshed Microsoft token {token_id}. "
                        f"Email: {token.email_address}, New expiry: {new_expiry}"
                    )
                except Exception as e:
                    error_msg = f"Microsoft OAuth refresh failed: {str(e)}"
                    logger.error(f"{error_msg}. Token: {token_id}, Email: {token.email_address}")
                    raise ValueError(error_msg)
            
            # Update token with new credentials
            if new_access_token and new_expiry:
                token.access_token_encrypted = encrypt_aes_gcm(new_access_token, EncryptionKeysAESGCM.OAUTH)
                token.expires_at = new_expiry
                token.updated_at = datetime.utcnow()
                token.refresh_count += 1
                token.last_sync_error = None  # Clear previous errors on success
                token.last_used_at = datetime.utcnow()
                await self.db.commit()
                logger.info(
                    f"Token {token_id} updated successfully. Refresh count: {token.refresh_count}, "
                    f"Email: {token.email_address}"
                )
                return True
            else:
                raise ValueError("No new access token or expiry received from OAuth provider. If recently changed to production, the old refresh token may still expire (7-day limit from testing). Revoke and re-auth to get a permanent one.")
            
        except Exception as e:
            error_msg = str(e)
            token.status = TokenStatus.REFRESH_FAILED
            token.last_sync_error = error_msg
            await self.db.commit()
            logger.error(
                f"Token refresh failed for token_id {token_id}: {error_msg}. "
                f"Token marked as REFRESH_FAILED. Email: {token.email_address}, "
                f"Provider: {token.provider}. "
                f"Remediation: User must revoke app access and re-authorize the application. Check if project is in 'Testing' mode."
            )
            return False

    async def revoke_token(self, token_id: int) -> bool:
        """Revoke OAuth token"""
        stmt = select(UserEmailToken).filter_by(id=token_id)
        result = await self.db.execute(stmt)
        token = result.scalar_one_or_none()
        
        if not token:
            logger.error(f"No token found for revoke: {token_id}")
            return False
        
        try:
            access_token = decrypt_aes_gcm(token.access_token_encrypted, EncryptionKeysAESGCM.OAUTH)
            if access_token:
                if token.provider == OAuthProvider.GOOGLE.name or token.provider == OAuthProvider.GMAIL.name:
                    import requests
                    response = requests.get(f"https://oauth2.googleapis.com/revoke?token={access_token}")
                    if not response.ok:
                        logger.warning(f"Google token revoke failed for {token_id}: {response.text}")
                
                elif token.provider == OAuthProvider.MICROSOFT.name or token.provider == OAuthProvider.OUTLOOK.name:
                    # Microsoft doesn't have a revoke endpoint for tokens
                    pass
            
            token.status = TokenStatus.REVOKED
            token.updated_at = datetime.utcnow()
            await self.db.commit()
            logger.info(f"Token {token_id} revoked successfully")
            return True
            
        except Exception as e:
            logger.error(f"Token revoke failed for {token_id}: {str(e)}")
            return False

    async def get_email_credentials(self, token_id: int) -> Optional[Dict[str, str]]:
        """Get decrypted email credentials"""
        user_token = await self.get_valid_token(token_id)
        if not user_token:
            logger.error(f"Failed to get valid token for {token_id}")
            return None
        
        try:
            access_token = decrypt_aes_gcm(user_token.access_token_encrypted, EncryptionKeysAESGCM.OAUTH)
            refresh_token = decrypt_aes_gcm(user_token.refresh_token_encrypted, EncryptionKeysAESGCM.OAUTH) if user_token.refresh_token_encrypted else None
            id_token = decrypt_aes_gcm(user_token.id_token_encrypted, EncryptionKeysAESGCM.OAUTH) if user_token.id_token_encrypted else None
            
            if not access_token:
                logger.error(f"No access_token after decryption for token_id {token_id}")
                return None
                
            logger.info(f"Successfully decrypted credentials for token {token_id}: access_present={bool(access_token)}, refresh_present={bool(refresh_token)}")
            
            return {
                'email': user_token.email_address,
                'access_token': access_token,
                'refresh_token': refresh_token,
                'id_token': id_token,
            }
        except Exception as e:
            logger.error(f"Failed to decrypt credentials for token {token_id}: {str(e)}")
            return None

    def sync_get_valid_token(self, token_id: int, db: Session) -> Optional[UserEmailToken]:
        """Synchronous version of get_valid_token. Prevents reuse of broken tokens."""
        stmt = select(UserEmailToken).filter_by(id=token_id)
        result = db.execute(stmt)
        token = result.scalar_one_or_none()
        
        if not token:
            logger.error(f"Token lookup failed: No token found for id {token_id}")
            return None
        
        # Prevent reuse of tokens that have failed refresh
        if token.status == TokenStatus.REFRESH_FAILED:
            logger.error(
                f"Token {token_id} has REFRESH_FAILED status and cannot be reused. "
                f"User must re-authorize the account. Email: {token.email_address}, "
                f"Provider: {token.provider}, Last error: {token.last_sync_error}"
            )
            return None
        
        # Prevent reuse of revoked tokens
        if token.status == TokenStatus.REVOKED:
            logger.error(
                f"Token {token_id} has been revoked and cannot be reused. "
                f"User must re-authorize the account. Email: {token.email_address}, "
                f"Provider: {token.provider}"
            )
            return None
        
        # Only ACTIVE tokens can be used or refreshed
        if token.status != TokenStatus.ACTIVE:
            logger.error(
                f"Token {token_id} has invalid status {token.status}. "
                f"Email: {token.email_address}, Provider: {token.provider}"
            )
            return None
        
        # Check if token has expired and needs refresh
        if token.is_expired():
            logger.info(
                f"Token {token_id} expired, attempting refresh. "
                f"Email: {token.email_address}, Provider: {token.provider}, "
                f"Expired at: {token.expires_at}"
            )
            success = self.sync_refresh_token(token_id, db)
            if not success:
                logger.error(
                    f"Failed to refresh token {token_id}. Token marked as REFRESH_FAILED. "
                    f"Remediation: User must revoke app access in their {token.provider} account "
                    f"settings and re-authorize the application to grant offline access. "
                    f"Email: {token.email_address}"
                )
                return None
            
            # Reload token after refresh
            db.refresh(token)
            logger.info(f"Successfully refreshed token {token_id}. Refresh count: {token.refresh_count}")
        
        return token if token.status == TokenStatus.ACTIVE else None

    def sync_get_email_credentials(self, token_id: int, db: Session) -> Optional[Dict[str, str]]:
        """Synchronous version of get_email_credentials"""
        user_token = self.sync_get_valid_token(token_id, db)
        if not user_token:
            logger.error(f"No valid token found for token_id {token_id}")
            return None
        
        try:
            access_token = decrypt_aes_gcm(user_token.access_token_encrypted, EncryptionKeysAESGCM.OAUTH)
            refresh_token = decrypt_aes_gcm(user_token.refresh_token_encrypted, EncryptionKeysAESGCM.OAUTH) if user_token.refresh_token_encrypted else None
            id_token = decrypt_aes_gcm(user_token.id_token_encrypted, EncryptionKeysAESGCM.OAUTH) if user_token.id_token_encrypted else None
            
            if not access_token:
                logger.error(f"No access_token after decryption for token_id {token_id}")
                return None
                
            logger.info(f"Successfully decrypted credentials for token {token_id}: access_present={bool(access_token)}, refresh_present={bool(refresh_token)}")
            
            return {
                'email': user_token.email_address,
                'access_token': access_token,
                'refresh_token': refresh_token,
                'id_token': id_token,
            }
        except Exception as e:
            logger.error(f"Failed to decrypt credentials for token {token_id}: {str(e)}")
            return None

    def sync_refresh_token(self, token_id: int, db: Session) -> bool:
        """Synchronous refresh OAuth token with enhanced error handling and logging"""
        stmt = select(UserEmailToken).filter_by(id=token_id)
        result = db.execute(stmt)
        token = result.scalar_one_or_none()
        
        if not token:
            logger.error(f"Token refresh failed: No token found for id {token_id}")
            return False
        
        refresh_token = decrypt_aes_gcm(token.refresh_token_encrypted, EncryptionKeysAESGCM.OAUTH)
        if not refresh_token:
            error_msg = (
                "No refresh token available. User must revoke app access in their account "
                "settings and re-authorize the application with offline access permissions."
            )
            token.status = TokenStatus.REFRESH_FAILED
            token.last_sync_error = error_msg
            db.commit()
            logger.error(
                f"Token refresh failed for token_id {token_id}: {error_msg} "
                f"Email: {token.email_address}, Provider: {token.provider}"
            )
            return False
        
        try:
            new_access_token = None
            new_expiry = None
            
            if token.provider == OAuthProvider.GOOGLE.name or token.provider == OAuthProvider.GMAIL.name:
                # Check if Google credentials are configured
                if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
                    error_msg = "Google OAuth credentials (GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET) are not set in .env file. Please configure them to use Google authentication."
                    logger.error(error_msg)
                    token.status = TokenStatus.REFRESH_FAILED
                    token.last_sync_error = error_msg
                    db.commit()
                    return False
                try:
                    creds = Credentials(
                        token=None,
                        refresh_token=refresh_token,
                        client_id=settings.GOOGLE_CLIENT_ID,
                        client_secret=settings.GOOGLE_CLIENT_SECRET,
                        token_uri='https://oauth2.googleapis.com/token'
                    )
                    logger.info(f"Attempting Google refresh for token {token_id}. Client ID set: {bool(settings.GOOGLE_CLIENT_ID)}, Secret set: {bool(settings.GOOGLE_CLIENT_SECRET)}")
                    creds.refresh(Request())
                    logger.info(
                        f"After creds.refresh() for token {token_id}: "
                        f"token_set={creds.token is not None}, expiry_set={creds.expiry is not None}, "
                        f"id_token_set={creds.id_token is not None}, scopes={creds.scopes}"
                    )
                    if not creds.token:
                        raise ValueError("Refresh completed but access token is None. Check if offline access was granted or revoke and re-authorize.")
                    if not creds.expiry:
                        raise ValueError("Refresh completed but expiry is None. Possible incomplete response from Google; check app configuration.")
                    new_access_token = creds.token
                    new_expiry = creds.expiry.replace(tzinfo=None)  # Make naive to match database
                    logger.info(
                        f"Successfully refreshed Google token {token_id}. "
                        f"Email: {token.email_address}, New expiry: {new_expiry}"
                    )
                except RefreshError as re:
                    error_msg = f"Google OAuth refresh error: {str(re)}. Possible bad token or revoked access. Error details: {re.args}"
                    if 'invalid_grant' in str(re):
                        error_msg += " (invalid_grant: Likely revoked or expired refresh token. Revoke via /api/v1/email/oauth/revoke/{token_id} and re-authorize via /api/v1/oauth/login/google. If recently changed to production, the old refresh token may still expire (7-day limit from testing). Revoke and re-auth to get a permanent one.)"
                    logger.error(f"{error_msg}. Token: {token_id}, Email: {token.email_address}")
                    raise ValueError(error_msg)
                except Exception as e:
                    error_msg = f"Google OAuth refresh failed: {str(e)}. Check client ID/secret or app configuration in Google Console."
                    logger.error(f"{error_msg}. Token: {token_id}, Email: {token.email_address}")
                    raise ValueError(error_msg)
                
            elif token.provider == OAuthProvider.MICROSOFT.name or token.provider == OAuthProvider.OUTLOOK.name:
                # Check if Microsoft credentials are configured
                if not settings.MICROSOFT_CLIENT_ID or not settings.MICROSOFT_CLIENT_SECRET:
                    error_msg = "Microsoft OAuth credentials (MICROSOFT_CLIENT_ID and MICROSOFT_CLIENT_SECRET) are not set in .env file. Please configure them to use Microsoft authentication."
                    logger.error(error_msg)
                    token.status = TokenStatus.REFRESH_FAILED
                    token.last_sync_error = error_msg
                    db.commit()
                    return False
                try:
                    from msal import ConfidentialClientApplication
                    app = ConfidentialClientApplication(
                        settings.MICROSOFT_CLIENT_ID,
                        authority=settings.MICROSOFT_AUTHORITY,
                        client_credential=settings.MICROSOFT_CLIENT_SECRET
                    )
                    result = app.acquire_token_by_refresh_token(
                        refresh_token,
                        scopes=token.scope.split()
                    )
                    logger.info(
                        f"Microsoft refresh result for token {token_id}: "
                        f"has_error={'error' in result}, has_access_token={'access_token' in result}, "
                        f"has_expires_in={'expires_in' in result}, result_keys={list(result.keys())}"
                    )
                    if 'error' in result:
                        error_msg = f"Microsoft OAuth error: {result.get('error_description', result.get('error'))}"
                        if 'invalid_grant' in error_msg:
                            error_msg += " (invalid_grant: Likely revoked or expired refresh token. Revoke via /api/v1/email/oauth/revoke/{token_id} and re-authorize via /api/v1/oauth/login/microsoft. If recently changed to production, the old refresh token may still expire (7-day limit from testing). Revoke and re-auth to get a permanent one.)"
                        logger.error(f"{error_msg}. Token: {token_id}, Email: {token.email_address}")
                        raise ValueError(error_msg)
                    if 'access_token' not in result:
                        raise ValueError("Refresh completed but no access_token in result")
                    if 'expires_in' not in result:
                        raise ValueError("Refresh completed but no expires_in in result")
                    new_access_token = result['access_token']
                    new_expiry = datetime.utcnow() + timedelta(seconds=result['expires_in'])
                    logger.info(
                        f"Successfully refreshed Microsoft token {token_id}. "
                        f"Email: {token.email_address}, New expiry: {new_expiry}"
                    )
                except Exception as e:
                    error_msg = f"Microsoft OAuth refresh failed: {str(e)}"
                    logger.error(f"{error_msg}. Token: {token_id}, Email: {token.email_address}")
                    raise ValueError(error_msg)
            
            # Update token with new credentials
            if new_access_token and new_expiry:
                token.access_token_encrypted = encrypt_aes_gcm(new_access_token, EncryptionKeysAESGCM.OAUTH)
                token.expires_at = new_expiry
                token.updated_at = datetime.utcnow()
                token.refresh_count += 1
                token.last_sync_error = None  # Clear previous errors on success
                token.last_used_at = datetime.utcnow()
                db.commit()
                logger.info(
                    f"Token {token_id} updated successfully. Refresh count: {token.refresh_count}, "
                    f"Email: {token.email_address}"
                )
                return True
            else:
                raise ValueError("No new access token or expiry received from OAuth provider. If recently changed to production, the old refresh token may still expire (7-day limit from testing). Revoke and re-auth to get a permanent one.")
            
        except Exception as e:
            error_msg = str(e)
            token.status = TokenStatus.REFRESH_FAILED
            token.last_sync_error = error_msg
            db.commit()
            logger.error(
                f"Token refresh failed for token_id {token_id}: {error_msg}. "
                f"Token marked as REFRESH_FAILED. Email: {token.email_address}, "
                f"Provider: {token.provider}. "
                f"Remediation: User must revoke app access and re-authorize the application. Check if project is in 'Testing' mode."
            )
            return False