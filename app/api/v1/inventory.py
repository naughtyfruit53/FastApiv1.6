# Revised: app/api/v1/inventory.py

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc, asc, func
from sqlalchemy.orm import joinedload
from typing import List, Optional
from datetime import datetime, date, timedelta
from decimal import Decimal

from app.core.database import get_db
from app.core.enforcement import require_access
from app.core.tenant import TenantQueryMixin
from app.core.org_restrictions import validate_company_setup
from app.models import (
    User, Stock, Product, Organization, InventoryTransaction, 
    JobParts, InventoryAlert, InstallationJob
)
from app.schemas.inventory import (
    InventoryTransactionCreate, InventoryTransactionUpdate, InventoryTransactionResponse,
    JobPartsCreate, JobPartsUpdate, JobPartsResponse,
    InventoryAlertCreate, InventoryAlertUpdate, InventoryAlertResponse,
    InventoryUsageReport, LowStockReport,
    BulkJobPartsAssignment, BulkInventoryAdjustment, BulkInventoryResponse,
    InventoryFilter, InventoryListResponse, TransactionType, JobPartsStatus,
    AlertType, AlertStatus, AlertPriority
)
from app.schemas.organization import TotalInventoryValue
from app.schemas.base import StockResponse
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


class InventoryService:
    """Service class for inventory operations"""
    
    @staticmethod
    async def get_current_stock(db: AsyncSession, organization_id: int, product_id: int, location: Optional[str] = None) -> float:
        """Get current stock level for a product"""
        stmt = select(Stock).where(
            Stock.organization_id == organization_id,
            Stock.product_id == product_id
        )
        if location:
            stmt = stmt.where(Stock.location == location)
        
        result = await db.execute(stmt)
        stock_record = result.scalar_one_or_none()
        return stock_record.quantity if stock_record else 0.0
    
    @staticmethod
    async def update_stock_level(db: AsyncSession, organization_id: int, product_id: int, 
                          new_quantity: float, location: Optional[str] = None):
        """Update stock level for a product"""
        stmt = select(Stock).where(
            Stock.organization_id == organization_id,
            Stock.product_id == product_id
        )
        if location:
            stmt = stmt.where(Stock.location == location)
        
        result = await db.execute(stmt)
        stock_record = result.scalar_one_or_none()
        if stock_record:
            stock_record.quantity = new_quantity
        else:
            # Create new stock record if it doesn't exist
            stmt_product = select(Product).where(Product.id == product_id)
            result_product = await db.execute(stmt_product)
            product = result_product.scalar_one_or_none()
            if product:
                stock_record = Stock(
                    organization_id=organization_id,
                    product_id=product_id,
                    quantity=new_quantity,
                    unit=product.unit,
                    location=location
                )
                db.add(stock_record)
        
        await db.commit()
        return stock_record
    
    @staticmethod
    async def create_inventory_transaction(db: AsyncSession, organization_id: int, user_id: int,
                                   transaction_data: InventoryTransactionCreate) -> InventoryTransaction:
        """Create an inventory transaction and update stock"""
        current_stock = await InventoryService.get_current_stock(
            db, organization_id, transaction_data.product_id, transaction_data.location
        )
        
        # Calculate new stock level
        if transaction_data.transaction_type in [TransactionType.RECEIPT]:
            new_stock = current_stock + transaction_data.quantity
        elif transaction_data.transaction_type in [TransactionType.ISSUE]:
            new_stock = current_stock - abs(transaction_data.quantity)  # Ensure negative for issues
            if new_stock < 0:
                raise ValueError(f"Insufficient stock. Current: {current_stock}, Requested: {abs(transaction_data.quantity)}")
        else:  # ADJUSTMENT
            new_stock = current_stock + transaction_data.quantity
        
        # Create transaction record
        transaction = InventoryTransaction(
            organization_id=organization_id,
            product_id=transaction_data.product_id,
            transaction_type=transaction_data.transaction_type,
            quantity=transaction_data.quantity,
            unit=transaction_data.unit,
            location=transaction_data.location,
            reference_type=transaction_data.reference_type,
            reference_id=transaction_data.reference_id,
            reference_number=transaction_data.reference_number,
            notes=transaction_data.notes,
            unit_cost=transaction_data.unit_cost,
            total_cost=transaction_data.total_cost,
            stock_before=current_stock,
            stock_after=new_stock,
            transaction_date=transaction_data.transaction_date,
            created_by_id=user_id
        )
        
        db.add(transaction)
        
        # Update stock level
        await InventoryService.update_stock_level(
            db, organization_id, transaction_data.product_id, new_stock, transaction_data.location
        )
        
        # Check for low stock alerts
        await InventoryService.check_and_create_alerts(db, organization_id, transaction_data.product_id, new_stock)
        
        await db.commit()
        return transaction
    
    @staticmethod
    async def check_and_create_alerts(db: AsyncSession, organization_id: int, product_id: int, current_stock: float):
        """Check stock levels and create alerts if necessary"""
        stmt = select(Product).where(Product.id == product_id)
        result = await db.execute(stmt)
        product = result.scalar_one_or_none()
        if not product:
            return
        
        # Check if alert already exists
        stmt = select(InventoryAlert).where(
            InventoryAlert.organization_id == organization_id,
            InventoryAlert.product_id == product_id,
            InventoryAlert.status == AlertStatus.ACTIVE
        )
        result = await db.execute(stmt)
        existing_alert = result.scalar_one_or_none()
        
        if current_stock <= 0 and not existing_alert:
            # Out of stock alert
            alert = InventoryAlert(
                organization_id=organization_id,
                product_id=product_id,
                alert_type=AlertType.OUT_OF_STOCK,
                current_stock=current_stock,
                reorder_level=product.reorder_level,
                priority=AlertPriority.CRITICAL,
                message=f"Product '{product.product_name}' is out of stock",
                suggested_order_quantity=max(product.reorder_level * 2, 10)
            )
            db.add(alert)
        elif current_stock <= product.reorder_level and current_stock > 0 and not existing_alert:
            # Low stock alert
            alert = InventoryAlert(
                organization_id=organization_id,
                product_id=product_id,
                alert_type=AlertType.LOW_STOCK,
                current_stock=current_stock,
                reorder_level=product.reorder_level,
                priority=AlertPriority.HIGH,
                message=f"Product '{product.product_name}' is below reorder level",
                suggested_order_quantity=max(product.reorder_level * 2 - current_stock, 10)
            )
            db.add(alert)
        elif current_stock > product.reorder_level and existing_alert:
            # Resolve existing alert
            existing_alert.status = AlertStatus.RESOLVED
            existing_alert.resolved_at = datetime.utcnow()


# Stock Endpoints
@router.get("/stock", response_model=List[StockResponse])
async def get_stock(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    low_stock_only: bool = Query(False, description="Filter for low stock items only"),
    search: Optional[str] = Query(None, description="Search by product name or HSN code"),
    show_zero: bool = Query(True, description="Include items with zero stock"),
    auth: tuple = Depends(require_access("inventory", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get stock inventory for the organization"""
    current_user, organization_id = auth
    
    try:
        query = select(Stock).join(Product).filter(
            Stock.organization_id == organization_id,
            Product.is_active == True
        )
        
        if low_stock_only:
            query = query.filter(Stock.quantity <= Product.reorder_level)
        
        if not show_zero:
            query = query.filter(Stock.quantity > 0)
        
        if search:
            search_filter = or_(
                Product.product_name.ilike(f"%{search}%"),
                Product.hsn_code.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        query = query.options(joinedload(Stock.product)).order_by(Product.product_name.asc())
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        stock_items = result.scalars().all()
        
        response = [
            StockResponse(
                id=item.id,
                product_id=item.product_id,
                product_name=item.product.product_name if item.product else "Unknown",
                quantity=item.quantity,
                unit=item.unit,
                location=item.location,
                last_updated=item.last_updated,
                product_hsn_code=item.product.hsn_code if item.product else None,
                product_part_number=item.product.part_number if item.product else None,
                unit_price=float(item.product.unit_price if item.product else 0.0),
                reorder_level=item.product.reorder_level if item.product else 0,
                gst_rate=float(item.product.gst_rate if item.product else 0.0),
                is_active=item.product.is_active if item.product else False,
                total_value=float(item.quantity * (item.product.unit_price if item.product else 0.0))
            ) for item in stock_items
        ]
        
        logger.info(f"Retrieved {len(response)} stock items for org {organization_id}")
        return response
        
    except Exception as e:
        logger.error(f"Error retrieving stock: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve stock inventory"
        )

@router.get("/stock/low-stock", response_model=List[StockResponse])
async def get_low_stock(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    auth: tuple = Depends(require_access("inventory", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get low stock items for the organization"""
    current_user, organization_id = auth
    
    try:
        query = select(Stock).join(Product).filter(
            Stock.organization_id == organization_id,
            Product.is_active == True,
            Stock.quantity <= Product.reorder_level
        )
        
        query = query.options(joinedload(Stock.product)).order_by(Product.product_name.asc())
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        stock_items = result.scalars().all()
        
        response = [
            StockResponse(
                id=item.id,
                product_id=item.product_id,
                product_name=item.product.product_name if item.product else "Unknown",
                quantity=item.quantity,
                unit=item.unit,
                location=item.location,
                last_updated=item.last_updated,
                product_hsn_code=item.product.hsn_code if item.product else None,
                product_part_number=item.product.part_number if item.product else None,
                unit_price=float(item.product.unit_price if item.product else 0.0),
                reorder_level=item.product.reorder_level if item.product else 0,
                gst_rate=float(item.product.gst_rate if item.product else 0.0),
                is_active=item.product.is_active if item.product else False,
                total_value=float(item.quantity * (item.product.unit_price if item.product else 0.0))
            ) for item in stock_items
        ]
        
        logger.info(f"Retrieved {len(response)} low stock items for org {organization_id}")
        return response
        
    except Exception as e:
        logger.error(f"Error retrieving low stock: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve low stock inventory"
        )

# Inventory Transactions Endpoints
@router.get("/transactions", response_model=List[InventoryTransactionResponse])
async def get_inventory_transactions(
    skip: int = 0,
    limit: int = 100,
    product_id: Optional[int] = None,
    transaction_type: Optional[TransactionType] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    auth: tuple = Depends(require_access("inventory", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get inventory transactions with filtering options"""
    current_user, organization_id = auth
    
    stmt = select(InventoryTransaction).where(
        InventoryTransaction.organization_id == organization_id
    ).options(
        joinedload(InventoryTransaction.product),
        joinedload(InventoryTransaction.created_by)
    )
    
    # Apply filters
    if product_id:
        stmt = stmt.where(InventoryTransaction.product_id == product_id)
    if transaction_type:
        stmt = stmt.where(InventoryTransaction.transaction_type == transaction_type)
    if start_date:
        stmt = stmt.where(InventoryTransaction.transaction_date >= start_date)
    if end_date:
        stmt = stmt.where(InventoryTransaction.transaction_date <= end_date)
    
    # Order by transaction date descending
    stmt = stmt.order_by(desc(InventoryTransaction.transaction_date))
    
    result = await db.execute(stmt.offset(skip).limit(limit))
    transactions = result.scalars().all()
    
    # Build response with related data
    response = []
    for transaction in transactions:
        transaction_data = InventoryTransactionResponse(
            **transaction.__dict__,
            product_name=transaction.product.product_name if transaction.product else None,
            created_by_name=transaction.created_by.full_name if transaction.created_by else None
        )
        response.append(transaction_data)
    
    return response


@router.post("/transactions", response_model=InventoryTransactionResponse)
async def create_inventory_transaction(
    transaction_data: InventoryTransactionCreate,
    auth: tuple = Depends(require_access("inventory", "create")),
    db: AsyncSession = Depends(get_db)
):
    """Create a new inventory transaction"""
    current_user, organization_id = auth
    
    try:
        transaction = await InventoryService.create_inventory_transaction(
            db, organization_id, current_user.id, transaction_data
        )
        
        # Load related data for response
        await db.refresh(transaction)
        stmt = select(InventoryTransaction).options(
            joinedload(InventoryTransaction.product),
            joinedload(InventoryTransaction.created_by)
        ).where(InventoryTransaction.id == transaction.id)
        result = await db.execute(stmt)
        transaction_with_product = result.scalar_one_or_none()
        
        return InventoryTransactionResponse(
            **transaction_with_product.__dict__,
            product_name=transaction_with_product.product.product_name,
            created_by_name=transaction_with_product.created_by.full_name if transaction_with_product.created_by else None
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating inventory transaction: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Job Parts Endpoints
@router.get("/job-parts", response_model=List[JobPartsResponse])
async def get_job_parts(
    skip: int = 0,
    limit: int = 100,
    job_id: Optional[int] = None,
    product_id: Optional[int] = None,
    status: Optional[JobPartsStatus] = None,
    auth: tuple = Depends(require_access("inventory", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get job parts assignments with filtering options"""
    current_user, organization_id = auth
    
    stmt = select(JobParts).where(
        JobParts.organization_id == organization_id
    ).options(
        joinedload(JobParts.product),
        joinedload(JobParts.job),
        joinedload(JobParts.allocated_by),
        joinedload(JobParts.used_by)
    )
    
    # Apply filters
    if job_id:
        stmt = stmt.where(JobParts.job_id == job_id)
    if product_id:
        stmt = stmt.where(JobParts.product_id == product_id)
    if status:
        stmt = stmt.where(JobParts.status == status)
    
    result = await db.execute(stmt.offset(skip).limit(limit))
    job_parts = result.scalars().all()
    
    # Build response with related data
    response = []
    for job_part in job_parts:
        job_part_data = JobPartsResponse(
            **job_part.__dict__,
            product_name=job_part.product.product_name if job_part.product else None,
            job_number=job_part.job.job_number if job_part.job else None,
            allocated_by_name=job_part.allocated_by.full_name if job_part.allocated_by else None,
            used_by_name=job_part.used_by.full_name if job_part.used_by else None
        )
        response.append(job_part_data)
    
    return response


@router.post("/job-parts", response_model=JobPartsResponse)
async def assign_parts_to_job(
    job_parts_data: JobPartsCreate,
    auth: tuple = Depends(require_access("inventory", "create")),
    db: AsyncSession = Depends(get_db)
):
    """Assign parts to a job"""
    current_user, organization_id = auth
    
    # Verify job exists and belongs to organization
    stmt = select(InstallationJob).where(
        InstallationJob.id == job_parts_data.job_id,
        InstallationJob.organization_id == organization_id
    )
    result = await db.execute(stmt)
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Verify product exists and belongs to organization
    stmt = select(Product).where(
        Product.id == job_parts_data.product_id,
        Product.organization_id == organization_id
    )
    result = await db.execute(stmt)
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check if assignment already exists
    stmt = select(JobParts).where(
        JobParts.job_id == job_parts_data.job_id,
        JobParts.product_id == job_parts_data.product_id
    )
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(status_code=400, detail="Product already assigned to this job")
    
    # Create job parts assignment
    job_part = JobParts(
        organization_id=organization_id,
        job_id=job_parts_data.job_id,
        product_id=job_parts_data.product_id,
        quantity_required=job_parts_data.quantity_required,
        unit=job_parts_data.unit,
        notes=job_parts_data.notes,
        allocated_by_id=current_user.id,
        allocated_at=datetime.utcnow()
    )
    
    db.add(job_part)
    await db.commit()
    await db.refresh(job_part)
    
    # Load related data for response
    stmt = select(JobParts).options(
        joinedload(JobParts.product),
        joinedload(JobParts.job),
        joinedload(JobParts.allocated_by)
    ).where(JobParts.id == job_part.id)
    result = await db.execute(stmt)
    job_part_with_relations = result.scalar_one_or_none()
    
    return JobPartsResponse(
        **job_part_with_relations.__dict__,
        product_name=job_part_with_relations.product.product_name,
        job_number=job_part_with_relations.job.job_number,
        allocated_by_name=job_part_with_relations.allocated_by.full_name if job_part_with_relations.allocated_by else None,
        used_by_name=job_part_with_relations.used_by.full_name if job_part_with_relations.used_by else None
    )


@router.put("/job-parts/{job_part_id}", response_model=JobPartsResponse)
async def update_job_parts(
    job_part_id: int,
    job_parts_data: JobPartsUpdate,
    auth: tuple = Depends(require_access("inventory", "update")),
    db: AsyncSession = Depends(get_db)
):
    """Update job parts assignment"""
    current_user, organization_id = auth
    
    stmt = select(JobParts).where(
        JobParts.id == job_part_id,
        JobParts.organization_id == organization_id
    )
    result = await db.execute(stmt)
    job_part = result.scalar_one_or_none()
    
    if not job_part:
        raise HTTPException(status_code=404, detail="Job parts assignment not found")
    
    # Update fields
    update_data = job_parts_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(job_part, field, value)
    
    # Track usage
    if job_parts_data.status == JobPartsStatus.USED and not job_part.used_at:
        job_part.used_by_id = current_user.id
        job_part.used_at = datetime.utcnow()
        
        # Create inventory transaction for parts usage
        if job_parts_data.quantity_used and job_parts_data.quantity_used > 0:
            transaction_data = InventoryTransactionCreate(
                product_id=job_part.product_id,
                transaction_type=TransactionType.ISSUE,
                quantity=-job_parts_data.quantity_used,  # Negative for issue
                unit=job_part.unit,
                location=job_parts_data.location_used,
                reference_type="job",
                reference_id=job_part.job_id,
                reference_number=f"Job-{job_part.job.job_number}" if job_part.job else None,
                notes=f"Parts used in job {job_part.job.job_number}" if job_part.job else "Parts used in job",
                unit_cost=job_parts_data.unit_cost,
                total_cost=job_parts_data.total_cost,
                transaction_date=datetime.utcnow()
            )
            
            try:
                await InventoryService.create_inventory_transaction(
                    db, organization_id, current_user.id, transaction_data
                )
            except ValueError as e:
                raise HTTPException(status_code=400, detail=f"Inventory error: {str(e)}")
    
    await db.commit()
    
    # Load related data for response
    stmt = select(JobParts).options(
        joinedload(JobParts.product),
        joinedload(JobParts.job),
        joinedload(JobParts.allocated_by),
        joinedload(JobParts.used_by)
    ).where(JobParts.id == job_part.id)
    result = await db.execute(stmt)
    job_part_with_relations = result.scalar_one_or_none()
    
    return JobPartsResponse(
        **job_part_with_relations.__dict__,
        product_name=job_part_with_relations.product.product_name,
        job_number=job_part_with_relations.job.job_number,
        allocated_by_name=job_part_with_relations.allocated_by.full_name if job_part_with_relations.allocated_by else None,
        used_by_name=job_part_with_relations.used_by.full_name if job_part_with_relations.used_by else None
    )


# Inventory Alerts Endpoints
@router.get("/alerts", response_model=List[InventoryAlertResponse])
async def get_inventory_alerts(
    skip: int = 0,
    limit: int = 100000,
    status: Optional[AlertStatus] = None,
    priority: Optional[AlertPriority] = None,
    alert_type: Optional[AlertType] = None,
    auth: tuple = Depends(require_access("inventory", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get inventory alerts with filtering options"""
    current_user, organization_id = auth
    
    stmt = select(InventoryAlert).where(
        InventoryAlert.organization_id == organization_id
    ).options(
        joinedload(InventoryAlert.product),
        joinedload(InventoryAlert.acknowledged_by)
    )
    
    # Apply filters
    if status:
        stmt = stmt.where(InventoryAlert.status == status)
    if priority:
        stmt = stmt.where(InventoryAlert.priority == priority)
    if alert_type:
        stmt = stmt.where(InventoryAlert.alert_type == alert_type)
    
    # Order by priority and creation date
    stmt = stmt.order_by(
        InventoryAlert.priority.desc(),
        desc(InventoryAlert.created_at)
    )
    
    result = await db.execute(stmt.offset(skip).limit(limit))
    alerts = result.scalars().all()
    
    # Build response with related data
    response = []
    for alert in alerts:
        alert_data = InventoryAlertResponse(
            **alert.__dict__,
            product_name=alert.product.product_name if alert.product else None,
            acknowledged_by_name=alert.acknowledged_by.full_name if alert.acknowledged_by else None
        )
        response.append(alert_data)
    
    return response


@router.put("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: int,
    auth: tuple = Depends(require_access("inventory", "update")),
    db: AsyncSession = Depends(get_db)
):
    """Acknowledge an inventory alert"""
    current_user, organization_id = auth
    
    stmt = select(InventoryAlert).where(
        InventoryAlert.id == alert_id,
        InventoryAlert.organization_id == organization_id
    )
    result = await db.execute(stmt)
    alert = result.scalar_one_or_none()
    
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert.status = AlertStatus.ACKNOWLEDGED
    alert.acknowledged_by_id = current_user.id
    alert.acknowledged_at = datetime.utcnow()
    
    await db.commit()
    
    return {"message": "Alert acknowledged successfully"}


# Reports Endpoints
@router.get("/reports/usage", response_model=List[InventoryUsageReport])
async def get_inventory_usage_report(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    product_id: Optional[int] = None,
    auth: tuple = Depends(require_access("inventory", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Generate inventory usage report"""
    current_user, organization_id = auth
    
    # Default date range to last 30 days if not provided
    if not end_date:
        end_date = datetime.utcnow()
    if not start_date:
        start_date = end_date - timedelta(days=30)
    
    # Query for inventory transactions in date range
    stmt_transactions = select(
        InventoryTransaction.product_id,
        func.sum(
            func.case(
                (InventoryTransaction.transaction_type == TransactionType.ISSUE, 
                 func.abs(InventoryTransaction.quantity)),
                else_=0
            )
        ).label('total_issued'),
        func.sum(
            func.case(
                (InventoryTransaction.transaction_type == TransactionType.RECEIPT, 
                 InventoryTransaction.quantity),
                else_=0
            )
        ).label('total_received')
    ).where(
        InventoryTransaction.organization_id == organization_id,
        InventoryTransaction.transaction_date >= start_date,
        InventoryTransaction.transaction_date <= end_date
    )
    
    if product_id:
        stmt_transactions = stmt_transactions.where(InventoryTransaction.product_id == product_id)
    
    stmt_transactions = stmt_transactions.group_by(InventoryTransaction.product_id)
    result_transactions = await db.execute(stmt_transactions)
    transactions_data = result_transactions.all()
    
    # Get current stock and product info
    stmt_products = select(Product, Stock).outerjoin(
        Stock, and_(
            Stock.product_id == Product.id,
            Stock.organization_id == organization_id
        )
    ).where(Product.organization_id == organization_id)
    
    if product_id:
        stmt_products = stmt_products.where(Product.id == product_id)
    
    result_products = await db.execute(stmt_products)
    products_data = result_products.all()
    
    # Get job usage count
    stmt_job_usage = select(
        JobParts.product_id,
        func.count(func.distinct(JobParts.job_id)).label('total_jobs_used')
    ).where(
        JobParts.organization_id == organization_id,
        JobParts.status == JobPartsStatus.USED
    )
    
    if start_date and end_date:
        stmt_job_usage = stmt_job_usage.where(
            JobParts.used_at >= start_date,
            JobParts.used_at <= end_date
        )
    
    if product_id:
        stmt_job_usage = stmt_job_usage.where(JobParts.product_id == product_id)
    
    stmt_job_usage = stmt_job_usage.group_by(JobParts.product_id)
    result_job_usage = await db.execute(stmt_job_usage)
    job_usage_data = result_job_usage.all()
    
    # Build report
    report = []
    
    # Create lookup dictionaries
    transactions_dict = {t[0]: t for t in transactions_data}
    job_usage_dict = {j[0]: j.total_jobs_used for j in job_usage_data}
    
    for product, stock in products_data:
        transaction = transactions_dict.get(product.id)
        
        report_item = InventoryUsageReport(
            product_id=product.id,
            product_name=product.product_name,
            total_issued=transaction.total_issued if transaction else 0.0,
            total_received=transaction.total_received if transaction else 0.0,
            current_stock=stock.quantity if stock else 0.0,
            reorder_level=product.reorder_level,
            total_jobs_used=job_usage_dict.get(product.id, 0),
            unit=product.unit,
            location=stock.location if stock else None
        )
        report.append(report_item)
    
    return report


@router.get("/reports/value", response_model=TotalInventoryValue)
async def get_inventory_value(
    auth: tuple = Depends(require_access("inventory", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get total inventory value"""
    current_user, organization_id = auth
    
    stmt = select(func.sum(Stock.quantity * Product.unit_price)).join(
        Product, Stock.product_id == Product.id
    ).where(Stock.organization_id == organization_id)
    
    result = await db.execute(stmt)
    total_value = result.scalar() or 0.0
    
    # Fetch the organization's currency
    stmt_org = select(Organization.currency).where(Organization.id == organization_id)
    result_org = await db.execute(stmt_org)
    currency = result_org.scalar() or 'INR'  # Default to 'INR' if not set
    
    return TotalInventoryValue(total_value=total_value, currency=currency)


@router.get("/reports/low-stock", response_model=List[LowStockReport])
async def get_low_stock_report(
    auth: tuple = Depends(require_access("inventory", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Generate low stock report"""
    current_user, organization_id = auth
    
    # Query for products with stock below reorder level
    stmt_low_stock = select(Product, Stock).join(
        Stock, and_(
            Stock.product_id == Product.id,
            Stock.organization_id == organization_id
        )
    ).where(
        Product.organization_id == organization_id,
        Stock.quantity <= Product.reorder_level
    )
    
    result_low_stock = await db.execute(stmt_low_stock)
    low_stock_items = result_low_stock.all()
    
    report = []
    for product, stock in low_stock_items:
        # Calculate days since last receipt
        stmt_last_receipt = select(InventoryTransaction).where(
            InventoryTransaction.organization_id == organization_id,
            InventoryTransaction.product_id == product.id,
            InventoryTransaction.transaction_type == TransactionType.RECEIPT
        ).order_by(desc(InventoryTransaction.transaction_date))
        result_last_receipt = await db.execute(stmt_last_receipt)
        last_receipt = result_last_receipt.scalar_one_or_none()
        
        days_since_last_receipt = None
        if last_receipt:
            days_since_last_receipt = (datetime.utcnow() - last_receipt.transaction_date).days
        
        report_item = LowStockReport(
            product_id=product.id,
            product_name=product.product_name,
            current_stock=stock.quantity,
            reorder_level=product.reorder_level,
            stock_deficit=product.reorder_level - stock.quantity,
            suggested_order_quantity=max(product.reorder_level * 2 - stock.quantity, 10),
            unit=product.unit,
            location=stock.location,
            days_since_last_receipt=days_since_last_receipt
        )
        report.append(report_item)
    
    return report