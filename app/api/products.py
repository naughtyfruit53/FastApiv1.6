# Revised: app/api/products.py

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload
from typing import List, Optional
import logging
import os
import uuid
import shutil

from app.core.database import get_db
from app.core.enforcement import require_access
from app.core.org_restrictions import validate_company_setup
from app.models import User, Product, Stock, ProductFile, Organization, Company
from app.schemas.base import ProductCreate, ProductUpdate, ProductInDB, ProductResponse, BulkImportResponse, ProductFileResponse
from app.services.excel_service import ProductExcelService, ExcelService

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("", response_model=List[ProductResponse])
async def get_products(
    skip: int = 0,
    limit: int = 1000000,
    search: Optional[str] = None,
    active_only: bool = True,
    auth: tuple = Depends(require_access("product", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get products in current organization"""
    current_user, org_id = auth
    
    stmt = select(Product).where(Product.organization_id == org_id)
    
    if active_only:
        stmt = stmt.where(Product.is_active == True)
    
    if search:
        search_filter = or_(
            Product.product_name.contains(search),
            Product.hsn_code.contains(search),
            Product.part_number.contains(search)
        )
        stmt = stmt.where(search_filter)
    
    # Add explicit ordering for stable results
    stmt = stmt.order_by(Product.product_name.asc())
    
    # Include files relationship
    stmt = stmt.options(selectinload(Product.files))
    
    result = await db.execute(stmt.offset(skip).limit(limit))
    products = result.scalars().all()
    
    # Use list comprehension with sync from_product
    response_products = [ProductResponse.from_product(product) for product in products]
    
    return response_products

@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    auth: tuple = Depends(require_access("product", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get product by ID"""
    current_user, org_id = auth
    
    stmt = select(Product).options(selectinload(Product.files)).where(
        Product.id == product_id,
        Product.organization_id == org_id
    )
    result = await db.execute(stmt)
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    return ProductResponse.from_product(product)  # Sync call

@router.post("", response_model=ProductResponse)
async def create_product(
    product: ProductCreate,
    auth: tuple = Depends(require_access("product", "create")),
    db: AsyncSession = Depends(get_db)
):
    """Create new product"""
    current_user, org_id = auth
    
    # Check if product name already exists in organization
    stmt = select(Product).where(
        Product.product_name == product.product_name,
        Product.organization_id == org_id
    )
    result = await db.execute(stmt)
    existing_product = result.scalar_one_or_none()
    if existing_product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product with this name already exists in organization"
        )
    
    # Create new product
    db_product = Product(
        organization_id=org_id,
        **product.dict()
    )
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)
    
    # Create initial stock entry with quantity 0
    new_stock = Stock(
        organization_id=org_id,
        product_id=db_product.id,
        quantity=0.0,
        unit=db_product.unit,
        location="Default"
    )
    db.add(new_stock)
    await db.commit()
    
    # Re-query with eager loading
    stmt = select(Product).options(selectinload(Product.files)).where(Product.id == db_product.id)
    result = await db.execute(stmt)
    db_product = result.scalar_one()
    
    logger.info(f"Product {product.product_name} created in org {org_id} by {current_user.email}")
    return ProductResponse.from_product(db_product)  # Sync call

@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_update: ProductUpdate,
    auth: tuple = Depends(require_access("product", "update")),
    db: AsyncSession = Depends(get_db)
):
    """Update product"""
    current_user, org_id = auth
    
    stmt = select(Product).where(
        Product.id == product_id,
        Product.organization_id == org_id
    )
    result = await db.execute(stmt)
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Check name uniqueness if being updated
    if product_update.product_name and product_update.product_name != product.product_name:
        stmt = select(Product).where(
            Product.product_name == product_update.product_name,
            Product.organization_id == product.organization_id
        )
        result = await db.execute(stmt)
        existing_product = result.scalar_one_or_none()
        if existing_product:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product with this name already exists in organization"
            )
    
    # Update product
    update_data = product_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        if field in ['part_number', 'hsn_code'] and value == '':
            value = None
        setattr(product, field, value)
    
    await db.commit()
    
    # Re-query with eager load
    stmt = select(Product).options(selectinload(Product.files)).where(Product.id == product_id)
    result = await db.execute(stmt)
    product = result.scalar_one()
    
    logger.info(f"Product {product.product_name} updated by {current_user.email}")
    return ProductResponse.from_product(product)  # Sync call

@router.delete("/{product_id}")
async def delete_product(
    product_id: int,
    auth: tuple = Depends(require_access("product", "delete")),
    db: AsyncSession = Depends(get_db)
):
    """Delete product (admin only)"""
    current_user, org_id = auth
    
    stmt = select(Product).where(
        Product.id == product_id,
        Product.organization_id == org_id
    )
    result = await db.execute(stmt)
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # TODO: Check if product has any associated transactions/vouchers
    # before allowing deletion
    
    await db.delete(product)
    await db.commit()
    
    logger.info(f"Product {product.product_name} deleted by {current_user.email}")
    return {"message": "Product deleted successfully"}

@router.post("/validate-product-ids")
async def validate_product_ids(
    product_ids: List[int],
    auth: tuple = Depends(require_access("product", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Validate product IDs and check for missing or invalid names"""
    current_user, org_id = auth
    
    try:
        stmt = select(Product).where(
            Product.id.in_(product_ids),
            Product.organization_id == org_id,
            Product.is_active == True
        )
        result = await db.execute(stmt)
        products = result.scalars().all()
        
        product_dict = {p.id: p for p in products}
        invalid_products = []
        
        for product_id in product_ids:
            product = product_dict.get(product_id)
            if not product:
                invalid_products.append({"id": product_id, "error": "Product does not exist or is inactive"})
            elif not product.product_name or product.product_name.strip() == '':
                invalid_products.append({"id": product_id, "error": "Product has no valid name"})
        
        return {"invalid_products": invalid_products}
        
    except Exception as e:
        logger.error(f"Error validating product IDs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to validate product IDs"
        )

@router.get("/template/excel")
async def download_products_template(
    auth: tuple = Depends(require_access("product", "read"))
):
    """Download Excel template for products bulk import"""
    current_user, org_id = auth
    excel_data = ProductExcelService.create_template()
    return ExcelService.create_streaming_response(excel_data, "products_template.xlsx")

@router.get("/export/excel")
async def export_products_excel(
    skip: int = 0,
    limit: int = 1000,
    search: Optional[str] = None,
    active_only: bool = True,
    auth: tuple = Depends(require_access("product", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Export products to Excel"""
    current_user, org_id = auth
    
    # Get products using the same logic as the list endpoint
    stmt = select(Product).where(Product.organization_id == org_id)
    
    if active_only:
        stmt = stmt.where(Product.is_active == True)
    
    if search:
        search_filter = or_(
            Product.product_name.contains(search),
            Product.hsn_code.contains(search),
            Product.part_number.contains(search)
        )
        stmt = stmt.where(search_filter)
    
    result = await db.execute(stmt.offset(skip).limit(limit))
    products = result.scalars().all()
    
    # Convert to dict format for Excel export
    products_data = []
    for product in products:
        products_data.append({
            "product_name": product.product_name,
            "hsn_code": product.hsn_code or "",
            "part_number": product.part_number or "",
            "unit": product.unit,
            "unit_price": product.unit_price,
            "gst_rate": product.gst_rate,
            "is_gst_inclusive": product.is_gst_inclusive,
            "reorder_level": product.reorder_level,
            "description": product.description or "",
            "is_manufactured": product.is_manufactured,
        })
    
    excel_data = ProductExcelService.export_products(products_data)
    return ExcelService.create_streaming_response(excel_data, "products_export.xlsx")

@router.post("/import/excel", response_model=BulkImportResponse)
async def import_products_excel(
    file: UploadFile = File(...),
    auth: tuple = Depends(require_access("product", "create")),
    db: AsyncSession = Depends(get_db)
):
    """Import products from Excel file"""
    current_user, org_id = auth
    
    # Validate company setup is completed before allowing product imports
    await validate_company_setup(db, org_id)
    
    # Validate file type
    if not file.filename or not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only Excel files (.xlsx, .xls) are allowed"
        )
    
    try:
        # Parse Excel file
        records = await ExcelService.parse_excel_file(file, ProductExcelService.REQUIRED_COLUMNS, "Product Import Template")
        
        if not records:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No data found in Excel file"
            )
        
        created_count = 0
        updated_count = 0
        created_stocks = 0
        updated_stocks = 0
        errors = []
        
        for i, record in enumerate(records, 1):
            try:
                # Map Excel columns to model fields
                product_data = {
                    "product_name": str(record.get("product_name", "")).strip(),
                    "hsn_code": str(record.get("hsn_code", "")).strip(),
                    "part_number": str(record.get("part_number", "")).strip(),
                    "unit": str(record.get("unit", "")).strip(),
                    "unit_price": float(record.get("unit_price", 0)),
                    "gst_rate": float(record.get("gst_rate", 0)),
                    "is_gst_inclusive": str(record.get("is_gst_inclusive", "")).upper() in ["TRUE", "YES", "1"],
                    "reorder_level": int(float(record.get("reorder_level", 0))),
                    "description": str(record.get("description", "")).strip(),
                    "is_manufactured": str(record.get("is_manufactured", "")).upper() in ["TRUE", "YES", "1"],
                }
                
                # Validate required fields
                if not product_data["product_name"]:
                    errors.append(f"Row {i}: Product Name is required")
                    continue
                    
                if not product_data["unit"]:
                    errors.append(f"Row {i}: Unit is required")
                    continue
                
                # Check if product already exists
                stmt = select(Product).where(
                    Product.product_name == product_data["product_name"],
                    Product.organization_id == org_id
                )
                result = await db.execute(stmt)
                existing_product = result.scalar_one_or_none()
                
                product = None
                if existing_product:
                    # Update existing product
                    for field, value in product_data.items():
                        setattr(existing_product, field, value)
                    updated_count += 1
                    product = existing_product
                    logger.info(f"Updated product: {product_data['product_name']}")
                else:
                    # Create new product
                    new_product = Product(
                        organization_id=org_id,
                        **product_data
                    )
                    db.add(new_product)
                    await db.flush()  # Get the new product ID
                    created_count += 1
                    product = new_product
                    logger.info(f"Created product: {product_data['product_name']}")
                
                # Handle stock creation/update for the product
                # Check for optional initial stock quantity in Excel
                initial_quantity = record.get("initial_quantity", None)
                initial_location_raw = record.get("initial_location", "")
                initial_location = str(initial_location_raw).strip() if initial_location_raw and str(initial_location_raw).strip() != 'nan' else ""
                
                # Only create/update stock if initial_quantity is provided or if it's a new product
                if initial_quantity is not None or not existing_product:
                    quantity = float(initial_quantity) if initial_quantity is not None else 0.0
                    
                    # Check if stock entry exists for this product
                    stmt = select(Stock).where(
                        Stock.product_id == product.id,
                        Stock.organization_id == org_id
                    )
                    result = await db.execute(stmt)
                    existing_stock = result.scalar_one_or_none()
                    
                    if existing_stock:
                        # Update existing stock only if initial_quantity was provided
                        if initial_quantity is not None:
                            setattr(existing_stock, "quantity", quantity)
                            existing_stock.unit = product_data["unit"]
                            if initial_location:
                                setattr(existing_stock, "location", initial_location)
                            updated_stocks += 1
                            logger.info(f"Updated stock for product: {product_data['product_name']}")
                    else:
                        # Create new stock entry
                        new_stock = Stock(
                            organization_id=org_id,
                            product_id=product.id,
                            quantity=quantity,
                            unit=product_data["unit"],
                            location=initial_location or "Default"
                        )
                        db.add(new_stock)
                        created_stocks += 1
                        logger.info(f"Created stock entry for product: {product_data['product_name']} with quantity: {quantity}")
                    
            except (ValueError, TypeError) as e:
                errors.append(f"Row {i}: Invalid data format - {str(e)}")
                continue
            except Exception as e:
                errors.append(f"Row {i}: Error processing record - {str(e)}")
                continue
        
        # Commit all changes
        await db.commit()
        
        logger.info(f"Products import completed by {current_user.email}: "
                   f"{created_count} created, {updated_count} updated, "
                   f"{created_stocks} stock entries created, {updated_stocks} stock entries updated, "
                   f"{len(errors)} errors")
        
        # Build success message
        message_parts = []
        if created_count > 0:
            message_parts.append(f"{created_count} products created")
        if updated_count > 0:
            message_parts.append(f"{updated_count} products updated")
        if created_stocks > 0:
            message_parts.append(f"{created_stocks} stock entries created")
        if updated_stocks > 0:
            message_parts.append(f"{updated_stocks} stock entries updated")
        
        message = f"Import completed successfully. {', '.join(message_parts)}."
        
        return BulkImportResponse(
            message=message,
            total_processed=len(records),
            created=created_count,
            updated=updated_count,
            errors=errors
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error importing products: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing import: {str(e)}"
        )

# File upload directory
UPLOAD_DIR = "Uploads/products"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/{product_id}/files", response_model=ProductFileResponse)
async def upload_product_file(
    product_id: int,
    file: UploadFile = File(...),
    auth: tuple = Depends(require_access("product", "update")),
    db: AsyncSession = Depends(get_db)
):
    """Upload a file for a product (max 5 files per product)"""
    current_user, org_id = auth
    
    # Verify product exists and belongs to current organization
    stmt = select(Product).where(
        Product.id == product_id,
        Product.organization_id == org_id
    )
    result = await db.execute(stmt)
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Check file count limit (max 5 files per product)
    stmt = select(ProductFile).where(
        ProductFile.product_id == product_id,
        ProductFile.organization_id == org_id
    )
    result = await db.execute(stmt)
    existing_files = result.scalars().all()
    existing_files_count = len(existing_files)
    
    if existing_files_count >= 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 5 files allowed per product"
        )
    
    # Validate file size (max 10MB)
    if file.size and file.size > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size must be less than 10MB"
        )
    
    # Generate unique filename
    file_extension = os.path.splitext(file.filename or "")[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    try:
        # Save file to disk
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Create database record
        db_file = ProductFile(
            product_id=product_id,
            organization_id=org_id,
            filename=unique_filename,
            original_filename=file.filename or "unknown",
            file_path=file_path,
            file_size=file.size or 0,
            content_type=file.content_type or "application/octet-stream"
        )
        
        db.add(db_file)
        await db.commit()
        await db.refresh(db_file)
        
        return ProductFileResponse(
            id=db_file.id,
            filename=db_file.filename,
            original_filename=db_file.original_filename,
            file_size=db_file.file_size,
            content_type=db_file.content_type,
            product_id=db_file.product_id,
            created_at=db_file.created_at
        )
        
    except Exception as e:
        # Clean up file if database operation fails
        if os.path.exists(file_path):
            os.remove(file_path)
        logger.error(f"Error uploading product file: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error uploading file"
        )

@router.get("/{product_id}/files", response_model=List[ProductFileResponse])
async def get_product_files(
    product_id: int,
    auth: tuple = Depends(require_access("product", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get all files for a product"""
    current_user, org_id = auth
    
    # Verify product exists and belongs to current organization
    stmt = select(Product).where(
        Product.id == product_id,
        Product.organization_id == org_id
    )
    result = await db.execute(stmt)
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    stmt = select(ProductFile).where(
        ProductFile.product_id == product_id,
        ProductFile.organization_id == org_id
    )
    result = await db.execute(stmt)
    files = result.scalars().all()
    
    return [
        ProductFileResponse(
            id=f.id,
            filename=f.filename,
            original_filename=f.original_filename,
            file_size=f.file_size,
            content_type=f.content_type,
            product_id=f.product_id,
            created_at=f.created_at
        ) for f in files
    ]

@router.get("/{product_id}/files/{file_id}/download")
async def download_product_file(
    product_id: int,
    file_id: int,
    auth: tuple = Depends(require_access("product", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Download a product file"""
    current_user, org_id = auth
    
    # Get file record
    stmt = select(ProductFile).where(
        ProductFile.id == file_id,
        ProductFile.product_id == product_id,
        ProductFile.organization_id == org_id
    )
    result = await db.execute(stmt)
    file_record = result.scalar_one_or_none()
    
    if not file_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # Check if file exists on disk
    if not os.path.exists(file_record.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found on disk"
        )
    
    return StreamingResponse(
        open(file_record.file_path, "rb"),
        media_type=file_record.content_type,
        headers={"Content-Disposition": f"attachment; filename={file_record.original_filename}"}
    )

@router.delete("/{product_id}/files/{file_id}")
async def delete_product_file(
    product_id: int,
    file_id: int,
    auth: tuple = Depends(require_access("product", "delete")),
    db: AsyncSession = Depends(get_db)
):
    """Delete a product file"""
    current_user, org_id = auth
    
    # Get file record
    stmt = select(ProductFile).where(
        ProductFile.id == file_id,
        ProductFile.product_id == product_id,
        ProductFile.organization_id == org_id
    )
    result = await db.execute(stmt)
    file_record = result.scalar_one_or_none()
    
    if not file_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    try:
        # Remove file from disk
        if os.path.exists(file_record.file_path):
            os.remove(file_record.file_path)
        
        # Remove database record
        await db.delete(file_record)
        await db.commit()
        
        return {"message": "File deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting product file: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting file"
        )

@router.post("/check-consistency")
async def check_products_stock_consistency(
    fix_issues: bool = False,
    auth: tuple = Depends(require_access("product", "update")),
    db: AsyncSession = Depends(get_db)
):
    """
    Check consistency between products and stock tables.
    If fix_issues=True, creates missing stock entries and removes orphaned stock.
    """
    current_user, org_id = auth
    
    # Count products and stock entries
    stmt = select(Product).where(Product.organization_id == org_id)
    result = await db.execute(stmt)
    products_count = len(result.scalars().all())
    
    stmt = select(Stock).where(Stock.organization_id == org_id)
    result = await db.execute(stmt)
    stock_count = len(result.scalars().all())
    
    result = {
        "organization_id": org_id,
        "products_count": products_count,
        "stock_count": stock_count,
        "consistency_issues": []
    }
    
    # Find products without stock entries
    stmt = select(Product).outerjoin(
        Stock, Product.id == Stock.product_id
    ).where(
        Product.organization_id == org_id,
        Product.is_active == True,
        Stock.id.is_(None)
    )
    result = await db.execute(stmt)
    products_without_stock = result.scalars().all()
    
    if products_without_stock:
        result["consistency_issues"].append({
            "type": "products_without_stock",
            "count": len(products_without_stock),
            "products": [{"id": p.id, "name": p.product_name} for p in products_without_stock]
        })
        
        if fix_issues:
            # Create missing stock entries
            for product in products_without_stock:
                new_stock = Stock(
                    organization_id=org_id,
                    product_id=product.id,
                    quantity=0.0,
                    unit=product.unit,
                    location="UNASSIGNED"
                )
                db.add(new_stock)
            
            result["fixed_missing_stock"] = len(products_without_stock)
    
    # Find orphaned stock entries
    stmt = select(Stock).outerjoin(
        Product, Stock.product_id == Product.id
    ).where(
        Stock.organization_id == org_id,
        Product.id.is_(None)
    )
    result = await db.execute(stmt)
    orphaned_stock = result.scalars().all()
    
    if orphaned_stock:
        result["consistency_issues"].append({
            "type": "orphaned_stock",
            "count": len(orphaned_stock),
            "stock_ids": [s.id for s in orphaned_stock]
        })
        
        if fix_issues:
            # Remove orphaned stock entries
            for stock in orphaned_stock:
                await db.delete(stock)
            
            result["removed_orphaned_stock"] = len(orphaned_stock)
    
    # Check for inactive products with stock
    stmt = select(Product, Stock).join(
        Stock, Product.id == Stock.product_id
    ).where(
        Product.organization_id == org_id,
        Product.is_active == False,
        Stock.quantity > 0
    )
    result = await db.execute(stmt)
    inactive_products_with_stock = result.all()
    
    if inactive_products_with_stock:
        result["consistency_issues"].append({
            "type": "inactive_products_with_stock",
            "count": len(inactive_products_with_stock),
            "products": [{"id": p.id, "name": p.product_name, "stock_qty": s.quantity} 
                        for p, s in inactive_products_with_stock]
        })
    
    result["is_consistent"] = len(result["consistency_issues"]) == 0
    result["recommendations"] = []
    
    if not result["is_consistent"]:
        result["recommendations"].append("Run with fix_issues=true to automatically fix missing stock entries and orphaned stock")
        result["recommendations"].append("Consider reactivating products with existing stock or transferring stock to active products")
    
    # Commit all fixes at once for atomicity if any fixes were applied
    if fix_issues and ("fixed_missing_stock" in result or "removed_orphaned_stock" in result):
        await db.commit()
    
    return result