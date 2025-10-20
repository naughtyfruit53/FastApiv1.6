# app/models/ledger.py

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean, UniqueConstraint, Index, Date, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
from typing import Optional, List
from datetime import datetime

class LedgerEntry(Base):
    __tablename__ = "ledger_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Multi-tenant field
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Entry details
    date = Column(Date, nullable=False, index=True)
    voucher_type = Column(String, nullable=False, index=True)
    voucher_number = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    debit_amount = Column(Numeric(15, 2), default=0.00, nullable=False)
    credit_amount = Column(Numeric(15, 2), default=0.00, nullable=False)
    balance = Column(Numeric(15, 2), nullable=False)
    
    # Account reference
    account_type = Column(String, nullable=False)  # vendor, customer
    account_id = Column(Integer, nullable=False, index=True)
    account_name = Column(String, nullable=False)
    
    # Reference to source document
    source_document_type = Column(String, nullable=True)
    source_document_id = Column(Integer, nullable=True)
    
    # Status
    status = Column(String, default="posted", nullable=False)
    
    # Metadata
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    organization = relationship("Organization", back_populates="ledger_entries")
    created_by_user = relationship("User", foreign_keys=[created_by])
    
    __table_args__ = (
        UniqueConstraint('organization_id', 'voucher_type', 'voucher_number', name='uq_ledger_org_voucher'),
        Index('idx_ledger_org_account', 'organization_id', 'account_type', 'account_id'),
        Index('idx_ledger_org_date', 'organization_id', 'date'),
        {'extend_existing': True}
    )

class LedgerSummary(Base):
    __tablename__ = "ledger_summaries"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Multi-tenant field
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Summary period
    summary_date = Column(Date, nullable=False, index=True)
    period_type = Column(String, default="daily", nullable=False)  # daily, weekly, monthly
    
    # Account summary
    total_debit = Column(Numeric(15, 2), default=0.00, nullable=False)
    total_credit = Column(Numeric(15, 2), default=0.00, nullable=False)
    net_balance = Column(Numeric(15, 2), default=0.00, nullable=False)
    transaction_count = Column(Integer, default=0, nullable=False)
    
    # Metadata
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    organization = relationship("Organization", back_populates="ledger_summaries")
    
    __table_args__ = (
        UniqueConstraint('organization_id', 'summary_date', 'period_type', name='uq_ledger_summary_org_date_period'),
        {'extend_existing': True}
    )