# app/api/v1/ledger.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
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
def get_complete_ledger(
    filters: LedgerFilters = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get complete ledger with all transactions
    """
    try:
        organization_id = current_user.organization_id
        return LedgerService.get_complete_ledger(db, organization_id, filters)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating complete ledger"
        )

@router.get("/outstanding", response_model=OutstandingLedgerResponse)
def get_outstanding_ledger(
    filters: LedgerFilters = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get outstanding ledger with balances
    """
    try:
        organization_id = current_user.organization_id
        return LedgerService.get_outstanding_ledger(db, organization_id, filters)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating outstanding ledger"
        )

@router.get("/chart-of-accounts", response_model=List[Dict[str, Any]])
def get_chart_of_accounts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get chart of accounts (temporarily here; consider moving to chart_of_accounts.py if separate)
    """
    try:
        organization_id = current_user.organization_id
        return LedgerService.get_chart_of_accounts(db, organization_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching chart of accounts"
        )

@router.post("/chart-of-accounts/standard")
def create_standard_chart_of_accounts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create standard chart of accounts (temporarily here; consider moving to chart_of_accounts.py if separate)
    """
    try:
        organization_id = current_user.organization_id
        LedgerService.create_standard_chart_of_accounts(db, organization_id)
        return {"message": "Standard chart of accounts created successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating standard chart of accounts"
        )