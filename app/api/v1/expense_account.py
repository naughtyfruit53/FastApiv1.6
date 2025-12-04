# app/api/v1/expense_account.py

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func
from typing import List, Optional
from datetime import datetime
from decimal import Decimal
import logging

from app.core.database import get_db
from app.core.enforcement import require_access


from app.models.user_models import User
from app.models.expense_account import ExpenseAccount
from app.schemas.expense_account import (
    ExpenseAccountCreate, ExpenseAccountUpdate, ExpenseAccountResponse, 
    ExpenseAccountList, ExpenseAccountFilter
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/expense-accounts", response_model=ExpenseAccountList)
async def get_expense_accounts(
    page: int = Query(1, ge=1),
    per_page: int = Query(100, ge=1, le=1000),
    ea_filter: ExpenseAccountFilter = Depends(),
    auth: tuple = Depends(require_access("expense_account", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get expense accounts with filtering and pagination"""
    current_user, org_id = auth
    
    try:
        stmt = select(ExpenseAccount).where(ExpenseAccount.organization_id == org_id)
        
        # Apply filters
        if ea_filter.category:
            stmt = stmt.where(ExpenseAccount.category == ea_filter.category)
        
        if ea_filter.parent_account_id is not None:
            stmt = stmt.where(ExpenseAccount.parent_account_id == ea_filter.parent_account_id)
        
        if ea_filter.is_group is not None:
            stmt = stmt.where(ExpenseAccount.is_group == ea_filter.is_group)
        
        if ea_filter.is_active is not None:
            stmt = stmt.where(ExpenseAccount.is_active == ea_filter.is_active)
        
        if ea_filter.search:
            search_term = f"%{ea_filter.search}%"
            stmt = stmt.where(
                or_(
                    ExpenseAccount.account_name.ilike(search_term),
                    ExpenseAccount.account_code.ilike(search_term),
                    ExpenseAccount.description.ilike(search_term)
                )
            )
        
        # Get total count
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await db.execute(count_stmt)
        total = total_result.scalar_one()
        
        # Apply pagination and ordering
        paginated_stmt = stmt.order_by(ExpenseAccount.account_code).offset((page-1)*per_page).limit(per_page)
        result = await db.execute(paginated_stmt)
        accounts = result.scalars().all()
        
        return ExpenseAccountList(
            items=accounts,
            total=total,
            page=page,
            size=per_page,
            pages=(total + per_page - 1) // per_page
        )
        
    except Exception as e:
        logger.error(f"Error fetching expense accounts: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch expense accounts")


@router.post("/expense-accounts", response_model=ExpenseAccountResponse)
async def create_expense_account(
    ea_data: ExpenseAccountCreate,
    auth: tuple = Depends(require_access("expense_account", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Create a new expense account"""
    current_user, org_id = auth
    
    try:
        # Check for duplicate code
        stmt = select(ExpenseAccount).where(
            ExpenseAccount.organization_id == org_id,
            ExpenseAccount.account_code == ea_data.account_code
        )
        existing = await db.execute(stmt)
        if existing.scalars().first():
            raise HTTPException(
                status_code=400,
                detail=f"Expense account with code '{ea_data.account_code}' already exists"
            )
        
        # Verify parent account if provided
        if ea_data.parent_account_id:
            parent_stmt = select(ExpenseAccount).where(
                ExpenseAccount.id == ea_data.parent_account_id,
                ExpenseAccount.organization_id == org_id
            )
            parent = await db.execute(parent_stmt)
            if not parent.scalars().first():
                raise HTTPException(status_code=404, detail="Parent account not found")
        
        # Create expense account
        expense_account = ExpenseAccount(
            organization_id=org_id,
            created_by=current_user.id,
            updated_by=current_user.id,
            **ea_data.model_dump()
        )
        
        db.add(expense_account)
        await db.commit()
        await db.refresh(expense_account)
        
        logger.info(f"Created expense account: {expense_account.account_code} by user {current_user.id}")
        return expense_account
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating expense account: {e}")
        raise HTTPException(status_code=500, detail="Failed to create expense account")


@router.get("/expense-accounts/{account_id}", response_model=ExpenseAccountResponse)
async def get_expense_account(
    account_id: int,
    auth: tuple = Depends(require_access("expense_account", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific expense account"""
    current_user, org_id = auth
    
    try:
        stmt = select(ExpenseAccount).where(
            ExpenseAccount.id == account_id,
            ExpenseAccount.organization_id == org_id
        )
        result = await db.execute(stmt)
        account = result.scalars().first()
        
        if not account:
            raise HTTPException(status_code=404, detail="Expense account not found")
        
        return account
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching expense account {account_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch expense account")


@router.put("/expense-accounts/{account_id}", response_model=ExpenseAccountResponse)
async def update_expense_account(
    account_id: int,
    ea_data: ExpenseAccountUpdate,
    auth: tuple = Depends(require_access("expense_account", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Update an expense account"""
    current_user, org_id = auth
    
    try:
        # Fetch existing account
        stmt = select(ExpenseAccount).where(
            ExpenseAccount.id == account_id,
            ExpenseAccount.organization_id == org_id
        )
        result = await db.execute(stmt)
        account = result.scalars().first()
        
        if not account:
            raise HTTPException(status_code=404, detail="Expense account not found")
        
        # Verify parent account if being updated
        if ea_data.parent_account_id is not None and ea_data.parent_account_id != account.parent_account_id:
            if ea_data.parent_account_id == account_id:
                raise HTTPException(status_code=400, detail="Account cannot be its own parent")
            
            parent_stmt = select(ExpenseAccount).where(
                ExpenseAccount.id == ea_data.parent_account_id,
                ExpenseAccount.organization_id == org_id
            )
            parent = await db.execute(parent_stmt)
            if not parent.scalars().first():
                raise HTTPException(status_code=404, detail="Parent account not found")
        
        # Update fields
        update_data = ea_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(account, field, value)
        
        account.updated_by = current_user.id
        account.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(account)
        
        logger.info(f"Updated expense account {account_id} by user {current_user.id}")
        return account
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating expense account {account_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update expense account")


@router.delete("/expense-accounts/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_expense_account(
    account_id: int,
    auth: tuple = Depends(require_access("expense_account", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Delete an expense account (soft delete by setting is_active=False)"""
    current_user, org_id = auth
    
    try:
        # Fetch existing account
        stmt = select(ExpenseAccount).where(
            ExpenseAccount.id == account_id,
            ExpenseAccount.organization_id == org_id
        )
        result = await db.execute(stmt)
        account = result.scalars().first()
        
        if not account:
            raise HTTPException(status_code=404, detail="Expense account not found")
        
        # Check if account has sub-accounts
        sub_stmt = select(func.count()).where(
            ExpenseAccount.parent_account_id == account_id,
            ExpenseAccount.organization_id == org_id,
            ExpenseAccount.is_active == True
        )
        sub_count = await db.execute(sub_stmt)
        if sub_count.scalar_one() > 0:
            raise HTTPException(
                status_code=400,
                detail="Cannot delete account with active sub-accounts"
            )
        
        # Soft delete
        account.is_active = False
        account.updated_by = current_user.id
        account.updated_at = datetime.utcnow()
        
        await db.commit()
        
        logger.info(f"Deleted expense account {account_id} by user {current_user.id}")
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting expense account {account_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete expense account")
    