"""
User Email service for sending emails via provider APIs (Google/Microsoft)
Separated from system email logic as per requirements.
Uses OAuth tokens to send emails from user's connected accounts.
"""

import logging
from typing import Optional, Dict, Any, Tuple
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.email import MailAccount
from app.models.oauth_models import UserEmailToken, OAuthProvider
from app.services.oauth_service import OAuth2Service
from app.core.logging import get_logger
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import base64
from app.core.config import settings
from msal import ConfidentialClientApplication
import requests
from app.utils.crypto_aes_gcm import encrypt_aes_gcm, decrypt_aes_gcm, EncryptionKeysAESGCM

logger = get_logger(__name__)

class UserEmailService:
    def __init__(self):
        pass  # Removed self.oauth_service initialization; will create locally in methods

    async def send_email(self, 
                         db: AsyncSession,
                         account_id: int,
                         to_email: str, 
                         subject: str, 
                         body: str, 
                         html_body: Optional[str] = None,
                         bcc_emails: Optional[list[str]] = None) -> tuple[bool, Optional[str]]:
        """
        Send email using the user's connected email account via provider API.
        
        Args:
            db: Async database session
            account_id: ID of the MailAccount to send from
            to_email: Recipient email
            subject: Email subject
            body: Plain text body
            html_body: Optional HTML body
            bcc_emails: Optional BCC recipients
            
        Returns:
            (success: bool, error_msg: Optional[str])
        """
        try:
            # Create local OAuth2Service instance with db
            oauth_service = OAuth2Service(db)
            
            # Get mail account
            stmt = select(MailAccount).filter(MailAccount.id == account_id)
            result = await db.execute(stmt)
            account = result.scalars().first()
            
            if not account:
                return False, "Mail account not found"
            
            if not account.oauth_token_id:
                return False, "No OAuth token associated with account"
            
            # Get valid token (will refresh if needed)
            token = await oauth_service.get_valid_token(account.oauth_token_id)
            if not token:
                return False, "Failed to get valid OAuth token. If status is REFRESH_FAILED, revoke token via /api/v1/email/oauth/revoke/{token_id} and re-authorize via /api/v1/oauth/login/{provider}. If recently changed to production, the old refresh token may still expire (7-day limit from testing). Revoke and re-auth to get a permanent one."
            
            success = False
            error = None
            
            if token.provider == OAuthProvider.GOOGLE.name or token.provider == OAuthProvider.GMAIL.name:
                success, error = await self._send_google_email(oauth_service, token, to_email, subject, body, html_body, bcc_emails)
            elif token.provider == OAuthProvider.MICROSOFT.name or token.provider == OAuthProvider.OUTLOOK.name:
                success, error = await self._send_microsoft_email(oauth_service, token, to_email, subject, body, html_body, bcc_emails)
            else:
                return False, f"Unsupported provider: {token.provider}"
            
            if success:
                logger.info(f"Email sent successfully via {token.provider} API to {to_email}")
                return True, None
            else:
                if "REFRESH_FAILED" in error or "cannot be reused" in error:
                    error += " To resolve, revoke the token using POST /api/v1/email/oauth/revoke/{token_id}, then re-authorize using POST /api/v1/oauth/login/{provider}. If recently changed to production, the old refresh token may still expire (7-day limit from testing). Revoke and re-auth to get a permanent one."
                elif "Bad Request" in error:
                    error += " Check Google API scopes and credentials. Ensure 'https://mail.google.com/' scope is enabled and app is verified if needed."
                return False, error
                
        except Exception as e:
            error_msg = f"Failed to send user email: {str(e)}"
            if "REFRESH_FAILED" in error_msg or "cannot be reused" in error_msg:
                error_msg += " To resolve, revoke the token using POST /api/v1/email/oauth/revoke/{token_id}, then re-authorize using POST /api/v1/oauth/login/{provider}. If recently changed to production, the old refresh token may still expire (7-day limit from testing). Revoke and re-auth to get a permanent one."
            elif "Bad Request" in error_msg:
                error_msg += " Check Google API scopes and credentials. Ensure 'https://mail.google.com/' scope is enabled and app is verified if needed."
            logger.error(error_msg)
            return False, error_msg
    
    async def _send_google_email(self, 
                                 oauth_service: OAuth2Service,
                                 token: UserEmailToken,
                                 to_email: str, 
                                 subject: str, 
                                 body: str, 
                                 html_body: Optional[str],
                                 bcc_emails: Optional[list[str]]) -> tuple[bool, Optional[str]]:
        """Send email via Gmail API"""
        try:
            # Decrypt tokens
            access_token = decrypt_aes_gcm(token.access_token_encrypted, EncryptionKeysAESGCM.OAUTH)
            refresh_token = decrypt_aes_gcm(token.refresh_token_encrypted, EncryptionKeysAESGCM.OAUTH) if token.refresh_token_encrypted else None
            
            creds = Credentials(
                token=access_token,
                refresh_token=refresh_token,
                client_id=settings.GOOGLE_CLIENT_ID,
                client_secret=settings.GOOGLE_CLIENT_SECRET,
                token_uri='https://oauth2.googleapis.com/token'
            )
            
            # Refresh if needed (though get_valid_token already handles)
            if creds.expired and creds.refresh_token:
                creds.refresh(Request())
            
            service = build('gmail', 'v1', credentials=creds)
            
            # Create message
            message = MIMEMultipart('alternative')
            message['To'] = to_email
            message['Subject'] = subject
            message['From'] = token.email_address
            
            if bcc_emails:
                message['Bcc'] = ', '.join(bcc_emails)
            
            # Plain text
            text_part = MIMEText(body, 'plain')
            message.attach(text_part)
            
            # HTML if provided
            if html_body:
                html_part = MIMEText(html_body, 'html')
                message.attach(html_part)
            
            # Encode for API
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            
            # Send
            send_request = service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            )
            send_request.execute()
            
            return True, None
            
        except HttpError as e:
            error_msg = f"Gmail API error: {str(e)}"
            if 'Bad Request' in str(e):
                error_msg += " (400 Bad Request: Likely invalid scope or unverified app. Ensure 'https://mail.google.com/' scope and verify app in Google Console if public)."
            return False, error_msg
        except Exception as e:
            return False, f"Failed to send via Gmail API: {str(e)}"
    
    async def _send_microsoft_email(self, 
                                    oauth_service: OAuth2Service,
                                    token: UserEmailToken,
                                    to_email: str, 
                                    subject: str, 
                                    body: str, 
                                    html_body: Optional[str],
                                    bcc_emails: Optional[list[str]]) -> tuple[bool, Optional[str]]:
        """Send email via Microsoft Graph API"""
        try:
            # Acquire fresh token
            app = ConfidentialClientApplication(
                settings.MICROSOFT_CLIENT_ID,
                authority=settings.MICROSOFT_AUTHORITY,
                client_credential=settings.MICROSOFT_CLIENT_SECRET
            )
            
            refresh_token = decrypt_aes_gcm(token.refresh_token_encrypted, EncryptionKeysAESGCM.OAUTH)
            result = app.acquire_token_by_refresh_token(
                refresh_token,
                scopes=["https://graph.microsoft.com/Mail.Send"]
            )
            
            if 'error' in result:
                return False, f"Microsoft token error: {result.get('error_description')}"
            
            access_token = result['access_token']
            
            # Send email via Graph API
            endpoint = f"https://graph.microsoft.com/v1.0/users/{token.email_address}/sendMail"
            
            message = {
                "subject": subject,
                "body": {
                    "contentType": "HTML" if html_body else "Text",
                    "content": html_body or body
                },
                "toRecipients": [{"emailAddress": {"address": to_email}}]
            }
            
            if bcc_emails:
                message["bccRecipients"] = [{"emailAddress": {"address": email}} for email in bcc_emails]
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(endpoint, headers=headers, json={"message": message})
            
            if response.status_code == 202:
                return True, None
            else:
                return False, f"Microsoft Graph error: {response.text}"
            
        except Exception as e:
            return False, f"Failed to send via Microsoft Graph: {str(e)}"

# Global instance
user_email_service = UserEmailService()