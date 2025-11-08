# app/utils/entitlement_helpers.py

"""
Standardized entitlement utility functions for module/feature access (Layer 2)
Provides helpers for checking module entitlements, trial status, and submodule access
"""

from typing import Dict, Any, Optional, Tuple
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
import logging

from app.core.constants import (
    ALWAYS_ON_MODULES,
    RBAC_ONLY_MODULES,
    ModuleStatusEnum,
    ENFORCEMENT_ERRORS,
)
from app.services.entitlement_service import EntitlementService

logger = logging.getLogger(__name__)


def normalize_enabled_modules(enabled_modules: Optional[Dict[str, Any]]) -> Dict[str, bool]:
    """
    Normalize enabled_modules dictionary to have lowercase keys and boolean values.
    
    Args:
        enabled_modules: The enabled_modules dict from organization, may be None or have mixed cases
        
    Returns:
        A normalized dict with lowercase keys and boolean values
        
    Example:
        >>> normalize_enabled_modules({"CRM": True, "ERP": "true", "Manufacturing": 1})
        {"crm": True, "erp": True, "manufacturing": True}
    """
    if not enabled_modules:
        return {}
    
    normalized = {}
    for key, value in enabled_modules.items():
        # Normalize key to lowercase
        normalized_key = key.lower() if isinstance(key, str) else str(key).lower()
        
        # Normalize value to boolean
        if isinstance(value, bool):
            normalized_value = value
        elif isinstance(value, str):
            # Handle string representations of booleans
            normalized_value = value.lower() in ('true', '1', 'yes', 'enabled')
        elif isinstance(value, (int, float)):
            # Handle numeric values (0 = False, anything else = True)
            normalized_value = bool(value)
        else:
            # Default to False for unknown types
            logger.warning(f"Unknown value type for enabled_modules[{key}]: {type(value)}, defaulting to False")
            normalized_value = False
        
        normalized[normalized_key] = normalized_value
    
    return normalized


def check_module_enabled(enabled_modules: Optional[Dict[str, Any]], module_key: str) -> bool:
    """
    Check if a module is enabled, handling case-insensitive lookup.
    
    Args:
        enabled_modules: The enabled_modules dict from organization
        module_key: The module key to check (e.g., 'crm', 'erp')
        
    Returns:
        True if the module is enabled, False otherwise
    """
    if not enabled_modules:
        return False
    
    # Normalize the dict
    normalized = normalize_enabled_modules(enabled_modules)
    
    # Check with case-insensitive key
    normalized_key = module_key.lower() if isinstance(module_key, str) else str(module_key).lower()
    
    return normalized.get(normalized_key, False)


def ensure_organization_module(enabled_modules: Optional[Dict[str, Any]]) -> Dict[str, bool]:
    """
    Ensure that the "organization" module is enabled in enabled_modules.
    This is required for organization dashboard access.
    
    Args:
        enabled_modules: The enabled_modules dict from organization
        
    Returns:
        Updated enabled_modules with "organization": True guaranteed
    """
    normalized = normalize_enabled_modules(enabled_modules)
    
    # Ensure organization module is always enabled
    if 'organization' not in normalized:
        normalized['organization'] = True
        logger.info("Added 'organization': True to enabled_modules")
    elif not normalized['organization']:
        normalized['organization'] = True
        logger.info("Changed 'organization' from False to True in enabled_modules")
    
    return normalized


# ============================================================================
# Enhanced Entitlement Checking (Layer 2)
# ============================================================================

class EntitlementHelper:
    """Helper class for entitlement operations"""

    @staticmethod
    def is_always_on_module(module_key: str) -> bool:
        """
        Check if module is always-on (not controlled by entitlements)
        
        Args:
            module_key: Module key to check
            
        Returns:
            bool: True if always-on
        """
        return module_key.lower() in ALWAYS_ON_MODULES

    @staticmethod
    def is_rbac_only_module(module_key: str) -> bool:
        """
        Check if module is RBAC-only (not controlled by entitlements)
        
        Args:
            module_key: Module key to check
            
        Returns:
            bool: True if RBAC-only
        """
        return module_key.lower() in RBAC_ONLY_MODULES

    @staticmethod
    def should_check_entitlement(module_key: str) -> bool:
        """
        Determine if entitlement check is required for module
        
        Args:
            module_key: Module key to check
            
        Returns:
            bool: True if entitlement check required
        """
        return not (
            EntitlementHelper.is_always_on_module(module_key) or
            EntitlementHelper.is_rbac_only_module(module_key)
        )

    @staticmethod
    async def check_module_entitlement(
        db: AsyncSession,
        org_id: int,
        module_key: str,
        submodule_key: Optional[str] = None
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Check if organization has entitlement for module/submodule
        
        Args:
            db: Database session
            org_id: Organization ID
            module_key: Module key to check
            submodule_key: Optional submodule key
            
        Returns:
            Tuple[bool, str, Optional[str]]: (is_entitled, status, reason)
        """
        # Skip check for always-on and RBAC-only modules
        if not EntitlementHelper.should_check_entitlement(module_key):
            logger.debug(f"Module {module_key} does not require entitlement check")
            return True, ModuleStatusEnum.ENABLED, None

        service = EntitlementService(db)
        return await service.check_entitlement(
            org_id=org_id,
            module_key=module_key,
            submodule_key=submodule_key
        )

    @staticmethod
    async def enforce_module_entitlement(
        db: AsyncSession,
        org_id: int,
        module_key: str,
        submodule_key: Optional[str] = None
    ) -> None:
        """
        Enforce organization has entitlement, raise exception if not
        
        Args:
            db: Database session
            org_id: Organization ID
            module_key: Module key to check
            submodule_key: Optional submodule key
            
        Raises:
            HTTPException: If not entitled
        """
        is_entitled, status, reason = await EntitlementHelper.check_module_entitlement(
            db, org_id, module_key, submodule_key
        )

        if not is_entitled:
            detail = ENFORCEMENT_ERRORS["entitlement_disabled"]
            if status == ModuleStatusEnum.TRIAL:
                detail = ENFORCEMENT_ERRORS["entitlement_trial_expired"]
            
            logger.warning(
                f"Org {org_id} denied access to {module_key}/{submodule_key}. "
                f"Status: {status}, Reason: {reason}"
            )
            
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "entitlement_required",
                    "module_key": module_key,
                    "submodule_key": submodule_key,
                    "status": status,
                    "reason": reason or detail,
                    "message": detail.format(module=module_key)
                }
            )

    @staticmethod
    async def get_org_module_status(
        db: AsyncSession,
        org_id: int,
        module_key: str
    ) -> str:
        """
        Get module status for organization
        
        Args:
            db: Database session
            org_id: Organization ID
            module_key: Module key
            
        Returns:
            str: Status (enabled, disabled, trial)
        """
        is_entitled, status, _ = await EntitlementHelper.check_module_entitlement(
            db, org_id, module_key
        )
        return status

    @staticmethod
    async def is_module_enabled(
        db: AsyncSession,
        org_id: int,
        module_key: str
    ) -> bool:
        """
        Check if module is enabled for organization
        
        Args:
            db: Database session
            org_id: Organization ID
            module_key: Module key
            
        Returns:
            bool: True if enabled or in trial
        """
        is_entitled, status, _ = await EntitlementHelper.check_module_entitlement(
            db, org_id, module_key
        )
        return is_entitled

    @staticmethod
    async def get_enabled_modules(
        db: AsyncSession,
        org_id: int
    ) -> Dict[str, str]:
        """
        Get all enabled modules for organization
        
        Args:
            db: Database session
            org_id: Organization ID
            
        Returns:
            Dict[str, str]: Module key to status mapping
        """
        service = EntitlementService(db)
        entitlements = await service.get_org_entitlements(org_id)
        
        enabled_modules = {}
        for module_ent in entitlements.entitlements:
            if module_ent.status in [ModuleStatusEnum.ENABLED, ModuleStatusEnum.TRIAL]:
                enabled_modules[module_ent.module_key] = module_ent.status
        
        return enabled_modules


# Convenience functions for common operations

def is_always_on_module(module_key: str) -> bool:
    """Check if module is always-on"""
    return EntitlementHelper.is_always_on_module(module_key)


def is_rbac_only_module(module_key: str) -> bool:
    """Check if module is RBAC-only"""
    return EntitlementHelper.is_rbac_only_module(module_key)


def should_check_entitlement(module_key: str) -> bool:
    """Check if entitlement check is required"""
    return EntitlementHelper.should_check_entitlement(module_key)


async def check_module_entitlement(
    db: AsyncSession,
    org_id: int,
    module_key: str,
    submodule_key: Optional[str] = None
) -> Tuple[bool, str, Optional[str]]:
    """Check module entitlement"""
    return await EntitlementHelper.check_module_entitlement(
        db, org_id, module_key, submodule_key
    )


async def enforce_module_entitlement(
    db: AsyncSession,
    org_id: int,
    module_key: str,
    submodule_key: Optional[str] = None
) -> None:
    """Enforce module entitlement"""
    await EntitlementHelper.enforce_module_entitlement(
        db, org_id, module_key, submodule_key
    )
