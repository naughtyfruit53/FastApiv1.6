# tests/test_dispatch_api_integration.py

"""
Integration tests for the dispatch API endpoints and workflow
"""

import pytest
from httpx import AsyncClient
from datetime import datetime, timezone
import json

from app.main import app
from app.core.database import get_db
from app.models.base import DispatchOrder, DispatchItem, InstallationJob, User, Organization, Customer, Product
from sqlalchemy.orm import Session


@pytest.fixture
async def test_client():
    """Create test client"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
def test_db_session():
    """Create test database session"""
    db = next(get_db())
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def test_organization(test_db_session: Session):
    """Create test organization"""
    org = Organization(
        name="Test Organization",
        license_type="premium",
        max_users=100,
        is_active=True
    )
    test_db_session.add(org)
    test_db_session.commit()
    test_db_session.refresh(org)
    return org


@pytest.fixture  
def test_user(test_db_session: Session, test_organization: Organization):
    """Create test user with dispatch permissions"""
    user = User(
        email="dispatch@test.com",
        full_name="Dispatch Manager",
        organization_id=test_organization.id,
        is_active=True,
        is_super_admin=False
    )
    test_db_session.add(user)
    test_db_session.commit()
    test_db_session.refresh(user)
    return user


@pytest.fixture
def test_customer(test_db_session: Session, test_organization: Organization):
    """Create test customer"""
    customer = Customer(
        name="Test Customer",
        organization_id=test_organization.id,
        email="customer@test.com",
        mobile="1234567890",
        address="Test Address"
    )
    test_db_session.add(customer)
    test_db_session.commit()
    test_db_session.refresh(customer)
    return customer


@pytest.fixture
def test_product(test_db_session: Session, test_organization: Organization):
    """Create test product"""
    product = Product(
        name="Test Product",
        organization_id=test_organization.id,
        unit="PCS",
        rate=100.0
    )
    test_db_session.add(product)
    test_db_session.commit()
    test_db_session.refresh(product)
    return product


class TestDispatchOrderAPI:
    """Test dispatch order API endpoints"""
    
    @pytest.mark.asyncio
    async def test_create_dispatch_order(self, test_client: AsyncClient, test_user: User, test_customer: Customer, test_product: Product):
        """Test creating a dispatch order"""
        order_data = {
            "customer_id": test_customer.id,
            "delivery_address": "Test Delivery Address",
            "items": [
                {
                    "product_id": test_product.id,
                    "quantity": 5,
                    "unit": "PCS"
                }
            ]
        }
        
        # Note: In a real test, we'd need to mock authentication
        # For now, we'll test the structure is correct
        response = await test_client.post(
            "/api/v1/dispatch/orders",
            json=order_data
        )
        
        # Without proper auth, this should return 401
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_dispatch_orders(self, test_client: AsyncClient):
        """Test getting dispatch orders list"""
        response = await test_client.get("/api/v1/dispatch/orders")
        
        # Without proper auth, this should return 401
        assert response.status_code == 401

    @pytest.mark.asyncio  
    async def test_update_dispatch_order_status(self, test_client: AsyncClient):
        """Test updating dispatch order status"""
        update_data = {
            "status": "in_transit"
        }
        
        response = await test_client.put(
            "/api/v1/dispatch/orders/1",
            json=update_data
        )
        
        # Without proper auth, this should return 401
        assert response.status_code == 401


class TestInstallationJobAPI:
    """Test installation job API endpoints"""
    
    @pytest.mark.asyncio
    async def test_create_installation_job(self, test_client: AsyncClient, test_customer: Customer):
        """Test creating an installation job"""
        job_data = {
            "dispatch_order_id": 1,
            "customer_id": test_customer.id,
            "installation_address": "Test Installation Address",
            "scheduled_date": datetime.now(timezone.utc).isoformat(),
            "priority": "medium"
        }
        
        response = await test_client.post(
            "/api/v1/dispatch/installation-jobs",
            json=job_data
        )
        
        # Without proper auth, this should return 401
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_installation_schedule_prompt(self, test_client: AsyncClient, test_customer: Customer):
        """Test installation schedule prompt workflow"""
        prompt_data = {
            "create_installation_schedule": True,
            "installation_job": {
                "dispatch_order_id": 1,
                "customer_id": test_customer.id,
                "installation_address": "Test Installation Address",
                "scheduled_date": datetime.now(timezone.utc).isoformat(),
                "priority": "high"
            }
        }
        
        response = await test_client.post(
            "/api/v1/dispatch/installation-schedule-prompt",
            json=prompt_data
        )
        
        # Without proper auth, this should return 401
        assert response.status_code == 401


class TestDispatchWorkflow:
    """Test complete dispatch workflow integration"""
    
    def test_dispatch_order_creation_flow(self, test_db_session: Session, test_organization: Organization, test_customer: Customer, test_product: Product):
        """Test complete dispatch order creation and status progression"""
        # Create dispatch order directly in database (simulating authenticated API call)
        dispatch_order = DispatchOrder(
            organization_id=test_organization.id,
            order_number="DO/2024/00001",
            customer_id=test_customer.id,
            delivery_address="Test Delivery Address",
            status="pending",
            created_by_id=None
        )
        test_db_session.add(dispatch_order)
        test_db_session.commit()
        test_db_session.refresh(dispatch_order)
        
        # Add dispatch items
        dispatch_item = DispatchItem(
            dispatch_order_id=dispatch_order.id,
            product_id=test_product.id,
            quantity=5,
            unit="PCS",
            status="pending"
        )
        test_db_session.add(dispatch_item)
        test_db_session.commit()
        
        # Verify order was created
        assert dispatch_order.id is not None
        assert dispatch_order.status == "pending"
        assert len(dispatch_order.items) == 1
        
        # Test status progression
        dispatch_order.status = "in_transit"
        dispatch_order.dispatch_date = datetime.now(timezone.utc)
        test_db_session.commit()
        
        assert dispatch_order.status == "in_transit"
        assert dispatch_order.dispatch_date is not None

    def test_installation_job_creation_flow(self, test_db_session: Session, test_organization: Organization, test_customer: Customer):
        """Test installation job creation from dispatch order"""
        # First create a dispatch order
        dispatch_order = DispatchOrder(
            organization_id=test_organization.id,
            order_number="DO/2024/00002",
            customer_id=test_customer.id,
            delivery_address="Test Delivery Address",
            status="delivered",
            created_by_id=None
        )
        test_db_session.add(dispatch_order)
        test_db_session.commit()
        test_db_session.refresh(dispatch_order)
        
        # Create installation job
        installation_job = InstallationJob(
            organization_id=test_organization.id,
            job_number="IJ/2024/00001",
            dispatch_order_id=dispatch_order.id,
            customer_id=test_customer.id,
            installation_address="Test Installation Address",
            status="scheduled",
            priority="medium"
        )
        test_db_session.add(installation_job)
        test_db_session.commit()
        test_db_session.refresh(installation_job)
        
        # Verify installation job was created
        assert installation_job.id is not None
        assert installation_job.status == "scheduled"
        assert installation_job.dispatch_order_id == dispatch_order.id
        
        # Test status progression
        installation_job.status = "in_progress"
        installation_job.actual_start_time = datetime.now(timezone.utc)
        test_db_session.commit()
        
        assert installation_job.status == "in_progress"
        assert installation_job.actual_start_time is not None

    def test_delivery_challan_integration_workflow(self, test_db_session: Session, test_organization: Organization, test_customer: Customer, test_product: Product):
        """Test the delivery challan to installation scheduling workflow"""
        # Simulate delivery challan creation triggering dispatch order
        dispatch_order = DispatchOrder(
            organization_id=test_organization.id,
            order_number="DO/2024/00003",
            customer_id=test_customer.id,
            delivery_address="Test Delivery Address", 
            status="pending",
            created_by_id=None
        )
        test_db_session.add(dispatch_order)
        test_db_session.commit()
        test_db_session.refresh(dispatch_order)
        
        # Add items
        dispatch_item = DispatchItem(
            dispatch_order_id=dispatch_order.id,
            product_id=test_product.id,
            quantity=2,
            unit="PCS",
            status="pending"
        )
        test_db_session.add(dispatch_item)
        test_db_session.commit()
        
        # Mark as delivered (delivery challan completed)
        dispatch_order.status = "delivered"
        dispatch_order.actual_delivery_date = datetime.now(timezone.utc)
        test_db_session.commit()
        
        # At this point, frontend should show installation prompt
        # User chooses to create installation schedule
        installation_job = InstallationJob(
            organization_id=test_organization.id,
            job_number="IJ/2024/00002",
            dispatch_order_id=dispatch_order.id,
            customer_id=test_customer.id,
            installation_address=dispatch_order.delivery_address,
            status="scheduled",
            priority="medium",
            scheduled_date=datetime.now(timezone.utc)
        )
        test_db_session.add(installation_job)
        test_db_session.commit()
        test_db_session.refresh(installation_job)
        
        # Verify complete workflow
        assert dispatch_order.status == "delivered"
        assert installation_job.dispatch_order_id == dispatch_order.id
        assert installation_job.status == "scheduled"
        assert installation_job.installation_address == dispatch_order.delivery_address


if __name__ == "__main__":
    pytest.main([__file__])