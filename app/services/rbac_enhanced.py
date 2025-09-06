# app/services/rbac_enhanced.py
"""
Enhanced RBAC Service with advanced permission matrix, role inheritance, and dynamic permissions
"""

from typing import List, Optional, Dict, Set, Any, Union
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func, text
from fastapi import HTTPException, status
from datetime import datetime, timedelta
import json
import logging
from enum import Enum

from app.models.user_models import (
    User, ServiceRole, ServicePermission, ServiceRolePermission, 
    UserServiceRole, Organization
)
from app.schemas.rbac import (
    ServiceRoleCreate, ServiceRoleUpdate, ServicePermissionCreate,
    UserServiceRoleCreate, ServiceRoleType, ServiceModule, ServiceAction
)

logger = logging.getLogger(__name__)


class PermissionScope(str, Enum):
    """Permission scope levels"""
    GLOBAL = "global"           # System-wide permissions
    ORGANIZATION = "organization"  # Organization-level permissions
    COMPANY = "company"         # Company-level permissions
    DEPARTMENT = "department"   # Department-level permissions
    TEAM = "team"              # Team-level permissions
    PERSONAL = "personal"      # Personal/self permissions


class PermissionEffect(str, Enum):
    """Permission effects"""
    ALLOW = "allow"
    DENY = "deny"
    INHERIT = "inherit"


class ResourceType(str, Enum):
    """Resource types for fine-grained permissions"""
    CUSTOMER = "customer"
    VENDOR = "vendor"
    PRODUCT = "product"
    ORDER = "order"
    INVOICE = "invoice"
    PAYMENT = "payment"
    TICKET = "ticket"
    PROJECT = "project"
    TASK = "task"
    REPORT = "report"
    DASHBOARD = "dashboard"
    WORKFLOW = "workflow"
    INTEGRATION = "integration"


class EnhancedRBACService:
    """Enhanced RBAC service with advanced features"""
    
    def __init__(self, db: Session):
        self.db = db
        self._permission_cache = {}
        self._cache_ttl = 300  # 5 minutes
    
    # ============================================================================
    # ADVANCED PERMISSION MANAGEMENT
    # ============================================================================
    
    def create_dynamic_permission(
        self, 
        name: str,
        module: str,
        action: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[int] = None,
        scope: PermissionScope = PermissionScope.ORGANIZATION,
        conditions: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ServicePermission:
        """Create dynamic permission with advanced attributes"""
        
        permission_data = {
            "name": name,
            "module": module,
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "scope": scope.value,
            "conditions": conditions or {},
            "metadata": metadata or {},
            "is_active": True
        }
        
        permission = ServicePermission(**permission_data)
        self.db.add(permission)
        self.db.commit()
        self.db.refresh(permission)
        
        logger.info(f"Created dynamic permission: {name}")
        return permission
    
    def create_permission_matrix(
        self, 
        organization_id: int,
        matrix_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create comprehensive permission matrix for organization"""
        
        try:
            results = {
                "created_permissions": [],
                "created_roles": [],
                "assigned_permissions": []
            }
            
            # Create permissions from matrix
            for module_name, module_config in matrix_config.get("modules", {}).items():
                for action_name, action_config in module_config.get("actions", {}).items():
                    for resource_type in action_config.get("resources", ["*"]):
                        
                        permission_name = f"{module_name}.{action_name}"
                        if resource_type != "*":
                            permission_name += f".{resource_type}"
                        
                        # Check if permission already exists
                        existing = self.db.query(ServicePermission).filter(
                            ServicePermission.name == permission_name
                        ).first()
                        
                        if not existing:
                            permission = self.create_dynamic_permission(
                                name=permission_name,
                                module=module_name,
                                action=action_name,
                                resource_type=resource_type if resource_type != "*" else None,
                                scope=PermissionScope(action_config.get("scope", "organization")),
                                conditions=action_config.get("conditions"),
                                metadata={
                                    "description": action_config.get("description"),
                                    "category": module_config.get("category", "general")
                                }
                            )
                            results["created_permissions"].append(permission.name)
            
            # Create roles from matrix
            for role_name, role_config in matrix_config.get("roles", {}).items():
                existing_role = self.db.query(ServiceRole).filter(
                    ServiceRole.organization_id == organization_id,
                    ServiceRole.name == role_name
                ).first()
                
                if not existing_role:
                    role = ServiceRole(
                        organization_id=organization_id,
                        name=role_name,
                        role_type=ServiceRoleType(role_config.get("type", "custom")),
                        description=role_config.get("description"),
                        is_active=True,
                        parent_role_id=None,  # We'll handle inheritance later
                        metadata=role_config.get("metadata", {})
                    )
                    self.db.add(role)
                    self.db.flush()
                    results["created_roles"].append(role_name)
                    
                    # Assign permissions to role
                    for permission_pattern in role_config.get("permissions", []):
                        permissions = self._resolve_permission_pattern(permission_pattern)
                        for permission in permissions:
                            role_permission = ServiceRolePermission(
                                organization_id=organization_id,
                                role_id=role.id,
                                permission_id=permission.id
                            )
                            self.db.add(role_permission)
                            results["assigned_permissions"].append(f"{role_name}:{permission.name}")
            
            self.db.commit()
            self._clear_permission_cache()
            
            return results
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create permission matrix: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create permission matrix: {str(e)}"
            )
    
    def _resolve_permission_pattern(self, pattern: str) -> List[ServicePermission]:
        """Resolve permission pattern to actual permissions"""
        # Support wildcards like "customers.*", "*.read", etc.
        if "*" in pattern:
            if pattern.endswith(".*"):
                # Module wildcard: "customers.*"
                module = pattern[:-2]
                return self.db.query(ServicePermission).filter(
                    ServicePermission.module == module
                ).all()
            elif pattern.startswith("*."):
                # Action wildcard: "*.read"
                action = pattern[2:]
                return self.db.query(ServicePermission).filter(
                    ServicePermission.action == action
                ).all()
            elif pattern == "*":
                # All permissions
                return self.db.query(ServicePermission).all()
        else:
            # Exact match
            permission = self.db.query(ServicePermission).filter(
                ServicePermission.name == pattern
            ).first()
            return [permission] if permission else []
        
        return []
    
    # ============================================================================
    # ROLE INHERITANCE SYSTEM
    # ============================================================================
    
    def create_role_with_inheritance(
        self,
        organization_id: int,
        name: str,
        parent_role_id: Optional[int] = None,
        role_type: ServiceRoleType = ServiceRoleType.CUSTOM,
        description: Optional[str] = None,
        additional_permissions: Optional[List[int]] = None,
        denied_permissions: Optional[List[int]] = None
    ) -> ServiceRole:
        """Create role with inheritance from parent role"""
        
        # Validate parent role if specified
        parent_role = None
        if parent_role_id:
            parent_role = self.db.query(ServiceRole).filter(
                ServiceRole.id == parent_role_id,
                ServiceRole.organization_id == organization_id
            ).first()
            
            if not parent_role:
                raise HTTPException(
                    status_code=404,
                    detail="Parent role not found"
                )
            
            # Check for circular inheritance
            if self._would_create_circular_inheritance(parent_role_id, organization_id):
                raise HTTPException(
                    status_code=400,
                    detail="Cannot create role: would result in circular inheritance"
                )
        
        # Create role
        role = ServiceRole(
            organization_id=organization_id,
            name=name,
            parent_role_id=parent_role_id,
            role_type=role_type,
            description=description,
            is_active=True,
            metadata={
                "inheritance_enabled": True,
                "inherit_from_parent": parent_role_id is not None
            }
        )
        
        self.db.add(role)
        self.db.flush()
        
        # Inherit permissions from parent
        inherited_permissions = set()
        if parent_role:
            inherited_permissions = self._get_inherited_permissions(parent_role_id)
        
        # Add additional permissions
        if additional_permissions:
            inherited_permissions.update(additional_permissions)
        
        # Remove denied permissions
        if denied_permissions:
            inherited_permissions.difference_update(denied_permissions)
        
        # Assign permissions to role
        for permission_id in inherited_permissions:
            role_permission = ServiceRolePermission(
                organization_id=organization_id,
                role_id=role.id,
                permission_id=permission_id,
                effect=PermissionEffect.ALLOW.value,
                inherited_from=parent_role_id if permission_id in self._get_inherited_permissions(parent_role_id) else None
            )
            self.db.add(role_permission)
        
        # Add explicit denies
        if denied_permissions:
            for permission_id in denied_permissions:
                role_permission = ServiceRolePermission(
                    organization_id=organization_id,
                    role_id=role.id,
                    permission_id=permission_id,
                    effect=PermissionEffect.DENY.value
                )
                self.db.add(role_permission)
        
        self.db.commit()
        self.db.refresh(role)
        
        logger.info(f"Created role with inheritance: {name}")
        return role
    
    def _would_create_circular_inheritance(self, parent_role_id: int, organization_id: int) -> bool:
        """Check if adding this parent would create circular inheritance"""
        visited = set()
        current = parent_role_id
        
        while current:
            if current in visited:
                return True
            
            visited.add(current)
            
            parent = self.db.query(ServiceRole).filter(
                ServiceRole.id == current,
                ServiceRole.organization_id == organization_id
            ).first()
            
            current = parent.parent_role_id if parent else None
        
        return False
    
    def _get_inherited_permissions(self, role_id: int) -> Set[int]:
        """Get all permissions inherited from role hierarchy"""
        permissions = set()
        current_role_id = role_id
        visited = set()
        
        while current_role_id and current_role_id not in visited:
            visited.add(current_role_id)
            
            # Get direct permissions for current role
            role_permissions = self.db.query(ServiceRolePermission).filter(
                ServiceRolePermission.role_id == current_role_id,
                ServiceRolePermission.effect.in_(["allow", None])
            ).all()
            
            for rp in role_permissions:
                permissions.add(rp.permission_id)
            
            # Move up the hierarchy
            parent_role = self.db.query(ServiceRole).filter(
                ServiceRole.id == current_role_id
            ).first()
            
            current_role_id = parent_role.parent_role_id if parent_role else None
        
        return permissions
    
    # ============================================================================
    # ADVANCED PERMISSION CHECKING
    # ============================================================================
    
    def check_permission_advanced(
        self,
        user_id: int,
        permission_name: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[int] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Advanced permission checking with context and conditions"""
        
        try:
            # Get user with roles
            user = self.db.query(User).options(
                joinedload(User.service_roles).joinedload(UserServiceRole.role)
            ).filter(User.id == user_id).first()
            
            if not user:
                return {"allowed": False, "reason": "User not found"}
            
            # Check cache first
            cache_key = f"{user_id}:{permission_name}:{resource_type}:{resource_id}"
            cached_result = self._get_cached_permission(cache_key)
            if cached_result:
                return cached_result
            
            # Get permission
            permission_query = self.db.query(ServicePermission).filter(
                ServicePermission.name == permission_name,
                ServicePermission.is_active == True
            )
            
            if resource_type:
                permission_query = permission_query.filter(
                    or_(
                        ServicePermission.resource_type == resource_type,
                        ServicePermission.resource_type.is_(None)
                    )
                )
            
            permission = permission_query.first()
            if not permission:
                result = {"allowed": False, "reason": "Permission not found"}
                self._cache_permission_result(cache_key, result)
                return result
            
            # Check user roles
            user_roles = [usr.role for usr in user.service_roles if usr.role.is_active]
            
            permission_granted = False
            explicit_deny = False
            grant_reason = None
            deny_reason = None
            
            for role in user_roles:
                # Get role permissions including inherited ones
                role_permissions = self._get_role_permissions_with_inheritance(role.id)
                
                for rp in role_permissions:
                    if rp.permission_id == permission.id:
                        # Check conditions if present
                        if permission.conditions:
                            condition_result = self._evaluate_conditions(
                                permission.conditions, 
                                user, 
                                context or {}
                            )
                            if not condition_result:
                                continue
                        
                        # Check resource-specific permissions
                        if resource_id and rp.resource_id and rp.resource_id != resource_id:
                            continue
                        
                        if rp.effect == PermissionEffect.DENY.value:
                            explicit_deny = True
                            deny_reason = f"Explicitly denied by role: {role.name}"
                            break
                        elif rp.effect in [PermissionEffect.ALLOW.value, None]:
                            permission_granted = True
                            grant_reason = f"Granted by role: {role.name}"
                
                if explicit_deny:
                    break
            
            # Deny takes precedence over allow
            if explicit_deny:
                result = {"allowed": False, "reason": deny_reason}
            elif permission_granted:
                result = {"allowed": True, "reason": grant_reason}
            else:
                result = {"allowed": False, "reason": "No matching permissions found"}
            
            # Cache result
            self._cache_permission_result(cache_key, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Permission check failed: {e}")
            return {"allowed": False, "reason": f"Error checking permission: {str(e)}"}
    
    def _get_role_permissions_with_inheritance(self, role_id: int) -> List[ServiceRolePermission]:
        """Get role permissions including inherited permissions"""
        permissions = []
        visited = set()
        current_role_id = role_id
        
        while current_role_id and current_role_id not in visited:
            visited.add(current_role_id)
            
            # Get direct permissions
            role_permissions = self.db.query(ServiceRolePermission).filter(
                ServiceRolePermission.role_id == current_role_id
            ).all()
            
            permissions.extend(role_permissions)
            
            # Get parent role
            role = self.db.query(ServiceRole).filter(
                ServiceRole.id == current_role_id
            ).first()
            
            current_role_id = role.parent_role_id if role else None
        
        return permissions
    
    def _evaluate_conditions(
        self, 
        conditions: Dict[str, Any], 
        user: User, 
        context: Dict[str, Any]
    ) -> bool:
        """Evaluate permission conditions"""
        
        try:
            for condition_type, condition_value in conditions.items():
                if condition_type == "time_restriction":
                    # Check time-based conditions
                    current_time = datetime.now().time()
                    start_time = datetime.strptime(condition_value["start"], "%H:%M").time()
                    end_time = datetime.strptime(condition_value["end"], "%H:%M").time()
                    
                    if not (start_time <= current_time <= end_time):
                        return False
                
                elif condition_type == "ip_restriction":
                    # Check IP-based conditions
                    allowed_ips = condition_value.get("allowed_ips", [])
                    user_ip = context.get("ip_address")
                    
                    if user_ip and allowed_ips and user_ip not in allowed_ips:
                        return False
                
                elif condition_type == "department_restriction":
                    # Check department-based conditions
                    allowed_departments = condition_value.get("departments", [])
                    user_department = context.get("department") or user.department
                    
                    if allowed_departments and user_department not in allowed_departments:
                        return False
                
                elif condition_type == "data_scope":
                    # Check data scope conditions
                    scope = condition_value.get("scope", "all")
                    
                    if scope == "own_only":
                        resource_owner = context.get("resource_owner_id")
                        if resource_owner and resource_owner != user.id:
                            return False
                    elif scope == "department_only":
                        resource_department = context.get("resource_department")
                        user_department = context.get("department") or user.department
                        if resource_department and resource_department != user_department:
                            return False
                
                elif condition_type == "custom_condition":
                    # Evaluate custom conditions using safe eval
                    condition_expr = condition_value.get("expression", "True")
                    safe_context = {
                        "user": {
                            "id": user.id,
                            "email": user.email,
                            "role": user.role,
                            "department": getattr(user, 'department', None)
                        },
                        "context": context,
                        "datetime": datetime,
                        "timedelta": timedelta
                    }
                    
                    # Use eval with restricted globals for safety
                    try:
                        result = eval(condition_expr, {"__builtins__": {}}, safe_context)
                        if not result:
                            return False
                    except Exception as e:
                        logger.warning(f"Failed to evaluate custom condition: {e}")
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error evaluating conditions: {e}")
            return False
    
    # ============================================================================
    # PERMISSION CACHING
    # ============================================================================
    
    def _get_cached_permission(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached permission result"""
        if cache_key in self._permission_cache:
            cached_item = self._permission_cache[cache_key]
            if datetime.now() - cached_item["timestamp"] < timedelta(seconds=self._cache_ttl):
                return cached_item["result"]
            else:
                del self._permission_cache[cache_key]
        return None
    
    def _cache_permission_result(self, cache_key: str, result: Dict[str, Any]):
        """Cache permission result"""
        self._permission_cache[cache_key] = {
            "result": result,
            "timestamp": datetime.now()
        }
    
    def _clear_permission_cache(self):
        """Clear permission cache"""
        self._permission_cache.clear()
    
    # ============================================================================
    # ANALYTICS AND REPORTING
    # ============================================================================
    
    def get_permission_analytics(self, organization_id: int) -> Dict[str, Any]:
        """Get permission usage analytics"""
        
        # Most used permissions
        most_used = self.db.execute(text("""
            SELECT p.name, p.module, p.action, COUNT(*) as usage_count
            FROM service_role_permissions rp
            JOIN service_permissions p ON rp.permission_id = p.id
            WHERE rp.organization_id = :org_id
            GROUP BY p.id, p.name, p.module, p.action
            ORDER BY usage_count DESC
            LIMIT 10
        """), {"org_id": organization_id}).fetchall()
        
        # Unused permissions
        unused = self.db.execute(text("""
            SELECT p.name, p.module, p.action
            FROM service_permissions p
            WHERE p.id NOT IN (
                SELECT DISTINCT permission_id 
                FROM service_role_permissions 
                WHERE organization_id = :org_id
            )
            ORDER BY p.module, p.action
        """), {"org_id": organization_id}).fetchall()
        
        # Role distribution
        role_distribution = self.db.execute(text("""
            SELECT r.name, r.role_type, COUNT(ur.user_id) as user_count
            FROM service_roles r
            LEFT JOIN user_service_roles ur ON r.id = ur.role_id
            WHERE r.organization_id = :org_id
            GROUP BY r.id, r.name, r.role_type
            ORDER BY user_count DESC
        """), {"org_id": organization_id}).fetchall()
        
        return {
            "most_used_permissions": [
                {
                    "name": row[0],
                    "module": row[1],
                    "action": row[2],
                    "usage_count": row[3]
                }
                for row in most_used
            ],
            "unused_permissions": [
                {
                    "name": row[0],
                    "module": row[1],
                    "action": row[2]
                }
                for row in unused
            ],
            "role_distribution": [
                {
                    "role_name": row[0],
                    "role_type": row[1],
                    "user_count": row[2]
                }
                for row in role_distribution
            ]
        }
    
    # ============================================================================
    # UTILITY METHODS
    # ============================================================================
    
    def get_user_effective_permissions(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all effective permissions for a user"""
        
        user = self.db.query(User).options(
            joinedload(User.service_roles).joinedload(UserServiceRole.role)
        ).filter(User.id == user_id).first()
        
        if not user:
            return []
        
        effective_permissions = {}
        
        for user_role in user.service_roles:
            if not user_role.role.is_active:
                continue
            
            role_permissions = self._get_role_permissions_with_inheritance(user_role.role.id)
            
            for rp in role_permissions:
                permission = self.db.query(ServicePermission).filter(
                    ServicePermission.id == rp.permission_id
                ).first()
                
                if permission:
                    perm_key = permission.name
                    
                    if perm_key not in effective_permissions:
                        effective_permissions[perm_key] = {
                            "permission": permission,
                            "effect": rp.effect or "allow",
                            "granted_by_roles": []
                        }
                    
                    effective_permissions[perm_key]["granted_by_roles"].append(user_role.role.name)
                    
                    # Deny takes precedence
                    if rp.effect == "deny":
                        effective_permissions[perm_key]["effect"] = "deny"
        
        return [
            {
                "name": perm["permission"].name,
                "module": perm["permission"].module,
                "action": perm["permission"].action,
                "effect": perm["effect"],
                "granted_by_roles": perm["granted_by_roles"]
            }
            for perm in effective_permissions.values()
            if perm["effect"] == "allow"  # Only return allowed permissions
        ]
    
    def bulk_assign_permissions(
        self,
        organization_id: int,
        assignments: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Bulk assign permissions to roles"""
        
        results = {
            "successful_assignments": 0,
            "failed_assignments": 0,
            "errors": []
        }
        
        try:
            for assignment in assignments:
                try:
                    role_id = assignment["role_id"]
                    permission_ids = assignment["permission_ids"]
                    effect = assignment.get("effect", "allow")
                    
                    # Validate role exists
                    role = self.db.query(ServiceRole).filter(
                        ServiceRole.id == role_id,
                        ServiceRole.organization_id == organization_id
                    ).first()
                    
                    if not role:
                        results["errors"].append(f"Role {role_id} not found")
                        results["failed_assignments"] += 1
                        continue
                    
                    # Assign permissions
                    for permission_id in permission_ids:
                        # Remove existing assignment if any
                        self.db.query(ServiceRolePermission).filter(
                            ServiceRolePermission.role_id == role_id,
                            ServiceRolePermission.permission_id == permission_id
                        ).delete()
                        
                        # Add new assignment
                        role_permission = ServiceRolePermission(
                            organization_id=organization_id,
                            role_id=role_id,
                            permission_id=permission_id,
                            effect=effect
                        )
                        self.db.add(role_permission)
                    
                    results["successful_assignments"] += 1
                    
                except Exception as e:
                    results["errors"].append(f"Assignment failed: {str(e)}")
                    results["failed_assignments"] += 1
            
            self.db.commit()
            self._clear_permission_cache()
            
        except Exception as e:
            self.db.rollback()
            results["errors"].append(f"Bulk assignment failed: {str(e)}")
        
        return results