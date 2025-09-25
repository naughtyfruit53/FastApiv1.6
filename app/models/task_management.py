# app/models/task_management.py

"""
Task Management Models for ClickUp-inspired task system
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from enum import Enum as PyEnum

from app.core.database import Base

class TaskStatus(PyEnum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    DONE = "done"
    CANCELLED = "cancelled"

class TaskPriority(PyEnum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    status = Column(Enum(TaskStatus), default=TaskStatus.TODO, nullable=False)
    priority = Column(Enum(TaskPriority), default=TaskPriority.NORMAL, nullable=False)
    
    # Dates
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    due_date = Column(DateTime, nullable=True)
    start_date = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Relations
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)  # Added for multi-company support
    task_project_id = Column(Integer, ForeignKey("task_projects.id"), nullable=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Additional fields
    estimated_hours = Column(Integer, nullable=True)  # Estimated time in hours
    actual_hours = Column(Integer, nullable=True)     # Actual time spent
    tags = Column(JSON, nullable=True)               # Array of tags
    custom_fields = Column(JSON, nullable=True)      # Custom task data
    
    # Relationships
    organization = relationship("Organization", back_populates="tasks")
    company = relationship("Company", back_populates="tasks")  # Added for multi-company support
    task_project = relationship("TaskProject", back_populates="tasks")
    project = relationship("Project", back_populates="tasks")
    creator = relationship("User", foreign_keys=[created_by], back_populates="created_tasks")
    assignee = relationship("User", foreign_keys=[assigned_to], back_populates="assigned_tasks")
    comments = relationship("TaskComment", back_populates="task", cascade="all, delete-orphan")
    attachments = relationship("TaskAttachment", back_populates="task", cascade="all, delete-orphan")
    time_logs = relationship("TaskTimeLog", back_populates="task", cascade="all, delete-orphan")
    reminders = relationship("TaskReminder", back_populates="task", cascade="all, delete-orphan")
    calendar_events = relationship("CalendarEvent", back_populates="task", cascade="all, delete-orphan")

class TaskProject(Base):
    __tablename__ = "task_projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    color = Column(String(7), nullable=True)  # Hex color code
    
    # Dates
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relations
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)  # Added for multi-company support
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    organization = relationship("Organization", back_populates="task_projects")
    company = relationship("Company", back_populates="task_projects")  # Added for multi-company support
    creator = relationship("User", back_populates="created_projects")
    tasks = relationship("Task", back_populates="task_project")
    members = relationship("TaskProjectMember", back_populates="project", cascade="all, delete-orphan")

class TaskProjectMember(Base):
    __tablename__ = "task_project_members"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("task_projects.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(String(50), default="member", nullable=False)  # member, admin, viewer
    added_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    project = relationship("TaskProject", back_populates="members")
    user = relationship("User", back_populates="project_memberships")

class TaskComment(Base):
    __tablename__ = "task_comments"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    task = relationship("Task", back_populates="comments")
    user = relationship("User", back_populates="task_comments")

class TaskAttachment(Base):
    __tablename__ = "task_attachments"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=True)
    mime_type = Column(String(100), nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    task = relationship("Task", back_populates="attachments")
    user = relationship("User", back_populates="task_attachments")

class TaskTimeLog(Base):
    __tablename__ = "task_time_logs"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    description = Column(String(255), nullable=True)
    hours = Column(Integer, nullable=False)  # Time in minutes
    logged_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    work_date = Column(DateTime, nullable=False)  # The date the work was done
    
    # Relationships
    task = relationship("Task", back_populates="time_logs")
    user = relationship("User", back_populates="time_logs")

class TaskReminder(Base):
    __tablename__ = "task_reminders"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    remind_at = Column(DateTime, nullable=False)
    message = Column(String(255), nullable=True)
    is_sent = Column(Boolean, default=False, nullable=False)
    sent_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    task = relationship("Task", back_populates="reminders")
    user = relationship("User", back_populates="task_reminders")