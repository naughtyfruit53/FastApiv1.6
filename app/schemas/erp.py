# app/schemas/erp.py
"""
ERP Core Schemas - Chart of Accounts, AP/AR, GST, and Financial Management
"""

from pydantic import BaseModel, Field, validator, SkipValidation
from typing import Optional, List, Union
from datetime import datetime, date  # Added date import
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
    
    sub_accounts: List["ChartOfAccountsResponse"] = []
    
    class Config:
        from_attributes = True

# GST Configuration Schemas
class GSTConfigurationBase(BaseModel):
    gstin: str = Field(..., description="GST Identification Number")
    trade_name: str = Field(..., description="Trade name")
    legal_name: str = Field(..., description="Legal name")
    registration_date: SkipValidation[date] = Field(..., description="GST registration date")
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
    registration_date: Optional[SkipValidation[date]] = None
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
    entry_date: SkipValidation[date] = Field(..., description="Entry date")
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
    entry_date: Optional[SkipValidation[date]] = None
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
    reconciled_date: Optional[SkipValidation[date]]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Accounts Payable Schemas
class AccountsPayableBase(BaseModel):
    vendor_id: int = Field(..., description="Vendor ID")
    bill_number: str = Field(..., description="Bill number")
    bill_date: SkipValidation[date] = Field(..., description="Bill date")
    due_date: SkipValidation[date] = Field(..., description="Due date")
    bill_amount: Decimal = Field(..., description="Bill amount")
    tax_amount: Decimal = Field(0.00, description="Tax amount")
    reference_type: Optional[str] = Field(None, description="Reference type")
    reference_id: Optional[int] = Field(None, description="Reference ID")
    notes: Optional[str] = Field(None, description="Notes")

class AccountsPayableCreate(AccountsPayableBase):
    pass

class AccountsPayableUpdate(BaseModel):
    bill_date: Optional[SkipValidation[date]] = None
    due_date: Optional[SkipValidation[date]] = None
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
    invoice_date: SkipValidation[date] = Field(..., description="Invoice date")
    due_date: SkipValidation[date] = Field(..., description="Due date")
    invoice_amount: Decimal = Field(..., description="Invoice amount")
    tax_amount: Decimal = Field(0.00, description="Tax amount")
    reference_type: Optional[str] = Field(None, description="Reference type")
    reference_id: Optional[int] = Field(None, description="Reference ID")
    notes: Optional[str] = Field(None, description="Notes")

class AccountsReceivableCreate(AccountsReceivableBase):
    pass

class AccountsReceivableUpdate(BaseModel):
    invoice_date: Optional[SkipValidation[date]] = None
    due_date: Optional[SkipValidation[date]] = None
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
    payment_date: SkipValidation[date] = Field(..., description="Payment date")
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
    payment_date: Optional[SkipValidation[date]] = None
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
    as_of_date: SkipValidation[date]
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
    from_date: SkipValidation[date]
    to_date: SkipValidation[date]
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
    as_of_date: SkipValidation[date]
    organization_id: int

# Update forward references
ChartOfAccountsResponse.model_rebuild()

# General Ledger Schemas
class GeneralLedgerBase(BaseModel):
    account_id: int = Field(..., description="Account ID")
    transaction_date: SkipValidation[date] = Field(..., description="Transaction date")
    transaction_number: str = Field(..., description="Transaction number")
    reference_type: Optional[str] = Field(None, description="Reference type")
    reference_id: Optional[int] = Field(None, description="Reference ID")
    reference_number: Optional[str] = Field(None, description="Reference number")
    debit_amount: Decimal = Field(0.00, description="Debit amount")
    credit_amount: Decimal = Field(0.00, description="Credit amount")
    description: Optional[str] = Field(None, description="Description")
    narration: Optional[str] = Field(None, description="Narration")
    cost_center_id: Optional[int] = Field(None, description="Cost center ID")

class GeneralLedgerCreate(GeneralLedgerBase):
    pass

class GeneralLedgerUpdate(BaseModel):
    transaction_date: Optional[SkipValidation[date]] = None
    description: Optional[str] = None
    narration: Optional[str] = None
    cost_center_id: Optional[int] = None
    is_reconciled: Optional[bool] = None

class GeneralLedgerResponse(GeneralLedgerBase):
    id: int
    organization_id: int
    running_balance: Decimal
    is_reconciled: bool
    reconciled_date: Optional[SkipValidation[date]]
    created_at: datetime
    
    class Config:
        from_attributes = True

# Cost Center Schemas
class CostCenterBase(BaseModel):
    cost_center_code: str = Field(..., description="Cost center code")
    cost_center_name: str = Field(..., description="Cost center name")
    parent_cost_center_id: Optional[int] = Field(None, description="Parent cost center ID")
    budget_amount: Decimal = Field(0.00, description="Budget amount")
    department: Optional[str] = Field(None, description="Department")
    manager_id: Optional[int] = Field(None, description="Manager ID")
    description: Optional[str] = Field(None, description="Description")

class CostCenterCreate(CostCenterBase):
    pass

class CostCenterUpdate(BaseModel):
    cost_center_name: Optional[str] = None
    parent_cost_center_id: Optional[int] = None
    budget_amount: Optional[Decimal] = None
    department: Optional[str] = None
    manager_id: Optional[int] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class CostCenterResponse(CostCenterBase):
    id: int
    organization_id: int
    level: int
    actual_amount: Decimal
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Bank Account Schemas
class BankAccountBase(BaseModel):
    chart_account_id: int = Field(..., description="Chart of accounts ID")
    bank_name: str = Field(..., description="Bank name")
    branch_name: Optional[str] = Field(None, description="Branch name")
    account_number: str = Field(..., description="Account number")
    ifsc_code: Optional[str] = Field(None, description="IFSC code")
    swift_code: Optional[str] = Field(None, description="SWIFT code")
    account_type: str = Field(..., description="Account type")
    currency: str = Field("INR", description="Currency")
    opening_balance: Decimal = Field(0.00, description="Opening balance")
    is_default: bool = Field(False, description="Is default account")
    auto_reconcile: bool = Field(False, description="Auto reconcile")

class BankAccountCreate(BankAccountBase):
    pass

class BankAccountUpdate(BaseModel):
    bank_name: Optional[str] = None
    branch_name: Optional[str] = None
    ifsc_code: Optional[str] = None
    swift_code: Optional[str] = None
    account_type: Optional[str] = None
    currency: Optional[str] = None
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None
    auto_reconcile: Optional[bool] = None

class BankAccountResponse(BankAccountBase):
    id: int
    organization_id: int
    current_balance: Decimal
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Bank Reconciliation Schemas
class BankReconciliationBase(BaseModel):
    bank_account_id: int = Field(..., description="Bank account ID")
    reconciliation_date: SkipValidation[date] = Field(..., description="Reconciliation date")
    statement_date: SkipValidation[date] = Field(..., description="Statement date")
    bank_balance: Decimal = Field(..., description="Bank balance")
    book_balance: Decimal = Field(..., description="Book balance")
    outstanding_deposits: Decimal = Field(0.00, description="Outstanding deposits")
    outstanding_checks: Decimal = Field(0.00, description="Outstanding checks")
    bank_charges: Decimal = Field(0.00, description="Bank charges")
    interest_earned: Decimal = Field(0.00, description="Interest earned")
    notes: Optional[str] = Field(None, description="Notes")

class BankReconciliationCreate(BankReconciliationBase):
    pass

class BankReconciliationUpdate(BaseModel):
    statement_date: Optional[SkipValidation[date]] = None
    bank_balance: Optional[Decimal] = None
    book_balance: Optional[Decimal] = None
    outstanding_deposits: Optional[Decimal] = None
    outstanding_checks: Optional[Decimal] = None
    bank_charges: Optional[Decimal] = None
    interest_earned: Optional[Decimal] = None
    status: Optional[str] = None
    notes: Optional[str] = None

class BankReconciliationResponse(BankReconciliationBase):
    id: int
    organization_id: int
    status: str
    difference_amount: Decimal
    created_at: datetime
    
    class Config:
        from_attributes = True

# Financial Statement Schemas
class FinancialStatementCreate(BaseModel):
    statement_type: str = Field(..., description="Statement type")
    statement_name: str = Field(..., description="Statement name")
    period_start: SkipValidation[date] = Field(..., description="Period start date")
    period_end: SkipValidation[date] = Field(..., description="Period end date")
    is_final: bool = Field(False, description="Is final statement")
    is_audited: bool = Field(False, description="Is audited")

class FinancialStatementResponse(BaseModel):
    id: int
    organization_id: int
    statement_type: str
    statement_name: str
    period_start: SkipValidation[date]
    period_end: SkipValidation[date]
    statement_data: dict = Field(..., description="Comprehensive financial statement data including account balances, sub-totals, and detailed line items. Contains nested structure with accounts, amounts, and calculation details.")
    summary_data: Optional[dict] = Field(None, description="Aggregated summary metrics and KPIs derived from statement data. Includes key ratios, totals, and comparative analysis data for quick insights.")
    is_final: bool
    is_audited: bool
    generated_at: datetime
    
    class Config:
        from_attributes = True

# Financial KPI Schemas
class FinancialKPIBase(BaseModel):
    kpi_code: str = Field(..., description="KPI code")
    kpi_name: str = Field(..., description="KPI name")
    kpi_category: str = Field(..., description="KPI category")
    kpi_value: Decimal = Field(..., description="KPI value")
    calculation_method: Optional[str] = Field(None, description="Calculation method")
    period_start: SkipValidation[date] = Field(..., description="Period start date")
    period_end: SkipValidation[date] = Field(..., description="Period end date")
    target_value: Optional[Decimal] = Field(None, description="Target value")

class FinancialKPICreate(FinancialKPIBase):
    pass

class FinancialKPIResponse(FinancialKPIBase):
    id: int
    organization_id: int
    variance_percentage: Optional[Decimal]
    calculated_at: datetime
    
    class Config:
        from_attributes = True

# Cash Flow Statement Schema
class CashFlowResponse(BaseModel):
    operating_activities: List[BalanceSheetItem]
    investing_activities: List[BalanceSheetItem]
    financing_activities: List[BalanceSheetItem]
    net_operating_cash: Decimal
    net_investing_cash: Decimal
    net_financing_cash: Decimal
    net_cash_flow: Decimal
    opening_cash: Decimal
    closing_cash: Decimal
    from_date: SkipValidation[date]
    to_date: SkipValidation[date]
    organization_id: int