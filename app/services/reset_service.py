# app/services/reset_service.py

"""
System-level reset service for factory default operations
"""
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from typing import Dict, Any
from app.models.user_models import Organization, User, ServiceRole, UserServiceRole
from app.models.system_models import Company, EmailNotification, PaymentTerm, OTPVerification, AuditLog
from app.models.customer_models import Customer, Vendor
from app.models.product_models import Product, Stock
from app.utils.supabase_auth import supabase_auth_service
import logging

logger = logging.getLogger(__name__)

class ResetService:
    """Service for system-level reset operations"""
    
    @staticmethod
    def factory_default_system(db: Session) -> Dict[str, Any]:
        """
        Complete system factory reset (for App Super Admin only)
        Removes ALL organizations, users, and data - resets entire system
        
        Args:
            db: Database session
            
        Returns:
            dict: Result with message and deleted counts
        """
        try:
            result = {"message": "System factory reset completed", "deleted": {}}
            
            # Delete in reverse dependency order to avoid foreign key constraints
            
            # Delete all user_service_roles (dependent on users)
            deleted_user_service_roles = db.query(UserServiceRole).delete()
            result["deleted"]["user_service_roles"] = deleted_user_service_roles
            
            # Delete all service_roles (dependent on organizations)
            deleted_service_roles = db.query(ServiceRole).delete()
            result["deleted"]["service_roles"] = deleted_service_roles
            
            # Delete all email notifications
            deleted_notifications = db.query(EmailNotification).delete()
            result["deleted"]["email_notifications"] = deleted_notifications
            
            # Delete all stock entries
            deleted_stock = db.query(Stock).delete()
            result["deleted"]["stock"] = deleted_stock
            
            # Delete all payment terms
            deleted_payment_terms = db.query(PaymentTerm).delete()
            result["deleted"]["payment_terms"] = deleted_payment_terms
            
            # Delete all products
            deleted_products = db.query(Product).delete()
            result["deleted"]["products"] = deleted_products
            
            # Delete all customers
            deleted_customers = db.query(Customer).delete()
            result["deleted"]["customers"] = deleted_customers
            
            # Delete all vendors
            deleted_vendors = db.query(Vendor).delete()
            result["deleted"]["vendors"] = deleted_vendors
            
            # Delete all companies
            deleted_companies = db.query(Company).delete()
            result["deleted"]["companies"] = deleted_companies
            
            # Delete all OTP verifications
            deleted_otps = db.query(OTPVerification).delete()
            result["deleted"]["otp_verifications"] = deleted_otps
            
            # Delete all non-super-admin users
            deleted_users = db.query(User).filter(
                User.is_super_admin == False
            ).delete()
            result["deleted"]["users"] = deleted_users
            
            # Delete all organizations
            deleted_organizations = db.query(Organization).delete()
            result["deleted"]["organizations"] = deleted_organizations
            
            # Reset sequence IDs to 1
            db.execute("ALTER SEQUENCE organizations_id_seq RESTART WITH 1;")
            db.execute("ALTER SEQUENCE users_id_seq RESTART WITH 1;")
            db.execute("ALTER SEQUENCE service_roles_id_seq RESTART WITH 1;")
            db.execute("ALTER SEQUENCE user_service_roles_id_seq RESTART WITH 1;")
            # Add other sequences if needed (e.g., for companies, customers, etc.)
            
            # Commit database changes
            db.commit()
            
            # Delete all Supabase auth users
            try:
                users = supabase_auth_service.get_all_users()
                for user in users:
                    supabase_auth_service.delete_user(user['id'])
                result["deleted"]["supabase_auth_users"] = len(users)
                logger.info(f"Deleted {len(users)} Supabase auth users")
            except Exception as e:
                logger.warning(f"Failed to delete Supabase auth users: {str(e)}")
                result["deleted"]["supabase_auth_users"] = 0
            
            logger.warning(f"FACTORY DEFAULT: Complete system reset completed - all data removed")
            
            return result
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error during factory default system reset: {str(e)}", exc_info=True)
            raise e
    
    @staticmethod
    def reset_organization_business_data(db: Session, organization_id: int) -> Dict[str, Any]:
        """
        Reset organization business data (preserves users and org settings)
        Removes business data like products, stock, customers, vendors, etc.
        
        Args:
            db: Database session
            organization_id: Organization ID to reset
            
        Returns:
            dict: Result with message and deleted counts
        """
        try:
            result = {"message": "Organization business data reset completed", "deleted": {}}
            
            # Validate organization exists
            org = db.query(Organization).filter(Organization.id == organization_id).first()
            if not org:
                raise ValueError(f"Organization with ID {organization_id} not found")
            
            # Delete business data in reverse dependency order to avoid foreign key constraints
            
            # Delete all user_service_roles for this org
            deleted_user_service_roles = db.query(UserServiceRole).filter(
                UserServiceRole.organization_id == organization_id
            ).delete()
            result["deleted"]["user_service_roles"] = deleted_user_service_roles
            
            # Delete all service_roles for this org
            deleted_service_roles = db.query(ServiceRole).filter(
                ServiceRole.organization_id == organization_id
            ).delete()
            result["deleted"]["service_roles"] = deleted_service_roles
            
            # Delete all email notifications for this org
            deleted_notifications = db.query(EmailNotification).filter(
                EmailNotification.organization_id == organization_id
            ).delete()
            result["deleted"]["email_notifications"] = deleted_notifications
            
            # Delete all stock entries for this org
            deleted_stock = db.query(Stock).filter(
                Stock.organization_id == organization_id
            ).delete()
            result["deleted"]["stock"] = deleted_stock
            
            # Delete all payment terms for this org
            deleted_payment_terms = db.query(PaymentTerm).filter(
                PaymentTerm.organization_id == organization_id
            ).delete()
            result["deleted"]["payment_terms"] = deleted_payment_terms
            
            # Delete all products for this org
            deleted_products = db.query(Product).filter(
                Product.organization_id == organization_id
            ).delete()
            result["deleted"]["products"] = deleted_products
            
            # Delete all customers for this org
            deleted_customers = db.query(Customer).filter(
                Customer.organization_id == organization_id
            ).delete()
            result["deleted"]["customers"] = deleted_customers
            
            # Delete all vendors for this org
            deleted_vendors = db.query(Vendor).filter(
                Vendor.organization_id == organization_id
            ).delete()
            result["deleted"]["vendors"] = deleted_vendors
            
            # Delete all companies for this org
            deleted_companies = db.query(Company).filter(
                Company.organization_id == organization_id
            ).delete()
            result["deleted"]["companies"] = deleted_companies
            
            # Reset organization status to indicate incomplete setup
            org.company_details_completed = False
            
            # Note: We preserve users and organization settings
            # Note: We preserve audit logs for compliance
            
            db.commit()
            logger.info(f"Organization {organization_id} business data reset completed - users and org settings preserved")
            
            return result
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error during organization {organization_id} business data reset: {str(e)}", exc_info=True)
            raise e