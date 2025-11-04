# scripts/migrate_management_modules.py
"""
Standalone script to migrate existing management users' assigned_modules
to match their organization's enabled_modules.

Usage: python migrate_management_modules.py [org_id]
- If org_id provided, migrate only that org
- If none, migrate all orgs
"""

import asyncio
import sys
import logging
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# Adjust import paths based on your app structure (assuming scripts/ is at root)
from app.core.database import AsyncSessionLocal  # Use the factory
from app.models.user_models import Organization
from app.services.user_rbac_service import UserRBACService

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


async def migrate_org(org_id: int, session: AsyncSession) -> None:
    """Migrate a single organization"""
    service = UserRBACService(session)
    updated = await service.migrate_management_modules(org_id)
    logger.info(f"Migrated org {org_id}: {updated} users updated")


async def migrate_all(session: AsyncSession) -> None:
    """Migrate all organizations"""
    orgs_result = await session.execute(select(Organization))
    orgs = orgs_result.scalars().all()
    
    for org in orgs:
        await migrate_org(org.id, session)


async def main(org_id: Optional[int] = None) -> None:
    """Main entry point"""
    async with AsyncSessionLocal() as session:  # Create session from factory
        async with session.begin():  # Use transaction
            if org_id:
                await migrate_org(org_id, session)
            else:
                await migrate_all(session)


if __name__ == "__main__":
    org_id_arg = int(sys.argv[1]) if len(sys.argv) > 1 else None
    asyncio.run(main(org_id_arg))