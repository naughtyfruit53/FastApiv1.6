# tests/test_customer_analytics.py

"""
Tests for Customer Analytics API endpoints and service
"""

import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.core.database import get_db
from app.models.base import User, Organization, Customer, CustomerInteraction, CustomerSegment
from app.services.customer_analytics_service import CustomerAnalyticsService
from app.schemas.base import UserRole


class TestCustomerAnalyticsService:
    """Test cases for CustomerAnalyticsService"""
    
    @pytest.fixture
    def analytics_service(self, test_db, test_organization):
        """Create analytics service instance"""
        return CustomerAnalyticsService(test_db, test_organization.id)
    
    @pytest.fixture
    def sample_customer(self, test_db, test_organization):
        """Create a sample customer for testing"""
        customer = Customer(
            organization_id=test_organization.id,
            name="Test Customer",
            contact_number="1234567890",
            email="test@customer.com",
            is_active=True
        )
        test_db.add(customer)
        test_db.commit()
        test_db.refresh(customer)
        return customer
    
    @pytest.fixture
    def sample_interactions(self, test_db, test_organization, sample_customer):
        """Create sample interactions for testing"""
        interactions = []
        
        # Create interactions with different types and statuses
        interaction_data = [
            ("call", "pending", "Customer inquiry call"),
            ("email", "completed", "Follow-up email"),
            ("meeting", "in_progress", "Product demo meeting"),
            ("support_ticket", "completed", "Technical support"),
            ("feedback", "completed", "Customer feedback")
        ]
        
        for i, (int_type, status, subject) in enumerate(interaction_data):
            interaction = CustomerInteraction(
                organization_id=test_organization.id,
                customer_id=sample_customer.id,
                interaction_type=int_type,
                subject=subject,
                status=status,
                interaction_date=datetime.utcnow() - timedelta(days=i)
            )
            interactions.append(interaction)
            test_db.add(interaction)
        
        test_db.commit()
        return interactions
    
    @pytest.fixture
    def sample_segments(self, test_db, test_organization, sample_customer):
        """Create sample segments for testing"""
        segments = []
        
        segment_data = [
            ("premium", 100.0, "Premium customer"),
            ("vip", 200.0, "VIP customer")
        ]
        
        for segment_name, value, description in segment_data:
            segment = CustomerSegment(
                organization_id=test_organization.id,
                customer_id=sample_customer.id,
                segment_name=segment_name,
                segment_value=value,
                segment_description=description,
                is_active=True
            )
            segments.append(segment)
            test_db.add(segment)
        
        test_db.commit()
        return segments
    
    def test_get_customer_metrics(self, analytics_service, sample_customer, sample_interactions, sample_segments):
        """Test getting customer metrics"""
        metrics = analytics_service.get_customer_metrics(sample_customer.id)
        
        assert metrics["customer_id"] == sample_customer.id
        assert metrics["customer_name"] == sample_customer.name
        assert metrics["total_interactions"] == 5
        assert metrics["last_interaction_date"] is not None
        
        # Check interaction type breakdown
        assert "call" in metrics["interaction_types"]
        assert "email" in metrics["interaction_types"]
        assert metrics["interaction_types"]["call"] == 1
        
        # Check status breakdown
        assert "completed" in metrics["interaction_status"]
        assert "pending" in metrics["interaction_status"]
        assert metrics["interaction_status"]["completed"] == 3
        
        # Check segments
        assert len(metrics["segments"]) == 2
        segment_names = [seg["segment_name"] for seg in metrics["segments"]]
        assert "premium" in segment_names
        assert "vip" in segment_names
        
        # Check recent interactions
        assert len(metrics["recent_interactions"]) == 5
        assert metrics["recent_interactions"][0]["interaction_type"] == "feedback"  # Most recent
    
    def test_get_segment_analytics(self, analytics_service, sample_customer, sample_interactions, sample_segments):
        """Test getting segment analytics"""
        analytics = analytics_service.get_segment_analytics("premium")
        
        assert analytics["segment_name"] == "premium"
        assert analytics["total_customers"] == 1
        assert analytics["total_interactions"] == 5
        assert analytics["avg_interactions_per_customer"] == 5.0
        
        # Check interaction distribution
        assert "call" in analytics["interaction_distribution"]
        assert analytics["interaction_distribution"]["call"] == 1
    
    def test_get_organization_analytics_summary(self, analytics_service, sample_customer, sample_interactions, sample_segments):
        """Test getting organization analytics summary"""
        summary = analytics_service.get_organization_analytics_summary()
        
        assert summary["total_customers"] == 1
        assert summary["total_interactions"] == 5
        
        # Check segment distribution
        assert "premium" in summary["segment_distribution"]
        assert "vip" in summary["segment_distribution"]
        assert summary["segment_distribution"]["premium"] == 1
        assert summary["segment_distribution"]["vip"] == 1
    
    def test_customer_not_found(self, analytics_service):
        """Test handling of non-existent customer"""
        metrics = analytics_service.get_customer_metrics(99999)
        assert metrics == {}
    
    def test_empty_segment(self, analytics_service):
        """Test handling of empty segment"""
        analytics = analytics_service.get_segment_analytics("nonexistent")
        
        assert analytics["segment_name"] == "nonexistent"
        assert analytics["total_customers"] == 0
        assert analytics["analytics"] == {}


class TestCustomerAnalyticsAPI:
    """Test cases for Customer Analytics API endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    @pytest.fixture
    def test_organization(self, test_db):
        """Create test organization"""
        org = Organization(
            name="Test Analytics Org",
            subdomain="analytics-test",
            is_active=True
        )
        test_db.add(org)
        test_db.commit()
        test_db.refresh(org)
        return org
    
    @pytest.fixture
    def test_user(self, test_db, test_organization):
        """Create test user"""
        from app.core.security import get_password_hash
        
        user = User(
            organization_id=test_organization.id,
            email="analytics@test.com",
            hashed_password=get_password_hash("testpassword"),
            full_name="Analytics Test User",
            role=UserRole.STANDARD_USER,
            is_active=True
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)
        return user
    
    @pytest.fixture
    def auth_headers(self, client, test_user):
        """Get authentication headers"""
        # Login to get token
        login_response = client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user.email,
                "password": "testpassword"
            }
        )
        token = login_response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    
    @pytest.fixture
    def test_customer_with_data(self, test_db, test_organization):
        """Create test customer with interactions and segments"""
        # Create customer
        customer = Customer(
            organization_id=test_organization.id,
            name="API Test Customer",
            contact_number="9876543210",
            email="api@test.com",
            is_active=True
        )
        test_db.add(customer)
        test_db.commit()
        test_db.refresh(customer)
        
        # Add interactions
        interaction = CustomerInteraction(
            organization_id=test_organization.id,
            customer_id=customer.id,
            interaction_type="call",
            subject="Test interaction",
            status="completed",
            interaction_date=datetime.utcnow()
        )
        test_db.add(interaction)
        
        # Add segment
        segment = CustomerSegment(
            organization_id=test_organization.id,
            customer_id=customer.id,
            segment_name="premium",
            segment_value=150.0,
            is_active=True
        )
        test_db.add(segment)
        
        test_db.commit()
        return customer
    
    def test_get_customer_analytics_success(self, client, auth_headers, test_customer_with_data):
        """Test successful customer analytics retrieval"""
        response = client.get(
            f"/api/v1/analytics/customers/{test_customer_with_data.id}/analytics",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["customer_id"] == test_customer_with_data.id
        assert data["customer_name"] == test_customer_with_data.name
        assert data["total_interactions"] >= 0
        assert "interaction_types" in data
        assert "segments" in data
        assert "calculated_at" in data
    
    def test_get_customer_analytics_not_found(self, client, auth_headers):
        """Test customer analytics for non-existent customer"""
        response = client.get(
            "/api/v1/analytics/customers/99999/analytics",
            headers=auth_headers
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_get_segment_analytics_success(self, client, auth_headers, test_customer_with_data):
        """Test successful segment analytics retrieval"""
        response = client.get(
            "/api/v1/analytics/segments/premium/analytics",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["segment_name"] == "premium"
        assert data["total_customers"] >= 0
        assert "total_interactions" in data
        assert "interaction_distribution" in data
        assert "calculated_at" in data
    
    def test_get_segment_analytics_not_found(self, client, auth_headers):
        """Test segment analytics for non-existent segment"""
        response = client.get(
            "/api/v1/analytics/segments/nonexistent/analytics",
            headers=auth_headers
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_get_organization_summary_success(self, client, auth_headers, test_customer_with_data):
        """Test successful organization summary retrieval"""
        response = client.get(
            "/api/v1/analytics/organization/summary",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "total_customers" in data
        assert "total_interactions" in data
        assert "segment_distribution" in data
        assert "calculated_at" in data
    
    def test_get_dashboard_metrics_success(self, client, auth_headers, test_customer_with_data):
        """Test successful dashboard metrics retrieval"""
        response = client.get(
            "/api/v1/analytics/dashboard/metrics",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "total_customers" in data
        assert "total_interactions_today" in data
        assert "total_interactions_week" in data
        assert "total_interactions_month" in data
        assert "top_segments" in data
        assert "calculated_at" in data
    
    def test_list_segments_success(self, client, auth_headers, test_customer_with_data):
        """Test successful segments list retrieval"""
        response = client.get(
            "/api/v1/analytics/segments",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        if data:  # If there are segments
            assert "premium" in data
    
    def test_unauthorized_access(self, client, test_customer_with_data):
        """Test unauthorized access to analytics endpoints"""
        response = client.get(
            f"/api/v1/analytics/customers/{test_customer_with_data.id}/analytics"
        )
        
        assert response.status_code == 401
    
    def test_customer_analytics_query_parameters(self, client, auth_headers, test_customer_with_data):
        """Test customer analytics with query parameters"""
        response = client.get(
            f"/api/v1/analytics/customers/{test_customer_with_data.id}/analytics"
            "?include_recent_interactions=false&recent_interactions_limit=3",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should have empty recent interactions when disabled
        assert data["recent_interactions"] == []
    
    def test_segment_analytics_query_parameters(self, client, auth_headers, test_customer_with_data):
        """Test segment analytics with query parameters"""
        response = client.get(
            "/api/v1/analytics/segments/premium/analytics"
            "?include_timeline=true&timeline_days=15",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "activity_timeline" in data
    
    def test_parameter_validation(self, client, auth_headers, test_customer_with_data):
        """Test parameter validation"""
        # Test invalid recent_interactions_limit
        response = client.get(
            f"/api/v1/analytics/customers/{test_customer_with_data.id}/analytics"
            "?recent_interactions_limit=25",
            headers=auth_headers
        )
        
        assert response.status_code == 422  # Validation error
        
        # Test invalid timeline_days
        response = client.get(
            "/api/v1/analytics/segments/premium/analytics"
            "?timeline_days=400",
            headers=auth_headers
        )
        
        assert response.status_code == 422  # Validation error


class TestMultiTenantIsolation:
    """Test multi-tenant data isolation in analytics"""
    
    @pytest.fixture
    def org1(self, test_db):
        """Create first organization"""
        org = Organization(
            name="Analytics Org 1",
            subdomain="analytics-org1",
            is_active=True
        )
        test_db.add(org)
        test_db.commit()
        test_db.refresh(org)
        return org
    
    @pytest.fixture
    def org2(self, test_db):
        """Create second organization"""
        org = Organization(
            name="Analytics Org 2", 
            subdomain="analytics-org2",
            is_active=True
        )
        test_db.add(org)
        test_db.commit()
        test_db.refresh(org)
        return org
    
    @pytest.fixture
    def user_org1(self, test_db, org1):
        """Create user for org1"""
        from app.core.security import get_password_hash
        
        user = User(
            organization_id=org1.id,
            email="user1@org1.com",
            hashed_password=get_password_hash("password123"),
            full_name="User 1",
            role=UserRole.STANDARD_USER,
            is_active=True
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)
        return user
    
    @pytest.fixture
    def user_org2(self, test_db, org2):
        """Create user for org2"""
        from app.core.security import get_password_hash
        
        user = User(
            organization_id=org2.id,
            email="user2@org2.com",
            hashed_password=get_password_hash("password123"),
            full_name="User 2",
            role=UserRole.STANDARD_USER,
            is_active=True
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)
        return user
    
    def test_analytics_service_isolation(self, test_db, org1, org2):
        """Test that analytics service only accesses organization data"""
        # Create customers in both organizations
        customer1 = Customer(
            organization_id=org1.id,
            name="Customer Org 1",
            contact_number="1111111111",
            is_active=True
        )
        customer2 = Customer(
            organization_id=org2.id,
            name="Customer Org 2", 
            contact_number="2222222222",
            is_active=True
        )
        test_db.add_all([customer1, customer2])
        test_db.commit()
        test_db.refresh(customer1)
        test_db.refresh(customer2)
        
        # Create analytics services for each org
        analytics1 = CustomerAnalyticsService(test_db, org1.id)
        analytics2 = CustomerAnalyticsService(test_db, org2.id)
        
        # Org1 service should not access org2 customer
        metrics1 = analytics1.get_customer_metrics(customer2.id)
        assert metrics1 == {}  # Should be empty
        
        # Org2 service should not access org1 customer
        metrics2 = analytics2.get_customer_metrics(customer1.id)
        assert metrics2 == {}  # Should be empty
        
        # Each service should access its own customers
        metrics1_own = analytics1.get_customer_metrics(customer1.id)
        assert metrics1_own["customer_id"] == customer1.id
        
        metrics2_own = analytics2.get_customer_metrics(customer2.id)
        assert metrics2_own["customer_id"] == customer2.id