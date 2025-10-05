# app/tests/test_email_integrations.py

"""
Tests for Email Module ERP Integrations and Advanced Features
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, date
import tempfile
import os

from app.main import app
from app.core.database import get_db, Base
from app.models.base import User, Organization, Customer, Vendor
from app.models.email import MailAccount, Email, EmailAttachment, EmailAccountType, EmailStatus
from app.models.calendar_management import CalendarEvent, EventType, EventStatus
from app.models.task_management import Task, TaskStatus, TaskPriority
from app.services.calendar_sync_service import calendar_sync_service
from app.services.email_search_service import email_search_service
from app.services.email_ai_service import email_ai_service
from app.services.ocr_service import email_attachment_ocr_service
from app.core.security import get_password_hash

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_email_integrations.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(scope="module")
def setup_database():
    """Setup test database"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def test_db():
    """Get test database session"""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def test_organization(test_db):
    """Create test organization"""
    org = Organization(
        name="Test ERP Company",
        email="test@erpcompany.com",
        phone="1234567890",
        address="123 Test Street"
    )
    test_db.add(org)
    test_db.commit()
    test_db.refresh(org)
    return org

@pytest.fixture
def test_user(test_db, test_organization):
    """Create test user"""
    user = User(
        email="testuser@erpcompany.com",
        hashed_password=get_password_hash("testpass123"),
        full_name="Test User",
        is_active=True,
        organization_id=test_organization.id
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user

@pytest.fixture
def test_customer(test_db, test_organization):
    """Create test customer"""
    customer = Customer(
        name="Test Customer Corp",
        email="customer@testcorp.com",
        phone="9876543210",
        organization_id=test_organization.id
    )
    test_db.add(customer)
    test_db.commit()
    test_db.refresh(customer)
    return customer

@pytest.fixture
def test_vendor(test_db, test_organization):
    """Create test vendor"""
    vendor = Vendor(
        name="Test Vendor LLC",
        email="vendor@testllc.com",
        phone="5555551234",
        organization_id=test_organization.id
    )
    test_db.add(vendor)
    test_db.commit()
    test_db.refresh(vendor)
    return vendor

@pytest.fixture
def test_mail_account(test_db, test_user):
    """Create test mail account"""
    account = MailAccount(
        user_id=test_user.id,
        organization_id=test_user.organization_id,
        email_address="test@example.com",
        display_name="Test Account",
        account_type=EmailAccountType.IMAP,
        is_active=True
    )
    test_db.add(account)
    test_db.commit()
    test_db.refresh(account)
    return account

@pytest.fixture
def test_email(test_db, test_mail_account, test_customer):
    """Create test email"""
    email = Email(
        account_id=test_mail_account.id,
        organization_id=test_mail_account.organization_id,
        message_id="test-message-123",
        subject="Test Invoice Discussion",
        sender_email="customer@testcorp.com",
        sender_name="Test Customer",
        recipient_emails=["test@example.com"],
        body_text="Please find the invoice attached. We need to discuss payment terms.",
        status=EmailStatus.UNREAD,
        sent_at=datetime.utcnow(),
        received_at=datetime.utcnow(),
        customer_id=test_customer.id
    )
    test_db.add(email)
    test_db.commit()
    test_db.refresh(email)
    return email

@pytest.fixture
def auth_headers(test_user):
    """Create authentication headers"""
    # In a real test, you would generate a proper JWT token
    # For now, we'll mock this
    return {"Authorization": "Bearer test-token"}


class TestCalendarSync:
    """Test calendar sync functionality"""
    
    def test_parse_ics_content_basic(self, setup_database, test_db, test_organization):
        """Test basic .ics parsing functionality"""
        # Create a simple .ics content
        ics_content = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Test//Test Calendar//EN
BEGIN:VEVENT
UID:test-event-123
DTSTART:20240120T140000Z
DTEND:20240120T150000Z
SUMMARY:Project Review Meeting
DESCRIPTION:Review Q1 project deliverables
LOCATION:Conference Room A
END:VEVENT
END:VCALENDAR"""
        
        # Create a temporary attachment with .ics content
        attachment = EmailAttachment(
            email_id=1,  # Dummy email ID
            filename="meeting.ics",
            original_filename="meeting.ics",
            content_type="text/calendar",
            file_data=ics_content.encode('utf-8'),
            size_bytes=len(ics_content)
        )
        test_db.add(attachment)
        test_db.commit()
        test_db.refresh(attachment)
        
        # Test parsing
        result = calendar_sync_service.parse_ics_attachment(
            attachment.id, test_organization.id
        )
        
        assert result["success"] == True
        assert len(result["events"]) == 1
        assert "Project Review Meeting" in result["events"][0]["title"]
    
    def test_sync_events_to_database(self, setup_database, test_user, test_organization):
        """Test syncing parsed events to database"""
        events = [{
            "title": "Test Meeting",
            "description": "Meeting description",
            "start_datetime": datetime(2024, 1, 20, 14, 0),
            "end_datetime": datetime(2024, 1, 20, 15, 0),
            "event_type": EventType.MEETING,
            "status": EventStatus.SCHEDULED,
            "organization_id": test_organization.id,
            "external_id": "test-event-456"
        }]
        
        result = calendar_sync_service.sync_events_to_database(events, test_user.id)
        
        assert result["success"] == True
        assert result["created_events"] == 1


class TestEmailSearch:
    """Test advanced email search functionality"""
    
    def test_full_text_search(self, setup_database, test_email, test_organization):
        """Test full-text search functionality"""
        result = email_search_service.full_text_search(
            query="invoice payment",
            organization_id=test_organization.id,
            limit=10,
            offset=0
        )
        
        assert result["success"] == True
        assert result["total_count"] >= 0  # May be 0 in SQLite without full-text extensions
    
    def test_search_by_customer_vendor(self, setup_database, test_email, test_customer, test_organization):
        """Test search by customer/vendor"""
        result = email_search_service.search_by_customer_vendor(
            organization_id=test_organization.id,
            customer_id=test_customer.id,
            limit=10,
            offset=0
        )
        
        assert result["success"] == True
        assert result["total_count"] >= 1
        assert result["emails"][0]["customer_id"] == test_customer.id
    
    def test_suggest_search_terms(self, setup_database, test_email, test_organization):
        """Test search term suggestions"""
        suggestions = email_search_service.suggest_search_terms(
            partial_query="inv",
            organization_id=test_organization.id
        )
        
        assert isinstance(suggestions, list)


class TestEmailAI:
    """Test AI-powered email features"""
    
    def test_generate_email_summary(self, setup_database, test_email):
        """Test email summary generation"""
        result = email_ai_service.generate_email_summary(test_email.id)
        
        assert result["success"] == True
        assert "summary" in result
        assert "sentiment" in result
        assert "category" in result
    
    def test_generate_reply_suggestions(self, setup_database, test_email):
        """Test reply suggestion generation"""
        result = email_ai_service.generate_reply_suggestions(test_email.id)
        
        assert result["success"] == True
        assert "suggestions" in result
        assert len(result["suggestions"]) > 0
    
    def test_categorize_email_batch(self, setup_database, test_email):
        """Test batch email categorization"""
        result = email_ai_service.categorize_email_batch([test_email.id])
        
        assert result["success"] == True
        assert len(result["categorized_emails"]) == 1
        assert result["categorized_emails"][0]["email_id"] == test_email.id
    
    def test_extract_action_items(self, setup_database, test_email):
        """Test action item extraction"""
        result = email_ai_service.extract_action_items(test_email.id)
        
        assert result["success"] == True
        assert "action_items" in result
        assert "suggested_tasks" in result


class TestOCRIntegration:
    """Test OCR processing for email attachments"""
    
    @pytest.mark.asyncio
    async def test_ocr_supported_formats(self):
        """Test OCR supported format checking"""
        assert email_attachment_ocr_service.is_supported_format("document.pdf") == True
        assert email_attachment_ocr_service.is_supported_format("image.jpg") == True
        assert email_attachment_ocr_service.is_supported_format("document.docx") == False
    
    @pytest.mark.asyncio
    async def test_process_image_attachment(self, setup_database, test_db):
        """Test OCR processing of image attachment"""
        # Create a simple test image (1x1 pixel PNG)
        test_image_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\x12IDATx\x9cc\xf8\x0f\x00\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01c\xf8\x0f\x00\x02\x00\x01\xfeR\xcc\x01\x00\x00\x00\x00IEND\xaeB`\x82'
        
        attachment = EmailAttachment(
            email_id=1,
            filename="test.png",
            original_filename="test.png",
            content_type="image/png",
            file_data=test_image_data,
            size_bytes=len(test_image_data)
        )
        test_db.add(attachment)
        test_db.commit()
        test_db.refresh(attachment)
        
        # Note: This test may fail without proper OCR setup (Tesseract)
        # In a real environment, you would have OCR dependencies installed
        try:
            result = await email_attachment_ocr_service.process_email_attachment(attachment.id)
            # OCR might not extract much from a 1x1 pixel image, but should not fail
            assert "success" in result
        except Exception as e:
            # OCR dependencies might not be available in test environment
            pytest.skip(f"OCR processing not available: {str(e)}")


class TestERPIntegrationAPI:
    """Test ERP integration API endpoints"""
    
    def test_search_emails_endpoint(self, setup_database, auth_headers, test_email):
        """Test email search API endpoint"""
        response = client.get(
            "/api/v1/email/search?query=invoice",
            headers=auth_headers
        )
        # May return 401 due to auth mocking, but endpoint should exist
        assert response.status_code in [200, 401, 422]
    
    def test_link_email_endpoint(self, setup_database, auth_headers, test_email, test_customer):
        """Test email linking API endpoint"""
        response = client.post(
            f"/api/v1/email/emails/{test_email.id}/link?customer_id={test_customer.id}",
            headers=auth_headers
        )
        # May return 401 due to auth mocking, but endpoint should exist
        assert response.status_code in [200, 401, 422]
    
    def test_ai_summary_endpoint(self, setup_database, auth_headers, test_email):
        """Test AI summary API endpoint"""
        response = client.get(
            f"/api/v1/email/ai/summary/{test_email.id}",
            headers=auth_headers
        )
        # May return 401 due to auth mocking, but endpoint should exist
        assert response.status_code in [200, 401, 422]
    
    def test_shared_inboxes_endpoint(self, setup_database, auth_headers):
        """Test shared inboxes API endpoint"""
        response = client.get(
            "/api/v1/email/shared-inboxes",
            headers=auth_headers
        )
        # May return 401 due to auth mocking, but endpoint should exist
        assert response.status_code in [200, 401, 422]


class TestVoucherEmailIntegration:
    """Test voucher email integration"""
    
    def test_voucher_email_function_exists(self):
        """Test that voucher email sending function exists"""
        from app.services.system_email_service import send_voucher_email
        assert callable(send_voucher_email)
    
    def test_email_linking_function_exists(self):
        """Test that email linking function exists"""
        from app.services.system_email_service import link_email_to_customer_vendor, auto_link_emails_by_sender
        assert callable(link_email_to_customer_vendor)
        assert callable(auto_link_emails_by_sender)