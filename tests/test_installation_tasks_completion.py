# tests/test_installation_tasks_completion.py

import pytest
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.base import (
    Base, Organization, Customer, Product, User, DispatchOrder, InstallationJob, 
    InstallationTask, CompletionRecord
)
from app.services.dispatch_service import InstallationJobService, InstallationTaskService, CompletionRecordService
from app.schemas.dispatch import (
    InstallationTaskStatus, CompletionStatus, InstallationTaskCreate, CompletionRecordCreate
)


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
    
    # Create test users (technician and manager)
    technician = User(
        id=1,
        organization_id=1,
        username="technician@test.com",
        email="technician@test.com",
        hashed_password="hashedpass",
        full_name="Test Technician",
        role="standard_user"
    )
    session.add(technician)
    
    manager = User(
        id=2,
        organization_id=1,
        username="manager@test.com",
        email="manager@test.com",
        hashed_password="hashedpass",
        full_name="Test Manager",
        role="admin"
    )
    session.add(manager)
    
    # Create test product
    product = Product(
        id=1,
        organization_id=1,
        name="Test Product",
        unit="pcs",
        unit_price=100.0
    )
    session.add(product)
    
    session.commit()
    
    yield session
    session.close()


@pytest.fixture
def sample_installation_job(db_session):
    """Create a sample installation job for testing"""
    # Create dispatch order first
    dispatch_order = DispatchOrder(
        id=1,
        organization_id=1,
        order_number="DO/2024/00001",
        customer_id=1,
        delivery_address="Test Delivery Address",
        status="delivered",
        created_by_id=2
    )
    db_session.add(dispatch_order)
    
    # Create installation job
    installation_job = InstallationJob(
        id=1,
        organization_id=1,
        job_number="IJ/2024/00001",
        dispatch_order_id=1,
        customer_id=1,
        installation_address="Test Installation Address",
        status="scheduled",
        assigned_technician_id=1,
        created_by_id=2
    )
    db_session.add(installation_job)
    db_session.commit()
    
    return installation_job


class TestInstallationTaskService:
    """Test InstallationTaskService functionality"""
    
    def test_create_installation_task(self, db_session, sample_installation_job):
        """Test creating an installation task"""
        task_service = InstallationTaskService(db_session)
        
        task = task_service.create_installation_task(
            organization_id=1,
            installation_job_id=1,
            title="Install Main Unit",
            created_by_id=2,
            description="Install and configure the main unit",
            priority="high",
            estimated_duration_minutes=120,
            sequence_order=1
        )
        
        assert task.id is not None
        assert task.task_number.startswith("IT/")
        assert task.title == "Install Main Unit"
        assert task.status == "pending"
        assert task.priority == "high"
        assert task.estimated_duration_minutes == 120
        assert task.sequence_order == 1
        assert task.organization_id == 1
        assert task.installation_job_id == 1
        assert task.created_by_id == 2
    
    def test_generate_task_number(self, db_session):
        """Test task number generation"""
        task_service = InstallationTaskService(db_session)
        
        task_number = task_service.generate_task_number(organization_id=1)
        
        assert task_number.startswith("IT/")
        assert len(task_number.split('/')) == 3
        assert task_number.endswith("/00001")
    
    def test_update_task_status(self, db_session, sample_installation_job):
        """Test updating task status with automatic timing"""
        task_service = InstallationTaskService(db_session)
        
        # Create task
        task = task_service.create_installation_task(
            organization_id=1,
            installation_job_id=1,
            title="Test Task",
            created_by_id=2
        )
        
        # Update to in_progress
        updated_task = task_service.update_task_status(
            task_id=task.id,
            status="in_progress",
            updated_by_id=1,
            work_notes="Started working on task"
        )
        
        assert updated_task.status == "in_progress"
        assert updated_task.started_at is not None
        assert updated_task.work_notes == "Started working on task"
        
        # Update to completed
        updated_task = task_service.update_task_status(
            task_id=task.id,
            status="completed",
            updated_by_id=1,
            completion_notes="Task completed successfully"
        )
        
        assert updated_task.status == "completed"
        assert updated_task.completed_at is not None
        assert updated_task.completion_notes == "Task completed successfully"
    
    def test_assign_technician(self, db_session, sample_installation_job):
        """Test assigning technician to task"""
        task_service = InstallationTaskService(db_session)
        
        # Create task
        task = task_service.create_installation_task(
            organization_id=1,
            installation_job_id=1,
            title="Test Task",
            created_by_id=2
        )
        
        # Assign technician
        updated_task = task_service.assign_technician(
            task_id=task.id,
            technician_id=1,
            updated_by_id=2
        )
        
        assert updated_task.assigned_technician_id == 1
        assert updated_task.updated_by_id == 2
    
    def test_assign_invalid_technician(self, db_session, sample_installation_job):
        """Test assigning technician from different organization"""
        task_service = InstallationTaskService(db_session)
        
        # Create task
        task = task_service.create_installation_task(
            organization_id=1,
            installation_job_id=1,
            title="Test Task",
            created_by_id=2
        )
        
        # Try to assign non-existent technician
        with pytest.raises(ValueError, match="Technician .* not found in organization"):
            task_service.assign_technician(
                task_id=task.id,
                technician_id=999,
                updated_by_id=2
            )


class TestCompletionRecordService:
    """Test CompletionRecordService functionality"""
    
    def test_create_completion_record(self, db_session, sample_installation_job):
        """Test creating a completion record"""
        completion_service = CompletionRecordService(db_session)
        
        completion_date = datetime.now(timezone.utc)
        actual_start = completion_date.replace(hour=9, minute=0)
        actual_end = completion_date.replace(hour=12, minute=30)
        
        completion_record = completion_service.create_completion_record(
            organization_id=1,
            installation_job_id=1,
            completed_by_id=1,  # Assigned technician
            completion_date=completion_date,
            work_performed="Successfully installed and configured all equipment",
            completion_status="completed",
            actual_start_time=actual_start,
            actual_end_time=actual_end,
            quality_check_passed=True,
            customer_present=True,
            customer_signature_received=True,
            customer_rating=5
        )
        
        assert completion_record.id is not None
        assert completion_record.installation_job_id == 1
        assert completion_record.completed_by_id == 1
        assert completion_record.completion_status == "completed"
        assert completion_record.work_performed == "Successfully installed and configured all equipment"
        assert completion_record.total_duration_minutes == 210  # 3.5 hours
        assert completion_record.quality_check_passed is True
        assert completion_record.customer_rating == 5
        assert completion_record.feedback_request_sent is True  # Should be triggered automatically
        
        # Check that installation job status was updated
        job = db_session.query(InstallationJob).filter(InstallationJob.id == 1).first()
        assert job.status == "completed"
        # Compare without timezone for SQLite compatibility
        assert job.actual_start_time.replace(tzinfo=None) == actual_start.replace(tzinfo=None)
        assert job.actual_end_time.replace(tzinfo=None) == actual_end.replace(tzinfo=None)
        assert job.customer_rating == 5
    
    def test_create_completion_record_unauthorized_user(self, db_session, sample_installation_job):
        """Test creating completion record with unauthorized user"""
        completion_service = CompletionRecordService(db_session)
        
        completion_date = datetime.now(timezone.utc)
        
        # Try to complete with user who is not assigned technician
        with pytest.raises(ValueError, match="Only the assigned technician can mark the job as complete"):
            completion_service.create_completion_record(
                organization_id=1,
                installation_job_id=1,
                completed_by_id=2,  # Manager, not assigned technician
                completion_date=completion_date,
                work_performed="Completed work"
            )
    
    def test_create_duplicate_completion_record(self, db_session, sample_installation_job):
        """Test creating duplicate completion record"""
        completion_service = CompletionRecordService(db_session)
        
        completion_date = datetime.now(timezone.utc)
        
        # Create first completion record
        completion_service.create_completion_record(
            organization_id=1,
            installation_job_id=1,
            completed_by_id=1,
            completion_date=completion_date,
            work_performed="First completion"
        )
        
        # Try to create second completion record for same job
        with pytest.raises(ValueError, match="Completion record already exists for this job"):
            completion_service.create_completion_record(
                organization_id=1,
                installation_job_id=1,
                completed_by_id=1,
                completion_date=completion_date,
                work_performed="Second completion"
            )
    
    def test_update_completion_record(self, db_session, sample_installation_job):
        """Test updating a completion record"""
        completion_service = CompletionRecordService(db_session)
        
        completion_date = datetime.now(timezone.utc)
        
        # Create completion record
        completion_record = completion_service.create_completion_record(
            organization_id=1,
            installation_job_id=1,
            completed_by_id=1,
            completion_date=completion_date,
            work_performed="Initial work performed"
        )
        
        # Update completion record
        updated_record = completion_service.update_completion_record(
            completion_record_id=completion_record.id,
            organization_id=1,
            work_performed="Updated work performed",
            customer_feedback_notes="Customer was very satisfied",
            customer_rating=5,
            follow_up_required=True,
            follow_up_notes="Schedule maintenance check in 6 months"
        )
        
        assert updated_record.work_performed == "Updated work performed"
        assert updated_record.customer_feedback_notes == "Customer was very satisfied"
        assert updated_record.customer_rating == 5
        assert updated_record.follow_up_required is True
        assert updated_record.follow_up_notes == "Schedule maintenance check in 6 months"
    
    def test_update_completion_record_with_timing(self, db_session, sample_installation_job):
        """Test updating completion record with timing recalculation"""
        completion_service = CompletionRecordService(db_session)
        
        completion_date = datetime.now(timezone.utc)
        
        # Create completion record without timing
        completion_record = completion_service.create_completion_record(
            organization_id=1,
            installation_job_id=1,
            completed_by_id=1,
            completion_date=completion_date,
            work_performed="Work performed"
        )
        
        # Update with timing information
        actual_start = completion_date.replace(hour=8, minute=0)
        actual_end = completion_date.replace(hour=16, minute=30)
        
        updated_record = completion_service.update_completion_record(
            completion_record_id=completion_record.id,
            organization_id=1,
            actual_start_time=actual_start,
            actual_end_time=actual_end
        )
        
        assert updated_record.actual_start_time.replace(tzinfo=None) == actual_start.replace(tzinfo=None)
        assert updated_record.actual_end_time.replace(tzinfo=None) == actual_end.replace(tzinfo=None)
        assert updated_record.total_duration_minutes == 510  # 8.5 hours


class TestInstallationTaskModel:
    """Test InstallationTask model functionality"""
    
    def test_installation_task_creation(self, db_session, sample_installation_job):
        """Test basic installation task creation"""
        task = InstallationTask(
            organization_id=1,
            installation_job_id=1,
            task_number="IT/2024/00001",
            title="Install Equipment",
            description="Install and test equipment",
            status="pending",
            priority="medium",
            sequence_order=1,
            estimated_duration_minutes=60,
            created_by_id=2
        )
        
        db_session.add(task)
        db_session.commit()
        
        assert task.id is not None
        assert task.title == "Install Equipment"
        assert task.status == "pending"
        assert task.created_at is not None
    
    def test_installation_task_relationships(self, db_session, sample_installation_job):
        """Test installation task relationships"""
        task = InstallationTask(
            organization_id=1,
            installation_job_id=1,
            task_number="IT/2024/00001",
            title="Install Equipment",
            sequence_order=1,
            assigned_technician_id=1,
            created_by_id=2
        )
        
        db_session.add(task)
        db_session.commit()
        
        # Test relationships
        assert task.installation_job is not None
        assert task.installation_job.job_number == "IJ/2024/00001"
        assert task.assigned_technician is not None
        assert task.assigned_technician.full_name == "Test Technician"
        assert task.organization is not None
        assert task.organization.name == "Test Organization"


class TestCompletionRecordModel:
    """Test CompletionRecord model functionality"""
    
    def test_completion_record_creation(self, db_session, sample_installation_job):
        """Test basic completion record creation"""
        completion_date = datetime.now(timezone.utc)
        
        completion_record = CompletionRecord(
            organization_id=1,
            installation_job_id=1,
            completed_by_id=1,
            completion_date=completion_date,
            work_performed="Installation completed successfully",
            completion_status="completed",
            quality_check_passed=True,
            customer_present=True,
            customer_rating=5
        )
        
        db_session.add(completion_record)
        db_session.commit()
        
        assert completion_record.id is not None
        assert completion_record.work_performed == "Installation completed successfully"
        assert completion_record.completion_status == "completed"
        assert completion_record.created_at is not None
    
    def test_completion_record_relationships(self, db_session, sample_installation_job):
        """Test completion record relationships"""
        completion_date = datetime.now(timezone.utc)
        
        completion_record = CompletionRecord(
            organization_id=1,
            installation_job_id=1,
            completed_by_id=1,
            completion_date=completion_date,
            work_performed="Work completed"
        )
        
        db_session.add(completion_record)
        db_session.commit()
        
        # Test relationships
        assert completion_record.installation_job is not None
        assert completion_record.installation_job.job_number == "IJ/2024/00001"
        assert completion_record.completed_by is not None
        assert completion_record.completed_by.full_name == "Test Technician"
        assert completion_record.organization is not None
        assert completion_record.organization.name == "Test Organization"