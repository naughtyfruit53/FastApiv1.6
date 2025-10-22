# app/models/website_agent.py

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON, Index, UniqueConstraint, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.core.database import Base
from typing import List, Optional, Dict, Any
from datetime import datetime, date


class WebsiteProject(Base):
    """
    Model for website projects managed by the website agent.
    Supports multi-tenant architecture with organization-level isolation.
    """
    __tablename__ = "website_projects"
 
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
 
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_website_project_organization_id"), nullable=False, index=True)
 
    # Project identification
    project_name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    project_type: Mapped[str] = mapped_column(String, nullable=False, default="landing_page") # 'landing_page', 'ecommerce', 'corporate', 'blog', 'portfolio'
    
    # Customer reference
    customer_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("customers.id", name="fk_website_project_customer_id"), nullable=True)
    
    # Project status
    status: Mapped[str] = mapped_column(String, nullable=False, default="draft") # 'draft', 'in_progress', 'review', 'deployed', 'archived'
    
    # Website configuration
    domain: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    subdomain: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    theme: Mapped[str] = mapped_column(String, nullable=False, default="modern")
    primary_color: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    secondary_color: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    # Content configuration
    site_title: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    site_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    logo_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    favicon_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    # Pages and sections (JSON)
    pages_config: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # SEO configuration
    seo_config: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Analytics configuration
    analytics_config: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Deployment information
    deployment_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    deployment_provider: Mapped[Optional[str]] = mapped_column(String, nullable=True) # 'vercel', 'netlify', 'aws', 'custom'
    last_deployed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Chatbot integration
    chatbot_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    chatbot_config: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # User tracking
    created_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", name="fk_website_project_created_by_id"), nullable=True)
    updated_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", name="fk_website_project_updated_by_id"), nullable=True)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")
    customer: Mapped[Optional["Customer"]] = relationship("Customer")
    created_by: Mapped[Optional["User"]] = relationship("User", foreign_keys=[created_by_id])
    updated_by: Mapped[Optional["User"]] = relationship("User", foreign_keys=[updated_by_id])
    pages: Mapped[List["WebsitePage"]] = relationship("WebsitePage", back_populates="project", cascade="all, delete-orphan")
    deployments: Mapped[List["WebsiteDeployment"]] = relationship("WebsiteDeployment", back_populates="project", cascade="all, delete-orphan")
    maintenance_logs: Mapped[List["WebsiteMaintenanceLog"]] = relationship("WebsiteMaintenanceLog", back_populates="project", cascade="all, delete-orphan")
    
    __table_args__ = (
        UniqueConstraint('organization_id', 'project_name', name='uq_website_project_org_name'),
        Index('idx_website_project_org_status', 'organization_id', 'status'),
        Index('idx_website_project_org_type', 'organization_id', 'project_type'),
        Index('idx_website_project_customer', 'customer_id'),
        Index('idx_website_project_created_at', 'created_at'),
    )


class WebsitePage(Base):
    """
    Model for individual pages within a website project.
    """
    __tablename__ = "website_pages"
 
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
 
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_website_page_organization_id"), nullable=False, index=True)
 
    # Project reference
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("website_projects.id", name="fk_website_page_project_id"), nullable=False)
    
    # Page details
    page_name: Mapped[str] = mapped_column(String, nullable=False)
    page_slug: Mapped[str] = mapped_column(String, nullable=False)
    page_type: Mapped[str] = mapped_column(String, nullable=False, default="standard") # 'home', 'about', 'contact', 'product', 'blog', 'standard'
    
    # Page content
    title: Mapped[str] = mapped_column(String, nullable=False)
    meta_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True) # HTML or JSON content
    
    # Sections configuration
    sections_config: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Page settings
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)
    order_index: Mapped[int] = mapped_column(Integer, default=0)
    
    # SEO
    seo_keywords: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    og_image: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")
    project: Mapped["WebsiteProject"] = relationship("WebsiteProject", back_populates="pages")
    
    __table_args__ = (
        UniqueConstraint('project_id', 'page_slug', name='uq_website_page_project_slug'),
        Index('idx_website_page_org_project', 'organization_id', 'project_id'),
        Index('idx_website_page_type', 'page_type'),
        Index('idx_website_page_published', 'is_published'),
        Index('idx_website_page_order', 'project_id', 'order_index'),
    )


class WebsiteDeployment(Base):
    """
    Model for tracking website deployment history.
    """
    __tablename__ = "website_deployments"
 
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
 
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_website_deployment_organization_id"), nullable=False, index=True)
 
    # Project reference
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("website_projects.id", name="fk_website_deployment_project_id"), nullable=False)
    
    # Deployment details
    deployment_version: Mapped[str] = mapped_column(String, nullable=False)
    deployment_status: Mapped[str] = mapped_column(String, nullable=False, default="pending") # 'pending', 'in_progress', 'success', 'failed'
    
    # Deployment configuration
    deployment_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    deployment_provider: Mapped[str] = mapped_column(String, nullable=False) # 'vercel', 'netlify', 'aws', 'custom'
    deployment_config: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Deployment results
    deployment_log: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timing
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # User tracking
    deployed_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", name="fk_website_deployment_deployed_by_id"), nullable=True)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")
    project: Mapped["WebsiteProject"] = relationship("WebsiteProject", back_populates="deployments")
    deployed_by: Mapped[Optional["User"]] = relationship("User")
    
    __table_args__ = (
        Index('idx_website_deployment_org_project', 'organization_id', 'project_id'),
        Index('idx_website_deployment_status', 'deployment_status'),
        Index('idx_website_deployment_created', 'created_at'),
    )


class WebsiteMaintenanceLog(Base):
    """
    Model for tracking website maintenance activities and updates.
    """
    __tablename__ = "website_maintenance_logs"
 
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
 
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_website_maintenance_log_organization_id"), nullable=False, index=True)
 
    # Project reference
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("website_projects.id", name="fk_website_maintenance_log_project_id"), nullable=False)
    
    # Maintenance details
    maintenance_type: Mapped[str] = mapped_column(String, nullable=False) # 'content_update', 'security_patch', 'performance_optimization', 'backup', 'other'
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Status
    status: Mapped[str] = mapped_column(String, nullable=False, default="completed") # 'pending', 'in_progress', 'completed', 'failed'
    
    # Changes made
    changes_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    files_affected: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Automation
    automated: Mapped[bool] = mapped_column(Boolean, default=False)
    scheduled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # User tracking
    performed_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", name="fk_website_maintenance_log_performed_by_id"), nullable=True)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")
    project: Mapped["WebsiteProject"] = relationship("WebsiteProject", back_populates="maintenance_logs")
    performed_by: Mapped[Optional["User"]] = relationship("User")
    
    __table_args__ = (
        Index('idx_website_maintenance_log_org_project', 'organization_id', 'project_id'),
        Index('idx_website_maintenance_log_type', 'maintenance_type'),
        Index('idx_website_maintenance_log_status', 'status'),
        Index('idx_website_maintenance_log_created', 'created_at'),
        Index('idx_website_maintenance_log_automated', 'automated'),
    )
