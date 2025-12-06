"""
Idempotent permission seeder for RBAC system.

This seeder ensures all permissions exist in the database with the new dotted format,
and creates mappings for legacy permissions to new format.

Safe for multiple runs - will not duplicate or overwrite existing data.
"""

import logging
from typing import List, Dict, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.permissions import LEGACY_PERMISSION_MAP, PERMISSION_HIERARCHY
from app.models.rbac_models import ServicePermission

logger = logging.getLogger(__name__)


class PermissionSeeder:
    """Idempotent permission seeder"""
    
    def __init__(self, db: Session):
        self.db = db
        self.created_count = 0
        self.updated_count = 0
        self.skipped_count = 0
    
    def get_all_dotted_permissions(self) -> List[Tuple[str, str, str]]:
        """
        Get all permissions in dotted format.
        
        Returns:
            List of (permission_key, display_name, description) tuples
        """
        permissions = [
            # User management
            ("users.manage", "Manage Users", "Create, update, and manage user accounts"),
            ("users.view", "View Users", "View user information"),
            ("users.create", "Create Users", "Create new user accounts"),
            ("users.delete", "Delete Users", "Delete user accounts"),
            
            # Password management
            ("password.reset_own", "Reset Own Password", "Reset your own password"),
            ("password.reset_org", "Reset Organization Passwords", "Reset passwords for users in the organization"),
            ("password.reset_any", "Reset Any Password", "Reset any user password (super admin)"),
            
            # Data management
            ("data.reset_own", "Reset Own Data", "Reset your own data"),
            ("data.reset_org", "Reset Organization Data", "Reset data for the organization"),
            ("data.reset_any", "Reset Any Data", "Reset data for any organization (super admin)"),
            
            # Organization management
            ("organizations.manage", "Manage Organizations", "Full organization management"),
            ("organizations.view", "View Organizations", "View organization information"),
            ("organizations.create", "Create Organizations", "Create new organizations"),
            ("organizations.delete", "Delete Organizations", "Delete organizations"),
            
            # Platform administration
            ("platform.admin", "Platform Admin", "Platform administrator access"),
            ("platform.super_admin", "Super Admin", "Super administrator with full access"),
            
            # Audit
            ("audit.view", "View Audit Logs", "View audit logs for own organization"),
            ("audit.view_all", "View All Audit Logs", "View audit logs for all organizations"),
            
            # Factory reset
            ("platform.factory_reset", "Factory Reset", "Perform factory reset (super admin only)"),
            
            # Settings
            ("settings.access", "Access Settings", "Access organization settings"),
            
            # Service management
            ("service.create", "Create Service", "Create service records"),
            ("service.read", "Read Service", "Read service records"),
            ("service.update", "Update Service", "Update service records"),
            ("service.delete", "Delete Service", "Delete service records"),
            
            # Technician management
            ("technician.create", "Create Technician", "Create technician records"),
            ("technician.read", "Read Technician", "Read technician records"),
            ("technician.update", "Update Technician", "Update technician records"),
            ("technician.delete", "Delete Technician", "Delete technician records"),
            
            # Appointments
            ("appointment.create", "Create Appointment", "Create appointments"),
            ("appointment.read", "Read Appointment", "Read appointments"),
            ("appointment.update", "Update Appointment", "Update appointments"),
            ("appointment.delete", "Delete Appointment", "Delete appointments"),
            
            # Customer service
            ("customer_service.create", "Create Customer Service", "Create customer service records"),
            ("customer_service.read", "Read Customer Service", "Read customer service records"),
            ("customer_service.update", "Update Customer Service", "Update customer service records"),
            ("customer_service.delete", "Delete Customer Service", "Delete customer service records"),
            
            # Work orders
            ("work_order.create", "Create Work Order", "Create work orders"),
            ("work_order.read", "Read Work Order", "Read work orders"),
            ("work_order.update", "Update Work Order", "Update work orders"),
            ("work_order.delete", "Delete Work Order", "Delete work orders"),
            
            # Service reports
            ("service_reports.read", "Read Service Reports", "Read service reports"),
            ("service_reports.export", "Export Service Reports", "Export service reports"),
            
            # CRM
            ("crm.admin", "CRM Admin", "CRM administrator access"),
            ("crm.settings", "CRM Settings", "Manage CRM settings"),
            
            # Vouchers
            ("vouchers.view", "View Vouchers", "View vouchers"),
            ("vouchers.manage", "Manage Vouchers", "Manage vouchers"),
            
            # Commission
            ("crm.commission.read", "Read Commission", "Read commission records"),
            ("crm.commission.create", "Create Commission", "Create commission records"),
            ("crm.commission.update", "Update Commission", "Update commission records"),
            ("crm.commission.delete", "Delete Commission", "Delete commission records"),
            
            # Inventory
            ("inventory.read", "Read Inventory", "Read inventory records"),
            ("inventory.write", "Write Inventory", "Create inventory records"),
            ("inventory.update", "Update Inventory", "Update inventory records"),
            ("inventory.delete", "Delete Inventory", "Delete inventory records"),
            
            # Products
            ("products.read", "Read Products", "Read product records"),
            ("products.write", "Write Products", "Create product records"),
            ("products.update", "Update Products", "Update product records"),
            ("products.delete", "Delete Products", "Delete product records"),
            
            # Master data
            ("master_data.read", "Read Master Data", "Read master data (includes vendors, products, inventory)"),
            ("master_data.write", "Write Master Data", "Create master data records"),
            ("master_data.update", "Update Master Data", "Update master data records"),
            ("master_data.delete", "Delete Master Data", "Delete master data records"),
            
            # Manufacturing
            ("manufacturing.read", "Read Manufacturing", "Read manufacturing records"),
            ("manufacturing.write", "Write Manufacturing", "Create manufacturing records"),
            ("manufacturing.update", "Update Manufacturing", "Update manufacturing records"),
            ("manufacturing.delete", "Delete Manufacturing", "Delete manufacturing records"),
            
            # Vendors
            ("vendors.read", "Read Vendors", "Read vendor records"),
            ("vendors.create", "Create Vendors", "Create vendor records"),
            ("vendors.update", "Update Vendors", "Update vendor records"),
            ("vendors.delete", "Delete Vendors", "Delete vendor records"),
            
            # Voucher (ERP)
            ("voucher.read", "Read Voucher", "Read voucher records"),
            ("voucher.create", "Create Voucher", "Create voucher records"),
            ("voucher.update", "Update Voucher", "Update voucher records"),
            ("voucher.delete", "Delete Voucher", "Delete voucher records"),
            
            # Mail module
            ("mail.dashboard.read", "Read Mail Dashboard", "View mail dashboard"),
            ("mail.accounts.read", "Read Mail Accounts", "View mail accounts"),
            ("mail.accounts.create", "Create Mail Accounts", "Create mail accounts"),
            ("mail.accounts.update", "Update Mail Accounts", "Update mail accounts"),
            ("mail.accounts.delete", "Delete Mail Accounts", "Delete mail accounts"),
            ("mail.emails.read", "Read Emails", "Read emails"),
            ("mail.emails.compose", "Compose Emails", "Compose and send emails"),
            ("mail.emails.update", "Update Emails", "Update email records"),
            ("mail.emails.sync", "Sync Emails", "Sync email accounts"),
            ("mail.templates.read", "Read Email Templates", "Read email templates"),
            ("mail.templates.create", "Create Email Templates", "Create email templates"),
        ]
        
        return permissions
    
    def seed_permission(self, permission_key: str, display_name: str, description: str, module: str = None, action: str = None):
        """
        Seed a single permission (idempotent).
        
        Args:
            permission_key: Permission key in dotted format
            display_name: Human-readable name
            description: Permission description
            module: Module name (extracted from permission_key if not provided)
            action: Action name (extracted from permission_key if not provided)
        """
        # Extract module and action from permission_key if not provided
        if module is None or action is None:
            parts = permission_key.split('.')
            if module is None:
                module = parts[0] if len(parts) > 0 else 'unknown'
            if action is None:
                action = parts[-1] if len(parts) > 1 else 'unknown'
        
        # Check if permission already exists
        existing = self.db.query(ServicePermission).filter(
            ServicePermission.permission_key == permission_key
        ).first()
        
        if existing:
            # Update if needed
            updated = False
            if existing.display_name != display_name:
                existing.display_name = display_name
                updated = True
            if existing.description != description:
                existing.description = description
                updated = True
            if existing.module != module:
                existing.module = module
                updated = True
            if existing.action != action:
                existing.action = action
                updated = True
            
            if updated:
                self.db.commit()
                self.updated_count += 1
                logger.info(f"Updated permission: {permission_key}")
            else:
                self.skipped_count += 1
                logger.debug(f"Skipped existing permission: {permission_key}")
        else:
            # Create new permission
            new_permission = ServicePermission(
                permission_key=permission_key,
                display_name=display_name,
                description=description,
                module=module,
                action=action,
                is_active=True
            )
            self.db.add(new_permission)
            self.db.commit()
            self.created_count += 1
            logger.info(f"Created permission: {permission_key}")
    
    def seed_all_permissions(self):
        """Seed all permissions in dotted format"""
        permissions = self.get_all_dotted_permissions()
        
        for permission_key, display_name, description in permissions:
            self.seed_permission(permission_key, display_name, description)
        
        logger.info(
            f"Permission seeding complete: {self.created_count} created, "
            f"{self.updated_count} updated, {self.skipped_count} skipped"
        )
    
    def create_legacy_mappings(self):
        """
        Create mappings for legacy permissions (informational only).
        This is handled in code via LEGACY_PERMISSION_MAP.
        """
        logger.info(f"Legacy permission mappings available: {len(LEGACY_PERMISSION_MAP)} mappings")
        for legacy, dotted in LEGACY_PERMISSION_MAP.items():
            logger.debug(f"Legacy mapping: {legacy} -> {dotted}")


def seed_permissions(db: Session) -> Dict[str, int]:
    """
    Main entry point for permission seeding.
    
    Args:
        db: Database session
        
    Returns:
        Dictionary with seeding statistics
    """
    logger.info("Starting permission seeding...")
    
    seeder = PermissionSeeder(db)
    seeder.seed_all_permissions()
    seeder.create_legacy_mappings()
    
    stats = {
        "created": seeder.created_count,
        "updated": seeder.updated_count,
        "skipped": seeder.skipped_count
    }
    
    logger.info(f"Permission seeding complete: {stats}")
    return stats


if __name__ == "__main__":
    # Can be run standalone for testing
    from app.core.database import SessionLocal
    
    db = SessionLocal()
    try:
        stats = seed_permissions(db)
        print(f"Seeding complete: {stats}")
    finally:
        db.close()
