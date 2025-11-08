# scripts/clean_duplicate_emails.py

"""
Script to clean duplicate emails from the database.
Run this script manually to remove duplicates based on message_id and organization_id.
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings  # Adjust import if needed
from app.core.database import Base  # Ensure Base is imported if needed

# Database connection
engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def clean_duplicates():
    db = SessionLocal()
    try:
        # SQL to delete duplicates, keeping the one with smallest id
        sql = text("""
            DELETE FROM emails
            WHERE id NOT IN (
                SELECT MIN(id)
                FROM emails
                GROUP BY message_id, organization_id
            )
        """)
        result = db.execute(sql)
        db.commit()
        print(f"Deleted {result.rowcount} duplicate emails.")
    except Exception as e:
        db.rollback()
        print(f"Error cleaning duplicates: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    clean_duplicates()