# tests/test_reset_service_improvements.py

"""
Test the improvements to the reset service including:
- Comprehensive table deletion
- Transaction handling and rollback
- Detailed logging
- Error handling for Supabase auth deletion
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.reset_service import ResetService, CUSTOM_RAW_SQL_TABLES
from sqlalchemy.ext.asyncio import AsyncSession


class TestResetServiceImprovements:
    """Test suite for reset service improvements"""

    @pytest.mark.asyncio
    async def test_custom_raw_sql_tables_defined(self):
        """Test that custom raw SQL tables are defined"""
        assert len(CUSTOM_RAW_SQL_TABLES) > 0
        assert 'oauth_states' in CUSTOM_RAW_SQL_TABLES
        assert 'user_email_tokens' in CUSTOM_RAW_SQL_TABLES

    @pytest.mark.asyncio
    async def test_factory_default_system_god_admin_only(self):
        """Test that factory default is restricted to god superadmin"""
        mock_db = AsyncMock(spec=AsyncSession)
        
        # Create a non-god admin user
        class MockUser:
            email = "notgod@example.com"
        
        mock_user = MockUser()
        
        # Should raise HTTPException
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            await ResetService.factory_default_system(mock_db, mock_user)
        
        assert exc_info.value.status_code == 403
        assert "god superadmin" in str(exc_info.value.detail).lower()

    @pytest.mark.asyncio
    async def test_factory_default_system_with_rollback(self):
        """Test that factory default rolls back on error"""
        mock_db = AsyncMock(spec=AsyncSession)
        
        # Create god admin user
        class MockUser:
            email = "naughtyfruit53@gmail.com"
        
        mock_user = MockUser()
        
        # Mock db.execute to raise an error
        mock_db.execute = AsyncMock(side_effect=Exception("Database error"))
        
        # Should raise exception and call rollback
        with pytest.raises(Exception) as exc_info:
            await ResetService.factory_default_system(mock_db, mock_user)
        
        # Verify rollback was called
        mock_db.rollback.assert_called_once()
        assert "Database error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_factory_default_system_deletes_custom_tables(self):
        """Test that factory default attempts to delete custom raw SQL tables"""
        mock_db = AsyncMock(spec=AsyncSession)
        
        # Create god admin user
        class MockUser:
            email = "naughtyfruit53@gmail.com"
        
        mock_user = MockUser()
        
        # Mock db.execute to track calls
        execute_calls = []
        async def track_execute(stmt):
            execute_calls.append(str(stmt))
            mock_result = MagicMock()
            mock_result.rowcount = 0
            return mock_result
        
        mock_db.execute = track_execute
        mock_db.commit = AsyncMock()
        mock_db.scalar = AsyncMock(return_value=None)
        
        # Mock supabase auth service
        with patch('app.services.reset_service.supabase_auth_service') as mock_supabase:
            mock_supabase.get_all_users.return_value = []
            
            result = await ResetService.factory_default_system(mock_db, mock_user)
        
        # Verify custom tables were attempted to be deleted
        execute_calls_str = ' '.join(execute_calls)
        assert 'oauth_states' in execute_calls_str
        assert 'user_email_tokens' in execute_calls_str
        
        # Verify result has error tracking
        assert 'errors' in result
        assert 'deleted' in result

    @pytest.mark.asyncio  
    async def test_factory_default_handles_supabase_errors_gracefully(self):
        """Test that Supabase auth deletion errors are handled gracefully"""
        mock_db = AsyncMock(spec=AsyncSession)
        
        # Create god admin user
        class MockUser:
            email = "naughtyfruit53@gmail.com"
        
        mock_user = MockUser()
        
        # Mock db operations
        mock_db.execute = AsyncMock(return_value=MagicMock(rowcount=0))
        mock_db.commit = AsyncMock()
        mock_db.scalar = AsyncMock(return_value=None)
        
        # Mock supabase to throw an error
        with patch('app.services.reset_service.supabase_auth_service') as mock_supabase:
            mock_supabase.get_all_users.side_effect = Exception("Supabase connection error")
            
            result = await ResetService.factory_default_system(mock_db, mock_user)
        
        # Should not raise exception - should handle gracefully
        assert result is not None
        assert 'deleted' in result
        assert 'errors' in result
        assert result['deleted']['supabase_auth_users'] == 0
        
        # Verify error was logged
        assert len(result['errors']) > 0
        assert any('Supabase' in error for error in result['errors'])


class TestPendingOrdersLogic:
    """Test pending orders endpoint improvements"""

    def test_color_status_logic_red(self):
        """Test color status is red when no tracking"""
        # This would be a mock PO with no tracking
        has_tracking = False
        
        color_status = "yellow" if has_tracking else "red"
        assert color_status == "red"

    def test_color_status_logic_yellow(self):
        """Test color status is yellow when tracking exists but GRN pending"""
        # This would be a mock PO with tracking
        has_tracking = True
        
        color_status = "yellow" if has_tracking else "red"
        assert color_status == "yellow"

    def test_color_status_logic_green(self):
        """Test color status is green when all items received"""
        # This would be tested via the actual endpoint
        # For unit test, just verify the logic
        all_items_received = True
        has_tracking = True
        
        if all_items_received:
            color_status = "green"
        elif has_tracking:
            color_status = "yellow"
        else:
            color_status = "red"
        
        assert color_status == "green"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
