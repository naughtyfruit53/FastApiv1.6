# seed_voucher_templates.py

import asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal
from app.models.organization_settings import VoucherFormatTemplate

async def seed_templates():
    async with AsyncSessionLocal() as session:
        async with session.begin():
            # Check if templates exist
            result = await session.execute(select(VoucherFormatTemplate))
            existing = result.scalars().all()
            if existing:
                print("Templates already seeded.")
                return

            # Standard
            standard = VoucherFormatTemplate(
                name="Standard",
                description="Classic business template with balanced layout and professional look.",
                template_config={"layout": "standard", "font": "sans-serif", "color_scheme": "blue"},
                is_system_template=True
            )
            session.add(standard)

            # Modern
            modern = VoucherFormatTemplate(
                name="Modern",
                description="Contemporary design with clean lines and modern typography.",
                template_config={"layout": "modern", "font": "serif", "color_scheme": "green"},
                is_system_template=True
            )
            session.add(modern)

            # Classic
            classic = VoucherFormatTemplate(
                name="Classic",
                description="Traditional formal template with elegant styling.",
                template_config={"layout": "classic", "font": "serif", "color_scheme": "black"},
                is_system_template=True
            )
            session.add(classic)

            # Minimal
            minimal = VoucherFormatTemplate(
                name="Minimal",
                description="Clean and simple design focusing on essential information.",
                template_config={"layout": "minimal", "font": "sans-serif", "color_scheme": "gray"},
                is_system_template=True
            )
            session.add(minimal)

            await session.commit()
            print("Seeded 4 voucher templates.")

if __name__ == "__main__":
    asyncio.run(seed_templates())