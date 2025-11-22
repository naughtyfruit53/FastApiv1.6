# app/services/organization_service.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Dict, List
from app.models import Organization, User
from app.models.product_models import Product
from app.models.customer_models import Customer
from app.models.vendors import Vendor
from app.models.vouchers.sales import SalesVoucher
from app.models.audit_log import AuditLog
from app.schemas.organization import OrganizationLicenseCreate, OrganizationLicenseResponse
from app.schemas.user import UserCreate, UserRole
from app.core.security import get_password_hash
from app.services.otp_service import OTPService
from app.services.system_email_service import system_email_service
from app.services.rbac import RBACService
from app.services.role_management_service import RoleManagementService
from app.services.user_service import UserService
from app.scripts.seed_default_coa_accounts import create_default_accounts
import secrets
import string
import logging
import asyncio
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class OrganizationService:
    @staticmethod
    def create_license(db: AsyncSession, license_data: OrganizationLicenseCreate, current_user: User) -> OrganizationLicenseResponse:
        """Create new organization license with super admin account and send credentials via email"""
        # Generate unique subdomain and org_code
        subdomain = license_data.organization_name.lower().replace(" ", "-")
        org_code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        
        # Create organization
        org = Organization(
            name=license_data.organization_name,
            subdomain=subdomain,
            org_code=org_code,
            primary_email=license_data.superadmin_email,
            primary_phone=license_data.primary_phone,
            address1=license_data.address1,
            pin_code=license_data.pin_code,
            city=license_data.city,
            state=license_data.state,
            state_code=license_data.state_code,
            gst_number=license_data.gst_number,
            max_users=license_data.max_users,
            license_type=license_data.license_type,
            license_issued_date=datetime.utcnow(),
            license_duration_months=license_data.license_duration_months,
            plan_type="premium" if license_data.license_type != "trial" else "trial",
            created_by_id=current_user.id
        )
        
        # Set expiry date based on license type
        if license_data.license_type == "perpetual":
            org.license_expiry_date = None
        elif license_data.license_type == "month":
            org.license_duration_months = 1
            org.license_expiry_date = datetime.utcnow() + timedelta(days=30)
        elif license_data.license_type == "year":
            org.license_duration_months = 12
            org.license_expiry_date = datetime.utcnow() + timedelta(days=365)
        elif license_data.license_type == "trial":
            org.license_duration_months = 1
            org.license_expiry_date = datetime.utcnow() + timedelta(days=7)  # Changed to 7 days for trial
        
        db.add(org)
        db.commit()
        db.refresh(org)
        
        # Seed standard chart of accounts for the new organization
        create_default_accounts(db, org.id)
        
        # Generate temp password for org super admin
        alphabet = string.ascii_letters + string.digits + string.punctuation
        temp_password = ''.join(secrets.choice(alphabet) for _ in range(12))
        
        # Create org super admin user with temp password
        super_admin = UserService.create_user(
            db=db,
            user_data=UserCreate(
                email=license_data.superadmin_email,
                password=temp_password,
                full_name="Org Super Admin",
                role=UserRole.ORG_ADMIN,
                organization_id=org.id,
                is_active=True,
                must_change_password=True  # Force password change on first login
            )
        )
        
        # Initialize RBAC for organization
        rbac_service = RBACService(db)
        rbac_service.initialize_default_permissions()
        rbac_service.initialize_default_roles(org.id)
        
        # Assign admin role
        RoleManagementService.assign_role_to_user(
            db=db,
            user_id=super_admin.id,
            role_name="admin",
            organization_id=org.id
        )
        
        # Send email with temp password (system-level: account creation)
        try:
            success, error = asyncio.run(system_email_service.send_user_creation_email(
                user_email=super_admin.email,
                user_name=super_admin.full_name,
                temp_password=temp_password,
                organization_name=org.name,
                login_url=f"https://{org.subdomain}.app.tritiq.com" if org.subdomain else "https://app.tritiq.com",
                organization_id=org.id,
                user_id=super_admin.id
            ))
        except RuntimeError:
            # Already in event loop, create new loop in thread
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    asyncio.run,
                    system_email_service.send_user_creation_email(
                        user_email=super_admin.email,
                        user_name=super_admin.full_name,
                        temp_password=temp_password,
                        organization_name=org.name,
                        login_url=f"https://{org.subdomain}.app.tritiq.com" if org.subdomain else "https://app.tritiq.com",
                        organization_id=org.id,
                        user_id=super_admin.id
                    )
                )
                success, error = future.result()
        
        if not success:
            logger.warning(f"License created but welcome email failed: {error}")
        
        license_status = "trial" if license_data.license_type == "trial" else "active"
        
        return OrganizationLicenseResponse(
            organization_id=org.id,
            organization_name=org.name,
            subdomain=org.subdomain,
            org_code=org.org_code,
            superadmin_email=super_admin.email,
            temp_password=temp_password if success else None,
            email_sent=success,
            email_error=error if not success else None,
            license_type=org.license_type,
            license_status=license_status,
            license_issued_date=org.license_issued_date,
            license_expiry_date=org.license_expiry_date
        )

    @staticmethod
    async def get_app_statistics(db: AsyncSession) -> Dict:
        """Get app-level statistics (admin only)"""
        total_orgs = (await db.execute(select(func.count(Organization.id)))).scalar_one()
        total_users = (await db.execute(select(func.count(User.id)))).scalar_one()
        return {
            "total_organizations": total_orgs,
            "total_users": total_users,
        }

    @staticmethod
    async def get_org_statistics(db: AsyncSession, org_id: int) -> Dict:
        """Get organization-level statistics"""
        total_products = (await db.execute(select(func.count(Product.id)).where(Product.organization_id == org_id))).scalar_one()
        total_customers = (await db.execute(select(func.count(Customer.id)).where(Customer.organization_id == org_id))).scalar_one()
        total_vendors = (await db.execute(select(func.count(Vendor.id)).where(Vendor.organization_id == org_id))).scalar_one()
        active_users = (await db.execute(select(func.count(User.id)).where(User.organization_id == org_id, User.is_active == True))).scalar_one()
        
        # Monthly sales (sum of sales vouchers in last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        monthly_sales = (await db.execute(select(func.sum(SalesVoucher.total_amount)).where(
            SalesVoucher.organization_id == org_id,
            SalesVoucher.date >= thirty_days_ago
        ))).scalar_one() or 0
        
        # Inventory value (assume Stock model with quantity and Product with unit_price)
        from app.models.stock import Stock  # Assume Stock model
        inventory_value = (await db.execute(select(func.sum(Stock.quantity * Product.unit_price)).join(Product).where(
            Stock.organization_id == org_id
        ))).scalar_one() or 0
        
        # License info from organization
        org = (await db.execute(select(Organization).where(Organization.id == org_id))).scalar_one()
        
        return {
            "total_products": total_products,
            "total_products_trend": 0,  # Add real trend calculation if needed
            "total_products_direction": "neutral",
            "total_customers": total_customers,
            "total_customers_trend": 0,
            "total_customers_direction": "neutral",
            "total_vendors": total_vendors,
            "total_vendors_trend": 0,
            "total_vendors_direction": "neutral",
            "active_users": active_users,
            "active_users_trend": 0,
            "active_users_direction": "neutral",
            "monthly_sales": monthly_sales,
            "monthly_sales_trend": 0,
            "monthly_sales_direction": "neutral",
            "inventory_value": inventory_value,
            "inventory_value_trend": 0,
            "inventory_value_direction": "neutral",
            "plan_type": org.plan_type,
            "license_status": org.license_status,
            "license_issued_date": org.license_issued_date.isoformat() if org.license_issued_date else None,
            "license_expiry_date": org.license_expiry_date.isoformat() if org.license_expiry_date else None,
        }

    @staticmethod
    async def get_recent_activities(db: AsyncSession, org_id: int, limit: int = 5) -> List[Dict]:
        """Get recent activities for the organization"""
        stmt = select(AuditLog).where(AuditLog.organization_id == org_id).order_by(AuditLog.timestamp.desc()).limit(limit)
        result = await db.execute(stmt)
        activities = result.scalars().all()
        
        return [{
            "id": activity.id,
            "type": activity.action,
            "title": activity.action.capitalize(),
            "description": activity.details,
            "timestamp": activity.timestamp.isoformat() if activity.timestamp else None,
            "user_name": (await db.execute(select(User.full_name).where(User.id == activity.user_id))).scalar_one_or_none() or "Organization Admin"
        } for activity in activities]

    # ... (rest of the original methods unchanged)