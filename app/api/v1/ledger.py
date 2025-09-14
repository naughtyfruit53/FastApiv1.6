# app/api/v1/ledger.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.api.v1.auth import get_current_active_user
from app.models.user_models import User
from app.models.vouchers.sales import SalesVoucher
from app.models.vouchers.financial import ReceiptVoucher, CreditNote, DebitNote
from app.models.vouchers.purchase import PurchaseVoucher
from app.models.vouchers.financial import PaymentVoucher

router = APIRouter(tags=["ledger"])

@router.get("/balances/{entity_type}/{entity_id}")
async def get_entity_balance(
    entity_type: str,
    entity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    org_id = current_user.organization_id
    
    if entity_type.lower() == "customer":
        # Customer balance: receivables positive
        sales = db.query(func.sum(SalesVoucher.total_amount)).filter(
            SalesVoucher.customer_id == entity_id,
            SalesVoucher.organization_id == org_id
        ).scalar() or 0
        
        receipts = db.query(func.sum(ReceiptVoucher.total_amount)).filter(
            ReceiptVoucher.customer_id == entity_id,
            ReceiptVoucher.organization_id == org_id
        ).scalar() or 0
        
        credit_notes = db.query(func.sum(CreditNote.total_amount)).filter(
            CreditNote.customer_id == entity_id,
            CreditNote.organization_id == org_id
        ).scalar() or 0
        
        debit_notes = db.query(func.sum(DebitNote.total_amount)).filter(
            DebitNote.customer_id == entity_id,
            DebitNote.organization_id == org_id
        ).scalar() or 0
        
        balance = sales - receipts - credit_notes + debit_notes
        return {"balance": balance}
    
    elif entity_type.lower() == "vendor":
        # Vendor balance: payables positive
        purchases = db.query(func.sum(PurchaseVoucher.total_amount)).filter(
            PurchaseVoucher.vendor_id == entity_id,
            PurchaseVoucher.organization_id == org_id
        ).scalar() or 0
        
        payments = db.query(func.sum(PaymentVoucher.total_amount)).filter(
            PaymentVoucher.vendor_id == entity_id,
            PaymentVoucher.organization_id == org_id
        ).scalar() or 0
        
        credit_notes = db.query(func.sum(CreditNote.total_amount)).filter(
            CreditNote.vendor_id == entity_id,
            CreditNote.organization_id == org_id
        ).scalar() or 0
        
        debit_notes = db.query(func.sum(DebitNote.total_amount)).filter(
            DebitNote.vendor_id == entity_id,
            DebitNote.organization_id == org_id
        ).scalar() or 0
        
        balance = purchases - payments + credit_notes - debit_notes
        return {"balance": balance}
    
    elif entity_type.lower() == "employee":
        # Placeholder for employee balance (e.g., from payroll)
        return {"balance": 0}
    
    else:
        raise HTTPException(status_code=400, detail="Invalid entity type")

@router.get("/vouchers/balance/{voucher_ref}")
async def get_voucher_balance(
    voucher_ref: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    org_id = current_user.organization_id
    
    if voucher_ref.startswith('SV/'):  # Sales Voucher
        voucher = db.query(SalesVoucher).filter(
            SalesVoucher.voucher_number == voucher_ref,
            SalesVoucher.organization_id == org_id
        ).first()
        
        if not voucher:
            raise HTTPException(status_code=404, detail="Voucher not found")
        
        # Placeholder: assume no linked payments, outstanding = total_amount
        # In full implementation, subtract sum of allocated receipts
        outstanding = voucher.total_amount
        return {"outstanding": outstanding}
    
    # Add similar for other voucher types like PV/ for Purchase
    else:
        raise HTTPException(status_code=400, detail="Invalid voucher reference")