# app/services/ledger_service.py

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, date
from decimal import Decimal

from app.models import Vendor, Customer
from app.models.hr_models import EmployeeProfile
from app.models.vouchers import (
    PaymentVoucher, ReceiptVoucher, PurchaseVoucher, SalesVoucher,
    DebitNote, CreditNote, BaseVoucher
)
from app.schemas.ledger import (
    LedgerFilters, LedgerTransaction, CompleteLedgerResponse,
    OutstandingBalance, OutstandingLedgerResponse
)
from app.core.tenant import TenantQueryFilter
import logging
from app.models.erp_models import ChartOfAccounts, AccountType

logger = logging.getLogger(__name__)


class LedgerService:
    """Service for generating ledger reports"""
    
    @staticmethod
    def get_complete_ledger(
        db: Session,
        organization_id: int,
        filters: LedgerFilters
    ) -> CompleteLedgerResponse:
        """
        Generate complete ledger showing all debit/credit transactions
        
        Args:
            db: Database session
            organization_id: Organization ID for tenant filtering
            filters: Ledger filters
            
        Returns:
            CompleteLedgerResponse with all transactions and summary
        """
        try:
            # Get all relevant transactions
            transactions = LedgerService._get_all_transactions(db, organization_id, filters)
            
            # Calculate running balances
            transactions_with_balance = LedgerService._calculate_running_balances(transactions)
            
            # Calculate summary
            total_debit = sum(t.debit_amount for t in transactions_with_balance)
            total_credit = sum(t.credit_amount for t in transactions_with_balance)
            net_balance = total_credit - total_debit
            
            summary = {
                "transaction_count": len(transactions_with_balance),
                "accounts_involved": len(set((t.account_type, t.account_id) for t in transactions_with_balance)),
                "date_range": LedgerService._get_date_range(transactions_with_balance),
                "currency": "INR"
            }
            
            return CompleteLedgerResponse(
                transactions=transactions_with_balance,
                summary=summary,
                filters_applied=filters,
                total_debit=total_debit,
                total_credit=total_credit,
                net_balance=net_balance
            )
            
        except Exception as e:
            logger.error(f"Error generating complete ledger: {e}")
            raise
    
    @staticmethod
    def get_outstanding_ledger(
        db: Session,
        organization_id: int,
        filters: LedgerFilters
    ) -> OutstandingLedgerResponse:
        """
        Generate outstanding ledger showing open balances by account
        
        Args:
            db: Database session
            organization_id: Organization ID for tenant filtering
            filters: Ledger filters
            
        Returns:
            OutstandingLedgerResponse with outstanding balances and summary
        """
        try:
            # Get outstanding balances
            outstanding_balances = LedgerService._calculate_outstanding_balances(
                db, organization_id, filters
            )
            
            # Calculate summary
            total_payable = sum(
                balance.outstanding_amount for balance in outstanding_balances
                if balance.account_type == "vendor" and balance.outstanding_amount < 0
            )
            total_receivable = sum(
                balance.outstanding_amount for balance in outstanding_balances
                if balance.account_type == "customer" and balance.outstanding_amount > 0
            )
            net_outstanding = total_receivable + total_payable  # payable is already negative
            
            summary = {
                "total_accounts": len(outstanding_balances),
                "accounts_with_balance": len([b for b in outstanding_balances if b.outstanding_amount != 0]),
                "vendor_accounts": len([b for b in outstanding_balances if b.account_type == "vendor"]),
                "customer_accounts": len([b for b in outstanding_balances if b.account_type == "customer"]),
                "currency": "INR"
            }
            
            return OutstandingLedgerResponse(
                outstanding_balances=outstanding_balances,
                summary=summary,
                filters_applied=filters,
                total_payable=total_payable,
                total_receivable=total_receivable,
                net_outstanding=net_outstanding
            )
            
        except Exception as e:
            logger.error(f"Error generating outstanding ledger: {e}")
            raise
    
    @staticmethod
    def _get_all_transactions(
        db: Session,
        organization_id: int,
        filters: LedgerFilters
    ) -> List[LedgerTransaction]:
        """Get all transactions from various voucher types"""
        transactions = []
        
        # Define voucher types and their impact on accounts
        voucher_configs = [
            {
                "model": PurchaseVoucher,
                "type": "purchase_voucher",
                "account_relation": "vendor",
                "account_field": "vendor_id",
                "debit_amount_field": "total_amount",  # Increases vendor payable
                "credit_amount_field": None
            },
            {
                "model": SalesVoucher,
                "type": "sales_voucher", 
                "account_relation": "customer",
                "account_field": "customer_id",
                "debit_amount_field": None,
                "credit_amount_field": "total_amount"  # Increases customer receivable
            },
            {
                "model": PaymentVoucher,
                "type": "payment_voucher",
                "account_relation": None,
                "account_field": None, 
                "debit_amount_field": None,
                "credit_amount_field": "total_amount"  # Adjusted based on entity_type
            },
            {
                "model": ReceiptVoucher,
                "type": "receipt_voucher",
                "account_relation": "customer", 
                "account_field": "customer_id",
                "debit_amount_field": "total_amount",  # Decreases customer receivable
                "credit_amount_field": None
            },
            {
                "model": DebitNote,
                "type": "debit_note",
                "account_relation": None,  # Can be either vendor or customer
                "account_field": None,
                "debit_amount_field": "total_amount",
                "credit_amount_field": None
            },
            {
                "model": CreditNote,
                "type": "credit_note",
                "account_relation": None,  # Can be either vendor or customer
                "account_field": None,
                "debit_amount_field": None,
                "credit_amount_field": "total_amount"
            }
        ]
        
        for config in voucher_configs:
            # Skip if filtering by voucher type and this doesn't match
            if filters.voucher_type != "all" and filters.voucher_type != config["type"]:
                continue
                
            voucher_transactions = LedgerService._get_voucher_transactions(
                db, organization_id, config, filters
            )
            transactions.extend(voucher_transactions)
        
        # Sort by date
        transactions.sort(key=lambda x: x.date)
        
        return transactions
    
    @staticmethod
    def _get_voucher_transactions(
        db: Session,
        organization_id: int,
        config: Dict[str, Any],
        filters: LedgerFilters
    ) -> List[LedgerTransaction]:
        """Get transactions for a specific voucher type"""
        model = config["model"]
        
        # Build base query with tenant filtering
        query = TenantQueryFilter.apply_organization_filter(
            db.query(model), model, organization_id
        )
        
        # Apply date filters
        if filters.start_date:
            query = query.filter(model.date >= filters.start_date)
        if filters.end_date:
            query = query.filter(model.date <= filters.end_date)
        
        # Handle special cases for DebitNote, CreditNote, and PaymentVoucher
        if config["type"] in ["debit_note", "credit_note", "payment_voucher"]:
            # For debit/credit notes and payments, we need to check both vendor_id and customer_id or entity_type
            if filters.account_type != "all":
                if config["type"] == "payment_voucher":
                    query = query.filter(model.entity_type.ilike(filters.account_type))
                else:
                    if filters.account_type == "vendor":
                        query = query.filter(model.vendor_id.isnot(None))
                    elif filters.account_type == "customer":
                        query = query.filter(model.customer_id.isnot(None))
                
            if filters.account_id:
                if config["type"] == "payment_voucher":
                    query = query.filter(model.entity_id == filters.account_id)
                else:
                    if filters.account_type == "vendor":
                        query = query.filter(model.vendor_id == filters.account_id)
                    elif filters.account_type == "customer":
                        query = query.filter(model.customer_id == filters.account_id)
        else:
            # Regular vouchers with single account type
            if config["account_relation"]:
                # Filter by account type
                if filters.account_type != "all" and filters.account_type != config["account_relation"]:
                    return []
                
                # Filter by specific account ID
                if filters.account_id:
                    account_field = getattr(model, config["account_field"])
                    query = query.filter(account_field == filters.account_id)
        
        vouchers = query.all()
        transactions = []
        
        for voucher in vouchers:
            # Determine account info
            account_type, account_id, account_name = LedgerService._get_account_info(
                voucher, config, db
            )
            
            if not account_type:  # Skip if couldn't determine account
                continue
            
            # Calculate debit/credit amounts
            debit_amount = Decimal(0)
            credit_amount = Decimal(0)
            
            if config["type"] == "payment_voucher":
                if account_type == "vendor" or account_type == "employee":
                    credit_amount = Decimal(str(getattr(voucher, config["credit_amount_field"], 0) or 0))
                elif account_type == "customer":
                    debit_amount = Decimal(str(getattr(voucher, config["credit_amount_field"], 0) or 0))
            else:
                if config["debit_amount_field"]:
                    debit_amount = Decimal(str(getattr(voucher, config["debit_amount_field"], 0) or 0))
                if config["credit_amount_field"]:
                    credit_amount = Decimal(str(getattr(voucher, config["credit_amount_field"], 0) or 0))
            
            transaction = LedgerTransaction(
                id=voucher.id,
                voucher_type=config["type"],
                voucher_number=voucher.voucher_number,
                date=voucher.date,
                account_type=account_type,
                account_id=account_id,
                account_name=account_name,
                debit_amount=debit_amount,
                credit_amount=credit_amount,
                balance=Decimal(0),  # Will be calculated later
                description=getattr(voucher, 'notes', '') or getattr(voucher, 'reason', ''),
                reference=getattr(voucher, 'reference', ''),
                status=voucher.status
            )
            transactions.append(transaction)
        
        return transactions
    
    @staticmethod
    def _get_account_info(voucher, config: Dict[str, Any], db: Session) -> Tuple[str, int, str]:
        """Get account type, ID and name from voucher"""
        account_type = None
        account_id = None
        account_name = ""
        
        if config["type"] in ["debit_note", "credit_note"]:
            # Check both vendor and customer for debit/credit notes
            if hasattr(voucher, 'vendor_id') and voucher.vendor_id:
                account_type = "vendor"
                account_id = voucher.vendor_id
                if hasattr(voucher, 'vendor') and voucher.vendor:
                    account_name = voucher.vendor.name
            elif hasattr(voucher, 'customer_id') and voucher.customer_id:
                account_type = "customer"
                account_id = voucher.customer_id
                if hasattr(voucher, 'customer') and voucher.customer:
                    account_name = voucher.customer.name
        elif config["type"] == "payment_voucher":
            if hasattr(voucher, 'entity_type') and voucher.entity_type:
                account_type = voucher.entity_type.lower()
                account_id = voucher.entity_id
                if account_type == "vendor":
                    vendor = db.query(Vendor).filter(Vendor.id == account_id).first()
                    account_name = vendor.name if vendor else "Unknown Vendor"
                elif account_type == "customer":
                    customer = db.query(Customer).filter(Customer.id == account_id).first()
                    account_name = customer.name if customer else "Unknown Customer"
                elif account_type == "employee":
                    employee = db.query(EmployeeProfile).filter(EmployeeProfile.id == account_id).first()
                    account_name = employee.user.full_name if employee and employee.user else "Unknown Employee"
        else:
            # Regular vouchers
            account_type = config["account_relation"]
            if config["account_field"]:
                account_id = getattr(voucher, config["account_field"])
                
                # Get account name
                relation_attr = config["account_relation"]
                if hasattr(voucher, relation_attr):
                    account_obj = getattr(voucher, relation_attr)
                    if account_obj:
                        account_name = account_obj.name
        
        return account_type, account_id, account_name
    
    @staticmethod
    def _calculate_running_balances(transactions: List[LedgerTransaction]) -> List[LedgerTransaction]:
        """Calculate running balances for transactions"""
        # Group transactions by account
        account_balances = {}
        
        for transaction in transactions:
            account_key = (transaction.account_type, transaction.account_id)
            
            if account_key not in account_balances:
                account_balances[account_key] = Decimal(0)
            
            # Update balance based on account type and transaction type
            if transaction.account_type == "vendor" or transaction.account_type == "employee":
                # For vendors/employees: debit increases payable (positive), credit decreases payable (negative)
                account_balances[account_key] += transaction.debit_amount - transaction.credit_amount
            else:  # customer
                # For customers: credit increases receivable (positive), debit decreases receivable (negative)
                account_balances[account_key] += transaction.credit_amount - transaction.debit_amount
            
            transaction.balance = account_balances[account_key]
        
        return transactions
    
    @staticmethod
    def _calculate_outstanding_balances(
        db: Session,
        organization_id: int,
        filters: LedgerFilters
    ) -> List[OutstandingBalance]:
        """Calculate outstanding balances for all accounts"""
        # Get all transactions to calculate balances
        all_transactions = LedgerService._get_all_transactions(db, organization_id, filters)
        
        # Group by account and calculate final balances
        account_data = {}
        
        for transaction in all_transactions:
            account_key = (transaction.account_type, transaction.account_id)
            
            if account_key not in account_data:
                account_data[account_key] = {
                    "account_type": transaction.account_type,
                    "account_id": transaction.account_id,
                    "account_name": transaction.account_name,
                    "balance": Decimal(0),
                    "last_transaction_date": transaction.date,
                    "transaction_count": 0,
                    "contact_info": ""
                }
            
            # Update balance
            if transaction.account_type == "vendor" or transaction.account_type == "employee":
                # Vendor/employee balance: positive = payable amount
                account_data[account_key]["balance"] += transaction.debit_amount - transaction.credit_amount
            else:  # customer
                # Customer balance: positive = receivable amount  
                account_data[account_key]["balance"] += transaction.credit_amount - transaction.debit_amount
            
            # Update metadata
            if transaction.date > account_data[account_key]["last_transaction_date"]:
                account_data[account_key]["last_transaction_date"] = transaction.date
            account_data[account_key]["transaction_count"] += 1
        
        # Get contact information
        for account_key, data in account_data.items():
            account_type, account_id = account_key
            if account_type == "vendor":
                vendor = db.query(Vendor).filter(
                    Vendor.id == account_id,
                    Vendor.organization_id == organization_id
                ).first()
                if vendor:
                    data["contact_info"] = vendor.contact_number
            elif account_type == "customer":
                customer = db.query(Customer).filter(
                    Customer.id == account_id,
                    Customer.organization_id == organization_id
                ).first()
                if customer:
                    data["contact_info"] = customer.contact_number
            elif account_type == "employee":
                employee = db.query(EmployeeProfile).filter(
                    EmployeeProfile.id == account_id,
                    EmployeeProfile.organization_id == organization_id
                ).first()
                if employee:
                    data["contact_info"] = employee.personal_phone
        
        # Convert to response objects
        outstanding_balances = []
        for data in account_data.values():
            # Apply correct sign convention:
            # - Negative for amounts payable to vendors/employees
            # - Positive for amounts receivable from customers
            outstanding_amount = data["balance"]
            if (data["account_type"] == "vendor" or data["account_type"] == "employee") and outstanding_amount > 0:
                outstanding_amount = -outstanding_amount  # Payable
            # For customers, positive is receivable
            
            outstanding_balance = OutstandingBalance(
                account_type=data["account_type"],
                account_id=data["account_id"], 
                account_name=data["account_name"],
                outstanding_amount=outstanding_amount,
                last_transaction_date=data["last_transaction_date"],
                transaction_count=data["transaction_count"],
                contact_info=data["contact_info"]
            )
            outstanding_balances.append(outstanding_balance)
        
        # Sort by account name
        outstanding_balances.sort(key=lambda x: x.account_name)
        
        return outstanding_balances
    
    @staticmethod
    def _get_date_range(transactions: List[LedgerTransaction]) -> Dict[str, Any]:
        """Get date range from transactions"""
        if not transactions:
            return {"start_date": None, "end_date": None}
        
        dates = [t.date for t in transactions]
        return {
            "start_date": min(dates).isoformat(),
            "end_date": max(dates).isoformat()
        }

    @staticmethod
    def create_standard_chart_of_accounts(db: Session, organization_id: int):
        """Create a standard chart of accounts structure without balances"""
        accounts = [
            # ASSETS (1000-1999)
            # Current Assets (1000-1199)
            {"code": "1000", "name": "Current Assets", "type": "asset", "is_group": True, "parent": None},
            {"code": "1010", "name": "Cash in Hand", "type": "cash", "is_group": False, "parent": "1000"},
            {"code": "1020", "name": "Petty Cash", "type": "cash", "is_group": False, "parent": "1000"},
            {"code": "1100", "name": "Bank Accounts", "type": "bank", "is_group": True, "parent": "1000"},
            {"code": "1110", "name": "Primary Bank Account", "type": "bank", "is_group": False, "parent": "1100", "reconcilable": True},
            {"code": "1120", "name": "Secondary Bank Account", "type": "bank", "is_group": False, "parent": "1100", "reconcilable": True},
            {"code": "1200", "name": "Accounts Receivable", "type": "asset", "is_group": True, "parent": "1000"},
            {"code": "1210", "name": "Trade Receivables", "type": "asset", "is_group": False, "parent": "1200"},
            {"code": "1220", "name": "Other Receivables", "type": "asset", "is_group": False, "parent": "1200"},
            {"code": "1300", "name": "Inventory", "type": "asset", "is_group": True, "parent": "1000"},
            {"code": "1310", "name": "Raw Materials", "type": "asset", "is_group": False, "parent": "1300"},
            {"code": "1320", "name": "Finished Goods", "type": "asset", "is_group": False, "parent": "1300"},
            {"code": "1330", "name": "Work in Progress", "type": "asset", "is_group": False, "parent": "1300"},
            
            # Fixed Assets (1500-1799)
            {"code": "1500", "name": "Fixed Assets", "type": "asset", "is_group": True, "parent": None},
            {"code": "1510", "name": "Plant & Machinery", "type": "asset", "is_group": False, "parent": "1500"},
            {"code": "1520", "name": "Office Equipment", "type": "asset", "is_group": False, "parent": "1500"},
            {"code": "1530", "name": "Furniture & Fixtures", "type": "asset", "is_group": False, "parent": "1500"},
            {"code": "1540", "name": "Vehicles", "type": "asset", "is_group": False, "parent": "1500"},
            {"code": "1550", "name": "Computer Equipment", "type": "asset", "is_group": False, "parent": "1500"},
            
            # LIABILITIES (2000-2999)
            # Current Liabilities (2000-2199)
            {"code": "2000", "name": "Current Liabilities", "type": "liability", "is_group": True, "parent": None},
            {"code": "2010", "name": "Accounts Payable", "type": "liability", "is_group": True, "parent": "2000"},
            {"code": "2011", "name": "Trade Payables", "type": "liability", "is_group": False, "parent": "2010"},
            {"code": "2012", "name": "Other Payables", "type": "liability", "is_group": False, "parent": "2010"},
            {"code": "2100", "name": "Tax Liabilities", "type": "liability", "is_group": True, "parent": "2000"},
            {"code": "2110", "name": "GST Payable", "type": "liability", "is_group": False, "parent": "2100"},
            {"code": "2120", "name": "TDS Payable", "type": "liability", "is_group": False, "parent": "2100"},
            {"code": "2130", "name": "Income Tax Payable", "type": "liability", "is_group": False, "parent": "2100"},
            {"code": "2200", "name": "Accrued Expenses", "type": "liability", "is_group": True, "parent": "2000"},
            {"code": "2210", "name": "Salary Payable", "type": "liability", "is_group": False, "parent": "2200"},
            {"code": "2220", "name": "Utility Bills Payable", "type": "liability", "is_group": False, "parent": "2200"},
            
            # Long-term Liabilities (2500-2799)
            {"code": "2500", "name": "Long-term Liabilities", "type": "liability", "is_group": True, "parent": None},
            {"code": "2510", "name": "Bank Loans", "type": "liability", "is_group": False, "parent": "2500"},
            {"code": "2520", "name": "Equipment Loans", "type": "liability", "is_group": False, "parent": "2500"},
            
            # EQUITY (3000-3999)
            {"code": "3000", "name": "Equity", "type": "equity", "is_group": True, "parent": None},
            {"code": "3100", "name": "Share Capital", "type": "equity", "is_group": False, "parent": "3000"},
            {"code": "3200", "name": "Retained Earnings", "type": "equity", "is_group": False, "parent": "3000"},
            {"code": "3300", "name": "Current Year Earnings", "type": "equity", "is_group": False, "parent": "3000"},
            
            # INCOME (4000-4999)
            {"code": "4000", "name": "Revenue", "type": "income", "is_group": True, "parent": None},
            {"code": "4100", "name": "Sales Revenue", "type": "income", "is_group": True, "parent": "4000"},
            {"code": "4110", "name": "Product Sales", "type": "income", "is_group": False, "parent": "4100"},
            {"code": "4120", "name": "Service Revenue", "type": "income", "is_group": False, "parent": "4100"},
            {"code": "4130", "name": "Consulting Revenue", "type": "income", "is_group": False, "parent": "4100"},
            {"code": "4200", "name": "Other Income", "type": "income", "is_group": True, "parent": "4000"},
            {"code": "4210", "name": "Interest Income", "type": "income", "is_group": False, "parent": "4200"},
            {"code": "4220", "name": "Dividend Income", "type": "income", "is_group": False, "parent": "4200"},
            {"code": "4230", "name": "Miscellaneous Income", "type": "income", "is_group": False, "parent": "4200"},
            
            # EXPENSES (5000-5999)
            {"code": "5000", "name": "Cost of Goods Sold", "type": "expense", "is_group": True, "parent": None},
            {"code": "5100", "name": "Material Costs", "type": "expense", "is_group": False, "parent": "5000"},
            {"code": "5200", "name": "Labor Costs", "type": "expense", "is_group": False, "parent": "5000"},
            {"code": "5300", "name": "Manufacturing Overhead", "type": "expense", "is_group": False, "parent": "5000"},
            
            # Operating Expenses (6000-6999)
            {"code": "6000", "name": "Operating Expenses", "type": "expense", "is_group": True, "parent": None},
            {"code": "6100", "name": "Administrative Expenses", "type": "expense", "is_group": True, "parent": "6000"},
            {"code": "6110", "name": "Salaries & Wages", "type": "expense", "is_group": False, "parent": "6100"},
            {"code": "6120", "name": "Office Rent", "type": "expense", "is_group": False, "parent": "6100"},
            {"code": "6130", "name": "Utilities", "type": "expense", "is_group": False, "parent": "6100"},
            {"code": "6140", "name": "Communication", "type": "expense", "is_group": False, "parent": "6100"},
            {"code": "6150", "name": "Office Supplies", "type": "expense", "is_group": False, "parent": "6100"},
            {"code": "6200", "name": "Sales & Marketing", "type": "expense", "is_group": True, "parent": "6000"},
            {"code": "6210", "name": "Advertising", "type": "expense", "is_group": False, "parent": "6200"},
            {"code": "6220", "name": "Marketing Events", "type": "expense", "is_group": False, "parent": "6200"},
            {"code": "6230", "name": "Sales Commission", "type": "expense", "is_group": False, "parent": "6200"},
            {"code": "6240", "name": "Travel & Entertainment", "type": "expense", "is_group": False, "parent": "6200"},
            {"code": "6300", "name": "IT & Technology", "type": "expense", "is_group": True, "parent": "6000"},
            {"code": "6310", "name": "Software Licenses", "type": "expense", "is_group": False, "parent": "6300"},
            {"code": "6320", "name": "Hardware Maintenance", "type": "expense", "is_group": False, "parent": "6300"},
            {"code": "6330", "name": "Internet & Hosting", "type": "expense", "is_group": False, "parent": "6300"},
            {"code": "6400", "name": "Professional Services", "type": "expense", "is_group": True, "parent": "6000"},
            {"code": "6410", "name": "Legal Fees", "type": "expense", "is_group": False, "parent": "6400"},
            {"code": "6420", "name": "Audit Fees", "type": "expense", "is_group": False, "parent": "6400"},
            {"code": "6430", "name": "Consulting Fees", "type": "expense", "is_group": False, "parent": "6400"},
            {"code": "6500", "name": "Finance Costs", "type": "expense", "is_group": True, "parent": "6000"},
            {"code": "6510", "name": "Interest Expense", "type": "expense", "is_group": False, "parent": "6500"},
            {"code": "6520", "name": "Bank Charges", "type": "expense", "is_group": False, "parent": "6500"},
            {"code": "6530", "name": "Foreign Exchange Loss", "type": "expense", "is_group": False, "parent": "6500"},
        ]
        
        # Create accounts and maintain parent-child relationships
        created_accounts = {}
        
        # First pass: Create all accounts
        for acc_data in accounts:
            account = ChartOfAccounts(
                organization_id=organization_id,
                account_code=acc_data["code"],
                account_name=acc_data["name"],
                account_type=AccountType(acc_data["type"]),
                is_group=acc_data["is_group"],
                opening_balance=Decimal('0.00'),
                current_balance=Decimal('0.00'),
                is_reconcilable=acc_data.get("reconcilable", False)
            )
            db.add(account)
            db.flush()  # Get the ID
            created_accounts[acc_data["code"]] = account
        
        # Second pass: Set parent relationships
        for acc_data in accounts:
            if acc_data["parent"]:
                created_accounts[acc_data["code"]].parent_account_id = created_accounts[acc_data["parent"]].id
        
        db.commit()