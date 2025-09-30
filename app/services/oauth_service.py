"""
OAuth2 Service for handling Google and Microsoft OAuth flows
"""

import secrets
import hashlib
import base64
import logging
import traceback
from typing import Optional, Dict, Any, Tuple, List
from urllib.parse import urlencode, parse_qs, urlparse
from datetime import datetime, timedelta

import requests
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from msal import ConfidentialClientApplication
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.core.config import settings
from app.models.oauth_models import UserEmailToken, OAuthState, OAuthProvider, TokenStatus
from app.schemas.oauth_schemas import (
    OAuthLoginRequest, OAuthLoginResponse, OAuthCallbackRequest, 
    OAuthTokenResponse, UserEmailTokenCreate
)
from app.utils.encryption import encrypt_field, decrypt_field, EncryptionKeys

logger = logging.getLogger(__name__)


class OAuthConfig:
    """OAuth2 configuration for different providers"""
    
    GOOGLE = {
        "client_id": getattr(settings, "GOOGLE_CLIENT_ID", ""),
        "client_secret": getattr(settings, "GOOGLE_CLIENT_SECRET", ""),
        "authorization_endpoint": "https://accounts.google.com/o/oauth2/auth",
        "token_endpoint": "https://oauth2.googleapis.com/token",
        "userinfo_endpoint": "https://www.googleapis.com/oauth2/v3/userinfo",
        "scopes": [
            "https://mail.google.com/",
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/userinfo.profile"
        ]
    }
    
    MICROSOFT = {
        "client_id": getattr(settings, "MICROSOFT_CLIENT_ID", ""),
        "client_secret": getattr(settings, "MICROSOFT_CLIENT_SECRET", ""),
        "authorization_endpoint": "https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
        "token_endpoint": "https://login.microsoftonline.com/common/oauth2/v2.0/token",
        "userinfo_endpoint": "https://graph.microsoft.com/v1.0/me",
        "scopes": [
            "https://graph.microsoft.com/Mail.ReadWrite",
            "https://graph.microsoft.com/Mail.Send",
            "https://graph.microsoft.com/User.Read"
        ]
    }


class OAuth2Service:
    """Service for handling OAuth2 flows with Google and Microsoft"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        
    def generate_state(self) -> str:
        """Generate a cryptographically secure state parameter"""
        return secrets.token_urlsafe(32)
    
    def generate_code_verifier(self) -> str:
        """Generate PKCE code verifier"""
        return base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
    
    def generate_code_challenge(self, verifier: str) -> str:
        """Generate PKCE code challenge from verifier"""
        digest = hashlib.sha256(verifier.encode('utf-8')).digest()
        return base64.urlsafe_b64encode(digest).decode('utf-8').rstrip('=')
    
    async def create_authorization_url(
        self, 
        provider: OAuthProvider, 
        user_id: int, 
        organization_id: Optional[int],
        redirect_uri: str,
        scope: Optional[str] = None
    ) -> Tuple[str, str]:
        """
        Create OAuth2 authorization URL and store state
        """
        config = getattr(OAuthConfig, provider.value.upper())
        if not config["client_id"]:
            raise ValueError(f"OAuth2 not configured for {provider.value}")
        
        state = self.generate_state()
        code_verifier = self.generate_code_verifier()
        code_challenge = self.generate_code_challenge(code_verifier)
        
        # Store state in database
        oauth_state = OAuthState(
            state=state,
            provider=provider,
            user_id=user_id,
            organization_id=organization_id,
            redirect_uri=redirect_uri,
            scope=scope or " ".join(config["scopes"]),
            code_verifier=code_verifier,
            expires_at=datetime.utcnow() + timedelta(minutes=10)
        )
        self.db.add(oauth_state)
        try:
            await self.db.commit()
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to commit OAuthState: {str(e)}\n{traceback.format_exc()}")
            raise
        
        # Build authorization URL
        params = {
            "client_id": config["client_id"],
            "response_type": "code",
            "redirect_uri": redirect_uri,
            "scope": scope or " ".join(config["scopes"]),
            "state": state,
            "access_type": "offline",  # For refresh tokens
            "prompt": "consent"
        }
        
        if provider == OAuthProvider.GOOGLE:
            params.update({
                "code_challenge": code_challenge,
                "code_challenge_method": "S256"
            })
        elif provider == OAuthProvider.MICROSOFT:
            params["response_mode"] = "query"
        
        auth_url = f"{config['authorization_endpoint']}?{urlencode(params)}"
        return auth_url, state
    
    async def exchange_code_for_tokens(
        self, 
        provider: OAuthProvider, 
        code: str, 
        state: str, 
        redirect_uri: str
    ) -> Tuple[Dict[str, Any], Dict[str, Any], int, Optional[int]]:
        """
        Exchange authorization code for access tokens
        """
        # Verify state
        stmt = select(OAuthState).where(
            OAuthState.state == state,
            OAuthState.provider == provider,
            OAuthState.expires_at > datetime.utcnow()
        )
        result = await self.db.execute(stmt)
        oauth_state = result.scalars().first()
        
        if not oauth_state:
            raise ValueError("Invalid or expired state parameter")
        
        config = getattr(OAuthConfig, provider.value.upper())
        
        # Prepare token request
        token_data = {
            "client_id": config["client_id"],
            "client_secret": config["client_secret"],
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri
        }
        
        if provider == OAuthProvider.GOOGLE:
            token_data["code_verifier"] = oauth_state.code_verifier
        
        # Exchange code for tokens
        try:
            response = requests.post(
                config["token_endpoint"],
                data=token_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error in token exchange: {str(e)}")
            raise ValueError("Network error during token exchange")
        
        if not response.ok:
            logger.error(f"Token exchange failed: {response.status_code} - {response.text}")
            raise ValueError(f"Token exchange failed: {response.status_code}")

        try:
            token_response = response.json()
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in token response: {response.text}")
            raise ValueError("Invalid response format from token endpoint")
        
        # Get user info
        user_info = self._get_user_info(provider, token_response["access_token"])
        
        user_id = oauth_state.user_id
        organization_id = oauth_state.organization_id
        
        # Clean up state
        await self.db.delete(oauth_state)
        await self.db.commit()
        
        return token_response, user_info, user_id, organization_id
    
    def _get_user_info(self, provider: OAuthProvider, access_token: str) -> Dict[str, Any]:
        """Get user information from provider"""
        config = getattr(OAuthConfig, provider.value.upper())
        
        headers = {"Authorization": f"Bearer {access_token}"}
        try:
            response = requests.get(config["userinfo_endpoint"], headers=headers)
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error in user info request: {str(e)}")
            raise ValueError("Network error during user info request")
        
        if not response.ok:
            logger.error(f"User info request failed: {response.status_code} - {response.text}")
            raise ValueError("Failed to get user information")
        
        try:
            return response.json()
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in user info response: {response.text}")
            raise ValueError("Invalid response format from user info endpoint")
    
    async def store_user_tokens(
        self,
        user_id: int,
        organization_id: Optional[int],
        provider: OAuthProvider,
        token_response: Dict[str, Any],
        user_info: Dict[str, Any]
    ) -> UserEmailToken:
        """
        Store encrypted OAuth tokens for user
        """
        # Calculate token expiry
        expires_at = None
        if "expires_in" in token_response:
            expires_at = datetime.utcnow() + timedelta(seconds=token_response["expires_in"])
        
        # Extract email and name from user_info
        email = user_info.get("email")
        if not email:
            raise ValueError("No email found in user profile")
        
        display_name = (
            user_info.get("name") or 
            user_info.get("displayName") or 
            user_info.get("given_name", "") + " " + user_info.get("family_name", "")
        ).strip()
        
        # Check if token already exists for this user/provider/email
        stmt = select(UserEmailToken).where(
            UserEmailToken.user_id == user_id,
            UserEmailToken.organization_id == organization_id,
            UserEmailToken.provider == provider,
            UserEmailToken.email_address == email
        )
        result = await self.db.execute(stmt)
        existing_token = result.scalars().first()
        
        if existing_token:
            # Update existing token
            existing_token.access_token = token_response["access_token"]
            existing_token.refresh_token = token_response.get("refresh_token")
            existing_token.id_token = token_response.get("id_token")
            existing_token.expires_at = expires_at
            existing_token.status = TokenStatus.ACTIVE
            existing_token.scope = token_response.get("scope")
            existing_token.updated_at = datetime.utcnow()
            existing_token.provider_metadata = user_info
            
            await self.db.commit()
            return existing_token
        else:
            # Create new token record
            user_token = UserEmailToken(
                user_id=user_id,
                organization_id=organization_id,
                provider=provider,
                email_address=email,
                display_name=display_name,
                access_token=token_response["access_token"],
                refresh_token=token_response.get("refresh_token"),
                id_token=token_response.get("id_token"),
                scope=token_response.get("scope"),
                expires_at=expires_at,
                status=TokenStatus.ACTIVE,
                provider_metadata=user_info
            )
            
            self.db.add(user_token)
            await self.db.commit()
            return user_token
    
    async def refresh_token(self, token_id: int) -> bool:
        """
        Refresh an expired access token
        """
        stmt = select(UserEmailToken).where(UserEmailToken.id == token_id)
        result = await self.db.execute(stmt)
        user_token = result.scalars().first()
        
        if not user_token or not user_token.refresh_token:
            return False
        
        config = getattr(OAuthConfig, user_token.provider.value.upper())
        
        # Prepare refresh request
        refresh_data = {
            "client_id": config["client_id"],
            "client_secret": config["client_secret"],
            "refresh_token": user_token.refresh_token,
            "grant_type": "refresh_token"
        }
        
        try:
            response = requests.post(
                config["token_endpoint"],
                data=refresh_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if not response.ok:
                logger.error("Token refresh failed: %s - %s", response.status_code, response.text)
                user_token.status = TokenStatus.REFRESH_FAILED
                await self.db.commit()
                return False
            
            try:
                token_response = response.json()
            except json.JSONDecodeError:
                logger.error("Invalid JSON in refresh token response: %s", response.text)
                user_token.status = TokenStatus.REFRESH_FAILED
                await self.db.commit()
                return False
            
            # Update token
            user_token.access_token = token_response["access_token"]
            if "refresh_token" in token_response:
                user_token.refresh_token = token_response["refresh_token"]
            
            if "expires_in" in token_response:
                user_token.expires_at = datetime.utcnow() + timedelta(
                    seconds=token_response["expires_in"]
                )
            
            user_token.status = TokenStatus.ACTIVE
            user_token.refresh_count += 1
            user_token.updated_at = datetime.utcnow()
            
            await self.db.commit()
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error in token refresh: {str(e)}")
            user_token.status = TokenStatus.REFRESH_FAILED
            await self.db.commit()
            return False
        except Exception as e:
            logger.error(f"Token refresh error: {str(e)}")
            user_token.status = TokenStatus.REFRESH_FAILED
            await self.db.commit()
            return False
    
    async def revoke_token(self, token_id: int) -> bool:
        """
        Revoke an OAuth token
        """
        stmt = select(UserEmailToken).where(UserEmailToken.id == token_id)
        result = await self.db.execute(stmt)
        user_token = result.scalars().first()
        
        if not user_token:
            return False
        
        # Mark as revoked in database
        user_token.status = TokenStatus.REVOKED
        user_token.updated_at = datetime.utcnow()
        await self.db.commit()
        
        # TODO: Also revoke with provider if they support it
        return True
    
    async def get_valid_token(self, token_id: int) -> Optional[UserEmailToken]:
        """
        Get a valid token, refreshing if necessary
        """
        stmt = select(UserEmailToken).where(
            UserEmailToken.id == token_id,
            UserEmailToken.status == TokenStatus.ACTIVE
        )
        result = await self.db.execute(stmt)
        user_token = result.scalars().first()
        
        if not user_token:
            return None
        
        # Check if token is expired and refresh if possible
        if user_token.is_expired() and user_token.refresh_token:
            if await self.refresh_token(token_id):
                # Refresh the object from database
                await self.db.refresh(user_token)
            else:
                return None
        
        # Update last used timestamp
        user_token.last_used_at = datetime.utcnow()
        await self.db.commit()
        
        return user_token if user_token.is_active() else None
    
    async def get_email_credentials(self, token_id: int) -> Optional[Dict[str, Any]]:
        """
        Get email credentials for IMAP/SMTP access
        Returns credentials dict with access_token for OAuth2 XOAUTH2 authentication
        """
        user_token = await self.get_valid_token(token_id)
        if not user_token:
            return None
        
        try:
            # Decrypt access token
            access_token = decrypt_field(
                user_token.access_token_encrypted,
                EncryptionKeys.PII_KEY
            )
            
            credentials = {
                "provider": user_token.provider.value,
                "email": user_token.email_address,
                "access_token": access_token,
                "auth_method": "oauth2",
                "token_type": "Bearer"
            }
            
            # Add provider-specific settings
            if user_token.provider == OAuthProvider.GOOGLE:
                credentials.update({
                    "imap_host": "imap.gmail.com",
                    "imap_port": 993,
                    "smtp_host": "smtp.gmail.com",
                    "smtp_port": 587,
                    "use_ssl": True
                })
            elif user_token.provider == OAuthProvider.MICROSOFT:
                credentials.update({
                    "imap_host": "outlook.office365.com",
                    "imap_port": 993,
                    "smtp_host": "smtp-mail.outlook.com",
                    "smtp_port": 587,
                    "use_ssl": True
                })
            
            return credentials
            
        except Exception as e:
            logger.error(f"Error getting email credentials: {str(e)}")
            return None
    
    async def list_user_tokens(self, user_id: int, organization_id: Optional[int] = None) -> List[UserEmailToken]:
        """
        List all active OAuth tokens for a user
        """
        stmt = select(UserEmailToken).where(
            UserEmailToken.user_id == user_id,
            UserEmailToken.status == TokenStatus.ACTIVE
        )
        
        if organization_id:
            stmt = stmt.where(UserEmailToken.organization_id == organization_id)
        
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def get_token_info(self, token_id: int) -> Optional[Dict[str, Any]]:
        """
        Get token information (without sensitive data)
        """
        stmt = select(UserEmailToken).where(UserEmailToken.id == token_id)
        result = await self.db.execute(stmt)
        user_token = result.scalars().first()
        
        if not user_token:
            return None
        
        return {
            "id": user_token.id,
            "provider": user_token.provider.value,
            "email_address": user_token.email_address,
            "display_name": user_token.display_name,
            "status": user_token.status.value,
            "scopes": user_token.scopes,
            "is_expired": user_token.is_expired(),
            "is_active": user_token.is_active(),
            "created_at": user_token.created_at,
            "expires_at": user_token.expires_at,
            "last_used_at": user_token.last_used_at,
            "refresh_count": user_token.refresh_count
        }