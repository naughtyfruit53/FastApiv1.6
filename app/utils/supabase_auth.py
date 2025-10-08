"""
Supabase Auth API utility module for user management integration.

This module encapsulates Supabase Auth Admin API operations to ensure
users created via FastAPI are also created in Supabase Auth system.
"""

import logging
from typing import Optional, Dict, Any, List
from app.core.config import settings

logger = logging.getLogger(__name__)  # Moved up to be available in except block

# Make supabase optional for testing
try:
    from supabase import create_client, Client
    from supabase.lib.client_options import ClientOptions
    SUPABASE_AVAILABLE = True
except ImportError as e:
    logger.error(f"Supabase import failed: {str(e)}")  # Added logging for import error
    SUPABASE_AVAILABLE = False
    Client = None
    create_client = None
    ClientOptions = None


class SupabaseAuthError(Exception):
    """Custom exception for Supabase Auth operations"""
    pass


class SupabaseAuthService:
    """Service class for Supabase Auth Admin API operations"""
    
    def __init__(self):
        if not SUPABASE_AVAILABLE:
            logger.warning("Supabase library not installed - auth service disabled")
            self.client = None
            return
            
        if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_KEY:
            raise SupabaseAuthError(
                "SUPABASE_URL and SUPABASE_SERVICE_KEY must be configured"
            )
        
        # Create Supabase client with service key for admin operations (updated to v2.x API)
        self.client: Client = create_client(
            settings.SUPABASE_URL, 
            settings.SUPABASE_SERVICE_KEY,
            options=ClientOptions(
                auto_refresh_token=False,
                persist_session=False,
            )
        )
    
    def get_all_users(self) -> List[Dict[str, Any]]:
        """
        Get all users from Supabase Auth.
        
        Returns:
            List of user data dictionaries
            
        Raises:
            SupabaseAuthError: If request fails
        """
        if not self.client:
            logger.warning("Supabase not available - user list skipped")
            return []
            
        try:
            # List all users (paginated; fetch all for small scale) - updated to v2.x pagination
            all_users = []
            page = 1
            per_page = 1000  # Max per page
            while True:
                response = self.client.auth.admin.list_users(page=page, per_page=per_page)
                users = response.users if hasattr(response, 'users') else response if isinstance(response, list) else []
                if not users:
                    break
                for user in users:
                    all_users.append({
                        "id": user.id,
                        "email": user.email,
                        "created_at": user.created_at,
                        "updated_at": user.updated_at,
                        "user_metadata": user.user_metadata or {}
                    })
                if len(users) < per_page:
                    break
                page += 1
            
            logger.info(f"Retrieved {len(all_users)} users from Supabase Auth")
            return all_users
            
        except Exception as e:
            error_msg = f"Failed to get all users from Supabase Auth: {str(e)}"
            logger.error(error_msg)
            raise SupabaseAuthError(error_msg) from e
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Get a user from Supabase Auth by email.
        
        Args:
            email: User email address
            
        Returns:
            User data if found, None otherwise
            
        Raises:
            SupabaseAuthError: If request fails
        """
        if not self.client:
            logger.warning("Supabase not available - user lookup skipped")
            return None
            
        try:
            # List users and find by email (no direct get_by_email, so paginate and search) - updated to v2.x
            page = 1
            per_page = 1000
            while True:
                response = self.client.auth.admin.list_users(page=page, per_page=per_page)
                
                users = response.users if hasattr(response, 'users') else response if isinstance(response, list) else []
                
                for user in users:
                    if user.email.lower() == email.lower():
                        return {
                            "supabase_uuid": user.id,
                            "email": user.email,
                            "created_at": user.created_at,
                            "updated_at": user.updated_at,
                            "user_metadata": user.user_metadata or {}
                        }
                
                if len(users) < per_page:
                    break
                page += 1
            
            return None
            
        except Exception as e:
            error_msg = f"Failed to get user by email {email} from Supabase Auth: {str(e)}"
            logger.error(error_msg)
            raise SupabaseAuthError(error_msg) from e
    
    def create_user(
        self, 
        email: str, 
        password: str, 
        user_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a user in Supabase Auth using Admin API.
        
        Args:
            email: User email address
            password: User password
            user_metadata: Optional metadata to store with the user
            
        Returns:
            Dict containing user data including UUID from Supabase
            
        Raises:
            SupabaseAuthError: If user creation fails
        """
        if not self.client:
            logger.warning("Supabase not available - user creation skipped")
            return {"supabase_uuid": None, "email": email}
            
        try:
            # Use admin API to create user - updated to v2.x (dict still works, but confirm email)
            response = self.client.auth.admin.create_user({
                "email": email,
                "password": password,
                "email_confirm": True,  # Auto-confirm email for admin-created users
                "user_metadata": user_metadata or {}
            })
            
            if not response.user:
                raise SupabaseAuthError("Failed to create user in Supabase Auth")
            
            logger.info(f"Successfully created user {email} in Supabase Auth with ID {response.user.id}")
            
            return {
                "supabase_uuid": response.user.id,
                "email": response.user.email,
                "created_at": response.user.created_at,
                "user_metadata": response.user.user_metadata or {}
            }
            
        except Exception as e:
            error_msg = f"Failed to create user {email} in Supabase Auth: {str(e)}"
            logger.error(error_msg)
            raise SupabaseAuthError(error_msg) from e
    
    def delete_user(self, supabase_uuid: str) -> bool:
        """
        Delete a user from Supabase Auth.
        
        Args:
            supabase_uuid: Supabase user UUID
            
        Returns:
            True if deletion was successful
            
        Raises:
            SupabaseAuthError: If user deletion fails
        """
        if not self.client:
            logger.warning("Supabase not available - user deletion skipped")
            return True
            
        try:
            # Updated to v2.x API, with should_soft_delete=False
            response = self.client.auth.admin.delete_user(supabase_uuid, should_soft_delete=False)
            # Validate the response to ensure deletion was successful
            if hasattr(response, "error") and response.error:
                error_msg = f"Failed to delete user {supabase_uuid} from Supabase Auth: {response.error}"
                logger.error(error_msg)
                raise SupabaseAuthError(error_msg)
            logger.info(f"Successfully deleted user {supabase_uuid} from Supabase Auth")
            return True
            
        except Exception as e:
            error_msg = f"Failed to delete user {supabase_uuid} from Supabase Auth: {str(e)}"
            logger.error(error_msg)
            raise SupabaseAuthError(error_msg) from e
    
    def update_user(
        self, 
        supabase_uuid: str, 
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update a user in Supabase Auth.
        
        Args:
            supabase_uuid: Supabase user UUID
            updates: Dictionary of updates to apply
            
        Returns:
            Updated user data
            
        Raises:
            SupabaseAuthError: If user update fails
        """
        if not self.client:
            logger.warning("Supabase not available - user update skipped")
            return {"supabase_uuid": supabase_uuid}
            
        try:
            # Updated to v2.x API
            response = self.client.auth.admin.update_user_by_id(supabase_uuid, updates)
            
            if not response.user:
                raise SupabaseAuthError("Failed to update user in Supabase Auth")
            
            logger.info(f"Successfully updated user {supabase_uuid} in Supabase Auth")
            
            return {
                "supabase_uuid": response.user.id,
                "email": response.user.email,
                "updated_at": response.user.updated_at,
                "user_metadata": response.user.user_metadata or {}
            }
            
        except Exception as e:
            error_msg = f"Failed to update user {supabase_uuid} in Supabase Auth: {str(e)}"
            logger.error(error_msg)
            raise SupabaseAuthError(error_msg) from e
    
    def get_user(self, supabase_uuid: str) -> Optional[Dict[str, Any]]:
        """
        Get a user from Supabase Auth.
        
        Args:
            supabase_uuid: Supabase user UUID
            
        Returns:
            User data if found, None otherwise
            
        Raises:
            SupabaseAuthError: If request fails
        """
        if not self.client:
            logger.warning("Supabase not available - user lookup skipped")
            return None
            
        try:
            # Updated to v2.x API
            response = self.client.auth.admin.get_user_by_id(supabase_uuid)
            
            if not response.user:
                return None
            
            return {
                "supabase_uuid": response.user.id,
                "email": response.user.email,
                "created_at": response.user.created_at,
                "updated_at": response.user.updated_at,
                "user_metadata": response.user.user_metadata or {}
            }
            
        except Exception as e:
            error_msg = f"Failed to get user {supabase_uuid} from Supabase Auth: {str(e)}"
            logger.error(error_msg)
            raise SupabaseAuthError(error_msg) from e


# Lazy singleton instance for use throughout the application
_supabase_auth_service_instance = None

def get_supabase_auth_service() -> SupabaseAuthService:
    """Get or create the singleton SupabaseAuthService instance"""
    global _supabase_auth_service_instance
    if _supabase_auth_service_instance is None:
        try:
            _supabase_auth_service_instance = SupabaseAuthService()
        except Exception as e:
            logger.warning(f"Failed to initialize Supabase auth service: {e}")
            _supabase_auth_service_instance = None
    return _supabase_auth_service_instance

# Create a proxy object that lazily initializes the service
class SupabaseAuthServiceProxy:
    def __getattr__(self, name):
        service = get_supabase_auth_service()
        if service is None:
            logger.warning(f"Supabase service not available - {name} operation skipped")
            return lambda *args, **kwargs: None
        return getattr(service, name)

supabase_auth_service = SupabaseAuthServiceProxy()