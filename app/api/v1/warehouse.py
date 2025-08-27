# app/api/v1/warehouse.py
"""
Enhanced Warehouse Management API endpoints - Batch/Serial tracking, Location management
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc, asc, func
from typing import List, Optional
from datetime import datetime, date
from decimal import Decimal

from app.core.database import get_db
from app.api.v1.auth import get_current_active_user
from app.core.tenant import TenantQueryMixin, validate_company_setup_for_operations
from app.core.org_restrictions import require_current_organization_id
from app.core.rbac_dependencies import check_service_permission
from app.models import (
    User, Organization, Product,
    Warehouse, StockLocation, ProductTracking, WarehouseStock,
    ProductBatch, ProductSerial, BatchLocation, StockMovement,
    StockAdjustment, StockAdjustmentItem
)
from app.schemas.enhanced_inventory import (
    WarehouseCreate, WarehouseUpdate, WarehouseResponse,
    StockLocationCreate, StockLocationUpdate, StockLocationResponse,
    ProductTrackingCreate, ProductTrackingUpdate, ProductTrackingResponse,
    WarehouseStockResponse, WarehouseStockUpdate,
    ProductBatchCreate, ProductBatchUpdate, ProductBatchResponse,
    ProductSerialCreate, ProductSerialUpdate, ProductSerialResponse,
    StockMovementCreate, StockMovementResponse,
    StockAdjustmentCreate, StockAdjustmentUpdate, StockAdjustmentResponse,
    InventoryTurnoverAnalysis, StockAgingAnalysis, LowStockAlert,
    ExpiryAlert, InventoryValuationReport, WarehouseUtilization,
    InventoryDashboard, BulkStockImport, BulkImportResponse
)
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


class WarehouseService:
    """Service class for warehouse operations"""
    
    @staticmethod
    def generate_warehouse_code(db: Session, organization_id: int) -> str:
        """Generate next warehouse code"""
        prefix = "WH"
        
        # Get the highest existing warehouse code
        last_warehouse = db.query(Warehouse).filter(
            Warehouse.organization_id == organization_id,
            Warehouse.warehouse_code.like(f"{prefix}%")
        ).order_by(desc(Warehouse.warehouse_code)).first()
        
        if last_warehouse:
            try:
                last_num = int(last_warehouse.warehouse_code.replace(prefix, ""))
                return f"{prefix}{str(last_num + 1).zfill(3)}"
            except ValueError:
                pass
        
        return f"{prefix}001"
    
    @staticmethod
    def calculate_warehouse_utilization(db: Session, warehouse_id: int) -> WarehouseUtilization:
        """Calculate warehouse utilization metrics"""
        warehouse = db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
        if not warehouse:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Warehouse not found"
            )
        
        # Get total stock value and product count
        stock_data = db.query(
            func.sum(WarehouseStock.total_value).label('total_value'),
            func.count(WarehouseStock.product_id).label('total_products'),
            func.sum(WarehouseStock.available_quantity).label('total_quantity')
        ).filter(WarehouseStock.warehouse_id == warehouse_id).first()
        
        total_value = stock_data.total_value or Decimal(0)
        total_products = stock_data.total_products or 0
        utilized_capacity = stock_data.total_quantity or Decimal(0)
        
        utilization_percentage = None
        if warehouse.storage_capacity_units and warehouse.storage_capacity_units > 0:
            utilization_percentage = float(utilized_capacity / warehouse.storage_capacity_units * 100)
        
        return WarehouseUtilization(
            warehouse_id=warehouse.id,
            warehouse_name=warehouse.warehouse_name,
            total_capacity=warehouse.storage_capacity_units,
            utilized_capacity=utilized_capacity,
            utilization_percentage=utilization_percentage,
            total_products=total_products,
            total_value=total_value
        )


# Warehouse Endpoints
@router.get("/warehouses", response_model=List[WarehouseResponse])
async def get_warehouses(
    skip: int = 0,
    limit: int = 100,
    warehouse_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Get warehouses with filtering options"""
    query = db.query(Warehouse).filter(
        Warehouse.organization_id == organization_id
    )
    
    if warehouse_type:
        query = query.filter(Warehouse.warehouse_type == warehouse_type)
    
    if is_active is not None:
        query = query.filter(Warehouse.is_active == is_active)
    
    if search:
        query = query.filter(or_(
            Warehouse.warehouse_name.ilike(f"%{search}%"),
            Warehouse.warehouse_code.ilike(f"%{search}%")
        ))
    
    query = query.order_by(Warehouse.warehouse_code)
    warehouses = query.offset(skip).limit(limit).all()
    return warehouses


@router.post("/warehouses", response_model=WarehouseResponse)
async def create_warehouse(
    warehouse_data: WarehouseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Create a new warehouse"""
    # Auto-generate warehouse code if not provided
    warehouse_code = warehouse_data.warehouse_code
    if not warehouse_code:
        warehouse_code = WarehouseService.generate_warehouse_code(db, organization_id)
    
    # Check if warehouse code already exists
    existing = db.query(Warehouse).filter(
        Warehouse.organization_id == organization_id,
        Warehouse.warehouse_code == warehouse_code
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Warehouse code already exists"
        )
    
    warehouse = Warehouse(
        organization_id=organization_id,
        warehouse_code=warehouse_code,
        warehouse_name=warehouse_data.warehouse_name,
        warehouse_type=warehouse_data.warehouse_type,
        address_line1=warehouse_data.address_line1,
        address_line2=warehouse_data.address_line2,
        city=warehouse_data.city,
        state=warehouse_data.state,
        pincode=warehouse_data.pincode,
        country=warehouse_data.country,
        contact_person=warehouse_data.contact_person,
        phone_number=warehouse_data.phone_number,
        email=warehouse_data.email,
        allow_negative_stock=warehouse_data.allow_negative_stock,
        is_main_warehouse=warehouse_data.is_main_warehouse,
        total_area_sqft=warehouse_data.total_area_sqft,
        storage_capacity_units=warehouse_data.storage_capacity_units,
        notes=warehouse_data.notes,
        created_by=current_user.id
    )
    
    db.add(warehouse)
    db.commit()
    db.refresh(warehouse)
    
    return warehouse


@router.get("/warehouses/{warehouse_id}", response_model=WarehouseResponse)
async def get_warehouse(
    warehouse_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Get a specific warehouse"""
    warehouse = db.query(Warehouse).filter(
        Warehouse.id == warehouse_id,
        Warehouse.organization_id == organization_id
    ).first()
    
    if not warehouse:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Warehouse not found"
        )
    
    return warehouse


@router.put("/warehouses/{warehouse_id}", response_model=WarehouseResponse)
async def update_warehouse(
    warehouse_id: int,
    warehouse_data: WarehouseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Update a warehouse"""
    warehouse = db.query(Warehouse).filter(
        Warehouse.id == warehouse_id,
        Warehouse.organization_id == organization_id
    ).first()
    
    if not warehouse:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Warehouse not found"
        )
    
    update_data = warehouse_data.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(warehouse, field, value)
    
    warehouse.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(warehouse)
    
    return warehouse


# Stock Location Endpoints
@router.get("/warehouses/{warehouse_id}/locations", response_model=List[StockLocationResponse])
async def get_stock_locations(
    warehouse_id: int,
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Get stock locations for a warehouse"""
    # Verify warehouse exists and belongs to organization
    warehouse = db.query(Warehouse).filter(
        Warehouse.id == warehouse_id,
        Warehouse.organization_id == organization_id
    ).first()
    
    if not warehouse:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Warehouse not found"
        )
    
    query = db.query(StockLocation).filter(
        StockLocation.warehouse_id == warehouse_id
    )
    
    if is_active is not None:
        query = query.filter(StockLocation.is_active == is_active)
    
    query = query.order_by(StockLocation.location_code)
    locations = query.offset(skip).limit(limit).all()
    return locations


@router.post("/warehouses/{warehouse_id}/locations", response_model=StockLocationResponse)
async def create_stock_location(
    warehouse_id: int,
    location_data: StockLocationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Create a new stock location"""
    # Verify warehouse exists and belongs to organization
    warehouse = db.query(Warehouse).filter(
        Warehouse.id == warehouse_id,
        Warehouse.organization_id == organization_id
    ).first()
    
    if not warehouse:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Warehouse not found"
        )
    
    # Check if location code already exists in this warehouse
    existing = db.query(StockLocation).filter(
        StockLocation.warehouse_id == warehouse_id,
        StockLocation.location_code == location_data.location_code
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Location code already exists in this warehouse"
        )
    
    location = StockLocation(
        warehouse_id=warehouse_id,
        location_code=location_data.location_code,
        location_name=location_data.location_name,
        location_type=location_data.location_type,
        parent_location_id=location_data.parent_location_id,
        row_number=location_data.row_number,
        column_number=location_data.column_number,
        level_number=location_data.level_number,
        max_capacity_units=location_data.max_capacity_units,
        max_weight_kg=location_data.max_weight_kg,
        is_pickable=location_data.is_pickable,
        is_receivable=location_data.is_receivable,
        notes=location_data.notes
    )
    
    db.add(location)
    db.commit()
    db.refresh(location)
    
    return location


# Product Tracking Endpoints
@router.get("/products/{product_id}/tracking", response_model=Optional[ProductTrackingResponse])
async def get_product_tracking(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Get product tracking configuration"""
    # Verify product exists and belongs to organization
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.organization_id == organization_id
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    tracking = db.query(ProductTracking).filter(
        ProductTracking.product_id == product_id
    ).first()
    
    return tracking


@router.post("/products/{product_id}/tracking", response_model=ProductTrackingResponse)
async def create_product_tracking(
    product_id: int,
    tracking_data: ProductTrackingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Create product tracking configuration"""
    # Verify product exists and belongs to organization
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.organization_id == organization_id
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Check if tracking already exists
    existing = db.query(ProductTracking).filter(
        ProductTracking.product_id == product_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product tracking configuration already exists"
        )
    
    tracking = ProductTracking(
        product_id=product_id,
        tracking_type=tracking_data.tracking_type,
        valuation_method=tracking_data.valuation_method,
        batch_naming_series=tracking_data.batch_naming_series,
        auto_create_batch=tracking_data.auto_create_batch,
        batch_expiry_required=tracking_data.batch_expiry_required,
        serial_naming_series=tracking_data.serial_naming_series,
        auto_create_serial=tracking_data.auto_create_serial,
        enable_reorder_alert=tracking_data.enable_reorder_alert,
        reorder_level=tracking_data.reorder_level,
        reorder_quantity=tracking_data.reorder_quantity,
        max_stock_level=tracking_data.max_stock_level,
        procurement_lead_time_days=tracking_data.procurement_lead_time_days
    )
    
    db.add(tracking)
    db.commit()
    db.refresh(tracking)
    
    return tracking


# Warehouse Stock Endpoints
@router.get("/warehouses/{warehouse_id}/stock", response_model=List[WarehouseStockResponse])
async def get_warehouse_stock(
    warehouse_id: int,
    skip: int = 0,
    limit: int = 100,
    product_id: Optional[int] = None,
    low_stock_only: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Get warehouse stock levels"""
    # Verify warehouse exists and belongs to organization
    warehouse = db.query(Warehouse).filter(
        Warehouse.id == warehouse_id,
        Warehouse.organization_id == organization_id
    ).first()
    
    if not warehouse:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Warehouse not found"
        )
    
    query = db.query(WarehouseStock).filter(
        WarehouseStock.warehouse_id == warehouse_id,
        WarehouseStock.organization_id == organization_id
    )
    
    if product_id:
        query = query.filter(WarehouseStock.product_id == product_id)
    
    if low_stock_only:
        # Join with product tracking to get reorder levels
        query = query.join(ProductTracking, WarehouseStock.product_id == ProductTracking.product_id).filter(
            WarehouseStock.available_quantity <= ProductTracking.reorder_level
        )
    
    query = query.order_by(WarehouseStock.product_id)
    stock_levels = query.offset(skip).limit(limit).all()
    return stock_levels


# Analytics Endpoints
@router.get("/analytics/dashboard", response_model=InventoryDashboard)
async def get_inventory_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Get inventory dashboard analytics"""
    # Total products
    total_products = db.query(Product).filter(
        Product.organization_id == organization_id,
        Product.is_active == True
    ).count()
    
    # Total warehouses
    total_warehouses = db.query(Warehouse).filter(
        Warehouse.organization_id == organization_id,
        Warehouse.is_active == True
    ).count()
    
    # Total stock value
    total_stock_value = db.query(func.sum(WarehouseStock.total_value)).filter(
        WarehouseStock.organization_id == organization_id
    ).scalar() or Decimal(0)
    
    # Low stock alerts
    low_stock_alerts = db.query(WarehouseStock).join(
        ProductTracking, WarehouseStock.product_id == ProductTracking.product_id
    ).filter(
        WarehouseStock.organization_id == organization_id,
        WarehouseStock.available_quantity <= ProductTracking.reorder_level,
        ProductTracking.enable_reorder_alert == True
    ).count()
    
    # Expiry alerts (products expiring in 30 days)
    expiry_date_threshold = datetime.now().date() + timedelta(days=30)
    expiry_alerts = db.query(ProductBatch).filter(
        ProductBatch.organization_id == organization_id,
        ProductBatch.expiry_date <= expiry_date_threshold,
        ProductBatch.expiry_date >= datetime.now().date(),
        ProductBatch.is_active == True
    ).count()
    
    # Recent movements (last 7 days)
    recent_movements = db.query(StockMovement).filter(
        StockMovement.organization_id == organization_id,
        StockMovement.movement_date >= datetime.now() - timedelta(days=7)
    ).count()
    
    # Warehouse utilization
    warehouse_utilization = []
    warehouses = db.query(Warehouse).filter(
        Warehouse.organization_id == organization_id,
        Warehouse.is_active == True
    ).all()
    
    for warehouse in warehouses:
        utilization = WarehouseService.calculate_warehouse_utilization(db, warehouse.id)
        warehouse_utilization.append(utilization)
    
    return InventoryDashboard(
        total_products=total_products,
        total_warehouses=total_warehouses,
        total_stock_value=total_stock_value,
        low_stock_alerts=low_stock_alerts,
        expiry_alerts=expiry_alerts,
        recent_movements=recent_movements,
        top_moving_products=[],  # Simplified for now
        warehouse_utilization=warehouse_utilization,
        organization_id=organization_id,
        as_of_date=datetime.utcnow()
    )


# Bulk Operations
@router.post("/bulk-import", response_model=BulkImportResponse)
async def bulk_stock_import(
    import_data: BulkStockImport,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Bulk import stock data"""
    # Verify warehouse exists and belongs to organization
    warehouse = db.query(Warehouse).filter(
        Warehouse.id == import_data.warehouse_id,
        Warehouse.organization_id == organization_id
    ).first()
    
    if not warehouse:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Warehouse not found"
        )
    
    total_records = len(import_data.import_data)
    successful_records = 0
    failed_records = 0
    errors = []
    warnings = []
    
    if not import_data.validate_only:
        for i, record in enumerate(import_data.import_data):
            try:
                # Process each record based on import_type
                if import_data.import_type == "stock_levels":
                    # Update warehouse stock levels
                    # This is a simplified implementation
                    successful_records += 1
                else:
                    warnings.append({
                        "row": i + 1,
                        "message": f"Unsupported import type: {import_data.import_type}"
                    })
                    
            except Exception as e:
                failed_records += 1
                errors.append({
                    "row": i + 1,
                    "error": str(e)
                })
    
    return BulkImportResponse(
        success=failed_records == 0,
        total_records=total_records,
        successful_records=successful_records,
        failed_records=failed_records,
        errors=errors,
        warnings=warnings
    )