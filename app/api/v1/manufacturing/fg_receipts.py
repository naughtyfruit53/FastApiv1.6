# app/api/v1/manufacturing/fg_receipts.py
"""
Finished Good Receipt module - Handles FG Receipt vouchers with integration tiles
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel
import json
import logging

from app.core.database import get_db
from app.api.v1.auth import get_current_active_user
from app.core.enforcement import require_access
from app.models.vouchers.manufacturing_operations import (
    FinishedGoodReceipt,
    FinishedGoodReceiptItem,
    FGReceiptCostDetail,
    FGReceiptAudit
)
from app.services.voucher_service import VoucherNumberService

logger = logging.getLogger(__name__)
router = APIRouter()


# Pydantic Schemas
class FGReceiptItemCreate(BaseModel):
    product_id: int
    quantity: float
    unit: str
    unit_cost: float = 0.0
    batch_number: Optional[str] = None
    lot_number: Optional[str] = None
    qc_status: Optional[str] = "pending"
    qc_remarks: Optional[str] = None


class FGReceiptCreate(BaseModel):
    manufacturing_order_id: Optional[int] = None
    bom_id: Optional[int] = None
    receipt_date: datetime
    production_batch_number: Optional[str] = None
    lot_number: Optional[str] = None
    expected_quantity: float = 0.0
    received_quantity: float = 0.0
    accepted_quantity: float = 0.0
    rejected_quantity: float = 0.0
    warehouse_location: Optional[str] = None
    bin_location: Optional[str] = None
    notes: Optional[str] = None
    items: List[FGReceiptItemCreate] = []


class FGReceiptResponse(BaseModel):
    id: int
    voucher_number: str
    organization_id: int
    manufacturing_order_id: Optional[int]
    bom_id: Optional[int]
    receipt_date: datetime
    production_batch_number: Optional[str]
    lot_number: Optional[str]
    expected_quantity: float
    received_quantity: float
    accepted_quantity: float
    rejected_quantity: float
    qc_status: Optional[str]
    inventory_posted: bool
    base_cost: float
    total_cost: float
    unit_cost: float
    status: Optional[str]
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


class InventoryUpdateResponse(BaseModel):
    receipt_id: int
    voucher_number: str
    inventory_posted: bool
    posted_at: Optional[datetime]
    posted_by: Optional[int]
    items: List[Dict[str, Any]]
    summary: Dict[str, Any]


class AuditTrailResponse(BaseModel):
    id: int
    action: str
    action_by: int
    action_at: datetime
    before_json: Optional[Dict[str, Any]]
    after_json: Optional[Dict[str, Any]]
    notes: Optional[str]

    class Config:
        from_attributes = True


class CostCalculationResponse(BaseModel):
    receipt_id: int
    voucher_number: str
    base_cost: float
    material_cost: float
    labor_cost: float
    overhead_cost: float
    freight_cost: float
    duty_cost: float
    total_cost: float
    unit_cost: float
    cost_details: List[Dict[str, Any]]


class CostDetailCreate(BaseModel):
    cost_type: str
    description: Optional[str] = None
    amount: float
    allocation_basis: Optional[str] = None
    allocation_value: float = 0.0


# Helper function to log audit
async def log_fg_receipt_audit(
    db: AsyncSession,
    org_id: int,
    receipt_id: int,
    action: str,
    user_id: int,
    before_state: Optional[dict] = None,
    after_state: Optional[dict] = None,
    notes: Optional[str] = None,
    ip_address: Optional[str] = None
):
    audit = FGReceiptAudit(
        organization_id=org_id,
        receipt_id=receipt_id,
        action=action,
        action_by=user_id,
        before_json=before_state,
        after_json=after_state,
        notes=notes,
        ip_address=ip_address
    )
    db.add(audit)


@router.get("", response_model=List[FGReceiptResponse])
async def get_fg_receipts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status: Optional[str] = Query(None),
    auth: tuple = Depends(require_access("manufacturing", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get finished good receipts"""
    current_user, org_id = auth
    try:
        stmt = select(FinishedGoodReceipt).where(
            FinishedGoodReceipt.organization_id == org_id
        )
        if status:
            stmt = stmt.where(FinishedGoodReceipt.status == status)
        stmt = stmt.order_by(FinishedGoodReceipt.created_at.desc()).offset(skip).limit(limit)
        result = await db.execute(stmt)
        receipts = result.scalars().all()
        return receipts
    except Exception as e:
        logger.error(f"Error fetching FG receipts: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch FG receipts")


@router.get("/next-number")
async def get_next_fg_receipt_number(
    auth: tuple = Depends(require_access("manufacturing", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get next FG receipt voucher number"""
    current_user, org_id = auth
    try:
        next_number = await VoucherNumberService.generate_voucher_number_async(
            db, "FGR", org_id, FinishedGoodReceipt
        )
        return {"next_number": next_number}
    except Exception as e:
        logger.error(f"Error generating FGR number: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate FG receipt number")


@router.post("", response_model=FGReceiptResponse)
async def create_fg_receipt(
    receipt_data: FGReceiptCreate,
    auth: tuple = Depends(require_access("manufacturing", "write")),
    db: AsyncSession = Depends(get_db)
):
    """Create new finished good receipt"""
    current_user, org_id = auth
    try:
        voucher_number = await VoucherNumberService.generate_voucher_number_async(
            db, "FGR", org_id, FinishedGoodReceipt
        )

        db_receipt = FinishedGoodReceipt(
            organization_id=org_id,
            voucher_number=voucher_number,
            date=datetime.now(),
            manufacturing_order_id=receipt_data.manufacturing_order_id,
            bom_id=receipt_data.bom_id,
            receipt_date=receipt_data.receipt_date,
            production_batch_number=receipt_data.production_batch_number,
            lot_number=receipt_data.lot_number,
            expected_quantity=receipt_data.expected_quantity,
            received_quantity=receipt_data.received_quantity,
            accepted_quantity=receipt_data.accepted_quantity,
            rejected_quantity=receipt_data.rejected_quantity,
            warehouse_location=receipt_data.warehouse_location,
            bin_location=receipt_data.bin_location,
            notes=receipt_data.notes,
            status="draft",
            created_by=current_user.id
        )

        db.add(db_receipt)
        await db.flush()

        total_cost = 0.0
        for item_data in receipt_data.items:
            item_total = item_data.quantity * item_data.unit_cost
            total_cost += item_total
            
            item = FinishedGoodReceiptItem(
                organization_id=org_id,
                receipt_id=db_receipt.id,
                product_id=item_data.product_id,
                quantity=item_data.quantity,
                unit=item_data.unit,
                unit_cost=item_data.unit_cost,
                total_cost=item_total,
                batch_number=item_data.batch_number,
                lot_number=item_data.lot_number,
                qc_status=item_data.qc_status,
                qc_remarks=item_data.qc_remarks
            )
            db.add(item)

        db_receipt.total_cost = total_cost
        db_receipt.unit_cost = total_cost / receipt_data.received_quantity if receipt_data.received_quantity > 0 else 0

        # Log audit
        await log_fg_receipt_audit(
            db, org_id, db_receipt.id, "create", current_user.id,
            after_state={"voucher_number": voucher_number, "status": "draft"},
            notes="FG Receipt created"
        )

        await db.commit()
        await db.refresh(db_receipt)
        return db_receipt

    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating FG receipt: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create FG receipt: {str(e)}")


@router.get("/{receipt_id}", response_model=FGReceiptResponse)
async def get_fg_receipt(
    receipt_id: int,
    auth: tuple = Depends(require_access("manufacturing", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific FG receipt"""
    current_user, org_id = auth
    try:
        stmt = select(FinishedGoodReceipt).options(
            joinedload(FinishedGoodReceipt.items)
        ).where(
            FinishedGoodReceipt.id == receipt_id,
            FinishedGoodReceipt.organization_id == org_id
        )
        result = await db.execute(stmt)
        receipt = result.unique().scalar_one_or_none()
        if not receipt:
            raise HTTPException(status_code=404, detail="FG receipt not found")
        return receipt
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching FG receipt {receipt_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch FG receipt")


# ============== Integration Tile Endpoints ==============

@router.get("/{receipt_id}/inventory-update", response_model=InventoryUpdateResponse)
async def get_inventory_update(
    receipt_id: int,
    auth: tuple = Depends(require_access("manufacturing", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get inventory update status and details for FG receipt (Inventory Update Tile)"""
    current_user, org_id = auth
    try:
        stmt = select(FinishedGoodReceipt).options(
            joinedload(FinishedGoodReceipt.items)
        ).where(
            FinishedGoodReceipt.id == receipt_id,
            FinishedGoodReceipt.organization_id == org_id
        )
        result = await db.execute(stmt)
        receipt = result.unique().scalar_one_or_none()
        
        if not receipt:
            raise HTTPException(status_code=404, detail="FG receipt not found")

        items_data = []
        for item in receipt.items:
            items_data.append({
                "product_id": item.product_id,
                "quantity": item.quantity,
                "unit": item.unit,
                "batch_number": item.batch_number,
                "lot_number": item.lot_number,
                "qc_status": item.qc_status
            })

        return InventoryUpdateResponse(
            receipt_id=receipt.id,
            voucher_number=receipt.voucher_number,
            inventory_posted=receipt.inventory_posted,
            posted_at=receipt.inventory_posted_at,
            posted_by=receipt.inventory_posted_by,
            items=items_data,
            summary={
                "total_items": len(receipt.items),
                "received_quantity": receipt.received_quantity,
                "accepted_quantity": receipt.accepted_quantity,
                "rejected_quantity": receipt.rejected_quantity,
                "status": receipt.status
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting inventory update for FG receipt {receipt_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get inventory update")


@router.post("/{receipt_id}/inventory-update/trigger")
async def trigger_inventory_update(
    receipt_id: int,
    auth: tuple = Depends(require_access("manufacturing", "write")),
    db: AsyncSession = Depends(get_db)
):
    """Trigger/re-trigger inventory update for FG receipt"""
    current_user, org_id = auth
    try:
        stmt = select(FinishedGoodReceipt).options(
            joinedload(FinishedGoodReceipt.items)
        ).where(
            FinishedGoodReceipt.id == receipt_id,
            FinishedGoodReceipt.organization_id == org_id
        )
        result = await db.execute(stmt)
        receipt = result.unique().scalar_one_or_none()
        
        if not receipt:
            raise HTTPException(status_code=404, detail="FG receipt not found")
        
        if receipt.status not in ["draft", "approved"]:
            raise HTTPException(status_code=400, detail="Cannot update inventory for this receipt status")

        # Update stock for each item
        from app.models import Stock
        for item in receipt.items:
            if item.qc_status == "rejected":
                continue  # Skip rejected items
                
            stock_stmt = select(Stock).where(
                Stock.product_id == item.product_id,
                Stock.organization_id == org_id
            )
            stock_result = await db.execute(stock_stmt)
            stock = stock_result.scalar_one_or_none()
            
            if not stock:
                stock = Stock(
                    product_id=item.product_id,
                    organization_id=org_id,
                    quantity=item.quantity,
                    unit=item.unit
                )
                db.add(stock)
            else:
                stock.quantity += item.quantity

        receipt.inventory_posted = True
        receipt.inventory_posted_at = datetime.now()
        receipt.inventory_posted_by = current_user.id
        receipt.status = "posted"

        # Log audit
        await log_fg_receipt_audit(
            db, org_id, receipt.id, "post", current_user.id,
            before_state={"inventory_posted": False},
            after_state={"inventory_posted": True, "status": "posted"},
            notes="Inventory updated"
        )

        await db.commit()
        return {"message": "Inventory updated successfully", "receipt_id": receipt.id}

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error triggering inventory update for FG receipt {receipt_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to trigger inventory update")


@router.get("/{receipt_id}/audit-trail", response_model=List[AuditTrailResponse])
async def get_audit_trail(
    receipt_id: int,
    action: Optional[str] = Query(None, description="Filter by action type"),
    user_id: Optional[int] = Query(None, description="Filter by user"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    auth: tuple = Depends(require_access("manufacturing", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get audit trail for FG receipt (Audit Trail Tile)"""
    current_user, org_id = auth
    try:
        # Verify receipt exists and belongs to org
        stmt = select(FinishedGoodReceipt).where(
            FinishedGoodReceipt.id == receipt_id,
            FinishedGoodReceipt.organization_id == org_id
        )
        result = await db.execute(stmt)
        receipt = result.scalar_one_or_none()
        if not receipt:
            raise HTTPException(status_code=404, detail="FG receipt not found")

        # Get audit records
        audit_stmt = select(FGReceiptAudit).where(
            FGReceiptAudit.receipt_id == receipt_id,
            FGReceiptAudit.organization_id == org_id
        )
        
        if action:
            audit_stmt = audit_stmt.where(FGReceiptAudit.action == action)
        if user_id:
            audit_stmt = audit_stmt.where(FGReceiptAudit.action_by == user_id)
        if start_date:
            audit_stmt = audit_stmt.where(FGReceiptAudit.action_at >= start_date)
        if end_date:
            audit_stmt = audit_stmt.where(FGReceiptAudit.action_at <= end_date)
        
        audit_stmt = audit_stmt.order_by(FGReceiptAudit.action_at.desc())
        audit_stmt = audit_stmt.offset((page - 1) * per_page).limit(per_page)
        
        result = await db.execute(audit_stmt)
        audits = result.scalars().all()
        return audits

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting audit trail for FG receipt {receipt_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get audit trail")


@router.get("/{receipt_id}/cost-calc", response_model=CostCalculationResponse)
async def get_cost_calculation(
    receipt_id: int,
    auth: tuple = Depends(require_access("manufacturing", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get cost calculation breakdown for FG receipt (Cost Calculation Tile)"""
    current_user, org_id = auth
    try:
        stmt = select(FinishedGoodReceipt).options(
            joinedload(FinishedGoodReceipt.cost_details)
        ).where(
            FinishedGoodReceipt.id == receipt_id,
            FinishedGoodReceipt.organization_id == org_id
        )
        result = await db.execute(stmt)
        receipt = result.unique().scalar_one_or_none()
        
        if not receipt:
            raise HTTPException(status_code=404, detail="FG receipt not found")

        cost_details_data = []
        for detail in receipt.cost_details:
            cost_details_data.append({
                "id": detail.id,
                "cost_type": detail.cost_type,
                "description": detail.description,
                "amount": detail.amount,
                "allocation_basis": detail.allocation_basis,
                "allocation_value": detail.allocation_value
            })

        return CostCalculationResponse(
            receipt_id=receipt.id,
            voucher_number=receipt.voucher_number,
            base_cost=receipt.base_cost,
            material_cost=receipt.material_cost,
            labor_cost=receipt.labor_cost,
            overhead_cost=receipt.overhead_cost,
            freight_cost=receipt.freight_cost,
            duty_cost=receipt.duty_cost,
            total_cost=receipt.total_cost,
            unit_cost=receipt.unit_cost,
            cost_details=cost_details_data
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting cost calculation for FG receipt {receipt_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get cost calculation")


@router.post("/{receipt_id}/cost-calc/recalculate", response_model=CostCalculationResponse)
async def recalculate_cost(
    receipt_id: int,
    cost_details: List[CostDetailCreate] = [],
    auth: tuple = Depends(require_access("manufacturing", "write")),
    db: AsyncSession = Depends(get_db)
):
    """Recalculate costs for FG receipt"""
    current_user, org_id = auth
    try:
        stmt = select(FinishedGoodReceipt).options(
            joinedload(FinishedGoodReceipt.items),
            joinedload(FinishedGoodReceipt.cost_details)
        ).where(
            FinishedGoodReceipt.id == receipt_id,
            FinishedGoodReceipt.organization_id == org_id
        )
        result = await db.execute(stmt)
        receipt = result.unique().scalar_one_or_none()
        
        if not receipt:
            raise HTTPException(status_code=404, detail="FG receipt not found")

        # Store old state for audit
        old_state = {
            "base_cost": receipt.base_cost,
            "material_cost": receipt.material_cost,
            "labor_cost": receipt.labor_cost,
            "overhead_cost": receipt.overhead_cost,
            "total_cost": receipt.total_cost,
            "unit_cost": receipt.unit_cost
        }

        # Clear existing cost details if new ones provided
        if cost_details:
            from sqlalchemy import delete
            await db.execute(delete(FGReceiptCostDetail).where(
                FGReceiptCostDetail.receipt_id == receipt_id
            ))

            material_cost = 0.0
            labor_cost = 0.0
            overhead_cost = 0.0
            freight_cost = 0.0
            duty_cost = 0.0

            for detail in cost_details:
                cost_detail = FGReceiptCostDetail(
                    organization_id=org_id,
                    receipt_id=receipt.id,
                    cost_type=detail.cost_type,
                    description=detail.description,
                    amount=detail.amount,
                    allocation_basis=detail.allocation_basis,
                    allocation_value=detail.allocation_value,
                    created_by=current_user.id
                )
                db.add(cost_detail)

                if detail.cost_type == "material":
                    material_cost += detail.amount
                elif detail.cost_type == "labor":
                    labor_cost += detail.amount
                elif detail.cost_type == "overhead":
                    overhead_cost += detail.amount
                elif detail.cost_type == "freight":
                    freight_cost += detail.amount
                elif detail.cost_type == "duty":
                    duty_cost += detail.amount

            receipt.material_cost = material_cost
            receipt.labor_cost = labor_cost
            receipt.overhead_cost = overhead_cost
            receipt.freight_cost = freight_cost
            receipt.duty_cost = duty_cost

        # Calculate base cost from items
        base_cost = sum(item.total_cost for item in receipt.items)
        receipt.base_cost = base_cost

        # Calculate total cost
        total_cost = (
            receipt.base_cost +
            receipt.material_cost +
            receipt.labor_cost +
            receipt.overhead_cost +
            receipt.freight_cost +
            receipt.duty_cost
        )
        receipt.total_cost = total_cost
        receipt.unit_cost = total_cost / receipt.received_quantity if receipt.received_quantity > 0 else 0

        # Log audit
        await log_fg_receipt_audit(
            db, org_id, receipt.id, "recalculate", current_user.id,
            before_state=old_state,
            after_state={
                "base_cost": receipt.base_cost,
                "material_cost": receipt.material_cost,
                "labor_cost": receipt.labor_cost,
                "overhead_cost": receipt.overhead_cost,
                "total_cost": receipt.total_cost,
                "unit_cost": receipt.unit_cost
            },
            notes="Cost recalculated"
        )

        await db.commit()
        await db.refresh(receipt)

        # Build response
        cost_details_data = []
        for detail in receipt.cost_details:
            cost_details_data.append({
                "id": detail.id,
                "cost_type": detail.cost_type,
                "description": detail.description,
                "amount": detail.amount,
                "allocation_basis": detail.allocation_basis,
                "allocation_value": detail.allocation_value
            })

        return CostCalculationResponse(
            receipt_id=receipt.id,
            voucher_number=receipt.voucher_number,
            base_cost=receipt.base_cost,
            material_cost=receipt.material_cost,
            labor_cost=receipt.labor_cost,
            overhead_cost=receipt.overhead_cost,
            freight_cost=receipt.freight_cost,
            duty_cost=receipt.duty_cost,
            total_cost=receipt.total_cost,
            unit_cost=receipt.unit_cost,
            cost_details=cost_details_data
        )

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error recalculating cost for FG receipt {receipt_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to recalculate cost")
