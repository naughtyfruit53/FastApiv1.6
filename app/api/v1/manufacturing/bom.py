# app/api/v1/manufacturing/bom.py
"""
Bill of Materials (BOM) module - Handles BOM CRUD and calculations
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from datetime import datetime
import logging  # ADDED: Import logging to fix NameError for logger

from app.core.database import get_db
from app.api.v1.auth import get_current_active_user
from app.core.enforcement import require_access
from app.models.vouchers.manufacturing_planning import BillOfMaterials, BOMComponent  # FIXED: Use full path to manufacturing_planning.py where the models are defined
from app.schemas.manufacturing import BillOfMaterialsCreate, BillOfMaterialsResponse, BOMComponentCreate
from app.services.mrp_service import MRPService
from app.models.product_models import Product
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter()

# BOM Response Schema
class BOMResponse(BaseModel):
    id: int
    bom_name: str
    output_item_id: int
    output_quantity: float
    version: str
    is_active: bool
    description: Optional[str] = None
    material_cost: float
    labor_cost: float
    overhead_cost: float
    total_cost: float
    created_by: int

    class Config:
        from_attributes = True

@router.get("", response_model=List[BOMResponse])
async def get_boms(
    skip: int = 0,
    limit: int = 100,
    product_id: Optional[int] = Query(None, description="Filter by output product ID"),
    auth: tuple = Depends(require_access("manufacturing", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get list of Bills of Materials"""
    current_user, org_id = auth
    
    stmt = select(BillOfMaterials).where(
        BillOfMaterials.organization_id == org_id
    )
    
    if product_id:
        stmt = stmt.where(BillOfMaterials.output_item_id == product_id)
    
    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    boms = result.scalars().all()
    
    if product_id and not boms:
        raise HTTPException(status_code=404, detail="No BOM found for this product")
    
    return boms

@router.post("", response_model=BillOfMaterialsResponse)
async def create_bom(
    bom_data: BillOfMaterialsCreate,
    auth: tuple = Depends(require_access("manufacturing", "write")),
    db: AsyncSession = Depends(get_db)
):
    current_user, org_id = auth
    db_bom = BillOfMaterials(
        organization_id=org_id,
        bom_name=bom_data.bom_name,
        output_item_id=bom_data.output_item_id,
        output_quantity=bom_data.output_quantity,
        version=bom_data.version,
        is_active=True,
        description=bom_data.description,
        material_cost=0.0,  # To be calculated
        labor_cost=0.0,
        overhead_cost=0.0,
        total_cost=0.0,
        created_by=current_user.id
    )
    db.add(db_bom)
    await db.flush()
    
    # Add components and calculate costs
    material_cost = 0.0
    for comp_data in bom_data.components or []:
        stmt = select(Product.unit_price).where(Product.id == comp_data.component_item_id)
        result = await db.execute(stmt)
        unit_price = result.scalar() or 0.0
        
        total_comp_cost = comp_data.quantity_required * unit_price
        material_cost += total_comp_cost
        
        comp = BOMComponent(
            organization_id=org_id,
            bom_id=db_bom.id,
            component_item_id=comp_data.component_item_id,
            quantity_required=comp_data.quantity_required,
            unit=comp_data.unit,
            unit_cost=unit_price,
            total_cost=total_comp_cost,
            wastage_percentage=comp_data.wastage_percentage,
            is_optional=comp_data.is_optional,
            sequence=comp_data.sequence,
            notes=comp_data.notes
        )
        db.add(comp)
    
    db_bom.material_cost = material_cost
    db_bom.total_cost = material_cost  # Add labor/overhead if available
    
    await db.commit()
    await db.refresh(db_bom)
    return db_bom

@router.post("/{bom_id}/clone")
async def clone_bom(
    bom_id: int,
    new_name: str,
    new_version: Optional[str] = None,
    auth: tuple = Depends(require_access("manufacturing", "create")),
    db: AsyncSession = Depends(get_db)
):
    """Clone an existing BOM with all its components"""
    current_user, org_id = auth
    
    # Get source BOM
    stmt = select(BillOfMaterials).where(
        BillOfMaterials.id == bom_id,
        BillOfMaterials.organization_id == org_id
    )
    result = await db.execute(stmt)
    source_bom = result.scalar_one_or_none()

    if not source_bom:
        raise HTTPException(status_code=404, detail="Source BOM not found")

    # Create new BOM
    new_bom = BillOfMaterials(
        organization_id=org_id,
        bom_name=new_name,
        output_item_id=source_bom.output_item_id,
        output_quantity=source_bom.output_quantity,
        version=new_version or "1.0",
        is_active=True,
        description=f"Cloned from {source_bom.bom_name} v{source_bom.version}",
        notes=source_bom.notes,
        material_cost=source_bom.material_cost,
        labor_cost=source_bom.labor_cost,
        overhead_cost=source_bom.overhead_cost,
        total_cost=source_bom.total_cost,
        created_by=current_user.id
    )

    db.add(new_bom)
    await db.flush()

    # Clone components
    stmt = select(BOMComponent).where(
        BOMComponent.bom_id == bom_id,
        BOMComponent.organization_id == org_id
    )
    result = await db.execute(stmt)
    source_components = result.scalars().all()

    for source_comp in source_components:
        new_comp = BOMComponent(
            organization_id=org_id,
            bom_id=new_bom.id,
            component_item_id=source_comp.component_item_id,
            quantity_required=source_comp.quantity_required,
            unit=source_comp.unit,
            unit_cost=source_comp.unit_cost,
            total_cost=source_comp.total_cost,
            wastage_percentage=source_comp.wastage_percentage,
            is_optional=source_comp.is_optional,
            sequence=source_comp.sequence,
            notes=source_comp.notes
        )
        db.add(new_comp)

    await db.commit()
    await db.refresh(new_bom)

    return {
        'id': new_bom.id,
        'bom_name': new_bom.bom_name,
        'version': new_bom.version,
        'output_item_id': new_bom.output_item_id,
        'components_cloned': len(source_components),
        'message': f"BOM cloned successfully as '{new_name}'"
    }

@router.get("/{bom_id}/cost-breakdown")
async def get_cost_breakdown(
    bom_id: int,
    production_quantity: float = 1.0,
    auth: tuple = Depends(require_access("manufacturing", "read")),
    db: AsyncSession = Depends(get_db)
):
    current_user, org_id = auth
    stmt = select(BillOfMaterials).where(
        BillOfMaterials.id == bom_id,
        BillOfMaterials.organization_id == org_id
    )
    result = await db.execute(stmt)
    bom = result.scalar_one_or_none()
    if not bom:
        raise HTTPException(404, "BOM not found")
    
    stmt = select(BOMComponent).where(BOMComponent.bom_id == bom_id)
    result = await db.execute(stmt)
    components = result.scalars().all()
    
    multiplier = production_quantity / bom.output_quantity
    material_cost = 0.0
    for c in components:
        stmt = select(Product.unit_price).where(Product.id == c.component_item_id)
        result = await db.execute(stmt)
        unit_price = result.scalar() or 0.0
        material_cost += c.quantity_required * multiplier * unit_price
    
    labor_cost = 0.0  # Assume or calculate
    overhead_cost = 0.0  # Assume or calculate
    total_cost = material_cost + labor_cost + overhead_cost
    
    return {
        "cost_breakdown": {
            "material_cost": material_cost,
            "labor_cost": labor_cost,
            "overhead_cost": overhead_cost,
            "total_cost": total_cost
        }
    }

@router.get("/{bom_id}/max-producible")
async def get_max_producible(
    bom_id: int,
    auth: tuple = Depends(require_access("manufacturing", "read")),
    db: AsyncSession = Depends(get_db)
):
    current_user, org_id = auth
    max_p = await MRPService.calculate_max_producible(db, org_id, bom_id)
    return {"max_producible": max_p}

@router.get("/{bom_id}/check-producible")
async def check_producible(
    bom_id: int,
    quantity: float,
    auth: tuple = Depends(require_access("manufacturing", "read")),
    db: AsyncSession = Depends(get_db)
):
    current_user, org_id = auth
    info = await MRPService.check_producible(db, org_id, bom_id, quantity)
    return info