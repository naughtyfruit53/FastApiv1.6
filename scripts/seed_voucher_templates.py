"""
Seed script to create system voucher format templates
"""
import asyncio
import sys
import os

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db_context
from app.models.organization_settings import VoucherFormatTemplate


async def seed_voucher_templates():
    """Create system voucher format templates"""
    async with get_db_context() as db:
        # Check if templates already exist
        stmt = select(VoucherFormatTemplate).where(
            VoucherFormatTemplate.is_system_template == True
        )
        result = await db.execute(stmt)
        existing_templates = result.scalars().all()
        
        if existing_templates:
            print(f"Found {len(existing_templates)} existing system templates. Skipping...")
            return
        
        # Create three system templates
        templates = [
            {
                "name": "Standard (Default)",
                "description": "Classic professional look with clean borders and structured layout. Best for formal business communications.",
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
                "description": "Contemporary design with gradient accents and rounded corners. Perfect for modern businesses and startups.",
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
                "description": "Traditional serif font design with heavy borders. Ideal for established companies preferring a formal appearance.",
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
                "description": "Clean and minimalist design with subtle borders. Great for service-based businesses and modern aesthetics.",
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
        print(f"✅ Created {len(templates)} system voucher format templates")
        
        # Display created templates
        stmt = select(VoucherFormatTemplate).where(
            VoucherFormatTemplate.is_system_template == True
        )
        result = await db.execute(stmt)
        created_templates = result.scalars().all()
        
        print("\n📋 Available Templates:")
        for t in created_templates:
            print(f"  - {t.name} (ID: {t.id})")
            print(f"    {t.description}")
            print(f"    Layout: {t.template_config.get('layout')}")
            print()


if __name__ == "__main__":
    print("🚀 Seeding voucher format templates...")
    asyncio.run(seed_voucher_templates())
    print("✅ Done!")
