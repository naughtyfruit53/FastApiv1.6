# tests/test_sla_models.py

"""
Tests for SLA Management models and services.
Validates model structure, relationships, and basic functionality.
"""

import pytest
import sys
import os
from datetime import datetime, timedelta
from unittest.mock import MagicMock

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class TestSLAModels:
    """Test SLA management database models"""
    
    @pytest.fixture(scope="class")
    def mock_dependencies(self):
        """Mock database dependencies for testing"""
        from sqlalchemy.orm import declarative_base
        
        # Mock the app.core.database module
        sys.modules['app.core.database'] = MagicMock()
        sys.modules['app.core.database'].Base = declarative_base()
        
        return True

    def test_sla_policy_model_import(self, mock_dependencies):
        """Test that the SLAPolicy model can be imported successfully."""
        try:
            from app.models.base import SLAPolicy
            print("✅ SLAPolicy model imported successfully")
            assert True
        except Exception as e:
            pytest.fail(f"❌ SLAPolicy model import failed: {e}")

    def test_sla_tracking_model_import(self, mock_dependencies):
        """Test that the SLATracking model can be imported successfully."""
        try:
            from app.models.base import SLATracking
            print("✅ SLATracking model imported successfully")
            assert True
        except Exception as e:
            pytest.fail(f"❌ SLATracking model import failed: {e}")

    def test_sla_schemas_import(self, mock_dependencies):
        """Test that SLA schemas can be imported successfully."""
        try:
            from app.schemas.sla import SLAPolicyCreate, SLATrackingResponse, SLAMetrics
            print("✅ SLA schemas imported successfully")
            assert True
        except Exception as e:
            pytest.fail(f"❌ SLA schemas import failed: {e}")

    def test_sla_service_import(self, mock_dependencies):
        """Test that SLA service can be imported successfully."""
        try:
            from app.services.sla import SLAService
            print("✅ SLA service imported successfully")
            assert True
        except Exception as e:
            pytest.fail(f"❌ SLA service import failed: {e}")

    def test_sla_schema_validation(self, mock_dependencies):
        """Test SLA schema validation."""
        try:
            from app.schemas.sla import SLAPolicyCreate
            
            # Test valid policy creation
            policy_data = {
                "name": "Critical Support",
                "description": "Critical priority support SLA",
                "priority": "urgent",
                "response_time_hours": 1.0,
                "resolution_time_hours": 4.0,
                "escalation_enabled": True,
                "escalation_threshold_percent": 80.0
            }
            
            policy = SLAPolicyCreate(**policy_data)
            assert policy.name == "Critical Support"
            assert policy.response_time_hours == 1.0
            assert policy.escalation_threshold_percent == 80.0
            print("✅ SLA policy schema validation passed")
            
        except Exception as e:
            pytest.fail(f"❌ SLA schema validation failed: {e}")

    def test_model_relationships(self, mock_dependencies):
        """Test that model relationships are properly defined."""
        try:
            from app.models.base import Ticket, SLAPolicy, SLATracking
            
            # Check that Ticket has sla_tracking relationship
            assert hasattr(Ticket, 'sla_tracking')
            
            # Check that SLAPolicy has sla_tracking relationship  
            assert hasattr(SLAPolicy, 'sla_tracking')
            
            # Check that SLATracking has proper relationships
            assert hasattr(SLATracking, 'ticket')
            assert hasattr(SLATracking, 'policy')
            
            print("✅ Model relationships are properly defined")
            
        except Exception as e:
            pytest.fail(f"❌ Model relationship test failed: {e}")


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])