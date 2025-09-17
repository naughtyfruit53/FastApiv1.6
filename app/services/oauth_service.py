"""
OAuth2 Service for handling Google and Microsoft OAuth flows
"""

import secrets
import hashlib
import base64
import logging
from typing import Optional, Dict, Any, Tuple
from urllib.parse import urlencode, parse_qs, urlparse

import requests
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from msal import ConfidentialClientApplication
from sqlalchemy.orm import Session

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
            "https://www.googleapis.com/auth/gmail.readonly",
            "https://www.googleapis.com/auth/gmail.send",
            "https://www.googleapis.com/auth/gmail.modify",
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
            "https://graph.microsoft.com/Mail.Read",
            "https://graph.microsoft.com/Mail.Send",
            "https://graph.microsoft.com/Mail.ReadWrite",
            "https://graph.microsoft.com/User.Read"
        ]
    }


class OAuth2Service:
    """Service for handling OAuth2 flows with Google and Microsoft"""
    
    def __init__(self, db: Session):
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
    
    def create_authorization_url(
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
            self.db.commit()
        except Exception as e:
            self.db.rollback()
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
    
    def exchange_code_for_tokens(
        self, 
        provider: OAuthProvider, 
        code: str, 
        state: str, 
        redirect_uri: str
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Exchange authorization code for access tokens
        """
        # Verify state
        oauth_state = self.db.query(OAuthState).filter(
            OAuthState.state == state,
            OAuthState.provider == provider,
            OAuthState.expires_at > datetime.utcnow()
        ).first()
        
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
        
        # Clean up state
        self.db.delete(oauth_state)
        self.db.commit()
        
        return token_response, user_info
    
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
    
    def store_user_tokens(
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
        existing_token = self.db.query(UserEmailToken).filter(
            UserEmailToken.user_id == user_id,
            UserEmailToken.organization_id == organization_id,
            UserEmailToken.provider == provider,
            UserEmailToken.email_address == email
        ).first()
        
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
            
            self.db.commit()
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
            self.db.commit()
            return user_token
    
    def refresh_token(self, token_id: int) -> bool:
        """
        Refresh an expired access token
        """
        user_token = self.db.query(UserEmailToken).filter(
            UserEmailToken.id == token_id
        ).first()
        
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
                logger.error(f"Token refresh failed: {response.text}")
                user_token.status = TokenStatus.REFRESH_FAILED
                self.db.commit()
                return False
            
            try:
                token_response = response.json()
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON in refresh token response: {response.text}")
                user_token.status = TokenStatus.REFRESH_FAILED
                self.db.commit()
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
            
            self.db.commit()
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error in token refresh: {str(e)}")
            user_token.status = TokenStatus.REFRESH_FAILED
            self.db.commit()
            return False
        except Exception as e:
            logger.error(f"Token refresh error: {str(e)}")
            user_token.status = TokenStatus.REFRESH_FAILED
            self.db.commit()
            return False
    
    def revoke_token(self, token_id: int) -> bool:
        """
        Revoke an OAuth token
        """
        user_token = self.db.query(UserEmailToken).filter(
            UserEmailToken.id == token_id
        ).first()
        
        if not user_token:
            return False
        
        # Mark as revoked in database
        user_token.status = TokenStatus.REVOKED
        user_token.updated_at = datetime.utcnow()
        self.db.commit()
        
        # TODO: Also revoke with provider if they support it
        return True
    
    def get_valid_token(self, token_id: int) -> Optional[UserEmailToken]:
        """
        Get a valid token, refreshing if necessary
        """
        user_token = self.db.query(UserEmailToken).filter(
            UserEmailToken.id == token_id,
            UserEmailToken.status == TokenStatus.ACTIVE
        ).first()
        
        if not user_token:
            return None
        
        # Check if token is expired and refresh if possible
        if user_token.is_expired() and user_token.refresh_token:
            if self.refresh_token(token_id):
                # Refresh the object from database
                self.db.refresh(user_token)
            else:
                return None
        
        # Update last used timestamp
        user_token.last_used_at = datetime.utcnow()
        self.db.commit()
        
        return user_token if user_token.is_active() else None