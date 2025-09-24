"""
Email API Service for fetching and sending emails using OAuth providers
"""

import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, cast
import logging
import io
import os
from typing import TYPE_CHECKING
from fastapi import UploadFile

if TYPE_CHECKING:
    from msgraph.generated.models.file_attachment import FileAttachment

logger = logging.getLogger(__name__)

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from msal import ConfidentialClientApplication
from azure.identity import ClientSecretCredential
from msgraph import GraphServiceClient
from msgraph.generated.models.message import Message
from msgraph.generated.models.item_body import ItemBody
from msgraph.generated.models.body_type import BodyType
from msgraph.generated.models.recipient import Recipient
from msgraph.generated.models.email_address import EmailAddress
from msgraph.generated.users.item.send_mail.send_mail_post_request_body import SendMailPostRequestBody
from msgraph.generated.users.item.mail_folders.item.messages.messages_request_builder import MessagesRequestBuilder
from msgraph.generated.models.attachment import Attachment

from app.core.config import settings
from app.models.oauth_models import UserEmailToken, OAuthProvider
from app.models.mail_management import Email, EmailAttachment, SentEmail
from app.schemas.mail_schemas import MailSyncResponse, MailComposeRequest, SentEmailResponse
from app.utils.encryption import encrypt_file_data  # Assuming you have encryption utils

class EmailAPIService:
    def __init__(self, db: Session):
        self.db = db

    async def list_emails(self, user, token_id: Optional[int], folder: str, page: int, per_page: int) -> Dict:
        """List emails from DB"""
        query = self.db.query(Email).filter(Email.organization_id == user.organization_id)
        
        if token_id:
            query = query.filter(Email.account_id == token_id)
        
        if folder:
            folder_upper = folder.upper()
            if folder_upper in ['INBOX', 'SENT', 'DRAFTS', 'SPAM', 'TRASH', 'ARCHIVED']:
                query = query.filter(Email.folder == folder_upper)
            elif folder_upper == 'STARRED':
                query = query.filter(Email.is_flagged == True)
            elif folder_upper == 'IMPORTANT':
                query = query.filter(Email.is_important == True)
            elif folder_upper == 'SNOOZED':
                query = query.filter(Email.status == 'SNOOZED')
            elif folder_upper == 'CATEGORIES':
                query = query.filter(Email.labels != None)
        
        total = query.count()
        emails = query.order_by(Email.received_at.desc()).offset((page - 1) * per_page).limit(per_page).all()
        
        # Eager load attachments
        for email_obj in emails:
            email_obj.attachments  # Trigger relation load
        
        return {
            "emails": [email.__dict__ for email in emails],
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page
        }

    async def get_email_detail(self, user, email_id: int) -> Dict:
        """Get email from DB with attachments"""
        email = self.db.query(Email).filter(
            Email.id == email_id,
            Email.organization_id == user.organization_id
        ).first()
        
        if not email:
            raise HTTPException(404, "Email not found")
        
        # Load attachments
        email.attachments
        
        return email.__dict__

    async def update_email(self, user, email_id: int, update_data: Dict) -> Dict:
        """Update email in DB and sync to provider"""
        email = self.db.query(Email).filter(
            Email.id == email_id,
            Email.organization_id == user.organization_id
        ).first()
        
        if not email:
            raise HTTPException(404, "Email not found")
        
        old_status = email.status
        for key, value in update_data.items():
            setattr(email, key, value)
        
        self.db.commit()
        self.db.refresh(email)
        
        # Sync to provider if status changed
        if 'status' in update_data and update_data['status'] != old_status:
            token = self.db.query(UserEmailToken).filter(UserEmailToken.id == email.account_id).first()
            if token:
                await self._sync_status_to_provider(token, email, update_data['status'])
        
        return email.__dict__

    async def _sync_status_to_provider(self, token: UserEmailToken, email: Email, new_status: str):
        """Sync status change to email provider"""
        try:
            if token.provider == OAuthProvider.GOOGLE:
                creds = Credentials(
                    token=token.access_token,
                    refresh_token=token.refresh_token,
                    token_uri="https://oauth2.googleapis.com/token",
                    client_id=settings.GOOGLE_CLIENT_ID,
                    client_secret=settings.GOOGLE_CLIENT_SECRET
                )
                
                if creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                    token.access_token = creds.token
                    token.refresh_token = creds.refresh_token
                    token.expires_at = creds.expiry
                    self.db.commit()
                
                service = build('gmail', 'v1', credentials=creds)
                
                if new_status == 'READ':
                    service.users().messages().modify(
                        userId='me',
                        id=email.message_id,
                        body={'removeLabelIds': ['UNREAD']}
                    ).execute()
                elif new_status == 'UNREAD':
                    service.users().messages().modify(
                        userId='me',
                        id=email.message_id,
                        body={'addLabelIds': ['UNREAD']}
                    ).execute()
                
            elif token.provider == OAuthProvider.MICROSOFT:
                app = ConfidentialClientApplication(
                    client_id=settings.MICROSOFT_CLIENT_ID,
                    authority=f"https://login.microsoftonline.com/common",
                    client_credential=settings.MICROSOFT_CLIENT_SECRET
                )
                
                result = app.acquire_token_by_refresh_token(
                    token.refresh_token,
                    scopes=["https://graph.microsoft.com/Mail.ReadWrite"]
                )
                
                if "access_token" in result:
                    access_token = result["access_token"]
                    token.access_token = access_token
                    if "refresh_token" in result:
                        token.refresh_token = result["refresh_token"]
                    if "expires_in" in result:
                        token.expires_at = datetime.utcnow() + timedelta(seconds=result["expires_in"])
                    self.db.commit()
                
                credential = ClientSecretCredential(
                    tenant_id="common",
                    client_id=settings.MICROSOFT_CLIENT_ID,
                    client_secret=settings.MICROSOFT_CLIENT_SECRET
                )
                
                graph_client = GraphServiceClient(credentials=credential)
                
                await graph_client.me.messages.by_message_id(email.message_id).patch(
                    Message(is_read=(new_status == 'READ'))
                )
            
            logger.info(f"Synced status {new_status} for email {email.id} to provider")
            
        except Exception as e:
            logger.error(f"Failed to sync status for email {email.id}: {str(e)}")

    async def delete_email(self, user, email_id: int) -> Dict:
        """Delete email from DB"""
        email = self.db.query(Email).filter(
            Email.id == email_id,
            Email.organization_id == user.organization_id
        ).first()
        
        if not email:
            raise HTTPException(404, "Email not found")
        
        self.db.delete(email)
        self.db.commit()
        return {"success": True}

    async def list_sent_emails(self, user, page: int, per_page: int) -> Dict:
        """List sent emails from DB"""
        query = self.db.query(SentEmail).filter(SentEmail.organization_id == user.organization_id)
        
        total = query.count()
        emails = query.offset((page - 1) * per_page).limit(per_page).order_by(SentEmail.sent_at.desc()).all()
        
        return {
            "emails": [email.__dict__ for email in emails],
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page
        }

    async def send_email(self, user, token_id: int, compose_request: MailComposeRequest, attachments: List[UploadFile] = None) -> SentEmailResponse:
        """Send email using provider API"""
        token = self.db.query(UserEmailToken).filter(
            UserEmailToken.id == token_id,
            UserEmailToken.user_id == user.id
        ).first()
        
        if not token:
            raise HTTPException(404, "Token not found")
        
        if token.provider == OAuthProvider.GOOGLE:
            success = self._send_google_email(token, compose_request, attachments)
        elif token.provider == OAuthProvider.MICROSOFT:
            success = await self._send_microsoft_email(token, compose_request, attachments)
        else:
            raise HTTPException(400, "Unsupported provider")
        
        if not success:
            raise HTTPException(500, "Failed to send email")
        
        # Store sent email in DB
        sent_email = SentEmail(
            subject=compose_request.subject,
            to_addresses=compose_request.to_addresses,
            cc_addresses=compose_request.cc_addresses,
            bcc_addresses=compose_request.bcc_addresses,
            body_text=compose_request.body_text,
            body_html=compose_request.body_html,
            account_id=token_id,
            organization_id=user.organization_id,
            sent_by=user.id,
            status="SENT",
            sent_at=datetime.utcnow()
        )
        
        self.db.add(sent_email)
        self.db.commit()
        self.db.refresh(sent_email)
        
        return sent_email.__dict__

    def _send_google_email(self, token: UserEmailToken, compose_request: MailComposeRequest, attachments: List[UploadFile] = None) -> bool:
        """Send email via Gmail API with attachments"""
        try:
            creds = Credentials(
                token=token.access_token,
                refresh_token=token.refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=settings.GOOGLE_CLIENT_ID,
                client_secret=settings.GOOGLE_CLIENT_SECRET
            )
            
            if creds.expired and creds.refresh_token:
                creds.refresh(Request())
                # Update token in DB
                token.access_token = creds.token
                token.refresh_token = creds.refresh_token
                token.expires_at = creds.expiry
                self.db.commit()
            
            service = build('gmail', 'v1', credentials=creds)
            
            message = self._create_mime_message(
                token.email_address,
                compose_request.to_addresses,
                compose_request.subject,
                compose_request.body_text,
                compose_request.body_html,
                compose_request.cc_addresses,
                compose_request.bcc_addresses,
                attachments
            )
            
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            
            send_request = service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            )
            send_request.execute()
            
            return True
            
        except Exception as e:
            logger.error(f"Gmail send error: {str(e)}")
            return False

    async def _send_microsoft_email(self, token: UserEmailToken, compose_request: MailComposeRequest, attachments: List[UploadFile] = None) -> bool:
        """Send email via Microsoft Graph with attachments"""
        try:
            app = ConfidentialClientApplication(
                client_id=settings.MICROSOFT_CLIENT_ID,
                authority=f"https://login.microsoftonline.com/common",
                client_credential=settings.MICROSOFT_CLIENT_SECRET
            )
            
            # Acquire token using refresh
            result = app.acquire_token_by_refresh_token(
                token.refresh_token,
                scopes=["https://graph.microsoft.com/Mail.Send"]
            )
            
            if "access_token" in result:
                access_token = result["access_token"]
                # Update token
                token.access_token = access_token
                if "refresh_token" in result:
                    token.refresh_token = result["refresh_token"]
                if "expires_in" in result:
                    token.expires_at = datetime.utcnow() + timedelta(seconds=result["expires_in"])
                self.db.commit()
            else:
                return False
            
            credential = ClientSecretCredential(
                tenant_id="common",
                client_id=settings.MICROSOFT_CLIENT_ID,
                client_secret=settings.MICROSOFT_CLIENT_SECRET
            )
            
            graph_client = GraphServiceClient(credentials=credential)
            
            message = Message(
                subject=compose_request.subject,
                body=ItemBody(
                    content_type=BodyType.HTML if compose_request.body_html else BodyType.TEXT,
                    content=compose_request.body_html or compose_request.body_text
                ),
                to_recipient=[Recipient(email_address=EmailAddress(address=addr)) for addr in compose_request.to_addresses],
                cc_recipient=[Recipient(email_address=EmailAddress(address=addr)) for addr in compose_request.cc_addresses or []],
                bcc_recipient=[Recipient(email_address=EmailAddress(address=addr)) for addr in compose_request.bcc_addresses or []]
            )
            
            # Add attachments if present
            if attachments:
                for att in attachments:
                    content_bytes = await att.read()
                    file_att = FileAttachment(
                        name=att.filename,
                        content_bytes=content_bytes,
                        content_type=att.content_type
                    )
                    message.attachments.append(file_att)
            
            request_body = SendMailPostRequestBody(message=message)
            
            await graph_client.me.send_mail.post(request_body)
            
            return True
            
        except Exception as e:
            logger.error(f"Microsoft Graph send error: {str(e)}")
            return False

    def _create_mime_message(self, sender, to, subject, body_text, body_html=None, cc=None, bcc=None, attachments=None):
        """Create MIME message with attachments"""
        message = MIMEMultipart('mixed')
        message['From'] = sender
        message['To'] = ', '.join(to)
        if cc:
            message['Cc'] = ', '.join(cc)
        if bcc:
            message['Bcc'] = ', '.join(bcc)
        message['Subject'] = subject
        
        # Alternative part for text/html
        alternative = MIMEMultipart('alternative')
        text_part = MIMEText(body_text, 'plain')
        alternative.attach(text_part)
        
        if body_html:
            html_part = MIMEText(body_html, 'html')
            alternative.attach(html_part)
        
        message.attach(alternative)
        
        # Add attachments
        if attachments:
            for att in attachments:
                att.file.seek(0)  # Reset file pointer
                mime_att = MIMEText(att.file.read(), 'base64', _charset='UTF-8')
                mime_att.add_header('Content-Disposition', f'attachment; filename="{att.filename}"')
                mime_att.add_header('Content-Type', att.content_type or 'application/octet-stream')
                message.attach(mime_att)
        
        return message

    async def sync_emails(self, user, token_id: Optional[int], force_sync: bool) -> MailSyncResponse:
        """Sync emails from providers - limits initial sync to last 30 days"""
        tokens = self.db.query(UserEmailToken).filter(
            UserEmailToken.user_id == user.id,
            UserEmailToken.organization_id == user.organization_id
        )
        
        if token_id:
            tokens = tokens.filter(UserEmailToken.id == token_id)
        
        tokens = tokens.all()
        
        accounts_synced = 0
        emails_imported = 0
        errors = []
        
        for token in tokens:
            try:
                new_emails = 0
                if token.provider == OAuthProvider.GOOGLE:
                    new_emails = self._sync_google_emails(token, force_sync)
                elif token.provider == OAuthProvider.MICROSOFT:
                    new_emails = await self._sync_microsoft_emails(token, force_sync)
                
                token.last_sync_at = datetime.utcnow()
                token.last_sync_status = "SUCCESS"
                token.last_sync_error = None
                emails_imported += new_emails
                accounts_synced += 1

                # Setup watch for Google after sync
                if token.provider == OAuthProvider.GOOGLE:
                    self._setup_google_watch(token)

            except Exception as e:
                errors.append(f"{token.email_address}: {str(e)}")
                token.last_sync_status = "ERROR"
                token.last_sync_error = str(e)
                logger.error(f"Sync error for {token.email_address}: {str(e)}")
        
        self.db.commit()
        
        return MailSyncResponse(
            success=len(errors) == 0,
            message="Sync completed" if len(errors) == 0 else "Sync completed with errors",
            accounts_synced=accounts_synced,
            emails_imported=emails_imported,
            errors=errors if errors else None
        )

    def _sync_google_emails(self, token: UserEmailToken, force_sync: bool, history_id: Optional[str] = None) -> int:
        """Sync emails from Gmail, with optional incremental sync using history_id"""
        creds = Credentials(
            token=token.access_token,
            refresh_token=token.refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET
        )
        
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            token.access_token = creds.token
            token.refresh_token = creds.refresh_token
            token.expires_at = creds.expiry
            self.db.commit()
        
        service = build('gmail', 'v1', credentials=creds)
        
        new_emails = 0
        
        if history_id and token.last_history_id:
            # Incremental sync using history
            logger.info(f"Performing incremental sync with history_id: {history_id}")
            try:
                history_response = service.users().history().list(
                    userId='me',
                    startHistoryId=token.last_history_id,
                    labelId=['INBOX']
                ).execute()
                
                history = history_response.get('history', [])
                for hist in history:
                    for msg_added in hist.get('messagesAdded', []):
                        msg = msg_added['message']
                        new_emails += self._process_google_message(service, token, msg['id'])
                
                # Update last_history_id
                token.last_history_id = history_id
                self.db.commit()
                
            except HttpError as e:
                if e.resp.status == 404:  # History ID too old, fallback to full sync
                    logger.warning("History ID too old, falling back to full sync")
                    new_emails = self._full_sync_google_emails(service, token, force_sync)
                else:
                    raise
        else:
            # Full sync - limit to last 30 days for initial
            new_emails = self._full_sync_google_emails(service, token, force_sync)
        
        logger.info(f"Imported {new_emails} new emails for {token.email_address}")
        return new_emails

    def _full_sync_google_emails(self, service, token: UserEmailToken, force_sync: bool) -> int:
        """Perform full sync of Gmail emails - limited to last 30 days initially"""
        # Always limit initial sync to last 30 days to avoid stuck sync
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        q = f"after:{int(cutoff_date.timestamp())}"
        
        if force_sync:
            # For force, go back further if needed
            q = None  # Full but still paginated
        
        logger.info(f"Full syncing Gmail with query: {q}")
        
        # Fetch messages with pagination
        results = service.users().messages().list(userId='me', q=q, maxResults=100, includeSpamTrash=True).execute()
        messages = results.get('messages', [])
        logger.info(f"Found {len(messages)} messages in first page")
        
        while 'nextPageToken' in results:
            results = service.users().messages().list(
                userId='me', 
                q=q, 
                maxResults=100, 
                pageToken=results['nextPageToken'], 
                includeSpamTrash=True
            ).execute()
            messages.extend(results.get('messages', []))
            logger.info(f"Paginated: total {len(messages)} messages")
        
        logger.info(f"Total messages found: {len(messages)}")
        
        new_emails = 0
        latest_history_id = token.last_history_id or '1'
        for msg in messages:
            if self.db.query(Email).filter(Email.message_id == msg['id']).first():
                continue
            
            new_emails += self._process_google_message(service, token, msg['id'])
            
            # Update latest history id
            try:
                msg_detail = service.users().messages().get(userId='me', id=msg['id']).execute()
                if 'historyId' in msg_detail and msg_detail['historyId'] > latest_history_id:
                    latest_history_id = msg_detail['historyId']
            except:
                pass  # Ignore if can't get history
        
        token.last_history_id = latest_history_id
        self.db.commit()
        
        return new_emails

    def _process_google_message(self, service, token: UserEmailToken, message_id: str) -> int:
        """Process and store a single Google message with full body and attachments"""
        try:
            msg_detail = service.users().messages().get(userId='me', id=message_id, format='full').execute()
            
            headers = {h['name'].lower(): h['value'] for h in msg_detail['payload']['headers']}
            labels = msg_detail.get('labelIds', [])
            
            # Determine folder
            folder = 'ARCHIVED'
            if 'INBOX' in labels:
                folder = 'INBOX'
            elif 'SENT' in labels:
                folder = 'SENT'
            elif 'DRAFT' in labels:
                folder = 'DRAFTS'
            elif 'SPAM' in labels:
                folder = 'SPAM'
            elif 'TRASH' in labels:
                folder = 'TRASH'
            elif any(label.startswith('CATEGORY_') for label in labels):
                folder = 'CATEGORIES'
            
            is_flagged = 'STARRED' in labels
            is_important = 'IMPORTANT' in labels
            
            # Parse full body and attachments
            body_html, body_text, attachments_data, size_bytes = self._parse_google_payload(msg_detail['payload'])
            
            email = Email(
                message_id=message_id,
                thread_id=msg_detail['threadId'],
                subject=headers.get('subject', ''),
                from_address=headers.get('from', ''),
                from_name=self._extract_name_from_header(headers.get('from', '')),
                to_addresses=self._parse_addresses(headers.get('to', '')),
                cc_addresses=self._parse_addresses(headers.get('cc', '')),
                bcc_addresses=self._parse_addresses(headers.get('bcc', '')),
                reply_to=headers.get('reply-to', ''),
                sent_at=datetime.fromtimestamp(int(msg_detail['internalDate'])/1000),
                received_at=datetime.fromtimestamp(int(msg_detail['internalDate'])/1000),
                body_text=body_text,
                body_html=body_html,
                status="UNREAD" if 'UNREAD' in labels else "READ",
                is_flagged=is_flagged,
                is_important=is_important,
                labels=labels,
                folder=folder,
                size_bytes=size_bytes,
                has_attachments=bool(attachments_data),
                account_id=token.id,
                organization_id=token.organization_id
            )
            
            self.db.add(email)
            self.db.flush()  # Get ID for attachments
            
            # Add attachments
            for att_data in attachments_data:
                att = EmailAttachment(
                    email_id=email.id,
                    filename=att_data['filename'],
                    content_type=att_data['content_type'],
                    size_bytes=att_data['size'],
                    content_id=att_data.get('content_id'),
                    file_data=encrypt_file_data(att_data['data']),  # Encrypt if needed
                    is_inline=att_data.get('is_inline', False),
                    is_downloaded=True  # Since we fetched it
                )
                self.db.add(att)
            
            self.db.commit()
            return 1
            
        except IntegrityError:
            self.db.rollback()
            logger.warning(f"Duplicate email {message_id}, skipping")
            return 0
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error processing Google message {message_id}: {str(e)}")
            return 0

    def _parse_google_payload(self, payload: Dict) -> tuple[str, str, list, int]:
        """Parse Gmail payload for full HTML/text, attachments, and size"""
        body_html = None
        body_text = None
        attachments = []
        size = 0
        
        if payload['mimeType'] == 'text/html':
            body_html = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
        elif payload['mimeType'] == 'text/plain':
            body_text = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
        elif payload['mimeType'] == 'multipart/alternative':
            # Find HTML or text part
            for part in payload['parts']:
                if part['mimeType'] == 'text/html':
                    body_html = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                elif part['mimeType'] == 'text/plain':
                    body_text = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
        elif payload['mimeType'] == 'multipart/mixed':
            # Mixed: body + attachments
            for part in payload['parts']:
                if part['mimeType'].startswith('text/'):
                    if part['mimeType'] == 'text/html':
                        body_html = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                    elif part['mimeType'] == 'text/plain':
                        body_text = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                elif not part['mimeType'].startswith('multipart/'):
                    # Attachment
                    att_data = base64.urlsafe_b64decode(part['body']['data']).decode('latin-1')  # Binary as string
                    attachments.append({
                        'filename': part['filename'],
                        'content_type': part['mimeType'],
                        'size': len(att_data.encode()),
                        'data': att_data.encode(),
                        'content_id': part.get('headers', {}).get('content-id', ''),
                        'is_inline': 'inline' in part.get('disposition', '').lower()
                    })
                    size += len(att_data.encode())
                else:
                    # Nested multipart
                    nested_html, nested_text, nested_att, nested_size = self._parse_google_payload(part)
                    if nested_html:
                        body_html = nested_html
                    if nested_text:
                        body_text = nested_text
                    attachments.extend(nested_att)
                    size += nested_size
        elif payload['filename'] and payload['body']['size'] > 0:
            # Attachment without body
            att_data = base64.urlsafe_b64decode(payload['body']['data']).decode('latin-1')
            attachments.append({
                'filename': payload['filename'],
                'content_type': payload['mimeType'],
                'size': payload['body']['size'],
                'data': att_data.encode(),
                'content_id': '',
                'is_inline': False
            })
            size = payload['body']['size']
        
        return body_html or '', body_text or '', attachments, size

    def _extract_name_from_header(self, header: str) -> str:
        """Extract display name from 'From' header"""
        import re
        match = re.match(r'([^<]+)<(.+)>', header.strip())
        return match.group(1).strip() if match else header

    def _parse_addresses(self, header: str) -> list:
        """Parse comma-separated addresses"""
        if not header:
            return []
        return [addr.strip().strip('<>') for addr in header.split(',')]

    def _setup_google_watch(self, token: UserEmailToken):
        """Setup Gmail watch for push notifications"""
        try:
            creds = Credentials(
                token=token.access_token,
                refresh_token=token.refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=settings.GOOGLE_CLIENT_ID,
                client_secret=settings.GOOGLE_CLIENT_SECRET
            )
            
            if creds.expired and creds.refresh_token:
                creds.refresh(Request())
                token.access_token = creds.token
                token.refresh_token = creds.refresh_token
                token.expires_at = creds.expiry
                self.db.commit()
            
            service = build('gmail', 'v1', credentials=creds)
            
            watch_request = {
                "labelIds": ["INBOX"],
                "labelFilterAction": "include",
                "topicName": settings.PUBSUB_TOPIC
            }
            
            response = service.users().watch(userId='me', body=watch_request).execute()
            logger.info(f"Watch setup for {token.email_address}: expires {response.get('expiration')}")
            
        except Exception as e:
            logger.error(f"Failed to setup watch for {token.email_address}: {str(e)}")

    async def _sync_microsoft_emails(self, token: UserEmailToken, force_sync: bool) -> int:
        """Sync emails from Microsoft with delta for incremental"""
        app = ConfidentialClientApplication(
            client_id=settings.MICROSOFT_CLIENT_ID,
            authority=f"https://login.microsoftonline.com/common",
            client_credential=settings.MICROSOFT_CLIENT_SECRET
        )
        
        result = app.acquire_token_by_refresh_token(
            token.refresh_token,
            scopes=["https://graph.microsoft.com/Mail.Read"]
        )
        
        if "access_token" not in result:
            raise Exception("Failed to acquire token")
        
        access_token = result["access_token"]
        token.access_token = access_token
        if "refresh_token" in result:
            token.refresh_token = result["refresh_token"]
        if "expires_in" in result:
            token.expires_at = datetime.utcnow() + timedelta(seconds=result["expires_in"])
        self.db.commit()
        
        credential = ClientSecretCredential(
            tenant_id="common",
            client_id=settings.MICROSOFT_CLIENT_ID,
            client_secret=settings.MICROSOFT_CLIENT_SECRET
        )
        
        graph_client = GraphServiceClient(credentials=credential)
        
        folders = ['inbox', 'sentitems', 'drafts', 'junkemail', 'deleteditems']
        new_emails = 0
        
        # Use delta for incremental sync if possible
        delta_token = token.last_delta_token if not force_sync else None
        odata_filter = None
        if not force_sync and token.last_sync_at:
            odata_filter = f"receivedDateTime ge {token.last_sync_at.isoformat()}Z"
        
        for folder_id in folders:
            try:
                request_builder = graph_client.me.mail_folders.by_mail_folder_id(folder_id).messages
                
                if delta_token:
                    # Delta sync for incremental
                    delta_request = request_builder.delta.get()
                    delta_request.query_parameters.delta_token = delta_token
                    messages = []
                    async for msg in delta_request:
                        if hasattr(msg, 'id') and msg.id:  # Only added/updated
                            messages.append(msg)
                else:
                    # Regular sync with filter
                    messages = []
                    page_iterator = request_builder.get_all_request_builder(
                        query_params=MessagesRequestBuilder.MessagesRequestBuilderGetQueryParameters(
                            top=100,
                            filter=odata_filter,
                            orderby=["receivedDateTime DESC"],
                            select="id,subject,from,toRecipients,ccRecipients,bccRecipients,sentDateTime,receivedDateTime,bodyPreview,body,hasAttachments,flag,importance,attachments"
                        )
                    )
                    
                    async for msg in page_iterator:
                        messages.append(msg)
                
                logger.info(f"Found {len(messages)} messages in folder {folder_id}")
                
                for msg in messages:
                    if self.db.query(Email).filter(Email.message_id == msg.id).first():
                        continue
                    
                    # Fetch full message if needed for attachments/body
                    full_msg = await request_builder.by_message_id(msg.id).get()
                    
                    # Process attachments
                    attachments_data = []
                    size_bytes = 0
                    if full_msg.has_attachments:
                        att_request = graph_client.me.messages.by_message_id(full_msg.id).attachments
                        att_iterator = att_request.get_all_request_builder()
                        async for att in att_iterator:
                            if att.o_data_type == '#microsoft.graph.fileAttachment':
                                file_att = cast(FileAttachment, att)
                                att_data = {
                                    'filename': file_att.name,
                                    'content_type': file_att.content_type,
                                    'size': len(file_att.content_bytes) if file_att.content_bytes else 0,
                                    'data': file_att.content_bytes,
                                    'content_id': '',
                                    'is_inline': False
                                }
                                attachments_data.append(att_data)
                                size_bytes += att_data['size']
                    
                    email = Email(
                        message_id=full_msg.id,
                        subject=full_msg.subject or '',
                        from_address=full_msg.from_.email_address.address if full_msg.from_ else '',
                        from_name=full_msg.from_.email_address.name if full_msg.from_ else '',
                        to_addresses=[r.email_address.address for r in full_msg.to_recipients or []],
                        cc_addresses=[r.email_address.address for r in full_msg.cc_recipient or []],
                        bcc_addresses=[r.email_address.address for r in full_msg.bcc_recipient or []],
                        reply_to=full_msg.reply_to.email_address.address if full_msg.reply_to else None,
                        sent_at=full_msg.sent_date_time,
                        received_at=full_msg.received_date_time,
                        body_text=full_msg.body_preview if full_msg.body.content_type != 'html' else None,
                        body_html=full_msg.body.content if full_msg.body.content_type == 'html' else None,
                        status="UNREAD" if not full_msg.is_read else "READ",
                        is_flagged=full_msg.flag.flag_status == 'flagged' if full_msg.flag else False,
                        is_important=full_msg.importance == 'high',
                        labels=full_msg.categories or [],
                        folder=folder_id.upper(),
                        size_bytes=size_bytes,
                        has_attachments=bool(attachments_data),
                        account_id=token.id,
                        organization_id=token.organization_id
                    )
                    
                    self.db.add(email)
                    self.db.flush()
                    
                    # Add attachments
                    for att_data in attachments_data:
                        att = EmailAttachment(
                            email_id=email.id,
                            filename=att_data['filename'],
                            content_type=att_data['content_type'],
                            size_bytes=att_data['size'],
                            content_id=att_data.get('content_id'),
                            file_data=encrypt_file_data(att_data['data']),
                            is_inline=att_data.get('is_inline', False),
                            is_downloaded=True
                        )
                        self.db.add(att)
                    
                    new_emails += 1
                
                # Update delta token if used
                if delta_token:
                    token.last_delta_token = delta_request.context.delta_link or delta_token
                    self.db.commit()
                
            except Exception as e:
                logger.error(f"Error syncing Microsoft folder {folder_id}: {str(e)}")
                continue
        
        self.db.commit()
        logger.info(f"Imported {new_emails} new emails for Microsoft")
        return new_emails