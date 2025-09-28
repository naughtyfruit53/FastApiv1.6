# app/api/v1/organizations/services.py

"""
Organization services - Business logic for organization management
"""
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func
from sqlalchemy import select
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
import secrets
import string
import re

from app.models import Organization, User, Product, Customer, Vendor, Stock, ServiceRole
from app.schemas.user import UserRole
from app.schemas import (
    OrganizationCreate, OrganizationUpdate, OrganizationInDB,
    OrganizationLicenseCreate, OrganizationLicenseResponse,
    UserCreate, UserInDB
)
from app.core.security import get_password_hash
from app.core.logging import log_license_creation, log_email_operation
from app.services.rbac import RBACService
from app.utils.supabase_auth import supabase_auth_service, SupabaseAuthError
from app.services.email_service import email_service

logger = logging.getLogger(__name__)

email_service = None
EMAIL_SERVICE_AVAILABLE = False

def _initialize_email_service():
    """Initialize email service if available."""
    global email_service, EMAIL_SERVICE_AVAILABLE
    try:
        from app.services.email_service import email_service as _email_service
        email_service = _email_service
        EMAIL_SERVICE_AVAILABLE = True
        logger.info("Email service initialized successfully")
    except ImportError as e:
        EMAIL_SERVICE_AVAILABLE = False
        email_service = None
        logger.warning(f"Email service not available: {e}")

_initialize_email_service()

def generate_subdomain(name: str) -> str:
    """Generate a clean subdomain from organization name"""
    subdomain = re.sub(r'[^a-z0-9-]', '', name.lower().replace(' ', '-'))
    subdomain = re.sub(r'-+', '-', subdomain)
    subdomain = subdomain.strip('-')
    subdomain = subdomain[:50]
    if len(subdomain) < 3:
        subdomain = f"{subdomain}-{secrets.choice(string.ascii_lowercase + string.digits) * (3 - len(subdomain))}"
    return subdomain

class OrganizationService:
    """Business logic for organization management"""
    
    @staticmethod
    async def get_app_statistics(db: AsyncSession) -> Dict:
        """Get application-level statistics"""
        result = await db.execute(select(func.count(Organization.id)))
        total_licenses = result.scalar_one()
        
        result = await db.execute(select(func.count(Organization.id)).where(Organization.status == "active"))
        active_organizations = result.scalar_one()
        
        result = await db.execute(select(func.count(Organization.id)).where(Organization.status == "trial"))
        trial_organizations = result.scalar_one()
        
        result = await db.execute(select(func.count(User.id)).where(User.organization_id.isnot(None), User.is_active == True))
        total_users = result.scalar_one()
        
        result = await db.execute(select(func.count(User.id)).where(User.is_super_admin == True, User.is_active == True))
        super_admins = result.scalar_one()
        
        plan_breakdown = {}
        result = await db.execute(select(Organization.plan_type).distinct())
        plan_types = result.scalars().all()
        for plan_type in plan_types:
            result = await db.execute(select(func.count(Organization.id)).where(Organization.plan_type == plan_type))
            count = result.scalar_one()
            plan_breakdown[plan_type] = count
        
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        result = await db.execute(select(func.count(Organization.id)).where(Organization.created_at >= thirty_days_ago))
        new_licenses_this_month = result.scalar_one()
        
        total_storage_used_gb = total_licenses * 0.5
        average_users_per_org = round(total_users / total_licenses) if total_licenses > 0 else 0
        
        result = await db.execute(select(func.sum(User.failed_login_attempts)))
        failed_login_attempts = result.scalar_one() or 0
        
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        result = await db.execute(select(func.count(Organization.id)).where(Organization.created_at >= seven_days_ago))
        recent_new_orgs = result.scalar_one()
        
        return {
            "total_licenses_issued": total_licenses,
            "active_organizations": active_organizations,
            "trial_organizations": trial_organizations,
            "total_active_users": total_users,
            "super_admins_count": super_admins,
            "new_licenses_this_month": new_licenses_this_month,
            "plan_breakdown": plan_breakdown,
            "system_health": {
                "status": "healthy",
                "uptime": "99.9%"
            },
            "generated_at": datetime.utcnow().isoformat(),
            "total_storage_used_gb": total_storage_used_gb,
            "average_users_per_org": average_users_per_org,
            "failed_login_attempts": failed_login_attempts,
            "recent_new_orgs": recent_new_orgs
        }

    @staticmethod
    async def get_org_statistics(db: AsyncSession, organization_id: int) -> Dict:
        """Get organization-specific statistics"""
        result = await db.execute(select(func.count(User.id)).where(
            User.organization_id == organization_id,
            User.is_active == True
        ))
        total_users = result.scalar_one()
        
        result = await db.execute(select(func.count(Customer.id)).where(
            Customer.organization_id == organization_id
        ))
        total_customers = result.scalar_one()
        
        result = await db.execute(select(func.count(Vendor.id)).where(
            Vendor.organization_id == organization_id
        ))
        total_vendors = result.scalar_one()
        
        result = await db.execute(select(func.count(Product.id)).where(
            Product.organization_id == organization_id
        ))
        total_products = result.scalar_one()
        
        result = await db.execute(select(func.count(Stock.id)).where(
            Stock.organization_id == organization_id
        ))
        total_stock_items = result.scalar_one()
        
        return {
            "organization_id": organization_id,
            "total_users": total_users,
            "total_customers": total_customers,
            "total_vendors": total_vendors,
            "total_products": total_products,
            "total_stock_items": total_stock_items,
            "generated_at": datetime.utcnow().isoformat()
        }

    @staticmethod
    async def create_license(db: AsyncSession, license_data: OrganizationLicenseCreate, current_user: User) -> Dict:
        """Create new organization license"""
        try:
            # Check if email already exists in our database
            result = await db.execute(select(User).filter_by(email=license_data.superadmin_email))
            existing_user = result.scalars().first()
            if existing_user:
                raise HTTPException(status_code=400, detail="Email already registered in the system")
            
            subdomain = license_data.subdomain or generate_subdomain(license_data.organization_name)
            result = await db.execute(select(Organization).filter_by(subdomain=subdomain))
            if result.scalars().first():
                raise ValueError(f"Subdomain '{subdomain}' is already in use")

            organization = Organization(
                name=license_data.organization_name,
                subdomain=subdomain,
                primary_email=license_data.superadmin_email,
                primary_phone=license_data.primary_phone,
                address1=license_data.address1,
                city=license_data.city,
                state=license_data.state,
                pin_code=license_data.pin_code,
                gst_number=license_data.gst_number,
                max_users=license_data.max_users,
                status="trial",
                plan_type="basic",
                enabled_modules=license_data.enabled_modules or {k: True for k in OrganizationService.get_available_modules()["available_modules"]},
                license_type="trial",
                license_issued_date=datetime.utcnow(),
                license_expiry_date=datetime.utcnow() + timedelta(days=30),
                license_duration_months=1
            )
            db.add(organization)
            await db.flush()

            temp_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
            
            # Check for orphan Supabase user and clean up if exists
            supabase_existing = supabase_auth_service.get_user_by_email(license_data.superadmin_email)
            if supabase_existing:
                logger.warning(f"Found orphan Supabase user for {license_data.superadmin_email} - deleting")
                supabase_auth_service.delete_user(supabase_existing['supabase_uuid'])
            
            supabase_user = supabase_auth_service.create_user(
                email=license_data.superadmin_email,
                password=temp_password,
                user_metadata={
                    "full_name": "Organization Admin",
                    "role": UserRole.ORG_ADMIN.value,
                    "organization_id": organization.id
                }
            )

            super_admin_user = User(
                organization_id=organization.id,
                email=license_data.superadmin_email,
                hashed_password=get_password_hash(temp_password),
                full_name="Organization Admin",
                role=UserRole.ORG_ADMIN,
                is_active=True,
                must_change_password=True,
                supabase_uuid=supabase_user["supabase_uuid"]
            )
            db.add(super_admin_user)
            await db.flush()

            rbac_service = RBACService(db)
            logger.info(f"Initializing RBAC for organization {organization.id}")
            permissions = await rbac_service.initialize_default_permissions()
            logger.info(f"Initialized {len(permissions)} default permissions")
            
            roles = await rbac_service.initialize_default_roles(organization.id)
            logger.info(f"Initialized {len(roles)} roles for organization {organization.id}")

            result = await db.execute(select(ServiceRole).filter_by(
                organization_id=organization.id,
                name='admin'
            ))
            admin_role = result.scalars().first()
            if admin_role:
                await rbac_service.assign_role_to_user(super_admin_user.id, admin_role.id)
                logger.info(f"Successfully assigned admin role to user {super_admin_user.email}")
            else:
                logger.error(f"Admin role not found after initialization for org {organization.id}")
                raise ValueError("Failed to initialize RBAC roles properly")

            await db.commit()

            log_license_creation(organization.name, license_data.superadmin_email, current_user.email)

            success, email_error = email_service.send_license_creation_email(
                license_data.superadmin_email,
                "Organization Admin",
                license_data.organization_name,
                temp_password,
                subdomain,
                organization.org_code,
                current_user.email,
                notify_creator=True
            )

            if not success:
                logger.warning(f"Failed to send license creation email: {email_error}")

            return {
                "organization_name": organization.name,
                "subdomain": organization.subdomain,
                "superadmin_email": super_admin_user.email,
                "temp_password": temp_password,
                "organization_id": organization.id,
                "message": "Organization license created successfully. Admin must change password on first login."
            }
        except ValueError as e:
            await db.rollback()
            raise HTTPException(status_code=400, detail=str(e))
        except SupabaseAuthError as e:
            await db.rollback()
            if "already been registered" in str(e):
                raise HTTPException(status_code=400, detail="Email already registered in authentication system. Please use a different email or contact support.")
            raise HTTPException(status_code=500, detail=str(e))
        except Exception as e:
            await db.rollback()
            logger.exception(f"Failed to create organization license: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")

    @staticmethod
    def get_available_modules() -> Dict:
        """Get available modules in the application"""
        available_modules = {
            "CRM": {
                "name": "CRM",
                "description": "Customer Relationship Management",
                "endpoints": ["/api/v1/customers"],
                "enabled": True
            },
            "ERP": {
                "name": "ERP", 
                "description": "Enterprise Resource Planning",
                "endpoints": ["/api/v1/companies", "/api/v1/users"],
                "enabled": True
            },
            "HR": {
                "name": "HR",
                "description": "Human Resources Management", 
                "endpoints": ["/api/v1/users"],
                "enabled": True
            },
            "Inventory": {
                "name": "Inventory",
                "description": "Inventory Management",
                "endpoints": ["/api/v1/stock", "/api/v1/products", "/api/v1/inventory"],
                "enabled": True
            },
            "Service": {
                "name": "Service",
                "description": "Service Management",
                "endpoints": ["/api/v1/service-analytics", "/api/v1/sla", "/api/v1/dispatch", "/api/v1/feedback"],
                "enabled": True
            },
            "Analytics": {
                "name": "Analytics", 
                "description": "Reports and Analytics",
                "endpoints": ["/api/v1/analytics", "/api/v1/service-analytics"],
                "enabled": True
            },
            "Finance": {
                "name": "Finance",
                "description": "Financial Management",
                "endpoints": ["/api/v1/vendors", "/api/v1", "/api/v1/gst"],
                "enabled": True
            }
        }
        
        return {
            "available_modules": available_modules,
            "default_enabled": list(available_modules.keys())
        }

    @staticmethod
    async def get_organization_modules(db: AsyncSession, organization_id: int) -> Dict:
        """Get organization's enabled modules"""
        result = await db.execute(select(Organization).filter_by(id=organization_id))
        org = result.scalars().first()
        if not org:
            return None
        
        enabled_modules = org.enabled_modules or {
            "CRM": True,
            "ERP": True,
            "HR": True,
            "Inventory": True,
            "Service": True,
            "Analytics": True,
            "Finance": True
        }
        
        return {
            "organization_id": organization_id,
            "organization_name": org.name,
            "enabled_modules": enabled_modules
        }

    @staticmethod
    async def update_organization_modules(db: AsyncSession, organization_id: int, enabled_modules: Dict) -> Dict:
        """Update organization's enabled modules"""
        result = await db.execute(select(Organization).filter_by(id=organization_id))
        org = result.scalars().first()
        if not org:
            return None
        
        if not isinstance(enabled_modules, dict):
            raise ValueError("enabled_modules must be a dictionary")
        
        org.enabled_modules = enabled_modules
        await db.commit()
        await db.refresh(org)
        
        return {
            "message": "Organization modules updated successfully",
            "organization_id": organization_id,
            "enabled_modules": enabled_modules
        }