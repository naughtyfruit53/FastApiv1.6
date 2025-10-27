# app/api/v1/accounts.py
"""
Account Management API endpoints
Accounts are companies/organizations in CRM
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, desc
from typing import List, Optional
from datetime import datetime
import logging

from app.core.database import get_db
from app.core.tenant import require_current_organization_id
from app.models.customer_models import Customer
from app.models.user_models import User
from app.core.security import get_current_user as core_get_current_user
from app.services.rbac import RBACService
from pydantic import BaseModel, EmailStr, Field

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/accounts", tags=["Accounts"])


# Pydantic schemas for Account (using Customer model)
class AccountBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    type: str = Field(default="customer", max_length=50)  # customer, prospect, partner, vendor
    industry: Optional[str] = Field(None, max_length=100)
    size: Optional[str] = Field(None, max_length=50)  # small, medium, large, enterprise
    revenue: Optional[float] = Field(None, ge=0)
    employees: Optional[int] = Field(None, ge=0)
    website: Optional[str] = Field(None, max_length=200)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    address1: Optional[str] = None
    address2: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    pin_code: Optional[str] = Field(None, max_length=20)
    country: Optional[str] = Field(None, max_length=100)
    status: str = Field(default="active", max_length=50)
    source: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    contact_person: Optional[str] = Field(None, max_length=100)
    contact_number: Optional[str] = Field(None, max_length=20)


class AccountCreate(AccountBase):
    pass


class AccountUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    type: Optional[str] = Field(None, max_length=50)
    industry: Optional[str] = Field(None, max_length=100)
    size: Optional[str] = Field(None, max_length=50)
    revenue: Optional[float] = Field(None, ge=0)
    employees: Optional[int] = Field(None, ge=0)
    website: Optional[str] = Field(None, max_length=200)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    address1: Optional[str] = None
    address2: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    pin_code: Optional[str] = Field(None, max_length=20)
    country: Optional[str] = Field(None, max_length=100)
    status: Optional[str] = Field(None, max_length=50)
    source: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    contact_person: Optional[str] = Field(None, max_length=100)
    contact_number: Optional[str] = Field(None, max_length=20)


class AccountResponse(AccountBase):
    id: int
    organization_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_active: bool
    
    class Config:
        from_attributes = True


@router.get("", response_model=List[AccountResponse])
async def get_accounts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(core_get_current_user),
    org_id: int = Depends(require_current_organization_id)
):
    """Get all accounts with filtering and pagination"""
    try:
        stmt = select(Customer).where(Customer.organization_id == org_id)
        
        # Apply filters
        if status:
            is_active = status.lower() == "active"
            stmt = stmt.where(Customer.is_active == is_active)
        if search:
            search_term = f"%{search}%"
            stmt = stmt.where(
                or_(
                    Customer.name.ilike(search_term),
                    Customer.email.ilike(search_term),
                    Customer.contact_person.ilike(search_term)
                )
            )
        
        # Order by created date descending
        stmt = stmt.order_by(desc(Customer.created_at))
        
        # Apply pagination
        stmt = stmt.offset(skip).limit(limit)
        
        result = await db.execute(stmt)
        accounts = result.scalars().all()
        
        # Enrich with type, industry, etc. from metadata if stored
        for account in accounts:
            # Set defaults if not present
            if not hasattr(account, 'type'):
                account.type = 'customer'
            if not hasattr(account, 'status'):
                account.status = 'active' if account.is_active else 'inactive'
        
        logger.info(f"Fetched {len(accounts)} accounts for org_id={org_id}")
        return accounts

    except Exception as e:
        logger.error(f"Error fetching accounts for org_id={org_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch accounts: {str(e)}"
        )


@router.post("", response_model=AccountResponse)
async def create_account(
    account_data: AccountCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(core_get_current_user),
    org_id: int = Depends(require_current_organization_id)
):
    """Create a new account"""
    try:
        # Create account using Customer model
        account_dict = account_data.model_dump()
        
        # Map account fields to customer fields
        customer_data = {
            "organization_id": org_id,
            "name": account_dict.get("name"),
            "email": account_dict.get("email", ""),
            "contact_person": account_dict.get("contact_person", ""),
            "contact_number": account_dict.get("contact_number", account_dict.get("phone", "")),
            "address1": account_dict.get("address1", ""),
            "address2": account_dict.get("address2", ""),
            "city": account_dict.get("city", ""),
            "state": account_dict.get("state", ""),
            "pin_code": account_dict.get("pin_code", ""),
            "is_active": account_dict.get("status", "active") == "active"
        }
        
        account = Customer(**customer_data)
        
        db.add(account)
        await db.commit()
        await db.refresh(account)
        
        # Enrich response
        account.type = account_dict.get("type", "customer")
        account.industry = account_dict.get("industry")
        account.size = account_dict.get("size")
        account.revenue = account_dict.get("revenue")
        account.employees = account_dict.get("employees")
        account.website = account_dict.get("website")
        account.phone = account_dict.get("phone")
        account.status = account_dict.get("status", "active")
        account.source = account_dict.get("source")
        account.description = account_dict.get("description")
        
        logger.info(f"Account {account.name} created by {current_user.email} in org {org_id}")
        return account

    except Exception as e:
        logger.error(f"Error creating account for org_id={org_id}: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create account: {str(e)}"
        )


@router.get("/{account_id}", response_model=AccountResponse)
async def get_account(
    account_id: int = Path(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(core_get_current_user),
    org_id: int = Depends(require_current_organization_id)
):
    """Get a specific account"""
    try:
        stmt = select(Customer).where(
            and_(Customer.id == account_id, Customer.organization_id == org_id)
        )
        result = await db.execute(stmt)
        account = result.scalar_one_or_none()
        
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        # Enrich response
        account.type = 'customer'
        account.status = 'active' if account.is_active else 'inactive'
        
        logger.info(f"Fetched account {account_id} for org_id={org_id}")
        return account

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching account {account_id} for org_id={org_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch account: {str(e)}"
        )


@router.put("/{account_id}", response_model=AccountResponse)
async def update_account(
    account_data: AccountUpdate,
    account_id: int = Path(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(core_get_current_user),
    org_id: int = Depends(require_current_organization_id)
):
    """Update an account"""
    try:
        stmt = select(Customer).where(
            and_(Customer.id == account_id, Customer.organization_id == org_id)
        )
        result = await db.execute(stmt)
        account = result.scalar_one_or_none()
        
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        # Update fields
        update_dict = account_data.model_dump(exclude_unset=True)
        
        # Map account fields to customer fields
        if "name" in update_dict:
            account.name = update_dict["name"]
        if "email" in update_dict:
            account.email = update_dict["email"]
        if "contact_person" in update_dict:
            account.contact_person = update_dict["contact_person"]
        if "contact_number" in update_dict or "phone" in update_dict:
            account.contact_number = update_dict.get("contact_number", update_dict.get("phone", ""))
        if "address1" in update_dict:
            account.address1 = update_dict["address1"]
        if "address2" in update_dict:
            account.address2 = update_dict["address2"]
        if "city" in update_dict:
            account.city = update_dict["city"]
        if "state" in update_dict:
            account.state = update_dict["state"]
        if "pin_code" in update_dict:
            account.pin_code = update_dict["pin_code"]
        if "status" in update_dict:
            account.is_active = update_dict["status"] == "active"
        
        account.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(account)
        
        # Enrich response
        account.type = update_dict.get("type", "customer")
        account.industry = update_dict.get("industry")
        account.size = update_dict.get("size")
        account.revenue = update_dict.get("revenue")
        account.employees = update_dict.get("employees")
        account.website = update_dict.get("website")
        account.phone = update_dict.get("phone", account.contact_number)
        account.status = update_dict.get("status", "active" if account.is_active else "inactive")
        account.source = update_dict.get("source")
        account.description = update_dict.get("description")
        
        logger.info(f"Account {account_id} updated by {current_user.email} in org {org_id}")
        return account

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating account {account_id} for org_id={org_id}: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update account: {str(e)}"
        )


@router.delete("/{account_id}")
async def delete_account(
    account_id: int = Path(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(core_get_current_user),
    org_id: int = Depends(require_current_organization_id)
):
    """Delete an account"""
    try:
        stmt = select(Customer).where(
            and_(Customer.id == account_id, Customer.organization_id == org_id)
        )
        result = await db.execute(stmt)
        account = result.scalar_one_or_none()
        
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        await db.delete(account)
        await db.commit()
        
        logger.info(f"Account {account_id} deleted by {current_user.email} in org {org_id}")
        return {"message": "Account deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting account {account_id} for org_id={org_id}: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete account: {str(e)}"
        )
