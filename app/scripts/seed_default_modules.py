"""
Script to update existing organizations with default enabled_modules.
Run this once: python seed_default_modules.py
Requires database connection - adjust credentials if needed.
"""
import asyncio
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, select, update
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import json # For potential JSON handling if needed
from app.models.user_models import Organization # Adjusted import
from app.core.modules_registry import get_default_enabled_modules
# Database URL - from your .env or hardcode for one-time run
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL") # Change to your DB
async def update_existing_orgs():
    engine = create_async_engine(DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
   
    async with async_session() as session:
        # Get all organizations
        stmt = select(Organization)
        result = await session.execute(stmt)
        orgs = result.scalars().all()
       
        defaults = get_default_enabled_modules()
       
        for org in orgs:
            if not org.enabled_modules or len(org.enabled_modules) == 0:
                print(f"Updating org {org.id} ({org.name}) with default modules")
                org.enabled_modules = defaults
            else:
                # Merge defaults - enable any missing
                updated = {**defaults, **org.enabled_modules}
                if updated != org.enabled_modules:
                    print(f"Merging defaults for org {org.id} ({org.name})")
                    org.enabled_modules = updated
       
        await session.commit()
        print(f"Updated {len(orgs)} organizations")
if __name__ == "__main__":
    asyncio.run(update_existing_orgs())