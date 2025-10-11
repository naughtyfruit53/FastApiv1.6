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
import re
import socket
import re
import ssl
import time
import concurrent.futures
import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple
from urllib.parse import urlparse, urljoin
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import decode_header
from email.utils import parsedate_tz, mktime_tz, parseaddr
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func

from app.core.config import settings
from app.core.database import SessionLocal, AsyncSessionLocal
from app.models.email import (
    MailAccount, Email, EmailThread, EmailAttachment, EmailSyncStatus, EmailStatus, EmailPriority, EmailSyncLog, EmailAccountType
)
from app.models.oauth_models import TokenStatus
from app.utils.text_processing import extract_plain_text, sanitize_html
from app.services.oauth_service import OAuth2Service
from app.services.calendar_sync_service import calendar_sync_service
from app.services.email_search_service import email_search_service
from app.services.email_ai_service import email_ai_service
from app.services.ocr_service import email_attachment_ocr_service

from app.services.email_api_sync_service import EmailAPISyncService  # Import the API sync service

logger = logging.getLogger(__name__)

# Import API sync service for OAuth2 providers
# This is the restored working logic from commit c2fadf02
try:
    from app.services.email_api_sync_service import EmailAPISyncService
    api_sync_available = True
except ImportError:
    api_sync_available = False
    logger.warning("Email API sync service not available, falling back to IMAP only")


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
    
    def get_imap_connection(self, account: MailAccount, db: Session) -> Optional[imaplib.IMAP4_SSL]:
        """
        Establish IMAP connection with OAuth2 or password authentication
        Uses standard imaplib.IMAP4_SSL for better compatibility
        """
        try:
            port = account.incoming_port or (993 if account.incoming_ssl else 143)
            logger.info(f"Attempting IMAP connection to {account.incoming_server}:{port} with SSL={account.incoming_ssl}")
            logger.info(f"Account provider: {account.provider}, auth_method: {account.incoming_auth_method}, has_token: {bool(account.oauth_token_id)}, has_password: {bool(account.password_encrypted)}")
            
            # Create SSL context
            context = ssl.create_default_context()
            context.check_hostname = True
            context.verify_mode = ssl.CERT_REQUIRED
            context.minimum_version = ssl.TLSVersion.TLSv1_2
            
            # Connect using standard IMAP4_SSL
            if account.incoming_ssl:
                imap = imaplib.IMAP4_SSL(
                    host=account.incoming_server,
                    port=port,
                    ssl_context=context,
                    timeout=30
                )
            else:
                imap = imaplib.IMAP4(host=account.incoming_server, port=port, timeout=30)
            
            logger.info(f"IMAP connection established to {account.incoming_server}:{port}")
            
            # Authenticate based on credentials available
            if account.oauth_token_id:
                # OAuth2 XOAUTH2 authentication
                # Use synchronous OAuth service
                oauth_service = OAuth2Service()
                credentials = oauth_service.sync_get_email_credentials(account.oauth_token_id, db)
                
                if not credentials:
                    logger.error(f"Failed to get OAuth2 credentials for account {account.id}")
                    return None
                
                email_addr = credentials.get('email')
                access_token = credentials.get('access_token')
                if not email_addr or not access_token:
                    logger.error(f"Missing email or access_token for account {account.id}")
                    return None
                
                auth_string = self._build_oauth2_auth_string(email_addr, access_token)
                if not auth_string:
                    logger.error(f"Failed to build auth_string for account {account.id}")
                    return None
                
                try:
                    # XOAUTH2 authentication
                    auth_bytes = base64.b64encode(auth_string.encode('utf-8'))
                    imap.authenticate('XOAUTH2', lambda x: auth_bytes)
                    logger.info("OAuth2 XOAUTH2 authentication succeeded")
                except imaplib.IMAP4.error as e:
                    logger.error(f"OAuth2 authentication failed for account {account.id}: {str(e)}")
                    return None
                
            elif account.username and account.password_encrypted:
                # Password authentication
                from app.utils.encryption import decrypt_field, EncryptionKeys
                password = decrypt_field(account.password_encrypted, EncryptionKeys.PII)
                logger.info(f"Using password auth for {account.username}")
                try:
                    imap.login(account.username, password)
                    logger.info("Password authentication succeeded")
                except imaplib.IMAP4.error as e:
                    logger.error(f"Password authentication failed for account {account.id}: {str(e)}")
                    return None
            else:
                logger.error(f"No valid authentication method for account {account.id}")
                return None
            
            logger.info("IMAP connection and authentication successful")
            return imap
            
        except Exception as e:
            logger.error(f"IMAP connection failed for account {account.id}: {str(e)}", exc_info=True)
            return None
    
    def _build_oauth2_auth_string(self, email: str, access_token: str) -> Optional[str]:
        """
        Build OAuth2 authentication string for IMAP/SMTP
        """
        if not email or not access_token:
            logger.error("Email or access token is missing for building auth string")
            return None
        return f'user={email}\x01auth=Bearer {access_token}\x01\x01'
    
    def sync_account(self, account_id: int, full_sync: bool = False, manual: bool = False) -> tuple[bool, dict]:
        """
        Sync emails for a specific account
        Returns (success, {'new': int, 'updated': int, 'total_messages_synced': int})
        """
        if self.db:
            return self._perform_sync(self.db, account_id, full_sync, manual)
        else:
            db = SessionLocal()
            try:
                return self._perform_sync(db, account_id, full_sync, manual)
            finally:
                db.close()
    
    def _perform_sync(self, db: Session, account_id: int, full_sync: bool = False, manual: bool = False) -> tuple[bool, dict]:
        account = db.query(MailAccount).filter(MailAccount.id == account_id).first()
        if not account:
            logger.error(f"Account {account_id} not found")
            return False, {'new': 0, 'updated': 0, 'total_messages_synced': 0}
        
        if not (manual or (account.sync_enabled and account.sync_status == EmailSyncStatus.ACTIVE)):
            logger.info(f"Sync skipped for account {account_id}")
            return True, {'new': 0, 'updated': 0, 'total_messages_synced': 0}
        
        # RESTORED LOGIC FROM WORKING COMMIT c2fadf02:
        # Prefer API-based sync for OAuth2 accounts (gmail_api, outlook_api)
        # This was the key to successful sync before IMAP issues
        if api_sync_available and account.account_type in [EmailAccountType.GMAIL_API, EmailAccountType.OUTLOOK_API]:
            logger.info(f"Using API-based sync for account {account_id} (type: {account.account_type})")
            api_sync = EmailAPISyncService(db)
            success, emails_synced, error = api_sync.sync_account_via_api(account, db, full_sync)
            
            if success:
                logger.info(f"API sync successful: {emails_synced} emails synced")
                # Update total_messages_synced to reflect actual count in DB
                total_emails = db.query(func.count(Email.id)).filter(Email.account_id == account_id).scalar()
                account.total_messages_synced = total_emails
                db.commit()
                return True, {'new': emails_synced, 'updated': 0, 'total_messages_synced': total_emails}
            else:
                logger.error(f"API sync failed: {error}")
                # Fall through to IMAP if API fails (though it shouldn't for these account types)
                if account.account_type in [EmailAccountType.GMAIL_API, EmailAccountType.OUTLOOK_API]:
                    # Don't fall back to IMAP for API-only account types
                    return False, {'new': 0, 'updated': 0, 'total_messages_synced': 0}
        
        # Create sync log
        sync_log = EmailSyncLog(
            account_id=account_id,
            sync_type='full' if full_sync else 'incremental',
            status='running',
            started_at=datetime.utcnow()
        )
        db.add(sync_log)
        db.commit()
        
        # Exponential backoff retry logic
        max_retries = 3
        base_delay = 2  # seconds
        
        for attempt in range(max_retries):
            try:
                # Refresh token if needed before connecting
                if account.oauth_token_id:
                    oauth_service = OAuth2Service()
                    refresh_result = oauth_service.sync_refresh_token(account.oauth_token_id, db)
                    if not refresh_result:
                        if attempt < max_retries - 1:
                            delay = base_delay * (2 ** attempt)
                            logger.info(f"Refresh failed, retrying in {delay}s")
                            time.sleep(delay)
                        else:
                            account.sync_status = EmailSyncStatus.ERROR
                            db.commit()
                            return False, {'new': 0, 'updated': 0, 'total_messages_synced': 0}
                
                # Connect to IMAP with exponential backoff
                imap = None
                for conn_attempt in range(3):
                    try:
                        imap = self.get_imap_connection(account, db)
                        if imap:
                            break
                        # Exponential backoff before retry
                        if conn_attempt < 2:
                            delay = base_delay * (2 ** conn_attempt)
                            logger.info(f"Connection failed, retrying in {delay}s (attempt {conn_attempt + 1}/3)")
                            time.sleep(delay)
                    except Exception as conn_e:
                        logger.warning(f"Connection attempt {conn_attempt + 1} failed: {str(conn_e)}")
                        if conn_attempt < 2:
                            delay = base_delay * (2 ** conn_attempt)
                            time.sleep(delay)
                
                if not imap:
                    raise Exception("Failed to connect to IMAP server after retries")
                
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
                account.total_messages_synced += total_new + total_updated  # Add both new and updated
                
                # Update to actual count in DB for accuracy
                total_emails = db.query(func.count(Email.id)).filter(Email.account_id == account_id).scalar()
                account.total_messages_synced = total_emails
                
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
                try:
                    imap.close()
                    imap.logout()
                except:
                    pass  # Ignore errors on close
                
                logger.info(f"Successfully synced account {account_id}: {total_new} new, {total_updated} updated")
                return True, {'new': total_new, 'updated': total_updated, 'total_messages_synced': total_emails}
                
            except Exception as e:
                error_msg = f"Sync attempt {attempt + 1} failed for account {account_id}: {str(e)}"
                logger.error(error_msg, exc_info=True)
                
                if attempt < max_retries - 1:
                    # Exponential backoff before retry
                    delay = base_delay * (2 ** attempt)
                    logger.info(f"Retrying sync in {delay}s (attempt {attempt + 2}/{max_retries})")
                    time.sleep(delay)
                else:
                    # Final failure - update account and sync log
                    account.last_sync_error = error_msg
                    sync_log.status = 'error'
                    sync_log.error_message = error_msg
                    sync_log.completed_at = datetime.utcnow()
                    
                    db.commit()
                    return False, {'new': 0, 'updated': 0, 'total_messages_synced': 0}
    
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
            from app.models.base import Customer, Vendor
            
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
            
            # First, try to find by references or in-reply_to
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