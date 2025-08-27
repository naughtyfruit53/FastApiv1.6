"""
Test for ticket management models for Service CRM.
Validates model structure, relationships, constraints, and basic functionality.
"""
import pytest
import sys
import os
from datetime import datetime
from unittest.mock import MagicMock

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class TestTicketManagementModels:
    """Test ticket management database models"""
    
    @pytest.fixture(scope="class")
    def mock_dependencies(self):
        """Mock database dependencies for testing"""
        from sqlalchemy.orm import declarative_base
        
        # Mock the app.core.database module
        sys.modules['app.core.database'] = MagicMock()
        sys.modules['app.core.database'].Base = declarative_base()
        
        return True

    def test_ticket_model_import(self, mock_dependencies):
        """Test that the Ticket model can be imported successfully."""
        try:
            from app.models.base import Ticket
            print("✅ Ticket model imported successfully")
            assert True
        except Exception as e:
            pytest.fail(f"❌ Ticket model import failed: {e}")

    def test_ticket_history_model_import(self, mock_dependencies):
        """Test that the TicketHistory model can be imported successfully."""
        try:
            from app.models.base import TicketHistory
            print("✅ TicketHistory model imported successfully")
            assert True
        except Exception as e:
            pytest.fail(f"❌ TicketHistory model import failed: {e}")

    def test_ticket_attachment_model_import(self, mock_dependencies):
        """Test that the TicketAttachment model can be imported successfully."""
        try:
            from app.models.base import TicketAttachment
            print("✅ TicketAttachment model imported successfully")
            assert True
        except Exception as e:
            pytest.fail(f"❌ TicketAttachment model import failed: {e}")

    def test_all_ticket_models_import(self, mock_dependencies):
        """Test that all ticket models can be imported together."""
        try:
            from app.models.base import Ticket, TicketHistory, TicketAttachment
            print("✅ All ticket models imported successfully")
            assert True
        except Exception as e:
            pytest.fail(f"❌ Ticket models import failed: {e}")

    def test_ticket_model_structure(self, mock_dependencies):
        """Test Ticket model has required fields and relationships."""
        try:
            from app.models.base import Ticket
            
            # Check that the model has required attributes
            required_fields = [
                'id', 'organization_id', 'ticket_number', 'customer_id',
                'title', 'description', 'status', 'priority', 'ticket_type',
                'created_at', 'updated_at'
            ]
            
            for field in required_fields:
                assert hasattr(Ticket, field), f"Ticket model missing field: {field}"
            
            # Check optional fields
            optional_fields = [
                'assigned_to_id', 'created_by_id', 'resolution', 'resolved_at',
                'closed_at', 'due_date', 'estimated_hours', 'actual_hours',
                'customer_rating', 'customer_feedback'
            ]
            
            for field in optional_fields:
                assert hasattr(Ticket, field), f"Ticket model missing optional field: {field}"
            
            # Check relationships
            relationship_fields = [
                'organization', 'customer', 'assigned_to', 'created_by',
                'history', 'attachments'
            ]
            
            for field in relationship_fields:
                assert hasattr(Ticket, field), f"Ticket model missing relationship: {field}"
            
            print("✅ Ticket model structure validation passed")
            
        except Exception as e:
            pytest.fail(f"❌ Ticket model structure validation failed: {e}")

    def test_ticket_history_model_structure(self, mock_dependencies):
        """Test TicketHistory model has required fields and relationships."""
        try:
            from app.models.base import TicketHistory
            
            # Check that the model has required attributes
            required_fields = [
                'id', 'organization_id', 'ticket_id', 'action', 'created_at'
            ]
            
            for field in required_fields:
                assert hasattr(TicketHistory, field), f"TicketHistory model missing field: {field}"
            
            # Check optional fields
            optional_fields = [
                'field_changed', 'old_value', 'new_value', 'comment', 'changed_by_id'
            ]
            
            for field in optional_fields:
                assert hasattr(TicketHistory, field), f"TicketHistory model missing optional field: {field}"
            
            # Check relationships
            relationship_fields = ['organization', 'ticket', 'changed_by']
            
            for field in relationship_fields:
                assert hasattr(TicketHistory, field), f"TicketHistory model missing relationship: {field}"
            
            print("✅ TicketHistory model structure validation passed")
            
        except Exception as e:
            pytest.fail(f"❌ TicketHistory model structure validation failed: {e}")

    def test_ticket_attachment_model_structure(self, mock_dependencies):
        """Test TicketAttachment model has required fields and relationships."""
        try:
            from app.models.base import TicketAttachment
            
            # Check that the model has required attributes
            required_fields = [
                'id', 'organization_id', 'ticket_id', 'filename', 'original_filename',
                'file_path', 'file_size', 'content_type', 'file_type', 'created_at'
            ]
            
            for field in required_fields:
                assert hasattr(TicketAttachment, field), f"TicketAttachment model missing field: {field}"
            
            # Check optional fields
            optional_fields = ['uploaded_by_id', 'updated_at']
            
            for field in optional_fields:
                assert hasattr(TicketAttachment, field), f"TicketAttachment model missing optional field: {field}"
            
            # Check relationships
            relationship_fields = ['organization', 'ticket', 'uploaded_by']
            
            for field in relationship_fields:
                assert hasattr(TicketAttachment, field), f"TicketAttachment model missing relationship: {field}"
            
            print("✅ TicketAttachment model structure validation passed")
            
        except Exception as e:
            pytest.fail(f"❌ TicketAttachment model structure validation failed: {e}")

    def test_model_constraints(self, mock_dependencies):
        """Test that model constraints are properly defined"""
        try:
            from app.models.base import Ticket, TicketHistory, TicketAttachment
            
            # Test Ticket constraints
            ticket_constraints = Ticket.__table__.constraints
            unique_constraints = [c for c in ticket_constraints if hasattr(c, 'columns')]
            assert any('ticket_number' in [col.name for col in c.columns] for c in unique_constraints), \
                "Ticket should have unique constraint on organization_id + ticket_number"
            
            # Test TicketHistory table name
            assert TicketHistory.__tablename__ == "ticket_history", \
                "TicketHistory should use 'ticket_history' table name"
            
            # Test TicketAttachment table name
            assert TicketAttachment.__tablename__ == "ticket_attachments", \
                "TicketAttachment should use 'ticket_attachments' table name"
            
            print("✅ Model constraints validation passed")
            
        except Exception as e:
            pytest.fail(f"❌ Model constraints validation failed: {e}")

    def test_model_relationships(self, mock_dependencies):
        """Test model relationships are properly defined"""
        try:
            from app.models.base import Ticket, TicketHistory, TicketAttachment
            
            # Test Ticket relationships
            assert hasattr(Ticket, 'organization'), "Ticket should have organization relationship"
            assert hasattr(Ticket, 'customer'), "Ticket should have customer relationship"
            assert hasattr(Ticket, 'assigned_to'), "Ticket should have assigned_to relationship"
            assert hasattr(Ticket, 'created_by'), "Ticket should have created_by relationship"
            assert hasattr(Ticket, 'history'), "Ticket should have history relationship"
            assert hasattr(Ticket, 'attachments'), "Ticket should have attachments relationship"
            
            # Test TicketHistory relationships
            assert hasattr(TicketHistory, 'organization'), "TicketHistory should have organization relationship"
            assert hasattr(TicketHistory, 'ticket'), "TicketHistory should have ticket relationship"
            assert hasattr(TicketHistory, 'changed_by'), "TicketHistory should have changed_by relationship"
            
            # Test TicketAttachment relationships
            assert hasattr(TicketAttachment, 'organization'), "TicketAttachment should have organization relationship"
            assert hasattr(TicketAttachment, 'ticket'), "TicketAttachment should have ticket relationship"
            assert hasattr(TicketAttachment, 'uploaded_by'), "TicketAttachment should have uploaded_by relationship"
            
            print("✅ Model relationships validation passed")
            
        except Exception as e:
            pytest.fail(f"❌ Model relationships validation failed: {e}")

    def test_model_indexes(self, mock_dependencies):
        """Test that model indexes are properly defined"""
        try:
            from app.models.base import Ticket, TicketHistory, TicketAttachment
            
            # Test Ticket has proper table args (indexes)
            assert hasattr(Ticket, '__table_args__'), "Ticket should have __table_args__ for indexes"
            
            # Test TicketHistory has proper table args (indexes)
            assert hasattr(TicketHistory, '__table_args__'), "TicketHistory should have __table_args__ for indexes"
            
            # Test TicketAttachment has proper table args (indexes)
            assert hasattr(TicketAttachment, '__table_args__'), "TicketAttachment should have __table_args__ for indexes"
            
            print("✅ Model indexes validation passed")
            
        except Exception as e:
            pytest.fail(f"❌ Model indexes validation failed: {e}")

    def test_models_in_init_file(self, mock_dependencies):
        """Test that ticket models are properly exported in __init__.py"""
        try:
            from app.models import Ticket, TicketHistory, TicketAttachment
            
            # All models should be importable from the package
            assert Ticket is not None, "Ticket should be importable from app.models"
            assert TicketHistory is not None, "TicketHistory should be importable from app.models"
            assert TicketAttachment is not None, "TicketAttachment should be importable from app.models"
            
            print("✅ Ticket models are properly exported in __init__.py")
            
        except ImportError as e:
            pytest.fail(f"❌ Ticket models not properly exported in __init__.py: {e}")

    def test_multi_tenant_support(self, mock_dependencies):
        """Test that all ticket models support multi-tenancy with organization_id"""
        try:
            from app.models.base import Ticket, TicketHistory, TicketAttachment
            
            # All models should have organization_id field
            models = [Ticket, TicketHistory, TicketAttachment]
            for model in models:
                assert hasattr(model, 'organization_id'), f"{model.__name__} should have organization_id field"
                
            print("✅ Multi-tenant support validation passed")
            
        except Exception as e:
            pytest.fail(f"❌ Multi-tenant support validation failed: {e}")


if __name__ == "__main__":
    # Run tests individually for debugging
    test_instance = TestTicketManagementModels()
    
    try:
        # Mock dependencies
        from sqlalchemy.orm import declarative_base
        sys.modules['app.core.database'] = MagicMock()
        sys.modules['app.core.database'].Base = declarative_base()
        mock_deps = True
        
        # Run all tests
        test_instance.test_ticket_model_import(mock_deps)
        test_instance.test_ticket_history_model_import(mock_deps)
        test_instance.test_ticket_attachment_model_import(mock_deps)
        test_instance.test_all_ticket_models_import(mock_deps)
        test_instance.test_ticket_model_structure(mock_deps)
        test_instance.test_ticket_history_model_structure(mock_deps)
        test_instance.test_ticket_attachment_model_structure(mock_deps)
        test_instance.test_model_constraints(mock_deps)
        test_instance.test_model_relationships(mock_deps)
        test_instance.test_model_indexes(mock_deps)
        test_instance.test_models_in_init_file(mock_deps)
        test_instance.test_multi_tenant_support(mock_deps)
        
        print("\n🎉 All ticket management model tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
        sys.exit(1)