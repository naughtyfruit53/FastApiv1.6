# app/services/organization_service.py

from sqlalchemy.orm import Session
from app.models import Organization, User
from app.schemas.organization import OrganizationLicenseCreate, OrganizationLicenseResponse
from app.schemas.user import UserCreate, UserRole
from app.core.security import get_password_hash, create_access_token
from app.services.otp_service import OTPService
from app.services.email_service import email_service
from app.services.rbac import RBACService
from app.services.role_management_service import RoleManagementService
from app.services.user_service import UserService
import secrets
import string
import logging

logger = logging.getLogger(__name__)

class OrganizationService:
    @staticmethod
    def create_license(db: Session, license_data: OrganizationLicenseCreate, current_user: User) -> OrganizationLicenseResponse:
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
            license_type="trial",
            license_issued_date=datetime.utcnow(),
            license_expiry_date=datetime.utcnow() + timedelta(days=30),
            license_duration_months=1,
            plan_type="trial",
            created_by_id=current_user.id
        )
        db.add(org)
        db.commit()
        db.refresh(org)
        
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
        
        # Assign super admin role
        RoleManagementService.assign_role_to_user(
            db=db,
            user_id=super_admin.id,
            role_name="super_admin",
            organization_id=org.id
        )
        
        # Send email with temp password
        success, error = email_service.send_user_creation_email(
            user_email=super_admin.email,
            user_name=super_admin.full_name,
            temp_password=temp_password,
            organization_name=org.name,
            login_url=f"https://{org.subdomain}.app.tritiq.com" if org.subdomain else "https://app.tritiq.com"
        )
        
        if not success:
            logger.warning(f"License created but welcome email failed: {error}")
        
        return OrganizationLicenseResponse(
            organization_id=org.id,
            organization_name=org.name,
            subdomain=org.subdomain,
            org_code=org.org_code,
            superadmin_email=super_admin.email,
            temp_password=temp_password if success else None,
            email_sent=success,
            email_error=error if not success else None
        )