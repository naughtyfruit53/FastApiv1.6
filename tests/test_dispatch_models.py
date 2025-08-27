# tests/test_dispatch_models.py

import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.base import Base, DispatchOrder, DispatchItem, InstallationJob, Organization, Customer, Product, User
from app.services.dispatch_service import DispatchService, InstallationJobService


# Test database setup
@pytest.fixture
def db_session():
    """Create a test database session"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    # Create test organization
    org = Organization(
        id=1,
        name="Test Organization",
        subdomain="test",
        primary_email="test@test.com",
        primary_phone="1234567890",
        address1="Test Address",
        city="Test City",
        state="Test State",
        pin_code="123456",
        plan_type="basic"
    )
    session.add(org)
    
    # Create test customer
    customer = Customer(
        id=1,
        organization_id=1,
        name="Test Customer",
        contact_number="1234567890",
        address1="Test Address",
        city="Test City",
        state="Test State",
        pin_code="123456",
        state_code="TS"
    )
    session.add(customer)
    
    # Create test user
    user = User(
        id=1,
        organization_id=1,
        email="test@test.com",
        username="testuser",
        hashed_password="hashed",
        full_name="Test User",
        role="admin",
        is_active=True
    )
    session.add(user)
    
    # Create test product
    product = Product(
        id=1,
        organization_id=1,
        name="Test Product",
        part_number="TEST001",
        unit="PCS",
        unit_price=100.0,
        gst_rate=18.0
    )
    session.add(product)
    
    session.commit()
    yield session
    session.close()


def test_dispatch_order_creation(db_session):
    """Test creating a dispatch order"""
    dispatch_order = DispatchOrder(
        organization_id=1,
        order_number="DO/2024/00001",
        customer_id=1,
        status="pending",
        delivery_address="Test Delivery Address",
        created_by_id=1
    )
    
    db_session.add(dispatch_order)
    db_session.commit()
    
    # Verify the dispatch order was created
    assert dispatch_order.id is not None
    assert dispatch_order.order_number == "DO/2024/00001"
    assert dispatch_order.customer_id == 1
    assert dispatch_order.status == "pending"


def test_dispatch_item_creation(db_session):
    """Test creating dispatch items"""
    # First create a dispatch order
    dispatch_order = DispatchOrder(
        organization_id=1,
        order_number="DO/2024/00001",
        customer_id=1,
        status="pending",
        delivery_address="Test Delivery Address",
        created_by_id=1
    )
    db_session.add(dispatch_order)
    db_session.flush()
    
    # Create dispatch item
    dispatch_item = DispatchItem(
        dispatch_order_id=dispatch_order.id,
        product_id=1,
        quantity=5.0,
        unit="PCS",
        description="Test item description",
        status="pending"
    )
    
    db_session.add(dispatch_item)
    db_session.commit()
    
    # Verify the dispatch item was created
    assert dispatch_item.id is not None
    assert dispatch_item.quantity == 5.0
    assert dispatch_item.unit == "PCS"
    assert dispatch_item.status == "pending"


def test_installation_job_creation(db_session):
    """Test creating an installation job"""
    # First create a dispatch order
    dispatch_order = DispatchOrder(
        organization_id=1,
        order_number="DO/2024/00001",
        customer_id=1,
        status="pending",
        delivery_address="Test Delivery Address",
        created_by_id=1
    )
    db_session.add(dispatch_order)
    db_session.flush()
    
    # Create installation job
    installation_job = InstallationJob(
        organization_id=1,
        job_number="IJ/2024/00001",
        dispatch_order_id=dispatch_order.id,
        customer_id=1,
        status="scheduled",
        priority="medium",
        installation_address="Test Installation Address",
        created_by_id=1
    )
    
    db_session.add(installation_job)
    db_session.commit()
    
    # Verify the installation job was created
    assert installation_job.id is not None
    assert installation_job.job_number == "IJ/2024/00001"
    assert installation_job.customer_id == 1
    assert installation_job.status == "scheduled"
    assert installation_job.priority == "medium"


def test_dispatch_service_create_order(db_session):
    """Test DispatchService create_dispatch_order method"""
    dispatch_service = DispatchService(db_session)
    
    items_data = [
        {
            "product_id": 1,
            "quantity": 3.0,
            "unit": "PCS",
            "description": "Test product",
            "status": "pending"
        }
    ]
    
    dispatch_order = dispatch_service.create_dispatch_order(
        organization_id=1,
        customer_id=1,
        delivery_address="Test Delivery Address",
        items=items_data,
        created_by_id=1
    )
    
    # Verify the dispatch order was created
    assert dispatch_order.id is not None
    assert dispatch_order.customer_id == 1
    assert dispatch_order.delivery_address == "Test Delivery Address"
    assert len(dispatch_order.items) == 1
    assert dispatch_order.items[0].quantity == 3.0


def test_dispatch_service_update_status(db_session):
    """Test DispatchService update_dispatch_status method"""
    dispatch_service = DispatchService(db_session)
    
    # Create a dispatch order first
    items_data = [{"product_id": 1, "quantity": 1.0, "unit": "PCS", "status": "pending"}]
    dispatch_order = dispatch_service.create_dispatch_order(
        organization_id=1,
        customer_id=1,
        delivery_address="Test Address",
        items=items_data,
        created_by_id=1
    )
    
    # Update status to in_transit
    updated_order = dispatch_service.update_dispatch_status(
        dispatch_order_id=dispatch_order.id,
        status="in_transit",
        updated_by_id=1
    )
    
    # Verify the status was updated and dispatch_date was set
    assert updated_order.status == "in_transit"
    assert updated_order.dispatch_date is not None
    assert updated_order.updated_by_id == 1


def test_installation_job_service_create_job(db_session):
    """Test InstallationJobService create_installation_job method"""
    # Create a dispatch order first
    dispatch_order = DispatchOrder(
        organization_id=1,
        order_number="DO/2024/00001",
        customer_id=1,
        status="pending",
        delivery_address="Test Delivery Address",
        created_by_id=1
    )
    db_session.add(dispatch_order)
    db_session.flush()
    
    installation_service = InstallationJobService(db_session)
    
    installation_job = installation_service.create_installation_job(
        organization_id=1,
        dispatch_order_id=dispatch_order.id,
        customer_id=1,
        installation_address="Test Installation Address",
        created_by_id=1,
        priority="high",
        estimated_duration_hours=4.0
    )
    
    # Verify the installation job was created
    assert installation_job.id is not None
    assert installation_job.dispatch_order_id == dispatch_order.id
    assert installation_job.customer_id == 1
    assert installation_job.priority == "high"
    assert installation_job.estimated_duration_hours == 4.0


def test_installation_job_service_assign_technician(db_session):
    """Test InstallationJobService assign_technician method"""
    # Create a dispatch order first
    dispatch_order = DispatchOrder(
        organization_id=1,
        order_number="DO/2024/00001",
        customer_id=1,
        status="pending",
        delivery_address="Test Address",
        created_by_id=1
    )
    db_session.add(dispatch_order)
    db_session.flush()
    
    # Create an installation job
    installation_service = InstallationJobService(db_session)
    installation_job = installation_service.create_installation_job(
        organization_id=1,
        dispatch_order_id=dispatch_order.id,
        customer_id=1,
        installation_address="Test Installation Address",
        created_by_id=1
    )
    
    # Assign technician
    updated_job = installation_service.assign_technician(
        job_id=installation_job.id,
        technician_id=1,
        updated_by_id=1
    )
    
    # Verify the technician was assigned
    assert updated_job.assigned_technician_id == 1
    assert updated_job.updated_by_id == 1


def test_installation_job_service_update_status(db_session):
    """Test InstallationJobService update_job_status method"""
    # Create a dispatch order first
    dispatch_order = DispatchOrder(
        organization_id=1,
        order_number="DO/2024/00001",
        customer_id=1,
        status="pending",
        delivery_address="Test Address",
        created_by_id=1
    )
    db_session.add(dispatch_order)
    db_session.flush()
    
    # Create an installation job
    installation_service = InstallationJobService(db_session)
    installation_job = installation_service.create_installation_job(
        organization_id=1,
        dispatch_order_id=dispatch_order.id,
        customer_id=1,
        installation_address="Test Installation Address",
        created_by_id=1
    )
    
    # Update status to in_progress
    updated_job = installation_service.update_job_status(
        job_id=installation_job.id,
        status="in_progress",
        updated_by_id=1
    )
    
    # Verify the status was updated and actual_start_time was set
    assert updated_job.status == "in_progress"
    assert updated_job.actual_start_time is not None
    assert updated_job.updated_by_id == 1


if __name__ == "__main__":
    pytest.main([__file__])