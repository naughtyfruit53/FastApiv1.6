# app/models/rbac_models.py

"""
RBAC Models
Defines models for Role-Based Access Control
"""

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, JSON, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from typing import Optional
from datetime import datetime

from app.models.base import Base
from app.models.user_models import User
from app.models.entitlement_models import Module, Submodule

class Role(Base):
    """System roles"""
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    role_key = Column(String(50), unique=True, index=True, nullable=False)
    display_name = Column(String(100), nullable=False)
    description = Column(String(255))
    hierarchy_level = Column(Integer, default=0)  # For role hierarchy
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)  # For auto-assignment
    permissions = Column(JSON, default=list)  # List of permission strings
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    users = relationship("User", primaryjoin="Role.id == User.role_id", back_populates="role_obj")


class Permission(Base):
    """System permissions"""
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    permission_key = Column(String(100), unique=True, index=True, nullable=False)  # e.g., 'crm.read'
    display_name = Column(String(100), nullable=False)
    description = Column(String(255))
    module_id = Column(Integer, ForeignKey('modules.id'), nullable=True)
    submodule_id = Column(Integer, ForeignKey('submodules.id'), nullable=True)
    category = Column(String(50))  # e.g., 'read', 'write', 'admin'
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    module = relationship("Module", back_populates="permissions")
    submodule = relationship("Submodule", back_populates="permissions")


class UserPermission(Base):
    """Direct user permissions (overrides role permissions)"""
    __tablename__ = "user_permissions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    permission_id = Column(Integer, ForeignKey('permissions.id'), nullable=False)
    granted = Column(Boolean, default=True)  # True: granted, False: denied
    granted_by = Column(Integer, ForeignKey('users.id'))  # Admin who granted/denied
    granted_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)  # For temporary permissions
    reason = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)

    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="direct_permissions")
    permission = relationship("Permission")
    granted_by_user = relationship("User", foreign_keys=[granted_by])


class RolePermission(Base):
    """Role to permission mapping"""
    __tablename__ = "role_permissions"

    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey('roles.id'), nullable=False)
    permission_id = Column(Integer, ForeignKey('permissions.id'), nullable=False)
    granted_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # Relationships
    role = relationship("Role", back_populates="role_permissions")
    permission = relationship("Permission")


class PermissionAudit(Base):
    """Audit log for permission changes"""
    __tablename__ = "permission_audits"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    changed_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    action = Column(Enum('grant', 'revoke', 'modify', name='permission_action'), nullable=False)
    permission_key = Column(String(100), nullable=False)
    details = Column(JSON, default=dict)
    timestamp = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)

    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    changer = relationship("User", foreign_keys=[changed_by])

class UserModulePermission(Base):
    """User module permissions"""
    __tablename__ = "user_module_permissions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    module_id = Column(Integer, ForeignKey('modules.id'), nullable=False)
    has_access = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    user = relationship("User")
    module = relationship("Module")


class RoleModulePermission(Base):
    """Role module permissions"""
    __tablename__ = "role_module_permissions"

    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey('roles.id'), nullable=False)
    module_id = Column(Integer, ForeignKey('modules.id'), nullable=False)
    has_access = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    role = relationship("Role")
    module = relationship("Module")


# Relationships in base models
User.direct_permissions = relationship("UserPermission", foreign_keys="UserPermission.user_id", back_populates="user")
Role.role_permissions = relationship("RolePermission", back_populates="role")
Module.permissions = relationship("Permission", back_populates="module")
Submodule.permissions = relationship("Permission", back_populates="submodule")

class ServiceRole(Base):
    __tablename__ = "service_roles"

    id = Column(Integer, primary_key=True, index=True)
    role_key = Column(String(50), unique=True, index=True, nullable=False)
    display_name = Column(String(100), nullable=False)
    description = Column(String(255))
    hierarchy_level = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    permissions = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=False)

    organization = relationship("Organization", back_populates="service_roles")

class ServicePermission(Base):
    __tablename__ = "service_permissions"

    id = Column(Integer, primary_key=True, index=True)
    permission_key = Column(String(100), unique=True, index=True, nullable=False)
    display_name = Column(String(100), nullable=False)
    description = Column(String(255))
    category = Column(String(50))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ServiceRolePermission(Base):
    __tablename__ = "service_role_permissions"

    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey('service_roles.id'), nullable=False)
    permission_id = Column(Integer, ForeignKey('service_permissions.id'), nullable=False)
    granted_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    role = relationship("ServiceRole")
    permission = relationship("ServicePermission")

class UserServiceRole(Base):
    __tablename__ = "user_service_roles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    service_role_id = Column(Integer, ForeignKey('service_roles.id'), nullable=False)
    assigned_at = Column(DateTime, default=datetime.utcnow)
    assigned_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    is_active = Column(Boolean, default=True)

    user = relationship("User", foreign_keys=[user_id])
    service_role = relationship("ServiceRole")
    assigned_by_user = relationship("User", foreign_keys=[assigned_by])