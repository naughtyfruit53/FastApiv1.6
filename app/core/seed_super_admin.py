"""
Super Admin Seeding Logic (Supabase Auth integrated)

This module seeds the default platform super admin user.
- Super admin is NOT tied to any organization.
- Now creates user in Supabase Auth first, then local DB.
- Handles rollback/cleanup if DB fails.
"""

import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import OperationalError
from sqlalchemy import select, text
from app.core.database import AsyncSessionLocal, Base
from app.models.user_models import User
from app.schemas.user import UserRole
from app.core.security import get_password_hash
from app.utils.supabase_auth import supabase_auth_service, SupabaseAuthError

logger = logging.getLogger(__name__)

async def seed_super_admin(db: AsyncSession = None) -> None:
    """
    Creates a default platform super admin (Supabase Auth integrated).
    Only runs if no super admin exists in the database.

    - Email: naughtyfruit53@gmail.com
    - Password: 123456 (must be changed after login)
    - organization_id: NULL (platform level)
    - role: super_admin
    - is_super_admin: True
    """
    db_session = db
    if db_session is None:
        db_session = AsyncSessionLocal()

    super_admin_email = "naughtyfruit53@gmail.com"
    super_admin_password = "123456"  # This should be changed after first login

    try:
        # Check for existing super admin
        try:
            result = await db_session.execute(
                select(User).filter_by(
                    is_super_admin=True,
                    organization_id=None
                )
            )
            existing_super_admin = result.scalars().first()
            if existing_super_admin:
                # Fix role if needed
                if existing_super_admin.role != UserRole.SUPER_ADMIN.value:
                    logger.warning(f"Super admin role mismatch detected: current role '{existing_super_admin.role}', fixing to 'super_admin'")
                    existing_super_admin.role = UserRole.SUPER_ADMIN.value
                    await db_session.commit()
                    await db_session.refresh(existing_super_admin)
                    logger.info("Super admin role fixed successfully.")
                else:
                    logger.info("Platform super admin already exists with correct role. Skipping seeding.")
                return

        except OperationalError as e:
            if "no such column" in str(e):
                logger.warning("DB schema missing columns (organization_id, is_super_admin). Please run migrations before seeding.")
                return
            else:
                raise

        # 1. Create user in Supabase Auth first
        try:
            supabase_user = supabase_auth_service.create_user(
                email=super_admin_email,
                password=super_admin_password,
                user_metadata={
                    "full_name": "Super Admin",
                    "role": UserRole.SUPER_ADMIN.value,
                    "is_super_admin": True,
                    "organization_id": None
                }
            )
            supabase_uuid = supabase_user["supabase_uuid"]
            logger.info(f"Created platform super admin in Supabase Auth with UUID {supabase_uuid}")

        except SupabaseAuthError as e:
            logger.error(f"Failed to create super admin in Supabase Auth: {e}")
            logger.warning("Super admin seeding aborted (Supabase Auth failure).")
            return
        except Exception as e:
            logger.error(f"Unexpected error creating super admin in Supabase Auth: {e}")
            logger.warning("Super admin seeding aborted (Supabase Auth failure).")
            return

        # 2. Create user in local database
        try:
            hashed_password = get_password_hash(super_admin_password)
            super_admin = User(
                email=super_admin_email,
                hashed_password=hashed_password,
                full_name="Super Admin",
                role=UserRole.SUPER_ADMIN,
                is_super_admin=True,
                is_active=True,
                must_change_password=True,
                organization_id=None,
                supabase_uuid=supabase_uuid
            )
            db_session.add(super_admin)
            await db_session.commit()
            await db_session.refresh(super_admin)
            logger.info(f"Successfully created platform super admin in local DB (email: {super_admin_email})")
            logger.warning("SECURITY: Default super admin created with password '123456'. Please change this password immediately after first login!")

        except Exception as e:
            # If DB creation fails, cleanup Supabase Auth user
            try:
                supabase_auth_service.delete_user(supabase_uuid)
                logger.info(f"Rolled back Supabase Auth user {supabase_uuid} after DB failure")
            except Exception as cleanup_error:
                logger.error(f"Failed to cleanup Supabase user {supabase_uuid}: {cleanup_error}")

            await db_session.rollback()
            logger.error(f"Failed to create super admin in local DB: {e}")
            raise

    finally:
        if db is None:
            await db_session.close()

async def check_super_admin_exists(db: AsyncSession = None) -> bool:
    """
    Check if a platform super admin exists.
    Returns: bool
    """
    db_session = db
    if db_session is None:
        db_session = AsyncSessionLocal()
    try:
        try:
            result = await db_session.execute(
                select(User).filter_by(
                    is_super_admin=True,
                    organization_id=None
                )
            )
            super_admin = result.scalars().first()
            return super_admin is not None

        except OperationalError as e:
            if "no such column" in str(e):
                logger.warning("Database schema is outdated. Cannot check for super admin existence.")
                return False
            else:
                raise

    except Exception as e:
        logger.error(f"Failed to check super admin existence: {e}")
        return False
    finally:
        if db is None:
            await db_session.close()

async def check_database_schema_updated(db: AsyncSession = None) -> bool:
    """
    Check if the database schema has been updated with organization support.
    Returns: bool
    """
    db_session = db
    if db_session is None:
        db_session = AsyncSessionLocal()
    try:
        await db_session.execute(text("SELECT organization_id, is_super_admin FROM users LIMIT 1"))
        return True
    except OperationalError:
        return False
    except Exception:
        return False
    finally:
        if db is None:
            await db_session.close()

if __name__ == "__main__":
    import asyncio
    asyncio.run(seed_super_admin())