# app/services/oauth_service.py

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
# from microsoftgraph.client import Client as MicrosoftGraphClient  # Commented out to avoid import error; install 'microsoftgraph-python' if needed
from app.core.config import settings
from app.models.oauth_models import UserEmailToken, OAuthProvider, TokenStatus
from app.utils.crypto_aes_gcm import encrypt_aes_gcm, decrypt_aes_gcm
from app.utils.encryption import EncryptionKeys
from app.core.database import SessionLocal
from app.utils.crypto_aes_gcm import EncryptionKeysAESGCM

logger = logging.getLogger(__name__)


class OAuth2Service:
    """OAuth2 service for handling authentication and token management"""

    def __init__(self, db: AsyncSession = None):
        self.db = db
        self.google_scopes = ['https://mail.google.com/']
        self.microsoft_scopes = ['Mail.ReadWrite', 'Mail.Send', 'offline_access']

    async def create_authorization_url(self, provider: OAuthProvider, user_id: int, organization_id: int, redirect_uri: str) -> tuple[str, str]:
        """Create OAuth2 authorization URL for the provider"""
        state = self._generate_state(user_id, organization_id)
        
        if provider == OAuthProvider.GOOGLE:
            from google_auth_oauthlib.flow import Flow
            flow = Flow.from_client_secrets_file(
                settings.GOOGLE_CLIENT_SECRETS_FILE,
                scopes=self.google_scopes,
                redirect_uri=redirect_uri
            )
            auth_url, _ = flow.authorization_url(prompt='consent', state=state)
            return auth_url, state
            
        elif provider == OAuthProvider.MICROSOFT:
            from msal import ConfidentialClientApplication
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
        
        if provider == OAuthProvider.GOOGLE:
            from google_auth_oauthlib.flow import Flow
            flow = Flow.from_client_secrets_file(
                settings.GOOGLE_CLIENT_SECRETS_FILE,
                scopes=self.google_scopes,
                redirect_uri=redirect_uri
            )
            flow.fetch_token(code=code)
            credentials = flow.credentials
            token_response = {
                'access_token': credentials.token,
                'refresh_token': credentials.refresh_token,
                'id_token': credentials.id_token,
                'token_type': credentials.token_type,
                'expires_in': credentials.expiry.timestamp() - datetime.now().timestamp(),
                'scope': ' '.join(credentials.scopes)
            }
            from google.oauth2.credentials import Credentials
            creds = Credentials(token=credentials.token)
            user_info = creds._request('https://www.googleapis.com/userinfo/v2/me')
            
            return token_response, user_info, user_id, organization_id
            
        elif provider == OAuthProvider.MICROSOFT:
            from msal import ConfidentialClientApplication
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
                raise ValueError(f"Microsoft OAuth error: {token_response['error_description']}")
            
            # Get user info
            # client = MicrosoftGraphClient(token_response['access_token'])  # Commented out
            # user_info = client.me()  # Commented out
            user_info = {}  # Placeholder; add logic if module is installed
            
            return token_response, user_info, user_id, organization_id
            
        raise ValueError(f"Unsupported provider: {provider}")

    async def store_user_tokens(self, user_id: int, organization_id: int, provider: OAuthProvider, token_response: Dict[str, Any], user_info: Dict[str, Any]) -> UserEmailToken:
        """Store or update OAuth tokens in database"""
        # Check for existing token
        stmt = select(UserEmailToken).filter_by(
            user_id=user_id,
            organization_id=organization_id,
            provider=provider.value,
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
            provider=provider.value,
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
        """Get valid token, refresh if expired"""
        stmt = select(UserEmailToken).filter_by(id=token_id)
        result = await self.db.execute(stmt)
        token = result.scalar_one_or_none()
        
        if not token:
            return None
        
        if token.is_expired():
            success = await self.refresh_token(token_id)
            if not success:
                return None
            
            await self.db.refresh(token)
        
        return token if token.status == TokenStatus.ACTIVE else None

    async def refresh_token(self, token_id: int) -> bool:
        """Refresh OAuth token"""
        stmt = select(UserEmailToken).filter_by(id=token_id)
        result = await self.db.execute(stmt)
        token = result.scalar_one_or_none()
        
        if not token or token.status != TokenStatus.ACTIVE:
            return False
        
        refresh_token = decrypt_aes_gcm(token.refresh_token_encrypted, EncryptionKeysAESGCM.OAUTH)
        if not refresh_token:
            token.status = TokenStatus.REFRESH_FAILED
            token.last_sync_error = "No refresh token available"
            await self.db.commit()
            return False
        
        try:
            if token.provider == OAuthProvider.GOOGLE.value:
                creds = Credentials(
                    token=None,
                    refresh_token=refresh_token,
                    client_id=settings.GOOGLE_CLIENT_ID,
                    client_secret=settings.GOOGLE_CLIENT_SECRET,
                    token_uri='https://oauth2.googleapis.com/token'
                )
                creds.refresh(Request())
                new_access_token = creds.token
                new_expiry = creds.expiry
                
            elif token.provider == OAuthProvider.MICROSOFT.value:
                from msal import ConfidentialClientApplication
                app = ConfidentialClientApplication(
                    settings.MICROSOFT_CLIENT_ID,
                    authority=settings.MICROSOFT_AUTHORITY,
                    client_credential=settings.MICROSOFT_CLIENT_SECRET
                )
                result = app.acquire_token_silent_with_error(
                    scopes=token.scope.split(),
                    account=None,
                    refresh_token=refresh_token
                )
                if 'error' in result:
                    raise ValueError(result['error_description'])
                new_access_token = result['access_token']
                new_expiry = datetime.utcnow() + timedelta(seconds=result['expires_in'])
            
            # Update token
            token.access_token_encrypted = encrypt_aes_gcm(new_access_token, EncryptionKeysAESGCM.OAUTH)
            token.expires_at = new_expiry
            token.updated_at = datetime.utcnow()
            token.refresh_count += 1
            token.last_sync_error = None
            await self.db.commit()
            return True
            
        except Exception as e:
            token.status = TokenStatus.REFRESH_FAILED
            token.last_sync_error = str(e)
            await self.db.commit()
            logger.error(f"Token refresh failed for {token_id}: {str(e)}")
            return False

    async def revoke_token(self, token_id: int) -> bool:
        """Revoke OAuth token"""
        stmt = select(UserEmailToken).filter_by(id=token_id)
        result = await self.db.execute(stmt)
        token = result.scalar_one_or_none()
        
        if not token:
            return False
        
        try:
            if token.provider == OAuthProvider.GOOGLE.value:
                access_token = decrypt_aes_gcm(token.access_token_encrypted, EncryptionKeysAESGCM.OAUTH)
                if access_token:
                    import requests
                    response = requests.get(f"https://oauth2.googleapis.com/revoke?token={access_token}")
                    if not response.ok:
                        logger.warning(f"Google token revoke failed: {response.text}")
            
            elif token.provider == OAuthProvider.MICROSOFT.value:
                # Microsoft doesn't have a revoke endpoint for tokens
                pass
            
            token.status = TokenStatus.REVOKED
            token.updated_at = datetime.utcnow()
            await self.db.commit()
            return True
            
        except Exception as e:
            logger.error(f"Token revoke failed for {token_id}: {str(e)}")
            return False

    async def get_email_credentials(self, token_id: int) -> Optional[Dict[str, str]]:
        """Get decrypted email credentials"""
        user_token = await self.get_valid_token(token_id)
        if not user_token:
            return None
        
        return {
            'email': user_token.email_address,
            'access_token': decrypt_aes_gcm(user_token.access_token_encrypted, EncryptionKeysAESGCM.OAUTH),
            'refresh_token': decrypt_aes_gcm(user_token.refresh_token_encrypted, EncryptionKeysAESGCM.OAUTH) if user_token.refresh_token_encrypted else None,
            'id_token': decrypt_aes_gcm(user_token.id_token_encrypted, EncryptionKeysAESGCM.OAUTH) if user_token.id_token_encrypted else None,
        }

    def sync_get_valid_token(self, token_id: int, db: Session) -> Optional[UserEmailToken]:
        """Synchronous version of get_valid_token"""
        stmt = select(UserEmailToken).filter_by(id=token_id)
        result = db.execute(stmt)
        token = result.scalar_one_or_none()
        
        if not token:
            return None
        
        if token.is_expired():
            success = self.sync_refresh_token(token_id, db)
            if not success:
                return None
            
            db.refresh(token)
        
        return token if token.status == TokenStatus.ACTIVE else None

    def sync_refresh_token(self, token_id: int, db: Session) -> bool:
        """Synchronous version of refresh_token"""
        stmt = select(UserEmailToken).filter_by(id=token_id)
        result = db.execute(stmt)
        token = result.scalar_one_or_none()
        
        if not token or token.status != TokenStatus.ACTIVE:
            return False
        
        refresh_token = decrypt_aes_gcm(token.refresh_token_encrypted, EncryptionKeysAESGCM.OAUTH)
        if not refresh_token:
            token.status = TokenStatus.REFRESH_FAILED
            token.last_sync_error = "No refresh token available"
            db.commit()
            return False
        
        try:
            if token.provider == OAuthProvider.GOOGLE.value:
                creds = Credentials(
                    token=None,
                    refresh_token=refresh_token,
                    client_id=settings.GOOGLE_CLIENT_ID,
                    client_secret=settings.GOOGLE_CLIENT_SECRET,
                    token_uri='https://oauth2.googleapis.com/token'
                )
                creds.refresh(Request())
                new_access_token = creds.token
                new_expiry = creds.expiry
                
            elif token.provider == OAuthProvider.MICROSOFT.value:
                from msal import ConfidentialClientApplication
                app = ConfidentialClientApplication(
                    settings.MICROSOFT_CLIENT_ID,
                    authority=settings.MICROSOFT_AUTHORITY,
                    client_credential=settings.MICROSOFT_CLIENT_SECRET
                )
                result = app.acquire_token_silent_with_error(
                    scopes=token.scope.split(),
                    account=None,
                    refresh_token=refresh_token
                )
                if 'error' in result:
                    raise ValueError(result['error_description'])
                new_access_token = result['access_token']
                new_expiry = datetime.utcnow() + timedelta(seconds=result['expires_in'])
            
            # Update token
            token.access_token_encrypted = encrypt_aes_gcm(new_access_token, EncryptionKeysAESGCM.OAUTH)
            token.expires_at = new_expiry
            token.updated_at = datetime.utcnow()
            token.refresh_count += 1
            token.last_sync_error = None
            db.commit()
            return True
            
        except Exception as e:
            token.status = TokenStatus.REFRESH_FAILED
            token.last_sync_error = str(e)
            db.commit()
            logger.error(f"Token refresh failed for {token_id}: {str(e)}")
            return False

    def sync_get_email_credentials(self, token_id: int, db: Session) -> Optional[Dict[str, str]]:
        """Synchronous version of get_email_credentials"""
        user_token = self.sync_get_valid_token(token_id, db)
        if not user_token:
            return None
        
        return {
            'email': user_token.email_address,
            'access_token': decrypt_aes_gcm(user_token.access_token_encrypted, EncryptionKeysAESGCM.OAUTH),
            'refresh_token': decrypt_aes_gcm(user_token.refresh_token_encrypted, EncryptionKeysAESGCM.OAUTH) if user_token.refresh_token_encrypted else None,
            'id_token': decrypt_aes_gcm(user_token.id_token_encrypted, EncryptionKeysAESGCM.OAUTH) if user_token.id_token_encrypted else None,
        }