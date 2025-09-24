"""
Email API Service for fetching and sending emails using OAuth providers
"""

import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

from sqlalchemy.orm import Session
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

from app.core.config import settings
from app.models.oauth_models import UserEmailToken, OAuthProvider
from app.models.mail_management import Email, EmailAttachment, SentEmail
from app.schemas.mail_schemas import MailSyncResponse, MailComposeRequest, SentEmailResponse

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
                # Assuming snoozed is a custom status or label; adjust as needed
                query = query.filter(Email.status == 'SNOOZED')
            elif folder_upper == 'CATEGORIES':
                # Assuming categories use labels; filter if has labels
                query = query.filter(Email.labels != None)
            # Add more custom filters as needed
        
        total = query.count()
        emails = query.offset((page - 1) * per_page).limit(per_page).all()
        
        return {
            "emails": [email.__dict__ for email in emails],
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page
        }

    async def get_email_detail(self, user, email_id: int) -> Dict:
        """Get email from DB"""
        email = self.db.query(Email).filter(
            Email.id == email_id,
            Email.organization_id == user.organization_id
        ).first()
        
        if not email:
            raise HTTPException(404, "Email not found")
        
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
        emails = query.offset((page - 1) * per_page).limit(per_page).all()
        
        return {
            "emails": [email.__dict__ for email in emails],
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page
        }

    async def send_email(self, user, token_id: int, compose_request: MailComposeRequest, attachments: List = None) -> SentEmailResponse:
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

    def _send_google_email(self, token: UserEmailToken, compose_request: MailComposeRequest) -> bool:
        """Send email via Gmail API"""
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
                compose_request.bcc_addresses
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

    async def _send_microsoft_email(self, token: UserEmailToken, compose_request: MailComposeRequest) -> bool:
        """Send email via Microsoft Graph"""
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
                to_recipient = [Recipient(email_address=EmailAddress(address=addr)) for addr in compose_request.to_addresses],
                cc_recipient = [Recipient(email_address=EmailAddress(address=addr)) for addr in compose_request.cc_addresses or []],
                bcc_recipient = [Recipient(email_address=EmailAddress(address=addr)) for addr in compose_request.bcc_addresses or []]
            )
            
            request_body = SendMailPostRequestBody(message=message)
            
            await graph_client.me.send_mail.post(request_body)
            
            return True
            
        except Exception as e:
            logger.error(f"Microsoft Graph send error: {str(e)}")
            return False

    def _create_mime_message(self, sender, to, subject, body_text, body_html=None, cc=None, bcc=None):
        """Create MIME message"""
        message = MIMEMultipart('alternative')
        message['From'] = sender
        message['To'] = ', '.join(to)
        if cc:
            message['Cc'] = ', '.join(cc)
        if bcc:
            message['Bcc'] = ', '.join(bcc)
        message['Subject'] = subject
        
        text_part = MIMEText(body_text, 'plain')
        message.attach(text_part)
        
        if body_html:
            html_part = MIMEText(body_html, 'html')
            message.attach(html_part)
        
        return message

    async def sync_emails(self, user, token_id: Optional[int], force_sync: bool) -> MailSyncResponse:
        """Sync emails from providers"""
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
                        # Process the added message
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
            # Full sync
            new_emails = self._full_sync_google_emails(service, token, force_sync)
        
        logger.info(f"Imported {new_emails} new emails")
        return new_emails

    def _full_sync_google_emails(self, service, token: UserEmailToken, force_sync: bool) -> int:
        """Perform full sync of Gmail emails"""
        q = None
        if not force_sync and token.last_sync_at:
            last_sync_date = token.last_sync_at - timedelta(days=1)
            q = f"after:{int(last_sync_date.timestamp())}"
        
        logger.info(f"Full syncing Gmail with query: {q}")
        
        # Fetch all messages
        results = service.users().messages().list(userId='me', q=q, maxResults=500, includeSpamTrash=True).execute()
        messages = results.get('messages', [])
        logger.info(f"Found {len(messages)} messages in first page")
        while 'nextPageToken' in results:
            logger.info("Fetching next page")
            results = service.users().messages().list(userId='me', q=q, maxResults=500, pageToken=results['nextPageToken'], includeSpamTrash=True).execute()
            messages.extend(results.get('messages', []))
        
        logger.info(f"Total messages found: {len(messages)}")
        
        new_emails = 0
        latest_history_id = None
        for msg in messages:
            if self.db.query(Email).filter(Email.message_id == msg['id']).first():
                continue
            
            new_emails += self._process_google_message(service, token, msg['id'])
            
            # Update latest history id if available
            msg_detail = service.users().messages().get(userId='me', id=msg['id']).execute()
            if 'historyId' in msg_detail and (not latest_history_id or msg_detail['historyId'] > latest_history_id):
                latest_history_id = msg_detail['historyId']
        
        if latest_history_id:
            token.last_history_id = latest_history_id
            self.db.commit()
        
        return new_emails

    def _process_google_message(self, service, token: UserEmailToken, message_id: str) -> int:
        """Process and store a single Google message"""
        try:
            msg_detail = service.users().messages().get(userId='me', id=message_id, format='full').execute()
            
            headers = {h['name'].lower(): h['value'] for h in msg_detail['payload']['headers']}
            labels = msg_detail.get('labelIds', [])
            
            folder = 'ARCHIVED'  # Default
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
            
            email = Email(
                message_id=message_id,
                thread_id=msg_detail['threadId'],
                subject=headers.get('subject', ''),
                from_address=headers.get('from', ''),
                to_addresses=[headers.get('to', '')],
                sent_at=datetime.fromtimestamp(int(msg_detail['internalDate'])/1000),
                received_at=datetime.fromtimestamp(int(msg_detail['internalDate'])/1000),
                body_text=msg_detail['snippet'],
                status="UNREAD" if 'UNREAD' in labels else "READ",
                is_flagged=is_flagged,
                is_important=is_important,
                labels=labels,
                folder=folder,
                account_id=token.id,
                organization_id=token.organization_id
            )
            
            self.db.add(email)
            self.db.commit()
            return 1
            
        except Exception as e:
            logger.error(f"Error processing Google message {message_id}: {str(e)}")
            return 0

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
        """Sync emails from Microsoft"""
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
        
        # Determine filter for recent emails
        odata_filter = None
        if force_sync:
            # Force sync last 90 days
            initial_date = (datetime.utcnow() - timedelta(days=90)).isoformat() + 'Z'
            odata_filter = f"receivedDateTime ge {initial_date}"
        elif token.last_sync_at:
            odata_filter = f"receivedDateTime ge {token.last_sync_at.isoformat()}Z"
        else:
            # Initial sync: last 90 days
            initial_date = (datetime.utcnow() - timedelta(days=90)).isoformat() + 'Z'
            odata_filter = f"receivedDateTime ge {initial_date}"
        
        logger.info(f"Syncing Microsoft with filter: {odata_filter}")
        for folder_id in folders:
            request_builder = graph_client.me.mail_folders.by_mail_folder_id(folder_id).messages
            messages = []
            page_iterator = request_builder.get_all_request_builder(
                query_params=MessagesRequestBuilder.MessagesRequestBuilderGetQueryParameters(
                    top=100,
                    filter=odata_filter,
                    orderby=["receivedDateTime DESC"]
                )
            )
            
            async for msg in page_iterator:
                messages.append(msg)
            
            logger.info(f"Found {len(messages)} messages in folder {folder_id}")
            for msg in messages:
                # Check if exists
                if self.db.query(Email).filter(Email.message_id == msg.id).first():
                    continue
                
                email = Email(
                    message_id=msg.id,
                    subject=msg.subject,
                    from_address=msg.from_.email_address.address,
                    to_addresses=[r.email_address.address for r in msg.to_recipient],
                    sent_at=msg.sent_date_time,
                    received_at=msg.received_date_time,
                    body_text=msg.body_preview,
                    body_html=msg.body.content if msg.body.content_type == 'html' else None,
                    status="UNREAD" if not msg.is_read else "READ",
                    is_flagged=msg.flag.flag_status == 'flagged',
                    is_important=msg.importance == 'high',
                    labels=[],  # Microsoft doesn't have labels like Google; use categories if needed
                    folder=folder_id.upper(),
                    account_id=token.id,
                    organization_id=token.organization_id
                )
                
                self.db.add(email)
                new_emails += 1
        
        self.db.commit()
        logger.info(f"Imported {new_emails} new emails")
        return new_emails