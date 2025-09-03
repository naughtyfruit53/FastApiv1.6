# app/api/products.py

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.api.v1.auth import get_current_active_user, get_current_admin_user
from app.core.tenant import TenantQueryMixin, require_current_organization_id, validate_company_setup_for_operations
from app.core.org_restrictions import require_organization_access, ensure_organization_context
from app.models import User, Product, Stock, ProductFile, Organization, Company
from app.schemas.base import ProductCreate, ProductUpdate, ProductInDB, ProductResponse, BulkImportResponse, ProductFileResponse
from app.services.excel_service import ProductExcelService, ExcelService
import logging
import os
import uuid
import shutil

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("", response_model=List[ProductResponse])
async def get_products(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    active_only: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get products in current organization"""
    
    # Check if user is app super admin
    org_id = ensure_organization_context(current_user)
    
    query = db.query(Product)
    query = TenantQueryMixin.filter_by_tenant(query, Product, org_id)
    
    if active_only:
        query = query.filter(Product.is_active == True)
    
    if search:
        search_filter = (
            Product.product_name.contains(search) |
            Product.hsn_code.contains(search) |
            Product.part_number.contains(search)
        )
        query = query.filter(search_filter)
    
    # Include files relationship
    from sqlalchemy.orm import selectinload
    query = query.options(selectinload(Product.files))
    
    products = query.offset(skip).limit(limit).all()
    return [ProductResponse.from_product(product) for product in products]

@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get product by ID"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Ensure tenant access for non-super-admin users
    if not current_user.is_super_admin is True:
        TenantQueryMixin.ensure_tenant_access(product, getattr(product, "organization_id", None))
    
    return ProductResponse.from_product(product)

@router.post("", response_model=ProductResponse)
async def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create new product"""
    
    org_id = require_current_organization_id()
    
    # Check if product name already exists in organization
    existing_product = db.query(Product).filter(
        Product.product_name == product.product_name,
        Product.organization_id == org_id
    ).first()
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
    db.commit()
    db.refresh(db_product)
    
    logger.info(f"Product {product.product_name} created in org {org_id} by {current_user.email}")
    return ProductResponse.from_product(db_product)

@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_update: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update product"""
    
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Ensure tenant access for non-super-admin users
    if not bool(current_user.is_super_admin):
        TenantQueryMixin.ensure_tenant_access(product, getattr(product, "organization_id", None))
    
    # Check name uniqueness if being updated
    if product_update.product_name and product_update.product_name != product.product_name:
        existing_product = db.query(Product).filter(
            Product.product_name == product_update.product_name,
            Product.organization_id == product.organization_id
        ).first()
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
    
    db.commit()
    db.refresh(product)
    
    logger.info(f"Product {product.product_name} updated by {current_user.email}")
    return ProductResponse.from_product(product)

@router.delete("/{product_id}")
async def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Delete product (admin only)"""
    
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Ensure tenant access for non-super-admin users
    if not bool(current_user.is_super_admin):
        TenantQueryMixin.ensure_tenant_access(product, getattr(product, "organization_id", None))
    
    # TODO: Check if product has any associated transactions/vouchers
    # before allowing deletion
    
    db.delete(product)
    db.commit()
    
    logger.info(f"Product {product.product_name} deleted by {current_user.email}")
    return {"message": "Product deleted successfully"}

# Excel Import/Export/Template endpoints

@router.get("/template/excel")
async def download_products_template(
    current_user: User = Depends(get_current_active_user)
):
    """Download Excel template for products bulk import"""
    excel_data = ProductExcelService.create_template()
    return ExcelService.create_streaming_response(excel_data, "products_template.xlsx")

@router.get("/export/excel")
async def export_products_excel(
    skip: int = 0,
    limit: int = 1000,
    search: Optional[str] = None,
    active_only: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Export products to Excel"""
    
    # Get products using the same logic as the list endpoint
    query = db.query(Product)
    
    # Apply tenant filtering for non-super-admin users
    if not bool(current_user.is_super_admin):
        org_id = require_current_organization_id()
        query = TenantQueryMixin.filter_by_tenant(query, Product, org_id)
    
    if active_only:
        query = query.filter(Product.is_active == True)
    
    if search:
        search_filter = (
            Product.product_name.contains(search) |
            Product.hsn_code.contains(search) |
            Product.part_number.contains(search)
        )
        query = query.filter(search_filter)
    
    products = query.offset(skip).limit(limit).all()
    
    # Convert to dict format for Excel export
    products_data = []
    for product in products:
        products_data.append({
            "product_name": product.product_name,  # Map name to product_name for consistency
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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Import products from Excel file"""
    
    org_id = require_current_organization_id()
    
    # Validate company setup is completed before allowing product imports
    validate_company_setup_for_operations(db, org_id)
    
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
                    "product_name": str(record.get("product_name", "")).strip(),  # Map product_name to name for DB
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
                existing_product = db.query(Product).filter(
                    Product.product_name == product_data["product_name"],
                    Product.organization_id == org_id
                ).first()
                
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
                    db.flush()  # Get the new product ID
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
                    existing_stock = db.query(Stock).filter(
                        Stock.product_id == product.id,
                        Stock.organization_id == org_id
                    ).first()
                    
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
        db.commit()
        
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
UPLOAD_DIR = "uploads/products"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/{product_id}/files", response_model=ProductFileResponse)
async def upload_product_file(
    product_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Upload a file for a product (max 5 files per product)"""
    
    org_id = ensure_organization_context(current_user)
    
    # Verify product exists and belongs to current organization
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.organization_id == org_id
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Check file count limit (max 5 files per product)
    existing_files_count = db.query(ProductFile).filter(
        ProductFile.product_id == product_id,
        ProductFile.organization_id == org_id
    ).count()
    
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
        db.commit()
        db.refresh(db_file)
        
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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all files for a product"""
    
    org_id = ensure_organization_context(current_user)
    
    # Verify product exists and belongs to current organization
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.organization_id == org_id
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    files = db.query(ProductFile).filter(
        ProductFile.product_id == product_id,
        ProductFile.organization_id == org_id
    ).all()
    
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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Download a product file"""
    
    org_id = ensure_organization_context(current_user)
    
    # Get file record
    file_record = db.query(ProductFile).filter(
        ProductFile.id == file_id,
        ProductFile.product_id == product_id,
        ProductFile.organization_id == org_id
    ).first()
    
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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a product file"""
    
    org_id = ensure_organization_context(current_user)
    
    # Get file record
    file_record = db.query(ProductFile).filter(
        ProductFile.id == file_id,
        ProductFile.product_id == product_id,
        ProductFile.organization_id == org_id
    ).first()
    
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
        db.delete(file_record)
        db.commit()
        
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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Check consistency between products and stock tables.
    If fix_issues=True, creates missing stock entries and removes orphaned stock.
    """
    
    # Get organization context
    org_id = ensure_organization_context(current_user)
    
    # Count products and stock entries
    products_count = db.query(Product).filter(Product.organization_id == org_id).count()
    stock_count = db.query(Stock).filter(Stock.organization_id == org_id).count()
    
    result = {
        "organization_id": org_id,
        "products_count": products_count,
        "stock_count": stock_count,
        "consistency_issues": []
    }
    
    # Find products without stock entries
    products_without_stock = db.query(Product).outerjoin(
        Stock, Product.id == Stock.product_id
    ).filter(
        Product.organization_id == org_id,
        Product.is_active == True,
        Stock.id.is_(None)
    ).all()
    
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
    orphaned_stock = db.query(Stock).outerjoin(
        Product, Stock.product_id == Product.id
    ).filter(
        Stock.organization_id == org_id,
        Product.id.is_(None)
    ).all()
    
    if orphaned_stock:
        result["consistency_issues"].append({
            "type": "orphaned_stock",
            "count": len(orphaned_stock),
            "stock_ids": [s.id for s in orphaned_stock]
        })
        
        if fix_issues:
            # Remove orphaned stock entries
            for stock in orphaned_stock:
                db.delete(stock)
            
            result["removed_orphaned_stock"] = len(orphaned_stock)
    
    # Check for inactive products with stock
    inactive_products_with_stock = db.query(Product, Stock).join(
        Stock, Product.id == Stock.product_id
    ).filter(
        Product.organization_id == org_id,
        Product.is_active == False,
        Stock.quantity > 0
    ).all()
    
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
        db.commit()
    
    return result


logger.info("Products router loaded")