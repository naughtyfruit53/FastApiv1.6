# app/api/v1/bom.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
import logging

from app.core.database import get_db
from app.core.security import get_current_user
from app.api.v1.auth import get_current_active_user
from app.models.vouchers import BillOfMaterials, BOMComponent
from app.models import Product
from app.services.voucher_service import VoucherNumberService

logger = logging.getLogger(__name__)
router = APIRouter()


# Pydantic schemas for BOM
from pydantic import BaseModel
from datetime import datetime


class BOMComponentCreate(BaseModel):
    component_item_id: int
    quantity_required: float
    unit: str
    unit_cost: Optional[float] = 0.0
    wastage_percentage: Optional[float] = 0.0
    is_optional: Optional[bool] = False
    sequence: Optional[int] = 0
    notes: Optional[str] = None


class BOMComponentResponse(BOMComponentCreate):
    id: int
    bom_id: int
    organization_id: int
    total_cost: float
    component_item: Optional[dict] = None

    class Config:
        from_attributes = True


class BOMCreate(BaseModel):
    bom_name: str
    output_item_id: int
    output_quantity: Optional[float] = 1.0
    version: Optional[str] = "1.0"
    validity_start: Optional[datetime] = None
    validity_end: Optional[datetime] = None
    description: Optional[str] = None
    notes: Optional[str] = None
    material_cost: Optional[float] = 0.0
    labor_cost: Optional[float] = 0.0
    overhead_cost: Optional[float] = 0.0
    components: List[BOMComponentCreate] = []


class BOMUpdate(BaseModel):
    bom_name: Optional[str] = None
    output_item_id: Optional[int] = None
    output_quantity: Optional[float] = None
    version: Optional[str] = None
    validity_start: Optional[datetime] = None
    validity_end: Optional[datetime] = None
    description: Optional[str] = None
    notes: Optional[str] = None
    material_cost: Optional[float] = None
    labor_cost: Optional[float] = None
    overhead_cost: Optional[float] = None
    is_active: Optional[bool] = None
    components: Optional[List[BOMComponentCreate]] = None


class BOMResponse(BaseModel):
    id: int
    organization_id: int
    bom_name: str
    output_item_id: int
    output_quantity: float
    version: str
    validity_start: Optional[datetime] = None
    validity_end: Optional[datetime] = None
    is_active: bool
    description: Optional[str] = None
    notes: Optional[str] = None
    material_cost: float
    labor_cost: float
    overhead_cost: float
    total_cost: float
    created_at: datetime
    updated_at: Optional[datetime] = None
    output_item: Optional[dict] = None
    components: List[BOMComponentResponse] = []

    class Config:
        from_attributes = True


@router.get("/", response_model=List[BOMResponse])
async def get_boms(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    output_item_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get all BOMs for the organization"""
    query = db.query(BillOfMaterials).filter(
        BillOfMaterials.organization_id == current_user.organization_id
    )
    
    if search:
        query = query.filter(
            BillOfMaterials.bom_name.ilike(f"%{search}%")
        )
    
    if is_active is not None:
        query = query.filter(BillOfMaterials.is_active == is_active)
    
    if output_item_id:
        query = query.filter(BillOfMaterials.output_item_id == output_item_id)
    
    boms = query.offset(skip).limit(limit).all()
    return boms


@router.get("/{bom_id}", response_model=BOMResponse)
async def get_bom(
    bom_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get a specific BOM by ID"""
    bom = db.query(BillOfMaterials).filter(
        BillOfMaterials.id == bom_id,
        BillOfMaterials.organization_id == current_user.organization_id
    ).first()
    
    if not bom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="BOM not found"
        )
    
    return bom


@router.post("/", response_model=BOMResponse)
async def create_bom(
    bom_data: BOMCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Create a new BOM"""
    
    # Check if output item exists
    output_item = db.query(Product).filter(
        Product.id == bom_data.output_item_id,
        Product.organization_id == current_user.organization_id
    ).first()
    
    if not output_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Output item not found"
        )
    
    # Check for duplicate BOM name + version
    existing_bom = db.query(BillOfMaterials).filter(
        BillOfMaterials.organization_id == current_user.organization_id,
        BillOfMaterials.bom_name == bom_data.bom_name,
        BillOfMaterials.version == bom_data.version
    ).first()
    
    if existing_bom:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"BOM '{bom_data.bom_name}' version '{bom_data.version}' already exists"
        )
    
    # Calculate total cost
    material_cost = sum(
        comp.quantity_required * comp.unit_cost * (1 + comp.wastage_percentage / 100)
        for comp in bom_data.components
    )
    total_cost = material_cost + bom_data.labor_cost + bom_data.overhead_cost
    
    # Create BOM
    db_bom = BillOfMaterials(
        organization_id=current_user.organization_id,
        bom_name=bom_data.bom_name,
        output_item_id=bom_data.output_item_id,
        output_quantity=bom_data.output_quantity,
        version=bom_data.version,
        validity_start=bom_data.validity_start,
        validity_end=bom_data.validity_end,
        description=bom_data.description,
        notes=bom_data.notes,
        material_cost=material_cost,
        labor_cost=bom_data.labor_cost,
        overhead_cost=bom_data.overhead_cost,
        total_cost=total_cost,
        created_by=current_user.id
    )
    
    db.add(db_bom)
    db.flush()  # Get the ID
    
    # Create components
    for idx, comp_data in enumerate(bom_data.components):
        # Verify component item exists
        component_item = db.query(Product).filter(
            Product.id == comp_data.component_item_id,
            Product.organization_id == current_user.organization_id
        ).first()
        
        if not component_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Component item ID {comp_data.component_item_id} not found"
            )
        
        total_comp_cost = comp_data.quantity_required * comp_data.unit_cost * (1 + comp_data.wastage_percentage / 100)
        
        component = BOMComponent(
            organization_id=current_user.organization_id,
            bom_id=db_bom.id,
            component_item_id=comp_data.component_item_id,
            quantity_required=comp_data.quantity_required,
            unit=comp_data.unit,
            unit_cost=comp_data.unit_cost,
            total_cost=total_comp_cost,
            wastage_percentage=comp_data.wastage_percentage,
            is_optional=comp_data.is_optional,
            sequence=comp_data.sequence or idx,
            notes=comp_data.notes
        )
        db.add(component)
    
    db.commit()
    db.refresh(db_bom)
    
    return db_bom


@router.put("/{bom_id}", response_model=BOMResponse)
async def update_bom(
    bom_id: int,
    bom_data: BOMUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Update an existing BOM"""
    
    # Get existing BOM
    db_bom = db.query(BillOfMaterials).filter(
        BillOfMaterials.id == bom_id,
        BillOfMaterials.organization_id == current_user.organization_id
    ).first()
    
    if not db_bom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="BOM not found"
        )
    
    # Check if BOM is in use (has manufacturing orders)
    # This is a basic check - in production you might want more sophisticated validation
    from app.models.vouchers import ManufacturingOrder
    in_use = db.query(ManufacturingOrder).filter(
        ManufacturingOrder.bom_id == bom_id,
        ManufacturingOrder.organization_id == current_user.organization_id,
        ManufacturingOrder.production_status.in_(["planned", "in_progress"])
    ).first()
    
    if in_use and bom_data.components is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot modify components of BOM that is currently in use in manufacturing orders"
        )
    
    # Update BOM fields
    update_data = bom_data.dict(exclude_unset=True)
    components_data = update_data.pop('components', None)
    
    for field, value in update_data.items():
        setattr(db_bom, field, value)
    
    # Update components if provided
    if components_data is not None:
        # Delete existing components
        db.query(BOMComponent).filter(BOMComponent.bom_id == bom_id).delete()
        
        # Create new components
        material_cost = 0
        for idx, comp_data in enumerate(components_data):
            # Verify component item exists
            component_item = db.query(Product).filter(
                Product.id == comp_data.component_item_id,
                Product.organization_id == current_user.organization_id
            ).first()
            
            if not component_item:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Component item ID {comp_data.component_item_id} not found"
                )
            
            total_comp_cost = comp_data.quantity_required * comp_data.unit_cost * (1 + comp_data.wastage_percentage / 100)
            material_cost += total_comp_cost
            
            component = BOMComponent(
                organization_id=current_user.organization_id,
                bom_id=db_bom.id,
                component_item_id=comp_data.component_item_id,
                quantity_required=comp_data.quantity_required,
                unit=comp_data.unit,
                unit_cost=comp_data.unit_cost,
                total_cost=total_comp_cost,
                wastage_percentage=comp_data.wastage_percentage,
                is_optional=comp_data.is_optional,
                sequence=comp_data.sequence or idx,
                notes=comp_data.notes
            )
            db.add(component)
        
        # Update material cost
        db_bom.material_cost = material_cost
        db_bom.total_cost = material_cost + db_bom.labor_cost + db_bom.overhead_cost
    
    db.commit()
    db.refresh(db_bom)
    
    return db_bom


@router.delete("/{bom_id}")
async def delete_bom(
    bom_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Delete a BOM (only if not in use)"""
    
    # Get existing BOM
    db_bom = db.query(BillOfMaterials).filter(
        BillOfMaterials.id == bom_id,
        BillOfMaterials.organization_id == current_user.organization_id
    ).first()
    
    if not db_bom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="BOM not found"
        )
    
    # Check if BOM is in use
    from app.models.vouchers import ManufacturingOrder
    in_use = db.query(ManufacturingOrder).filter(
        ManufacturingOrder.bom_id == bom_id,
        ManufacturingOrder.organization_id == current_user.organization_id
    ).first()
    
    if in_use:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete BOM that is in use in manufacturing orders"
        )
    
    # Delete the BOM (components will be deleted due to cascade)
    db.delete(db_bom)
    db.commit()
    
    return {"message": "BOM deleted successfully"}


@router.get("/{bom_id}/cost-breakdown")
async def get_bom_cost_breakdown(
    bom_id: int,
    production_quantity: float = 1.0,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get detailed cost breakdown for a BOM"""
    
    bom = db.query(BillOfMaterials).filter(
        BillOfMaterials.id == bom_id,
        BillOfMaterials.organization_id == current_user.organization_id
    ).first()
    
    if not bom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="BOM not found"
        )
    
    # Calculate costs for the requested production quantity
    multiplier = production_quantity / bom.output_quantity
    
    component_costs = []
    total_material_cost = 0
    
    for component in bom.components:
        required_qty = component.quantity_required * multiplier
        wastage_qty = required_qty * (component.wastage_percentage / 100)
        total_qty = required_qty + wastage_qty
        component_cost = total_qty * component.unit_cost
        
        component_costs.append({
            "component_name": component.component_item.product_name if component.component_item else "Unknown",
            "required_quantity": required_qty,
            "wastage_quantity": wastage_qty,
            "total_quantity": total_qty,
            "unit_cost": component.unit_cost,
            "total_cost": component_cost,
            "unit": component.unit
        })
        
        total_material_cost += component_cost
    
    return {
        "bom_name": bom.bom_name,
        "output_item": bom.output_item.product_name if bom.output_item else "Unknown",
        "production_quantity": production_quantity,
        "cost_breakdown": {
            "material_cost": total_material_cost,
            "labor_cost": bom.labor_cost * multiplier,
            "overhead_cost": bom.overhead_cost * multiplier,
            "total_cost": (total_material_cost + bom.labor_cost + bom.overhead_cost) * multiplier
        },
        "component_costs": component_costs
    }