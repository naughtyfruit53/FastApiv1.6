# app/api/v1/master_data.py

"""
Master Data API endpoints for Categories, Units, Payment Terms, and Tax Codes
These endpoints provide complete CRUD operations for master data management
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status, BackgroundTasks
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func, desc, asc, text
from typing import List, Optional, Dict, Any
from datetime import datetime
from decimal import Decimal
import logging

from app.core.database import get_db
from app.api.v1.auth import get_current_active_user
from app.core.tenant import validate_company_setup_for_operations
from app.core.org_restrictions import require_current_organization_id
from app.services.rbac import require_permission, RBACService
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
    def calculate_category_path(category: Category, db: Session) -> str:
        """Calculate materialized path for category hierarchy"""
        if category.parent_category_id is None:
            return f"/{category.id}/"
        
        parent = db.query(Category).filter(Category.id == category.parent_category_id).first()
        if parent:
            parent_path = parent.path or MasterDataService.calculate_category_path(parent, db)
            return f"{parent_path}{category.id}/"
        
        return f"/{category.id}/"
    
    @staticmethod
    def convert_units(value: Decimal, from_unit: Unit, to_unit: Unit, db: Session) -> Decimal:
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
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    organization_id: int = Depends(require_current_organization_id)
):
    """Get master data dashboard statistics"""
    try:
        # Base queries with organization filter
        category_query = db.query(Category).filter(Category.organization_id == organization_id)
        unit_query = db.query(Unit).filter(Unit.organization_id == organization_id)
        tax_code_query = db.query(TaxCode).filter(TaxCode.organization_id == organization_id)
        payment_terms_query = db.query(PaymentTermsExtended).filter(PaymentTermsExtended.organization_id == organization_id)
        
        # Apply company filter if specified
        if company_id:
            category_query = category_query.filter(or_(Category.company_id == company_id, Category.company_id.is_(None)))
            unit_query = unit_query.filter(or_(Unit.company_id == company_id, Unit.company_id.is_(None)))
            tax_code_query = tax_code_query.filter(or_(TaxCode.company_id == company_id, TaxCode.company_id.is_(None)))
            payment_terms_query = payment_terms_query.filter(or_(PaymentTermsExtended.company_id == company_id, PaymentTermsExtended.company_id.is_(None)))
        
        # Calculate statistics
        stats = MasterDataStats(
            total_categories=category_query.count(),
            active_categories=category_query.filter(Category.is_active == True).count(),
            total_units=unit_query.count(),
            active_units=unit_query.filter(Unit.is_active == True).count(),
            total_tax_codes=tax_code_query.count(),
            active_tax_codes=tax_code_query.filter(TaxCode.is_active == True).count(),
            total_payment_terms=payment_terms_query.count(),
            active_payment_terms=payment_terms_query.filter(PaymentTermsExtended.is_active == True).count()
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
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    organization_id: int = Depends(require_current_organization_id)
):
    """Get categories with filtering and pagination"""
    try:
        query = db.query(Category).filter(Category.organization_id == organization_id)
        
        # Apply filters
        if category_filter.category_type:
            query = query.filter(Category.category_type == category_filter.category_type)
        
        if category_filter.parent_category_id is not None:
            query = query.filter(Category.parent_category_id == category_filter.parent_category_id)
        
        if category_filter.is_active is not None:
            query = query.filter(Category.is_active == category_filter.is_active)
        
        if category_filter.search:
            search_term = f"%{category_filter.search}%"
            query = query.filter(
                or_(
                    Category.name.ilike(search_term),
                    Category.code.ilike(search_term),
                    Category.description.ilike(search_term)
                )
            )
        
        # Get total count
        total = query.count()
        
        # Apply pagination and ordering
        categories = query.order_by(Category.sort_order, Category.name).offset((page-1)*per_page).limit(per_page).all()
        
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
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    organization_id: int = Depends(require_current_organization_id)
):
    """Create a new category"""
    try:
        # Check for duplicate name
        existing = db.query(Category).filter(
            Category.organization_id == organization_id,
            Category.name == category_data.name,
            Category.category_type == category_data.category_type
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Category with name '{category_data.name}' already exists for type '{category_data.category_type}'"
            )
        
        # Validate parent category if specified
        level = 0
        if category_data.parent_category_id:
            parent = db.query(Category).filter(
                Category.id == category_data.parent_category_id,
                Category.organization_id == organization_id
            ).first()
            
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
        db.commit()
        db.refresh(category)
        
        # Calculate and update path
        category.path = MasterDataService.calculate_category_path(category, db)
        db.commit()
        db.refresh(category)
        
        logger.info(f"Category created: {category.name} (ID: {category.id})")
        return category
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating category: {e}")
        raise HTTPException(status_code=500, detail="Failed to create category")


@router.get("/categories/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    organization_id: int = Depends(require_current_organization_id)
):
    """Get a specific category"""
    category = db.query(Category).filter(
        Category.id == category_id,
        Category.organization_id == organization_id
    ).first()
    
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    return category


@router.put("/categories/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    organization_id: int = Depends(require_current_organization_id)
):
    """Update a category"""
    try:
        category = db.query(Category).filter(
            Category.id == category_id,
            Category.organization_id == organization_id
        ).first()
        
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        
        # Check for duplicate name if being updated
        if category_data.name and category_data.name != category.name:
            existing = db.query(Category).filter(
                Category.organization_id == organization_id,
                Category.name == category_data.name,
                Category.category_type == category_data.category_type or category.category_type,
                Category.id != category_id
            ).first()
            
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
        
        db.commit()
        db.refresh(category)
        
        logger.info(f"Category updated: {category.name} (ID: {category.id})")
        return category
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating category: {e}")
        raise HTTPException(status_code=500, detail="Failed to update category")


@router.delete("/categories/{category_id}")
async def delete_category(
    category_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    organization_id: int = Depends(require_current_organization_id)
):
    """Delete a category"""
    try:
        category = db.query(Category).filter(
            Category.id == category_id,
            Category.organization_id == organization_id
        ).first()
        
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        
        # Check for subcategories
        subcategories = db.query(Category).filter(Category.parent_category_id == category_id).count()
        if subcategories > 0:
            raise HTTPException(
                status_code=400,
                detail="Cannot delete category with subcategories"
            )
        
        db.delete(category)
        db.commit()
        
        logger.info(f"Category deleted: {category.name} (ID: {category.id})")
        return {"message": "Category deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
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
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    organization_id: int = Depends(require_current_organization_id)
):
    """Get units with filtering and pagination"""
    try:
        query = db.query(Unit).filter(Unit.organization_id == organization_id)
        
        # Apply filters
        if unit_filter.unit_type:
            query = query.filter(Unit.unit_type == unit_filter.unit_type)
        
        if unit_filter.is_base_unit is not None:
            query = query.filter(Unit.is_base_unit == unit_filter.is_base_unit)
        
        if unit_filter.is_active is not None:
            query = query.filter(Unit.is_active == unit_filter.is_active)
        
        if unit_filter.search:
            search_term = f"%{unit_filter.search}%"
            query = query.filter(
                or_(
                    Unit.name.ilike(search_term),
                    Unit.symbol.ilike(search_term),
                    Unit.description.ilike(search_term)
                )
            )
        
        # Get total count
        total = query.count()
        
        # Apply pagination and ordering
        units = query.order_by(Unit.unit_type, Unit.name).offset((page-1)*per_page).limit(per_page).all()
        
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
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    organization_id: int = Depends(require_current_organization_id)
):
    """Create a new unit"""
    try:
        # Check for duplicate name or symbol
        existing = db.query(Unit).filter(
            Unit.organization_id == organization_id,
            or_(
                Unit.name == unit_data.name,
                Unit.symbol == unit_data.symbol
            )
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Unit with name '{unit_data.name}' or symbol '{unit_data.symbol}' already exists"
            )
        
        # Validate base unit if specified
        if unit_data.base_unit_id:
            base_unit = db.query(Unit).filter(
                Unit.id == unit_data.base_unit_id,
                Unit.organization_id == organization_id
            ).first()
            
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
        db.commit()
        db.refresh(unit)
        
        logger.info(f"Unit created: {unit.name} (ID: {unit.id})")
        return unit
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating unit: {e}")
        raise HTTPException(status_code=500, detail="Failed to create unit")


@router.post("/units/convert", response_model=UnitConversion)
async def convert_units(
    conversion_data: UnitConversion,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    organization_id: int = Depends(require_current_organization_id)
):
    """Convert value between units"""
    try:
        from_unit = db.query(Unit).filter(
            Unit.id == conversion_data.from_unit_id,
            Unit.organization_id == organization_id
        ).first()
        
        to_unit = db.query(Unit).filter(
            Unit.id == conversion_data.to_unit_id,
            Unit.organization_id == organization_id
        ).first()
        
        if not from_unit or not to_unit:
            raise HTTPException(status_code=404, detail="Unit not found")
        
        converted_value = MasterDataService.convert_units(
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
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    organization_id: int = Depends(require_current_organization_id)
):
    """Get tax codes with filtering and pagination"""
    try:
        query = db.query(TaxCode).filter(TaxCode.organization_id == organization_id)
        
        # Apply filters
        if tax_filter.tax_type:
            query = query.filter(TaxCode.tax_type == tax_filter.tax_type)
        
        if tax_filter.is_active is not None:
            query = query.filter(TaxCode.is_active == tax_filter.is_active)
        
        if tax_filter.hsn_sac_code:
            query = query.filter(TaxCode.hsn_sac_codes.contains([tax_filter.hsn_sac_code]))
        
        if tax_filter.search:
            search_term = f"%{tax_filter.search}%"
            query = query.filter(
                or_(
                    TaxCode.name.ilike(search_term),
                    TaxCode.code.ilike(search_term),
                    TaxCode.description.ilike(search_term)
                )
            )
        
        # Get total count
        total = query.count()
        
        # Apply pagination and ordering
        tax_codes = query.order_by(TaxCode.tax_type, TaxCode.tax_rate).offset((page-1)*per_page).limit(per_page).all()
        
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
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    organization_id: int = Depends(require_current_organization_id)
):
    """Create a new tax code"""
    try:
        # Check for duplicate code
        existing = db.query(TaxCode).filter(
            TaxCode.organization_id == organization_id,
            TaxCode.code == tax_code_data.code
        ).first()
        
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
        db.commit()
        db.refresh(tax_code)
        
        logger.info(f"Tax code created: {tax_code.name} (ID: {tax_code.id})")
        return tax_code
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating tax code: {e}")
        raise HTTPException(status_code=500, detail="Failed to create tax code")


@router.post("/tax-codes/calculate", response_model=TaxCalculation)
async def calculate_tax(
    tax_calculation: TaxCalculation,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    organization_id: int = Depends(require_current_organization_id)
):
    """Calculate tax for a given amount"""
    try:
        tax_code = db.query(TaxCode).filter(
            TaxCode.id == tax_calculation.tax_code_id,
            TaxCode.organization_id == organization_id
        ).first()
        
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
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    organization_id: int = Depends(require_current_organization_id)
):
    """Get payment terms with filtering and pagination"""
    try:
        query = db.query(PaymentTermsExtended).filter(PaymentTermsExtended.organization_id == organization_id)
        
        # Apply filters
        if payment_terms_filter.is_default is not None:
            query = query.filter(PaymentTermsExtended.is_default == payment_terms_filter.is_default)
        
        if payment_terms_filter.is_active is not None:
            query = query.filter(PaymentTermsExtended.is_active == payment_terms_filter.is_active)
        
        if payment_terms_filter.search:
            search_term = f"%{payment_terms_filter.search}%"
            query = query.filter(
                or_(
                    PaymentTermsExtended.name.ilike(search_term),
                    PaymentTermsExtended.code.ilike(search_term),
                    PaymentTermsExtended.description.ilike(search_term)
                )
            )
        
        # Get total count
        total = query.count()
        
        # Apply pagination and ordering
        payment_terms = query.order_by(PaymentTermsExtended.payment_days, PaymentTermsExtended.name).offset((page-1)*per_page).limit(per_page).all()
        
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
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    organization_id: int = Depends(require_current_organization_id)
):
    """Create new payment terms"""
    try:
        # Check for duplicate name
        existing = db.query(PaymentTermsExtended).filter(
            PaymentTermsExtended.organization_id == organization_id,
            PaymentTermsExtended.name == payment_terms_data.name
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Payment terms '{payment_terms_data.name}' already exist"
            )
        
        # If this is set as default, unset other defaults
        if payment_terms_data.is_default:
            db.query(PaymentTermsExtended).filter(
                PaymentTermsExtended.organization_id == organization_id,
                PaymentTermsExtended.is_default == True
            ).update({"is_default": False})
        
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
        db.commit()
        db.refresh(payment_terms)
        
        logger.info(f"Payment terms created: {payment_terms.name} (ID: {payment_terms.id})")
        return payment_terms
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating payment terms: {e}")
        raise HTTPException(status_code=500, detail="Failed to create payment terms")


# ============================================================================
# BULK OPERATIONS
# ============================================================================

@router.post("/categories/bulk-update")
async def bulk_update_categories(
    bulk_update: BulkCategoryUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    organization_id: int = Depends(require_current_organization_id)
):
    """Bulk update categories"""
    try:
        update_fields = bulk_update.updates.dict(exclude_unset=True)
        if not update_fields:
            raise HTTPException(status_code=400, detail="No update fields provided")
        
        # Update categories
        result = db.query(Category).filter(
            Category.id.in_(bulk_update.category_ids),
            Category.organization_id == organization_id
        ).update(update_fields, synchronize_session=False)
        
        db.commit()
        
        logger.info(f"Bulk updated {result} categories")
        return {"message": f"Updated {result} categories", "updated_count": result}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error in bulk category update: {e}")
        raise HTTPException(status_code=500, detail="Failed to bulk update categories")