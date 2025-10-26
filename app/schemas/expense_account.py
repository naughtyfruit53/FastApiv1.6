# app/schemas/expense_account.py
"""
Expense Account Schemas
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


# Base schema with common fields
class ExpenseAccountBase(BaseModel):
    account_code: str = Field(..., description="Unique account code", min_length=1, max_length=50)
    account_name: str = Field(..., description="Account name", min_length=1, max_length=200)
    parent_account_id: Optional[int] = Field(None, description="Parent account ID for hierarchy")
    category: Optional[str] = Field(None, description="Account category", max_length=100)
    sub_category: Optional[str] = Field(None, description="Account sub-category", max_length=100)
    opening_balance: Decimal = Field(default=Decimal("0.00"), description="Opening balance")
    budgeted_amount: Optional[Decimal] = Field(None, description="Budgeted amount")
    is_group: bool = Field(default=False, description="Whether this is a group account")
    can_post: bool = Field(default=True, description="Can post transactions to this account")
    requires_approval: bool = Field(default=False, description="Expense posting requires approval")
    coa_account_id: Optional[int] = Field(None, description="Chart of Accounts reference")
    description: Optional[str] = Field(None, description="Account description")
    notes: Optional[str] = Field(None, description="Additional notes")
    tags: Optional[str] = Field(None, description="Comma-separated tags")


# Create schema
class ExpenseAccountCreate(ExpenseAccountBase):
    pass


# Update schema - all fields optional
class ExpenseAccountUpdate(BaseModel):
    account_name: Optional[str] = Field(None, min_length=1, max_length=200)
    parent_account_id: Optional[int] = None
    category: Optional[str] = Field(None, max_length=100)
    sub_category: Optional[str] = Field(None, max_length=100)
    opening_balance: Optional[Decimal] = None
    budgeted_amount: Optional[Decimal] = None
    is_group: Optional[bool] = None
    can_post: Optional[bool] = None
    requires_approval: Optional[bool] = None
    coa_account_id: Optional[int] = None
    description: Optional[str] = None
    notes: Optional[str] = None
    tags: Optional[str] = None
    is_active: Optional[bool] = None


# Response schema
class ExpenseAccountResponse(ExpenseAccountBase):
    id: int
    organization_id: int
    current_balance: Decimal
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    # Nested sub-accounts
    sub_accounts: List["ExpenseAccountResponse"] = []
    
    class Config:
        from_attributes = True


# List response with pagination
class ExpenseAccountList(BaseModel):
    items: List[ExpenseAccountResponse]
    total: int
    page: int
    size: int
    pages: int


# Filter schema for querying
class ExpenseAccountFilter(BaseModel):
    category: Optional[str] = None
    parent_account_id: Optional[int] = None
    is_group: Optional[bool] = None
    is_active: Optional[bool] = None
    search: Optional[str] = None  # Search in account code, name, description


# Minimal schema for use in other schemas
class ExpenseAccountMinimal(BaseModel):
    id: int
    account_code: str
    account_name: str
    category: Optional[str]
    
    class Config:
        from_attributes = True


# Update forward references
ExpenseAccountResponse.model_rebuild()
