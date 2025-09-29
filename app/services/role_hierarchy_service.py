# app/services/role_hierarchy_service.py

from sqlalchemy.orm import Session
from typing import Optional, List
import logging

from app.models import User, OrganizationSettings

logger = logging.getLogger(__name__)

class RoleHierarchyService:
    """Service for handling role hierarchy and email BCC logic"""
    
    ROLE_HIERARCHY = {
        "executive": "manager",
        "manager": "management",
        "management": None  # Top level - no BCC
    }
    
    def __init__(self):
        pass
    
    def get_bcc_recipients_for_user(self, db: Session, sender_user: User) -> List[str]:
        """
        Get BCC recipients for a user based on their role and organization settings.
        
        Args:
            db: Database session
            sender_user: User sending the email
            
        Returns:
            List of email addresses to BCC
        """
        try:
            # Check if Mail 1 Level Up is enabled for the organization
            if not self._is_mail_1_level_up_enabled(db, sender_user.organization_id):
                return []
            
            # Get the next level up role
            next_role = self.ROLE_HIERARCHY.get(sender_user.role)
            if not next_role:
                # User is at top level (management) - no BCC
                return []
            
            # Get users with the next level up role in the same organization
            upper_level_users = self._get_users_by_role(db, sender_user.organization_id, next_role)
            
            # Handle specific role logic
            if sender_user.role == "executive":
                # Executive should BCC their assigned manager
                bcc_users = self._get_assigned_manager(db, sender_user)
            elif sender_user.role == "manager":
                # Manager should BCC all management users
                bcc_users = upper_level_users
            else:
                # Default: BCC all users of the next level up
                bcc_users = upper_level_users
            
            # Extract email addresses
            bcc_emails = [user.email for user in bcc_users if user.email and user.is_active]
            
            logger.info(f"BCC recipients for user {sender_user.id} ({sender_user.role}): {bcc_emails}")
            return bcc_emails
            
        except Exception as e:
            logger.error(f"Error getting BCC recipients for user {sender_user.id}: {str(e)}")
            return []
    
    def _is_mail_1_level_up_enabled(self, db: Session, organization_id: int) -> bool:
        """Check if Mail 1 Level Up is enabled for the organization"""
        try:
            settings = db.query(OrganizationSettings).filter(
                OrganizationSettings.organization_id == organization_id
            ).first()
            
            if not settings:
                return False
                
            return settings.mail_1_level_up_enabled
            
        except Exception as e:
            logger.error(f"Error checking Mail 1 Level Up setting for org {organization_id}: {str(e)}")
            return False
    
    def _get_users_by_role(self, db: Session, organization_id: int, role: str) -> List[User]:
        """Get all active users with a specific role in the organization"""
        try:
            return db.query(User).filter(
                User.organization_id == organization_id,
                User.role == role,
                User.is_active == True
            ).all()
            
        except Exception as e:
            logger.error(f"Error getting users by role {role} for org {organization_id}: {str(e)}")
            return []
    
    def _get_assigned_manager(self, db: Session, executive_user: User) -> List[User]:
        """Get the assigned manager for an executive user"""
        try:
            if not executive_user.reporting_manager_id:
                # No assigned manager, fallback to all managers in organization
                return self._get_users_by_role(db, executive_user.organization_id, "manager")
            
            # Get the specific assigned manager
            manager = db.query(User).filter(
                User.id == executive_user.reporting_manager_id,
                User.is_active == True
            ).first()
            
            if manager:
                return [manager]
            else:
                # Assigned manager not found or inactive, fallback to all managers
                return self._get_users_by_role(db, executive_user.organization_id, "manager")
                
        except Exception as e:
            logger.error(f"Error getting assigned manager for user {executive_user.id}: {str(e)}")
            # Fallback to all managers in organization
            return self._get_users_by_role(db, executive_user.organization_id, "manager")
    
    def validate_role_hierarchy(self, user_role: str) -> bool:
        """Validate if a role is part of the hierarchy"""
        return user_role in self.ROLE_HIERARCHY
    
    def get_next_level_role(self, current_role: str) -> Optional[str]:
        """Get the next level up role for a given role"""
        return self.ROLE_HIERARCHY.get(current_role)