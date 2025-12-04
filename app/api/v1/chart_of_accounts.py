# app/api/v1/chart_of_accounts.py

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func
from typing import List, Optional
from datetime import datetime
from decimal import Decimal
import logging
from fastapi import HTTPException

from app.core.database import get_db
from app.core.enforcement import require_access

from app.models.user_models import User
from app.models.erp_models import ChartOfAccounts
from app.schemas.master_data import (
    ChartOfAccountsCreate, ChartOfAccountsUpdate, ChartOfAccountsResponse, ChartOfAccountsList, ChartOfAccountsFilter
)
from app.services.ledger_service import LedgerService
from pydantic import ValidationError
from app.api.v1.auth import get_current_active_user  # Added import for get_current_active_user

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/chart-of-accounts", response_model=ChartOfAccountsList)
async def get_chart_of_accounts(
    page: int = Query(1, ge=1),
    per_page: int = Query(100, ge=1, le=1000),
    coa_filter: ChartOfAccountsFilter = Depends(),
    auth: tuple = Depends(require_access("chart_of_accounts", "read")),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)  # Added current_user param
):
    """Get chart of accounts with filtering and pagination"""
    current_user, org_id = auth
    
    try:
        stmt = select(ChartOfAccounts).where(ChartOfAccounts.organization_id == org_id)
        
        # Apply filters
        if coa_filter.account_type:
            stmt = stmt.where(ChartOfAccounts.account_type == coa_filter.account_type.value.upper())
        
        if coa_filter.parent_account_id is not None:
            stmt = stmt.where(ChartOfAccounts.parent_account_id == coa_filter.parent_account_id)
        
        if coa_filter.is_group is not None:
            stmt = stmt.where(ChartOfAccounts.is_group == coa_filter.is_group)
        
        if coa_filter.is_active is not None:
            stmt = stmt.where(ChartOfAccounts.is_active == coa_filter.is_active)
        
        if coa_filter.search:
            search_term = f"%{coa_filter.search}%"
            stmt = stmt.where(
                or_(
                    ChartOfAccounts.account_name.ilike(search_term),
                    ChartOfAccounts.account_code.ilike(search_term),
                    ChartOfAccounts.description.ilike(search_term)
                )
            )
        
        # Get total count
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await db.execute(count_stmt)
        total = total_result.scalar_one()
        
        # Apply pagination and ordering
        paginated_stmt = stmt.order_by(ChartOfAccounts.account_code).offset((page-1)*per_page).limit(per_page)
        result = await db.execute(paginated_stmt)
        accounts = result.scalars().all()
        
        return ChartOfAccountsList(
            items=accounts,
            total=total,
            page=page,
            size=per_page,
            pages=(total + per_page - 1) // per_page
        )
        
    except Exception as e:
        logger.error(f"Error fetching chart of accounts: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch chart of accounts")


@router.post("/chart-of-accounts", response_model=ChartOfAccountsResponse)
async def create_chart_of_account(
    coa_data: ChartOfAccountsCreate,
    auth: tuple = Depends(require_access("chart_of_accounts", "create")),
    db: AsyncSession = Depends(get_db)
):
    """Create a new chart of account"""
    current_user, org_id = auth
    
    try:
        logger.info(f"master_data.py validator loaded - received raw account_type: {coa_data.account_type}")
        # Generate code if not provided or empty
        account_code = coa_data.account_code.strip() if coa_data.account_code else ""
        if not account_code:
            account_code = await LedgerService.generate_account_code(db, org_id, coa_data.account_type.upper())
        
        # Check for duplicate code
        existing_stmt = select(ChartOfAccounts).where(
            ChartOfAccounts.organization_id == org_id,
            ChartOfAccounts.account_code == account_code
        )
        existing_result = await db.execute(existing_stmt)
        existing = existing_result.scalars().first()
        
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Account with code '{account_code}' already exists"
            )
        
        # Validate parent account if specified
        level = 0
        if coa_data.parent_account_id:
            parent_stmt = select(ChartOfAccounts).where(
                ChartOfAccounts.id == coa_data.parent_account_id,
                ChartOfAccounts.organization_id == org_id
            )
            parent_result = await db.execute(parent_stmt)
            parent = parent_result.scalars().first()
            
            if not parent:
                raise HTTPException(status_code=404, detail="Parent account not found")
            
            level = parent.level + 1
        
        # Create account
        account = ChartOfAccounts(
            organization_id=org_id,
            account_code=account_code,
            account_name=coa_data.account_name,
            account_type=coa_data.account_type.upper(),
            parent_account_id=coa_data.parent_account_id,
            level=level,
            is_group=coa_data.is_group,
            opening_balance=coa_data.opening_balance,
            current_balance=coa_data.opening_balance,
            is_reconcilable=coa_data.is_reconcilable,
            description=coa_data.description,
            notes=coa_data.notes,
            created_by=current_user.id
        )
        
        db.add(account)
        await db.commit()
        await db.refresh(account)
        
        logger.info(f"Account created: {account.account_name} (ID: {account.id})")
        return account
        
    except ValidationError as ve:
        logger.error(f"Validation error: {ve}")
        raise HTTPException(status_code=422, detail=str(ve))
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating account: {e}")
        raise HTTPException(status_code=500, detail="Failed to create account")


@router.get("/chart-of-accounts/get-next-code")
async def get_next_account_code(
    account_type: str = Query(..., alias="type", description="Account type for code generation"),
    auth: tuple = Depends(require_access("chart_of_accounts", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get next suggested account code for a type"""
    current_user, org_id = auth
    
    try:
        logger.info(f"Generating next account code for type: {account_type}, org: {org_id}")
        next_code = await LedgerService.generate_account_code(db, org_id, account_type.upper())
        logger.info(f"Generated next code: {next_code}")
        return {"next_code": next_code}
    except Exception as e:
        logger.error(f"Error generating next account code: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate next account code")


@router.get("/chart-of-accounts/{account_id}", response_model=ChartOfAccountsResponse)
async def get_chart_of_account(
    account_id: int,
    auth: tuple = Depends(require_access("chart_of_accounts", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific chart of account"""
    current_user, org_id = auth
    
    stmt = select(ChartOfAccounts).where(
        ChartOfAccounts.id == account_id,
        ChartOfAccounts.organization_id == org_id
    )
    result = await db.execute(stmt)
    account = result.scalars().first()
    
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    return account


@router.put("/chart-of-accounts/{account_id}", response_model=ChartOfAccountsResponse)
async def update_chart_of_account(
    account_id: int,
    coa_data: ChartOfAccountsUpdate,
    auth: tuple = Depends(require_access("chart_of_accounts", "update")),
    db: AsyncSession = Depends(get_db)
):
    """Update a chart of account"""
    current_user, org_id = auth
    
    try:
        stmt = select(ChartOfAccounts).where(
            ChartOfAccounts.id == account_id,
            ChartOfAccounts.organization_id == org_id
        )
        result = await db.execute(stmt)
        account = result.scalars().first()
        
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        # Check for duplicate code if being updated
        if coa_data.account_code and coa_data.account_code != account.account_code:
            existing_stmt = select(ChartOfAccounts).where(
                ChartOfAccounts.organization_id == org_id,
                ChartOfAccounts.account_code == coa_data.account_code,
                ChartOfAccounts.id != account_id
            )
            existing_result = await db.execute(existing_stmt)
            existing = existing_result.scalars().first()
            
            if existing:
                raise HTTPException(
                    status_code=400,
                    detail=f"Account with code '{coa_data.account_code}' already exists"
                )
        
        # Update fields
        update_fields = coa_data.dict(exclude_unset=True)
        if "account_type" in update_fields:
            update_fields["account_type"] = update_fields["account_type"].value.upper()
        for field, value in update_fields.items():
            setattr(account, field, value)
        
        account.updated_by = current_user.id
        
        await db.commit()
        await db.refresh(account)
        
        logger.info(f"Account updated: {account.account_name} (ID: {account.id})")
        return account
        
    except ValidationError as ve:
        logger.error(f"Validation error: {ve}")
        raise HTTPException(status_code=422, detail=str(ve))
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating account: {e}")
        raise HTTPException(status_code=500, detail="Failed to update account")


@router.delete("/chart-of-accounts/{account_id}")
async def delete_chart_of_account(
    account_id: int,
    auth: tuple = Depends(require_access("chart_of_accounts", "delete")),
    db: AsyncSession = Depends(get_db)
):
    """Delete a chart of account"""
    current_user, org_id = auth
    
    try:
        stmt = select(ChartOfAccounts).where(
            ChartOfAccounts.id == account_id,
            ChartOfAccounts.organization_id == org_id
        )
        result = await db.execute(stmt)
        account = result.scalars().first()
        
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        # Check for sub-accounts
        sub_stmt = select(func.count()).select_from(select(ChartOfAccounts).where(ChartOfAccounts.parent_account_id == account_id).subquery())
        sub_result = await db.execute(sub_stmt)
        sub_accounts = sub_result.scalar_one()
        if sub_accounts > 0:
            raise HTTPException(
                status_code=400,
                detail="Cannot delete account with sub-accounts"
            )
        
        await db.delete(account)
        await db.commit()
        
        logger.info(f"Account deleted: {account.account_name} (ID: {account.id})")
        return {"message": "Account deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting account: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete account")


@router.get("/chart-of-accounts/payroll-eligible", response_model=ChartOfAccountsList)
async def get_payroll_eligible_accounts(
    page: int = Query(1, ge=1),
    per_page: int = Query(100, ge=1, le=1000),
    account_types: List[str] = Query(["expense", "liability"], description="Account types eligible for payroll"),
    component_type: Optional[str] = Query(None, description="Filter by component type"),
    is_active: bool = Query(True, description="Filter active accounts"),
    auth: tuple = Depends(require_access("chart_of_accounts", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get chart of accounts eligible for payroll component mapping"""
    current_user, org_id = auth
    
    try:
        # Valid account types for payroll
        valid_payroll_types = ["expense", "liability", "asset"]
        
        # Filter to only valid account types
        filtered_types = [t.upper() for t in account_types if t.lower() in valid_payroll_types]
        
        if not filtered_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid account types. Valid types for payroll: {', '.join(valid_payroll_types)}"
            )
        
        stmt = select(ChartOfAccounts).where(
            ChartOfAccounts.organization_id == org_id,
            ChartOfAccounts.account_type.in_(filtered_types),
            ChartOfAccounts.is_active == is_active,
            ChartOfAccounts.can_post == True  # Only accounts that can have transactions posted
        )
        
        # Apply component type specific filtering
        if component_type:
            if component_type in ["earning", "deduction"]:
                # For earnings and deductions, prefer expense accounts
                stmt = stmt.where(ChartOfAccounts.account_type == "EXPENSE")
            elif component_type == "employer_contribution":
                # For employer contributions, prefer liability accounts (for payables)
                stmt = stmt.where(ChartOfAccounts.account_type == "LIABILITY")
        
        # Get total count
        count_stmt = select(func.count()).select_from(stmt.subquery())
        count_result = await db.execute(count_stmt)
        total = count_result.scalar_one()
        
        # Apply pagination and ordering
        paginated_stmt = stmt.order_by(
            ChartOfAccounts.account_type,
            ChartOfAccounts.account_code
        ).offset((page - 1) * per_page).limit(per_page)
        result = await db.execute(paginated_stmt)
        accounts = result.scalars().all()
        
        logger.info(f"Retrieved {len(accounts)} payroll-eligible accounts for organization {org_id}")
        
        return ChartOfAccountsList(
            items=accounts,
            total=total,
            page=page,
            size=per_page,
            pages=(total + per_page - 1) // per_page
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching payroll-eligible accounts: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching payroll-eligible accounts"
        )


@router.get("/chart-of-accounts/lookup")
async def chart_accounts_lookup(
    search: str = Query(None, description="Search term for account name or code"),
    account_types: Optional[List[str]] = Query(None, description="Filter by account types"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of results"),
    auth: tuple = Depends(require_access("chart_of_accounts", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Lookup chart of accounts for dropdown/autocomplete components"""
    current_user, org_id = auth
    
    try:
        stmt = select(ChartOfAccounts).where(
            ChartOfAccounts.organization_id == org_id,
            ChartOfAccounts.is_active == True
        )
        
        # Apply search filter
        if search:
            search_term = f"%{search}%"
            stmt = stmt.where(
                or_(
                    ChartOfAccounts.account_name.ilike(search_term),
                    ChartOfAccounts.account_code.ilike(search_term)
                )
            )
        
        # Apply account type filter
        if account_types:
            account_types = [t.upper() for t in account_types]
            stmt = stmt.where(ChartOfAccounts.account_type.in_(account_types))
        
        # Get results with limit
        limited_stmt = stmt.order_by(ChartOfAccounts.account_code).limit(limit)
        result = await db.execute(limited_stmt)
        accounts = result.scalars().all()
        
        # Return simplified format for lookups
        results = [
            {
                "id": account.id,
                "account_code": account.account_code,
                "account_name": account.account_name,
                "account_type": account.account_type,
                "display_name": f"{account.account_code} - {account.account_name}"
            }
            for account in accounts
        ]
        
        return {"accounts": results, "count": len(results)}
        
    except Exception as e:
        logger.error(f"Error in chart accounts lookup: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error performing account lookup"
        )

# Add alias route for /expense-accounts (maps to chart-of-accounts with filter)
@router.get("/expense-accounts", response_model=ChartOfAccountsList)
async def get_expense_accounts(
    page: int = Query(1, ge=1),
    per_page: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None),
    auth: tuple = Depends(require_access("chart_of_accounts", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Alias for expense accounts (filter chart-of-accounts by expense type)"""
    current_user, org_id = auth
    
    coa_filter = ChartOfAccountsFilter(account_type="EXPENSE", search=search)
    return await get_chart_of_accounts(
        page=page,
        per_page=per_page,
        coa_filter=coa_filter,
        auth=auth,
        db=db
    )
