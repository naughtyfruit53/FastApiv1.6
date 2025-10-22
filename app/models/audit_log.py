"""
Audit Log Models for comprehensive activity tracking
Including AI/chatbot-driven actions and automation tasks
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON, Index
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional, Dict, Any

from app.core.database import Base


class AuditActionType(PyEnum):
    """Types of auditable actions"""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    READ = "read"
    EXPORT = "export"
    IMPORT = "import"
    LOGIN = "login"
    LOGOUT = "logout"
    API_CALL = "api_call"
    AI_ACTION = "ai_action"
    AUTOMATION = "automation"
    INTEGRATION = "integration"


class AuditEntityType(PyEnum):
    """Types of entities being audited"""
    USER = "user"
    COMPANY = "company"
    CUSTOMER = "customer"
    VENDOR = "vendor"
    PRODUCT = "product"
    VOUCHER = "voucher"
    INVOICE = "invoice"
    ORDER = "order"
    PAYMENT = "payment"
    REPORT = "report"
    SETTINGS = "settings"
    INTEGRATION = "integration"
    AI_AGENT = "ai_agent"
    PLUGIN = "plugin"
    WORKFLOW = "workflow"


class AuditLog(Base):
    """
    Enhanced Audit Log with support for AI/chatbot actions and automation.
    Tracks all major system actions with comprehensive metadata.
    """
    __tablename__ = "audit_logs_enhanced"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Multi-tenant field
    organization_id: Mapped[Optional[int]] = mapped_column(
        Integer, 
        ForeignKey("organizations.id", name="fk_audit_enhanced_organization_id"), 
        nullable=True, 
        index=True
    )
    
    # Entity information
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    entity_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    entity_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Action details
    action: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    action_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Actor information (human or system)
    user_id: Mapped[Optional[int]] = mapped_column(
        Integer, 
        ForeignKey("users.id", name="fk_audit_enhanced_user_id"), 
        nullable=True,
        index=True
    )
    actor_type: Mapped[str] = mapped_column(String(50), default="user", nullable=False)  # user, ai_agent, automation, system
    actor_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # ID of AI agent or automation
    actor_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # AI/Automation specific fields
    ai_agent_id: Mapped[Optional[int]] = mapped_column(
        Integer, 
        ForeignKey("ai_agents.id", name="fk_audit_ai_agent_id"), 
        nullable=True
    )
    automation_workflow_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    triggered_by_automation: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Change tracking
    changes: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    old_values: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    new_values: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Context and metadata
    context: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Request information
    ip_address: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    request_method: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    request_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Status and result
    success: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Compliance and security
    severity: Mapped[str] = mapped_column(String(50), default="info", nullable=False)  # info, warning, critical
    compliance_tags: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    
    # Timestamps
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    user: Mapped[Optional["app.models.user_models.User"]] = relationship("app.models.user_models.User")
    ai_agent: Mapped[Optional["app.models.ai_agents.AIAgent"]] = relationship("app.models.ai_agents.AIAgent")
    
    __table_args__ = (
        Index('idx_audit_org_entity', 'organization_id', 'entity_type', 'entity_id'),
        Index('idx_audit_org_action', 'organization_id', 'action'),
        Index('idx_audit_org_timestamp', 'organization_id', 'timestamp'),
        Index('idx_audit_user_timestamp', 'user_id', 'timestamp'),
        Index('idx_audit_actor', 'actor_type', 'actor_id'),
        Index('idx_audit_ai_agent', 'ai_agent_id'),
        Index('idx_audit_automation', 'triggered_by_automation'),
        {'extend_existing': True}
    )


class AuditLogView(Base):
    """
    Audit log view configuration for UI.
    Allows users to configure what they want to see in audit logs.
    """
    __tablename__ = "audit_log_views"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("organizations.id", name="fk_audit_view_organization_id"), 
        nullable=False, 
        index=True
    )
    
    # View configuration
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Filters
    entity_types: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    action_types: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    actor_types: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    severity_levels: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    
    # Display settings
    columns: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    sort_order: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Access control
    created_by: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("users.id", name="fk_audit_view_user_id"), 
        nullable=False
    )
    shared: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user: Mapped["app.models.user_models.User"] = relationship("app.models.user_models.User")
    
    __table_args__ = (
        Index('idx_audit_view_org', 'organization_id'),
        Index('idx_audit_view_user', 'created_by'),
        {'extend_existing': True}
    )


class AuditLogExport(Base):
    """
    Audit log export requests for compliance and reporting.
    """
    __tablename__ = "audit_log_exports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("organizations.id", name="fk_audit_export_organization_id"), 
        nullable=False, 
        index=True
    )
    
    # Export details
    requested_by: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("users.id", name="fk_audit_export_user_id"), 
        nullable=False
    )
    
    # Filter criteria
    start_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    end_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    filters: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Export configuration
    format: Mapped[str] = mapped_column(String(50), default="csv", nullable=False)  # csv, json, pdf
    include_metadata: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Status
    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)  # pending, processing, completed, failed
    record_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Output
    file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    file_size_bytes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    download_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Error tracking
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user: Mapped["app.models.user_models.User"] = relationship("app.models.user_models.User")
    
    __table_args__ = (
        Index('idx_audit_export_org_status', 'organization_id', 'status'),
        Index('idx_audit_export_user', 'requested_by'),
        {'extend_existing': True}
    )
