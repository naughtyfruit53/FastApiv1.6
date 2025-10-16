# app/api/v1/stock.py

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from typing import List, Optional, Dict, Any
from app.core.database import get_db
from app.api.v1.auth import get_current_active_user
from app.core.org_restrictions import require_current_organization_id, validate_company_setup
from app.models import User, Stock, Product, Organization, Company, InventoryTransaction, PurchaseVoucher, Vendor
from app.schemas.stock import (
    StockCreate, StockUpdate, StockInDB, StockWithProduct,
    BulkImportResponse, BulkImportError, StockAdjustment, StockAdjustmentResponse
)
from app.schemas.base import ProductCreate
from app.utils.excel_import import StockExcelImporter
from app.services.excel_service import StockExcelService, ExcelService
from app.schemas.inventory import InventoryTransactionResponse
from datetime import datetime, timedelta
import logging
import pytz

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("", response_model=List[StockWithProduct])
async def get_stock(
    skip: int = 0,
    limit: Optional[int] = Query(None),
    product_id: Optional[int] = None,
    low_stock_only: bool = False,
    search: str = Query("", description="Search term for stock items"),
    show_zero: bool = Query(True, description="Show items with zero quantity"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get stock information with product details
    
    Access Control:
    - Super admins: Can view all stock across all organizations
    - Organization users (admin, org_admin): Can view stock for their organization
    - Standard users: Can view stock only if they have stock module access
    
    This endpoint implements enhanced access control for stock module visibility.
    """
    logger.info(f"Stock endpoint accessed by user {current_user.email} (ID: {current_user.id})")
    logger.info(f"User role: {current_user.role}, is_super_admin: {getattr(current_user, 'is_super_admin', False)}")
    logger.info(f"User organization_id: {getattr(current_user, 'organization_id', None)}")
    logger.info(f"User has_stock_access: {getattr(current_user, 'has_stock_access', True)}")
    
    try:
        # Check stock module access for standard users
        if current_user.role == "standard_user" and not getattr(current_user, 'has_stock_access', True):
            logger.warning(f"Standard user {current_user.email} denied access to stock - no stock module access")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. You do not have permission to view stock information."
            )
        
        is_super_admin = getattr(current_user, 'is_super_admin', False)
        org_id = current_user.organization_id if not is_super_admin else None
        
        if not is_super_admin and org_id is None:
            logger.error(f"User {current_user.email} has no organization_id set")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is not associated with any organization"
            )
        
        # Always select from Product to include zeros when show_zero=true
        if show_zero:
            logger.info("Using outer join to include zero stock products")
            stmt = select(Product, Stock).join_from(Product, Stock, Product.id == Stock.product_id, isouter=True)
        else:
            logger.info("Using inner join for non-zero stock")
            stmt = select(Product, Stock).join_from(Product, Stock, Product.id == Stock.product_id, isouter=False)
        
        if not is_super_admin:
            stmt = stmt.where(Product.organization_id == org_id)
        
        if product_id is not None:
            logger.info(f"Filtering by product_id: {product_id}")
            stmt = stmt.where(Product.id == product_id)
        
        if low_stock_only:
            logger.info("Filtering for low stock items only")
            stmt = stmt.where(or_(Stock.quantity <= Product.reorder_level, Stock.id.is_(None)))
        
        if search:
            logger.info(f"Searching for products with term: {search}")
            stmt = stmt.where(Product.product_name.ilike(f"%{search}%"))
        
        if not show_zero:
            logger.info("Excluding zero quantity items")
            stmt = stmt.where(Stock.quantity > 0)
        
        logger.info(f"Executing stock query with skip={skip}, limit={limit}")
        stmt = stmt.offset(skip)
        if limit is not None:
            stmt = stmt.limit(limit)
        result = await db.execute(stmt)
        product_stock_pairs = result.all()
        logger.info(f"Found {len(product_stock_pairs)} stock items")
        
        # Transform the results to include product information
        result_list = []
        for product, stock in product_stock_pairs:
            try:
                effective_quantity = stock.quantity if stock else 0.0
                effective_unit = stock.unit if stock else product.unit
                effective_location = stock.location if stock else ""
                effective_last_updated = (
                    stock.last_updated if stock else
                    product.updated_at if product.updated_at else
                    product.created_at if product.created_at else
                    datetime.utcnow()
                )
                effective_id = stock.id if stock else 0
                effective_org_id = stock.organization_id if stock else product.organization_id
                
                unit_price = product.unit_price or 0.0
                total_value = effective_quantity * unit_price
                
                stock_with_product = StockWithProduct(
                    id=effective_id,
                    organization_id=effective_org_id,
                    product_id=product.id,
                    quantity=effective_quantity,
                    unit=effective_unit,
                    location=effective_location,
                    last_updated=effective_last_updated,
                    product_name=product.product_name,
                    product_hsn_code=product.hsn_code,
                    product_part_number=product.part_number,
                    unit_price=unit_price,  # Handle None values
                    reorder_level=product.reorder_level or 0,  # Handle None values
                    gst_rate=product.gst_rate or 0.0,
                    is_active=product.is_active,
                    total_value=total_value
                )
                result_list.append(stock_with_product)
            except Exception as e:
                logger.error(f"Error creating StockWithProduct for product ID {product.id}: {e}")
                logger.error(f"Stock data: {stock.__dict__ if hasattr(stock, '__dict__') else 'No dict'}")
                logger.error(f"Product data: {product.__dict__ if hasattr(product, '__dict__') else 'No dict'}")
                # Continue processing other items instead of failing completely
                continue
        
        logger.info(f"Successfully transformed {len(result_list)} stock items")
        return result_list
        
    except Exception as e:
        logger.error(f"Unexpected error in get_stock endpoint: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error while fetching stock data: {str(e)}"
        )

@router.get("/low-stock", response_model=List[StockWithProduct])
async def get_low_stock(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get products with low stock (below reorder level) with product details, including products without stock entries"""
    logger.info(f"Low stock endpoint accessed by user {current_user.email}")
    
    # Check stock module access for standard users
    if current_user.role == "standard_user" and not getattr(current_user, 'has_stock_access', True):
        logger.warning(f"Standard user {current_user.email} denied access to low stock - no stock module access")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. You do not have permission to view stock information."
        )
    
    if getattr(current_user, 'is_super_admin', False):
        logger.info("Super admin access - querying all low stock items")
        stmt = select(Product, Stock).join_from(Product, Stock, Product.id == Stock.product_id, isouter=True).where(
            or_(
                Stock.quantity <= Product.reorder_level,
                Stock.id.is_(None)  # Products without stock entries
            ),
            Product.reorder_level > 0  # Exclude products with reorder_level = 0
        )
    else:
        # For non-super-admin users, use their organization_id directly  
        org_id = current_user.organization_id
        if not org_id:
            logger.error(f"User {current_user.email} has no organization_id set")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is not associated with any organization"
            )
        logger.info(f"Organization-specific low stock access for org_id: {org_id}")
        stmt = select(Product, Stock).join_from(Product, Stock, Product.id == Stock.product_id, isouter=True).where(
            or_(
                Stock.quantity <= Product.reorder_level,
                Stock.id.is_(None)  # Products without stock entries
            ),
            Product.reorder_level > 0,  # Exclude products with reorder_level = 0
            Product.organization_id == org_id
        )
    
    result = await db.execute(stmt)
    product_stock_pairs = result.all()
    
    # Transform the results to include product information, handling missing stock
    result_list = []
    for product, stock in product_stock_pairs:
        try:
            effective_quantity = stock.quantity if stock else 0.0
            effective_location = stock.location if stock else ""
            effective_last_updated = (
                stock.last_updated if stock else
                product.updated_at if product.updated_at else
                product.created_at if product.created_at else
                datetime.utcnow()
            )
            unit_price = product.unit_price or 0.0
            total_value = effective_quantity * unit_price
            
            stock_with_product = StockWithProduct(
                id=stock.id if stock else 0,
                organization_id=product.organization_id,
                product_id=product.id,
                quantity=effective_quantity,
                unit=product.unit,
                location=effective_location,
                last_updated=effective_last_updated,
                product_name=product.product_name,
                product_hsn_code=product.hsn_code,
                product_part_number=product.part_number,
                unit_price=unit_price,
                reorder_level=product.reorder_level or 0,
                gst_rate=product.gst_rate or 0.0,
                is_active=product.is_active,
                total_value=total_value
            )
            result_list.append(stock_with_product)
        except Exception as e:
            logger.error(f"Error creating StockWithProduct for low stock product ID {product.id}: {e}")
            continue
    
    return result_list

@router.get("/movements", response_model=List[InventoryTransactionResponse])
async def get_stock_movements(
    search: Optional[str] = Query(None, description="Search term for movements"),
    recent: bool = Query(True, description="Show only recent movements (last 30 days)"),
    product_id: Optional[int] = Query(None, description="Filter by specific product ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get stock movement history (inventory transactions)"""
    logger.info(f"Stock movements endpoint accessed by user {current_user.email}")
    
    if current_user.role == "standard_user" and not getattr(current_user, 'has_stock_access', True):
        logger.warning(f"Standard user {current_user.email} denied access to stock movements - no stock module access")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. You do not have permission to view stock movements."
        )
    
    stmt = select(InventoryTransaction)
    
    if not current_user.is_super_admin:
        org_id = current_user.organization_id
        if org_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not associated with any organization"
            )
        stmt = stmt.where(InventoryTransaction.organization_id == org_id)
    
    if recent:
        thirty_days_ago = datetime.now(pytz.utc) - timedelta(days=30)
        stmt = stmt.where(InventoryTransaction.created_at >= thirty_days_ago)
    
    if search:
        stmt = stmt.where(
            or_(
                InventoryTransaction.transaction_type.ilike(f"%{search}%"),
                InventoryTransaction.reference_number.ilike(f"%{search}%"),
                InventoryTransaction.notes.ilike(f"%{search}%")
            )
        )
    
    if product_id:
        stmt = stmt.where(InventoryTransaction.product_id == product_id)
    
    stmt = stmt.order_by(InventoryTransaction.created_at.desc())
    
    result = await db.execute(stmt)
    movements = result.scalars().all()
    
    # Transform to response schema with product name
    result_list = []
    for movement in movements:
        stmt_product = select(Product).where(Product.id == movement.product_id)
        result_product = await db.execute(stmt_product)
        product = result_product.scalar_one_or_none()
        result_list.append(InventoryTransactionResponse(
            **movement.__dict__,
            product_name=product.product_name if product else "Unknown Product"
        ))
    
    return result_list

@router.get("/product/{product_id}/last-vendor", response_model=Dict[str, Any])
async def get_last_vendor_for_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get the last vendor who supplied this product"""
    logger.info(f"Last vendor endpoint accessed by user {current_user.email} for product {product_id}")
    
    if current_user.role == "standard_user" and not getattr(current_user, 'has_stock_access', True):
        logger.warning(f"Standard user {current_user.email} denied access to last vendor - no stock module access")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. You do not have permission to view purchase information."
        )
    
    from app.models.vouchers.purchase import PurchaseVoucherItem  # Assuming this is the model
    stmt = select(PurchaseVoucher).join(PurchaseVoucherItem).where(
        PurchaseVoucherItem.product_id == product_id
    ).order_by(PurchaseVoucher.date.desc())
    result = await db.execute(stmt)
    last_purchase = result.scalar_one_or_none()
    
    if not last_purchase:
        return None
    
    # Ensure tenant access
    if not current_user.is_super_admin:
        TenantQueryMixin.ensure_tenant_access(last_purchase, current_user.organization_id)
    
    stmt_vendor = select(Vendor).where(Vendor.id == last_purchase.vendor_id)
    result_vendor = await db.execute(stmt_vendor)
    vendor = result_vendor.scalar_one_or_none()
    
    if not vendor:
        return None
    
    return {
        "id": vendor.id,
        "name": vendor.name,
        "last_purchase_date": last_purchase.date
    }

@router.get("/product/{product_id}", response_model=StockInDB)
async def get_product_stock(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get stock for specific product"""
    logger.info(f"Product stock endpoint accessed by user {current_user.email} for product {product_id}")
    
    # Check stock module access for standard users
    if current_user.role == "standard_user" and not getattr(current_user, 'has_stock_access', True):
        logger.warning(f"Standard user {current_user.email} denied access to product stock - no stock module access")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. You do not have permission to view stock information."
        )
        
    stmt = select(Stock).where(Stock.product_id == product_id)
    result = await db.execute(stmt)
    stock = result.scalar_one_or_none()
    
    if not stock:
        # Return zero stock if no record exists
        stmt_product = select(Product).where(Product.id == product_id)
        result_product = await db.execute(stmt_product)
        product = result_product.scalar_one_or_none()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        # Ensure tenant access for non-super-admin users
        if not current_user.is_super_admin:
            TenantQueryMixin.ensure_tenant_access(product, current_user.organization_id)
        
        return StockInDB(
            id=0,
            organization_id=product.organization_id,
            product_id=product_id,
            quantity=0.0,
            unit=product.unit,
            location="",
            last_updated=product.created_at or datetime.utcnow()
        )
    
    # Ensure tenant access for non-super-admin users
    if not current_user.is_super_admin:
        TenantQueryMixin.ensure_tenant_access(stock, current_user.organization_id)
    
    return stock

@router.post("", response_model=StockInDB)
async def create_stock_entry(
    stock: StockCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create new stock entry"""
    logger.info(f"Create stock endpoint accessed by user {current_user.email}")
    
    # Check stock module access for standard users
    if current_user.role == "standard_user" and not getattr(current_user, 'has_stock_access', True):
        logger.warning(f"Standard user {current_user.email} denied access to create stock - no stock module access")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. You do not have permission to manage stock information."
        )
        
    org_id = require_current_organization_id(current_user)
    
    # Check if product exists
    stmt = select(Product).where(Product.id == stock.product_id)
    result = await db.execute(stmt)
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Ensure tenant access for non-super-admin users
    if not current_user.is_super_admin:
        TenantQueryMixin.ensure_tenant_access(product, current_user.organization_id)
    
    # Check if stock entry already exists
    stmt = select(Stock).where(
        Stock.product_id == stock.product_id,
        Stock.organization_id == org_id
    )
    result = await db.execute(stmt)
    existing_stock = result.scalar_one_or_none()
    if existing_stock:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Stock entry already exists for this product. Use update endpoint."
        )
    
    # Create new stock entry
    db_stock = Stock(
        organization_id=org_id,
        **stock.dict(),
        last_updated=datetime.utcnow()
    )
    db.add(db_stock)
    await db.commit()
    await db.refresh(db_stock)
    
    logger.info(f"Stock entry created for product {product.product_name} by {current_user.email}")
    return db_stock

@router.put("/product/{product_id}", response_model=StockInDB)
async def update_stock(
    product_id: int,
    stock_update: StockUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update stock for a product"""
    logger.info(f"Update stock endpoint accessed by user {current_user.email} for product {product_id}")
    
    # Check stock module access for standard users
    if current_user.role == "standard_user" and not getattr(current_user, 'has_stock_access', True):
        logger.warning(f"Standard user {current_user.email} denied access to update stock - no stock module access")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. You do not have permission to manage stock information."
        )
        
    org_id = require_current_organization_id(current_user)
        
    stmt = select(Stock).where(Stock.product_id == product_id)
    result = await db.execute(stmt)
    stock = result.scalar_one_or_none()
    
    if not stock:
        # Create new stock entry if doesn't exist
        stmt_product = select(Product).where(Product.id == product_id)
        result_product = await db.execute(stmt_product)
        product = result_product.scalar_one_or_none()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        stock = Stock(
            organization_id=org_id,
            product_id=product_id,
            quantity=stock_update.quantity or 0.0,
            unit=stock_update.unit or product.unit,
            location=stock_update.location or "",
            last_updated=datetime.utcnow()
        )
        db.add(stock)
    else:
        # Update existing stock
        for field, value in stock_update.dict(exclude_unset=True).items():
            setattr(stock, field, value)
        stock.last_updated = datetime.utcnow()
    
    await db.commit()
    await db.refresh(stock)
    
    logger.info(f"Stock updated for product ID {product_id} by {current_user.email}")
    return stock

@router.post("/adjust/{product_id}", response_model=StockAdjustmentResponse)
async def adjust_stock(
    product_id: int,
    adjustment: StockAdjustment,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Enhanced stock quantity adjustment with detailed response"""
    logger.info(f"Adjust stock endpoint accessed by user {current_user.email} for product {product_id}")
    
    if current_user.role == "standard_user" and not getattr(current_user, 'has_stock_access', True):
        logger.warning(f"Standard user {current_user.email} denied access to adjust stock - no stock module access")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. You do not have permission to manage stock information."
        )
        
    org_id = require_current_organization_id(current_user)
        
    stmt = select(Stock).where(Stock.product_id == product_id)
    result = await db.execute(stmt)
    stock = result.scalar_one_or_none()
    
    if not stock:
        stmt_product = select(Product).where(Product.id == product_id)
        result_product = await db.execute(stmt_product)
        product = result_product.scalar_one_or_none()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        previous_quantity = 0.0
        new_quantity = max(0, adjustment.quantity_change)
        
        stock = Stock(
            organization_id=org_id,
            product_id=product_id,
            quantity=new_quantity,
            unit=product.unit,
            location="",
            last_updated=datetime.utcnow()
        )
        db.add(stock)
    else:
        previous_quantity = stock.quantity
        new_quantity = stock.quantity + adjustment.quantity_change
        
        if new_quantity < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock for this adjustment. Current: {previous_quantity}, Requested change: {adjustment.quantity_change}"
            )
        stock.quantity = new_quantity
        stock.last_updated = datetime.utcnow()
    
    try:
        await db.commit()
        await db.refresh(stock)
        
        logger.info(f"Stock adjusted for product ID {product_id}: {adjustment.quantity_change:+.2f} - {adjustment.reason} by {current_user.email}")
        
        return StockAdjustmentResponse(
            message=f"Stock adjusted successfully.{adjustment.reason}",
            previous_quantity=previous_quantity,
            quantity_change=adjustment.quantity_change,
            new_quantity=new_quantity
        )
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error adjusting stock: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to adjust stock. Please try again."
        )

@router.post("/bulk", response_model=BulkImportResponse)
async def bulk_import_stock(
    file: UploadFile = File(...),
    mode: str = "replace",
    organization_id: Optional[int] = Query(None, description="Organization ID (only for super admins)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Enhanced bulk import stock entries from Excel file with comprehensive validation and mode selection"""
    
    # Add logging at the start of import for user/org context
    logger.info(f"[bulk_import_stock] Starting import for user {current_user.id} ({current_user.email})")
    logger.info(f"[bulk_import_stock] User role: {current_user.role}, is_super_admin: {getattr(current_user, 'is_super_admin', False)}")
    logger.info(f"[bulk_import_stock] User organization_id: {getattr(current_user, 'organization_id', None)}")
    
    # Determine org_id based on user type - strict enforcement
    if getattr(current_user, 'is_super_admin', False):
        # Super admins can specify organization_id
        if organization_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Super admins must provide organization_id"
            )
        org_id = organization_id
        logger.info(f"[bulk_import_stock] Super admin importing for org_id: {org_id}")
        # Validate organization exists
        stmt = select(Organization).where(Organization.id == org_id)
        result = await db.execute(stmt)
        org = result.scalar_one_or_none()
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Specified organization not found"
            )
    else:
        # Non-super-admin users: use their organization_id only, ignore any frontend-supplied org_id
        if organization_id is not None and organization_id != current_user.organization_id:
            logger.warning(f"[bulk_import_stock] User {current_user.email} attempted to specify different org_id: {organization_id}, ignoring")
        
        org_id = require_current_organization_id(current_user)
        logger.info(f"[bulk_import_stock] Regular user importing for their org_id: {org_id}")

    # Validate company setup is completed before allowing inventory operations
    await validate_company_setup(db, org_id)

    start_time = datetime.now(pytz.utc)
    
    # Validate mode
    if mode not in ['add', 'replace']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid mode. Must be 'add' or 'replace'."
        )
    
    # Validate file type
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only Excel files (.xlsx, .xls) are allowed"
        )
    
    try:
        # Parse Excel file using existing service
        records = await ExcelService.parse_excel_file(file, StockExcelService.REQUIRED_COLUMNS, "Stock Import Template")
        
        if not records:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No data found in Excel file"
            )
        
        created_products = 0
        created_stocks = 0
        updated_stocks = 0
        skipped_records = 0
        detailed_errors = []
        warnings = []
        simple_errors = []
        
        for i, record in enumerate(records, 1):
            try:
                # Extract product and stock data with enhanced validation
                product_name = str(record.get("product_name", "")).strip()
                unit = str(record.get("unit", "")).strip()
                
                # Enhanced validation for required fields
                if not product_name:
                    detailed_errors.append(BulkImportError(
                        row=i,
                        field="product_name",
                        value="",
                        error="Product Name is required and cannot be empty",
                        error_code="REQUIRED_FIELD_MISSING"
                    ))
                    simple_errors.append(f"Row {i}: Product Name is required and cannot be empty")
                    skipped_records += 1
                    continue
                    
                if not unit:
                    detailed_errors.append(BulkImportError(
                        row=i,
                        field="unit",
                        value="",
                        error="Unit is required and cannot be empty",
                        error_code="REQUIRED_FIELD_MISSING"
                    ))
                    simple_errors.append(f"Row {i}: Unit is required and cannot be empty")
                    skipped_records += 1
                    continue
                
                # Enhanced quantity validation
                try:
                    quantity = float(record.get("quantity", 0))
                    if quantity < 0:
                        detailed_errors.append(BulkImportError(
                            row=i,
                            field="quantity",
                            value=str(record.get("quantity")),
                            error="Quantity cannot be negative",
                            error_code="INVALID_VALUE"
                        ))
                        simple_errors.append(f"Row {i}: Quantity cannot be negative")
                        skipped_records += 1
                        continue
                except (ValueError, TypeError):
                    detailed_errors.append(BulkImportError(
                        row=i,
                        field="quantity",
                        value=str(record.get("quantity")),
                        error=f"Invalid quantity value: {record.get('quantity')}",
                        error_code="INVALID_DATA_TYPE"
                    ))
                    simple_errors.append(f"Row {i}: Invalid data format - could not convert string to float: '{record.get('quantity')}'")
                    skipped_records += 1
                    continue
                
                # Log record details for debugging
                logger.debug(f"Processing row {i}: product_name={product_name}, unit={unit}, quantity={quantity}")
                
                # Check if product exists by name
                stmt = select(Product).where(
                    Product.product_name == product_name,
                    Product.organization_id == org_id
                )
                result = await db.execute(stmt)
                product = result.scalar_one_or_none()
                
                if not product:
                    # Create new product if not exists with enhanced validation
                    try:
                        # Validate and clean optional fields
                        def to_optional(value):
                            if value is None:
                                return None
                            val_str = str(value).strip().lower()
                            if val_str in ['', 'none', 'null', 'na', 'nan']:
                                return None
                            return str(value).strip()
                        
                        hsn_code = to_optional(record.get("hsn_code"))
                        part_number = to_optional(record.get("part_number"))
                        
                        # Validate numeric fields
                        try:
                            unit_price = float(record.get("unit_price", 0))
                            if unit_price < 0:
                                warnings.append(f"Row {i}: Unit price is negative for '{product_name}', setting to 0")
                                unit_price = 0.0
                        except (ValueError, TypeError):
                            unit_price = 0.0
                            warnings.append(f"Row {i}: Invalid unit price for '{product_name}', setting to 0")
                        
                        try:
                            gst_rate = float(record.get("gst_rate", 18.0))
                            if gst_rate < 0 or gst_rate > 100:
                                warnings.append(f"Row {i}: Invalid GST rate for '{product_name}', setting to 18%")
                                gst_rate = 18.0
                        except (ValueError, TypeError):
                            gst_rate = 18.0
                            warnings.append(f"Row {i}: Invalid GST rate for '{product_name}', setting to 18%")
                        
                        try:
                            reorder_level = int(float(record.get("reorder_level", 10)))
                            if reorder_level < 0:
                                reorder_level = 10
                                warnings.append(f"Row {i}: Invalid reorder level for '{product_name}', setting to 10")
                        except (ValueError, TypeError):
                            reorder_level = 10
                            warnings.append(f"Row {i}: Invalid reorder level for '{product_name}', setting to 10")
                        
                        product_data = {
                            "product_name": product_name,
                            "hsn_code": hsn_code,
                            "part_number": part_number,
                            "unit": unit.upper(),
                            "unit_price": unit_price,
                            "gst_rate": gst_rate,
                            "reorder_level": reorder_level,
                            "is_active": True
                        }
                        
                        new_product = Product(
                            organization_id=org_id,
                            **product_data
                        )
                        db.add(new_product)
                        await db.flush()  # Get the new product ID
                        product = new_product
                        created_products += 1
                        logger.info(f"Created new product: {product_name}")
                        
                    except Exception as e:
                        detailed_errors.append(BulkImportError(
                            row=i,
                            field="product_creation",
                            value=product_name,
                            error=f"Failed to create product: {str(e)}",
                            error_code="PRODUCT_CREATION_FAILED"
                        ))
                        simple_errors.append(f"Row {i}: Invalid product data - {str(e)}")
                        logger.error(f"Row {i}: Failed to create product - {str(e)}")
                        skipped_records += 1
                        continue
                
                # Handle stock with enhanced validation
                stmt = select(Stock).where(
                    Stock.product_id == product.id,
                    Stock.organization_id == org_id
                )
                result = await db.execute(stmt)
                stock = result.scalar_one_or_none()
                
                location = str(record.get("location", "")).strip() or ""
                
                if not stock:
                    # Create new stock entry
                    new_stock = Stock(
                        organization_id=org_id,
                        product_id=product.id,
                        quantity=quantity,
                        unit=unit.upper(),
                        location=location,
                        last_updated=datetime.utcnow()
                    )
                    db.add(new_stock)
                    created_stocks += 1
                    logger.info(f"Created stock entry for: {product_name}")
                else:
                    # Update stock based on mode
                    old_quantity = stock.quantity
                    if mode == 'add':
                        new_quantity = old_quantity + quantity
                    else:  # replace
                        new_quantity = quantity
                    
                    stock.quantity = new_quantity
                    stock.unit = unit.upper()
                    stock.location = location
                    stock.last_updated = datetime.utcnow()
                    updated_stocks += 1
                    
                    if old_quantity != new_quantity:
                        warnings.append(f"Row {i}: Updated stock for '{product_name}' from {old_quantity} to {new_quantity} (mode: {mode})")
                    
                    logger.info(f"Updated stock for: {product_name} (mode: {mode})")
                    
            except Exception as e:
                detailed_errors.append(BulkImportError(
                    row=i,
                    error=f"Error processing record: {str(e)}",
                    error_code="PROCESSING_ERROR"
                ))
                simple_errors.append(f"Row {i}: Error processing record - {str(e)}")
                logger.error(f"Row {i}: Error processing record - {str(e)}")
                skipped_records += 1
                continue
        
        # Commit all changes
        await db.commit()
        
        end_time = datetime.now(pytz.utc)
        processing_time = (end_time - start_time).total_seconds()
        
        logger.info(f"Stock import completed by {current_user.email}: "
                   f"{created_products} products created, {created_stocks} stocks created, "
                   f"{updated_stocks} stocks updated, {len(detailed_errors)} errors")
        
        message_parts = []
        if created_products > 0:
            message_parts.append(f"{created_products} products created")
        if created_stocks > 0:
            message_parts.append(f"{created_stocks} stock entries created")
        if updated_stocks > 0:
            message_parts.append(f"{updated_stocks} stock entries updated")
        if skipped_records > 0:
            message_parts.append(f"{skipped_records} records skipped")
        if detailed_errors:
            message_parts.append(f"{len(detailed_errors)} errors encountered")
        
        message = f"Import completed. {', '.join(message_parts)}." if message_parts else "Import completed successfully."
        
        return BulkImportResponse(
            message=message,
            total_processed=len(records),
            created=created_stocks,
            updated=updated_stocks,
            skipped=skipped_records,
            errors=simple_errors,
            detailed_errors=detailed_errors,
            warnings=warnings,
            processing_time_seconds=processing_time
        )
        
    except HTTPException as e:
        logger.error(f"HTTP error during stock import: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error importing stock: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error during import processing: {str(e)}"
        )

@router.post("/import/excel", response_model=BulkImportResponse)
async def import_stock_excel(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Import stock entries from Excel file - alias for bulk import"""
    return await bulk_import_stock(file, db, current_user)

@router.get("/template/excel")
async def download_stock_template():
    """Download Excel template for stock bulk import with error handling"""
    try:
        excel_data = StockExcelService.create_template()
        logger.info("Stock template downloaded successfully")
        return ExcelService.create_streaming_response(excel_data, "stock_template.xlsx")
    except Exception as e:
        logger.error(f"Error generating stock template: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate stock template. Please try again later."
        )

@router.get("/export/excel")
async def export_stock_excel(
    skip: int = 0,
    limit: int = 1000,
    product_id: int = None,
    low_stock_only: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Export stock to Excel"""
    org_id = require_current_organization_id(current_user)
    
    # Get stock using the same logic as the list endpoint
    stmt = select(Stock).join(Product)
    
    stmt = stmt.where(Stock.organization_id == org_id)
    
    if product_id:
        stmt = stmt.where(Stock.product_id == product_id)
    
    if low_stock_only:
        stmt = stmt.where(Stock.quantity <= Product.reorder_level)
    
    result = await db.execute(stmt.offset(skip).limit(limit))
    stock_items = result.scalars().all()
    
    # Convert to dict format for Excel export
    stock_data = []
    for stock in stock_items:
        stock_data.append({
            "product_name": stock.product.product_name,
            "hsn_code": stock.product.hsn_code or "",
            "part_number": stock.product.part_number or "",
            "unit": stock.unit,
            "unit_price": stock.product.unit_price,
            "gst_rate": stock.product.gst_rate,
            "reorder_level": stock.product.reorder_level,
            "quantity": stock.quantity,
            "location": stock.location or "",
        })
    
    excel_data = StockExcelService.export_stock(stock_data)
    return ExcelService.create_streaming_response(excel_data, "stock_export.xlsx")

async def update_stock_from_po(po_id: int, db: AsyncSession):
    """Update stock valuation using discounted prices from PO items (called after GRN or PO completion)"""
    stmt = select(PurchaseOrderItem).where(PurchaseOrderItem.purchase_order_id == po_id)
    result = await db.execute(stmt)
    items = result.scalars().all()
    
    for item in items:
        # Get or create stock
        stmt_stock = select(Stock).where(Stock.product_id == item.product_id)
        result_stock = await db.execute(stmt_stock)
        stock = result_stock.scalar_one_or_none()
        
        if not stock:
            stock = Stock(
                organization_id=item.purchase_order.organization_id,
                product_id=item.product_id,
                quantity=item.quantity,
                unit=item.unit,
                location="",
                last_updated=datetime.utcnow()
            )
            db.add(stock)
            await db.flush()
        
        # Update quantity (add received quantity; assume full for simplicity, adjust for partial GRN)
        stock.quantity += item.quantity
        stock.last_updated = datetime.utcnow()
        
        # Update valuation - use simple average for now (can change to weighted)
        current_value = stock.quantity * item.product.unit_price  # Old value
        new_value = item.quantity * item.discounted_price
        total_quantity = stock.quantity + item.quantity
        new_avg_price = (current_value + new_value) / total_quantity if total_quantity > 0 else item.discounted_price
        item.product.unit_price = new_avg_price  # Update product's effective price for future use
        
        # Log transaction
        transaction = InventoryTransaction(
            organization_id=stock.organization_id,
            product_id=stock.product_id,
            quantity=item.quantity,
            transaction_type="purchase",
            reference_number=item.purchase_order.voucher_number,
            notes=f"PO {item.purchase_order.voucher_number} - Discounted price: {item.discounted_price}"
        )
        db.add(transaction)
    
    await db.commit()