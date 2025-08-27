"""
Inventory & Parts Management API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc, asc, func
from typing import List, Optional
from datetime import datetime, timedelta

from app.core.database import get_db
from app.api.v1.auth import get_current_active_user
from app.core.tenant import TenantQueryMixin, validate_company_setup_for_operations
from app.core.org_restrictions import require_current_organization_id
from app.core.rbac_dependencies import check_service_permission
from app.models import (
    User, Stock, Product, Organization, InventoryTransaction, 
    JobParts, InventoryAlert, InstallationJob
)
from app.schemas.inventory import (
    InventoryTransactionCreate, InventoryTransactionUpdate, InventoryTransactionResponse,
    JobPartsCreate, JobPartsUpdate, JobPartsResponse,
    InventoryAlertCreate, InventoryAlertUpdate, InventoryAlertResponse,
    InventoryUsageReport, InventoryValueReport, LowStockReport,
    BulkJobPartsAssignment, BulkInventoryAdjustment, BulkInventoryResponse,
    InventoryFilter, InventoryListResponse, TransactionType, JobPartsStatus,
    AlertType, AlertStatus, AlertPriority
)
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


class InventoryService:
    """Service class for inventory operations"""
    
    @staticmethod
    def get_current_stock(db: Session, organization_id: int, product_id: int, location: Optional[str] = None) -> float:
        """Get current stock level for a product"""
        query = db.query(Stock).filter(
            Stock.organization_id == organization_id,
            Stock.product_id == product_id
        )
        if location:
            query = query.filter(Stock.location == location)
        
        stock_record = query.first()
        return stock_record.quantity if stock_record else 0.0
    
    @staticmethod
    def update_stock_level(db: Session, organization_id: int, product_id: int, 
                          new_quantity: float, location: Optional[str] = None):
        """Update stock level for a product"""
        query = db.query(Stock).filter(
            Stock.organization_id == organization_id,
            Stock.product_id == product_id
        )
        if location:
            query = query.filter(Stock.location == location)
        
        stock_record = query.first()
        if stock_record:
            stock_record.quantity = new_quantity
        else:
            # Create new stock record if it doesn't exist
            product = db.query(Product).filter(Product.id == product_id).first()
            if product:
                stock_record = Stock(
                    organization_id=organization_id,
                    product_id=product_id,
                    quantity=new_quantity,
                    unit=product.unit,
                    location=location
                )
                db.add(stock_record)
        
        db.commit()
        return stock_record
    
    @staticmethod
    def create_inventory_transaction(db: Session, organization_id: int, user_id: int,
                                   transaction_data: InventoryTransactionCreate) -> InventoryTransaction:
        """Create an inventory transaction and update stock"""
        current_stock = InventoryService.get_current_stock(
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
        InventoryService.update_stock_level(
            db, organization_id, transaction_data.product_id, new_stock, transaction_data.location
        )
        
        # Check for low stock alerts
        InventoryService.check_and_create_alerts(db, organization_id, transaction_data.product_id, new_stock)
        
        db.commit()
        return transaction
    
    @staticmethod
    def check_and_create_alerts(db: Session, organization_id: int, product_id: int, current_stock: float):
        """Check stock levels and create alerts if necessary"""
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return
        
        # Check if alert already exists
        existing_alert = db.query(InventoryAlert).filter(
            InventoryAlert.organization_id == organization_id,
            InventoryAlert.product_id == product_id,
            InventoryAlert.status == AlertStatus.ACTIVE
        ).first()
        
        if current_stock <= 0 and not existing_alert:
            # Out of stock alert
            alert = InventoryAlert(
                organization_id=organization_id,
                product_id=product_id,
                alert_type=AlertType.OUT_OF_STOCK,
                current_stock=current_stock,
                reorder_level=product.reorder_level,
                priority=AlertPriority.CRITICAL,
                message=f"Product '{product.name}' is out of stock",
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
                message=f"Product '{product.name}' is below reorder level",
                suggested_order_quantity=max(product.reorder_level * 2 - current_stock, 10)
            )
            db.add(alert)
        elif current_stock > product.reorder_level and existing_alert:
            # Resolve existing alert
            existing_alert.status = AlertStatus.RESOLVED
            existing_alert.resolved_at = datetime.utcnow()


# Inventory Transactions Endpoints
@router.get("/transactions", response_model=List[InventoryTransactionResponse])
async def get_inventory_transactions(
    skip: int = 0,
    limit: int = 100,
    product_id: Optional[int] = None,
    transaction_type: Optional[TransactionType] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get inventory transactions with filtering options"""
    organization_id = require_current_organization_id(current_user)
    
    # Check permissions
    check_service_permission(
        user=current_user, 
        module="inventory", 
        action="read",
        db=db
    )
    
    query = db.query(InventoryTransaction).filter(
        InventoryTransaction.organization_id == organization_id
    ).options(
        joinedload(InventoryTransaction.product),
        joinedload(InventoryTransaction.created_by)
    )
    
    # Apply filters
    if product_id:
        query = query.filter(InventoryTransaction.product_id == product_id)
    if transaction_type:
        query = query.filter(InventoryTransaction.transaction_type == transaction_type)
    if start_date:
        query = query.filter(InventoryTransaction.transaction_date >= start_date)
    if end_date:
        query = query.filter(InventoryTransaction.transaction_date <= end_date)
    
    # Order by transaction date descending
    query = query.order_by(desc(InventoryTransaction.transaction_date))
    
    transactions = query.offset(skip).limit(limit).all()
    
    # Build response with related data
    response = []
    for transaction in transactions:
        transaction_data = InventoryTransactionResponse(
            **transaction.__dict__,
            product_name=transaction.product.name if transaction.product else None,
            created_by_name=transaction.created_by.full_name if transaction.created_by else None
        )
        response.append(transaction_data)
    
    return response


@router.post("/transactions", response_model=InventoryTransactionResponse)
async def create_inventory_transaction(
    transaction_data: InventoryTransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new inventory transaction"""
    organization_id = require_current_organization_id(current_user)
    
    # Check permissions
    check_service_permission(
        user=current_user, 
        module="inventory", 
        action="create",
        db=db
    )
    
    try:
        transaction = InventoryService.create_inventory_transaction(
            db, organization_id, current_user.id, transaction_data
        )
        
        # Load related data for response
        db.refresh(transaction)
        transaction_with_product = db.query(InventoryTransaction).options(
            joinedload(InventoryTransaction.product),
            joinedload(InventoryTransaction.created_by)
        ).filter(InventoryTransaction.id == transaction.id).first()
        
        return InventoryTransactionResponse(
            **transaction_with_product.__dict__,
            product_name=transaction_with_product.product.name,
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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get job parts assignments with filtering options"""
    organization_id = require_current_organization_id(current_user)
    
    # Check permissions
    check_service_permission(
        user=current_user, 
        module="job_parts", 
        action="read",
        db=db
    )
    
    query = db.query(JobParts).filter(
        JobParts.organization_id == organization_id
    ).options(
        joinedload(JobParts.product),
        joinedload(JobParts.job),
        joinedload(JobParts.allocated_by),
        joinedload(JobParts.used_by)
    )
    
    # Apply filters
    if job_id:
        query = query.filter(JobParts.job_id == job_id)
    if product_id:
        query = query.filter(JobParts.product_id == product_id)
    if status:
        query = query.filter(JobParts.status == status)
    
    job_parts = query.offset(skip).limit(limit).all()
    
    # Build response with related data
    response = []
    for job_part in job_parts:
        job_part_data = JobPartsResponse(
            **job_part.__dict__,
            product_name=job_part.product.name if job_part.product else None,
            job_number=job_part.job.job_number if job_part.job else None,
            allocated_by_name=job_part.allocated_by.full_name if job_part.allocated_by else None,
            used_by_name=job_part.used_by.full_name if job_part.used_by else None
        )
        response.append(job_part_data)
    
    return response


@router.post("/job-parts", response_model=JobPartsResponse)
async def assign_parts_to_job(
    job_parts_data: JobPartsCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Assign parts to a job"""
    organization_id = require_current_organization_id(current_user)
    
    # Check permissions
    check_service_permission(
        user=current_user, 
        module="job_parts", 
        action="create",
        db=db
    )
    
    # Verify job exists and belongs to organization
    job = db.query(InstallationJob).filter(
        InstallationJob.id == job_parts_data.job_id,
        InstallationJob.organization_id == organization_id
    ).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Verify product exists and belongs to organization
    product = db.query(Product).filter(
        Product.id == job_parts_data.product_id,
        Product.organization_id == organization_id
    ).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check if assignment already exists
    existing = db.query(JobParts).filter(
        JobParts.job_id == job_parts_data.job_id,
        JobParts.product_id == job_parts_data.product_id
    ).first()
    
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
    db.commit()
    db.refresh(job_part)
    
    # Load related data for response
    job_part_with_relations = db.query(JobParts).options(
        joinedload(JobParts.product),
        joinedload(JobParts.job),
        joinedload(JobParts.allocated_by)
    ).filter(JobParts.id == job_part.id).first()
    
    return JobPartsResponse(
        **job_part_with_relations.__dict__,
        product_name=job_part_with_relations.product.name,
        job_number=job_part_with_relations.job.job_number,
        allocated_by_name=job_part_with_relations.allocated_by.full_name if job_part_with_relations.allocated_by else None
    )


@router.put("/job-parts/{job_part_id}", response_model=JobPartsResponse)
async def update_job_parts(
    job_part_id: int,
    job_parts_data: JobPartsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update job parts assignment"""
    organization_id = require_current_organization_id(current_user)
    
    # Check permissions
    check_service_permission(
        user=current_user, 
        module="job_parts", 
        action="create",
        db=db
    )
    
    job_part = db.query(JobParts).filter(
        JobParts.id == job_part_id,
        JobParts.organization_id == organization_id
    ).first()
    
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
                InventoryService.create_inventory_transaction(
                    db, organization_id, current_user.id, transaction_data
                )
            except ValueError as e:
                raise HTTPException(status_code=400, detail=f"Inventory error: {str(e)}")
    
    db.commit()
    db.refresh(job_part)
    
    # Load related data for response
    job_part_with_relations = db.query(JobParts).options(
        joinedload(JobParts.product),
        joinedload(JobParts.job),
        joinedload(JobParts.allocated_by),
        joinedload(JobParts.used_by)
    ).filter(JobParts.id == job_part.id).first()
    
    return JobPartsResponse(
        **job_part_with_relations.__dict__,
        product_name=job_part_with_relations.product.name,
        job_number=job_part_with_relations.job.job_number,
        allocated_by_name=job_part_with_relations.allocated_by.full_name if job_part_with_relations.allocated_by else None,
        used_by_name=job_part_with_relations.used_by.full_name if job_part_with_relations.used_by else None
    )


# Inventory Alerts Endpoints
@router.get("/alerts", response_model=List[InventoryAlertResponse])
async def get_inventory_alerts(
    skip: int = 0,
    limit: int = 100,
    status: Optional[AlertStatus] = None,
    priority: Optional[AlertPriority] = None,
    alert_type: Optional[AlertType] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get inventory alerts with filtering options"""
    organization_id = require_current_organization_id(current_user)
    
    # Check permissions
    check_service_permission(
        user=current_user, 
        module="inventory_alerts", 
        action="read",
        db=db
    )
    
    query = db.query(InventoryAlert).filter(
        InventoryAlert.organization_id == organization_id
    ).options(
        joinedload(InventoryAlert.product),
        joinedload(InventoryAlert.acknowledged_by)
    )
    
    # Apply filters
    if status:
        query = query.filter(InventoryAlert.status == status)
    if priority:
        query = query.filter(InventoryAlert.priority == priority)
    if alert_type:
        query = query.filter(InventoryAlert.alert_type == alert_type)
    
    # Order by priority and creation date
    query = query.order_by(
        InventoryAlert.priority.desc(),
        desc(InventoryAlert.created_at)
    )
    
    alerts = query.offset(skip).limit(limit).all()
    
    # Build response with related data
    response = []
    for alert in alerts:
        alert_data = InventoryAlertResponse(
            **alert.__dict__,
            product_name=alert.product.name if alert.product else None,
            acknowledged_by_name=alert.acknowledged_by.full_name if alert.acknowledged_by else None
        )
        response.append(alert_data)
    
    return response


@router.put("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Acknowledge an inventory alert"""
    organization_id = require_current_organization_id(current_user)
    
    # Check permissions
    check_service_permission(
        user=current_user, 
        module="inventory_alerts", 
        action="update",
        db=db
    )
    
    alert = db.query(InventoryAlert).filter(
        InventoryAlert.id == alert_id,
        InventoryAlert.organization_id == organization_id
    ).first()
    
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert.status = AlertStatus.ACKNOWLEDGED
    alert.acknowledged_by_id = current_user.id
    alert.acknowledged_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Alert acknowledged successfully"}


# Reports Endpoints
@router.get("/reports/usage", response_model=List[InventoryUsageReport])
async def get_inventory_usage_report(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    product_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Generate inventory usage report"""
    organization_id = require_current_organization_id(current_user)
    
    # Check permissions
    check_service_permission(
        user=current_user, 
        module="inventory_reports", 
        action="read",
        db=db
    )
    
    # Default date range to last 30 days if not provided
    if not end_date:
        end_date = datetime.utcnow()
    if not start_date:
        start_date = end_date - timedelta(days=30)
    
    # Query for inventory transactions in date range
    transactions_query = db.query(
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
    ).filter(
        InventoryTransaction.organization_id == organization_id,
        InventoryTransaction.transaction_date >= start_date,
        InventoryTransaction.transaction_date <= end_date
    )
    
    if product_id:
        transactions_query = transactions_query.filter(InventoryTransaction.product_id == product_id)
    
    transactions_data = transactions_query.group_by(InventoryTransaction.product_id).all()
    
    # Get current stock and product info
    products_query = db.query(Product, Stock).outerjoin(
        Stock, and_(
            Stock.product_id == Product.id,
            Stock.organization_id == organization_id
        )
    ).filter(Product.organization_id == organization_id)
    
    if product_id:
        products_query = products_query.filter(Product.id == product_id)
    
    products_data = products_query.all()
    
    # Get job usage count
    job_usage_query = db.query(
        JobParts.product_id,
        func.count(func.distinct(JobParts.job_id)).label('total_jobs_used')
    ).filter(
        JobParts.organization_id == organization_id,
        JobParts.status == JobPartsStatus.USED
    )
    
    if start_date and end_date:
        job_usage_query = job_usage_query.filter(
            JobParts.used_at >= start_date,
            JobParts.used_at <= end_date
        )
    
    if product_id:
        job_usage_query = job_usage_query.filter(JobParts.product_id == product_id)
    
    job_usage_data = job_usage_query.group_by(JobParts.product_id).all()
    
    # Build report
    report = []
    
    # Create lookup dictionaries
    transactions_dict = {t.product_id: t for t in transactions_data}
    job_usage_dict = {j.product_id: j.total_jobs_used for j in job_usage_data}
    
    for product, stock in products_data:
        transaction = transactions_dict.get(product.id)
        
        report_item = InventoryUsageReport(
            product_id=product.id,
            product_name=product.name,
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


@router.get("/reports/low-stock", response_model=List[LowStockReport])
async def get_low_stock_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Generate low stock report"""
    organization_id = require_current_organization_id(current_user)
    
    # Check permissions
    check_service_permission(
        user=current_user, 
        module="inventory_reports", 
        action="read",
        db=db
    )
    
    # Query for products with stock below reorder level
    low_stock_query = db.query(Product, Stock).join(
        Stock, and_(
            Stock.product_id == Product.id,
            Stock.organization_id == organization_id
        )
    ).filter(
        Product.organization_id == organization_id,
        Stock.quantity <= Product.reorder_level
    )
    
    low_stock_items = low_stock_query.all()
    
    report = []
    for product, stock in low_stock_items:
        # Calculate days since last receipt
        last_receipt = db.query(InventoryTransaction).filter(
            InventoryTransaction.organization_id == organization_id,
            InventoryTransaction.product_id == product.id,
            InventoryTransaction.transaction_type == TransactionType.RECEIPT
        ).order_by(desc(InventoryTransaction.transaction_date)).first()
        
        days_since_last_receipt = None
        if last_receipt:
            days_since_last_receipt = (datetime.utcnow() - last_receipt.transaction_date).days
        
        report_item = LowStockReport(
            product_id=product.id,
            product_name=product.name,
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