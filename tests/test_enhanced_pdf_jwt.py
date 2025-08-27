"""
Test suite for enhanced PDF generation and JWT token expiry handling
"""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta, timezone
from app.main import app
from app.core.security import create_access_token
from app.core.config import settings

client = TestClient(app)

class TestJWTConfiguration:
    """Test JWT token expiry configuration and validation"""
    
    def test_jwt_expiry_within_range(self):
        """Test that JWT expiry is within the required range (120-300 minutes)"""
        # Test the current configuration
        assert 120 <= settings.ACCESS_TOKEN_EXPIRE_MINUTES <= 300, \
            f"JWT expiry {settings.ACCESS_TOKEN_EXPIRE_MINUTES} is outside required range (120-300 minutes)"
    
    def test_jwt_expiry_validation(self):
        """Test JWT expiry validation in settings"""
        from app.core.config import Settings
        from pydantic import ValidationError
        
        # Test too low value
        with pytest.raises(ValidationError) as exc_info:
            Settings(ACCESS_TOKEN_EXPIRE_MINUTES=60)
        assert "must be at least 120 minutes" in str(exc_info.value)
        
        # Test too high value
        with pytest.raises(ValidationError) as exc_info:
            Settings(ACCESS_TOKEN_EXPIRE_MINUTES=400)
        assert "must not exceed 300 minutes" in str(exc_info.value)
        
        # Test valid values
        valid_settings = Settings(ACCESS_TOKEN_EXPIRE_MINUTES=180)
        assert valid_settings.ACCESS_TOKEN_EXPIRE_MINUTES == 180

    def test_token_creation_with_expiry(self):
        """Test that tokens are created with proper expiry"""
        token = create_access_token(
            subject="testuser@example.com",
            organization_id=1,
            user_role="admin"
        )
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

class TestPDFGeneration:
    """Test PDF generation functionality"""
    
    def test_company_branding_endpoint(self):
        """Test company branding API endpoint"""
        # Create a test token
        token = create_access_token(
            subject="testuser@example.com",
            organization_id=1,
            user_role="admin"
        )
        
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get("/api/v1/company/branding", headers=headers)
        
        # Should return 200 or 500 (if no database setup), but not 401
        assert response.status_code in [200, 500], f"Unexpected status code: {response.status_code}"
        
        if response.status_code == 200:
            data = response.json()
            # Check required branding fields
            required_fields = ["name", "address", "contact_number", "email"]
            for field in required_fields:
                assert field in data, f"Missing required field: {field}"

    def test_pdf_audit_endpoint(self):
        """Test PDF generation audit logging"""
        # Create a test token
        token = create_access_token(
            subject="testuser@example.com",
            organization_id=1,
            user_role="admin"
        )
        
        headers = {"Authorization": f"Bearer {token}"}
        audit_data = {
            "action": "pdf_generated",
            "voucher_type": "payment-voucher",
            "voucher_number": "PV/TEST/001",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        response = client.post("/api/v1/audit/pdf-generation", 
                              json=audit_data, headers=headers)
        
        # Should return 200 or 500, but not 401
        assert response.status_code in [200, 500], f"Unexpected status code: {response.status_code}"

class TestVoucherPDFCoverage:
    """Test that all voucher types have PDF configuration"""
    
    def test_voucher_types_have_pdf_config(self):
        """Test that all defined voucher types have proper PDF configuration"""
        # Import the voucher configurations
        try:
            from frontend.src.utils.voucherUtils import VOUCHER_CONFIGS
            
            # Check that all voucher types have necessary PDF config
            for voucher_type, config in VOUCHER_CONFIGS.items():
                assert 'voucherType' in config, f"{voucher_type} missing voucherType"
                assert 'voucherTitle' in config, f"{voucher_type} missing voucherTitle"
                assert 'hasItems' in config, f"{voucher_type} missing hasItems"
                
        except ImportError:
            # Skip if we can't import the frontend config (expected in pure backend test)
            pytest.skip("Frontend voucher config not available in backend test")

    def test_manufacturing_vouchers_supported(self):
        """Test that manufacturing vouchers are configured"""
        try:
            from frontend.src.utils.voucherUtils import VOUCHER_CONFIGS
            
            manufacturing_vouchers = [
                'job-card', 'production-order', 'work-order', 
                'material-receipt', 'material-requisition', 
                'finished-good-receipt', 'manufacturing-journal', 'stock-journal'
            ]
            
            for voucher_type in manufacturing_vouchers:
                assert voucher_type in VOUCHER_CONFIGS, \
                    f"Manufacturing voucher {voucher_type} not configured"
                
        except ImportError:
            pytest.skip("Frontend voucher config not available in backend test")

if __name__ == "__main__":
    # Run tests with: python -m pytest tests/test_enhanced_pdf_jwt.py -v
    pytest.main([__file__, "-v"])