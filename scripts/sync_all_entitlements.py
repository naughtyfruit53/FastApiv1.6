#!/usr/bin/env python3
"""
Comprehensive entitlement synchronization script.
Ensures all modules from modules_registry are seeded and all organizations have proper entitlements.
"""

import sys
import os
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from app.core.config import settings
from app.models.entitlement_models import Module, Submodule, OrgEntitlement
from app.models.user_models import Organization
from app.services.entitlement_service import EntitlementService
from app.core.modules_registry import MODULE_SUBMODULES, get_all_modules
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def seed_modules_from_registry(session: AsyncSession):
    """Seed all modules and submodules from modules_registry"""
    logger.info("=" * 60)
    logger.info("Seeding modules and submodules from registry...")
    logger.info("=" * 60)
    
    service = EntitlementService(session)
    created_count = await service.seed_all_modules()
    
    logger.info(f"✓ Seeded {created_count} modules/submodules")
    return created_count


async def sync_organization_entitlements(session: AsyncSession):
    """Sync entitlements for all organizations"""
    logger.info("=" * 60)
    logger.info("Syncing entitlements for all organizations...")
    logger.info("=" * 60)
    
    # Get all organizations
    result = await session.execute(select(Organization))
    organizations = result.scalars().all()
    
    logger.info(f"Found {len(organizations)} organizations")
    
    service = EntitlementService(session)
    synced_orgs = 0
    
    for org in organizations:
        logger.info(f"Processing org {org.id}: {org.name}")
        
        # Ensure entitlements exist for all modules
        await service.get_app_entitlements(org.id)
        
        # Sync enabled_modules
        await service.sync_enabled_modules(org.id)
        
        synced_orgs += 1
        logger.info(f"  ✓ Synced org {org.id}")
    
    logger.info(f"✓ Synced {synced_orgs} organizations")
    return synced_orgs


async def validate_entitlements(session: AsyncSession):
    """Validate entitlement consistency"""
    logger.info("=" * 60)
    logger.info("Validating entitlements...")
    logger.info("=" * 60)
    
    # Check module count
    result = await session.execute(select(Module))
    modules = result.scalars().all()
    logger.info(f"Total modules in database: {len(modules)}")
    
    registry_modules = get_all_modules()
    logger.info(f"Total modules in registry: {len(registry_modules)}")
    
    # Check missing modules
    db_module_keys = {m.module_key.lower() for m in modules}
    missing_modules = [m for m in registry_modules if m.lower() not in db_module_keys]
    
    if missing_modules:
        logger.warning(f"⚠ Missing modules in database: {missing_modules}")
    else:
        logger.info("✓ All registry modules present in database")
    
    # Check submodules
    result = await session.execute(select(Submodule))
    submodules = result.scalars().all()
    logger.info(f"Total submodules in database: {len(submodules)}")
    
    # Check organizations with entitlements
    result = await session.execute(select(Organization))
    orgs = result.scalars().all()
    
    for org in orgs:
        result = await session.execute(
            select(OrgEntitlement).where(OrgEntitlement.org_id == org.id)
        )
        org_ents = result.scalars().all()
        logger.info(f"Org {org.id} ({org.name}): {len(org_ents)} entitlements")
        
        if len(org_ents) < len(modules):
            logger.warning(f"  ⚠ Org {org.id} has fewer entitlements than modules")
    
    logger.info("✓ Validation complete")


async def main():
    """Main synchronization function"""
    logger.info("=" * 60)
    logger.info("Comprehensive Entitlements Synchronization")
    logger.info("=" * 60)
    
    # Create async engine
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        try:
            # Step 1: Seed modules and submodules
            await seed_modules_from_registry(session)
            
            # Step 2: Sync organization entitlements
            await sync_organization_entitlements(session)
            
            # Step 3: Validate
            await validate_entitlements(session)
            
            logger.info("\n" + "=" * 60)
            logger.info("✓ Synchronization completed successfully!")
            logger.info("=" * 60)
            
        except Exception as e:
            await session.rollback()
            logger.error(f"\n❌ Error during synchronization: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
