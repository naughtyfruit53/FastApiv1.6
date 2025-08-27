# app/schemas/erp.py
"""
ERP Core Schemas - Chart of Accounts, AP/AR, GST, and Financial Management
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Union
from datetime import datetime, date
from decimal import Decimal
from enum import Enum


class AccountTypeEnum(str, Enum):
    """Account types for Chart of Accounts"""
    ASSET = "asset"
    LIABILITY = "liability"
    EQUITY = "equity"
    INCOME = "income"
    EXPENSE = "expense"
    BANK = "bank"
    CASH = "cash"


class TaxTypeEnum(str, Enum):
    """Tax types for GST compliance"""
    CGST = "cgst"
    SGST = "sgst"
    IGST = "igst"
    CESS = "cess"
    TCS = "tcs"
    TDS = "tds"


# Chart of Accounts Schemas
class ChartOfAccountsBase(BaseModel):
    account_code: str = Field(..., description="Unique account code")
    account_name: str = Field(..., description="Account name")
    account_type: AccountTypeEnum = Field(..., description="Account type")
    parent_account_id: Optional[int] = Field(None, description="Parent account ID for hierarchy")
    is_group: bool = Field(False, description="Whether this is a group account")
    opening_balance: Decimal = Field(0.00, description="Opening balance")
    can_post: bool = Field(True, description="Can post transactions to this account")
    is_reconcilable: bool = Field(False, description="Is this account reconcilable")
    description: Optional[str] = Field(None, description="Account description")
    notes: Optional[str] = Field(None, description="Additional notes")


class ChartOfAccountsCreate(ChartOfAccountsBase):
    pass


class ChartOfAccountsUpdate(BaseModel):
    account_name: Optional[str] = None
    account_type: Optional[AccountTypeEnum] = None
    parent_account_id: Optional[int] = None
    is_group: Optional[bool] = None
    opening_balance: Optional[Decimal] = None
    can_post: Optional[bool] = None
    is_reconcilable: Optional[bool] = None
    description: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class ChartOfAccountsResponse(ChartOfAccountsBase):
    id: int
    organization_id: int
    level: int
    current_balance: Decimal
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    # Hierarchy information
    sub_accounts: List["ChartOfAccountsResponse"] = []
    
    class Config:
        from_attributes = True


# GST Configuration Schemas
class GSTConfigurationBase(BaseModel):
    gstin: str = Field(..., description="GST Identification Number")
    trade_name: str = Field(..., description="Trade name")
    legal_name: str = Field(..., description="Legal name")
    registration_date: date = Field(..., description="GST registration date")
    constitution: str = Field(..., description="Constitution type")
    business_type: str = Field(..., description="Business type")
    address_line1: str = Field(..., description="Address line 1")
    address_line2: Optional[str] = Field(None, description="Address line 2")
    city: str = Field(..., description="City")
    state: str = Field(..., description="State")
    pincode: str = Field(..., description="Pincode")
    is_composition_scheme: bool = Field(False, description="Is composition scheme dealer")
    composition_tax_rate: Optional[Decimal] = Field(None, description="Composition tax rate")


class GSTConfigurationCreate(GSTConfigurationBase):
    pass


class GSTConfigurationUpdate(BaseModel):
    trade_name: Optional[str] = None
    legal_name: Optional[str] = None
    registration_date: Optional[date] = None
    constitution: Optional[str] = None
    business_type: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    is_composition_scheme: Optional[bool] = None
    composition_tax_rate: Optional[Decimal] = None
    is_active: Optional[bool] = None


class GSTConfigurationResponse(GSTConfigurationBase):
    id: int
    organization_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Tax Code Schemas
class TaxCodeBase(BaseModel):
    tax_code: str = Field(..., description="Tax code")
    tax_name: str = Field(..., description="Tax name")
    tax_type: TaxTypeEnum = Field(..., description="Tax type")
    tax_rate: Decimal = Field(..., description="Tax rate percentage")
    is_inclusive: bool = Field(False, description="Is tax inclusive")
    hsn_sac_code: Optional[str] = Field(None, description="HSN/SAC code")
    description: Optional[str] = Field(None, description="Description")
    is_default: bool = Field(False, description="Is default tax code")
    tax_payable_account_id: Optional[int] = Field(None, description="Tax payable account ID")
    tax_input_account_id: Optional[int] = Field(None, description="Tax input account ID")


class TaxCodeCreate(TaxCodeBase):
    gst_configuration_id: Optional[int] = Field(None, description="GST configuration ID")


class TaxCodeUpdate(BaseModel):
    tax_name: Optional[str] = None
    tax_type: Optional[TaxTypeEnum] = None
    tax_rate: Optional[Decimal] = None
    is_inclusive: Optional[bool] = None
    hsn_sac_code: Optional[str] = None
    description: Optional[str] = None
    is_default: Optional[bool] = None
    tax_payable_account_id: Optional[int] = None
    tax_input_account_id: Optional[int] = None
    is_active: Optional[bool] = None


class TaxCodeResponse(TaxCodeBase):
    id: int
    organization_id: int
    gst_configuration_id: Optional[int]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Journal Entry Schemas
class JournalEntryBase(BaseModel):
    account_id: int = Field(..., description="Account ID")
    entry_number: str = Field(..., description="Entry number")
    entry_date: date = Field(..., description="Entry date")
    reference_type: Optional[str] = Field(None, description="Reference type")
    reference_id: Optional[int] = Field(None, description="Reference ID")
    reference_number: Optional[str] = Field(None, description="Reference number")
    debit_amount: Decimal = Field(0.00, description="Debit amount")
    credit_amount: Decimal = Field(0.00, description="Credit amount")
    description: Optional[str] = Field(None, description="Description")
    notes: Optional[str] = Field(None, description="Notes")


class JournalEntryCreate(JournalEntryBase):
    pass


class JournalEntryUpdate(BaseModel):
    account_id: Optional[int] = None
    entry_date: Optional[date] = None
    reference_type: Optional[str] = None
    reference_id: Optional[int] = None
    reference_number: Optional[str] = None
    debit_amount: Optional[Decimal] = None
    credit_amount: Optional[Decimal] = None
    description: Optional[str] = None
    notes: Optional[str] = None
    is_reconciled: Optional[bool] = None


class JournalEntryResponse(JournalEntryBase):
    id: int
    organization_id: int
    is_reconciled: bool
    reconciled_date: Optional[date]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Accounts Payable Schemas
class AccountsPayableBase(BaseModel):
    vendor_id: int = Field(..., description="Vendor ID")
    bill_number: str = Field(..., description="Bill number")
    bill_date: date = Field(..., description="Bill date")
    due_date: date = Field(..., description="Due date")
    bill_amount: Decimal = Field(..., description="Bill amount")
    tax_amount: Decimal = Field(0.00, description="Tax amount")
    reference_type: Optional[str] = Field(None, description="Reference type")
    reference_id: Optional[int] = Field(None, description="Reference ID")
    notes: Optional[str] = Field(None, description="Notes")


class AccountsPayableCreate(AccountsPayableBase):
    pass


class AccountsPayableUpdate(BaseModel):
    bill_date: Optional[date] = None
    due_date: Optional[date] = None
    bill_amount: Optional[Decimal] = None
    tax_amount: Optional[Decimal] = None
    reference_type: Optional[str] = None
    reference_id: Optional[int] = None
    notes: Optional[str] = None
    payment_status: Optional[str] = None


class AccountsPayableResponse(AccountsPayableBase):
    id: int
    organization_id: int
    paid_amount: Decimal
    outstanding_amount: Decimal
    payment_status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Accounts Receivable Schemas
class AccountsReceivableBase(BaseModel):
    customer_id: int = Field(..., description="Customer ID")
    invoice_number: str = Field(..., description="Invoice number")
    invoice_date: date = Field(..., description="Invoice date")
    due_date: date = Field(..., description="Due date")
    invoice_amount: Decimal = Field(..., description="Invoice amount")
    tax_amount: Decimal = Field(0.00, description="Tax amount")
    reference_type: Optional[str] = Field(None, description="Reference type")
    reference_id: Optional[int] = Field(None, description="Reference ID")
    notes: Optional[str] = Field(None, description="Notes")


class AccountsReceivableCreate(AccountsReceivableBase):
    pass


class AccountsReceivableUpdate(BaseModel):
    invoice_date: Optional[date] = None
    due_date: Optional[date] = None
    invoice_amount: Optional[Decimal] = None
    tax_amount: Optional[Decimal] = None
    reference_type: Optional[str] = None
    reference_id: Optional[int] = None
    notes: Optional[str] = None
    payment_status: Optional[str] = None


class AccountsReceivableResponse(AccountsReceivableBase):
    id: int
    organization_id: int
    received_amount: Decimal
    outstanding_amount: Decimal
    payment_status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Payment Record Schemas
class PaymentRecordBase(BaseModel):
    payment_number: str = Field(..., description="Payment number")
    payment_date: date = Field(..., description="Payment date")
    payment_amount: Decimal = Field(..., description="Payment amount")
    payment_method: str = Field(..., description="Payment method")
    accounts_payable_id: Optional[int] = Field(None, description="Accounts payable ID")
    accounts_receivable_id: Optional[int] = Field(None, description="Accounts receivable ID")
    bank_account: Optional[str] = Field(None, description="Bank account")
    cheque_number: Optional[str] = Field(None, description="Cheque number")
    transaction_reference: Optional[str] = Field(None, description="Transaction reference")
    notes: Optional[str] = Field(None, description="Notes")


class PaymentRecordCreate(PaymentRecordBase):
    pass


class PaymentRecordUpdate(BaseModel):
    payment_date: Optional[date] = None
    payment_amount: Optional[Decimal] = None
    payment_method: Optional[str] = None
    bank_account: Optional[str] = None
    cheque_number: Optional[str] = None
    transaction_reference: Optional[str] = None
    notes: Optional[str] = None


class PaymentRecordResponse(PaymentRecordBase):
    id: int
    organization_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Financial Reports Schemas
class TrialBalanceItem(BaseModel):
    account_code: str
    account_name: str
    debit_balance: Decimal
    credit_balance: Decimal


class TrialBalanceResponse(BaseModel):
    trial_balance: List[TrialBalanceItem]
    total_debits: Decimal
    total_credits: Decimal
    as_of_date: date
    organization_id: int


class ProfitAndLossItem(BaseModel):
    account_code: str
    account_name: str
    amount: Decimal


class ProfitAndLossResponse(BaseModel):
    income: List[ProfitAndLossItem]
    expenses: List[ProfitAndLossItem]
    total_income: Decimal
    total_expenses: Decimal
    net_profit_loss: Decimal
    from_date: date
    to_date: date
    organization_id: int


class BalanceSheetItem(BaseModel):
    account_code: str
    account_name: str
    amount: Decimal


class BalanceSheetResponse(BaseModel):
    assets: List[BalanceSheetItem]
    liabilities: List[BalanceSheetItem]
    equity: List[BalanceSheetItem]
    total_assets: Decimal
    total_liabilities: Decimal
    total_equity: Decimal
    as_of_date: date
    organization_id: int


# Update forward references
ChartOfAccountsResponse.model_rebuild()