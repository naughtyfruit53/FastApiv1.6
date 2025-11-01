# app/utils/entitlement_helpers.py

"""
Entitlement utility functions for normalizing and checking enabled_modules.
"""

from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


def normalize_enabled_modules(enabled_modules: Optional[Dict[str, Any]]) -> Dict[str, bool]:
    """
    Normalize enabled_modules dictionary to have lowercase keys and boolean values.
    
    Args:
        enabled_modules: The enabled_modules dict from organization, may be None or have mixed cases
        
    Returns:
        A normalized dict with lowercase keys and boolean values
        
    Example:
        >>> normalize_enabled_modules({"CRM": true, "ERP": "true", "Manufacturing": 1})
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
