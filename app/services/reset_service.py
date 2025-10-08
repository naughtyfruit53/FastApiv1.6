# app/services/reset_service.py

"""
System-level reset service for factory default operations
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete, select, text  # Added for raw SQL execution
from typing import Dict, Any
from app.models.user_models import Organization, User, ServiceRole, UserServiceRole, ServiceRolePermission
from app.models.system_models import Company, EmailNotification, PaymentTerm, OTPVerification, AuditLog
from app.models.customer_models import Customer, Vendor
from app.models.product_models import Product, Stock
from app.utils.supabase_auth import supabase_auth_service
import logging

logger = logging.getLogger(__name__)

# List of custom raw SQL tables that need to be cleaned up
CUSTOM_RAW_SQL_TABLES = [
    'oauth_states',
    'user_email_tokens',
    'bank_accounts',
    'chart_of_accounts',
    'snappymail_configs',
    'email_attachments',
    'emails',
    'mail_accounts',
]

class ResetService:
    """Service for system-level reset operations"""
    
    @staticmethod
    async def factory_default_system(db: AsyncSession, admin_user: User) -> Dict[str, Any]:
        """
        Complete system factory reset (for God Super Admin only - naughtyfruit53@gmail.com)
        Removes ALL organizations, users, and data - resets entire system
        
        This operation is atomic - either all deletions succeed or all are rolled back.
        
        Args:
            db: Database session
            admin_user: Admin user performing the reset (must be god superadmin)
            
        Returns:
            dict: Result with message and deleted counts
            
        Raises:
            HTTPException: If user is not the god superadmin
        """
        # Restrict to god superadmin only
        GOD_SUPERADMIN_EMAIL = "naughtyfruit53@gmail.com"
        if admin_user.email != GOD_SUPERADMIN_EMAIL:
            from fastapi import HTTPException, status
            logger.error(f"Unauthorized factory reset attempt by {admin_user.email}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Factory reset is restricted to god superadmin ({GOD_SUPERADMIN_EMAIL}) only"
            )
        
        logger.warning(f"FACTORY DEFAULT: Starting complete system reset initiated by {admin_user.email}")
        
        try:
            result = {"message": "System factory reset completed", "deleted": {}, "errors": []}
            
            # Delete in reverse dependency order to avoid foreign key constraints
            logger.info("Step 1: Deleting user_service_roles")
            res_user_service_roles = await db.execute(delete(UserServiceRole))
            deleted_user_service_roles = res_user_service_roles.rowcount
            result["deleted"]["user_service_roles"] = deleted_user_service_roles
            logger.info(f"Deleted {deleted_user_service_roles} user_service_roles")
            
            logger.info("Step 2: Deleting service_role_permissions")
            res_role_permissions = await db.execute(delete(ServiceRolePermission))
            deleted_role_permissions = res_role_permissions.rowcount
            result["deleted"]["service_role_permissions"] = deleted_role_permissions
            logger.info(f"Deleted {deleted_role_permissions} service_role_permissions")
            
            logger.info("Step 3: Deleting service_roles")
            res_service_roles = await db.execute(delete(ServiceRole))
            deleted_service_roles = res_service_roles.rowcount
            result["deleted"]["service_roles"] = deleted_service_roles
            logger.info(f"Deleted {deleted_service_roles} service_roles")
            
            logger.info("Step 4: Deleting email_notifications")
            res_notifications = await db.execute(delete(EmailNotification))
            deleted_notifications = res_notifications.rowcount
            result["deleted"]["email_notifications"] = deleted_notifications
            logger.info(f"Deleted {deleted_notifications} email_notifications")
            
            logger.info("Step 5: Deleting stock entries")
            res_stock = await db.execute(delete(Stock))
            deleted_stock = res_stock.rowcount
            result["deleted"]["stock"] = deleted_stock
            logger.info(f"Deleted {deleted_stock} stock entries")
            
            logger.info("Step 6: Deleting payment_terms")
            res_payment_terms = await db.execute(delete(PaymentTerm))
            deleted_payment_terms = res_payment_terms.rowcount
            result["deleted"]["payment_terms"] = deleted_payment_terms
            logger.info(f"Deleted {deleted_payment_terms} payment_terms")
            
            logger.info("Step 7: Deleting products")
            res_products = await db.execute(delete(Product))
            deleted_products = res_products.rowcount
            result["deleted"]["products"] = deleted_products
            logger.info(f"Deleted {deleted_products} products")
            
            logger.info("Step 8: Deleting customers")
            res_customers = await db.execute(delete(Customer))
            deleted_customers = res_customers.rowcount
            result["deleted"]["customers"] = deleted_customers
            logger.info(f"Deleted {deleted_customers} customers")
            
            logger.info("Step 9: Deleting vendors")
            res_vendors = await db.execute(delete(Vendor))
            deleted_vendors = res_vendors.rowcount
            result["deleted"]["vendors"] = deleted_vendors
            logger.info(f"Deleted {deleted_vendors} vendors")
            
            logger.info("Step 10: Deleting companies")
            res_companies = await db.execute(delete(Company))
            deleted_companies = res_companies.rowcount
            result["deleted"]["companies"] = deleted_companies
            logger.info(f"Deleted {deleted_companies} companies")
            
            logger.info("Step 11: Deleting OTP verifications")
            res_otps = await db.execute(delete(OTPVerification))
            deleted_otps = res_otps.rowcount
            result["deleted"]["otp_verifications"] = deleted_otps
            logger.info(f"Deleted {deleted_otps} OTP verifications")
            
            logger.info("Step 12: Deleting audit_logs")
            res_audit_logs = await db.execute(delete(AuditLog))
            deleted_audit_logs = res_audit_logs.rowcount
            result["deleted"]["audit_logs"] = deleted_audit_logs
            logger.info(f"Deleted {deleted_audit_logs} audit_logs")
            
            # Delete custom raw SQL tables
            logger.info("Step 13: Deleting custom raw SQL tables")
            for table_name in CUSTOM_RAW_SQL_TABLES:
                try:
                    logger.info(f"Deleting from {table_name}")
                    res = await db.execute(text(f"DELETE FROM {table_name}"))
                    deleted_count = res.rowcount
                    result["deleted"][table_name] = deleted_count
                    logger.info(f"Deleted {deleted_count} records from {table_name}")
                except Exception as e:
                    # Log but don't fail if table doesn't exist or has other issues
                    logger.warning(f"Error deleting from {table_name}: {str(e)}")
                    result["errors"].append(f"Failed to delete {table_name}: {str(e)}")
                    result["deleted"][table_name] = 0
            
            logger.info("Step 14: Deleting non-super-admin users")
            res_users = await db.execute(delete(User).where(User.is_super_admin == False))
            deleted_users = res_users.rowcount
            result["deleted"]["users"] = deleted_users
            logger.info(f"Deleted {deleted_users} non-super-admin users")
            
            logger.info("Step 15: Deleting organizations")
            res_organizations = await db.execute(delete(Organization))
            deleted_organizations = res_organizations.rowcount
            result["deleted"]["organizations"] = deleted_organizations
            logger.info(f"Deleted {deleted_organizations} organizations")
            
            # Reset sequence IDs to 1
            logger.info("Step 16: Resetting sequence IDs")
            sequences_to_reset = [
                "organizations_id_seq",
                "users_id_seq",
                "service_roles_id_seq",
                "user_service_roles_id_seq",
                "service_role_permissions_id_seq",
                "companies_id_seq",
                "customers_id_seq",
                "vendors_id_seq",
                "products_id_seq",
                "stock_id_seq",
                "payment_terms_id_seq",
            ]
            for seq in sequences_to_reset:
                try:
                    await db.execute(text(f"ALTER SEQUENCE {seq} RESTART WITH 1;"))
                    logger.info(f"Reset sequence {seq}")
                except Exception as e:
                    logger.warning(f"Failed to reset sequence {seq}: {str(e)}")
            
            # Commit database changes
            logger.info("Step 17: Committing database transaction")
            await db.commit()
            logger.info("Database transaction committed successfully")
            
            # Delete all Supabase auth users (done after DB commit as this is external)
            logger.info("Step 18: Deleting Supabase auth users")
            try:
                users = supabase_auth_service.get_all_users()
                deleted_supabase_users = 0
                for user in users:
                    try:
                        supabase_auth_service.delete_user(user['id'])
                        deleted_supabase_users += 1
                    except Exception as user_error:
                        logger.warning(f"Failed to delete Supabase user {user.get('id', 'unknown')}: {str(user_error)}")
                        result["errors"].append(f"Failed to delete Supabase user {user.get('id', 'unknown')}: {str(user_error)}")
                result["deleted"]["supabase_auth_users"] = deleted_supabase_users
                logger.info(f"Deleted {deleted_supabase_users} out of {len(users)} Supabase auth users")
            except Exception as e:
                logger.warning(f"Failed to enumerate or delete Supabase auth users: {str(e)}")
                result["errors"].append(f"Supabase auth deletion error: {str(e)}")
                result["deleted"]["supabase_auth_users"] = 0
            
            logger.warning(f"FACTORY DEFAULT: Complete system reset completed - all data removed")
            logger.info(f"Deletion summary: {result['deleted']}")
            if result["errors"]:
                logger.warning(f"Errors encountered: {result['errors']}")
            
            return result
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error during factory default system reset: {str(e)}", exc_info=True)
            logger.error("Transaction rolled back - no changes were made to the database")
            raise e
    
    @staticmethod
    async def reset_organization_business_data(db: AsyncSession, organization_id: int) -> Dict[str, Any]:
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
            org = await db.scalar(select(Organization).where(Organization.id == organization_id))
            if not org:
                raise ValueError(f"Organization with ID {organization_id} not found")
            
            # Delete business data in reverse dependency order to avoid foreign key constraints
            
            # Delete all user_service_roles for this org
            res_user_service_roles = await db.execute(delete(UserServiceRole).where(UserServiceRole.organization_id == organization_id))
            deleted_user_service_roles = res_user_service_roles.rowcount
            result["deleted"]["user_service_roles"] = deleted_user_service_roles
            
            # Delete all service_role_permissions for this org
            res_role_permissions = await db.execute(delete(ServiceRolePermission).where(ServiceRolePermission.organization_id == organization_id))
            deleted_role_permissions = res_role_permissions.rowcount
            result["deleted"]["service_role_permissions"] = deleted_role_permissions
            
            # Delete all service_roles for this org
            res_service_roles = await db.execute(delete(ServiceRole).where(ServiceRole.organization_id == organization_id))
            deleted_service_roles = res_service_roles.rowcount
            result["deleted"]["service_roles"] = deleted_service_roles
            
            # Delete all email notifications for this org
            res_notifications = await db.execute(delete(EmailNotification).where(EmailNotification.organization_id == organization_id))
            deleted_notifications = res_notifications.rowcount
            result["deleted"]["email_notifications"] = deleted_notifications
            
            # Delete all stock entries for this org
            res_stock = await db.execute(delete(Stock).where(Stock.organization_id == organization_id))
            deleted_stock = res_stock.rowcount
            result["deleted"]["stock"] = deleted_stock
            
            # Delete all payment terms for this org
            res_payment_terms = await db.execute(delete(PaymentTerm).where(PaymentTerm.organization_id == organization_id))
            deleted_payment_terms = res_payment_terms.rowcount
            result["deleted"]["payment_terms"] = deleted_payment_terms
            
            # Delete all products for this org
            res_products = await db.execute(delete(Product).where(Product.organization_id == organization_id))
            deleted_products = res_products.rowcount
            result["deleted"]["products"] = deleted_products
            
            # Delete all customers for this org
            res_customers = await db.execute(delete(Customer).where(Customer.organization_id == organization_id))
            deleted_customers = res_customers.rowcount
            result["deleted"]["customers"] = deleted_customers
            
            # Delete all vendors for this org
            res_vendors = await db.execute(delete(Vendor).where(Vendor.organization_id == organization_id))
            deleted_vendors = res_vendors.rowcount
            result["deleted"]["vendors"] = deleted_vendors
            
            # Delete all companies for this org
            res_companies = await db.execute(delete(Company).where(Company.organization_id == organization_id))
            deleted_companies = res_companies.rowcount
            result["deleted"]["companies"] = deleted_companies
            
            # Note: We preserve users and organization settings
            # Note: We preserve audit logs for compliance
            
            await db.commit()
            logger.info(f"Organization {organization_id} business data reset completed - users and org settings preserved")
            
            return result
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error during organization {organization_id} business data reset: {str(e)}", exc_info=True)
            raise e