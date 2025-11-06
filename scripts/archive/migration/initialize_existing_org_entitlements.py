#!/usr/bin/env python3
"""
Initialize entitlements for existing organizations.

Run this ONCE after applying entitlement migrations to production.
This script creates org_entitlement records for organizations that
existed before the entitlement system was implemented.
"""

import asyncio
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import async_session_maker
from app.models.user_models import Organization
from app.models.rbac_models import Module, OrgEntitlement
from app.core.constants import ModuleStatusEnum, ALWAYS_ON_MODULES
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def initialize_org_entitlements():
    """Initialize entitlements for existing organizations"""
    
    async with async_session_maker() as db:
        try:
            # Get all organizations
            logger.info("Fetching organizations...")
            result = await db.execute(select(Organization))
            orgs = result.scalars().all()
            
            if not orgs:
                logger.warning("⚠️  No organizations found!")
                return
            
            logger.info(f"Found {len(orgs)} organizations")
            
            # Get all modules
            logger.info("Fetching modules...")
            result = await db.execute(select(Module))
            modules = result.scalars().all()
            
            if not modules:
                logger.error("❌ No modules found! Run seed_entitlements.py first.")
                return
            
            logger.info(f"Found {len(modules)} modules")
            logger.info(f"Always-on modules: {ALWAYS_ON_MODULES}")
            
            # Statistics
            total_created = 0
            total_skipped = 0
            
            for org in orgs:
                logger.info(f"\n{'='*60}")
                logger.info(f"Processing: {org.name} (ID: {org.id})")
                logger.info(f"{'='*60}")
                
                # Get org's enabled_modules (from JSON field)
                enabled_modules = org.enabled_modules or {}
                logger.info(f"Enabled modules in org settings: {list(enabled_modules.keys())}")
                
                org_created = 0
                org_skipped = 0
                
                for module in modules:
                    # Check if entitlement already exists
                    result = await db.execute(
                        select(OrgEntitlement).where(
                            OrgEntitlement.org_id == org.id,
                            OrgEntitlement.module_id == module.id
                        )
                    )
                    existing = result.scalars().first()
                    
                    if existing:
                        logger.debug(f"  ⏭️  {module.module_key}: Already exists (status: {existing.status})")
                        org_skipped += 1
                        continue
                    
                    # Determine status from org.enabled_modules
                    # Check multiple case variations
                    module_key_lower = module.module_key.lower()
                    module_key_upper = module.module_key.upper()
                    module_key_title = module.module_key.title()
                    
                    is_enabled = (
                        enabled_modules.get(module_key_lower, False) or
                        enabled_modules.get(module_key_upper, False) or
                        enabled_modules.get(module_key_title, False) or
                        enabled_modules.get(module.module_key, False)  # Exact match
                    )
                    
                    # Determine status
                    if module_key_lower in ALWAYS_ON_MODULES:
                        # Always-on modules are always enabled
                        status = ModuleStatusEnum.ENABLED
                        reason = "always-on"
                    elif is_enabled:
                        # Module is enabled in org settings
                        status = ModuleStatusEnum.ENABLED
                        reason = "org-enabled"
                    else:
                        # Module is not enabled in org settings
                        status = ModuleStatusEnum.DISABLED
                        reason = "org-disabled"
                    
                    # Create entitlement
                    entitlement = OrgEntitlement(
                        org_id=org.id,
                        module_id=module.id,
                        status=status.value,
                        source='migration',
                        trial_expires_at=None  # No trial for migrated orgs
                    )
                    db.add(entitlement)
                    
                    logger.info(f"  ✅ {module.module_key}: Created ({status.value}) - {reason}")
                    org_created += 1
                
                # Commit after each org
                try:
                    await db.commit()
                    logger.info(f"✅ Committed changes for {org.name}")
                    logger.info(f"   Created: {org_created}, Skipped: {org_skipped}")
                    total_created += org_created
                    total_skipped += org_skipped
                except Exception as e:
                    logger.error(f"❌ Failed to commit for {org.name}: {e}")
                    await db.rollback()
                    raise
            
            # Final summary
            logger.info(f"\n{'='*60}")
            logger.info("✅ Entitlement initialization complete!")
            logger.info(f"{'='*60}")
            logger.info(f"Organizations processed: {len(orgs)}")
            logger.info(f"Entitlements created: {total_created}")
            logger.info(f"Entitlements skipped (already exist): {total_skipped}")
            logger.info(f"{'='*60}\n")
            
        except Exception as e:
            logger.error(f"❌ Error initializing entitlements: {e}", exc_info=True)
            await db.rollback()
            raise


async def verify_entitlements():
    """Verify entitlements were created correctly"""
    
    async with async_session_maker() as db:
        logger.info("\n🔍 Verifying entitlements...")
        
        # Count organizations
        result = await db.execute(select(Organization))
        org_count = len(result.scalars().all())
        
        # Count modules
        result = await db.execute(select(Module))
        module_count = len(result.scalars().all())
        
        # Count entitlements
        result = await db.execute(select(OrgEntitlement))
        entitlement_count = len(result.scalars().all())
        
        expected = org_count * module_count
        
        logger.info(f"Organizations: {org_count}")
        logger.info(f"Modules: {module_count}")
        logger.info(f"Entitlements: {entitlement_count}")
        logger.info(f"Expected: {expected}")
        
        if entitlement_count >= expected:
            logger.info("✅ Verification passed!")
        else:
            logger.warning(f"⚠️  Missing {expected - entitlement_count} entitlements")
        
        # Sample check - first org
        result = await db.execute(select(Organization).limit(1))
        first_org = result.scalars().first()
        
        if first_org:
            result = await db.execute(
                select(OrgEntitlement).where(OrgEntitlement.org_id == first_org.id)
            )
            org_entitlements = result.scalars().all()
            
            logger.info(f"\nSample org: {first_org.name}")
            logger.info(f"Entitlements: {len(org_entitlements)}")
            
            enabled = [e for e in org_entitlements if e.status == ModuleStatusEnum.ENABLED.value]
            disabled = [e for e in org_entitlements if e.status == ModuleStatusEnum.DISABLED.value]
            
            logger.info(f"  Enabled: {len(enabled)}")
            logger.info(f"  Disabled: {len(disabled)}")


async def main():
    """Main entry point"""
    try:
        logger.info("="*60)
        logger.info("Organization Entitlement Initialization")
        logger.info("="*60)
        logger.info("")
        logger.info("This script will:")
        logger.info("1. Find all existing organizations")
        logger.info("2. Create entitlement records based on enabled_modules")
        logger.info("3. Skip organizations that already have entitlements")
        logger.info("")
        logger.info("⚠️  This should only be run ONCE after migration")
        logger.info("")
        
        # Prompt for confirmation
        response = input("Continue? (yes/no): ")
        if response.lower() != 'yes':
            logger.info("Aborted by user")
            return
        
        # Initialize
        await initialize_org_entitlements()
        
        # Verify
        await verify_entitlements()
        
        logger.info("\n✅ Script completed successfully!")
        
    except KeyboardInterrupt:
        logger.info("\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n❌ Script failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
