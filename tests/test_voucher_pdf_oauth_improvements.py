"""
Tests for Voucher PDF Generation and OAuth Token Management Improvements
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models.oauth_models import UserEmailToken, OAuthProvider, TokenStatus
from app.services.oauth_service import OAuth2Service


class TestVoucherPDFEndpoints:
    """Test new PDF generation endpoints for vouchers"""
    
    def test_purchase_order_pdf_endpoint_exists(self):
        """Verify purchase_order PDF endpoint is accessible"""
        # This is a smoke test to ensure the endpoint exists
        from app.api.v1.vouchers.purchase_order import router
        
        # Check if the PDF route is registered
        routes = [route.path for route in router.routes]
        assert any("pdf" in path for path in routes), "Purchase order PDF endpoint should exist"
    
    def test_purchase_voucher_pdf_endpoint_exists(self):
        """Verify purchase_voucher PDF endpoint is accessible"""
        from app.api.v1.vouchers.purchase_voucher import router
        
        routes = [route.path for route in router.routes]
        assert any("pdf" in path for path in routes), "Purchase voucher PDF endpoint should exist"
    
    def test_sales_return_pdf_endpoint_exists(self):
        """Verify sales_return PDF endpoint is accessible"""
        from app.api.v1.vouchers.sales_return import router
        
        routes = [route.path for route in router.routes]
        assert any("pdf" in path for path in routes), "Sales return PDF endpoint should exist"
    
    def test_purchase_return_pdf_endpoint_exists(self):
        """Verify purchase_return PDF endpoint is accessible"""
        from app.api.v1.vouchers.purchase_return import router
        
        routes = [route.path for route in router.routes]
        assert any("pdf" in path for path in routes), "Purchase return PDF endpoint should exist"


class TestOAuthTokenManagementImprovements:
    """Test OAuth token management improvements"""
    
    @pytest.mark.asyncio
    async def test_get_valid_token_prevents_refresh_failed_reuse(self):
        """Test that REFRESH_FAILED tokens cannot be reused"""
        # Mock database
        db_mock = AsyncMock()
        
        # Create a token with REFRESH_FAILED status
        token = UserEmailToken(
            id=1,
            user_id=1,
            organization_id=1,
            provider=OAuthProvider.GOOGLE,
            email_address="test@example.com",
            status=TokenStatus.REFRESH_FAILED,
            last_sync_error="Previous refresh failed"
        )
        
        # Mock database query
        result_mock = AsyncMock()
        result_mock.scalar_one_or_none.return_value = token
        db_mock.execute.return_value = result_mock
        
        oauth_service = OAuth2Service(db_mock)
        
        # Should return None for REFRESH_FAILED tokens
        result = await oauth_service.get_valid_token(1)
        assert result is None, "REFRESH_FAILED tokens should not be reused"
    
    @pytest.mark.asyncio
    async def test_get_valid_token_prevents_revoked_reuse(self):
        """Test that REVOKED tokens cannot be reused"""
        # Mock database
        db_mock = AsyncMock()
        
        # Create a revoked token
        token = UserEmailToken(
            id=1,
            user_id=1,
            organization_id=1,
            provider=OAuthProvider.GOOGLE,
            email_address="test@example.com",
            status=TokenStatus.REVOKED
        )
        
        # Mock database query
        result_mock = AsyncMock()
        result_mock.scalar_one_or_none.return_value = token
        db_mock.execute.return_value = result_mock
        
        oauth_service = OAuth2Service(db_mock)
        
        # Should return None for REVOKED tokens
        result = await oauth_service.get_valid_token(1)
        assert result is None, "REVOKED tokens should not be reused"
    
    @pytest.mark.asyncio
    async def test_refresh_token_marks_as_failed_on_error(self):
        """Test that refresh_token marks tokens as REFRESH_FAILED on error"""
        # Mock database
        db_mock = AsyncMock()
        
        # Create an active but expired token with no refresh token
        token = UserEmailToken(
            id=1,
            user_id=1,
            organization_id=1,
            provider=OAuthProvider.GOOGLE,
            email_address="test@example.com",
            status=TokenStatus.ACTIVE,
            refresh_token_encrypted=None  # No refresh token
        )
        
        # Mock database query
        result_mock = AsyncMock()
        result_mock.scalar_one_or_none.return_value = token
        db_mock.execute.return_value = result_mock
        
        oauth_service = OAuth2Service(db_mock)
        
        # Should fail and mark token as REFRESH_FAILED
        result = await oauth_service.refresh_token(1)
        assert result is False, "Refresh should fail when no refresh token is available"
        assert token.status == TokenStatus.REFRESH_FAILED, "Token should be marked as REFRESH_FAILED"
        assert token.last_sync_error is not None, "Error message should be set"
    
    @pytest.mark.asyncio
    async def test_get_valid_token_allows_active_tokens(self):
        """Test that active, non-expired tokens are returned"""
        # Mock database
        db_mock = AsyncMock()
        
        # Create an active, non-expired token
        token = UserEmailToken(
            id=1,
            user_id=1,
            organization_id=1,
            provider=OAuthProvider.GOOGLE,
            email_address="test@example.com",
            status=TokenStatus.ACTIVE,
            expires_at=datetime.utcnow() + timedelta(hours=1),  # Not expired
            access_token_encrypted=b"encrypted_token"
        )
        
        # Mock is_expired to return False
        with patch.object(UserEmailToken, 'is_expired', return_value=False):
            # Mock database query
            result_mock = AsyncMock()
            result_mock.scalar_one_or_none.return_value = token
            db_mock.execute.return_value = result_mock
            
            oauth_service = OAuth2Service(db_mock)
            
            # Should return the token
            result = await oauth_service.get_valid_token(1)
            assert result is not None, "Active, non-expired tokens should be returned"
            assert result.id == token.id
    
    def test_sync_get_valid_token_prevents_refresh_failed_reuse(self):
        """Test that sync version also prevents REFRESH_FAILED token reuse"""
        # Mock database
        db_mock = Mock()
        
        # Create a token with REFRESH_FAILED status
        token = UserEmailToken(
            id=1,
            user_id=1,
            organization_id=1,
            provider=OAuthProvider.GOOGLE,
            email_address="test@example.com",
            status=TokenStatus.REFRESH_FAILED,
            last_sync_error="Previous refresh failed"
        )
        
        # Mock database query
        result_mock = Mock()
        result_mock.scalar_one_or_none.return_value = token
        db_mock.execute.return_value = result_mock
        
        oauth_service = OAuth2Service()
        
        # Should return None for REFRESH_FAILED tokens
        result = oauth_service.sync_get_valid_token(1, db_mock)
        assert result is None, "REFRESH_FAILED tokens should not be reused in sync version"


class TestProformaInvoiceRevisionSystem:
    """Test proforma invoice revision numbering"""
    
    def test_proforma_invoice_has_func_import(self):
        """Verify that proforma_invoice.py has func import"""
        import ast
        import inspect
        from app.api.v1.vouchers import proforma_invoice
        
        # Get the source code
        source = inspect.getsource(proforma_invoice)
        
        # Parse the source code
        tree = ast.parse(source)
        
        # Check for func import
        func_imported = False
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.module == 'sqlalchemy':
                    for alias in node.names:
                        if alias.name == 'func':
                            func_imported = True
                            break
        
        assert func_imported, "proforma_invoice.py should import func from sqlalchemy"
    
    def test_sales_order_has_func_import(self):
        """Verify that sales_order.py has func import"""
        import ast
        import inspect
        from app.api.v1.vouchers import sales_order
        
        # Get the source code
        source = inspect.getsource(sales_order)
        
        # Parse the source code
        tree = ast.parse(source)
        
        # Check for func import
        func_imported = False
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.module == 'sqlalchemy':
                    for alias in node.names:
                        if alias.name == 'func':
                            func_imported = True
                            break
        
        assert func_imported, "sales_order.py should import func from sqlalchemy"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
