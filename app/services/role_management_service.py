# app/services/role_management_service.py

"""
Role Management Service

Provides business logic for the new organization role hierarchy and voucher approval workflow.
This service will be expanded in Phase 2 with full API endpoints.
This service is updated to exclude system-level roles like "super_admin" for org admins.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime

from app.models.user_models import (
    Organization, User, OrganizationRole, RoleModuleAssignment,
    UserOrganizationRole, OrganizationApprovalSettings, VoucherApproval
)
from app.schemas.role_management import (
    OrganizationRoleCreate, RoleModuleAssignmentCreate, UserOrganizationRoleCreate,
    OrganizationApprovalSettingsCreate, VoucherApprovalCreate,
    ApprovalModel, ApprovalStatus
)


class RoleManagementService:
    """Service for managing organization roles and permissions"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # Organization Role Management
    
    def create_organization_role(
        self, 
        role_data: OrganizationRoleCreate, 
        created_by_user_id: Optional[int] = None
    ) -> OrganizationRole:
        """Create a new organization role"""
        role = OrganizationRole(
            organization_id=role_data.organization_id,
            name=role_data.name,
            display_name=role_data.display_name,
            description=role_data.description,
            hierarchy_level=role_data.hierarchy_level,
            is_active=role_data.is_active,
            created_by_id=created_by_user_id
        )
        self.db.add(role)
        self.db.commit()
        self.db.refresh(role)
        return role
    
    def get_organization_roles(self, organization_id: int) -> List[OrganizationRole]:
        """Get all roles for an organization"""
        return self.db.query(OrganizationRole).filter(
            and_(
                OrganizationRole.organization_id == organization_id,
                OrganizationRole.is_active == True
            )
        ).order_by(OrganizationRole.hierarchy_level).all()
    
    def get_role_by_name(self, organization_id: int, role_name: str) -> Optional[OrganizationRole]:
        """Get a role by name within an organization"""
        return self.db.query(OrganizationRole).filter(
            and_(
                OrganizationRole.organization_id == organization_id,
                OrganizationRole.name == role_name,
                OrganizationRole.is_active == True
            )
        ).first()
    
    # Module Assignment Management
    
    def assign_module_to_role(
        self, 
        assignment_data: RoleModuleAssignmentCreate,
        assigned_by_user_id: Optional[int] = None
    ) -> RoleModuleAssignment:
        """Assign a module to a role with specific permissions"""
        assignment = RoleModuleAssignment(
            organization_id=assignment_data.organization_id,
            role_id=assignment_data.role_id,
            module_name=assignment_data.module_name,
            access_level=assignment_data.access_level,
            permissions=assignment_data.permissions,
            is_active=assignment_data.is_active,
            assigned_by_id=assigned_by_user_id
        )
        self.db.add(assignment)
        self.db.commit()
        self.db.refresh(assignment)
        return assignment
    
    def get_role_modules(self, role_id: int) -> List[RoleModuleAssignment]:
        """Get all module assignments for a role"""
        return self.db.query(RoleModuleAssignment).filter(
            and_(
                RoleModuleAssignment.role_id == role_id,
                RoleModuleAssignment.is_active == True
            )
        ).all()
    
    def remove_module_from_role(self, role_id: int, module_name: str) -> bool:
        """Remove a module assignment from a role"""
        assignment = self.db.query(RoleModuleAssignment).filter(
            and_(
                RoleModuleAssignment.role_id == role_id,
                RoleModuleAssignment.module_name == module_name
            )
        ).first()
        
        if assignment:
            assignment.is_active = False
            self.db.commit()
            return True
        return False
    
    # User Role Assignment Management
    
    def assign_user_to_role(
        self,
        assignment_data: UserOrganizationRoleCreate,
        assigned_by_user_id: Optional[int] = None
    ) -> UserOrganizationRole:
        """Assign a user to an organization role"""
        assignment = UserOrganizationRole(
            organization_id=assignment_data.organization_id,
            user_id=assignment_data.user_id,
            role_id=assignment_data.role_id,
            is_active=assignment_data.is_active,
            manager_assignments=assignment_data.manager_assignments,
            assigned_by_id=assigned_by_user_id
        )
        self.db.add(assignment)
        self.db.commit()
        self.db.refresh(assignment)
        return assignment
    
    def get_user_roles(self, user_id: int) -> List[UserOrganizationRole]:
        """Get all role assignments for a user"""
        return self.db.query(UserOrganizationRole).filter(
            and_(
                UserOrganizationRole.user_id == user_id,
                UserOrganizationRole.is_active == True
            )
        ).all()
    
    def get_role_users(self, role_id: int) -> List[UserOrganizationRole]:
        """Get all users assigned to a role"""
        return self.db.query(UserOrganizationRole).filter(
            and_(
                UserOrganizationRole.role_id == role_id,
                UserOrganizationRole.is_active == True
            )
        ).all()
    
    def remove_user_from_role(self, user_id: int, role_id: int) -> bool:
        """Remove a user from a role"""
        assignment = self.db.query(UserOrganizationRole).filter(
            and_(
                UserOrganizationRole.user_id == user_id,
                UserOrganizationRole.role_id == role_id
            )
        ).first()
        
        if assignment:
            assignment.is_active = False
            self.db.commit()
            return True
        return False
    
    # Permission Checking
    
    def user_has_module_access(
        self, 
        user_id: int, 
        module_name: str, 
        required_access_level: str = "view_only"
    ) -> bool:
        """Check if a user has access to a specific module"""
        # Get user's active role assignments
        user_roles = self.get_user_roles(user_id)
        
        access_hierarchy = {"view_only": 1, "limited": 2, "full": 3}
        required_level = access_hierarchy.get(required_access_level, 1)
        
        for user_role in user_roles:
            # Get module assignments for this role
            module_assignments = self.db.query(RoleModuleAssignment).filter(
                and_(
                    RoleModuleAssignment.role_id == user_role.role_id,
                    RoleModuleAssignment.module_name == module_name,
                    RoleModuleAssignment.is_active == True
                )
            ).all()
            
            for assignment in module_assignments:
                user_level = access_hierarchy.get(assignment.access_level, 0)
                if user_level >= required_level:
                    return True
        
        return False
    
    def get_user_module_permissions(self, user_id: int, module_name: str) -> Dict[str, Any]:
        """Get detailed permissions for a user on a specific module"""
        user_roles = self.get_user_roles(user_id)
        permissions = {"has_access": False, "access_level": None, "permissions": {}}
        
        highest_level = 0
        access_hierarchy = {"view_only": 1, "limited": 2, "full": 3}
        
        for user_role in user_roles:
            module_assignments = self.db.query(RoleModuleAssignment).filter(
                and_(
                    RoleModuleAssignment.role_id == user_role.role_id,
                    RoleModuleAssignment.module_name == module_name,
                    RoleModuleAssignment.is_active == True
                )
            ).all()
            
            for assignment in module_assignments:
                level = access_hierarchy.get(assignment.access_level, 0)
                if level > highest_level:
                    highest_level = level
                    permissions["has_access"] = True
                    permissions["access_level"] = assignment.access_level
                    permissions["permissions"] = assignment.permissions or {}
        
        return permissions


class VoucherApprovalService:
    """Service for managing voucher approval workflow"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # Approval Settings Management
    
    def get_or_create_approval_settings(self, organization_id: int) -> OrganizationApprovalSettings:
        """Get existing approval settings or create default ones"""
        settings = self.db.query(OrganizationApprovalSettings).filter(
            OrganizationApprovalSettings.organization_id == organization_id
        ).first()
        
        if not settings:
            settings = OrganizationApprovalSettings(
                organization_id=organization_id,
                approval_model=ApprovalModel.NO_APPROVAL,
                escalation_timeout_hours=72
            )
            self.db.add(settings)
            self.db.commit()
            self.db.refresh(settings)
        
        return settings
    
    def update_approval_settings(
        self,
        organization_id: int,
        approval_model: ApprovalModel,
        level_2_approvers: Optional[Dict[str, List[int]]] = None,
        auto_approve_threshold: Optional[float] = None,
        escalation_timeout_hours: Optional[int] = None,
        updated_by_user_id: Optional[int] = None
    ) -> OrganizationApprovalSettings:
        """Update organization approval settings"""
        settings = self.get_or_create_approval_settings(organization_id)
        
        settings.approval_model = approval_model.value
        if level_2_approvers is not None:
            settings.level_2_approvers = level_2_approvers
        if auto_approve_threshold is not None:
            settings.auto_approve_threshold = auto_approve_threshold
        if escalation_timeout_hours is not None:
            settings.escalation_timeout_hours = escalation_timeout_hours
        
        settings.updated_at = datetime.utcnow()
        settings.updated_by_id = updated_by_user_id
        
        self.db.commit()
        self.db.refresh(settings)
        return settings
    
    # Voucher Approval Management
    
    def submit_voucher_for_approval(
        self,
        approval_data: VoucherApprovalCreate
    ) -> VoucherApproval:
        """Submit a voucher for approval"""
        settings = self.get_or_create_approval_settings(approval_data.organization_id)
        
        # Determine initial approver based on approval model
        current_approver_id = None
        if settings.approval_model in [ApprovalModel.LEVEL_1.value, ApprovalModel.LEVEL_2.value]:
            # Find the user's manager for level 1 approval
            current_approver_id = self._find_level_1_approver(approval_data.submitted_by_id)
        
        approval = VoucherApproval(
            organization_id=approval_data.organization_id,
            approval_settings_id=settings.id,
            voucher_type=approval_data.voucher_type,
            voucher_id=approval_data.voucher_id,
            voucher_number=approval_data.voucher_number,
            voucher_amount=approval_data.voucher_amount,
            submitted_by_id=approval_data.submitted_by_id,
            current_approver_id=current_approver_id,
            status=ApprovalStatus.PENDING.value
        )
        
        # Auto-approve if below threshold and no approval required
        if (settings.approval_model == ApprovalModel.NO_APPROVAL.value or
            (settings.auto_approve_threshold and 
             approval_data.voucher_amount and
             approval_data.voucher_amount < settings.auto_approve_threshold)):
            approval.status = ApprovalStatus.APPROVED.value
            approval.final_decision = "approved"
            approval.final_decision_at = datetime.utcnow()
            approval.final_decision_by_id = approval_data.submitted_by_id
        
        self.db.add(approval)
        self.db.commit()
        self.db.refresh(approval)
        return approval
    
    def approve_voucher_level_1(
        self,
        approval_id: int,
        approver_user_id: int,
        comments: Optional[str] = None
    ) -> VoucherApproval:
        """Approve voucher at level 1 (manager approval)"""
        approval = self.db.query(VoucherApproval).filter(
            VoucherApproval.id == approval_id
        ).first()
        
        if not approval or approval.status != ApprovalStatus.PENDING.value:
            raise ValueError("Approval not found or not in pending status")
        
        approval.level_1_approver_id = approver_user_id
        approval.level_1_approved_at = datetime.utcnow()
        approval.level_1_comments = comments
        
        # Check if level 2 approval is needed
        settings = approval.approval_settings
        if settings.approval_model == ApprovalModel.LEVEL_2.value:
            approval.status = ApprovalStatus.LEVEL_1_APPROVED.value
            # Set next approver from level 2 approvers
            if settings.level_2_approvers and "user_ids" in settings.level_2_approvers:
                approval.current_approver_id = settings.level_2_approvers["user_ids"][0]
        else:
            # Final approval for level 1 workflow
            approval.status = ApprovalStatus.APPROVED.value
            approval.final_decision = "approved"
            approval.final_decision_at = datetime.utcnow()
            approval.final_decision_by_id = approver_user_id
            approval.current_approver_id = None
        
        self.db.commit()
        self.db.refresh(approval)
        return approval
    
    def approve_voucher_level_2(
        self,
        approval_id: int,
        approver_user_id: int,
        comments: Optional[str] = None
    ) -> VoucherApproval:
        """Approve voucher at level 2 (management approval)"""
        approval = self.db.query(VoucherApproval).filter(
            VoucherApproval.id == approval_id
        ).first()
        
        if not approval or approval.status != ApprovalStatus.LEVEL_1_APPROVED.value:
            raise ValueError("Approval not found or not in level 1 approved status")
        
        approval.level_2_approver_id = approver_user_id
        approval.level_2_approved_at = datetime.utcnow()
        approval.level_2_comments = comments
        approval.status = ApprovalStatus.APPROVED.value
        approval.final_decision = "approved"
        approval.final_decision_at = datetime.utcnow()
        approval.final_decision_by_id = approver_user_id
        approval.current_approver_id = None
        
        self.db.commit()
        self.db.refresh(approval)
        return approval
    
    def reject_voucher(
        self,
        approval_id: int,
        rejector_user_id: int,
        rejection_reason: str
    ) -> VoucherApproval:
        """Reject a voucher"""
        approval = self.db.query(VoucherApproval).filter(
            VoucherApproval.id == approval_id
        ).first()
        
        if not approval or approval.status not in [
            ApprovalStatus.PENDING.value, 
            ApprovalStatus.LEVEL_1_APPROVED.value
        ]:
            raise ValueError("Approval not found or not in rejectable status")
        
        approval.status = ApprovalStatus.REJECTED.value
        approval.final_decision = "rejected"
        approval.final_decision_at = datetime.utcnow()
        approval.final_decision_by_id = rejector_user_id
        approval.rejection_reason = rejection_reason
        approval.current_approver_id = None
        
        self.db.commit()
        self.db.refresh(approval)
        return approval
    
    def get_pending_approvals_for_user(self, user_id: int) -> List[VoucherApproval]:
        """Get all vouchers pending approval by a specific user"""
        return self.db.query(VoucherApproval).filter(
            and_(
                VoucherApproval.current_approver_id == user_id,
                VoucherApproval.status.in_([
                    ApprovalStatus.PENDING.value,
                    ApprovalStatus.LEVEL_1_APPROVED.value
                ])
            )
        ).order_by(VoucherApproval.submitted_at).all()
    
    def get_voucher_approval_history(self, voucher_type: str, voucher_id: int) -> Optional[VoucherApproval]:
        """Get approval history for a specific voucher"""
        return self.db.query(VoucherApproval).filter(
            and_(
                VoucherApproval.voucher_type == voucher_type,
                VoucherApproval.voucher_id == voucher_id
            )
        ).first()
    
    def _find_level_1_approver(self, submitted_by_user_id: int) -> Optional[int]:
        """Find the manager who should approve this user's vouchers"""
        # Get user's role assignments
        user_roles = self.db.query(UserOrganizationRole).filter(
            and_(
                UserOrganizationRole.user_id == submitted_by_user_id,
                UserOrganizationRole.is_active == True
            )
        ).all()
        
        # Look for manager assignments in the user's roles
        for user_role in user_roles:
            if (user_role.manager_assignments and 
                isinstance(user_role.manager_assignments, dict)):
                # Return first available manager (in real implementation, 
                # you might want to select based on the voucher's module)
                for module, manager_id in user_role.manager_assignments.items():
                    if manager_id:
                        return manager_id
        
        return None


# Helper functions for role initialization

def initialize_default_roles(db: Session, organization_id: int) -> List[OrganizationRole]:
    """Initialize default roles for an organization"""
    service = RoleManagementService(db)
    
    default_roles = [
        {"name": "management", "display_name": "Management", "hierarchy_level": 1, 
         "description": "Full access to all modules and approval authority"},
        {"name": "manager", "display_name": "Manager", "hierarchy_level": 2,
         "description": "Full access to assigned modules with approval authority"},
        {"name": "executive", "display_name": "Executive", "hierarchy_level": 3,
         "description": "Limited access to assigned modules, reports to managers"}
    ]
    
    created_roles = []
    for role_data in default_roles:
        # Check if role already exists
        existing_role = service.get_role_by_name(organization_id, role_data["name"])
        if not existing_role:
            from app.schemas.role_management import OrganizationRoleCreate
            role_create = OrganizationRoleCreate(
                organization_id=organization_id,
                **role_data
            )
            role = service.create_organization_role(role_create)
            created_roles.append(role)
        else:
            created_roles.append(existing_role)
    
    return created_roles


def assign_default_modules_to_role(
    db: Session, 
    role_id: int, 
    organization_id: int, 
    modules: List[str],
    access_level: str = "full"
) -> List[RoleModuleAssignment]:
    """Assign default modules to a role"""
    service = RoleManagementService(db)
    
    assignments = []
    for module_name in modules:
        from app.schemas.role_management import RoleModuleAssignmentCreate
        assignment_data = RoleModuleAssignmentCreate(
            organization_id=organization_id,
            role_id=role_id,
            module_name=module_name,
            access_level=access_level
        )
        assignment = service.assign_module_to_role(assignment_data)
        assignments.append(assignment)
    
    return assignments