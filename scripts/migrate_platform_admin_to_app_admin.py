#!/usr/bin/env python3
"""
Migration script to rename platform_admin role to app_admin

This script updates existing platform_admin users to app_admin role.
Run this once after deploying the platform role refactor changes.

Usage:
    python scripts/migrate_platform_admin_to_app_admin.py [--dry-run]

Options:
    --dry-run    Show what would be changed without making changes
"""

import sys
import os
import asyncio
import argparse
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select, update, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal
from app.models.user_models import User, PlatformUser
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def migrate_users_table(db: AsyncSession, dry_run: bool = False) -> int:
    """Migrate platform_admin to app_admin in users table"""
    try:
        # Find users with platform_admin role
        result = await db.execute(
            select(User).where(
                and_(
                    User.role == 'platform_admin',
                    User.organization_id.is_(None)  # Platform-level users only
                )
            )
        )
        users = result.scalars().all()
        
        if not users:
            logger.info("No users with platform_admin role found in users table")
            return 0
        
        logger.info(f"Found {len(users)} user(s) with platform_admin role in users table")
        
        for user in users:
            logger.info(f"  - User ID {user.id}: {user.email} ({user.full_name})")
        
        if dry_run:
            logger.info("DRY RUN: Would update these users to app_admin role")
            return len(users)
        
        # Update the roles
        await db.execute(
            update(User)
            .where(
                and_(
                    User.role == 'platform_admin',
                    User.organization_id.is_(None)
                )
            )
            .values(role='app_admin')
        )
        
        await db.commit()
        logger.info(f"✓ Updated {len(users)} user(s) from platform_admin to app_admin in users table")
        return len(users)
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error migrating users table: {e}")
        raise


async def migrate_platform_users_table(db: AsyncSession, dry_run: bool = False) -> int:
    """Migrate platform_admin to app_admin in platform_users table"""
    try:
        # Find platform users with platform_admin role
        result = await db.execute(
            select(PlatformUser).where(
                PlatformUser.role == 'platform_admin'
            )
        )
        platform_users = result.scalars().all()
        
        if not platform_users:
            logger.info("No users with platform_admin role found in platform_users table")
            return 0
        
        logger.info(f"Found {len(platform_users)} user(s) with platform_admin role in platform_users table")
        
        for user in platform_users:
            logger.info(f"  - PlatformUser ID {user.id}: {user.email} ({user.full_name})")
        
        if dry_run:
            logger.info("DRY RUN: Would update these users to app_admin role")
            return len(platform_users)
        
        # Update the roles
        await db.execute(
            update(PlatformUser)
            .where(PlatformUser.role == 'platform_admin')
            .values(role='app_admin')
        )
        
        await db.commit()
        logger.info(f"✓ Updated {len(platform_users)} user(s) from platform_admin to app_admin in platform_users table")
        return len(platform_users)
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error migrating platform_users table: {e}")
        raise


async def verify_migration(db: AsyncSession) -> bool:
    """Verify that no platform_admin roles remain"""
    try:
        # Check users table
        result = await db.execute(
            select(User).where(
                and_(
                    User.role == 'platform_admin',
                    User.organization_id.is_(None)
                )
            )
        )
        remaining_users = result.scalars().all()
        
        # Check platform_users table
        result = await db.execute(
            select(PlatformUser).where(
                PlatformUser.role == 'platform_admin'
            )
        )
        remaining_platform_users = result.scalars().all()
        
        if remaining_users or remaining_platform_users:
            logger.error(f"✗ Verification failed: Found {len(remaining_users) + len(remaining_platform_users)} users still with platform_admin role")
            return False
        
        logger.info("✓ Verification passed: No platform_admin roles found")
        return True
        
    except Exception as e:
        logger.error(f"Error during verification: {e}")
        return False


async def run_migration(dry_run: bool = False):
    """Main migration function"""
    logger.info("=" * 60)
    logger.info("PLATFORM ROLE MIGRATION: platform_admin → app_admin")
    if dry_run:
        logger.info("DRY RUN MODE - No changes will be made")
    logger.info("=" * 60)
    
    async with AsyncSessionLocal() as db:
        try:
            total_updated = 0
            
            # Migrate users table
            logger.info("\nStep 1: Migrating users table...")
            count = await migrate_users_table(db, dry_run)
            total_updated += count
            
            # Migrate platform_users table
            logger.info("\nStep 2: Migrating platform_users table...")
            count = await migrate_platform_users_table(db, dry_run)
            total_updated += count
            
            if dry_run:
                logger.info("\n" + "=" * 60)
                logger.info(f"DRY RUN COMPLETE: Would update {total_updated} user(s)")
                logger.info("Run without --dry-run to apply changes")
                logger.info("=" * 60)
                return
            
            # Verify migration
            logger.info("\nStep 3: Verifying migration...")
            if await verify_migration(db):
                logger.info("\n" + "=" * 60)
                logger.info(f"✓ MIGRATION COMPLETED SUCCESSFULLY")
                logger.info(f"Total users migrated: {total_updated}")
                logger.info("=" * 60)
            else:
                logger.error("\n" + "=" * 60)
                logger.error("✗ MIGRATION VERIFICATION FAILED")
                logger.error("Please review the logs and retry if needed")
                logger.error("=" * 60)
                sys.exit(1)
            
        except Exception as e:
            logger.error("\n" + "=" * 60)
            logger.error(f"✗ MIGRATION FAILED: {e}")
            logger.error("=" * 60)
            await db.rollback()
            raise


def main():
    """Entry point for the script"""
    parser = argparse.ArgumentParser(
        description='Migrate platform_admin role to app_admin',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be changed without making changes'
    )
    
    args = parser.parse_args()
    
    try:
        asyncio.run(run_migration(dry_run=args.dry_run))
    except KeyboardInterrupt:
        logger.info("\nMigration interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
