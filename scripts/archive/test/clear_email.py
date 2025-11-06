# scripts/clear_emails.py

"""
Script to clear all emails from the database for a full resync.
Run this script manually to delete all emails, then call /sync with force_sync=True.
"""

from sqlalchemy import create_engine, delete
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.mail_management import Email

# Database connection
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def clear_emails():
    db = SessionLocal()
    try:
        # Delete all emails
        stmt = delete(Email)
        result = db.execute(stmt)
        db.commit()
        print(f"Deleted {result.rowcount} emails.")
    except Exception as e:
        db.rollback()
        print(f"Error clearing emails: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    clear_emails()