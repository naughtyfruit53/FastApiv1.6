# scripts/seed_snappymail_config.py

import os
import sys
import logging
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.database import get_db
from app.models.system_models import SnappyMailConfig
from app.models.user_models import User
from sqlalchemy.orm import Session

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_snappymail_config(db: Session):
    # Find the user by email (adjust email if needed)
    user = db.query(User).filter(User.email == 'potymatic@gmail.com').first()
    if not user:
        print("User not found. Update email in script.")
        return

    # Check if config exists
    existing_config = db.query(SnappyMailConfig).filter(SnappyMailConfig.user_id == user.id).first()
    if existing_config:
        print("SnappyMail config already exists for user.")
        return

    # Pull configs from environment variables (secure, avoids hardcoding)
    imap_host = os.getenv('SNAPPYMAIL_IMAP_HOST', 'imap.gmail.com')
    imap_port = int(os.getenv('SNAPPYMAIL_IMAP_PORT', '993'))
    smtp_host = os.getenv('SNAPPYMAIL_SMTP_HOST', 'smtp.gmail.com')
    smtp_port = int(os.getenv('SNAPPYMAIL_SMTP_PORT', '587'))
    use_ssl = os.getenv('SNAPPYMAIL_IMAP_SSL', 'true').lower() == 'true'
    password = os.getenv('SMTP_PASSWORD')  # Use the app password from .env

    if not password:
        print("SMTP_PASSWORD not set in .env. Cannot seed without password.")
        return

    # Create config
    config = SnappyMailConfig(
        user_id=user.id,
        email=user.email,
        imap_host=imap_host,
        imap_port=imap_port,
        smtp_host=smtp_host,
        smtp_port=smtp_port,
        use_ssl=use_ssl,
        password=password
    )
    db.add(config)
    db.commit()
    print(f"SnappyMail config seeded for user ID {user.id}!")

if __name__ == "__main__":
    db = next(get_db())
    seed_snappymail_config(db)