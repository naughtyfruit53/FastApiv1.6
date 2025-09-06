"""
Email API Service for Gmail and Microsoft Graph integration
"""

import logging
import base64
import json
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import re

import requests
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from sqlalchemy.orm import Session

from app.models.oauth_models import UserEmailToken, OAuthProvider, TokenStatus
from app.schemas.oauth_schemas import (
    EmailMessage, EmailListResponse, EmailDetailResponse, 
    EmailAttachment, EmailComposeRequest, EmailComposeResponse
)
from app.services.oauth_service import OAuth2Service

logger = logging.getLogger(__name__)


class EmailAPIService:
    """Service for interacting with email APIs (Gmail, Microsoft Graph)"""
    
    def __init__(self, db: Session):
        self.db = db
        self.oauth_service = OAuth2Service(db)
    
    def _get_valid_token(self, token_id: int) -> Optional[UserEmailToken]:
        """Get a valid token, refreshing if necessary"""
        return self.oauth_service.get_valid_token(token_id)
    
    def _build_gmail_service(self, token: UserEmailToken):
        """Build Gmail API service"""
        creds = Credentials(
            token=token.access_token,
            refresh_token=token.refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=None,  # Not needed for API calls
            client_secret=None
        )
        
        # Build the service
        service = build('gmail', 'v1', credentials=creds)
        return service
    
    def _get_graph_headers(self, token: UserEmailToken) -> Dict[str, str]:
        """Get headers for Microsoft Graph API"""
        return {
            'Authorization': f'Bearer {token.access_token}',
            'Content-Type': 'application/json'
        }
    
    def list_emails_gmail(
        self, 
        token_id: int, 
        folder: str = "INBOX", 
        limit: int = 50, 
        offset: int = 0,
        unread_only: bool = False,
        search_query: Optional[str] = None
    ) -> EmailListResponse:
        """List emails from Gmail"""
        token = self._get_valid_token(token_id)
        if not token:
            raise ValueError("Invalid or expired token")
        
        try:
            service = self._build_gmail_service(token)
            
            # Build query
            query_parts = []
            if unread_only:
                query_parts.append("is:unread")
            if search_query:
                query_parts.append(search_query)
            
            query = " ".join(query_parts) if query_parts else None
            
            # Get message list
            result = service.users().messages().list(
                userId='me',
                labelIds=[folder] if folder != "INBOX" else None,
                q=query,
                maxResults=limit
            ).execute()
            
            messages = result.get('messages', [])
            total_count = result.get('resultSizeEstimate', 0)
            
            # Get message details
            email_messages = []
            for msg in messages:
                try:
                    msg_detail = service.users().messages().get(
                        userId='me', 
                        id=msg['id'],
                        format='metadata',
                        metadataHeaders=['Subject', 'From', 'To', 'Date']
                    ).execute()
                    
                    headers = {h['name']: h['value'] for h in msg_detail.get('payload', {}).get('headers', [])}
                    
                    # Parse from address
                    from_header = headers.get('From', '')
                    from_match = re.match(r'(.*?)\s*<(.+?)>', from_header)
                    if from_match:
                        from_name = from_match.group(1).strip(' "')
                        from_address = from_match.group(2)
                    else:
                        from_name = None
                        from_address = from_header
                    
                    # Parse date
                    date_str = headers.get('Date', '')
                    try:
                        received_at = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %z')
                    except:
                        received_at = datetime.utcnow()
                    
                    # Check if read
                    label_ids = msg_detail.get('labelIds', [])
                    is_read = 'UNREAD' not in label_ids
                    
                    # Get snippet for preview
                    snippet = msg_detail.get('snippet', '')
                    
                    email_msg = EmailMessage(
                        id=msg['id'],
                        subject=headers.get('Subject', '(No Subject)'),
                        sender=from_address,
                        recipients=[headers.get('To', '')],
                        received_at=received_at,
                        body_preview=snippet,
                        is_read=is_read,
                        has_attachments=any(part.get('filename') for part in self._get_parts(msg_detail.get('payload', {}))),
                        folder=folder
                    )
                    email_messages.append(email_msg)
                    
                except Exception as e:
                    logger.error(f"Error processing Gmail message {msg['id']}: {e}")
                    continue
            
            return EmailListResponse(
                emails=email_messages,
                total_count=total_count,
                has_more=len(messages) >= limit
            )
            
        except Exception as e:
            logger.error(f"Error listing Gmail emails: {e}")
            raise ValueError(f"Failed to list Gmail emails: {e}")
    
    def list_emails_microsoft(
        self, 
        token_id: int, 
        folder: str = "INBOX", 
        limit: int = 50, 
        offset: int = 0,
        unread_only: bool = False,
        search_query: Optional[str] = None
    ) -> EmailListResponse:
        """List emails from Microsoft Graph"""
        token = self._get_valid_token(token_id)
        if not token:
            raise ValueError("Invalid or expired token")
        
        try:
            headers = self._get_graph_headers(token)
            
            # Build Graph API URL
            folder_map = {
                "INBOX": "inbox",
                "SENT": "sentitems",
                "DRAFTS": "drafts",
                "DELETED": "deleteditems"
            }
            graph_folder = folder_map.get(folder, folder.lower())
            
            url = f"https://graph.microsoft.com/v1.0/me/mailFolders/{graph_folder}/messages"
            
            # Build parameters
            params = {
                '$top': limit,
                '$skip': offset,
                '$select': 'id,subject,from,toRecipients,receivedDateTime,bodyPreview,isRead,hasAttachments',
                '$orderby': 'receivedDateTime desc'
            }
            
            if unread_only:
                params['$filter'] = 'isRead eq false'
            
            if search_query:
                params['$search'] = f'"{search_query}"'
            
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            messages = data.get('value', [])
            
            # Convert to our format
            email_messages = []
            for msg in messages:
                try:
                    from_addr = msg.get('from', {}).get('emailAddress', {})
                    recipients = [r.get('emailAddress', {}).get('address', '') 
                                for r in msg.get('toRecipients', [])]
                    
                    received_str = msg.get('receivedDateTime', '')
                    try:
                        received_at = datetime.fromisoformat(received_str.replace('Z', '+00:00'))
                    except:
                        received_at = datetime.utcnow()
                    
                    email_msg = EmailMessage(
                        id=msg['id'],
                        subject=msg.get('subject', '(No Subject)'),
                        sender=from_addr.get('address', ''),
                        recipients=recipients,
                        received_at=received_at,
                        body_preview=msg.get('bodyPreview', ''),
                        is_read=msg.get('isRead', False),
                        has_attachments=msg.get('hasAttachments', False),
                        folder=folder
                    )
                    email_messages.append(email_msg)
                    
                except Exception as e:
                    logger.error(f"Error processing Microsoft message {msg.get('id')}: {e}")
                    continue
            
            total_count = len(messages)  # Graph API doesn't provide total count easily
            
            return EmailListResponse(
                emails=email_messages,
                total_count=total_count,
                has_more=len(messages) >= limit
            )
            
        except Exception as e:
            logger.error(f"Error listing Microsoft emails: {e}")
            raise ValueError(f"Failed to list Microsoft emails: {e}")
    
    def get_email_detail_gmail(self, token_id: int, message_id: str) -> EmailDetailResponse:
        """Get detailed email content from Gmail"""
        token = self._get_valid_token(token_id)
        if not token:
            raise ValueError("Invalid or expired token")
        
        try:
            service = self._build_gmail_service(token)
            
            # Get full message
            msg = service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            
            payload = msg.get('payload', {})
            headers = {h['name']: h['value'] for h in payload.get('headers', [])}
            
            # Parse from address
            from_header = headers.get('From', '')
            from_match = re.match(r'(.*?)\s*<(.+?)>', from_header)
            if from_match:
                from_name = from_match.group(1).strip(' "')
                from_address = from_match.group(2)
            else:
                from_name = None
                from_address = from_header
            
            # Parse recipients
            recipients = []
            for field in ['To', 'Cc', 'Bcc']:
                if headers.get(field):
                    recipients.extend(self._parse_email_addresses(headers[field]))
            
            # Parse date
            date_str = headers.get('Date', '')
            try:
                received_at = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %z')
            except:
                received_at = datetime.utcnow()
            
            # Extract body content
            body_html, body_text = self._extract_body_gmail(payload)
            
            # Extract attachments
            attachments = self._extract_attachments_gmail(payload)
            
            # Check if read
            label_ids = msg.get('labelIds', [])
            is_read = 'UNREAD' not in label_ids
            
            return EmailDetailResponse(
                id=message_id,
                subject=headers.get('Subject', '(No Subject)'),
                sender=from_address,
                recipients=recipients,
                received_at=received_at,
                body_preview=msg.get('snippet', ''),
                is_read=is_read,
                has_attachments=len(attachments) > 0,
                folder="INBOX",  # Would need additional logic to determine folder
                body_html=body_html,
                body_text=body_text,
                attachments=attachments,
                headers=headers
            )
            
        except Exception as e:
            logger.error(f"Error getting Gmail email detail: {e}")
            raise ValueError(f"Failed to get Gmail email detail: {e}")
    
    def send_email_gmail(self, token_id: int, compose_request: EmailComposeRequest) -> EmailComposeResponse:
        """Send email via Gmail"""
        token = self._get_valid_token(token_id)
        if not token:
            raise ValueError("Invalid or expired token")
        
        try:
            service = self._build_gmail_service(token)
            
            # Create message
            message = self._create_mime_message_gmail(compose_request)
            
            # Send message
            result = service.users().messages().send(
                userId='me',
                body={'raw': message}
            ).execute()
            
            return EmailComposeResponse(
                success=True,
                message="Email sent successfully",
                message_id=result.get('id'),
                sent_at=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Error sending Gmail email: {e}")
            return EmailComposeResponse(
                success=False,
                message=f"Failed to send email: {e}"
            )
    
    def send_email_microsoft(self, token_id: int, compose_request: EmailComposeRequest) -> EmailComposeResponse:
        """Send email via Microsoft Graph"""
        token = self._get_valid_token(token_id)
        if not token:
            raise ValueError("Invalid or expired token")
        
        try:
            headers = self._get_graph_headers(token)
            
            # Build message payload
            message_data = {
                "message": {
                    "subject": compose_request.subject,
                    "body": {
                        "contentType": "HTML" if compose_request.html_body else "Text",
                        "content": compose_request.html_body or compose_request.body
                    },
                    "toRecipients": [
                        {"emailAddress": {"address": addr}} for addr in compose_request.to
                    ]
                }
            }
            
            if compose_request.cc:
                message_data["message"]["ccRecipients"] = [
                    {"emailAddress": {"address": addr}} for addr in compose_request.cc
                ]
            
            if compose_request.bcc:
                message_data["message"]["bccRecipients"] = [
                    {"emailAddress": {"address": addr}} for addr in compose_request.bcc
                ]
            
            # Send message
            url = "https://graph.microsoft.com/v1.0/me/sendMail"
            response = requests.post(url, headers=headers, json=message_data)
            response.raise_for_status()
            
            return EmailComposeResponse(
                success=True,
                message="Email sent successfully",
                sent_at=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Error sending Microsoft email: {e}")
            return EmailComposeResponse(
                success=False,
                message=f"Failed to send email: {e}"
            )
    
    # Helper methods
    def _get_parts(self, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Recursively get all parts from email payload"""
        parts = []
        if 'parts' in payload:
            for part in payload['parts']:
                parts.extend(self._get_parts(part))
        else:
            parts.append(payload)
        return parts
    
    def _extract_body_gmail(self, payload: Dict[str, Any]) -> Tuple[Optional[str], Optional[str]]:
        """Extract HTML and text body from Gmail payload"""
        html_body = None
        text_body = None
        
        parts = self._get_parts(payload)
        
        for part in parts:
            mime_type = part.get('mimeType', '')
            body = part.get('body', {})
            
            if body.get('data'):
                content = base64.urlsafe_b64decode(body['data']).decode('utf-8', errors='ignore')
                
                if mime_type == 'text/html':
                    html_body = content
                elif mime_type == 'text/plain':
                    text_body = content
        
        return html_body, text_body
    
    def _extract_attachments_gmail(self, payload: Dict[str, Any]) -> List[EmailAttachment]:
        """Extract attachments from Gmail payload"""
        attachments = []
        parts = self._get_parts(payload)
        
        for part in parts:
            filename = part.get('filename')
            if filename:
                body = part.get('body', {})
                attachment = EmailAttachment(
                    id=body.get('attachmentId', ''),
                    name=filename,
                    content_type=part.get('mimeType', ''),
                    size=body.get('size', 0)
                )
                attachments.append(attachment)
        
        return attachments
    
    def _parse_email_addresses(self, address_string: str) -> List[str]:
        """Parse email addresses from a header string"""
        # Simple email extraction - could be improved
        import re
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        return re.findall(email_pattern, address_string)
    
    def _create_mime_message_gmail(self, compose_request: EmailComposeRequest) -> str:
        """Create MIME message for Gmail API"""
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        import base64
        
        if compose_request.html_body:
            msg = MIMEMultipart('alternative')
            msg.attach(MIMEText(compose_request.body, 'plain'))
            msg.attach(MIMEText(compose_request.html_body, 'html'))
        else:
            msg = MIMEText(compose_request.body)
        
        msg['to'] = ', '.join(compose_request.to)
        msg['subject'] = compose_request.subject
        
        if compose_request.cc:
            msg['cc'] = ', '.join(compose_request.cc)
        
        raw_message = base64.urlsafe_b64encode(msg.as_bytes()).decode()
        return raw_message