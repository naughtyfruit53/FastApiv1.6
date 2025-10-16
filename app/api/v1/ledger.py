# app/api/v1/ledger.py

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any

from app.db.session import get_db
from app.services.ledger_service import LedgerService
from app.schemas.ledger import (
    LedgerFilters, CompleteLedgerResponse,
    OutstandingLedgerResponse
)
from app.core.security import get_current_user
from app.models.user_models import User

router = APIRouter(
    prefix="/ledger",
    tags=["Ledger"]
)

@router.get("/complete", response_model=CompleteLedgerResponse)
async def get_complete_ledger(
    filters: LedgerFilters = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get complete ledger with all transactions
    """
    try:
        organization_id = current_user.organization_id
        return await LedgerService.get_complete_ledger(db, organization_id, filters)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating complete ledger"
        )

@router.get("/outstanding", response_model=OutstandingLedgerResponse)
async def get_outstanding_ledger(
    account_type: str = Query(None, alias="account_type"),
    account_id: int = Query(None, alias="account_id"),
    voucher_type: str = Query("all", alias="voucher_type"),
    start_date: str = Query(None, alias="start_date"),
    end_date: str = Query(None, alias="end_date"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get outstanding ledger with balances
    """
    try:
        organization_id = current_user.organization_id
        filters = LedgerFilters(
            account_type=account_type,
            account_id=account_id,
            voucher_type=voucher_type,
            start_date=start_date,
            end_date=end_date
        )
        return await LedgerService.get_outstanding_ledger(db, organization_id, filters)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating outstanding ledger"
        )

@router.get("/balances/{entity_type}/{entity_id}", response_model=Dict[str, Any])
async def get_entity_balance(
    entity_type: str,
    entity_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get outstanding balance for a specific vendor or customer
    """
    try:
        organization_id = current_user.organization_id
        filters = LedgerFilters(account_type=entity_type.lower(), account_id=entity_id)
        ledger_response = await LedgerService.get_outstanding_ledger(db, organization_id, filters)
        
        # Find the matching balance
        for balance in ledger_response.outstanding_balances:
            if balance.account_type == entity_type.lower() and balance.account_id == entity_id:
                return {
                    "account_type": balance.account_type,
                    "account_id": balance.account_id,
                    "account_name": balance.account_name,
                    "outstanding_amount": float(balance.outstanding_amount),
                    "last_transaction_date": balance.last_transaction_date,
                    "transaction_count": balance.transaction_count,
                    "contact_info": balance.contact_info
                }
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No balance found for {entity_type} with ID {entity_id}"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching balance for {entity_type}/{entity_id}: {str(e)}"
        )

@router.get("/chart-of-accounts", response_model=List[Dict[str, Any]])
async def get_chart_of_accounts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get chart of accounts (temporarily here; consider moving to chart_of_accounts.py if separate)
    """
    try:
        organization_id = current_user.organization_id
        return await LedgerService.get_chart_of_accounts(db, organization_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching chart of accounts"
        )

@router.post("/chart-of-accounts/standard")
async def create_standard_chart_of_accounts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create standard chart of accounts (temporarily here; consider moving to chart_of_accounts.py if separate)
    """
    try:
        organization_id = current_user.organization_id
        await LedgerService.create_standard_chart_of_accounts(db, organization_id)
        return {"message": "Standard chart of accounts created successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating standard chart of accounts"
        )