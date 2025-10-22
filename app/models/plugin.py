"""
Plugin System Models for Backend and Frontend Extensibility
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum, JSON, Index, UniqueConstraint
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional, Dict, Any, List

from app.core.database import Base


class PluginType(PyEnum):
    """Types of plugins"""
    BACKEND_SERVICE = "backend_service"
    FRONTEND_COMPONENT = "frontend_component"
    INTEGRATION = "integration"
    WORKFLOW = "workflow"
    REPORT = "report"
    WIDGET = "widget"
    THEME = "theme"


class PluginStatus(PyEnum):
    """Plugin status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    INSTALLING = "installing"
    UPDATING = "updating"
    ERROR = "error"


class PluginScope(PyEnum):
    """Scope of plugin availability"""
    GLOBAL = "global"  # Available to all organizations
    ORGANIZATION = "organization"  # Specific to one organization
    USER = "user"  # User-specific plugin


class Plugin(Base):
    """
    Plugin registry for backend and frontend extensibility.
    Supports modular architecture with pluggable components.
    """
    __tablename__ = "plugins"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Multi-tenant fields (optional for global plugins)
    organization_id: Mapped[Optional[int]] = mapped_column(
        Integer, 
        ForeignKey("organizations.id", name="fk_plugin_organization_id"), 
        nullable=True, 
        index=True
    )
    
    # Plugin identification
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    version: Mapped[str] = mapped_column(String(50), nullable=False, default="1.0.0")
    
    # Plugin metadata
    plugin_type: Mapped[str] = mapped_column(String(50), nullable=False)
    scope: Mapped[str] = mapped_column(String(50), default="organization", nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    author: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    homepage_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    documentation_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    
    # Plugin status and configuration
    status: Mapped[str] = mapped_column(String(50), default="inactive", nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Plugin files and resources
    entry_point: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    assets_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Configuration and settings
    config: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    default_settings: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Dependencies and requirements
    dependencies: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    min_platform_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    max_platform_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Permissions and security
    required_permissions: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    sandboxed: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Installation tracking
    install_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_installed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    installations: Mapped[list["PluginInstallation"]] = relationship(
        "PluginInstallation", 
        back_populates="plugin",
        cascade="all, delete-orphan"
    )
    hooks: Mapped[list["PluginHook"]] = relationship(
        "PluginHook", 
        back_populates="plugin",
        cascade="all, delete-orphan"
    )
    
    __table_args__ = (
        Index('idx_plugin_org_type', 'organization_id', 'plugin_type'),
        Index('idx_plugin_status', 'status'),
        Index('idx_plugin_scope', 'scope'),
        {'extend_existing': True}
    )


class PluginInstallation(Base):
    """
    Plugin installation instances.
    Tracks which plugins are installed for which organizations.
    """
    __tablename__ = "plugin_installations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # References
    plugin_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("plugins.id", name="fk_installation_plugin_id"), 
        nullable=False,
        index=True
    )
    organization_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("organizations.id", name="fk_installation_organization_id"), 
        nullable=False, 
        index=True
    )
    
    # Installation details
    installed_by: Mapped[Optional[int]] = mapped_column(
        Integer, 
        ForeignKey("users.id", name="fk_installation_user_id"), 
        nullable=True
    )
    installed_version: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Status and configuration
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    settings: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Usage tracking
    last_used_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    usage_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Error tracking
    error_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    last_error_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    installed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    plugin: Mapped["Plugin"] = relationship("Plugin", back_populates="installations")
    user: Mapped[Optional["app.models.user_models.User"]] = relationship("app.models.user_models.User")
    
    __table_args__ = (
        Index('idx_installation_org_plugin', 'organization_id', 'plugin_id'),
        UniqueConstraint('plugin_id', 'organization_id', name='uq_plugin_org_installation'),
        {'extend_existing': True}
    )


class PluginHook(Base):
    """
    Plugin hooks for event-driven architecture.
    Allows plugins to register for system events.
    """
    __tablename__ = "plugin_hooks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Plugin reference
    plugin_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("plugins.id", name="fk_hook_plugin_id"), 
        nullable=False,
        index=True
    )
    
    # Hook details
    hook_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Handler configuration
    handler_function: Mapped[str] = mapped_column(String(500), nullable=False)
    priority: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    
    # Status
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Execution tracking
    execution_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_executed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    average_execution_time_ms: Mapped[Optional[float]] = mapped_column(JSON, nullable=True)
    
    # Error tracking
    error_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    plugin: Mapped["Plugin"] = relationship("Plugin", back_populates="hooks")
    
    __table_args__ = (
        Index('idx_hook_plugin_event', 'plugin_id', 'event_type'),
        Index('idx_hook_name', 'hook_name'),
        {'extend_existing': True}
    )


class PluginRegistry(Base):
    """
    Registry of available plugins from marketplace.
    Tracks plugin metadata for discovery and installation.
    """
    __tablename__ = "plugin_registry"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Plugin identification
    slug: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Metadata
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    tags: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    
    # Versions
    latest_version: Mapped[str] = mapped_column(String(50), nullable=False)
    available_versions: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    
    # Distribution
    download_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    repository_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    
    # Metadata
    author: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    license: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    homepage_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    
    # Ratings and popularity
    rating: Mapped[Optional[float]] = mapped_column(JSON, nullable=True)
    download_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Status
    verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    
    __table_args__ = (
        Index('idx_registry_category', 'category'),
        Index('idx_registry_verified', 'verified'),
        {'extend_existing': True}
    )
