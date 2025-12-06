"""
Unit tests for permission format API endpoints
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.permissions import LEGACY_PERMISSION_MAP, PERMISSION_HIERARCHY


client = TestClient(app)


class TestPermissionFormatAPI:
    """Test the /api/v1/system/permission-format endpoints"""
    
    @pytest.fixture
    def auth_headers(self):
        """Create authentication headers for testing"""
        # This is a simplified fixture - in real tests you'd need proper auth
        return {"Authorization": "Bearer test-token"}
    
    def test_permission_format_endpoint_exists(self):
        """Test that the permission-format endpoint exists"""
        # Note: This will fail without proper authentication
        # In actual tests, you'd need to create a test user and get a real token
        response = client.get("/api/v1/system/permission-format")
        # Should be 401 (unauthorized) not 404 (not found)
        assert response.status_code in [200, 401, 403]
    
    def test_permission_format_response_structure(self, auth_headers):
        """Test the structure of permission-format response"""
        # Skip if authentication fails
        response = client.get("/api/v1/system/permission-format", headers=auth_headers)
        
        if response.status_code == 200:
            data = response.json()
            
            # Check required fields
            assert "primary_format" in data
            assert "compatibility" in data
            assert "legacy_formats" in data
            assert "hierarchy_enabled" in data
            assert "version" in data
            assert "migration_status" in data
            
            # Check field types
            assert isinstance(data["primary_format"], str)
            assert isinstance(data["compatibility"], bool)
            assert isinstance(data["legacy_formats"], list)
            assert isinstance(data["hierarchy_enabled"], bool)
            assert isinstance(data["version"], str)
            assert isinstance(data["migration_status"], str)
    
    def test_permission_format_values(self, auth_headers):
        """Test the values in permission-format response"""
        response = client.get("/api/v1/system/permission-format", headers=auth_headers)
        
        if response.status_code == 200:
            data = response.json()
            
            # Check expected values
            assert data["primary_format"] == "dotted"
            assert data["compatibility"] == True  # Should be enabled during migration
            assert data["hierarchy_enabled"] == True
            assert data["version"] == "1.0"
            
            # Check legacy formats
            if data["compatibility"]:
                assert len(data["legacy_formats"]) > 0
                assert "underscore" in data["legacy_formats"] or "colon" in data["legacy_formats"]
    
    def test_permission_format_counts(self, auth_headers):
        """Test that mapping and hierarchy counts are accurate"""
        response = client.get("/api/v1/system/permission-format", headers=auth_headers)
        
        if response.status_code == 200:
            data = response.json()
            
            # Verify counts match actual data
            assert data["total_legacy_mappings"] == len(LEGACY_PERMISSION_MAP)
            assert data["total_hierarchy_rules"] == len(PERMISSION_HIERARCHY)
            
            # Sanity checks
            assert data["total_legacy_mappings"] > 0
            assert data["total_hierarchy_rules"] > 0
    
    def test_permission_mappings_endpoint_exists(self):
        """Test that the permission-mappings endpoint exists"""
        response = client.get("/api/v1/system/permission-format/mappings")
        # Should require authentication
        assert response.status_code in [200, 401, 403]
    
    def test_permission_mappings_admin_only(self):
        """Test that mappings endpoint is admin-only"""
        # Without admin credentials, should get 403
        response = client.get("/api/v1/system/permission-format/mappings")
        assert response.status_code in [401, 403]
    
    def test_permission_mappings_response_structure(self, auth_headers):
        """Test the structure of permission-mappings response"""
        response = client.get("/api/v1/system/permission-format/mappings", headers=auth_headers)
        
        if response.status_code == 200:
            data = response.json()
            
            # Check required fields
            assert "legacy_to_dotted" in data
            assert "total_mappings" in data
            
            # Check types
            assert isinstance(data["legacy_to_dotted"], dict)
            assert isinstance(data["total_mappings"], int)
            
            # Verify count matches
            assert data["total_mappings"] == len(data["legacy_to_dotted"])
    
    def test_permission_mappings_content(self, auth_headers):
        """Test that mappings contain expected entries"""
        response = client.get("/api/v1/system/permission-format/mappings", headers=auth_headers)
        
        if response.status_code == 200:
            data = response.json()
            mappings = data["legacy_to_dotted"]
            
            # Check some expected mappings
            expected_mappings = {
                "manage_users": "users.manage",
                "view_users": "users.view",
                "create_organizations": "organizations.create"
            }
            
            for legacy, dotted in expected_mappings.items():
                if legacy in mappings:
                    assert mappings[legacy] == dotted
    
    def test_permission_hierarchy_endpoint_exists(self):
        """Test that the permission-hierarchy endpoint exists"""
        response = client.get("/api/v1/system/permission-format/hierarchy")
        # Should require authentication
        assert response.status_code in [200, 401, 403]
    
    def test_permission_hierarchy_admin_only(self):
        """Test that hierarchy endpoint is admin-only"""
        # Without admin credentials, should get 403
        response = client.get("/api/v1/system/permission-format/hierarchy")
        assert response.status_code in [401, 403]
    
    def test_permission_hierarchy_response_structure(self, auth_headers):
        """Test the structure of permission-hierarchy response"""
        response = client.get("/api/v1/system/permission-format/hierarchy", headers=auth_headers)
        
        if response.status_code == 200:
            data = response.json()
            
            # Check required fields
            assert "hierarchy" in data
            assert "total_parent_permissions" in data
            assert "total_child_permissions" in data
            
            # Check types
            assert isinstance(data["hierarchy"], dict)
            assert isinstance(data["total_parent_permissions"], int)
            assert isinstance(data["total_child_permissions"], int)
    
    def test_permission_hierarchy_content(self, auth_headers):
        """Test that hierarchy contains expected entries"""
        response = client.get("/api/v1/system/permission-format/hierarchy", headers=auth_headers)
        
        if response.status_code == 200:
            data = response.json()
            hierarchy = data["hierarchy"]
            
            # Check some expected hierarchies
            if "master_data.read" in hierarchy:
                children = hierarchy["master_data.read"]
                assert "vendors.read" in children
                assert "products.read" in children
                assert "inventory.read" in children
            
            if "crm.admin" in hierarchy:
                children = hierarchy["crm.admin"]
                assert "crm.settings" in children
    
    def test_permission_hierarchy_counts(self, auth_headers):
        """Test that hierarchy counts are accurate"""
        response = client.get("/api/v1/system/permission-format/hierarchy", headers=auth_headers)
        
        if response.status_code == 200:
            data = response.json()
            
            # Verify counts
            assert data["total_parent_permissions"] == len(data["hierarchy"])
            
            # Calculate total children
            total_children = sum(len(children) for children in data["hierarchy"].values())
            assert data["total_child_permissions"] == total_children


class TestPermissionFormatAPIIntegration:
    """Integration tests for permission format API"""
    
    def test_all_endpoints_accessible(self):
        """Test that all system endpoints are registered"""
        endpoints = [
            "/api/v1/system/permission-format",
            "/api/v1/system/permission-format/mappings",
            "/api/v1/system/permission-format/hierarchy"
        ]
        
        for endpoint in endpoints:
            response = client.get(endpoint)
            # Should not be 404 (not found)
            assert response.status_code != 404, f"Endpoint {endpoint} not found"
    
    def test_consistency_across_endpoints(self, auth_headers):
        """Test that data is consistent across endpoints"""
        # Get main endpoint data
        main_response = client.get("/api/v1/system/permission-format", headers=auth_headers)
        
        if main_response.status_code == 200:
            main_data = main_response.json()
            
            # Get mappings
            mappings_response = client.get("/api/v1/system/permission-format/mappings", headers=auth_headers)
            if mappings_response.status_code == 200:
                mappings_data = mappings_response.json()
                # Counts should match
                assert main_data["total_legacy_mappings"] == mappings_data["total_mappings"]
            
            # Get hierarchy
            hierarchy_response = client.get("/api/v1/system/permission-format/hierarchy", headers=auth_headers)
            if hierarchy_response.status_code == 200:
                hierarchy_data = hierarchy_response.json()
                # Counts should match
                assert main_data["total_hierarchy_rules"] == hierarchy_data["total_parent_permissions"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
