# app/schemas/ledger.py

from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime, date
from decimal import Decimal


class LedgerFilters(BaseModel):
    """Filters for ledger reports"""
    start_date: Optional[date] = Field(None, description="Start date for filtering transactions")
    end_date: Optional[date] = Field(None, description="End date for filtering transactions")
    account_type: Optional[Literal["vendor", "customer", "all"]] = Field(
        "all", description="Type of account to filter by"
    )
    account_id: Optional[int] = Field(None, description="Specific vendor or customer ID to filter by")
    voucher_type: Optional[Literal[
        "purchase_voucher", "sales_voucher", "payment_voucher", 
        "receipt_voucher", "debit_note", "credit_note", "all"
    ]] = Field("all", description="Type of voucher to filter by")


class LedgerTransaction(BaseModel):
    """Individual ledger transaction entry"""
    id: int
    voucher_type: str = Field(..., description="Type of voucher (e.g., payment_voucher, sales_voucher)")
    voucher_number: str = Field(..., description="Voucher number")
    date: datetime = Field(..., description="Transaction date")
    account_type: Literal["vendor", "customer"] = Field(..., description="Account type")
    account_id: int = Field(..., description="Vendor or customer ID")
    account_name: str = Field(..., description="Vendor or customer name")
    debit_amount: Decimal = Field(default=0, description="Debit amount (increases vendor payable or decreases customer receivable)")
    credit_amount: Decimal = Field(default=0, description="Credit amount (decreases vendor payable or increases customer receivable)")
    balance: Decimal = Field(..., description="Running balance after this transaction")
    description: Optional[str] = Field(None, description="Transaction description or notes")
    reference: Optional[str] = Field(None, description="Reference number or document")
    status: str = Field(..., description="Transaction status")


class CompleteLedgerResponse(BaseModel):
    """Response for complete ledger report"""
    transactions: List[LedgerTransaction] = Field(..., description="List of all transactions")
    summary: dict = Field(..., description="Summary statistics")
    filters_applied: LedgerFilters = Field(..., description="Filters that were applied")
    total_debit: Decimal = Field(..., description="Total debit amount")
    total_credit: Decimal = Field(..., description="Total credit amount")
    net_balance: Decimal = Field(..., description="Net balance (credit - debit)")


class OutstandingBalance(BaseModel):
    """Outstanding balance for an account"""
    account_type: Literal["vendor", "customer"] = Field(..., description="Account type")
    account_id: int = Field(..., description="Vendor or customer ID")
    account_name: str = Field(..., description="Vendor or customer name")
    outstanding_amount: Decimal = Field(
        ..., 
        description="Outstanding amount (negative for payable to vendors, positive for receivable from customers)"
    )
    last_transaction_date: Optional[datetime] = Field(None, description="Date of last transaction")
    transaction_count: int = Field(..., description="Number of transactions contributing to balance")
    contact_info: Optional[str] = Field(None, description="Contact information")


class OutstandingLedgerResponse(BaseModel):
    """Response for outstanding ledger report"""
    outstanding_balances: List[OutstandingBalance] = Field(..., description="List of outstanding balances")
    summary: dict = Field(..., description="Summary statistics")
    filters_applied: LedgerFilters = Field(..., description="Filters that were applied")
    total_payable: Decimal = Field(..., description="Total amount payable to vendors (negative)")
    total_receivable: Decimal = Field(..., description="Total amount receivable from customers (positive)")
    net_outstanding: Decimal = Field(..., description="Net outstanding amount (receivable - payable)")


class LedgerSummary(BaseModel):
    """Summary statistics for ledger reports"""
    total_vendors: int = Field(..., description="Number of vendors")
    total_customers: int = Field(..., description="Number of customers")
    total_transactions: int = Field(..., description="Total number of transactions")
    date_range: dict = Field(..., description="Date range of transactions")
    currency: str = Field(default="INR", description="Currency code")