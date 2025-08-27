# app/api/v1/organizations/utils.py

"""
Organization utilities - Helper functions for organization management
"""
import secrets
import string
import re
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


def generate_temporary_password(length: int = 12) -> str:
    """Generate a temporary password for new organization admins"""
    characters = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(characters) for _ in range(length))


def validate_subdomain(subdomain: str) -> bool:
    """Validate subdomain format"""
    # Subdomain must be 3-50 characters, alphanumeric with hyphens
    if not subdomain or len(subdomain) < 3 or len(subdomain) > 50:
        return False
    
    # Must start and end with alphanumeric character
    if not re.match(r'^[a-zA-Z0-9].*[a-zA-Z0-9]$', subdomain):
        return False
    
    # Only allow alphanumeric characters and hyphens
    if not re.match(r'^[a-zA-Z0-9-]+$', subdomain):
        return False
    
    return True


def generate_subdomain(organization_name: str) -> str:
    """Generate a subdomain from organization name"""
    # Convert to lowercase and replace spaces/special chars with hyphens
    subdomain = re.sub(r'[^a-zA-Z0-9]', '-', organization_name.lower())
    
    # Remove multiple consecutive hyphens
    subdomain = re.sub(r'-+', '-', subdomain)
    
    # Remove leading/trailing hyphens
    subdomain = subdomain.strip('-')
    
    # Ensure minimum length
    if len(subdomain) < 3:
        subdomain = f"org-{subdomain}"
    
    # Truncate if too long
    if len(subdomain) > 50:
        subdomain = subdomain[:50].rstrip('-')
    
    return subdomain


def validate_gst_number(gst_number: Optional[str]) -> bool:
    """Validate GST number format (Indian GST)"""
    if not gst_number:
        return True  # GST is optional
    
    # GST format: 2 digits state code + 10 characters PAN + 1 digit checksum + 1 character default + 1 character checksum
    gst_pattern = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$'
    return bool(re.match(gst_pattern, gst_number.upper()))


def validate_pan_number(pan_number: Optional[str]) -> bool:
    """Validate PAN number format (Indian PAN)"""
    if not pan_number:
        return True  # PAN is optional
    
    # PAN format: 5 letters + 4 digits + 1 letter
    pan_pattern = r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$'
    return bool(re.match(pan_pattern, pan_number.upper()))


def validate_pin_code(pin_code: str) -> bool:
    """Validate Indian PIN code format"""
    if not pin_code:
        return False
    
    # PIN code should be 6 digits
    return bool(re.match(r'^[0-9]{6}$', pin_code))


def sanitize_organization_data(data: Dict) -> Dict:
    """Sanitize organization data before database save"""
    sanitized = {}
    
    # String fields to trim
    string_fields = [
        'organization_name', 'superadmin_email', 'primary_phone',
        'address1', 'address2', 'city', 'state', 'pin_code',
        'country', 'state_code', 'gst_number', 'pan_number',
        'cin_number', 'business_type', 'industry', 'website'
    ]
    
    for field in string_fields:
        if field in data and data[field]:
            sanitized[field] = str(data[field]).strip()
        elif field in data:
            sanitized[field] = data[field]
    
    # Numeric fields
    numeric_fields = ['max_users', 'storage_limit_gb']
    for field in numeric_fields:
        if field in data:
            sanitized[field] = data[field]
    
    # Boolean fields
    bool_fields = ['company_details_completed']
    for field in bool_fields:
        if field in data:
            sanitized[field] = data[field]
    
    # Dict fields
    dict_fields = ['enabled_modules', 'features']
    for field in dict_fields:
        if field in data:
            sanitized[field] = data[field]
    
    return sanitized


def get_default_organization_modules() -> Dict[str, bool]:
    """Get default modules for new organizations"""
    return {
        "CRM": True,
        "ERP": True,
        "HR": True,
        "Inventory": True,
        "Service": True,
        "Analytics": True,
        "Finance": True
    }


def log_organization_activity(action: str, organization_id: int, user_id: int, details: Optional[Dict] = None):
    """Log organization-related activities"""
    log_message = f"Organization {action}: org_id={organization_id}, user_id={user_id}"
    if details:
        log_message += f", details={details}"
    
    logger.info(log_message)


def calculate_organization_storage_usage(organization_id: int) -> float:
    """Calculate storage usage for an organization (placeholder)"""
    # This would typically query file storage, database size, etc.
    # For now, return a placeholder value
    return 0.5  # GB