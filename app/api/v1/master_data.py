# app/api/v1/master_data.py

"""
Master Data API endpoints for Categories, Units, Payment Terms, and Tax Codes
These endpoints provide complete CRUD operations for master data management
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, desc, asc, text
from typing import List, Optional, Dict, Any
from datetime import datetime
from decimal import Decimal
import logging

from app.core.database import get_db
from app.core.enforcement import require_access

from app.models.user_models import User
from app.models.master_data_models import (
    Category, Unit, TaxCode, PaymentTermsExtended
)
from app.schemas.master_data import (
    CategoryCreate, CategoryUpdate, CategoryResponse, CategoryList, CategoryFilter,
    UnitCreate, UnitUpdate, UnitResponse, UnitList, UnitFilter, UnitConversion,
    TaxCodeCreate, TaxCodeUpdate, TaxCodeResponse, TaxCodeList, TaxCodeFilter, TaxCalculation,
    PaymentTermsExtendedCreate, PaymentTermsExtendedUpdate, PaymentTermsExtendedResponse,
    PaymentTermsExtendedList, PaymentTermsExtendedFilter,
    BulkCategoryUpdate, BulkUnitUpdate, BulkTaxCodeUpdate, BulkPaymentTermsUpdate,
    MasterDataStats
)
from app.services.master_service import search_hsn_codes  # Added import for HSN search

logger = logging.getLogger(__name__)
router = APIRouter()


class MasterDataService:
    """Service class for master data operations with advanced business logic"""
    
    @staticmethod
    def build_category_hierarchy(categories: List[Category]) -> List[CategoryResponse]:
        """Build hierarchical category structure"""
        category_map = {cat.id: cat for cat in categories}
        root_categories = []
        
        for category in categories:
            if category.parent_category_id is None:
                root_categories.append(category)
            elif category.parent_category_id in category_map:
                parent = category_map[category.parent_category_id]
                if not hasattr(parent, 'children'):
                    parent.children = []
                parent.children.append(category)
        
        return root_categories
    
    @staticmethod
    async def calculate_category_path(category: Category, db: AsyncSession) -> str:
        """Calculate materialized path for category hierarchy"""
        if category.parent_category_id is None:
            return f"/{category.id}/"
        
        result = await db.execute(select(Category).filter_by(id=category.parent_category_id))
        parent = result.scalars().first()
        if parent:
            parent_path = parent.path or await MasterDataService.calculate_category_path(parent, db)
            return f"{parent_path}{category.id}/"
        
        return f"/{category.id}/"
    
    @staticmethod
    async def convert_units(value: Decimal, from_unit: Unit, to_unit: Unit, db: AsyncSession) -> Decimal:
        """Convert value between units with proper conversion factors"""
        if from_unit.id == to_unit.id:
            return value
        
        # Both units must have the same base unit for conversion
        from_base = from_unit.base_unit_id or from_unit.id
        to_base = to_unit.base_unit_id or to_unit.id
        
        if from_base != to_base:
            raise ValueError("Cannot convert between units of different types")
        
        # Convert to base unit first
        base_value = value * from_unit.conversion_factor
        
        # Convert from base unit to target unit
        converted_value = base_value / to_unit.conversion_factor
        
        return round(converted_value, to_unit.decimal_places)
    
    @staticmethod
    def calculate_tax(amount: Decimal, tax_code: TaxCode) -> Dict[str, Any]:
        """Calculate tax amount with component breakdown"""
        if not tax_code.is_active:
            raise ValueError("Tax code is not active")
        
        tax_amount = amount * (tax_code.tax_rate / 100)
        
        breakdown = {}
        if tax_code.components:
            for component, rate in tax_code.components.items():
                component_amount = amount * (Decimal(str(rate)) / 100)
                breakdown[component] = round(component_amount, 2)
        else:
            breakdown[tax_code.tax_type] = round(tax_amount, 2)
        
        return {
            "base_amount": amount,
            "tax_rate": tax_code.tax_rate,
            "tax_amount": round(tax_amount, 2),
            "total_amount": round(amount + tax_amount, 2),
            "breakdown": breakdown
        }


# Dashboard endpoint
@router.get("/dashboard", response_model=MasterDataStats)
async def get_master_data_dashboard(
    company_id: Optional[int] = Query(None, description="Filter by specific company"),
    auth: tuple = Depends(require_access("master_data", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get master data dashboard statistics"""
    current_user, organization_id = auth
    try:
        # Base queries with organization filter
        category_stmt = select(Category).filter_by(organization_id=organization_id)
        unit_stmt = select(Unit).filter_by(organization_id=organization_id)
        tax_code_stmt = select(TaxCode).filter_by(organization_id=organization_id)
        payment_terms_stmt = select(PaymentTermsExtended).filter_by(organization_id=organization_id)
        
        # Apply company filter if specified
        if company_id:
            category_stmt = category_stmt.where(or_(Category.company_id == company_id, Category.company_id.is_(None)))
            unit_stmt = unit_stmt.where(or_(Unit.company_id == company_id, Unit.company_id.is_(None)))
            tax_code_stmt = tax_code_stmt.where(or_(TaxCode.company_id == company_id, TaxCode.company_id.is_(None)))
            payment_terms_stmt = payment_terms_stmt.where(or_(PaymentTermsExtended.company_id == company_id, PaymentTermsExtended.company_id.is_(None)))
        
        # Calculate statistics
        category_result = await db.execute(category_stmt)
        categories = category_result.scalars().all()
        active_categories = len([c for c in categories if c.is_active])
        
        unit_result = await db.execute(unit_stmt)
        units = unit_result.scalars().all()
        active_units = len([u for u in units if u.is_active])
        
        tax_code_result = await db.execute(tax_code_stmt)
        tax_codes = tax_code_result.scalars().all()
        active_tax_codes = len([t for t in tax_codes if t.is_active])
        
        payment_terms_result = await db.execute(payment_terms_stmt)
        payment_terms = payment_terms_result.scalars().all()
        active_payment_terms = len([p for p in payment_terms if p.is_active])
        
        stats = MasterDataStats(
            total_categories=len(categories),
            active_categories=active_categories,
            total_units=len(units),
            active_units=active_units,
            total_tax_codes=len(tax_codes),
            active_tax_codes=active_tax_codes,
            total_payment_terms=len(payment_terms),
            active_payment_terms=active_payment_terms
        )
        
        return stats
        
    except Exception as e:
        logger.error(f"Error fetching master data dashboard: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch dashboard statistics")


# ============================================================================
# CATEGORY ENDPOINTS
# ============================================================================

@router.get("/categories", response_model=CategoryList)
async def get_categories(
    page: int = Query(1, ge=1),
    per_page: int = Query(100, ge=1, le=1000),
    category_filter: CategoryFilter = Depends(),
    auth: tuple = Depends(require_access("master_data", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get categories with filtering and pagination"""
    current_user, organization_id = auth
    try:
        stmt = select(Category).filter_by(organization_id=organization_id)
        
        # Apply filters
        if category_filter.category_type:
            stmt = stmt.where(Category.category_type == category_filter.category_type)
        
        if category_filter.parent_category_id is not None:
            stmt = stmt.where(Category.parent_category_id == category_filter.parent_category_id)
        
        if category_filter.is_active is not None:
            stmt = stmt.where(Category.is_active == category_filter.is_active)
        
        if category_filter.search:
            search_term = f"%{category_filter.search}%"
            stmt = stmt.where(
                or_(
                    Category.name.ilike(search_term),
                    Category.code.ilike(search_term),
                    Category.description.ilike(search_term)
                )
            )
        
        # Get total count
        count_result = await db.execute(select(func.count()).select_from(stmt.subquery()))
        total = count_result.scalar_one()
        
        # Apply pagination and ordering
        stmt = stmt.order_by(Category.sort_order, Category.name).offset((page-1)*per_page).limit(per_page)
        result = await db.execute(stmt)
        categories = result.scalars().all()
        
        return CategoryList(
            items=categories,
            total=total,
            page=page,
            per_page=per_page,
            total_pages=(total + per_page - 1) // per_page
        )
        
    except Exception as e:
        logger.error(f"Error fetching categories: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch categories")


@router.post("/categories", response_model=CategoryResponse)
async def create_category(
    category_data: CategoryCreate,
    auth: tuple = Depends(require_access("master_data", "create")),
    db: AsyncSession = Depends(get_db)
):
    """Create a new category"""
    current_user, organization_id = auth
    try:
        # Check for duplicate name
        existing_result = await db.execute(select(Category).filter_by(
            organization_id=organization_id,
            name=category_data.name,
            category_type=category_data.category_type
        ))
        existing = existing_result.scalars().first()
        
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Category with name '{category_data.name}' already exists for type '{category_data.category_type}'"
            )
        
        # Validate parent category if specified
        level = 0
        if category_data.parent_category_id:
            parent_result = await db.execute(select(Category).filter_by(
                id=category_data.parent_category_id,
                organization_id=organization_id
            ))
            parent = parent_result.scalars().first()
            
            if not parent:
                raise HTTPException(status_code=404, detail="Parent category not found")
            
            level = parent.level + 1
        
        # Create category
        category = Category(
            organization_id=organization_id,
            company_id=category_data.company_id,
            name=category_data.name,
            code=category_data.code,
            category_type=category_data.category_type,
            parent_category_id=category_data.parent_category_id,
            level=level,
            description=category_data.description,
            sort_order=category_data.sort_order,
            default_income_account_id=category_data.default_income_account_id,
            default_expense_account_id=category_data.default_expense_account_id,
            default_asset_account_id=category_data.default_asset_account_id,
            default_tax_code_id=category_data.default_tax_code_id,
            created_by=current_user.id
        )
        
        db.add(category)
        await db.commit()
        await db.refresh(category)
        
        # Calculate and update path
        category.path = await MasterDataService.calculate_category_path(category, db)
        await db.commit()
        await db.refresh(category)
        
        logger.info(f"Category created: {category.name} (ID: {category.id})")
        return category
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating category: {e}")
        raise HTTPException(status_code=500, detail="Failed to create category")


@router.get("/categories/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: int,
    auth: tuple = Depends(require_access("master_data", "read")),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific category"""
    current_user, organization_id = auth
    result = await db.execute(select(Category).filter_by(
        id=category_id,
        organization_id=organization_id
    ))
    category = result.scalars().first()
    
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    return category


@router.put("/categories/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    auth: tuple = Depends(require_access("master_data", "update")),
    db: AsyncSession = Depends(get_db),
):
    """Update a category"""
    current_user, organization_id = auth
    try:
        result = await db.execute(select(Category).filter_by(
            id=category_id,
            organization_id=organization_id
        ))
        category = result.scalars().first()
        
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        
        # Check for duplicate name if being updated
        if category_data.name and category_data.name != category.name:
            existing_result = await db.execute(select(Category).filter_by(
                organization_id=organization_id,
                name=category_data.name,
                category_type=category_data.category_type or category.category_type,
            ).filter(Category.id != category_id))
            existing = existing_result.scalars().first()
            
            if existing:
                raise HTTPException(
                    status_code=400,
                    detail=f"Category with name '{category_data.name}' already exists"
                )
        
        # Update fields
        update_fields = category_data.dict(exclude_unset=True)
        for field, value in update_fields.items():
            setattr(category, field, value)
        
        category.updated_by = current_user.id
        
        await db.commit()
        await db.refresh(category)
        
        logger.info(f"Category updated: {category.name} (ID: {category.id})")
        return category
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating category: {e}")
        raise HTTPException(status_code=500, detail="Failed to update category")


@router.delete("/categories/{category_id}")
async def delete_category(
    category_id: int,
    auth: tuple = Depends(require_access("master_data", "delete")),
    db: AsyncSession = Depends(get_db),
):
    """Delete a category"""
    current_user, organization_id = auth
    try:
        result = await db.execute(select(Category).filter_by(
            id=category_id,
            organization_id=organization_id
        ))
        category = result.scalars().first()
        
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        
        # Check for subcategories
        sub_result = await db.execute(select(func.count(Category.id)).filter_by(parent_category_id=category_id))
        subcategories = sub_result.scalar_one()
        if subcategories > 0:
            raise HTTPException(
                status_code=400,
                detail="Cannot delete category with subcategories"
            )
        
        await db.delete(category)
        await db.commit()
        
        logger.info(f"Category deleted: {category.name} (ID: {category.id})")
        return {"message": "Category deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting category: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete category")


# ============================================================================
# UNIT ENDPOINTS
# ============================================================================

@router.get("/units", response_model=UnitList)
async def get_units(
    page: int = Query(1, ge=1),
    per_page: int = Query(100, ge=1, le=1000),
    unit_filter: UnitFilter = Depends(),
    auth: tuple = Depends(require_access("master_data", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get units with filtering and pagination"""
    current_user, organization_id = auth
    try:
        stmt = select(Unit).filter_by(organization_id=organization_id)
        
        # Apply filters
        if unit_filter.unit_type:
            stmt = stmt.where(Unit.unit_type == unit_filter.unit_type)
        
        if unit_filter.is_base_unit is not None:
            stmt = stmt.where(Unit.is_base_unit == unit_filter.is_base_unit)
        
        if unit_filter.is_active is not None:
            stmt = stmt.where(Unit.is_active == unit_filter.is_active)
        
        if unit_filter.search:
            search_term = f"%{unit_filter.search}%"
            stmt = stmt.where(
                or_(
                    Unit.name.ilike(search_term),
                    Unit.symbol.ilike(search_term),
                    Unit.description.ilike(search_term)
                )
            )
        
        # Get total count
        count_result = await db.execute(select(func.count()).select_from(stmt.subquery()))
        total = count_result.scalar_one()
        
        # Apply pagination and ordering
        stmt = stmt.order_by(Unit.unit_type, Unit.name).offset((page-1)*per_page).limit(per_page)
        result = await db.execute(stmt)
        units = result.scalars().all()
        
        return UnitList(
            items=units,
            total=total,
            page=page,
            per_page=per_page,
            total_pages=(total + per_page - 1) // per_page
        )
        
    except Exception as e:
        logger.error(f"Error fetching units: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch units")


@router.post("/units", response_model=UnitResponse)
async def create_unit(
    unit_data: UnitCreate,
    auth: tuple = Depends(require_access("master_data", "create")),
    db: AsyncSession = Depends(get_db),
):
    """Create a new unit"""
    current_user, organization_id = auth
    try:
        # Check for duplicate name or symbol
        existing_result = await db.execute(select(Unit).filter_by(organization_id=organization_id).where(
            or_(Unit.name == unit_data.name, Unit.symbol == unit_data.symbol)
        ))
        existing = existing_result.scalars().first()
        
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Unit with name '{unit_data.name}' or symbol '{unit_data.symbol}' already exists"
            )
        
        # Validate base unit if specified
        if unit_data.base_unit_id:
            base_result = await db.execute(select(Unit).filter_by(
                id=unit_data.base_unit_id,
                organization_id=organization_id
            ))
            base_unit = base_result.scalars().first()
            
            if not base_unit:
                raise HTTPException(status_code=404, detail="Base unit not found")
            
            if base_unit.unit_type != unit_data.unit_type:
                raise HTTPException(
                    status_code=400,
                    detail="Base unit must be of the same type"
                )
        
        # Create unit
        unit = Unit(
            organization_id=organization_id,
            company_id=unit_data.company_id,
            name=unit_data.name,
            symbol=unit_data.symbol,
            unit_type=unit_data.unit_type,
            description=unit_data.description,
            is_base_unit=unit_data.is_base_unit,
            base_unit_id=unit_data.base_unit_id,
            conversion_factor=unit_data.conversion_factor,
            conversion_formula=unit_data.conversion_formula,
            decimal_places=unit_data.decimal_places,
            created_by=current_user.id
        )
        
        db.add(unit)
        await db.commit()
        await db.refresh(unit)
        
        logger.info(f"Unit created: {unit.name} (ID: {unit.id})")
        return unit
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating unit: {e}")
        raise HTTPException(status_code=500, detail="Failed to create unit")


@router.get("/units/{unit_id}", response_model=UnitResponse)
async def get_unit(
    unit_id: int,
    auth: tuple = Depends(require_access("master_data", "read")),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific unit"""
    current_user, organization_id = auth
    result = await db.execute(select(Unit).filter_by(
        id=unit_id,
        organization_id=organization_id
    ))
    unit = result.scalars().first()
    
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    
    return unit


@router.put("/units/{unit_id}", response_model=UnitResponse)
async def update_unit(
    unit_id: int,
    unit_data: UnitUpdate,
    auth: tuple = Depends(require_access("master_data", "update")),
    db: AsyncSession = Depends(get_db),
):
    """Update an existing unit"""
    current_user, organization_id = auth
    try:
        result = await db.execute(select(Unit).filter_by(
            id=unit_id,
            organization_id=organization_id
        ))
        unit = result.scalars().first()
        
        if not unit:
            raise HTTPException(status_code=404, detail="Unit not found")
        
        # Check for duplicate name (excluding current unit)
        if unit_data.name and unit_data.name != unit.name:
            existing_result = await db.execute(select(Unit).filter_by(
                organization_id=organization_id,
                name=unit_data.name
            ).filter(Unit.id != unit_id))
            existing = existing_result.scalars().first()
            
            if existing:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unit with name '{unit_data.name}' already exists"
                )
        
        # Update unit fields
        update_data = unit_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(unit, field, value)
        
        unit.updated_by = current_user.id
        
        await db.commit()
        await db.refresh(unit)
        
        logger.info(f"Unit updated: {unit.name} (ID: {unit.id})")
        return unit
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating unit: {e}")
        raise HTTPException(status_code=500, detail="Failed to update unit")


@router.delete("/units/{unit_id}")
async def delete_unit(
    unit_id: int,
    auth: tuple = Depends(require_access("master_data", "delete")),
    db: AsyncSession = Depends(get_db),
):
    """Delete a unit"""
    current_user, organization_id = auth
    try:
        result = await db.execute(select(Unit).filter_by(
            id=unit_id,
            organization_id=organization_id
        ))
        unit = result.scalars().first()
        
        if not unit:
            raise HTTPException(status_code=404, detail="Unit not found")
        
        # Check if unit is being used (implement business logic as needed)
        # For now, we'll allow deletion
        
        await db.delete(unit)
        await db.commit()
        
        logger.info(f"Unit deleted: {unit.name} (ID: {unit.id})")
        return {"message": "Unit deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting unit: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete unit")


@router.post("/units/convert", response_model=UnitConversion)
async def convert_units(
    conversion_data: UnitConversion,
    auth: tuple = Depends(require_access("master_data", "create")),
    db: AsyncSession = Depends(get_db),
):
    """Convert value between units"""
    current_user, organization_id = auth
    try:
        from_result = await db.execute(select(Unit).filter_by(
            id=conversion_data.from_unit_id,
            organization_id=organization_id
        ))
        from_unit = from_result.scalars().first()
        
        to_result = await db.execute(select(Unit).filter_by(
            id=conversion_data.to_unit_id,
            organization_id=organization_id
        ))
        to_unit = to_result.scalars().first()
        
        if not from_unit or not to_unit:
            raise HTTPException(status_code=404, detail="Unit not found")
        
        converted_value = await MasterDataService.convert_units(
            conversion_data.value, from_unit, to_unit, db
        )
        
        conversion_data.converted_value = converted_value
        return conversion_data
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error converting units: {e}")
        raise HTTPException(status_code=500, detail="Failed to convert units")


# ============================================================================
# TAX CODE ENDPOINTS
# ============================================================================

@router.get("/tax-codes", response_model=TaxCodeList)
async def get_tax_codes(
    page: int = Query(1, ge=1),
    per_page: int = Query(100, ge=1, le=1000),
    tax_filter: TaxCodeFilter = Depends(),
    auth: tuple = Depends(require_access("master_data", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get tax codes with filtering and pagination"""
    current_user, organization_id = auth
    try:
        stmt = select(TaxCode).filter_by(organization_id=organization_id)
        
        # Apply filters
        if tax_filter.tax_type:
            stmt = stmt.where(TaxCode.tax_type == tax_filter.tax_type)
        
        if tax_filter.is_active is not None:
            stmt = stmt.where(TaxCode.is_active == tax_filter.is_active)
        
        if tax_filter.hsn_sac_code:
            stmt = stmt.where(TaxCode.hsn_sac_codes.contains([tax_filter.hsn_sac_code]))
        
        if tax_filter.search:
            search_term = f"%{tax_filter.search}%"
            stmt = stmt.where(
                or_(
                    TaxCode.name.ilike(search_term),
                    TaxCode.code.ilike(search_term),
                    TaxCode.description.ilike(search_term)
                )
            )
        
        # Get total count
        count_result = await db.execute(select(func.count()).select_from(stmt.subquery()))
        total = count_result.scalar_one()
        
        # Apply pagination and ordering
        stmt = stmt.order_by(TaxCode.tax_type, TaxCode.tax_rate).offset((page-1)*per_page).limit(per_page)
        result = await db.execute(stmt)
        tax_codes = result.scalars().all()
        
        return TaxCodeList(
            items=tax_codes,
            total=total,
            page=page,
            per_page=per_page,
            total_pages=(total + per_page - 1) // per_page
        )
        
    except Exception as e:
        logger.error(f"Error fetching tax codes: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch tax codes")


@router.post("/tax-codes", response_model=TaxCodeResponse)
async def create_tax_code(
    tax_code_data: TaxCodeCreate,
    auth: tuple = Depends(require_access("master_data", "create")),
    db: AsyncSession = Depends(get_db),
):
    """Create a new tax code"""
    current_user, organization_id = auth
    try:
        # Check for duplicate code
        existing_result = await db.execute(select(TaxCode).filter_by(
            organization_id=organization_id,
            code=tax_code_data.code
        ))
        existing = existing_result.scalars().first()
        
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Tax code '{tax_code_data.code}' already exists"
            )
        
        # Create tax code
        tax_code = TaxCode(
            organization_id=organization_id,
            company_id=tax_code_data.company_id,
            name=tax_code_data.name,
            code=tax_code_data.code,
            tax_type=tax_code_data.tax_type,
            tax_rate=tax_code_data.tax_rate,
            is_compound=tax_code_data.is_compound,
            components=tax_code_data.components,
            tax_account_id=tax_code_data.tax_account_id,
            effective_from=tax_code_data.effective_from,
            effective_to=tax_code_data.effective_to,
            description=tax_code_data.description,
            hsn_sac_codes=tax_code_data.hsn_sac_codes,
            created_by=current_user.id
        )
        
        db.add(tax_code)
        await db.commit()
        await db.refresh(tax_code)
        
        logger.info(f"Tax code created: {tax_code.name} (ID: {tax_code.id})")
        return tax_code
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating tax code: {e}")
        raise HTTPException(status_code=500, detail="Failed to create tax code")


@router.get("/tax-codes/{tax_code_id}", response_model=TaxCodeResponse)
async def get_tax_code(
    tax_code_id: int,
    auth: tuple = Depends(require_access("master_data", "read")),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific tax code"""
    current_user, organization_id = auth
    result = await db.execute(select(TaxCode).filter_by(
        id=tax_code_id,
        organization_id=organization_id
    ))
    tax_code = result.scalars().first()
    
    if not tax_code:
        raise HTTPException(status_code=404, detail="Tax code not found")
    
    return tax_code


@router.put("/tax-codes/{tax_code_id}", response_model=TaxCodeResponse)
async def update_tax_code(
    tax_code_id: int,
    tax_code_data: TaxCodeUpdate,
    auth: tuple = Depends(require_access("master_data", "update")),
    db: AsyncSession = Depends(get_db),
):
    """Update an existing tax code"""
    current_user, organization_id = auth
    try:
        result = await db.execute(select(TaxCode).filter_by(
            id=tax_code_id,
            organization_id=organization_id
        ))
        tax_code = result.scalars().first()
        
        if not tax_code:
            raise HTTPException(status_code=404, detail="Tax code not found")
        
        # Check for duplicate name (excluding current tax code)
        if tax_code_data.name and tax_code_data.name != tax_code.name:
            existing_result = await db.execute(select(TaxCode).filter_by(
                organization_id=organization_id,
                name=tax_code_data.name
            ).filter(TaxCode.id != tax_code_id))
            existing = existing_result.scalars().first()
            
            if existing:
                raise HTTPException(
                    status_code=400,
                    detail=f"Tax code with name '{tax_code_data.name}' already exists"
                )
        
        # Update tax code fields
        update_data = tax_code_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(tax_code, field, value)
        
        tax_code.updated_by = current_user.id
        
        await db.commit()
        await db.refresh(tax_code)
        
        logger.info(f"Tax code updated: {tax_code.name} (ID: {tax_code.id})")
        return tax_code
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating tax code: {e}")
        raise HTTPException(status_code=500, detail="Failed to update tax code")


@router.delete("/tax-codes/{tax_code_id}")
async def delete_tax_code(
    tax_code_id: int,
    auth: tuple = Depends(require_access("master_data", "delete")),
    db: AsyncSession = Depends(get_db),
):
    """Delete a tax code"""
    current_user, organization_id = auth
    try:
        result = await db.execute(select(TaxCode).filter_by(
            id=tax_code_id,
            organization_id=organization_id
        ))
        tax_code = result.scalars().first()
        
        if not tax_code:
            raise HTTPException(status_code=404, detail="Tax code not found")
        
        # Check if tax code is being used (implement business logic as needed)
        # For now, we'll allow deletion
        
        await db.delete(tax_code)
        await db.commit()
        
        logger.info(f"Tax code deleted: {tax_code.name} (ID: {tax_code.id})")
        return {"message": "Tax code deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting tax code: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete tax code")


@router.post("/tax-codes/calculate", response_model=TaxCalculation)
async def calculate_tax(
    tax_calculation: TaxCalculation,
    auth: tuple = Depends(require_access("master_data", "create")),
    db: AsyncSession = Depends(get_db),
):
    """Calculate tax for a given amount"""
    current_user, organization_id = auth
    try:
        result = await db.execute(select(TaxCode).filter_by(
            id=tax_calculation.tax_code_id,
            organization_id=organization_id
        ))
        tax_code = result.scalars().first()
        
        if not tax_code:
            raise HTTPException(status_code=404, detail="Tax code not found")
        
        calculation_result = MasterDataService.calculate_tax(
            tax_calculation.amount, tax_code
        )
        
        tax_calculation.calculated_tax = calculation_result["tax_amount"]
        tax_calculation.tax_breakdown = calculation_result["breakdown"]
        
        return tax_calculation
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error calculating tax: {e}")
        raise HTTPException(status_code=500, detail="Failed to calculate tax")


# ============================================================================
# PAYMENT TERMS ENDPOINTS
# ============================================================================

@router.get("/payment-terms", response_model=PaymentTermsExtendedList)
async def get_payment_terms(
    page: int = Query(1, ge=1),
    per_page: int = Query(100, ge=1, le=1000),
    payment_terms_filter: PaymentTermsExtendedFilter = Depends(),
    auth: tuple = Depends(require_access("master_data", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get payment terms with filtering and pagination"""
    current_user, organization_id = auth
    try:
        stmt = select(PaymentTermsExtended).filter_by(organization_id=organization_id)
        
        # Apply filters
        if payment_terms_filter.is_default is not None:
            stmt = stmt.where(PaymentTermsExtended.is_default == payment_terms_filter.is_default)
        
        if payment_terms_filter.is_active is not None:
            stmt = stmt.where(PaymentTermsExtended.is_active == payment_terms_filter.is_active)
        
        if payment_terms_filter.search:
            search_term = f"%{payment_terms_filter.search}%"
            stmt = stmt.where(
                or_(
                    PaymentTermsExtended.name.ilike(search_term),
                    PaymentTermsExtended.code.ilike(search_term),
                    PaymentTermsExtended.description.ilike(search_term)
                )
            )
        
        # Get total count
        count_result = await db.execute(select(func.count()).select_from(stmt.subquery()))
        total = count_result.scalar_one()
        
        # Apply pagination and ordering
        stmt = stmt.order_by(PaymentTermsExtended.payment_days, PaymentTermsExtended.name).offset((page-1)*per_page).limit(per_page)
        result = await db.execute(stmt)
        payment_terms = result.scalars().all()
        
        return PaymentTermsExtendedList(
            items=payment_terms,
            total=total,
            page=page,
            per_page=per_page,
            total_pages=(total + per_page - 1) // per_page
        )
        
    except Exception as e:
        logger.error(f"Error fetching payment terms: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch payment terms")


@router.post("/payment-terms", response_model=PaymentTermsExtendedResponse)
async def create_payment_terms(
    payment_terms_data: PaymentTermsExtendedCreate,
    auth: tuple = Depends(require_access("master_data", "create")),
    db: AsyncSession = Depends(get_db),
):
    """Create new payment terms"""
    current_user, organization_id = auth
    try:
        # Check for duplicate name
        existing_result = await db.execute(select(PaymentTermsExtended).filter_by(
            organization_id=organization_id,
            name=payment_terms_data.name
        ))
        existing = existing_result.scalars().first()
        
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Payment terms '{payment_terms_data.name}' already exist"
            )
        
        # If this is set as default, unset other defaults
        if payment_terms_data.is_default:
            await db.execute(
                PaymentTermsExtended.__table__.update()
                .where(
                    PaymentTermsExtended.organization_id == organization_id,
                    PaymentTermsExtended.is_default == True
                )
                .values(is_default=False)
            )
        
        # Create payment terms
        payment_terms = PaymentTermsExtended(
            organization_id=organization_id,
            company_id=payment_terms_data.company_id,
            name=payment_terms_data.name,
            code=payment_terms_data.code,
            payment_days=payment_terms_data.payment_days,
            is_default=payment_terms_data.is_default,
            early_payment_discount_days=payment_terms_data.early_payment_discount_days,
            early_payment_discount_rate=payment_terms_data.early_payment_discount_rate,
            late_payment_penalty_days=payment_terms_data.late_payment_penalty_days,
            late_payment_penalty_rate=payment_terms_data.late_payment_penalty_rate,
            payment_schedule=payment_terms_data.payment_schedule,
            credit_limit_amount=payment_terms_data.credit_limit_amount,
            requires_approval=payment_terms_data.requires_approval,
            discount_account_id=payment_terms_data.discount_account_id,
            penalty_account_id=payment_terms_data.penalty_account_id,
            description=payment_terms_data.description,
            terms_conditions=payment_terms_data.terms_conditions,
            created_by=current_user.id
        )
        
        db.add(payment_terms)
        await db.commit()
        await db.refresh(payment_terms)
        
        logger.info(f"Payment terms created: {payment_terms.name} (ID: {payment_terms.id})")
        return payment_terms
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating payment terms: {e}")
        raise HTTPException(status_code=500, detail="Failed to create payment terms")


@router.get("/payment-terms/{payment_terms_id}", response_model=PaymentTermsExtendedResponse)
async def get_payment_terms_by_id(
    payment_terms_id: int,
    auth: tuple = Depends(require_access("master_data", "read")),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific payment terms"""
    current_user, organization_id = auth
    result = await db.execute(select(PaymentTermsExtended).filter_by(
        id=payment_terms_id,
        organization_id=organization_id
    ))
    payment_terms = result.scalars().first()
    
    if not payment_terms:
        raise HTTPException(status_code=404, detail="Payment terms not found")
    
    return payment_terms


@router.put("/payment-terms/{payment_terms_id}", response_model=PaymentTermsExtendedResponse)
async def update_payment_terms(
    payment_terms_id: int,
    payment_terms_data: PaymentTermsExtendedUpdate,
    auth: tuple = Depends(require_access("master_data", "update")),
    db: AsyncSession = Depends(get_db),
):
    """Update an existing payment terms"""
    current_user, organization_id = auth
    try:
        result = await db.execute(select(PaymentTermsExtended).filter_by(
            id=payment_terms_id,
            organization_id=organization_id
        ))
        payment_terms = result.scalars().first()
        
        if not payment_terms:
            raise HTTPException(status_code=404, detail="Payment terms not found")
        
        # Check for duplicate name (excluding current payment terms)
        if payment_terms_data.name and payment_terms_data.name != payment_terms.name:
            existing_result = await db.execute(select(PaymentTermsExtended).filter_by(
                organization_id=organization_id,
                name=payment_terms_data.name
            ).filter(PaymentTermsExtended.id != payment_terms_id))
            existing = existing_result.scalars().first()
            
            if existing:
                raise HTTPException(
                    status_code=400,
                    detail=f"Payment terms with name '{payment_terms_data.name}' already exists"
                )
        
        # Update payment terms fields
        update_data = payment_terms_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(payment_terms, field, value)
        
        payment_terms.updated_by = current_user.id
        
        await db.commit()
        await db.refresh(payment_terms)
        
        logger.info(f"Payment terms updated: {payment_terms.name} (ID: {payment_terms.id})")
        return payment_terms
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating payment terms: {e}")
        raise HTTPException(status_code=500, detail="Failed to update payment terms")


@router.delete("/payment-terms/{payment_terms_id}")
async def delete_payment_terms(
    payment_terms_id: int,
    auth: tuple = Depends(require_access("master_data", "delete")),
    db: AsyncSession = Depends(get_db),
):
    """Delete a payment terms"""
    current_user, organization_id = auth
    try:
        result = await db.execute(select(PaymentTermsExtended).filter_by(
            id=payment_terms_id,
            organization_id=organization_id
        ))
        payment_terms = result.scalars().first()
        
        if not payment_terms:
            raise HTTPException(status_code=404, detail="Payment terms not found")
        
        # Check if payment terms is being used (implement business logic as needed)
        # For now, we'll allow deletion
        
        await db.delete(payment_terms)
        await db.commit()
        
        logger.info(f"Payment terms deleted: {payment_terms.name} (ID: {payment_terms.id})")
        return {"message": "Payment terms deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting payment terms: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete payment terms")


# ============================================================================
# BULK OPERATIONS
# ============================================================================

@router.post("/categories/bulk-update")
async def bulk_update_categories(
    bulk_update: BulkCategoryUpdate,
    auth: tuple = Depends(require_access("master_data", "create")),
    db: AsyncSession = Depends(get_db),
):
    """Bulk update categories"""
    current_user, organization_id = auth
    try:
        update_fields = bulk_update.updates.dict(exclude_unset=True)
        if not update_fields:
            raise HTTPException(status_code=400, detail="No update fields provided")
        
        # Update categories
        await db.execute(
            Category.__table__.update()
            .where(
                Category.id.in_(bulk_update.category_ids),
                Category.organization_id == organization_id
            )
            .values(update_fields)
        )
        
        await db.commit()
        
        logger.info(f"Bulk updated categories")
        return {"message": "Updated categories", "updated_count": len(bulk_update.category_ids)}
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error in bulk category update: {e}")
        raise HTTPException(status_code=500, detail="Failed to bulk update categories")

# ============================================================================
# HSN SEARCH ENDPOINTS
# ============================================================================

@router.get("/hsn-search", response_model=List[Dict[str, Any]])
async def hsn_search(
    query: str = Query(..., min_length=2, description="HSN code or description to search (min 2 chars)"),
    limit: int = Query(10, ge=1, le=50, description="Max results to return"),
    auth: tuple = Depends(require_access("master_data", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Search HSN codes with dynamic GST rates from external API"""
    current_user, organization_id = auth
    try:
        results = await search_hsn_codes(query, limit)
        return results
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error in HSN search: {e}")
        raise HTTPException(status_code=500, detail="Failed to search HSN codes")