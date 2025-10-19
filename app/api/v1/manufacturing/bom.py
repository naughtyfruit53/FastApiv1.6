# app/api/v1/manufacturing/bom.py
"""Bill of Materials module"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from app.core.database import get_db
from app.api.v1.auth import get_current_active_user
from app.models.vouchers import BillOfMaterials
from pydantic import BaseModel

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
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get list of Bills of Materials"""
    stmt = select(BillOfMaterials).where(
        BillOfMaterials.organization_id == current_user.organization_id
    ).offset(skip).limit(limit)
    result = await db.execute(stmt)
    boms = result.scalars().all()
    return boms

@router.post("/{bom_id}/clone")
async def clone_bom(
    bom_id: int,
    new_name: str,
    new_version: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Clone an existing BOM with all its components"""
    # Get source BOM
    stmt = select(BillOfMaterials).where(
        BillOfMaterials.id == bom_id,
        BillOfMaterials.organization_id == current_user.organization_id
    )
    result = await db.execute(stmt)
    source_bom = result.scalar_one_or_none()

    if not source_bom:
        raise HTTPException(status_code=404, detail="Source BOM not found")

    # Create new BOM
    new_bom = BillOfMaterials(
        organization_id=current_user.organization_id,
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
    from app.models.vouchers import BOMComponent
    stmt = select(BOMComponent).where(
        BOMComponent.bom_id == bom_id,
        BOMComponent.organization_id == current_user.organization_id
    )
    result = await db.execute(stmt)
    source_components = result.scalars().all()

    for source_comp in source_components:
        new_comp = BOMComponent(
            organization_id=current_user.organization_id,
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