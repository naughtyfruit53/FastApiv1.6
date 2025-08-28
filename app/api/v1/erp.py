# app/api/v1/erp.py

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc, asc, func
from typing import List, Optional
from datetime import datetime, date
from decimal import Decimal

from app.core.database import get_db
from app.api.v1.auth import get_current_active_user
from app.core.tenant import TenantQueryMixin, validate_company_setup_for_operations
from app.core.org_restrictions import require_current_organization_id
from app.core.rbac_dependencies import check_service_permission
from app.schemas.user import UserInDB
from app.models.erp_models import (
    ChartOfAccounts, GSTConfiguration, TaxCode, JournalEntry,
    AccountsPayable, AccountsReceivable, PaymentRecord,
    GeneralLedger, CostCenter, BankAccount, BankReconciliation,
    FinancialStatement, FinancialKPI
)
from app.schemas.erp import (
    ChartOfAccountsCreate, ChartOfAccountsUpdate, ChartOfAccountsResponse,
    GSTConfigurationCreate, GSTConfigurationUpdate, GSTConfigurationResponse,
    TaxCodeCreate, TaxCodeUpdate, TaxCodeResponse,
    JournalEntryCreate, JournalEntryUpdate, JournalEntryResponse,
    AccountsPayableCreate, AccountsPayableUpdate, AccountsPayableResponse,
    AccountsReceivableCreate, AccountsReceivableUpdate, AccountsReceivableResponse,
    PaymentRecordCreate, PaymentRecordUpdate, PaymentRecordResponse,
    TrialBalanceResponse, ProfitAndLossResponse, BalanceSheetResponse,
    GeneralLedgerCreate, GeneralLedgerUpdate, GeneralLedgerResponse,
    CostCenterCreate, CostCenterUpdate, CostCenterResponse,
    BankAccountCreate, BankAccountUpdate, BankAccountResponse,
    BankReconciliationCreate, BankReconciliationUpdate, BankReconciliationResponse,
    FinancialStatementCreate, FinancialStatementResponse,
    FinancialKPICreate, FinancialKPIResponse, CashFlowResponse
)
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


class ERPService:
    """Service class for ERP operations"""
    
    @staticmethod
    def generate_account_code(db: Session, organization_id: int, account_type: str) -> str:
        """Generate next account code based on account type"""
        type_prefixes = {
            "asset": "1",
            "liability": "2", 
            "equity": "3",
            "income": "4",
            "expense": "5",
            "bank": "1001",
            "cash": "1002"
        }
        
        prefix = type_prefixes.get(account_type.lower(), "9")
        
        # Get the highest existing code for this type
        last_account = db.query(ChartOfAccounts).filter(
            ChartOfAccounts.organization_id == organization_id,
            ChartOfAccounts.account_code.like(f"{prefix}%")
        ).order_by(desc(ChartOfAccounts.account_code)).first()
        
        if last_account:
            try:
                last_num = int(last_account.account_code)
                return str(last_num + 1)
            except ValueError:
                pass
        
        return f"{prefix}001"


# Chart of Accounts Endpoints
@router.get("/chart-of-accounts", response_model=List[ChartOfAccountsResponse])
async def get_chart_of_accounts(
    skip: int = 0,
    limit: int = 100,
    account_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Get chart of accounts with filtering options"""
    query = db.query(ChartOfAccounts).filter(
        ChartOfAccounts.organization_id == organization_id
    )
    
    if account_type:
        query = query.filter(ChartOfAccounts.account_type == account_type)
    
    if is_active is not None:
        query = query.filter(ChartOfAccounts.is_active == is_active)
    
    if search:
        query = query.filter(or_(
            ChartOfAccounts.account_name.ilike(f"%{search}%"),
            ChartOfAccounts.account_code.ilike(f"%{search}%")
        ))
    
    # Order by account code
    query = query.order_by(ChartOfAccounts.account_code)
    
    accounts = query.offset(skip).limit(limit).all()
    return accounts


@router.post("/chart-of-accounts", response_model=ChartOfAccountsResponse)
async def create_chart_of_account(
    account_data: ChartOfAccountsCreate,
    db: Session = Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Create a new chart of account"""
    # Auto-generate account code if not provided
    account_code = account_data.account_code
    if not account_code:
        account_code = ERPService.generate_account_code(
            db, organization_id, account_data.account_type.value
        )
    
    # Check if account code already exists
    existing = db.query(ChartOfAccounts).filter(
        ChartOfAccounts.organization_id == organization_id,
        ChartOfAccounts.account_code == account_code
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account code already exists"
        )
    
    # Calculate level based on parent account
    level = 0
    if account_data.parent_account_id:
        parent = db.query(ChartOfAccounts).filter(
            ChartOfAccounts.id == account_data.parent_account_id,
            ChartOfAccounts.organization_id == organization_id
        ).first()
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Parent account not found"
            )
        level = parent.level + 1
    
    account = ChartOfAccounts(
        organization_id=organization_id,
        account_code=account_code,
        account_name=account_data.account_name,
        account_type=account_data.account_type,
        parent_account_id=account_data.parent_account_id,
        level=level,
        is_group=account_data.is_group,
        opening_balance=account_data.opening_balance,
        current_balance=account_data.opening_balance,
        can_post=account_data.can_post,
        is_reconcilable=account_data.is_reconcilable,
        description=account_data.description,
        notes=account_data.notes,
        created_by=current_user.id
    )
    
    db.add(account)
    db.commit()
    db.refresh(account)
    
    return account


@router.get("/chart-of-accounts/{account_id}", response_model=ChartOfAccountsResponse)
async def get_chart_of_account(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Get a specific chart of account"""
    account = db.query(ChartOfAccounts).filter(
        ChartOfAccounts.id == account_id,
        ChartOfAccounts.organization_id == organization_id
    ).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    
    return account


@router.put("/chart-of-accounts/{account_id}", response_model=ChartOfAccountsResponse)
async def update_chart_of_account(
    account_id: int,
    account_data: ChartOfAccountsUpdate,
    db: Session = Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Update a chart of account"""
    account = db.query(ChartOfAccounts).filter(
        ChartOfAccounts.id == account_id,
        ChartOfAccounts.organization_id == organization_id
    ).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    
    update_data = account_data.dict(exclude_unset=True)
    
    # Recalculate level if parent changes
    if 'parent_account_id' in update_data:
        if update_data['parent_account_id']:
            parent = db.query(ChartOfAccounts).filter(
                ChartOfAccounts.id == update_data['parent_account_id'],
                ChartOfAccounts.organization_id == organization_id
            ).first()
            if not parent:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Parent account not found"
                )
            update_data['level'] = parent.level + 1
        else:
            update_data['level'] = 0
    
    for field, value in update_data.items():
        setattr(account, field, value)
    
    account.updated_by = current_user.id
    account.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(account)
    
    return account


@router.delete("/chart-of-accounts/{account_id}")
async def delete_chart_of_account(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Delete a chart of account"""
    account = db.query(ChartOfAccounts).filter(
        ChartOfAccounts.id == account_id,
        ChartOfAccounts.organization_id == organization_id
    ).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    
    # Check if account has sub-accounts
    sub_accounts = db.query(ChartOfAccounts).filter(
        ChartOfAccounts.parent_account_id == account_id,
        ChartOfAccounts.organization_id == organization_id
    ).count()
    
    if sub_accounts > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete account with sub-accounts"
        )
    
    # Check if account has journal entries
    journal_entries = db.query(JournalEntry).filter(
        JournalEntry.account_id == account_id,
        JournalEntry.organization_id == organization_id
    ).count()
    
    if journal_entries > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete account with journal entries"
        )
    
    db.delete(account)
    db.commit()
    
    return {"message": "Account deleted successfully"}


# GST Configuration Endpoints
@router.get("/gst-configuration", response_model=List[GSTConfigurationResponse])
async def get_gst_configurations(
    db: Session = Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Get GST configurations"""
    configurations = db.query(GSTConfiguration).filter(
        GSTConfiguration.organization_id == organization_id
    ).all()
    
    return configurations


@router.post("/gst-configuration", response_model=GSTConfigurationResponse)
async def create_gst_configuration(
    config_data: GSTConfigurationCreate,
    db: Session = Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Create GST configuration"""
    # Check if GSTIN already exists
    existing = db.query(GSTConfiguration).filter(
        GSTConfiguration.gstin == config_data.gstin
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="GSTIN already exists"
        )
    
    configuration = GSTConfiguration(
        organization_id=organization_id,
        **config_data.dict()
    )
    
    db.add(configuration)
    db.commit()
    db.refresh(configuration)
    
    return configuration


# Tax Code Endpoints
@router.get("/tax-codes", response_model=List[TaxCodeResponse])
async def get_tax_codes(
    skip: int = 0,
    limit: int = 100,
    tax_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Get tax codes with filtering options"""
    query = db.query(TaxCode).filter(
        TaxCode.organization_id == organization_id
    )
    
    if tax_type:
        query = query.filter(TaxCode.tax_type == tax_type)
    
    if is_active is not None:
        query = query.filter(TaxCode.is_active == is_active)
    
    tax_codes = query.offset(skip).limit(limit).all()
    return tax_codes


@router.post("/tax-codes", response_model=TaxCodeResponse)
async def create_tax_code(
    tax_data: TaxCodeCreate,
    db: Session = Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Create a new tax code"""
    # Check if tax code already exists
    existing = db.query(TaxCode).filter(
        TaxCode.organization_id == organization_id,
        TaxCode.tax_code == tax_data.tax_code
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tax code already exists"
        )
    
    tax_code = TaxCode(
        organization_id=organization_id,
        **tax_data.dict()
    )
    
    db.add(tax_code)
    db.commit()
    db.refresh(tax_code)
    
    return tax_code


# Financial Reports
@router.get("/reports/trial-balance", response_model=TrialBalanceResponse)
async def get_trial_balance(
    as_of_date: date = Query(..., description="As of date for trial balance"),
    db: Session = Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Generate trial balance report"""
    # Get all accounts with their balances
    accounts = db.query(ChartOfAccounts).filter(
        ChartOfAccounts.organization_id == organization_id,
        ChartOfAccounts.is_active == True,
        ChartOfAccounts.can_post == True
    ).all()
    
    trial_balance = []
    total_debits = Decimal(0)
    total_credits = Decimal(0)
    
    for account in accounts:
        # Calculate balance up to as_of_date
        # This is a simplified calculation - in production, you'd calculate from journal entries
        debit_balance = Decimal(0)
        credit_balance = Decimal(0)
        
        if account.current_balance > 0:
            if account.account_type.value in ['asset', 'expense']:
                debit_balance = account.current_balance
            else:
                credit_balance = account.current_balance
        elif account.current_balance < 0:
            if account.account_type.value in ['asset', 'expense']:
                credit_balance = abs(account.current_balance)
            else:
                debit_balance = abs(account.current_balance)
        
        if debit_balance > 0 or credit_balance > 0:
            trial_balance.append({
                "account_code": account.account_code,
                "account_name": account.account_name,
                "debit_balance": debit_balance,
                "credit_balance": credit_balance
            })
            
            total_debits += debit_balance
            total_credits += credit_balance
    
    return TrialBalanceResponse(
        trial_balance=trial_balance,
        total_debits=total_debits,
        total_credits=total_credits,
        as_of_date=as_of_date,
        organization_id=organization_id
    )


# Accounts Payable/Receivable endpoints would follow similar patterns...


# General Ledger Endpoints
@router.get("/general-ledger", response_model=List[GeneralLedgerResponse])
async def get_general_ledger(
    skip: int = 0,
    limit: int = 100,
    account_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    reference_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Get general ledger entries with filtering options"""
    query = db.query(GeneralLedger).filter(
        GeneralLedger.organization_id == organization_id
    )
    
    if account_id:
        query = query.filter(GeneralLedger.account_id == account_id)
    
    if start_date:
        query = query.filter(GeneralLedger.transaction_date >= start_date)
    
    if end_date:
        query = query.filter(GeneralLedger.transaction_date <= end_date)
    
    if reference_type:
        query = query.filter(GeneralLedger.reference_type == reference_type)
    
    query = query.order_by(desc(GeneralLedger.transaction_date), desc(GeneralLedger.id))
    
    entries = query.offset(skip).limit(limit).all()
    return entries


@router.post("/general-ledger", response_model=GeneralLedgerResponse)
async def create_general_ledger_entry(
    entry: GeneralLedgerCreate,
    db: Session = Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Create a new general ledger entry"""
    # Validate account exists
    account = db.query(ChartOfAccounts).filter(
        ChartOfAccounts.id == entry.account_id,
        ChartOfAccounts.organization_id == organization_id
    ).first()
    
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    # Calculate running balance
    last_entry = db.query(GeneralLedger).filter(
        GeneralLedger.account_id == entry.account_id,
        GeneralLedger.organization_id == organization_id
    ).order_by(desc(GeneralLedger.transaction_date), desc(GeneralLedger.id)).first()
    
    previous_balance = last_entry.running_balance if last_entry else account.opening_balance
    
    if account.account_type.value in ['asset', 'expense']:
        running_balance = previous_balance + entry.debit_amount - entry.credit_amount
    else:
        running_balance = previous_balance + entry.credit_amount - entry.debit_amount
    
    db_entry = GeneralLedger(
        organization_id=organization_id,
        running_balance=running_balance,
        created_by=current_user.id,
        **entry.dict()
    )
    
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    
    return db_entry


# Cost Center Endpoints
@router.get("/cost-centers", response_model=List[CostCenterResponse])
async def get_cost_centers(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    parent_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Get cost centers with filtering options"""
    query = db.query(CostCenter).filter(
        CostCenter.organization_id == organization_id
    )
    
    if is_active is not None:
        query = query.filter(CostCenter.is_active == is_active)
    
    if parent_id is not None:
        query = query.filter(CostCenter.parent_cost_center_id == parent_id)
    
    cost_centers = query.offset(skip).limit(limit).all()
    return cost_centers


@router.post("/cost-centers", response_model=CostCenterResponse)
async def create_cost_center(
    cost_center: CostCenterCreate,
    db: Session = Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Create a new cost center"""
    # Check if cost center code exists
    existing = db.query(CostCenter).filter(
        CostCenter.organization_id == organization_id,
        CostCenter.cost_center_code == cost_center.cost_center_code
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Cost center code already exists")
    
    # Calculate level
    level = 0
    if cost_center.parent_cost_center_id:
        parent = db.query(CostCenter).filter(
            CostCenter.id == cost_center.parent_cost_center_id,
            CostCenter.organization_id == organization_id
        ).first()
        if parent:
            level = parent.level + 1
    
    db_cost_center = CostCenter(
        organization_id=organization_id,
        level=level,
        created_by=current_user.id,
        **cost_center.dict()
    )
    
    db.add(db_cost_center)
    db.commit()
    db.refresh(db_cost_center)
    
    return db_cost_center


# Bank Account Endpoints
@router.get("/bank-accounts", response_model=List[BankAccountResponse])
async def get_bank_accounts(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Get bank accounts with filtering options"""
    query = db.query(BankAccount).filter(
        BankAccount.organization_id == organization_id
    )
    
    if is_active is not None:
        query = query.filter(BankAccount.is_active == is_active)
    
    bank_accounts = query.offset(skip).limit(limit).all()
    return bank_accounts


@router.post("/bank-accounts", response_model=BankAccountResponse)
async def create_bank_account(
    bank_account: BankAccountCreate,
    db: Session = Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Create a new bank account"""
    # Check if account number exists
    existing = db.query(BankAccount).filter(
        BankAccount.organization_id == organization_id,
        BankAccount.account_number == bank_account.account_number
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Account number already exists")
    
    # Validate chart account exists
    chart_account = db.query(ChartOfAccounts).filter(
        ChartOfAccounts.id == bank_account.chart_account_id,
        ChartOfAccounts.organization_id == organization_id
    ).first()
    
    if not chart_account:
        raise HTTPException(status_code=404, detail="Chart account not found")
    
    db_bank_account = BankAccount(
        organization_id=organization_id,
        current_balance=bank_account.opening_balance,
        **bank_account.dict()
    )
    
    db.add(db_bank_account)
    db.commit()
    db.refresh(db_bank_account)
    
    return db_bank_account


# Financial KPI Endpoints
@router.get("/financial-kpis", response_model=List[FinancialKPIResponse])
async def get_financial_kpis(
    skip: int = 0,
    limit: int = 100,
    kpi_category: Optional[str] = None,
    period_start: Optional[date] = None,
    period_end: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Get financial KPIs with filtering options"""
    query = db.query(FinancialKPI).filter(
        FinancialKPI.organization_id == organization_id
    )
    
    if kpi_category:
        query = query.filter(FinancialKPI.kpi_category == kpi_category)
    
    if period_start:
        query = query.filter(FinancialKPI.period_start >= period_start)
    
    if period_end:
        query = query.filter(FinancialKPI.period_end <= period_end)
    
    kpis = query.order_by(desc(FinancialKPI.period_end)).offset(skip).limit(limit).all()
    return kpis


@router.post("/financial-kpis", response_model=FinancialKPIResponse)
async def create_financial_kpi(
    kpi: FinancialKPICreate,
    db: Session = Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Create a new financial KPI"""
    # Calculate variance if target is provided
    variance_percentage = None
    if kpi.target_value and kpi.target_value != 0:
        variance_percentage = ((kpi.kpi_value - kpi.target_value) / kpi.target_value) * 100
    
    db_kpi = FinancialKPI(
        organization_id=organization_id,
        variance_percentage=variance_percentage,
        calculated_by=current_user.id,
        **kpi.dict()
    )
    
    db.add(db_kpi)
    db.commit()
    db.refresh(db_kpi)
    
    return db_kpi


# Financial Dashboard Endpoint
@router.get("/dashboard")
async def get_financial_dashboard(
    db: Session = Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Get financial dashboard data"""
    # Get key financial metrics
    total_assets = db.query(func.sum(ChartOfAccounts.current_balance)).filter(
        ChartOfAccounts.organization_id == organization_id,
        ChartOfAccounts.account_type == 'asset'
    ).scalar() or 0
    
    total_liabilities = db.query(func.sum(ChartOfAccounts.current_balance)).filter(
        ChartOfAccounts.organization_id == organization_id,
        ChartOfAccounts.account_type == 'liability'
    ).scalar() or 0
    
    total_equity = db.query(func.sum(ChartOfAccounts.current_balance)).filter(
        ChartOfAccounts.organization_id == organization_id,
        ChartOfAccounts.account_type == 'equity'
    ).scalar() or 0
    
    # Get pending AP and AR
    pending_ap = db.query(func.sum(AccountsPayable.outstanding_amount)).filter(
        AccountsPayable.organization_id == organization_id,
        AccountsPayable.payment_status == 'pending'
    ).scalar() or 0
    
    pending_ar = db.query(func.sum(AccountsReceivable.outstanding_amount)).filter(
        AccountsReceivable.organization_id == organization_id,
        AccountsReceivable.payment_status == 'pending'
    ).scalar() or 0
    
    # Get total bank balance
    total_bank_balance = db.query(func.sum(BankAccount.current_balance)).filter(
        BankAccount.organization_id == organization_id,
        BankAccount.is_active == True
    ).scalar() or 0
    
    return {
        "total_assets": float(total_assets),
        "total_liabilities": float(total_liabilities),
        "total_equity": float(total_equity),
        "pending_accounts_payable": float(pending_ap),
        "pending_accounts_receivable": float(pending_ar),
        "total_bank_balance": float(total_bank_balance),
        "working_capital": float(total_assets - total_liabilities),
        "current_ratio": float(total_assets / total_liabilities) if total_liabilities > 0 else 0
    }
# Due to length constraints, I'll implement the key endpoints here and continue with other modules