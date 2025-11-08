# app/api/v1/contacts.py
"""
Contact Management API endpoints
Contacts are individuals associated with accounts/companies in CRM
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, desc
from typing import List, Optional
from datetime import datetime
import logging

from app.core.database import get_db
from app.core.enforcement import require_access
from app.models.crm_models import Lead
from app.models.user_models import User
from pydantic import BaseModel, EmailStr, Field

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/contacts", tags=["Contacts"])


# Pydantic schemas for Contact (using Lead model as base)
class ContactBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    mobile: Optional[str] = Field(None, max_length=20)
    job_title: Optional[str] = Field(None, max_length=100)
    department: Optional[str] = Field(None, max_length=100)
    company: Optional[str] = Field(None, max_length=200)
    address1: Optional[str] = None
    address2: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    pin_code: Optional[str] = Field(None, max_length=20)
    country: Optional[str] = Field(None, max_length=100)
    source: str = Field(default="manual", max_length=50)
    status: str = Field(default="active", max_length=50)
    notes: Optional[str] = None
    tags: Optional[List[str]] = Field(default_factory=list)


class ContactCreate(ContactBase):
    pass


class ContactUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    mobile: Optional[str] = Field(None, max_length=20)
    job_title: Optional[str] = Field(None, max_length=100)
    department: Optional[str] = Field(None, max_length=100)
    company: Optional[str] = Field(None, max_length=200)
    address1: Optional[str] = None
    address2: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    pin_code: Optional[str] = Field(None, max_length=20)
    country: Optional[str] = Field(None, max_length=100)
    source: Optional[str] = Field(None, max_length=50)
    status: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = None
    tags: Optional[List[str]] = None


class ContactResponse(ContactBase):
    id: int
    organization_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_contacted: Optional[datetime] = None
    
    class Config:
        from_attributes = True


@router.get("", response_model=List[ContactResponse])
async def get_contacts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    auth: tuple = Depends(require_access("contact", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get all contacts with filtering and pagination"""
    current_user, org_id = auth
    
    try:
        stmt = select(Lead).where(
            and_(
                Lead.organization_id == org_id,
                Lead.status != "converted"  # Exclude converted leads
            )
        )
        
        # Apply filters
        if status:
            stmt = stmt.where(Lead.status == status)
        if search:
            search_term = f"%{search}%"
            stmt = stmt.where(
                or_(
                    Lead.first_name.ilike(search_term),
                    Lead.last_name.ilike(search_term),
                    Lead.email.ilike(search_term),
                    Lead.company.ilike(search_term)
                )
            )
        
        # Order by created date descending
        stmt = stmt.order_by(desc(Lead.created_at))
        
        # Apply pagination
        stmt = stmt.offset(skip).limit(limit)
        
        result = await db.execute(stmt)
        contacts = result.scalars().all()
        
        logger.info(f"Fetched {len(contacts)} contacts for org_id={org_id}")
        return contacts

    except Exception as e:
        logger.error(f"Error fetching contacts for org_id={org_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch contacts: {str(e)}"
        )


@router.post("", response_model=ContactResponse)
async def create_contact(
    contact_data: ContactCreate,
    auth: tuple = Depends(require_access("contact", "create")),
    db: AsyncSession = Depends(get_db)
):
    """Create a new contact"""
    current_user, org_id = auth
    
    try:
        # Create contact using Lead model
        import secrets
        import string
        
        # Generate unique contact number
        random_suffix = ''.join(secrets.choice(string.digits) for _ in range(6))
        contact_number = f"CT{random_suffix}"
        
        contact = Lead(
            organization_id=org_id,
            lead_number=contact_number,
            created_by_id=current_user.id,
            **contact_data.model_dump()
        )
        
        db.add(contact)
        await db.commit()
        await db.refresh(contact)
        
        logger.info(f"Contact {contact_number} created by {current_user.email} in org {org_id}")
        return contact

    except Exception as e:
        logger.error(f"Error creating contact for org_id={org_id}: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create contact: {str(e)}"
        )


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(
    contact_id: int = Path(...),
    auth: tuple = Depends(require_access("contact", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific contact"""
    current_user, org_id = auth
    
    try:
        stmt = select(Lead).where(
            and_(Lead.id == contact_id, Lead.organization_id == org_id)
        )
        result = await db.execute(stmt)
        contact = result.scalar_one_or_none()
        
        if not contact:
            raise HTTPException(status_code=404, detail="Contact not found")
        
        logger.info(f"Fetched contact {contact_id} for org_id={org_id}")
        return contact

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching contact {contact_id} for org_id={org_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch contact: {str(e)}"
        )


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_data: ContactUpdate,
    contact_id: int = Path(...),
    auth: tuple = Depends(require_access("contact", "update")),
    db: AsyncSession = Depends(get_db)
):
    """Update a contact"""
    current_user, org_id = auth
    
    try:
        stmt = select(Lead).where(
            and_(Lead.id == contact_id, Lead.organization_id == org_id)
        )
        result = await db.execute(stmt)
        contact = result.scalar_one_or_none()
        
        if not contact:
            raise HTTPException(status_code=404, detail="Contact not found")
        
        # Update fields
        update_data = contact_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(contact, field, value)
        
        contact.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(contact)
        
        logger.info(f"Contact {contact_id} updated by {current_user.email} in org {org_id}")
        return contact

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating contact {contact_id} for org_id={org_id}: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update contact: {str(e)}"
        )


@router.delete("/{contact_id}")
async def delete_contact(
    contact_id: int = Path(...),
    auth: tuple = Depends(require_access("contact", "delete")),
    db: AsyncSession = Depends(get_db)
):
    """Delete a contact"""
    current_user, org_id = auth
    
    try:
        stmt = select(Lead).where(
            and_(Lead.id == contact_id, Lead.organization_id == org_id)
        )
        result = await db.execute(stmt)
        contact = result.scalar_one_or_none()
        
        if not contact:
            raise HTTPException(status_code=404, detail="Contact not found")
        
        await db.delete(contact)
        await db.commit()
        
        logger.info(f"Contact {contact_id} deleted by {current_user.email} in org {org_id}")
        return {"message": "Contact deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting contact {contact_id} for org_id={org_id}: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete contact: {str(e)}"
        )
