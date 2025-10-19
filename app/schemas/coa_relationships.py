# app/schemas/coa_relationships.py
"""
Enhanced schemas showing Chart of Accounts relationships with entities
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.schemas.erp import ChartOfAccountMinimal
from app.schemas.base import CustomerInDB, VendorInDB


class CustomerWithCOA(CustomerInDB):
    """Customer schema with Chart of Accounts relationship"""
    receivable_account: Optional[ChartOfAccountMinimal] = None


class VendorWithCOA(VendorInDB):
    """Vendor schema with Chart of Accounts relationship"""
    payable_account: Optional[ChartOfAccountMinimal] = None


class FreightRateWithCOA(BaseModel):
    """Freight Rate schema with Chart of Accounts relationship"""
    id: int
    organization_id: int
    rate_code: str
    freight_mode: str
    rate_basis: str
    freight_expense_account_id: Optional[int] = None
    freight_expense_account: Optional[ChartOfAccountMinimal] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class COAEntityLink(BaseModel):
    """Represents a link from COA to an entity using that account"""
    entity_type: str  # "Customer", "Vendor", "FreightRate", etc.
    entity_id: int
    entity_name: str
    link_type: str  # "receivable", "payable", "expense", etc.
    
    class Config:
        from_attributes = True


class ChartOfAccountsWithEntities(BaseModel):
    """Chart of Accounts with reverse links to entities"""
    id: int
    organization_id: int
    account_code: str
    account_name: str
    account_type: str
    current_balance: float
    is_active: bool
    
    # Reverse links to entities using this account
    linked_entities: list[COAEntityLink] = []
    
    class Config:
        from_attributes = True
