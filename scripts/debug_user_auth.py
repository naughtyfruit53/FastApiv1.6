"""
Debug script to verify user authentication data, flags, and generate test token
Run this script in the backend environment to check for inconsistencies
Usage: python scripts/debug_user_auth.py <email>
"""

import sys
import os

# Add project root to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.core.security import create_access_token, get_password_hash, verify_token
from app.models.base import User
from app.core.database import Base

# Replace with your actual DB URL if .env not loading
# engine = create_engine("sqlite:///tritiq_erp.db")  # Example for SQLite

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def debug_user(email: str):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            print(f"User with email {email} not found")
            return

        print("\nUser Data:")
        print(f"ID: {user.id}")
        print(f"Email: {user.email}")
        print(f"Username: {user.username}")
        print(f"Organization ID: {user.organization_id}")
        print(f"Role: {user.role}")
        print(f"Is Super Admin: {user.is_super_admin}")
        print(f"Is Active: {user.is_active}")
        print(f"Must Change Password: {user.must_change_password}")
        print(f"Force Password Reset: {user.force_password_reset}")
        print(f"Failed Login Attempts: {user.failed_login_attempts}")
        print(f"Locked Until: {user.locked_until}")
        print(f"Temp Password Expires: {user.temp_password_expires}")
        print(f"Last Login: {user.last_login}")

        if user.must_change_password:
            print("\nWARNING: must_change_password flag is still set - this should be False after successful change")

        # Generate test token
        test_token = create_access_token(
            subject=user.email,
            organization_id=user.organization_id,
            user_role=user.role,
            user_type="organization" if user.organization_id else "platform"
        )
        print("\nGenerated Test Token:")
        print(test_token)

        # Verify the test token
        verified = verify_token(test_token)
        print("\nToken Verification:")
        print(f"Email: {verified[0]}")
        print(f"Org ID: {verified[1]}")
        print(f"Role: {verified[2]}")
        print(f"Type: {verified[3]}")

    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/debug_user_auth.py <user_email>")
        sys.exit(1)
    
    debug_user(sys.argv[1])