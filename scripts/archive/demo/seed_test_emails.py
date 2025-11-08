# app/scripts/seed_test_emails.py

from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.mail_management import Email, EmailStatus
from app.models.oauth_models import UserEmailToken  # Assuming you have a token to associate

# Setup database connection
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def seed_test_emails():
    db = SessionLocal()
    try:
        # Assume organization_id=1, account_id=1 (replace with actual IDs from your DB)
        org_id = 1
        account_id = 1  # From your connected Gmail token

        now = datetime.utcnow()
        this_week_start = now - timedelta(days=now.weekday())  # Monday of this week
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)

        # Clear existing emails for clean test (optional - comment if not needed)
        # db.query(Email).filter(Email.organization_id == org_id).delete()

        # Seed 5 unread emails this week
        for i in range(5):
            email = Email(
                message_id=f"test_unread_{i}",
                thread_id=f"thread_{i}",
                subject=f"Unread Test Email {i}",
                from_address="test@sender.com",
                to_addresses=["user@receiver.com"],
                sent_at=this_week_start + timedelta(days=i),
                received_at=this_week_start + timedelta(days=i),
                body_text="This is a test unread email.",
                status=EmailStatus.UNREAD,
                folder="INBOX",
                account_id=account_id,
                organization_id=org_id
            )
            db.add(email)

        # Seed 10 read emails this week
        for i in range(10):
            email = Email(
                message_id=f"test_read_{i}",
                thread_id=f"thread_read_{i}",
                subject=f"Read Test Email {i}",
                from_address="test@sender.com",
                to_addresses=["user@receiver.com"],
                sent_at=this_week_start + timedelta(days=i % 7),
                received_at=this_week_start + timedelta(days=i % 7),
                body_text="This is a test read email.",
                status=EmailStatus.READ,
                folder="INBOX",
                account_id=account_id,
                organization_id=org_id
            )
            db.add(email)

        # Seed 3 emails today (unread)
        for i in range(3):
            email = Email(
                message_id=f"test_today_{i}",
                thread_id=f"thread_today_{i}",
                subject=f"Today Test Email {i}",
                from_address="test@sender.com",
                to_addresses=["user@receiver.com"],
                sent_at=today + timedelta(hours=i),
                received_at=today + timedelta(hours=i),
                body_text="This is a test email from today.",
                status=EmailStatus.UNREAD,
                folder="INBOX",
                account_id=account_id,
                organization_id=org_id
            )
            db.add(email)

        db.commit()
        print("Seeded 15 emails this week (5 unread, 10 read), including 3 unread today.")

    except Exception as e:
        db.rollback()
        print(f"Error seeding emails: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_test_emails()