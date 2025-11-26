# app/services/ledger_service.py

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, date
from decimal import Decimal
from dateutil.parser import parse as date_parser

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
from app.models.erp_models import ChartOfAccounts

logger = logging.getLogger(__name__)


class LedgerService:
    """Service for generating ledger reports"""
    
    @staticmethod
    async def get_complete_ledger(
        db: AsyncSession,
        organization_id: int,
        filters: LedgerFilters
    ) -> CompleteLedgerResponse:
        """
        Generate complete ledger showing all debit/credit transactions
        
        Args:
            db: Async database session
            organization_id: Organization ID for tenant filtering
            filters: Ledger filters
            
        Returns:
            CompleteLedgerResponse with all transactions and summary
        """
        try:
            # Get all relevant transactions
            transactions = await LedgerService._get_all_transactions(db, organization_id, filters)
            
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
            logger.error(f"Error generating complete ledger: {str(e)}", exc_info=True)
            raise
    
    @staticmethod
    async def get_outstanding_ledger(
        db: AsyncSession,
        organization_id: int,
        filters: LedgerFilters
    ) -> OutstandingLedgerResponse:
        """
        Generate outstanding ledger showing open balances by account
        
        Args:
            db: Async database session
            organization_id: Organization ID for tenant filtering
            filters: Ledger filters
            
        Returns:
            OutstandingLedgerResponse with outstanding balances and summary
        """
        try:
            # Get outstanding balances
            outstanding_balances = await LedgerService._calculate_outstanding_balances(
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
            logger.error(f"Error generating outstanding ledger: {str(e)}", exc_info=True)
            raise
    
    @staticmethod
    async def _get_all_transactions(
        db: AsyncSession,
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
                "account_relation": None, 
                "account_field": "customer_id",  # Changed to None to use fetch logic
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
                
            voucher_transactions = await LedgerService._get_voucher_transactions(
                db, organization_id, config, filters
            )
            transactions.extend(voucher_transactions)
        
        # Filter out transactions with no date
        transactions = [t for t in transactions if t.date is not None]
        
        # Sort by date
        transactions.sort(key=lambda x: x.date)
        
        return transactions
    
    @staticmethod
    async def _get_voucher_transactions(
        db: AsyncSession,
        organization_id: int,
        config: Dict[str, Any],
        filters: LedgerFilters
    ) -> List[LedgerTransaction]:
        """Get transactions for a specific voucher type"""
        model = config["model"]
        
        # Build base query with tenant filtering
        query = TenantQueryFilter.apply_organization_filter(
            select(model), model, organization_id
        )
        
        # Parse and apply date filters
        if filters.start_date:
            try:
                start_date = date_parser(filters.start_date).date()
                query = query.filter(model.date >= start_date)
            except Exception as e:
                logger.warning(f"Invalid start_date format: {filters.start_date}, error: {str(e)}")
        
        if filters.end_date:
            try:
                end_date = date_parser(filters.end_date).date()
                query = query.filter(model.date <= end_date)
            except Exception as e:
                logger.warning(f"Invalid end_date format: {filters.end_date}, error: {str(e)}")
        
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
        
        result = await db.execute(query)
        vouchers = result.scalars().all()
        transactions = []
        
        for voucher in vouchers:
            # Determine account info
            account_type, account_id, account_name = await LedgerService._get_account_info(
                voucher, config, db
            )
            
            if not account_type:  # Skip if couldn't determine account
                continue
            
            # Normalize date to datetime
            transaction_date = voucher.date
            if transaction_date is None:
                continue
            if isinstance(transaction_date, date) and not isinstance(transaction_date, datetime):
                transaction_date = datetime.combine(transaction_date, datetime.min.time())
            
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
                date=transaction_date,
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
    async def _get_account_info(voucher, config: Dict[str, Any], db: AsyncSession) -> Tuple[str, int, str]:
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
                else:
                    # Fetch if not loaded
                    result = await db.execute(select(Vendor).filter(Vendor.id == voucher.vendor_id))
                    vendor = result.scalar_one_or_none()
                    if vendor:
                        account_name = vendor.name
            elif hasattr(voucher, 'customer_id') and voucher.customer_id:
                account_type = "customer"
                account_id = voucher.customer_id
                if hasattr(voucher, 'customer') and voucher.customer:
                    account_name = voucher.customer.name
                else:
                    # Fetch if not loaded
                    result = await db.execute(select(Customer).filter(Customer.id == voucher.customer_id))
                    customer = result.scalar_one_or_none()
                    if customer:
                        account_name = customer.name
        elif config["type"] == "payment_voucher":
            if hasattr(voucher, 'entity_type') and voucher.entity_type:
                account_type = voucher.entity_type.lower()
                account_id = voucher.entity_id
                if account_type == "vendor":
                    result = await db.execute(select(Vendor).filter(Vendor.id == account_id))
                    vendor = result.scalars().first()
                    account_name = vendor.name if vendor else "Unknown Vendor"
                elif account_type == "customer":
                    result = await db.execute(select(Customer).filter(Customer.id == account_id))
                    customer = result.scalars().first()
                    account_name = customer.name if customer else "Unknown Customer"
                elif account_type == "employee":
                    result = await db.execute(select(EmployeeProfile).filter(EmployeeProfile.id == account_id))
                    employee = result.scalars().first()
                    account_name = employee.user.full_name if employee and employee.user else "Unknown Employee"
        elif config["type"] == "receipt_voucher":
            # Assuming receipt_voucher has entity_type and entity_id like payment
            if hasattr(voucher, 'entity_type') and voucher.entity_type:
                account_type = voucher.entity_type.lower()
                account_id = voucher.entity_id
                if account_type == "customer":
                    result = await db.execute(select(Customer).filter(Customer.id == account_id))
                    customer = result.scalars().first()
                    account_name = customer.name if customer else "Unknown Customer"
                # Add other types if needed
            else:
                # Fallback assuming customer_id
                if hasattr(voucher, 'customer_id') and voucher.customer_id:
                    account_type = "customer"
                    account_id = voucher.customer_id
                    result = await db.execute(select(Customer).filter(Customer.id == account_id))
                    customer = result.scalars().first()
                    account_name = customer.name if customer else "Unknown Customer"
        else:
            # Regular vouchers
            account_type = config["account_relation"]
            if config["account_field"]:
                account_id = getattr(voucher, config["account_field"])
                
                # Fetch name based on account_type
                if account_type == "vendor":
                    result = await db.execute(select(Vendor).filter(Vendor.id == account_id))
                    vendor = result.scalars().first()
                    account_name = vendor.name if vendor else "Unknown Vendor"
                elif account_type == "customer":
                    result = await db.execute(select(Customer).filter(Customer.id == account_id))
                    customer = result.scalars().first()
                    account_name = customer.name if customer else "Unknown Customer"
        
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
    async def _calculate_outstanding_balances(
        db: AsyncSession,
        organization_id: int,
        filters: LedgerFilters
    ) -> List[OutstandingBalance]:
        """Calculate outstanding balances for all accounts"""
        # Get all transactions
        all_transactions = await LedgerService._get_all_transactions(db, organization_id, filters)
        
        # Filter out transactions with no date
        all_transactions = [t for t in all_transactions if t.date is not None]
        
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
            if account_id is None:
                continue
            if account_type == "vendor":
                result = await db.execute(
                    select(Vendor).filter(
                        Vendor.id == account_id,
                        Vendor.organization_id == organization_id
                    )
                )
                vendor = result.scalars().first()
                if vendor:
                    data["contact_info"] = vendor.contact_number
            elif account_type == "customer":
                result = await db.execute(
                    select(Customer).filter(
                        Customer.id == account_id,
                        Customer.organization_id == organization_id
                    )
                )
                customer = result.scalars().first()
                if customer:
                    data["contact_info"] = customer.contact_number
            elif account_type == "employee":
                result = await db.execute(
                    select(EmployeeProfile).filter(
                        EmployeeProfile.id == account_id,
                        EmployeeProfile.organization_id == organization_id
                    )
                )
                employee = result.scalars().first()
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
        dates = [t.date for t in transactions if t.date is not None]
        if not dates:
            return {"start_date": None, "end_date": None}
        
        return {
            "start_date": min(dates).isoformat(),
            "end_date": max(dates).isoformat()
        }

    @staticmethod
    async def generate_account_code(db: AsyncSession, organization_id: int, account_type: str) -> str:
        """Generate next account code based on type"""
        account_type = account_type.upper()
        min_codes = {
            'CASH': 1000,
            'BANK': 1100,
            'ASSET': 1200,
            'LIABILITY': 2000,
            'EQUITY': 3000,
            'INCOME': 4000,
            'EXPENSE': 5000,
        }
        
        min_code = min_codes.get(account_type, 9000)
        
        result = await db.execute(
            select(ChartOfAccounts).filter(
                ChartOfAccounts.organization_id == organization_id,
                ChartOfAccounts.account_type == account_type
            )
        )
        type_accounts = result.scalars().all()
        
        max_code = 0
        for acc in type_accounts:
            try:
                code_num = int(acc.account_code)
                if code_num > max_code:
                    max_code = code_num
            except ValueError:
                pass  # Skip non-numeric codes
        
        if max_code < min_code:
            next_code = min_code
        else:
            next_code = (max_code // 10 + 1) * 10
        
        return f"{next_code:04d}"

    @staticmethod
    async def create_standard_chart_of_accounts(db: AsyncSession, organization_id: int):
        """Create a standard chart of accounts structure without balances"""
        accounts = [
            # ASSETS (1000-1999)
            # Current Assets (1000-1199)
            {"code": "1000", "name": "Current Assets", "type": "ASSET", "is_group": True, "parent": None},
            # Fixed Assets (1500-1799)
            {"code": "1500", "name": "Fixed Assets", "type": "ASSET", "is_group": True, "parent": None},
            # LIABILITIES (2000-2999)
            # Current Liabilities (2000-2199)
            {"code": "2000", "name": "Current Liabilities", "type": "LIABILITY", "is_group": True, "parent": None},
            # Long-term Liabilities (2500-2799)
            {"code": "2500", "name": "Long-term Liabilities", "type": "LIABILITY", "is_group": True, "parent": None},
            # EQUITY (3000-3999)
            {"code": "3000", "name": "Equity", "type": "EQUITY", "is_group": True, "parent": None},
            # INCOME (4000-4999)
            {"code": "4000", "name": "Revenue", "type": "INCOME", "is_group": True, "parent": None},
            # EXPENSES (5000-5999)
            {"code": "5000", "name": "Cost of Goods Sold", "type": "EXPENSE", "is_group": True, "parent": None},
            # Operating Expenses (6000-6999)
            {"code": "6000", "name": "Operating Expenses", "type": "EXPENSE", "is_group": True, "parent": None},
        ]
        
        # Create accounts and maintain parent-child relationships
        created_accounts = {}
        
        # First pass: Create all accounts
        for acc_data in accounts:
            account = ChartOfAccounts(
                organization_id=organization_id,
                account_code=acc_data["code"],
                account_name=acc_data["name"],
                account_type=acc_data["type"],
                is_group=acc_data["is_group"],
                opening_balance=Decimal('0.00'),
                current_balance=Decimal('0.00'),
                is_reconcilable=acc_data.get("reconcilable", False)
            )
            db.add(account)
            await db.flush()
            created_accounts[acc_data["code"]] = account
        
        # Second pass: Set parent relationships
        for acc_data in accounts:
            if acc_data["parent"]:
                created_accounts[acc_data["code"]].parent_account_id = created_accounts[acc_data["parent"]].id
        
        await db.commit()
        return created_accounts

    @staticmethod
    async def get_chart_of_accounts(db: AsyncSession, organization_id: int) -> List[Dict[str, Any]]:
        """Get chart of accounts"""
        result = await db.execute(
            select(ChartOfAccounts).filter(
                ChartOfAccounts.organization_id == organization_id
            ).order_by(ChartOfAccounts.account_code)
        )
        accounts = result.scalars().all()
        return [
            {
                "id": acc.id,
                "account_code": acc.account_code,
                "account_name": acc.account_name,
                "account_type": acc.account_type,
                "opening_balance": float(acc.opening_balance),
                "current_balance": float(acc.current_balance),
                "is_group": acc.is_group,
                "parent_account_id": acc.parent_account_id
            }
            for acc in accounts
        ]

def main():
    """Main function to seed standard chart of accounts for all organizations"""
    # Note: This is synchronous; for async usage, wrap in asyncio.run()
    import asyncio
    from app.core.database import SessionLocal
    from app.models.system_models import Organization
    db = SessionLocal()
    
    try:
        # Get all organizations
        organizations = db.query(Organization).all()
        if not organizations:
            print("No organizations found. Please create at least one organization first.")
            return
        
        total_created = 0
        for org in organizations:
            # Check if already seeded to avoid duplicates
            existing_count = db.query(ChartOfAccounts).filter(ChartOfAccounts.organization_id == org.id).count()
            if existing_count > 0:
                print(f"Skipping organization '{org.name}' (ID: {org.id}) - already has {existing_count} accounts.")
                continue
            
            print(f"Seeding standard chart of accounts for organization: {org.name} (ID: {org.id})")
            
            # Create standard chart of accounts
            chart_accounts = LedgerService.create_standard_chart_of_accounts(db, org.id)
            total_created += len(chart_accounts)
            print(f"Created {len(chart_accounts)} chart of accounts for {org.name}")
        
        print(f"\n🎉 Standard chart of accounts seeded successfully for all eligible organizations!")
        print(f"Total accounts created: {total_created}")
        print("You can now edit these accounts with your actual balances in the app.")
        
    except Exception as e:
        print(f"Error seeding chart of accounts: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()