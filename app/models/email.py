# app/models/email.py

"""
Email Module Core Models
Contains all email-related models for IMAP/SMTP sync, threads, attachments, and mail accounts
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, JSON, Index, UniqueConstraint, Date, Enum as SQLEnum, LargeBinary
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.core.database import Base
from typing import List, Optional
from datetime import datetime, date
import enum


class EmailAccountType(enum.Enum):
    """Types of email accounts supported"""
    IMAP = "imap"
    POP3 = "pop3"
    EXCHANGE = "exchange"
    GMAIL_API = "gmail_api"
    OUTLOOK_API = "outlook_api"


class EmailSyncStatus(enum.Enum):
    """Email account sync status"""
    ACTIVE = "active"
    PAUSED = "paused"
    ERROR = "error"
    DISABLED = "disabled"


class EmailStatus(enum.Enum):
    """Email message status"""
    UNREAD = "unread"
    READ = "read"
    REPLIED = "replied"
    FORWARDED = "forwarded"
    ARCHIVED = "archived"
    DELETED = "deleted"
    SPAM = "spam"


class EmailPriority(enum.Enum):
    """Email priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class MailAccount(Base):
    """
    Email accounts for IMAP/SMTP sync with OAuth2 support
    """
    __tablename__ = "mail_accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Account identification
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email_address: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    display_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Account type and provider
    account_type: Mapped[EmailAccountType] = mapped_column(
        SQLEnum(EmailAccountType, values_callable=lambda enum: [e.value for e in enum]),
        nullable=False
    )
    provider: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # gmail, outlook, etc.
    
    # Server configuration for IMAP/SMTP
    incoming_server: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    incoming_port: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    incoming_ssl: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    incoming_auth_method: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # password, oauth2, xoauth2
    
    outgoing_server: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    outgoing_port: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    outgoing_ssl: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    outgoing_auth_method: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Authentication (encrypted)
    username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    password_encrypted: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # OAuth2 tokens (encrypted) - reference to UserEmailToken
    oauth_token_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("user_email_tokens.id"), nullable=True)
    
    # Sync configuration
    sync_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    sync_frequency_minutes: Mapped[int] = mapped_column(Integer, default=15, nullable=False)
    sync_folders: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)  # List of folders to sync
    full_sync_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    last_sync_uid: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # Last synced message UID
    
    # Integration settings
    auto_link_to_customers: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    auto_link_to_vendors: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    auto_create_tasks: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Organization and user
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Status tracking
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    sync_status: Mapped[EmailSyncStatus] = mapped_column(
        SQLEnum(EmailSyncStatus, values_callable=lambda enum: [e.value for e in enum]),
        default=EmailSyncStatus.ACTIVE, 
        nullable=False
    )
    last_sync_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_sync_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    total_messages_synced: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    organization: Mapped["app.models.user_models.Organization"] = relationship(
        "app.models.user_models.Organization",
        foreign_keys=[organization_id]
    )
    user: Mapped["app.models.user_models.User"] = relationship(
        "app.models.user_models.User",
        foreign_keys=[user_id]
    )
    oauth_token: Mapped[Optional["app.models.oauth_models.UserEmailToken"]] = relationship(
        "app.models.oauth_models.UserEmailToken",
        foreign_keys=[oauth_token_id]
    )
    
    # Reverse relationships
    emails: Mapped[List["Email"]] = relationship("Email", back_populates="account")
    email_threads: Mapped[List["EmailThread"]] = relationship("EmailThread", back_populates="account")
    
    __table_args__ = (
        UniqueConstraint('email_address', 'user_id', name='uq_mail_account_email_user'),
        Index('idx_mail_account_org_user', 'organization_id', 'user_id'),
        Index('idx_mail_account_sync_status', 'sync_status'),
        Index('idx_mail_account_last_sync', 'last_sync_at'),
        {'extend_existing': True}
    )


class EmailThread(Base):
    """
    Email conversation threads
    """
    __tablename__ = "email_threads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Thread identification
    thread_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)  # Provider thread ID
    subject: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    original_subject: Mapped[str] = mapped_column(String(500), nullable=False)  # Without Re:, Fwd: prefixes
    
    # Thread participants
    participants: Mapped[dict] = mapped_column(JSONB, nullable=False)  # All email addresses involved
    primary_participants: Mapped[list] = mapped_column(JSONB, nullable=False)  # Main participants (from/to)
    
    # Thread metadata
    message_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    unread_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    has_attachments: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Thread status
    status: Mapped[EmailStatus] = mapped_column(
        SQLEnum(EmailStatus, values_callable=lambda enum: [e.value for e in enum]),
        default=EmailStatus.UNREAD, 
        nullable=False
    )
    priority: Mapped[EmailPriority] = mapped_column(
        SQLEnum(EmailPriority, values_callable=lambda enum: [e.value for e in enum]),
        default=EmailPriority.NORMAL, 
        nullable=False
    )
    is_flagged: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_important: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Timestamps
    first_message_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    last_message_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    last_activity_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    
    # Organization and account
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    account_id: Mapped[int] = mapped_column(Integer, ForeignKey("mail_accounts.id"), nullable=False, index=True)
    
    # Business entity linking
    customer_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("customers.id"), nullable=True, index=True)
    vendor_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("vendors.id"), nullable=True, index=True)
    
    # Labels and categorization
    labels: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    folder: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    organization: Mapped["app.models.user_models.Organization"] = relationship(
        "app.models.user_models.Organization",
        foreign_keys=[organization_id]
    )
    account: Mapped["MailAccount"] = relationship("MailAccount", back_populates="email_threads")
    customer: Mapped[Optional["app.models.customer_models.Customer"]] = relationship(
        "app.models.customer_models.Customer",
        foreign_keys=[customer_id]
    )
    vendor: Mapped[Optional["app.models.customer_models.Vendor"]] = relationship(
        "app.models.customer_models.Vendor",
        foreign_keys=[vendor_id]
    )
    
    # Reverse relationships
    emails: Mapped[List["Email"]] = relationship("Email", back_populates="thread")
    
    __table_args__ = (
        UniqueConstraint('thread_id', 'account_id', name='uq_email_thread_id_account'),
        Index('idx_email_thread_org_account', 'organization_id', 'account_id'),
        Index('idx_email_thread_last_activity', 'last_activity_at'),
        Index('idx_email_thread_status', 'status'),
        Index('idx_email_thread_participants', 'participants', postgresql_using='gin'),
        {'extend_existing': True}
    )


class Email(Base):
    """
    Individual email messages
    """
    __tablename__ = "emails"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Message identification
    message_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)  # Email Message-ID header
    thread_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("email_threads.id"), nullable=True, index=True)
    provider_message_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)  # Provider-specific ID
    uid: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)  # IMAP UID
    
    # Message headers
    subject: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    from_address: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    from_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    reply_to: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Recipients
    to_addresses: Mapped[list] = mapped_column(JSONB, nullable=False)  # [{"email": "...", "name": "..."}]
    cc_addresses: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    bcc_addresses: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    
    # Message content (sanitized)
    body_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    body_html: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Sanitized HTML
    body_html_raw: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Original HTML (internal use)
    
    # Message metadata
    status: Mapped[EmailStatus] = mapped_column(
        SQLEnum(EmailStatus, values_callable=lambda enum: [e.value for e in enum]),
        default=EmailStatus.UNREAD, 
        nullable=False, 
        index=True
    )
    priority: Mapped[EmailPriority] = mapped_column(
        SQLEnum(EmailPriority, values_callable=lambda enum: [e.value for e in enum]),
        default=EmailPriority.NORMAL, 
        nullable=False
    )
    is_flagged: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_important: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    has_attachments: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Timestamps
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    
    # Organization and account
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    account_id: Mapped[int] = mapped_column(Integer, ForeignKey("mail_accounts.id"), nullable=False, index=True)
    
    # Business entity linking
    customer_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("customers.id"), nullable=True, index=True)
    vendor_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("vendors.id"), nullable=True, index=True)
    
    # Folder and labels
    folder: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    labels: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    
    # Message properties
    size_bytes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    headers_raw: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)  # Raw email headers
    
    # Processing status
    is_processed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    processing_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    organization: Mapped["app.models.user_models.Organization"] = relationship(
        "app.models.user_models.Organization",
        foreign_keys=[organization_id]
    )
    account: Mapped["MailAccount"] = relationship("MailAccount", back_populates="emails")
    thread: Mapped[Optional["EmailThread"]] = relationship("EmailThread", back_populates="emails")
    customer: Mapped[Optional["app.models.customer_models.Customer"]] = relationship(
        "app.models.customer_models.Customer",
        foreign_keys=[customer_id]
    )
    vendor: Mapped[Optional["app.models.customer_models.Vendor"]] = relationship(
        "app.models.customer_models.Vendor",
        foreign_keys=[vendor_id]
    )
    
    # Reverse relationships
    attachments: Mapped[List["EmailAttachment"]] = relationship("EmailAttachment", back_populates="email")
    
    __table_args__ = (
        UniqueConstraint('message_id', 'account_id', name='uq_email_message_id_account'),
        Index('idx_email_org_account', 'organization_id', 'account_id'),
        Index('idx_email_from_received', 'from_address', 'received_at'),
        Index('idx_email_status_received', 'status', 'received_at'),
        Index('idx_email_subject_text', 'subject'),  # For search
        {'extend_existing': True}
    )


class EmailAttachment(Base):
    """
    Email attachments with secure storage
    """
    __tablename__ = "email_attachments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Parent email
    email_id: Mapped[int] = mapped_column(Integer, ForeignKey("emails.id"), nullable=False, index=True)
    
    # File metadata
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)  # Original name from email
    content_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    size_bytes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Content identification
    content_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # For inline attachments
    content_disposition: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # attachment, inline
    
    # Storage
    file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)  # Path to stored file
    file_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)  # SHA-256 hash for deduplication
    
    # Security and scanning
    is_safe: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)  # Virus scan result
    scan_result: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Scan details
    is_quarantined: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Download tracking
    is_downloaded: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    download_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_downloaded_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Inline image handling
    is_inline: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    email: Mapped["Email"] = relationship("Email", back_populates="attachments")
    
    __table_args__ = (
        Index('idx_email_attachment_email_id', 'email_id'),
        Index('idx_email_attachment_filename', 'filename'),
        Index('idx_email_attachment_hash', 'file_hash'),
        {'extend_existing': True}
    )


class EmailSyncLog(Base):
    """
    Log of email sync operations for monitoring and debugging
    """
    __tablename__ = "email_sync_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Sync operation
    account_id: Mapped[int] = mapped_column(Integer, ForeignKey("mail_accounts.id"), nullable=False, index=True)
    sync_type: Mapped[str] = mapped_column(String(50), nullable=False)  # full, incremental, folder
    folder: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Results
    status: Mapped[str] = mapped_column(String(20), nullable=False)  # success, error, partial
    messages_processed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    messages_new: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    messages_updated: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    messages_deleted: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Error details
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    error_details: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    # Timing
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Sync range
    sync_from_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    sync_to_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_uid_synced: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    account: Mapped["MailAccount"] = relationship("MailAccount", foreign_keys=[account_id])
    
    __table_args__ = (
        Index('idx_email_sync_log_account_started', 'account_id', 'started_at'),
        Index('idx_email_sync_log_status', 'status'),
        {'extend_existing': True}
    )


class VoucherEmailTemplate(Base):
    """
    Email templates for different voucher types and entity types
    """
    __tablename__ = "voucher_email_templates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Multi-tenant
    organization_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("organizations.id", name="fk_voucher_email_templates_organization_id"),
        nullable=False, 
        index=True
    )
    
    # Template identification
    voucher_type: Mapped[str] = mapped_column(String(50), nullable=False)  # purchase_order, sales_order, etc.
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)   # customer, vendor
    
    # Email content
    subject_template: Mapped[str] = mapped_column(String(500), nullable=False)
    body_template: Mapped[Text] = mapped_column(Text, nullable=False)
    
    # Metadata
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    
    __table_args__ = (
        Index('idx_voucher_email_template_org_type', 'organization_id', 'voucher_type', 'entity_type'),
        UniqueConstraint('organization_id', 'voucher_type', 'entity_type', name='uq_org_voucher_entity_template'),
        {'extend_existing': True}
    )