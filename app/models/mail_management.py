# app/models/mail_management.py

"""
Mail and Email Management Models for inbox sync and email operations
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum, JSON, LargeBinary
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from enum import Enum as PyEnum

from app.core.database import Base

class EmailAccountType(PyEnum):
    IMAP = "imap"
    POP3 = "pop3"
    EXCHANGE = "exchange"
    GMAIL = "gmail"
    OUTLOOK = "outlook"

class EmailStatus(PyEnum):
    UNREAD = "unread"
    READ = "read"
    REPLIED = "replied"
    FORWARDED = "forwarded"
    ARCHIVED = "archived"
    DELETED = "deleted"
    SPAM = "spam"

class EmailPriority(PyEnum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

class EmailAccount(Base):
    __tablename__ = "email_accounts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)  # Display name for account
    email_address = Column(String(255), nullable=False, index=True)
    
    # Account configuration
    account_type = Column(Enum(EmailAccountType), nullable=False)
    
    # IMAP/POP3 settings
    incoming_server = Column(String(255), nullable=True)
    incoming_port = Column(Integer, nullable=True)
    incoming_ssl = Column(Boolean, default=True, nullable=False)
    
    # SMTP settings
    outgoing_server = Column(String(255), nullable=True)
    outgoing_port = Column(Integer, nullable=True)
    outgoing_ssl = Column(Boolean, default=True, nullable=False)
    
    # Authentication (encrypted)
    username = Column(String(255), nullable=True)
    password_encrypted = Column(Text, nullable=True)  # Encrypted password
    oauth_token = Column(Text, nullable=True)  # OAuth token for modern auth
    oauth_refresh_token = Column(Text, nullable=True)
    oauth_expires_at = Column(DateTime, nullable=True)
    
    # Sync settings
    sync_enabled = Column(Boolean, default=True, nullable=False)
    sync_frequency_minutes = Column(Integer, default=15, nullable=False)
    sync_folders = Column(JSON, nullable=True)  # Array of folder names to sync
    auto_link_to_tasks = Column(Boolean, default=True, nullable=False)
    auto_link_to_calendar = Column(Boolean, default=True, nullable=False)
    
    # Relations
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    last_sync_at = Column(DateTime, nullable=True)
    last_sync_status = Column(String(20), default="pending", nullable=False)
    last_sync_error = Column(Text, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    organization = relationship("Organization", back_populates="email_accounts")
    user = relationship("User", back_populates="email_accounts")
    emails = relationship("Email", back_populates="account", cascade="all, delete-orphan")
    sent_emails = relationship("SentEmail", back_populates="account", cascade="all, delete-orphan")

class Email(Base):
    __tablename__ = "emails"

    id = Column(Integer, primary_key=True, index=True)
    
    # Email identifiers
    message_id = Column(String(255), nullable=False, index=True)  # RFC message ID
    thread_id = Column(String(255), nullable=True, index=True)   # For threading
    
    # Email headers
    subject = Column(String(500), nullable=False, index=True)
    from_address = Column(String(255), nullable=False, index=True)
    from_name = Column(String(255), nullable=True)
    to_addresses = Column(JSON, nullable=False)  # Array of recipient emails
    cc_addresses = Column(JSON, nullable=True)   # Array of CC emails
    bcc_addresses = Column(JSON, nullable=True)  # Array of BCC emails
    reply_to = Column(String(255), nullable=True)
    
    # Email content
    body_text = Column(Text, nullable=True)
    body_html = Column(Text, nullable=True)
    
    # Email metadata
    status = Column(Enum(EmailStatus), default=EmailStatus.UNREAD, nullable=False)
    priority = Column(Enum(EmailPriority), default=EmailPriority.NORMAL, nullable=False)
    is_flagged = Column(Boolean, default=False, nullable=False)
    is_important = Column(Boolean, default=False, nullable=False)
    
    # Timing
    sent_at = Column(DateTime, nullable=False, index=True)
    received_at = Column(DateTime, nullable=False, index=True)
    
    # Relations
    account_id = Column(Integer, ForeignKey("email_accounts.id"), nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    
    # Linked entities
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)
    calendar_event_id = Column(Integer, ForeignKey("calendar_events.id"), nullable=True)
    
    # Folder/labels
    folder = Column(String(255), nullable=True)  # INBOX, Sent, Drafts, etc.
    labels = Column(JSON, nullable=True)  # Array of labels/tags
    
    # Size and attachments
    size_bytes = Column(Integer, nullable=True)
    has_attachments = Column(Boolean, default=False, nullable=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    account = relationship("EmailAccount", back_populates="emails")
    organization = relationship("Organization", back_populates="emails")
    task = relationship("Task", back_populates="linked_emails")
    calendar_event = relationship("CalendarEvent", back_populates="linked_emails")
    attachments = relationship("EmailAttachment", back_populates="email", cascade="all, delete-orphan")
    actions = relationship("EmailAction", back_populates="email", cascade="all, delete-orphan")
    replies = relationship("SentEmail", back_populates="in_reply_to")

class EmailAttachment(Base):
    __tablename__ = "email_attachments"

    id = Column(Integer, primary_key=True, index=True)
    email_id = Column(Integer, ForeignKey("emails.id"), nullable=False)
    
    # Attachment details
    filename = Column(String(255), nullable=False)
    content_type = Column(String(100), nullable=True)
    size_bytes = Column(Integer, nullable=True)
    content_id = Column(String(255), nullable=True)  # For inline attachments
    
    # Storage
    file_path = Column(String(500), nullable=True)  # Local file path
    file_data = Column(LargeBinary, nullable=True)  # Direct storage for small files
    
    # Status
    is_inline = Column(Boolean, default=False, nullable=False)
    is_downloaded = Column(Boolean, default=False, nullable=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    email = relationship("Email", back_populates="attachments")

class SentEmail(Base):
    __tablename__ = "sent_emails"

    id = Column(Integer, primary_key=True, index=True)
    
    # Email identifiers
    message_id = Column(String(255), nullable=True, index=True)
    thread_id = Column(String(255), nullable=True, index=True)
    
    # Email details
    subject = Column(String(500), nullable=False)
    to_addresses = Column(JSON, nullable=False)  # Array of recipient emails
    cc_addresses = Column(JSON, nullable=True)
    bcc_addresses = Column(JSON, nullable=True)
    
    # Content
    body_text = Column(Text, nullable=True)
    body_html = Column(Text, nullable=True)
    
    # Relations
    account_id = Column(Integer, ForeignKey("email_accounts.id"), nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    sent_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Linked entities
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)
    calendar_event_id = Column(Integer, ForeignKey("calendar_events.id"), nullable=True)
    in_reply_to_id = Column(Integer, ForeignKey("emails.id"), nullable=True)  # Reply to original email
    
    # Status
    status = Column(String(20), default="sent", nullable=False)  # sent, failed, pending
    delivery_status = Column(String(20), nullable=True)  # delivered, bounced, etc.
    
    # Timing
    sent_at = Column(DateTime, nullable=False)
    scheduled_at = Column(DateTime, nullable=True)  # For scheduled emails
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    account = relationship("EmailAccount", back_populates="sent_emails")
    organization = relationship("Organization", back_populates="sent_emails")
    sender = relationship("User", back_populates="sent_emails")
    task = relationship("Task", back_populates="sent_emails")
    calendar_event = relationship("CalendarEvent", back_populates="sent_emails")
    in_reply_to = relationship("Email", back_populates="replies")

class EmailAction(Base):
    __tablename__ = "email_actions"

    id = Column(Integer, primary_key=True, index=True)
    email_id = Column(Integer, ForeignKey("emails.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Action details
    action_type = Column(String(50), nullable=False)  # read, reply, forward, archive, delete, flag, etc.
    action_data = Column(JSON, nullable=True)  # Additional data for the action
    
    # Metadata
    performed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    email = relationship("Email", back_populates="actions")
    user = relationship("User", back_populates="email_actions")

class EmailTemplate(Base):
    __tablename__ = "email_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Template content
    subject_template = Column(String(500), nullable=False)
    body_text_template = Column(Text, nullable=True)
    body_html_template = Column(Text, nullable=True)
    
    # Template variables/placeholders
    variables = Column(JSON, nullable=True)  # Array of available variables
    
    # Relations
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Settings
    is_active = Column(Boolean, default=True, nullable=False)
    is_shared = Column(Boolean, default=False, nullable=False)
    category = Column(String(100), nullable=True)  # task_notification, meeting_invite, etc.
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    organization = relationship("Organization", back_populates="email_templates")
    creator = relationship("User", back_populates="created_email_templates")

class EmailRule(Base):
    __tablename__ = "email_rules"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Rule conditions
    conditions = Column(JSON, nullable=False)  # Array of condition objects
    
    # Rule actions
    actions = Column(JSON, nullable=False)  # Array of action objects
    
    # Relations
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Settings
    is_active = Column(Boolean, default=True, nullable=False)
    priority = Column(Integer, default=1, nullable=False)  # Higher number = higher priority
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    organization = relationship("Organization", back_populates="email_rules")
    user = relationship("User", back_populates="email_rules")