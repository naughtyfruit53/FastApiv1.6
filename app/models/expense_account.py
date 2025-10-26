# app/models/expense_account.py

"""
Expense Account Model for tracking and categorizing business expenses
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Numeric, Index, UniqueConstraint, Date
from sqlalchemy.orm import relationship
from datetime import datetime
from decimal import Decimal

from .base import Base


class ExpenseAccount(Base):
    """Expense Account model for categorizing and tracking business expenses"""
    __tablename__ = "expense_accounts"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Account identification
    account_code = Column(String(50), nullable=False, index=True)
    account_name = Column(String(200), nullable=False, index=True)
    
    # Category and hierarchy
    parent_account_id = Column(Integer, ForeignKey("expense_accounts.id"), nullable=True, index=True)
    category = Column(String(100), nullable=True, index=True)  # e.g., "Operating", "Administrative", "Manufacturing"
    sub_category = Column(String(100), nullable=True)
    
    # Financial details
    opening_balance = Column(Numeric(15, 2), default=0.00, nullable=False)
    current_balance = Column(Numeric(15, 2), default=0.00, nullable=False)
    budgeted_amount = Column(Numeric(15, 2), nullable=True)  # Annual or period budget
    
    # Configuration
    is_active = Column(Boolean, default=True, nullable=False)
    is_group = Column(Boolean, default=False, nullable=False)  # Group account vs leaf account
    can_post = Column(Boolean, default=True, nullable=False)  # Can post transactions to this account
    requires_approval = Column(Boolean, default=False, nullable=False)  # Expense posting requires approval
    
    # Chart of Accounts integration
    coa_account_id = Column(Integer, ForeignKey("chart_of_accounts.id"), nullable=True, index=True)
    
    # Metadata
    description = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    tags = Column(Text, nullable=True)  # Comma-separated tags for grouping/filtering
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    organization = relationship("Organization", back_populates="expense_accounts")
    parent_account = relationship("ExpenseAccount", remote_side=[id], back_populates="sub_accounts")
    sub_accounts = relationship("ExpenseAccount", back_populates="parent_account")
    coa_account = relationship("ChartOfAccounts")
    created_by_user = relationship("User", foreign_keys=[created_by])
    updated_by_user = relationship("User", foreign_keys=[updated_by])
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('organization_id', 'account_code', name='uq_org_expense_account_code'),
        Index('idx_expense_account_org_category', 'organization_id', 'category'),
        Index('idx_expense_account_org_active', 'organization_id', 'is_active'),
        {'extend_existing': True}
    )

    def __repr__(self):
        return f"<ExpenseAccount(id={self.id}, code={self.account_code}, name={self.account_name})>"
