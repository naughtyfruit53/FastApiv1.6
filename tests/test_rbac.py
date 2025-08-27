# tests/test_rbac.py

"""
Unit tests for Service CRM RBAC functionality
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import Base, get_db
from app.services.rbac import RBACService
from app.models.base import Organization, User, ServiceRole, ServicePermission
from app.schemas.rbac import ServiceRoleCreate, ServicePermissionCreate, ServiceRoleType

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_rbac.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def test_organization(db_session):
    org = Organization(
        name="Test Organization",
        subdomain="test",
        status="active",
        primary_email="test@example.com",
        primary_phone="+1234567890",
        address1="123 Test St",
        city="Test City",
        state="Test State",
        pin_code="12345",
        country="Test Country"
    )
    db_session.add(org)
    db_session.commit()
    db_session.refresh(org)
    return org


@pytest.fixture
def test_user(db_session, test_organization):
    user = User(
        organization_id=test_organization.id,
        email="test@example.com",
        username="testuser",
        hashed_password="hashedpassword",
        full_name="Test User",
        role="admin"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def rbac_service(db_session):
    return RBACService(db_session)


class TestServicePermissions:
    """Test Service Permission functionality"""
    
    def test_create_permission(self, rbac_service):
        permission = ServicePermissionCreate(
            name="test_permission",
            display_name="Test Permission",
            description="A test permission",
            module="test",
            action="create"
        )
        
        db_permission = rbac_service.create_permission(permission)
        
        assert db_permission.id is not None
        assert db_permission.name == "test_permission"
        assert db_permission.display_name == "Test Permission"
        assert db_permission.module == "test"
        assert db_permission.action == "create"
        assert db_permission.is_active is True
    
    def test_get_permissions(self, rbac_service):
        # Create test permissions
        permissions = [
            ServicePermissionCreate(name="service_create", display_name="Create Service", module="service", action="create"),
            ServicePermissionCreate(name="service_read", display_name="Read Service", module="service", action="read"),
            ServicePermissionCreate(name="technician_create", display_name="Create Technician", module="technician", action="create"),
        ]
        
        for perm in permissions:
            rbac_service.create_permission(perm)
        
        # Test get all permissions
        all_perms = rbac_service.get_permissions()
        assert len(all_perms) == 3
        
        # Test filter by module
        service_perms = rbac_service.get_permissions(module="service")
        assert len(service_perms) == 2
        
        # Test filter by action
        create_perms = rbac_service.get_permissions(action="create")
        assert len(create_perms) == 2
    
    def test_get_permission_by_name(self, rbac_service):
        permission = ServicePermissionCreate(
            name="unique_permission",
            display_name="Unique Permission",
            module="test",
            action="test"
        )
        
        created = rbac_service.create_permission(permission)
        found = rbac_service.get_permission_by_name("unique_permission")
        
        assert found is not None
        assert found.id == created.id
        assert found.name == "unique_permission"
    
    def test_initialize_default_permissions(self, rbac_service):
        permissions = rbac_service.initialize_default_permissions()
        
        assert len(permissions) > 0
        
        # Check that some expected permissions exist
        expected_permissions = [
            "service_create", "service_read", "service_update", "service_delete",
            "technician_create", "technician_read", "technician_update", "technician_delete",
            "appointment_create", "appointment_read", "appointment_update", "appointment_delete"
        ]
        
        permission_names = [p.name for p in permissions]
        for expected in expected_permissions:
            assert expected in permission_names


class TestServiceRoles:
    """Test Service Role functionality"""
    
    def test_create_role(self, rbac_service, test_organization):
        # Create some permissions first
        rbac_service.initialize_default_permissions()
        permissions = rbac_service.get_permissions()
        permission_ids = [p.id for p in permissions[:3]]  # Use first 3 permissions
        
        role = ServiceRoleCreate(
            name=ServiceRoleType.ADMIN,
            display_name="Test Admin",
            description="Test admin role",
            organization_id=test_organization.id,
            permission_ids=permission_ids
        )
        
        db_role = rbac_service.create_role(role)
        
        assert db_role.id is not None
        assert db_role.name == ServiceRoleType.ADMIN
        assert db_role.display_name == "Test Admin"
        assert db_role.organization_id == test_organization.id
        assert db_role.is_active is True
    
    def test_create_duplicate_role_fails(self, rbac_service, test_organization):
        rbac_service.initialize_default_permissions()
        permissions = rbac_service.get_permissions()
        permission_ids = [p.id for p in permissions[:2]]
        
        role = ServiceRoleCreate(
            name=ServiceRoleType.ADMIN,
            display_name="Admin Role",
            organization_id=test_organization.id,
            permission_ids=permission_ids
        )
        
        # Create first role
        rbac_service.create_role(role)
        
        # Try to create duplicate - should fail
        with pytest.raises(Exception):  # HTTPException in actual usage
            rbac_service.create_role(role)
    
    def test_get_roles(self, rbac_service, test_organization):
        rbac_service.initialize_default_permissions()
        permissions = rbac_service.get_permissions()
        permission_ids = [p.id for p in permissions[:2]]
        
        # Create test roles
        roles_data = [
            ServiceRoleCreate(name=ServiceRoleType.ADMIN, display_name="Admin", organization_id=test_organization.id, permission_ids=permission_ids),
            ServiceRoleCreate(name=ServiceRoleType.MANAGER, display_name="Manager", organization_id=test_organization.id, permission_ids=permission_ids[:1]),
        ]
        
        for role_data in roles_data:
            rbac_service.create_role(role_data)
        
        roles = rbac_service.get_roles(test_organization.id)
        assert len(roles) == 2
        
        role_names = [r.name for r in roles]
        assert ServiceRoleType.ADMIN in role_names
        assert ServiceRoleType.MANAGER in role_names
    
    def test_get_role_by_id(self, rbac_service, test_organization):
        rbac_service.initialize_default_permissions()
        permissions = rbac_service.get_permissions()
        permission_ids = [p.id for p in permissions[:1]]
        
        role = ServiceRoleCreate(
            name=ServiceRoleType.SUPPORT,
            display_name="Support Agent",
            organization_id=test_organization.id,
            permission_ids=permission_ids
        )
        
        created_role = rbac_service.create_role(role)
        found_role = rbac_service.get_role_by_id(created_role.id)
        
        assert found_role is not None
        assert found_role.id == created_role.id
        assert found_role.name == ServiceRoleType.SUPPORT
    
    def test_initialize_default_roles(self, rbac_service, test_organization):
        roles = rbac_service.initialize_default_roles(test_organization.id)
        
        assert len(roles) == 4  # admin, manager, support, viewer
        
        role_names = [r.name for r in roles]
        expected_roles = [ServiceRoleType.ADMIN, ServiceRoleType.MANAGER, ServiceRoleType.SUPPORT, ServiceRoleType.VIEWER]
        
        for expected in expected_roles:
            assert expected in role_names


class TestUserRoleAssignments:
    """Test User-Role Assignment functionality"""
    
    def test_assign_role_to_user(self, rbac_service, test_user, test_organization):
        # Initialize default roles
        roles = rbac_service.initialize_default_roles(test_organization.id)
        admin_role = next(r for r in roles if r.name == ServiceRoleType.ADMIN)
        
        assignment = rbac_service.assign_role_to_user(test_user.id, admin_role.id)
        
        assert assignment.id is not None
        assert assignment.user_id == test_user.id
        assert assignment.role_id == admin_role.id
        assert assignment.is_active is True
    
    def test_assign_multiple_roles_to_user(self, rbac_service, test_user, test_organization):
        roles = rbac_service.initialize_default_roles(test_organization.id)
        role_ids = [r.id for r in roles[:2]]  # Assign first 2 roles
        
        assignments = rbac_service.assign_multiple_roles_to_user(test_user.id, role_ids)
        
        assert len(assignments) == 2
        for assignment in assignments:
            assert assignment.user_id == test_user.id
            assert assignment.is_active is True
    
    def test_get_user_service_roles(self, rbac_service, test_user, test_organization):
        roles = rbac_service.initialize_default_roles(test_organization.id)
        admin_role = next(r for r in roles if r.name == ServiceRoleType.ADMIN)
        manager_role = next(r for r in roles if r.name == ServiceRoleType.MANAGER)
        
        # Assign roles
        rbac_service.assign_role_to_user(test_user.id, admin_role.id)
        rbac_service.assign_role_to_user(test_user.id, manager_role.id)
        
        user_roles = rbac_service.get_user_service_roles(test_user.id)
        
        assert len(user_roles) == 2
        role_names = [r.name for r in user_roles]
        assert ServiceRoleType.ADMIN in role_names
        assert ServiceRoleType.MANAGER in role_names
    
    def test_remove_role_from_user(self, rbac_service, test_user, test_organization):
        roles = rbac_service.initialize_default_roles(test_organization.id)
        admin_role = next(r for r in roles if r.name == ServiceRoleType.ADMIN)
        
        # Assign role
        rbac_service.assign_role_to_user(test_user.id, admin_role.id)
        
        # Verify assignment
        user_roles = rbac_service.get_user_service_roles(test_user.id)
        assert len(user_roles) == 1
        
        # Remove role
        success = rbac_service.remove_role_from_user(test_user.id, admin_role.id)
        assert success is True
        
        # Verify removal
        user_roles = rbac_service.get_user_service_roles(test_user.id)
        assert len(user_roles) == 0
    
    def test_remove_all_service_roles_from_user(self, rbac_service, test_user, test_organization):
        roles = rbac_service.initialize_default_roles(test_organization.id)
        role_ids = [r.id for r in roles[:3]]  # Assign first 3 roles
        
        # Assign multiple roles
        rbac_service.assign_multiple_roles_to_user(test_user.id, role_ids)
        
        # Verify assignments
        user_roles = rbac_service.get_user_service_roles(test_user.id)
        assert len(user_roles) == 3
        
        # Remove all roles
        count = rbac_service.remove_all_service_roles_from_user(test_user.id)
        assert count == 3
        
        # Verify removal
        user_roles = rbac_service.get_user_service_roles(test_user.id)
        assert len(user_roles) == 0


class TestPermissionChecking:
    """Test Permission Checking functionality"""
    
    def test_user_has_service_permission(self, rbac_service, test_user, test_organization):
        # Initialize defaults
        rbac_service.initialize_default_permissions()
        roles = rbac_service.initialize_default_roles(test_organization.id)
        
        # Assign admin role (should have all permissions)
        admin_role = next(r for r in roles if r.name == ServiceRoleType.ADMIN)
        rbac_service.assign_role_to_user(test_user.id, admin_role.id)
        
        # Test permission checking
        assert rbac_service.user_has_service_permission(test_user.id, "service_create") is True
        assert rbac_service.user_has_service_permission(test_user.id, "service_read") is True
        assert rbac_service.user_has_service_permission(test_user.id, "nonexistent_permission") is False
    
    def test_viewer_role_permissions(self, rbac_service, test_user, test_organization):
        # Initialize defaults
        rbac_service.initialize_default_permissions()
        roles = rbac_service.initialize_default_roles(test_organization.id)
        
        # Assign viewer role (should have only read permissions)
        viewer_role = next(r for r in roles if r.name == ServiceRoleType.VIEWER)
        rbac_service.assign_role_to_user(test_user.id, viewer_role.id)
        
        # Test read permissions
        assert rbac_service.user_has_service_permission(test_user.id, "service_read") is True
        assert rbac_service.user_has_service_permission(test_user.id, "technician_read") is True
        
        # Test create/update/delete permissions (should be denied)
        assert rbac_service.user_has_service_permission(test_user.id, "service_create") is False
        assert rbac_service.user_has_service_permission(test_user.id, "service_update") is False
        assert rbac_service.user_has_service_permission(test_user.id, "service_delete") is False
    
    def test_get_user_service_permissions(self, rbac_service, test_user, test_organization):
        # Initialize defaults
        rbac_service.initialize_default_permissions()
        roles = rbac_service.initialize_default_roles(test_organization.id)
        
        # Assign support role
        support_role = next(r for r in roles if r.name == ServiceRoleType.SUPPORT)
        rbac_service.assign_role_to_user(test_user.id, support_role.id)
        
        # Get all permissions
        permissions = rbac_service.get_user_service_permissions(test_user.id)
        
        assert len(permissions) > 0
        assert "service_read" in permissions
        assert "appointment_create" in permissions
        assert "customer_service_create" in permissions
        
        # Support role should not have delete permissions for core entities
        assert "service_delete" not in permissions
        assert "technician_delete" not in permissions


# Integration tests with FastAPI
class TestRBACAPI:
    """Test RBAC API endpoints"""
    
    def test_get_permissions_endpoint(self, client):
        # This would require proper authentication setup
        # For now, just test that the endpoint exists
        response = client.get("/api/v1/rbac/permissions")
        # Without authentication, should get 401 or 403
        assert response.status_code in [401, 403]
    
    def test_get_organization_roles_endpoint(self, client):
        response = client.get("/api/v1/rbac/organizations/1/roles")
        # Without authentication, should get 401 or 403
        assert response.status_code in [401, 403]


if __name__ == "__main__":
    pytest.main([__file__])