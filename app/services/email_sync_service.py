# app/services/email_sync_service.py

"""
Email Sync Service for IMAP/SMTP operations with OAuth2 support
Handles email fetching, parsing, and synchronization with database
"""

import imaplib
import smtplib
import email
import email.message
import logging
import base64
import hashlib
import os
import re
import bleach
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import decode_header
from email.utils import parsedate_tz, mktime_tz, parseaddr
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.email import (
    MailAccount, Email, EmailThread, EmailAttachment, EmailSyncStatus, EmailStatus, EmailPriority, EmailSyncLog
)
from app.utils.text_processing import extract_plain_text, sanitize_html

logger = logging.getLogger(__name__)


class EmailSyncService:
    """
    Service for syncing emails via IMAP and sending via SMTP with OAuth2 support
    """
    
    def __init__(self, db: Optional[Session] = None):
        self.db = db
        
        # HTML sanitization settings
        self.allowed_tags = [
            'p', 'br', 'div', 'span', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            'strong', 'b', 'em', 'i', 'u', 'ol', 'ul', 'li', 'blockquote',
            'a', 'img', 'table', 'thead', 'tbody', 'tr', 'td', 'th'
        ]
        self.allowed_attributes = {
            'a': ['href', 'title'],
            'img': ['src', 'alt', 'width', 'height'],
            'table': ['border', 'cellpadding', 'cellspacing'],
            '*': ['style', 'class']
        }
    
    def get_imap_connection(self, account: MailAccount) -> Optional[imaplib.IMAP4_SSL]:
        """
        Establish IMAP connection with OAuth2 or password authentication
        """
        try:
            # Create IMAP connection
            if account.incoming_ssl:
                imap = imaplib.IMAP4_SSL(account.incoming_server, account.incoming_port or 993)
            else:
                imap = imaplib.IMAP4(account.incoming_server, account.incoming_port or 143)
                if account.incoming_ssl:
                    imap.starttls()
            
            # Authenticate
            if account.oauth_token_id and account.incoming_auth_method == 'oauth2':
                # OAuth2 authentication
                credentials = self.oauth_service.get_email_credentials(account.oauth_token_id)
                if not credentials:
                    logger.error(f"Failed to get OAuth2 credentials for account {account.id}")
                    return None
                
                auth_string = self._build_oauth2_auth_string(
                    credentials['email'],
                    credentials['access_token']
                )
                imap.authenticate('XOAUTH2', lambda x: auth_string)
                
            elif account.username and account.password_encrypted:
                # Password authentication
                from app.utils.encryption import decrypt_field, EncryptionKeys
                password = decrypt_field(account.password_encrypted, EncryptionKeys.PII_KEY)
                imap.login(account.username, password)
            else:
                logger.error(f"No valid authentication method for account {account.id}")
                return None
            
            return imap
            
        except Exception as e:
            logger.error(f"IMAP connection failed for account {account.id}: {str(e)}")
            return None
    
    def _build_oauth2_auth_string(self, email: str, access_token: str) -> str:
        """
        Build OAuth2 authentication string for IMAP/SMTP
        """
        auth_string = f'user={email}\x01auth=Bearer {access_token}\x01\x01'
        return base64.b64encode(auth_string.encode()).decode()
    
    def sync_account(self, account_id: int, full_sync: bool = False) -> bool:
        """
        Sync emails for a specific account
        """
        if self.db:
            return self._perform_sync(self.db, account_id, full_sync)
        else:
            db = SessionLocal()
            try:
                return self._perform_sync(db, account_id, full_sync)
            finally:
                db.close()
    
    def _perform_sync(self, db: Session, account_id: int, full_sync: bool = False) -> bool:
        account = db.query(MailAccount).filter(MailAccount.id == account_id).first()
        if not account:
            logger.error(f"Account {account_id} not found")
            return False
        
        if not account.sync_enabled or account.sync_status != EmailSyncStatus.ACTIVE:
            logger.info(f"Sync disabled for account {account_id}")
            return True
        
        # Create sync log
        sync_log = EmailSyncLog(
            account_id=account_id,
            sync_type='full' if full_sync else 'incremental',
            status='running',
            started_at=datetime.utcnow()
        )
        db.add(sync_log)
        db.commit()
        
        try:
            # Connect to IMAP
            imap = self.get_imap_connection(account)
            if not imap:
                raise Exception("Failed to connect to IMAP server")
            
            # Sync folders
            folders_to_sync = account.sync_folders or ['INBOX']
            total_new = 0
            total_updated = 0
            
            for folder in folders_to_sync:
                try:
                    new_count, updated_count = self._sync_folder(imap, account, folder, db, full_sync)
                    total_new += new_count
                    total_updated += updated_count
                except Exception as e:
                    logger.error(f"Error syncing folder {folder} for account {account_id}: {str(e)}")
            
            # Update sync status
            account.last_sync_at = datetime.utcnow()
            account.last_sync_error = None
            account.total_messages_synced += total_new
            
            # Mark full sync as completed
            if full_sync:
                account.full_sync_completed = True
            
            # Update sync log
            sync_log.status = 'success'
            sync_log.completed_at = datetime.utcnow()
            sync_log.messages_new = total_new
            sync_log.messages_updated = total_updated
            sync_log.duration_seconds = (sync_log.completed_at - sync_log.started_at).total_seconds()
            
            db.commit()
            
            # Close IMAP connection
            imap.close()
            imap.logout()
            
            logger.info(f"Successfully synced account {account_id}: {total_new} new, {total_updated} updated")
            return True
            
        except Exception as e:
            error_msg = f"Sync failed for account {account_id}: {str(e)}"
            logger.error(error_msg)
            
            # Update account and sync log
            account.last_sync_error = error_msg
            sync_log.status = 'error'
            sync_log.error_message = error_msg
            sync_log.completed_at = datetime.utcnow()
            
            db.commit()
            return False
    
    def _sync_folder(self, imap: imaplib.IMAP4_SSL, account: MailAccount, folder: str, db: Session, full_sync: bool = False) -> Tuple[int, int]:
        """
        Sync a specific folder
        Returns tuple of (new_messages_count, updated_messages_count)
        """
        try:
            # Select folder
            status, messages = imap.select(folder)
            if status != 'OK':
                logger.error(f"Failed to select folder {folder}")
                return 0, 0
            
            total_messages = int(messages[0])
            logger.info(f"Syncing folder {folder} with {total_messages} messages")
            
            # Determine which messages to sync
            if full_sync or not account.last_sync_uid:
                # Full sync - get all messages (or last N days for large mailboxes)
                days_back = getattr(settings, 'EMAIL_FULL_SYNC_DAYS', 30)
                since_date = (datetime.now() - timedelta(days=days_back)).strftime('%d-%b-%Y')
                status, message_ids = imap.search(None, f'SINCE {since_date}')
            else:
                # Incremental sync - get messages since last sync
                status, message_ids = imap.search(None, f'UID {account.last_sync_uid}:*')
            
            if status != 'OK':
                logger.error(f"Failed to search messages in folder {folder}")
                return 0, 0
            
            if not message_ids[0]:
                logger.info(f"No new messages in folder {folder}")
                return 0, 0
            
            message_ids = message_ids[0].split()
            new_count = 0
            updated_count = 0
            
            # Process messages in batches
            batch_size = getattr(settings, 'EMAIL_SYNC_BATCH_SIZE', 50)
            for i in range(0, len(message_ids), batch_size):
                batch = message_ids[i:i + batch_size]
                
                for msg_id in batch:
                    try:
                        msg_id = msg_id.decode() if isinstance(msg_id, bytes) else msg_id
                        
                        # Fetch message
                        status, msg_data = imap.fetch(msg_id, '(RFC822 UID)')
                        if status != 'OK':
                            continue
                        
                        # Parse message
                        raw_email = msg_data[0][1]
                        msg = email.message_from_bytes(raw_email)
                        
                        # Get UID
                        uid_match = re.search(r'UID (\d+)', msg_data[0][0].decode())
                        uid = uid_match.group(1) if uid_match else msg_id
                        
                        # Check if message already exists
                        message_id = msg.get('Message-ID', '').strip('<>')
                        existing = db.query(Email).filter(
                            and_(
                                Email.message_id == message_id,
                                Email.account_id == account.id
                            )
                        ).first()
                        
                        if existing:
                            # Update existing message if needed
                            if self._update_email_if_changed(existing, msg, folder, db):
                                updated_count += 1
                        else:
                            # Create new message
                            if self._create_email_from_message(msg, uid, account, folder, db):
                                new_count += 1
                        
                        # Update last sync UID
                        account.last_sync_uid = uid
                        
                    except Exception as e:
                        logger.error(f"Error processing message {msg_id}: {str(e)}")
                        continue
                
                # Commit batch
                db.commit()
            
            return new_count, updated_count
            
        except Exception as e:
            logger.error(f"Error syncing folder {folder}: {str(e)}")
            return 0, 0
    
    def _create_email_from_message(self, msg: email.message.Message, uid: str, account: MailAccount, folder: str, db: Session) -> bool:
        """
        Create Email record from email message
        """
        try:
            # Extract basic info
            message_id = msg.get('Message-ID', '').strip('<>')
            subject = self._decode_header(msg.get('Subject', ''))
            from_header = msg.get('From', '')
            from_name, from_address = parseaddr(from_header)
            
            # Parse recipients
            to_addresses = self._parse_addresses(msg.get('To', ''))
            cc_addresses = self._parse_addresses(msg.get('Cc', ''))
            bcc_addresses = self._parse_addresses(msg.get('Bcc', ''))
            
            # Parse dates
            sent_date = self._parse_date(msg.get('Date'))
            received_date = datetime.utcnow()  # Use current time as received
            
            # Extract body content
            body_text, body_html = self._extract_body_content(msg)
            
            # Sanitize HTML
            body_html_raw = body_html
            if body_html:
                body_html = self._sanitize_html(body_html)
            
            # Determine priority
            priority = self._determine_priority(msg)
            
            # Create email record
            email_record = Email(
                message_id=message_id,
                uid=uid,
                subject=subject,
                from_address=from_address,
                from_name=self._decode_header(from_name) if from_name else None,
                reply_to=msg.get('Reply-To'),
                to_addresses=to_addresses,
                cc_addresses=cc_addresses if cc_addresses else None,
                bcc_addresses=bcc_addresses if bcc_addresses else None,
                body_text=body_text,
                body_html=body_html,
                body_html_raw=body_html_raw,
                status=EmailStatus.UNREAD,
                priority=priority,
                has_attachments=False,  # Will be updated when processing attachments
                sent_at=sent_date,
                received_at=received_date,
                organization_id=account.organization_id,
                account_id=account.id,
                folder=folder,
                size_bytes=len(str(msg)),
                headers_raw=dict(msg.items()),
                is_processed=False
            )
            
            db.add(email_record)
            db.flush()  # Get ID
            
            # Process attachments
            has_attachments = self._process_attachments(msg, email_record, db)
            email_record.has_attachments = has_attachments
            
            # Auto-link to customers/vendors
            self._auto_link_email(email_record, db)
            
            # Find or create thread
            thread = self._find_or_create_thread(email_record, account, db)
            if thread:
                email_record.thread_id = thread.id
            
            email_record.is_processed = True
            return True
            
        except Exception as e:
            logger.error(f"Error creating email record: {str(e)}")
            return False
    
    def _decode_header(self, header: str) -> str:
        """
        Decode email header with proper encoding handling
        """
        if not header:
            return ''
        
        try:
            decoded_parts = decode_header(header)
            decoded_text = ''
            
            for text, encoding in decoded_parts:
                if isinstance(text, bytes):
                    decoded_text += text.decode(encoding or 'utf-8', errors='ignore')
                else:
                    decoded_text += text
            
            return decoded_text.strip()
        except Exception as e:
            logger.error(f"Error decoding header: {str(e)}")
            return header
    
    def _parse_addresses(self, address_header: str) -> List[Dict[str, str]]:
        """
        Parse email addresses from header
        """
        if not address_header:
            return []
        
        try:
            addresses = []
            for addr in address_header.split(','):
                name, email_addr = parseaddr(addr.strip())
                if email_addr:
                    addresses.append({
                        'name': self._decode_header(name) if name else None,
                        'email': email_addr
                    })
            return addresses
        except Exception as e:
            logger.error(f"Error parsing addresses: {str(e)}")
            return []
    
    def _parse_date(self, date_header: str) -> datetime:
        """
        Parse email date header
        """
        if not date_header:
            return datetime.utcnow()
        
        try:
            date_tuple = parsedate_tz(date_header)
            if date_tuple:
                timestamp = mktime_tz(date_tuple)
                return datetime.fromtimestamp(timestamp)
        except Exception as e:
            logger.error(f"Error parsing date: {str(e)}")
        
        return datetime.utcnow()
    
    def _extract_body_content(self, msg: email.message.Message) -> Tuple[Optional[str], Optional[str]]:
        """
        Extract text and HTML content from email message
        """
        text_content = None
        html_content = None
        
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get('Content-Disposition', ''))
                
                if 'attachment' in content_disposition:
                    continue
                
                if content_type == 'text/plain':
                    payload = part.get_payload(decode=True)
                    if payload:
                        text_content = payload.decode('utf-8', errors='ignore')
                elif content_type == 'text/html':
                    payload = part.get_payload(decode=True)
                    if payload:
                        html_content = payload.decode('utf-8', errors='ignore')
        else:
            content_type = msg.get_content_type()
            payload = msg.get_payload(decode=True)
            
            if payload:
                content = payload.decode('utf-8', errors='ignore')
                if content_type == 'text/plain':
                    text_content = content
                elif content_type == 'text/html':
                    html_content = content
        
        # If we only have HTML, extract text from it
        if html_content and not text_content:
            text_content = extract_plain_text(html_content)
        
        return text_content, html_content
    
    def _sanitize_html(self, html: str) -> str:
        """
        Sanitize HTML content for safe storage and display
        """
        try:
            return bleach.clean(
                html,
                tags=self.allowed_tags,
                attributes=self.allowed_attributes,
                strip=True
            )
        except Exception as e:
            logger.error(f"Error sanitizing HTML: {str(e)}")
            return bleach.clean(html, tags=[], attributes={}, strip=True)
    
    def _determine_priority(self, msg: email.message.Message) -> EmailPriority:
        """
        Determine email priority from headers
        """
        priority_header = msg.get('X-Priority', '').lower()
        importance_header = msg.get('Importance', '').lower()
        
        if priority_header in ['1', '2'] or importance_header == 'high':
            return EmailPriority.HIGH
        elif priority_header == '5' or importance_header == 'low':
            return EmailPriority.LOW
        else:
            return EmailPriority.NORMAL
    
    def _process_attachments(self, msg: email.message.Message, email_record: Email, db: Session) -> bool:
        """
        Process email attachments
        Returns True if attachments were found
        """
        has_attachments = False
        
        for part in msg.walk():
            content_disposition = str(part.get('Content-Disposition', ''))
            
            if 'attachment' in content_disposition or part.get_filename():
                try:
                    filename = part.get_filename()
                    if filename:
                        filename = self._decode_header(filename)
                        
                        # Create attachment record
                        attachment = EmailAttachment(
                            email_id=email_record.id,
                            filename=self._sanitize_filename(filename),
                            original_filename=filename,
                            content_type=part.get_content_type(),
                            size_bytes=len(part.get_payload(decode=True) or b''),
                            content_id=part.get('Content-ID'),
                            content_disposition=content_disposition,
                            is_inline='inline' in content_disposition,
                            is_downloaded=False
                        )
                        
                        # Calculate file hash for deduplication
                        payload = part.get_payload(decode=True)
                        if payload:
                            attachment.file_hash = hashlib.sha256(payload).hexdigest()
                        
                        db.add(attachment)
                        has_attachments = True
                        
                except Exception as e:
                    logger.error(f"Error processing attachment: {str(e)}")
        
        return has_attachments
    
    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename for safe storage
        """
        # Remove path separators and dangerous characters
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        filename = filename.strip('. ')
        
        # Limit length
        if len(filename) > 255:
            name, ext = os.path.splitext(filename)
            filename = name[:250] + ext
        
        return filename or 'attachment'
    
    def _auto_link_email(self, email_record: Email, db: Session):
        """
        Automatically link email to customers/vendors based on email addresses
        """
        try:
            from app.models.customer_models import Customer, Vendor
            
            # Extract all email addresses from the message
            all_emails = set()
            
            # From address
            if email_record.from_address:
                all_emails.add(email_record.from_address.lower())
            
            # To addresses
            for addr in email_record.to_addresses or []:
                if addr.get('email'):
                    all_emails.add(addr['email'].lower())
            
            # CC addresses
            for addr in email_record.cc_addresses or []:
                if addr.get('email'):
                    all_emails.add(addr['email'].lower())
            
            # Check for customer matches
            if not email_record.customer_id:
                customer = db.query(Customer).filter(
                    Customer.organization_id == email_record.organization_id,
                    Customer.email.in_(list(all_emails))
                ).first()
                
                if customer:
                    email_record.customer_id = customer.id
            
            # Check for vendor matches
            if not email_record.vendor_id:
                vendor = db.query(Vendor).filter(
                    Vendor.organization_id == email_record.organization_id,
                    Vendor.email.in_(list(all_emails))
                ).first()
                
                if vendor:
                    email_record.vendor_id = vendor.id
            
        except Exception as e:
            logger.error(f"Error auto-linking email: {str(e)}")
    
    def _find_or_create_thread(self, email_record: Email, account: MailAccount, db: Session) -> Optional[EmailThread]:
        """
        Find existing thread or create new one for the email
        """
        try:
            # Extract thread information from headers
            references = email_record.headers_raw.get('References', '')
            in_reply_to = email_record.headers_raw.get('In-Reply-To', '')
            
            # Clean subject for thread matching
            clean_subject = re.sub(r'^(Re:|Fwd?:|RE:|FWD?:)\s*', '', email_record.subject, flags=re.IGNORECASE).strip()
            
            # Look for existing thread
            thread = None
            
            # First, try to find by references or in-reply-to
            if references or in_reply_to:
                ref_ids = []
                if references:
                    ref_ids.extend(re.findall(r'<([^>]+)>', references))
                if in_reply_to:
                    ref_ids.extend(re.findall(r'<([^>]+)>', in_reply_to))
                
                if ref_ids:
                    # Find emails with matching message IDs
                    related_email = db.query(Email).filter(
                        and_(
                            Email.message_id.in_(ref_ids),
                            Email.account_id == account.id
                        )
                    ).first()
                    
                    if related_email and related_email.thread_id:
                        thread = db.query(EmailThread).filter(
                            EmailThread.id == related_email.thread_id
                        ).first()
            
            # If no thread found, try subject matching
            if not thread and clean_subject:
                thread = db.query(EmailThread).filter(
                    and_(
                        EmailThread.original_subject == clean_subject,
                        EmailThread.account_id == account.id,
                        EmailThread.last_activity_at >= datetime.utcnow() - timedelta(days=7)  # Only recent threads
                    )
                ).order_by(desc(EmailThread.last_activity_at)).first()
            
            # Create new thread if none found
            if not thread:
                # Extract participants
                participants = set()
                if email_record.from_address:
                    participants.add(email_record.from_address.lower())
                
                for addr in (email_record.to_addresses or []) + (email_record.cc_addresses or []):
                    if addr.get('email'):
                        participants.add(addr['email'].lower())
                
                thread = EmailThread(
                    thread_id=email_record.message_id,  # Use message ID as thread ID for first message
                    subject=email_record.subject,
                    original_subject=clean_subject,
                    participants=list(participants),
                    primary_participants=[email_record.from_address] + [
                        addr['email'] for addr in email_record.to_addresses or [] if addr.get('email')
                    ],
                    message_count=1,
                    unread_count=1 if email_record.status == EmailStatus.UNREAD else 0,
                    has_attachments=email_record.has_attachments,
                    status=email_record.status,
                    priority=email_record.priority,
                    first_message_at=email_record.sent_at,
                    last_message_at=email_record.sent_at,
                    last_activity_at=email_record.received_at,
                    organization_id=email_record.organization_id,
                    account_id=account.id,
                    customer_id=email_record.customer_id,
                    vendor_id=email_record.vendor_id,
                    folder=email_record.folder
                )
                
                db.add(thread)
                db.flush()
            else:
                # Update existing thread
                thread.message_count += 1
                if email_record.status == EmailStatus.UNREAD:
                    thread.unread_count += 1
                if email_record.has_attachments:
                    thread.has_attachments = True
                thread.last_message_at = max(thread.last_message_at, email_record.sent_at)
                thread.last_activity_at = email_record.received_at
                
                # Update participants
                current_participants = set(thread.participants or [])
                if email_record.from_address:
                    current_participants.add(email_record.from_address.lower())
                for addr in (email_record.to_addresses or []) + (email_record.cc_addresses or []):
                    if addr.get('email'):
                        current_participants.add(addr['email'].lower())
                thread.participants = list(current_participants)
            
            return thread
            
        except Exception as e:
            logger.error(f"Error finding/creating thread: {str(e)}")
            return None
    
    def _update_email_if_changed(self, existing: Email, msg: email.message.Message, folder: str, db: Session) -> bool:
        """
        Update existing email if status or folder changed
        Returns True if updated
        """
        updated = False
        
        # Check if folder changed
        if existing.folder != folder:
            existing.folder = folder
            updated = True
        
        # Check if read status changed (this would require parsing IMAP flags)
        # This is a simplified implementation
        
        return updated


# Create global instance
email_sync_service = EmailSyncService()