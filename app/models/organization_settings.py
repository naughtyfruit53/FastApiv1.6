# app/models/organization_settings.py

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON, Index, UniqueConstraint, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.core.database import Base
from typing import Optional
from datetime import datetime
import enum


class VoucherCounterResetPeriod(enum.Enum):
    """Voucher counter reset period options"""
    NEVER = "never"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUALLY = "annually"

class OrganizationSettings(Base):
    """Organization-wide settings including email preferences"""
    __tablename__ = "organization_settings"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Multi-tenant field (one record per organization)
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_organization_settings_organization_id"), nullable=False, unique=True, index=True)
    
    # Email Settings
    mail_1_level_up_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Future extensibility for organization-wide settings
    auto_send_notifications: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Voucher Settings (Requirement 5)
    voucher_prefix: Mapped[Optional[str]] = mapped_column(String(5), nullable=True)  # Max 5 chars
    voucher_prefix_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Voucher Counter Reset Settings (Requirement 6)
    voucher_counter_reset_period: Mapped[VoucherCounterResetPeriod] = mapped_column(
        SQLEnum(VoucherCounterResetPeriod, values_callable=lambda enum: [e.value for e in enum]),
        default=VoucherCounterResetPeriod.ANNUALLY,
        nullable=False
    )
    
    # Voucher Format Template (Requirement 7)
    voucher_format_template_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Terms & Conditions for different voucher types (Feature 8)
    purchase_order_terms: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    purchase_voucher_terms: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    sales_order_terms: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    sales_voucher_terms: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    quotation_terms: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    proforma_invoice_terms: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    delivery_challan_terms: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    grn_terms: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    manufacturing_terms: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Custom settings (JSON for flexibility)
    custom_settings: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Added Tally config fields for org-level storage
    tally_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    tally_host: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    tally_port: Mapped[Optional[int]] = mapped_column(Integer, default=9000, nullable=True)
    tally_company_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    tally_sync_frequency: Mapped[Optional[str]] = mapped_column(String(50), default="manual", nullable=True)
    tally_last_sync: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="settings"
    )

    __table_args__ = (
        Index('idx_organization_settings_organization_id', 'organization_id'),
        Index('idx_organization_settings_mail_1_level_up', 'mail_1_level_up_enabled'),
        {'extend_existing': True}
    )


class VoucherFormatTemplate(Base):
    """Voucher format templates for PDF and email generation (Requirement 7)"""
    __tablename__ = "voucher_format_templates"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Template identification
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Template configuration (JSON with layout, styles, etc.)
    template_config: Mapped[dict] = mapped_column(JSON, nullable=False)
    
    # Preview image
    preview_image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Availability
    is_system_template: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)  # System vs custom
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    
    __table_args__ = (
        Index('idx_voucher_format_template_active', 'is_active'),
        Index('idx_voucher_format_template_system', 'is_system_template'),
        {'extend_existing': True}
    )