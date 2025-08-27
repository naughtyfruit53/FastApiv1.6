"""
Test for new customer interaction and segment models.
Validates model structure, relationships, and migration compatibility.
"""
# import pytest  # Not required for this test
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_customer_models_import():
    """Test that the new customer models can be imported successfully."""
    try:
        # Import with minimal dependencies by mocking the database Base
        from sqlalchemy.orm import declarative_base
        from sqlalchemy import create_engine
        
        # Mock the Base class
        import sys
        from unittest.mock import MagicMock
        
        # Mock the app.core.database module
        sys.modules['app.core.database'] = MagicMock()
        sys.modules['app.core.database'].Base = declarative_base()
        
        # Now import the models
        from app.models.base import Customer, CustomerInteraction, CustomerSegment
        
        print("✅ All customer models imported successfully")
        return True
    except Exception as e:
        print(f"❌ Model import failed: {e}")
        return False

def test_customer_interaction_model_structure():
    """Test CustomerInteraction model has required fields and relationships."""
    try:
        # Mock dependencies
        from sqlalchemy.orm import declarative_base
        import sys
        from unittest.mock import MagicMock
        
        sys.modules['app.core.database'] = MagicMock()
        sys.modules['app.core.database'].Base = declarative_base()
        
        from app.models.base import CustomerInteraction
        
        # Check that the model has required attributes
        required_fields = [
            'id', 'organization_id', 'customer_id', 'interaction_type', 
            'subject', 'description', 'status', 'interaction_date', 
            'created_by', 'created_at', 'updated_at'
        ]
        
        for field in required_fields:
            assert hasattr(CustomerInteraction, field), f"Missing field: {field}"
        
        # Check table name
        assert CustomerInteraction.__tablename__ == "customer_interactions"
        
        print("✅ CustomerInteraction model structure is valid")
        return True
    except Exception as e:
        print(f"❌ CustomerInteraction model validation failed: {e}")
        return False

def test_customer_segment_model_structure():
    """Test CustomerSegment model has required fields and relationships."""
    try:
        # Mock dependencies
        from sqlalchemy.orm import declarative_base
        import sys
        from unittest.mock import MagicMock
        
        sys.modules['app.core.database'] = MagicMock()
        sys.modules['app.core.database'].Base = declarative_base()
        
        from app.models.base import CustomerSegment
        
        # Check that the model has required attributes
        required_fields = [
            'id', 'organization_id', 'customer_id', 'segment_name', 
            'segment_value', 'segment_description', 'is_active', 'assigned_date',
            'assigned_by', 'created_at', 'updated_at'
        ]
        
        for field in required_fields:
            assert hasattr(CustomerSegment, field), f"Missing field: {field}"
        
        # Check table name
        assert CustomerSegment.__tablename__ == "customer_segments"
        
        print("✅ CustomerSegment model structure is valid")
        return True
    except Exception as e:
        print(f"❌ CustomerSegment model validation failed: {e}")
        return False

def test_migration_file_exists():
    """Test that the migration file exists and is properly structured."""
    migration_path = os.path.join(
        os.path.dirname(__file__), 
        '..', 
        'migrations', 
        'versions', 
        'b4f8c2d1a9e0_add_customer_interactions_and_segments.py'
    )
    
    assert os.path.exists(migration_path), "Migration file does not exist"
    
    # Read migration content and check for key components
    with open(migration_path, 'r') as f:
        content = f.read()
    
    required_components = [
        'def upgrade()',
        'def downgrade()', 
        'customer_interactions',
        'customer_segments',
        'ForeignKeyConstraint',
        'organization_id',
        'customer_id'
    ]
    
    for component in required_components:
        assert component in content, f"Missing migration component: {component}"
    
    print("✅ Migration file is properly structured")
    return True

def test_model_relationships():
    """Test that the Customer model has relationships to new models."""
    try:
        # Mock dependencies
        from sqlalchemy.orm import declarative_base
        import sys
        from unittest.mock import MagicMock
        
        sys.modules['app.core.database'] = MagicMock()
        sys.modules['app.core.database'].Base = declarative_base()
        
        from app.models.base import Customer
        
        # Check that Customer model has relationships to new models
        assert hasattr(Customer, 'interactions'), "Customer missing interactions relationship"
        assert hasattr(Customer, 'segments'), "Customer missing segments relationship"
        
        print("✅ Customer model relationships are properly defined")
        return True
    except Exception as e:
        print(f"❌ Customer model relationship validation failed: {e}")
        return False

if __name__ == "__main__":
    """Run all tests when executed directly."""
    print("Running customer models validation tests...")
    
    tests = [
        test_customer_models_import,
        test_customer_interaction_model_structure,
        test_customer_segment_model_structure,
        test_migration_file_exists,
        test_model_relationships
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All customer model tests passed!")
        exit(0)
    else:
        print("⚠️  Some tests failed")
        exit(1)