# app/api/v1/assets.py

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import logging

from app.core.database import get_db
from app.core.security import get_current_user
from app.api.v1.auth import get_current_active_user
from app.models.asset_models import (
    Asset, AssetStatus, AssetCondition, MaintenanceSchedule, MaintenanceRecord, 
    MaintenanceType, MaintenanceStatus, DepreciationRecord, MaintenancePartUsed,
    DepreciationMethod
)
from app.services.voucher_service import VoucherNumberService
from pydantic import BaseModel
from typing import Union

logger = logging.getLogger(__name__)
router = APIRouter()

# Asset Schemas
class AssetCreate(BaseModel):
    asset_code: str
    asset_name: str
    description: Optional[str] = None
    category: str
    subcategory: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    year_of_manufacture: Optional[int] = None
    purchase_cost: Optional[float] = 0.0
    purchase_date: Optional[datetime] = None
    vendor_id: Optional[int] = None
    warranty_start_date: Optional[datetime] = None
    warranty_end_date: Optional[datetime] = None
    location: Optional[str] = None
    department: Optional[str] = None
    assigned_to_employee: Optional[str] = None
    status: AssetStatus = AssetStatus.ACTIVE
    condition: AssetCondition = AssetCondition.GOOD
    specifications: Optional[str] = None
    operating_capacity: Optional[str] = None
    power_rating: Optional[str] = None
    depreciation_method: DepreciationMethod = DepreciationMethod.STRAIGHT_LINE
    useful_life_years: Optional[int] = None
    salvage_value: Optional[float] = 0.0
    depreciation_rate: Optional[float] = None
    insurance_provider: Optional[str] = None
    insurance_policy_number: Optional[str] = None
    insurance_expiry_date: Optional[datetime] = None
    notes: Optional[str] = None

class AssetUpdate(BaseModel):
    asset_name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    location: Optional[str] = None
    department: Optional[str] = None
    assigned_to_employee: Optional[str] = None
    status: Optional[AssetStatus] = None
    condition: Optional[AssetCondition] = None
    specifications: Optional[str] = None
    operating_capacity: Optional[str] = None
    power_rating: Optional[str] = None
    notes: Optional[str] = None

class AssetResponse(BaseModel):
    id: int
    asset_code: str
    asset_name: str
    description: Optional[str] = None
    category: str
    subcategory: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    purchase_cost: Optional[float] = None
    purchase_date: Optional[datetime] = None
    location: Optional[str] = None
    department: Optional[str] = None
    assigned_to_employee: Optional[str] = None
    status: AssetStatus
    condition: AssetCondition
    useful_life_years: Optional[int] = None
    salvage_value: Optional[float] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# Maintenance Schedule Schemas
class MaintenanceScheduleCreate(BaseModel):
    asset_id: int
    schedule_name: str
    maintenance_type: MaintenanceType
    description: Optional[str] = None
    frequency_type: str
    frequency_value: Optional[int] = None
    estimated_duration_hours: Optional[float] = None
    meter_type: Optional[str] = None
    meter_frequency: Optional[float] = None
    estimated_cost: Optional[float] = 0.0
    required_skills: Optional[str] = None
    required_parts: Optional[str] = None
    assigned_technician: Optional[str] = None
    assigned_department: Optional[str] = None
    priority: str = "medium"
    advance_notice_days: int = 7

class MaintenanceScheduleResponse(BaseModel):
    id: int
    asset_id: int
    schedule_name: str
    maintenance_type: MaintenanceType
    description: Optional[str] = None
    frequency_type: str
    frequency_value: Optional[int] = None
    next_due_date: Optional[datetime] = None
    estimated_cost: Optional[float] = None
    priority: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Maintenance Record Schemas
class MaintenancePartUsedCreate(BaseModel):
    product_id: int
    quantity_used: float
    unit: str
    unit_cost: Optional[float] = 0.0
    batch_number: Optional[str] = None
    serial_number: Optional[str] = None
    notes: Optional[str] = None

class MaintenanceRecordCreate(BaseModel):
    asset_id: int
    schedule_id: Optional[int] = None
    maintenance_type: MaintenanceType
    priority: str = "medium"
    scheduled_date: Optional[datetime] = None
    description: str
    work_performed: Optional[str] = None
    findings: Optional[str] = None
    recommendations: Optional[str] = None
    assigned_technician: Optional[str] = None
    performed_by: Optional[str] = None
    supervised_by: Optional[str] = None
    labor_cost: Optional[float] = 0.0
    parts_cost: Optional[float] = 0.0
    external_cost: Optional[float] = 0.0
    meter_reading_before: Optional[float] = None
    meter_reading_after: Optional[float] = None
    condition_before: Optional[AssetCondition] = None
    condition_after: Optional[AssetCondition] = None
    quality_check_passed: bool = True
    quality_remarks: Optional[str] = None
    parts_used: List[MaintenancePartUsedCreate] = []

class MaintenanceRecordResponse(BaseModel):
    id: int
    work_order_number: str
    asset_id: int
    maintenance_type: MaintenanceType
    priority: str
    scheduled_date: Optional[datetime] = None
    actual_start_date: Optional[datetime] = None
    actual_end_date: Optional[datetime] = None
    status: MaintenanceStatus
    description: str
    total_cost: float
    created_at: datetime
    
    class Config:
        from_attributes = True

# Asset Endpoints
@router.get("/assets/", response_model=List[AssetResponse])
async def get_assets(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    status: Optional[AssetStatus] = None,
    location: Optional[str] = None,
    department: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    query = db.query(Asset).filter(
        Asset.organization_id == current_user.organization_id
    )
    
    if category:
        query = query.filter(Asset.category == category)
    if status:
        query = query.filter(Asset.status == status)
    if location:
        query = query.filter(Asset.location == location)
    if department:
        query = query.filter(Asset.department == department)
    
    assets = query.offset(skip).limit(limit).all()
    return assets

@router.post("/assets/", response_model=AssetResponse)
async def create_asset(
    asset_data: AssetCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    # Check if asset code already exists
    existing_asset = db.query(Asset).filter(
        Asset.organization_id == current_user.organization_id,
        Asset.asset_code == asset_data.asset_code
    ).first()
    
    if existing_asset:
        raise HTTPException(
            status_code=400, 
            detail="Asset code already exists"
        )
    
    db_asset = Asset(
        organization_id=current_user.organization_id,
        created_by=current_user.id,
        **asset_data.dict()
    )
    
    db.add(db_asset)
    db.commit()
    db.refresh(db_asset)
    
    return db_asset

@router.get("/assets/{asset_id}", response_model=AssetResponse)
async def get_asset(
    asset_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    asset = db.query(Asset).filter(
        Asset.id == asset_id,
        Asset.organization_id == current_user.organization_id
    ).first()
    
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    return asset

@router.put("/assets/{asset_id}", response_model=AssetResponse)
async def update_asset(
    asset_id: int,
    asset_data: AssetUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    asset = db.query(Asset).filter(
        Asset.id == asset_id,
        Asset.organization_id == current_user.organization_id
    ).first()
    
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    for field, value in asset_data.dict(exclude_unset=True).items():
        setattr(asset, field, value)
    
    db.commit()
    db.refresh(asset)
    
    return asset

@router.delete("/assets/{asset_id}")
async def delete_asset(
    asset_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    asset = db.query(Asset).filter(
        Asset.id == asset_id,
        Asset.organization_id == current_user.organization_id
    ).first()
    
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    db.delete(asset)
    db.commit()
    
    return {"message": "Asset deleted successfully"}

# Asset Categories
@router.get("/assets/categories/")
async def get_asset_categories(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    categories = db.query(Asset.category).filter(
        Asset.organization_id == current_user.organization_id
    ).distinct().all()
    
    return [cat[0] for cat in categories if cat[0]]

# Maintenance Schedule Endpoints
@router.get("/maintenance-schedules/", response_model=List[MaintenanceScheduleResponse])
async def get_maintenance_schedules(
    skip: int = 0,
    limit: int = 100,
    asset_id: Optional[int] = None,
    maintenance_type: Optional[MaintenanceType] = None,
    is_active: Optional[bool] = True,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    query = db.query(MaintenanceSchedule).filter(
        MaintenanceSchedule.organization_id == current_user.organization_id
    )
    
    if asset_id:
        query = query.filter(MaintenanceSchedule.asset_id == asset_id)
    if maintenance_type:
        query = query.filter(MaintenanceSchedule.maintenance_type == maintenance_type)
    if is_active is not None:
        query = query.filter(MaintenanceSchedule.is_active == is_active)
    
    schedules = query.offset(skip).limit(limit).all()
    return schedules

@router.post("/maintenance-schedules/", response_model=MaintenanceScheduleResponse)
async def create_maintenance_schedule(
    schedule_data: MaintenanceScheduleCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    # Verify asset exists
    asset = db.query(Asset).filter(
        Asset.id == schedule_data.asset_id,
        Asset.organization_id == current_user.organization_id
    ).first()
    
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    # Calculate next due date based on frequency
    next_due_date = None
    if schedule_data.frequency_type in ["daily", "weekly", "monthly", "quarterly", "yearly"]:
        days_map = {
            "daily": 1,
            "weekly": 7,
            "monthly": 30,
            "quarterly": 90,
            "yearly": 365
        }
        days = days_map.get(schedule_data.frequency_type, 30)
        if schedule_data.frequency_value:
            days *= schedule_data.frequency_value
        next_due_date = datetime.now() + timedelta(days=days)
    
    db_schedule = MaintenanceSchedule(
        organization_id=current_user.organization_id,
        created_by=current_user.id,
        next_due_date=next_due_date,
        **schedule_data.dict()
    )
    
    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)
    
    return db_schedule

# Due Maintenance
@router.get("/maintenance-schedules/due/", response_model=List[MaintenanceScheduleResponse])
async def get_due_maintenance(
    days_ahead: int = 30,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    due_date = datetime.now() + timedelta(days=days_ahead)
    
    schedules = db.query(MaintenanceSchedule).filter(
        MaintenanceSchedule.organization_id == current_user.organization_id,
        MaintenanceSchedule.is_active == True,
        MaintenanceSchedule.next_due_date <= due_date
    ).all()
    
    return schedules

# Maintenance Record Endpoints
@router.get("/maintenance-records/", response_model=List[MaintenanceRecordResponse])
async def get_maintenance_records(
    skip: int = 0,
    limit: int = 100,
    asset_id: Optional[int] = None,
    maintenance_type: Optional[MaintenanceType] = None,
    status: Optional[MaintenanceStatus] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    query = db.query(MaintenanceRecord).filter(
        MaintenanceRecord.organization_id == current_user.organization_id
    )
    
    if asset_id:
        query = query.filter(MaintenanceRecord.asset_id == asset_id)
    if maintenance_type:
        query = query.filter(MaintenanceRecord.maintenance_type == maintenance_type)
    if status:
        query = query.filter(MaintenanceRecord.status == status)
    
    records = query.order_by(MaintenanceRecord.created_at.desc()).offset(skip).limit(limit).all()
    return records

@router.post("/maintenance-records/", response_model=MaintenanceRecordResponse)
async def create_maintenance_record(
    record_data: MaintenanceRecordCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    # Verify asset exists
    asset = db.query(Asset).filter(
        Asset.id == record_data.asset_id,
        Asset.organization_id == current_user.organization_id
    ).first()
    
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    # Generate work order number
    work_order_number = f"WO-{datetime.now().strftime('%Y%m%d')}-{asset.asset_code}-{asset.id:04d}"
    
    # Calculate total cost
    total_cost = record_data.labor_cost + record_data.parts_cost + record_data.external_cost
    
    db_record = MaintenanceRecord(
        organization_id=current_user.organization_id,
        work_order_number=work_order_number,
        total_cost=total_cost,
        created_by=current_user.id,
        **record_data.dict(exclude={'parts_used'})
    )
    
    db.add(db_record)
    db.flush()
    
    # Add parts used
    for part_data in record_data.parts_used:
        total_cost = part_data.quantity_used * part_data.unit_cost
        part = MaintenancePartUsed(
            organization_id=current_user.organization_id,
            maintenance_record_id=db_record.id,
            total_cost=total_cost,
            **part_data.dict()
        )
        db.add(part)
    
    # Update asset condition if specified
    if record_data.condition_after:
        asset.condition = record_data.condition_after
    
    db.commit()
    db.refresh(db_record)
    
    return db_record

@router.put("/maintenance-records/{record_id}/complete")
async def complete_maintenance_record(
    record_id: int,
    actual_end_date: Optional[datetime] = None,
    work_performed: Optional[str] = None,
    findings: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    record = db.query(MaintenanceRecord).filter(
        MaintenanceRecord.id == record_id,
        MaintenanceRecord.organization_id == current_user.organization_id
    ).first()
    
    if not record:
        raise HTTPException(status_code=404, detail="Maintenance record not found")
    
    record.status = MaintenanceStatus.COMPLETED
    record.actual_end_date = actual_end_date or datetime.now()
    
    if work_performed:
        record.work_performed = work_performed
    if findings:
        record.findings = findings
    
    # Update next due date for related schedule
    if record.schedule_id:
        schedule = db.query(MaintenanceSchedule).filter(
            MaintenanceSchedule.id == record.schedule_id
        ).first()
        
        if schedule and schedule.frequency_type in ["daily", "weekly", "monthly", "quarterly", "yearly"]:
            days_map = {
                "daily": 1,
                "weekly": 7,
                "monthly": 30,
                "quarterly": 90,
                "yearly": 365
            }
            days = days_map.get(schedule.frequency_type, 30)
            if schedule.frequency_value:
                days *= schedule.frequency_value
            schedule.next_due_date = datetime.now() + timedelta(days=days)
            schedule.last_maintenance_date = datetime.now()
    
    db.commit()
    db.refresh(record)
    
    return record

# Asset Depreciation
@router.get("/assets/{asset_id}/depreciation")
async def get_asset_depreciation(
    asset_id: int,
    year: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    asset = db.query(Asset).filter(
        Asset.id == asset_id,
        Asset.organization_id == current_user.organization_id
    ).first()
    
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    query = db.query(DepreciationRecord).filter(
        DepreciationRecord.asset_id == asset_id,
        DepreciationRecord.organization_id == current_user.organization_id
    )
    
    if year:
        query = query.filter(DepreciationRecord.depreciation_year == year)
    
    records = query.order_by(DepreciationRecord.depreciation_year.desc()).all()
    return records

@router.post("/assets/{asset_id}/depreciation")
async def calculate_depreciation(
    asset_id: int,
    year: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    asset = db.query(Asset).filter(
        Asset.id == asset_id,
        Asset.organization_id == current_user.organization_id
    ).first()
    
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    # Check if depreciation already exists for this year
    existing = db.query(DepreciationRecord).filter(
        DepreciationRecord.asset_id == asset_id,
        DepreciationRecord.depreciation_year == year
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400, 
            detail="Depreciation already calculated for this year"
        )
    
    # Calculate depreciation based on method
    if asset.depreciation_method == DepreciationMethod.STRAIGHT_LINE:
        annual_depreciation = (asset.purchase_cost - asset.salvage_value) / asset.useful_life_years
    else:
        # For now, default to straight line
        annual_depreciation = (asset.purchase_cost - asset.salvage_value) / asset.useful_life_years
    
    # Get previous year's record for opening balance
    previous_record = db.query(DepreciationRecord).filter(
        DepreciationRecord.asset_id == asset_id,
        DepreciationRecord.depreciation_year == year - 1
    ).first()
    
    if previous_record:
        opening_book_value = previous_record.closing_book_value
        accumulated_depreciation = previous_record.accumulated_depreciation + annual_depreciation
    else:
        opening_book_value = asset.purchase_cost
        accumulated_depreciation = annual_depreciation
    
    closing_book_value = opening_book_value - annual_depreciation
    
    db_record = DepreciationRecord(
        organization_id=current_user.organization_id,
        asset_id=asset_id,
        depreciation_year=year,
        period_start_date=datetime(year, 1, 1),
        period_end_date=datetime(year, 12, 31),
        opening_book_value=opening_book_value,
        depreciation_amount=annual_depreciation,
        accumulated_depreciation=accumulated_depreciation,
        closing_book_value=closing_book_value,
        depreciation_method=asset.depreciation_method,
        depreciation_rate=asset.depreciation_rate,
        created_by=current_user.id
    )
    
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    
    return db_record

# Asset Dashboard
@router.get("/assets/dashboard/summary")
async def get_asset_dashboard_summary(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    # Total assets by status
    total_assets = db.query(Asset).filter(
        Asset.organization_id == current_user.organization_id
    ).count()
    
    active_assets = db.query(Asset).filter(
        Asset.organization_id == current_user.organization_id,
        Asset.status == AssetStatus.ACTIVE
    ).count()
    
    maintenance_assets = db.query(Asset).filter(
        Asset.organization_id == current_user.organization_id,
        Asset.status == AssetStatus.MAINTENANCE
    ).count()
    
    # Due maintenance count
    due_date = datetime.now() + timedelta(days=7)
    due_maintenance = db.query(MaintenanceSchedule).filter(
        MaintenanceSchedule.organization_id == current_user.organization_id,
        MaintenanceSchedule.is_active == True,
        MaintenanceSchedule.next_due_date <= due_date
    ).count()
    
    # Overdue maintenance
    overdue_maintenance = db.query(MaintenanceSchedule).filter(
        MaintenanceSchedule.organization_id == current_user.organization_id,
        MaintenanceSchedule.is_active == True,
        MaintenanceSchedule.next_due_date < datetime.now()
    ).count()
    
    # Total asset value
    total_value = db.query(Asset).filter(
        Asset.organization_id == current_user.organization_id
    ).with_entities(Asset.purchase_cost).all()
    
    total_asset_value = sum(cost[0] or 0 for cost in total_value)
    
    return {
        "total_assets": total_assets,
        "active_assets": active_assets,
        "maintenance_assets": maintenance_assets,
        "due_maintenance": due_maintenance,
        "overdue_maintenance": overdue_maintenance,
        "total_asset_value": total_asset_value
    }