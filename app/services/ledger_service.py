# app/services/ledger_service.py

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, date
from decimal import Decimal

from app.models import Vendor, Customer
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
                "account_relation": "vendor",
                "account_field": "vendor_id", 
                "debit_amount_field": None,
                "credit_amount_field": "total_amount"  # Decreases vendor payable
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
        
        # Handle special cases for DebitNote and CreditNote which can have vendor or customer
        if config["type"] in ["debit_note", "credit_note"]:
            # For debit/credit notes, we need to check both vendor_id and customer_id
            if filters.account_type == "vendor":
                query = query.filter(model.vendor_id.isnot(None))
            elif filters.account_type == "customer":
                query = query.filter(model.customer_id.isnot(None))
                
            if filters.account_id:
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
            if transaction.account_type == "vendor":
                # For vendors: debit increases payable (positive), credit decreases payable (negative)
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
            if transaction.account_type == "vendor":
                # Vendor balance: positive = payable amount
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
            else:  # customer
                customer = db.query(Customer).filter(
                    Customer.id == account_id,
                    Customer.organization_id == organization_id
                ).first()
                if customer:
                    data["contact_info"] = customer.contact_number
        
        # Convert to response objects
        outstanding_balances = []
        for data in account_data.values():
            # Apply correct sign convention:
            # - Negative for amounts payable to vendors
            # - Positive for amounts receivable from customers
            outstanding_amount = data["balance"]
            if data["account_type"] == "vendor" and outstanding_amount > 0:
                outstanding_amount = -outstanding_amount  # Payable to vendor
            
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