# app/models/project_models.py

"""
Enhanced Project Management Models for comprehensive project lifecycle management
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum, JSON, Float, Date, Index, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, date
from enum import Enum as PyEnum
from decimal import Decimal

from app.core.database import Base


class ProjectStatus(PyEnum):
    PLANNING = "planning"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ProjectPriority(PyEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ProjectType(PyEnum):
    INTERNAL = "internal"
    CLIENT = "client"
    RESEARCH = "research"
    MAINTENANCE = "maintenance"
    DEVELOPMENT = "development"


class MilestoneStatus(PyEnum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DELAYED = "delayed"


class ResourceType(PyEnum):
    HUMAN = "human"
    EQUIPMENT = "equipment"
    MATERIAL = "material"
    BUDGET = "budget"


class Project(Base):
    """Enhanced Project model for comprehensive project management"""
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    
    # Multi-tenant fields
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True, index=True)
    
    # Project identification
    project_code = Column(String(50), nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Project classification
    project_type = Column(Enum(ProjectType), default=ProjectType.INTERNAL, nullable=False)
    status = Column(Enum(ProjectStatus), default=ProjectStatus.PLANNING, nullable=False)
    priority = Column(Enum(ProjectPriority), default=ProjectPriority.MEDIUM, nullable=False)
    
    # Timeline
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    planned_start_date = Column(Date, nullable=True)
    planned_end_date = Column(Date, nullable=True)
    
    # Financial
    budget = Column(Float, nullable=True, default=0.0)
    actual_cost = Column(Float, nullable=True, default=0.0)
    
    # Progress tracking
    progress_percentage = Column(Float, default=0.0, nullable=False)
    
    # Relationships
    client_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    project_manager_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Additional settings
    is_billable = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    tags = Column(JSON, nullable=True)  # Flexible tagging system
    custom_fields = Column(JSON, nullable=True)  # Custom project fields
    
    # Relationships
    organization = relationship("Organization", back_populates="projects")
    company = relationship("Company", back_populates="projects")
    client = relationship("Customer")
    project_manager = relationship("User", foreign_keys=[project_manager_id])
    creator = relationship("User", foreign_keys=[created_by])
    
    milestones = relationship("ProjectMilestone", back_populates="project", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")
    resources = relationship("ProjectResource", back_populates="project", cascade="all, delete-orphan")
    documents = relationship("ProjectDocument", back_populates="project", cascade="all, delete-orphan")
    time_logs = relationship("ProjectTimeLog", back_populates="project", cascade="all, delete-orphan")
    
    __table_args__ = (
        UniqueConstraint('organization_id', 'project_code', name='uq_project_org_code'),
        Index('idx_project_org_status', 'organization_id', 'status'),
        Index('idx_project_org_type', 'organization_id', 'project_type'),
        Index('idx_project_org_manager', 'organization_id', 'project_manager_id'),
        Index('idx_project_org_client', 'organization_id', 'client_id'),
    )


class ProjectMilestone(Base):
    """Project milestones for tracking major deliverables"""
    __tablename__ = "project_milestones"

    id = Column(Integer, primary_key=True, index=True)
    
    # Multi-tenant fields
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    
    # Milestone details
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(MilestoneStatus), default=MilestoneStatus.NOT_STARTED, nullable=False)
    
    # Timeline
    target_date = Column(Date, nullable=False)
    completion_date = Column(Date, nullable=True)
    
    # Progress
    progress_percentage = Column(Float, default=0.0, nullable=False)
    
    # Dependencies
    dependencies = Column(JSON, nullable=True)  # List of milestone IDs this depends on
    
    # Assignment
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    project = relationship("Project", back_populates="milestones")
    assignee = relationship("User", foreign_keys=[assigned_to])
    creator = relationship("User", foreign_keys=[created_by])
    
    __table_args__ = (
        Index('idx_milestone_org_project', 'organization_id', 'project_id'),
        Index('idx_milestone_org_status', 'organization_id', 'status'),
        Index('idx_milestone_org_target_date', 'organization_id', 'target_date'),
    )


class ProjectResource(Base):
    """Project resource allocation and tracking"""
    __tablename__ = "project_resources"

    id = Column(Integer, primary_key=True, index=True)
    
    # Multi-tenant fields
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    
    # Resource details
    resource_type = Column(Enum(ResourceType), nullable=False)
    resource_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Allocation
    allocated_quantity = Column(Float, nullable=False, default=1.0)
    used_quantity = Column(Float, nullable=False, default=0.0)
    unit = Column(String(50), nullable=True)  # hours, pieces, kg, etc.
    
    # Cost tracking
    unit_cost = Column(Float, nullable=True, default=0.0)
    total_cost = Column(Float, nullable=True, default=0.0)
    
    # Timeline
    allocation_start = Column(Date, nullable=True)
    allocation_end = Column(Date, nullable=True)
    
    # Resource reference (for human resources)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    project = relationship("Project", back_populates="resources")
    user = relationship("User", foreign_keys=[user_id])
    creator = relationship("User", foreign_keys=[created_by])
    
    __table_args__ = (
        Index('idx_resource_org_project', 'organization_id', 'project_id'),
        Index('idx_resource_org_type', 'organization_id', 'resource_type'),
        Index('idx_resource_org_user', 'organization_id', 'user_id'),
    )


class ProjectDocument(Base):
    """Project document management"""
    __tablename__ = "project_documents"

    id = Column(Integer, primary_key=True, index=True)
    
    # Multi-tenant fields
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    
    # Document details
    document_name = Column(String(255), nullable=False)
    document_type = Column(String(100), nullable=True)  # contract, requirement, design, etc.
    file_path = Column(String(500), nullable=True)
    file_size = Column(Integer, nullable=True)
    mime_type = Column(String(100), nullable=True)
    
    # Document metadata
    version = Column(String(20), default="1.0")
    description = Column(Text, nullable=True)
    tags = Column(JSON, nullable=True)
    
    # Access control
    is_public = Column(Boolean, default=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    project = relationship("Project", back_populates="documents")
    uploader = relationship("User")
    
    __table_args__ = (
        Index('idx_document_org_project', 'organization_id', 'project_id'),
        Index('idx_document_org_type', 'organization_id', 'document_type'),
        Index('idx_document_org_public', 'organization_id', 'is_public'),
    )


class ProjectTimeLog(Base):
    """Time tracking for project work"""
    __tablename__ = "project_time_logs"

    id = Column(Integer, primary_key=True, index=True)
    
    # Multi-tenant fields
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    
    # Time tracking
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)  # Optional task association
    
    # Time details
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    duration_minutes = Column(Integer, nullable=True)  # Calculated or manual entry
    
    # Work description
    description = Column(Text, nullable=False)
    work_type = Column(String(100), nullable=True)  # development, testing, meeting, etc.
    
    # Billing
    is_billable = Column(Boolean, default=True)
    hourly_rate = Column(Float, nullable=True)
    billable_amount = Column(Float, nullable=True)
    
    # Approval
    is_approved = Column(Boolean, default=False)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    project = relationship("Project", back_populates="time_logs")
    user = relationship("User", foreign_keys=[user_id])
    task = relationship("Task")
    approver = relationship("User", foreign_keys=[approved_by])
    
    __table_args__ = (
        Index('idx_timelog_org_project', 'organization_id', 'project_id'),
        Index('idx_timelog_org_user', 'organization_id', 'user_id'),
        Index('idx_timelog_org_date', 'organization_id', 'start_time'),
        Index('idx_timelog_org_billable', 'organization_id', 'is_billable'),
    )