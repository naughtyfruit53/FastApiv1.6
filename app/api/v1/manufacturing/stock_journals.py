# app/api/v1/manufacturing/stock_journals.py
"""Stock Journals module - Handles stock journal vouchers"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
import logging

from app.core.database import get_db
from app.api.v1.auth import get_current_active_user
from app.core.enforcement import require_access
from app.models.vouchers.manufacturing_operations import StockJournal, StockJournalEntry
from app.services.voucher_service import VoucherNumberService

logger = logging.getLogger(__name__)
router = APIRouter()


# Pydantic Schemas
class StockJournalEntryCreate(BaseModel):
    product_id: int
    debit_quantity: float = 0.0
    credit_quantity: float = 0.0
    unit: str
    unit_rate: float = 0.0
    from_location: Optional[str] = None
    to_location: Optional[str] = None
    from_warehouse: Optional[str] = None
    to_warehouse: Optional[str] = None
    from_bin: Optional[str] = None
    to_bin: Optional[str] = None
    batch_number: Optional[str] = None
    lot_number: Optional[str] = None
    transformation_type: Optional[str] = None


class StockJournalCreate(BaseModel):
    journal_type: str  # 'transfer', 'assembly', 'disassembly', 'adjustment', 'manufacturing'
    from_location: Optional[str] = None
    to_location: Optional[str] = None
    from_warehouse: Optional[str] = None
    to_warehouse: Optional[str] = None
    manufacturing_order_id: Optional[int] = None
    bom_id: Optional[int] = None
    transfer_reason: Optional[str] = None
    assembly_product_id: Optional[int] = None
    assembly_quantity: Optional[float] = None
    notes: Optional[str] = None
    entries: List[StockJournalEntryCreate] = []


class StockJournalEntryResponse(BaseModel):
    id: int
    product_id: int
    debit_quantity: float
    credit_quantity: float
    unit: str
    unit_rate: float
    debit_value: float
    credit_value: float
    from_location: Optional[str]
    to_location: Optional[str]
    batch_number: Optional[str]
    lot_number: Optional[str]

    class Config:
        from_attributes = True


class StockJournalResponse(BaseModel):
    id: int
    voucher_number: str
    organization_id: int
    journal_type: str
    from_location: Optional[str]
    to_location: Optional[str]
    from_warehouse: Optional[str]
    to_warehouse: Optional[str]
    manufacturing_order_id: Optional[int]
    bom_id: Optional[int]
    transfer_reason: Optional[str]
    status: Optional[str]
    notes: Optional[str]
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


@router.get("", response_model=List[StockJournalResponse])
async def get_stock_journals(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    journal_type: Optional[str] = Query(None, description="Filter by journal type"),
    auth: tuple = Depends(require_access("manufacturing", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get stock journals"""
    current_user, org_id = auth
    try:
        stmt = select(StockJournal).where(
            StockJournal.organization_id == org_id
        )
        if journal_type:
            stmt = stmt.where(StockJournal.journal_type == journal_type)
        stmt = stmt.order_by(StockJournal.created_at.desc()).offset(skip).limit(limit)
        result = await db.execute(stmt)
        journals = result.scalars().all()
        logger.info(f"Fetched {len(journals)} stock journals for organization {org_id}")
        return journals
    except Exception as e:
        logger.error(f"Error fetching stock journals: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch stock journals"
        )


@router.get("/next-number")
async def get_next_stock_journal_number(
    auth: tuple = Depends(require_access("manufacturing", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get next stock journal voucher number"""
    current_user, org_id = auth
    try:
        next_number = await VoucherNumberService.generate_voucher_number_async(
            db, "STJ", org_id, StockJournal
        )
        logger.info(f"Generated next STJ number: {next_number} for organization {org_id}")
        return {"next_number": next_number}
    except Exception as e:
        logger.error(f"Error generating STJ number: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to generate stock journal voucher number"
        )


@router.post("", response_model=StockJournalResponse)
async def create_stock_journal(
    journal_data: StockJournalCreate,
    auth: tuple = Depends(require_access("manufacturing", "write")),
    db: AsyncSession = Depends(get_db)
):
    """Create new stock journal"""
    current_user, org_id = auth
    try:
        # Generate voucher number atomically
        voucher_number = await VoucherNumberService.generate_voucher_number_async(
            db, "STJ", org_id, StockJournal
        )

        db_journal = StockJournal(
            organization_id=org_id,
            voucher_number=voucher_number,
            date=datetime.now(),
            journal_type=journal_data.journal_type,
            from_location=journal_data.from_location,
            to_location=journal_data.to_location,
            from_warehouse=journal_data.from_warehouse,
            to_warehouse=journal_data.to_warehouse,
            manufacturing_order_id=journal_data.manufacturing_order_id,
            bom_id=journal_data.bom_id,
            transfer_reason=journal_data.transfer_reason,
            assembly_product_id=journal_data.assembly_product_id,
            assembly_quantity=journal_data.assembly_quantity,
            notes=journal_data.notes,
            status="draft",
            created_by=current_user.id
        )

        db.add(db_journal)
        await db.flush()

        # Add entries
        for entry_data in journal_data.entries:
            entry = StockJournalEntry(
                organization_id=org_id,
                stock_journal_id=db_journal.id,
                product_id=entry_data.product_id,
                debit_quantity=entry_data.debit_quantity,
                credit_quantity=entry_data.credit_quantity,
                unit=entry_data.unit,
                unit_rate=entry_data.unit_rate,
                debit_value=entry_data.debit_quantity * entry_data.unit_rate,
                credit_value=entry_data.credit_quantity * entry_data.unit_rate,
                from_location=entry_data.from_location,
                to_location=entry_data.to_location,
                from_warehouse=entry_data.from_warehouse,
                to_warehouse=entry_data.to_warehouse,
                from_bin=entry_data.from_bin,
                to_bin=entry_data.to_bin,
                batch_number=entry_data.batch_number,
                lot_number=entry_data.lot_number,
                transformation_type=entry_data.transformation_type
            )
            db.add(entry)

        await db.commit()
        await db.refresh(db_journal)
        logger.info(f"Created stock journal {voucher_number} for organization {org_id}")
        return db_journal

    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating stock journal: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create stock journal: {str(e)}"
        )


@router.get("/{journal_id}", response_model=StockJournalResponse)
async def get_stock_journal(
    journal_id: int,
    auth: tuple = Depends(require_access("manufacturing", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific stock journal"""
    current_user, org_id = auth
    try:
        stmt = select(StockJournal).where(
            StockJournal.id == journal_id,
            StockJournal.organization_id == org_id
        )
        result = await db.execute(stmt)
        journal = result.scalar_one_or_none()
        if not journal:
            raise HTTPException(
                status_code=404,
                detail="Stock journal not found"
            )
        return journal
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching stock journal {journal_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch stock journal"
        )
