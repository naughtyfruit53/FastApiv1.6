# app/models/entitlement_models.py

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Numeric, Index, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB
from app.core.database import Base
from typing import Optional, List
from datetime import datetime
import enum


class ModuleStatusEnum(enum.Enum):
    """Module entitlement status"""
    ENABLED = "enabled"
    DISABLED = "disabled"
    TRIAL = "trial"


class Module(Base):
    """Module taxonomy - top-level features like sales, inventory, manufacturing"""
    __tablename__ = "modules"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    module_key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    display_name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    icon: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    submodules: Mapped[List["Submodule"]] = relationship("Submodule", back_populates="module", cascade="all, delete-orphan")
    org_entitlements: Mapped[List["OrgEntitlement"]] = relationship("OrgEntitlement", back_populates="module", cascade="all, delete-orphan")
    plan_entitlements: Mapped[List["PlanEntitlement"]] = relationship("PlanEntitlement", back_populates="module", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_modules_key', 'module_key'),
        Index('idx_modules_active', 'is_active'),
    )


class Submodule(Base):
    """Submodule taxonomy - fine-grained features within modules"""
    __tablename__ = "submodules"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    module_id: Mapped[int] = mapped_column(Integer, ForeignKey("modules.id", ondelete="CASCADE"), nullable=False, index=True)
    submodule_key: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    display_name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    menu_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    permission_key: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    module: Mapped["Module"] = relationship("Module", back_populates="submodules")
    org_subentitlements: Mapped[List["OrgSubentitlement"]] = relationship("OrgSubentitlement", back_populates="submodule", cascade="all, delete-orphan")
    plan_entitlements: Mapped[List["PlanEntitlement"]] = relationship("PlanEntitlement", back_populates="submodule", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint('module_id', 'submodule_key', name='uq_submodules_module_submodule'),
        Index('idx_submodules_module', 'module_id'),
        Index('idx_submodules_key', 'submodule_key'),
        Index('idx_submodules_active', 'is_active'),
    )


class Plan(Base):
    """License plans (e.g., Starter, Professional, Enterprise)"""
    __tablename__ = "plans"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    plan_key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    display_name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    price_monthly: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), nullable=True)
    price_annual: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    plan_entitlements: Mapped[List["PlanEntitlement"]] = relationship("PlanEntitlement", back_populates="plan", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_plans_key', 'plan_key'),
        Index('idx_plans_active', 'is_active'),
    )


class PlanEntitlement(Base):
    """Plan entitlements (which modules/submodules are included in each plan)"""
    __tablename__ = "plan_entitlements"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    plan_id: Mapped[int] = mapped_column(Integer, ForeignKey("plans.id", ondelete="CASCADE"), nullable=False, index=True)
    module_id: Mapped[int] = mapped_column(Integer, ForeignKey("modules.id", ondelete="CASCADE"), nullable=False, index=True)
    submodule_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("submodules.id", ondelete="CASCADE"), nullable=True, index=True)
    is_included: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    plan: Mapped["Plan"] = relationship("Plan", back_populates="plan_entitlements")
    module: Mapped["Module"] = relationship("Module", back_populates="plan_entitlements")
    submodule: Mapped[Optional["Submodule"]] = relationship("Submodule", back_populates="plan_entitlements")

    __table_args__ = (
        UniqueConstraint('plan_id', 'module_id', 'submodule_id', name='uq_plan_entitlements'),
        Index('idx_plan_entitlements_plan', 'plan_id'),
        Index('idx_plan_entitlements_module', 'module_id'),
        Index('idx_plan_entitlements_submodule', 'submodule_id'),
    )


class OrgEntitlement(Base):
    """Organization-level module entitlements"""
    __tablename__ = "org_entitlements"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    org_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    module_id: Mapped[int] = mapped_column(Integer, ForeignKey("modules.id", ondelete="CASCADE"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), default="disabled", nullable=False)
    trial_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    source: Mapped[str] = mapped_column(String(100), default="manual", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization", back_populates="org_entitlements")
    module: Mapped["Module"] = relationship("Module", back_populates="org_entitlements")
    subentitlements: Mapped[List["OrgSubentitlement"]] = relationship("OrgSubentitlement", back_populates="org_entitlement", cascade="all, delete-orphan", foreign_keys="[OrgSubentitlement.org_id, OrgSubentitlement.module_id]")

    __table_args__ = (
        UniqueConstraint('org_id', 'module_id', name='uq_org_entitlements_org_module'),
        CheckConstraint("status IN ('enabled', 'disabled', 'trial')", name='ck_org_entitlements_status'),
        Index('idx_org_entitlements_org', 'org_id'),
        Index('idx_org_entitlements_module', 'module_id'),
        Index('idx_org_entitlements_org_module', 'org_id', 'module_id'),
        Index('idx_org_entitlements_status', 'status'),
    )


class OrgSubentitlement(Base):
    """Organization-level submodule entitlements (fine-grained control)"""
    __tablename__ = "org_subentitlements"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    org_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    module_id: Mapped[int] = mapped_column(Integer, ForeignKey("modules.id", ondelete="CASCADE"), nullable=False, index=True)
    submodule_id: Mapped[int] = mapped_column(Integer, ForeignKey("submodules.id", ondelete="CASCADE"), nullable=False, index=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    source: Mapped[str] = mapped_column(String(100), default="manual", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization", back_populates="org_subentitlements")
    module: Mapped["Module"] = relationship("Module")
    submodule: Mapped["Submodule"] = relationship("Submodule", back_populates="org_subentitlements")
    org_entitlement: Mapped["OrgEntitlement"] = relationship("OrgEntitlement", back_populates="subentitlements", foreign_keys=[org_id, module_id])

    __table_args__ = (
        UniqueConstraint('org_id', 'module_id', 'submodule_id', name='uq_org_subentitlements'),
        Index('idx_org_subentitlements_org', 'org_id'),
        Index('idx_org_subentitlements_module', 'module_id'),
        Index('idx_org_subentitlements_submodule', 'submodule_id'),
        Index('idx_org_subentitlements_org_module', 'org_id', 'module_id'),
        Index('idx_org_subentitlements_org_module_sub', 'org_id', 'module_id', 'submodule_id'),
    )


class EntitlementEvent(Base):
    """Entitlement audit/event log"""
    __tablename__ = "entitlement_events"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    org_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    actor_user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    payload: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization", back_populates="entitlement_events")
    actor: Mapped[Optional["User"]] = relationship("User", foreign_keys=[actor_user_id])

    __table_args__ = (
        Index('idx_entitlement_events_org', 'org_id'),
        Index('idx_entitlement_events_type', 'event_type'),
        Index('idx_entitlement_events_actor', 'actor_user_id'),
        Index('idx_entitlement_events_created', 'created_at'),
    )
