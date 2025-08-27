"""
Simplified test for JWT configuration validation
"""
import pytest
from app.core.config import Settings
from pydantic import ValidationError

def test_jwt_expiry_validation():
    """Test JWT expiry validation in settings"""
    # Test too low value
    with pytest.raises(ValidationError) as exc_info:
        Settings(ACCESS_TOKEN_EXPIRE_MINUTES=60, DATABASE_URL="sqlite:///test.db")
    assert "must be at least 120 minutes" in str(exc_info.value)
    
    # Test too high value  
    with pytest.raises(ValidationError) as exc_info:
        Settings(ACCESS_TOKEN_EXPIRE_MINUTES=400, DATABASE_URL="sqlite:///test.db")
    assert "must not exceed 300 minutes" in str(exc_info.value)
    
    # Test valid values
    valid_settings = Settings(ACCESS_TOKEN_EXPIRE_MINUTES=180, DATABASE_URL="sqlite:///test.db")
    assert valid_settings.ACCESS_TOKEN_EXPIRE_MINUTES == 180

def test_current_jwt_configuration():
    """Test that current JWT configuration is within required range"""
    from app.core.config import settings
    assert 120 <= settings.ACCESS_TOKEN_EXPIRE_MINUTES <= 300, \
        f"JWT expiry {settings.ACCESS_TOKEN_EXPIRE_MINUTES} is outside required range (120-300 minutes)"

if __name__ == "__main__":
    # Run tests with: python -m pytest tests/test_jwt_config.py -v
    pytest.main([__file__, "-v"])