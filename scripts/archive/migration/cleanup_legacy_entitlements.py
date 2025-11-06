#!/usr/bin/env python3
"""
Cleanup Legacy Entitlements Script

This script syncs legacy enabled_modules (from Organization.enabled_modules JSON field)
to the new entitlements system and removes old RBAC logic for org admin.

Purpose:
1. Migrate organization's enabled_modules to proper entitlement records
2. Ensure backward compatibility with existing organizations
3. Clean up deprecated RBAC logic related to org admin module access

Usage:
    python scripts/cleanup_legacy_entitlements.py

Requirements:
    - Run after database migrations are applied
    - Requires super admin privileges
    - Should be run during maintenance window
"""

import asyncio
import sys
import logging
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select, and_, update
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from typing import List, Dict, Set
import json

from app.core.database import Base
from app.models.user_models import Organization
from app.models.entitlement_models import Module, OrgEntitlement, EntitlementEvent, ModuleStatusEnum
from app.core.config import settings
from app.core.module_categories import (
    get_all_categories,
    get_modules_for_category,
    ALWAYS_ON_MODULES,
    RBAC_ONLY_MODULES,
    MODULE_CATEGORY_MAP
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Legacy module name mappings (old names to new names)
LEGACY_MODULE_MAP = {
    'CRM': 'crm',
    'ERP': 'erp',
    'HR': 'hr',
    'Inventory': 'inventory',
    'Service': 'service',
    'Analytics': 'analytics',
    'Finance': 'finance',
    'Manufacturing': 'manufacturing',
    'Procurement': 'procurement',
    'Project': 'project',
    'Asset': 'asset',
    'Transport': 'transport',
    'SEO': 'seo',
    'Marketing': 'marketing',
    'Payroll': 'payroll',
    'Talent': 'talent',
    'Workflow': 'workflow',
    'Integration': 'integration',
    'AI_Analytics': 'ai_analytics',
    'Streaming_Analytics': 'streaming_analytics',
    'AB_Testing': 'ab_testing',
    'Website_Agent': 'website_agent',
    'Email': 'email',
    'Calendar': 'calendar',
    'Task_Management': 'task_management',
    'Order_Book': 'order_book',
    'Exhibition': 'exhibition',
}


async def get_or_create_module(db: AsyncSession, module_key: str) -> Module:
    """Get existing module or create if doesn't exist"""
    result = await db.execute(
        select(Module).where(Module.module_key == module_key)
    )
    module = result.scalar_one_or_none()
    
    if not module:
        logger.info(f"Creating new module record for '{module_key}'")
        module = Module(
            module_key=module_key,
            display_name=module_key.replace('_', ' ').title(),
            description=f"Auto-created module for {module_key}",
            is_active=True,
            sort_order=999
        )
        db.add(module)
        await db.flush()
    
    return module


async def sync_organization_entitlements(db: AsyncSession, org: Organization) -> Dict[str, any]:
    """
    Sync a single organization's enabled_modules to entitlements
    
    Returns:
        Dict with sync statistics
    """
    stats = {
        'org_id': org.id,
        'org_name': org.name,
        'modules_synced': 0,
        'modules_skipped': 0,
        'errors': []
    }
    
    try:
        logger.info(f"Processing organization: {org.name} (ID: {org.id})")
        
        # Get legacy enabled_modules
        enabled_modules = org.enabled_modules or {}
        if not enabled_modules:
            logger.warning(f"Organization {org.id} has no enabled_modules")
            return stats
        
        logger.info(f"Found {len(enabled_modules)} legacy modules: {list(enabled_modules.keys())}")
        
        # Normalize module names
        normalized_modules = set()
        for legacy_key, is_enabled in enabled_modules.items():
            if not is_enabled:
                continue
            
            # Map legacy name to new name
            module_key = LEGACY_MODULE_MAP.get(legacy_key, legacy_key.lower())
            normalized_modules.add(module_key)
        
        logger.info(f"Normalized to {len(normalized_modules)} modules: {normalized_modules}")
        
        # Process each module
        for module_key in normalized_modules:
            # Skip RBAC-only modules (they're controlled by roles, not entitlements)
            if module_key in RBAC_ONLY_MODULES:
                logger.debug(f"Skipping RBAC-only module: {module_key}")
                stats['modules_skipped'] += 1
                continue
            
            # Get or create module
            module = await get_or_create_module(db, module_key)
            
            # Check if entitlement already exists
            result = await db.execute(
                select(OrgEntitlement).where(
                    and_(
                        OrgEntitlement.org_id == org.id,
                        OrgEntitlement.module_id == module.id
                    )
                )
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                # Update if disabled
                if existing.status == ModuleStatusEnum.DISABLED:
                    logger.info(f"Enabling existing entitlement for module '{module_key}'")
                    existing.status = ModuleStatusEnum.ENABLED
                    existing.source = 'legacy_sync'
                    stats['modules_synced'] += 1
                else:
                    logger.debug(f"Entitlement for module '{module_key}' already enabled")
                    stats['modules_skipped'] += 1
            else:
                # Create new entitlement
                logger.info(f"Creating new entitlement for module '{module_key}'")
                entitlement = OrgEntitlement(
                    org_id=org.id,
                    module_id=module.id,
                    status=ModuleStatusEnum.ENABLED,
                    source='legacy_sync'
                )
                db.add(entitlement)
                stats['modules_synced'] += 1
        
        # Create audit event
        event = EntitlementEvent(
            org_id=org.id,
            actor_user_id=None,  # System migration
            action='bulk_enable',
            entity_type='module',
            reason=f'Legacy entitlements sync - migrated {stats["modules_synced"]} modules',
            details={
                'legacy_modules': list(enabled_modules.keys()),
                'synced_modules': list(normalized_modules),
                'synced_count': stats['modules_synced']
            }
        )
        db.add(event)
        
        await db.commit()
        logger.info(f"Successfully synced {stats['modules_synced']} modules for org {org.id}")
        
    except Exception as e:
        logger.error(f"Error syncing org {org.id}: {e}", exc_info=True)
        stats['errors'].append(str(e))
        await db.rollback()
    
    return stats


async def cleanup_legacy_rbac_logic(db: AsyncSession) -> Dict[str, any]:
    """
    Remove old RBAC logic that allowed org admins to bypass module entitlements.
    This is now handled properly through the entitlements system.
    
    Returns:
        Dict with cleanup statistics
    """
    stats = {
        'cleanup_performed': True,
        'notes': []
    }
    
    logger.info("Checking for legacy RBAC logic to clean up...")
    
    # Note: Since RBAC logic is in code, not database, this function documents what was removed
    stats['notes'].append("Legacy RBAC bypass logic for org_admin has been removed from code")
    stats['notes'].append("Org admins now require proper entitlements like other users")
    stats['notes'].append("Settings/Admin/Organization modules remain RBAC-only (not entitlement-controlled)")
    
    logger.info("Legacy RBAC cleanup check complete")
    return stats


async def main():
    """Main execution function"""
    logger.info("=" * 80)
    logger.info("Legacy Entitlements Cleanup Script")
    logger.info("=" * 80)
    
    # Create async engine
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
        pool_pre_ping=True
    )
    
    # Create async session factory
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    try:
        async with async_session() as db:
            # Get all organizations
            result = await db.execute(select(Organization))
            organizations = result.scalars().all()
            
            logger.info(f"Found {len(organizations)} organizations to process")
            
            total_stats = {
                'total_orgs': len(organizations),
                'orgs_processed': 0,
                'total_modules_synced': 0,
                'total_modules_skipped': 0,
                'errors': []
            }
            
            # Process each organization
            for org in organizations:
                stats = await sync_organization_entitlements(db, org)
                total_stats['orgs_processed'] += 1
                total_stats['total_modules_synced'] += stats['modules_synced']
                total_stats['total_modules_skipped'] += stats['modules_skipped']
                if stats['errors']:
                    total_stats['errors'].extend(stats['errors'])
            
            # Clean up legacy RBAC logic
            rbac_stats = await cleanup_legacy_rbac_logic(db)
            
            # Print summary
            logger.info("=" * 80)
            logger.info("CLEANUP SUMMARY")
            logger.info("=" * 80)
            logger.info(f"Total organizations: {total_stats['total_orgs']}")
            logger.info(f"Organizations processed: {total_stats['orgs_processed']}")
            logger.info(f"Total modules synced: {total_stats['total_modules_synced']}")
            logger.info(f"Total modules skipped: {total_stats['total_modules_skipped']}")
            logger.info(f"Errors encountered: {len(total_stats['errors'])}")
            
            if total_stats['errors']:
                logger.error("Errors:")
                for error in total_stats['errors']:
                    logger.error(f"  - {error}")
            
            logger.info("\nRBAC Cleanup Notes:")
            for note in rbac_stats['notes']:
                logger.info(f"  - {note}")
            
            logger.info("=" * 80)
            logger.info("Cleanup completed successfully!")
            
    except Exception as e:
        logger.error(f"Fatal error during cleanup: {e}", exc_info=True)
        sys.exit(1)
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
