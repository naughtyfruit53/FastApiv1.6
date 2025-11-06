#!/usr/bin/env python3
"""
Unified Database Seeding Script

This script seeds all essential baseline data required for proper system operation:
1. Super admin user
2. Module and submodule taxonomy (entitlements)
3. RBAC permissions, roles, and default assignments
4. Default Chart of Accounts structure
5. Voucher format templates
6. Default organization modules

This script is idempotent and can be safely run multiple times.
It will only create data that doesn't already exist.

Usage:
    python scripts/seed_all.py [--skip-check]

Options:
    --skip-check    Skip the check for existing data and force seeding
"""

import sys
import os
import asyncio
import argparse
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal
from app.models.user_models import User, Organization
from app.models.entitlement_models import Module, Submodule
from app.models.rbac_models import ServicePermission, ServiceRole
from app.models.organization_settings import VoucherFormatTemplate
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def check_if_seeding_needed(db: AsyncSession) -> bool:
    """
    Check if database needs seeding by looking for essential baseline data.
    Returns True if seeding is needed, False otherwise.
    """
    try:
        # Check for super admin
        result = await db.execute(
            select(User).where(User.is_super_admin == True).limit(1)
        )
        if not result.scalar_one_or_none():
            logger.info("No super admin found - seeding needed")
            return True
        
        # Check for modules
        result = await db.execute(select(Module).limit(1))
        if not result.scalar_one_or_none():
            logger.info("No modules found - seeding needed")
            return True
        
        # Check for RBAC permissions
        result = await db.execute(select(ServicePermission).limit(1))
        if not result.scalar_one_or_none():
            logger.info("No RBAC permissions found - seeding needed")
            return True
        
        # Check for voucher templates
        result = await db.execute(
            select(VoucherFormatTemplate).where(
                VoucherFormatTemplate.is_system_template == True
            ).limit(1)
        )
        if not result.scalar_one_or_none():
            logger.info("No voucher templates found - seeding needed")
            return True
        
        logger.info("All baseline data exists - seeding not needed")
        return False
        
    except Exception as e:
        logger.warning(f"Error checking seeding status: {e}")
        # If there's an error (e.g., table doesn't exist), we should seed
        return True


async def seed_super_admin(db: AsyncSession):
    """Seed super admin user"""
    logger.info("=" * 60)
    logger.info("Step 1: Seeding Super Admin")
    logger.info("=" * 60)
    
    try:
        from app.core.seed_super_admin import seed_super_admin as _seed_super_admin
        await _seed_super_admin(db)
        logger.info("✓ Super admin seeding completed")
    except Exception as e:
        logger.error(f"✗ Error seeding super admin: {e}")
        raise


async def seed_modules_and_entitlements(db: AsyncSession):
    """Seed module and submodule taxonomy"""
    logger.info("=" * 60)
    logger.info("Step 2: Seeding Modules and Entitlements")
    logger.info("=" * 60)
    
    try:
        from app.services.entitlement_service import EntitlementService
        service = EntitlementService(db)
        
        # Seed all modules and submodules
        created = await service.seed_all_modules()
        logger.info(f"✓ Seeded {created} modules/submodules")
        
        # Sync enabled modules for existing organizations
        orgs = (await db.execute(select(Organization))).scalars().all()
        for org in orgs:
            synced = await service.sync_enabled_modules(org.id)
            logger.info(f"✓ Synced enabled_modules for org {org.id}: {synced}")
        
    except Exception as e:
        logger.error(f"✗ Error seeding modules: {e}")
        raise


async def seed_rbac_permissions(db: AsyncSession):
    """Seed RBAC permissions and default roles"""
    logger.info("=" * 60)
    logger.info("Step 3: Seeding RBAC Permissions")
    logger.info("=" * 60)
    
    try:
        from app.services.rbac import RBACService
        rbac = RBACService(db)
        
        # Initialize default permissions
        await rbac.initialize_default_permissions()
        logger.info("✓ Default permissions initialized")
        
        # Initialize roles for existing organizations
        orgs = (await db.execute(select(Organization))).scalars().all()
        for org in orgs:
            roles = await rbac.get_roles(org.id)
            if not roles:
                await rbac.initialize_default_roles(org.id)
                logger.info(f"✓ Initialized default roles for org {org.id}")
        
    except Exception as e:
        logger.error(f"✗ Error seeding RBAC: {e}")
        raise


async def seed_chart_of_accounts(db: AsyncSession):
    """Seed default Chart of Accounts"""
    logger.info("=" * 60)
    logger.info("Step 4: Seeding Chart of Accounts")
    logger.info("=" * 60)
    
    try:
        # Import and run the CoA seeding script
        from app.scripts.seed_default_coa_accounts import seed_default_coa
        
        # Get organizations that need CoA
        orgs = (await db.execute(select(Organization))).scalars().all()
        
        if orgs:
            for org in orgs:
                logger.info(f"Seeding CoA for org {org.id} - {org.name}")
                await seed_default_coa(db, org.id)
            logger.info("✓ Chart of Accounts seeding completed")
        else:
            logger.info("No organizations found - skipping CoA seeding")
            
    except Exception as e:
        logger.warning(f"⚠ Error seeding Chart of Accounts: {e}")
        logger.warning("This is optional - continuing with other seeds...")


async def seed_voucher_templates(db: AsyncSession):
    """Seed system voucher format templates"""
    logger.info("=" * 60)
    logger.info("Step 5: Seeding Voucher Templates")
    logger.info("=" * 60)
    
    try:
        # Check if templates already exist
        stmt = select(VoucherFormatTemplate).where(
            VoucherFormatTemplate.is_system_template == True
        )
        result = await db.execute(stmt)
        existing_templates = result.scalars().all()
        
        if existing_templates:
            logger.info(f"Found {len(existing_templates)} existing system templates - skipping")
            return
        
        # Create system templates
        templates = [
            {
                "name": "Standard (Default)",
                "description": "Classic professional look with clean borders and structured layout",
                "template_config": {
                    "layout": "standard",
                    "header": {"show_logo": True},
                    "colors": {"primary": "#222222"},
                    "fonts": {"heading": "Segoe UI", "body": "Segoe UI"},
                    "sections": {"show_items_table": True, "show_bank_details": True, "show_terms": True}
                },
                "is_system_template": True,
                "is_active": True
            },
            {
                "name": "Modern",
                "description": "Contemporary design with gradient accents and rounded corners",
                "template_config": {
                    "layout": "modern",
                    "header": {"show_logo": True},
                    "colors": {"primary": "#667eea", "secondary": "#764ba2"},
                    "fonts": {"heading": "Segoe UI", "body": "Segoe UI"},
                    "sections": {"show_items_table": True, "show_bank_details": True, "show_terms": True}
                },
                "is_system_template": True,
                "is_active": True
            },
            {
                "name": "Classic",
                "description": "Traditional serif font design with heavy borders",
                "template_config": {
                    "layout": "classic",
                    "header": {"show_logo": True},
                    "colors": {"primary": "#1a1a1a"},
                    "fonts": {"heading": "Georgia", "body": "Times New Roman"},
                    "sections": {"show_items_table": True, "show_bank_details": True, "show_terms": True}
                },
                "is_system_template": True,
                "is_active": True
            },
            {
                "name": "Minimal",
                "description": "Clean and minimalist design with subtle borders",
                "template_config": {
                    "layout": "minimal",
                    "header": {"show_logo": True},
                    "colors": {"primary": "#0066cc"},
                    "fonts": {"heading": "Helvetica Neue", "body": "Arial"},
                    "sections": {"show_items_table": True, "show_bank_details": True, "show_terms": True}
                },
                "is_system_template": True,
                "is_active": True
            }
        ]
        
        for template_data in templates:
            template = VoucherFormatTemplate(**template_data)
            db.add(template)
        
        await db.commit()
        logger.info(f"✓ Created {len(templates)} system voucher format templates")
        
    except Exception as e:
        logger.warning(f"⚠ Error seeding voucher templates: {e}")
        logger.warning("This is optional - continuing...")


async def seed_organization_defaults(db: AsyncSession):
    """Backfill default enabled_modules for organizations"""
    logger.info("=" * 60)
    logger.info("Step 6: Setting Organization Defaults")
    logger.info("=" * 60)
    
    try:
        from app.core.modules_registry import get_default_enabled_modules
        
        orgs = (await db.execute(select(Organization))).scalars().all()
        updated_count = 0
        
        for org in orgs:
            if not org.enabled_modules or len(org.enabled_modules) == 0:
                org.enabled_modules = get_default_enabled_modules()
                updated_count += 1
                logger.info(f"✓ Set default modules for org {org.id} - {org.name}")
        
        if updated_count > 0:
            await db.commit()
            logger.info(f"✓ Updated {updated_count} organizations with default modules")
        else:
            logger.info("All organizations already have enabled_modules set")
            
    except Exception as e:
        logger.warning(f"⚠ Error setting organization defaults: {e}")
        logger.warning("This is optional - continuing...")


async def run_seed_all(skip_check: bool = False):
    """Main function to run all seeding operations"""
    logger.info("=" * 60)
    logger.info("UNIFIED DATABASE SEEDING")
    logger.info("=" * 60)
    
    async with AsyncSessionLocal() as db:
        try:
            # Check if seeding is needed
            if not skip_check:
                if not await check_if_seeding_needed(db):
                    logger.info("\n" + "=" * 60)
                    logger.info("Database already has baseline data - no seeding needed")
                    logger.info("Use --skip-check to force seeding")
                    logger.info("=" * 60)
                    return
            
            # Run all seeding steps in order
            await seed_super_admin(db)
            await seed_modules_and_entitlements(db)
            await seed_rbac_permissions(db)
            await seed_chart_of_accounts(db)
            await seed_voucher_templates(db)
            await seed_organization_defaults(db)
            
            logger.info("\n" + "=" * 60)
            logger.info("✓ ALL SEEDING COMPLETED SUCCESSFULLY")
            logger.info("=" * 60)
            logger.info("\nBaseline data seeded:")
            logger.info("  ✓ Super admin user")
            logger.info("  ✓ Module and submodule taxonomy")
            logger.info("  ✓ RBAC permissions and roles")
            logger.info("  ✓ Chart of Accounts (if orgs exist)")
            logger.info("  ✓ Voucher format templates")
            logger.info("  ✓ Organization default modules")
            logger.info("=" * 60)
            
        except Exception as e:
            logger.error("\n" + "=" * 60)
            logger.error(f"✗ SEEDING FAILED: {e}")
            logger.error("=" * 60)
            await db.rollback()
            raise


def main():
    """Entry point for the script"""
    parser = argparse.ArgumentParser(
        description='Unified database seeding script',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument(
        '--skip-check',
        action='store_true',
        help='Skip check for existing data and force seeding'
    )
    
    args = parser.parse_args()
    
    try:
        asyncio.run(run_seed_all(skip_check=args.skip_check))
    except KeyboardInterrupt:
        logger.info("\nSeeding interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
