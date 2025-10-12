# app/models/rbac_models.py

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
from datetime import datetime

class ServicePermission(Base):
    """Service CRM permissions"""
    __tablename__ = "service_permissions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    display_name = Column(String(100), nullable=False)
    description = Column(String(200), nullable=True)
    module = Column(String(50), nullable=False, index=True)
    action = Column(String(50), nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    roles = relationship("ServiceRolePermission", back_populates="permission")

    __table_args__ = (
        UniqueConstraint('module', 'action', name='uq_service_permission_module_action'),
        Index('idx_service_permission_module', 'module'),
    )

class ServiceRole(Base):
    """Service CRM roles"""
    __tablename__ = "service_roles"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False, index=True)
    display_name = Column(String(100), nullable=False)
    description = Column(String(200), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    organization = relationship("Organization", back_populates="service_roles")
    permissions = relationship("ServiceRolePermission", back_populates="role")
    users = relationship("UserServiceRole", back_populates="role")

    __table_args__ = (
        UniqueConstraint('organization_id', 'name', name='uq_service_role_org_name'),
        Index('idx_service_role_org_active', 'organization_id', 'is_active'),
    )

class ServiceRolePermission(Base):
    """Mapping between service roles and permissions"""
    __tablename__ = "service_role_permissions"

    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey("service_roles.id"), nullable=False, index=True)
    permission_id = Column(Integer, ForeignKey("service_permissions.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    role = relationship("ServiceRole", back_populates="permissions")
    permission = relationship("ServicePermission", back_populates="roles")

    __table_args__ = (
        UniqueConstraint('role_id', 'permission_id', name='uq_role_permission'),
    )

class UserServiceRole(Base):
    """Mapping between users and service roles"""
    __tablename__ = "user_service_roles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    role_id = Column(Integer, ForeignKey("service_roles.id"), nullable=False, index=True)
    assigned_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="service_roles")
    role = relationship("ServiceRole", back_populates="users")
    assigned_by = relationship("User", foreign_keys=[assigned_by_id])

    __table_args__ = (
        UniqueConstraint('user_id', 'role_id', name='uq_user_service_role'),
        Index('idx_user_service_role_active', 'user_id', 'is_active'),
    )