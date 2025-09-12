# app/services/security_enhancements.py
"""
Enhanced Security Service for Advanced Access Controls and Security Features
"""

import hashlib
import hmac
import secrets
import jwt
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import text, and_, or_
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import ipaddress
import re
from enum import Enum

from app.core.config import settings
from app.models.user_models import User, Organization
from app.models.system_models import AuditLog

logger = logging.getLogger(__name__)


class SecurityLevel(str, Enum):
    """Security levels for different operations"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ThreatType(str, Enum):
    """Types of security threats"""
    BRUTE_FORCE = "brute_force"
    SQL_INJECTION = "sql_injection"
    XSS = "xss"
    CSRF = "csrf"
    DATA_BREACH = "data_breach"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"


class SecurityEnhancementService:
    """Enhanced security service with advanced features"""
    
    def __init__(self, db: Session):
        self.db = db
        self._failed_attempts = {}  # In production, use Redis
        self._security_cache = {}
        self.max_failed_attempts = 5
        self.lockout_duration = timedelta(minutes=30)
        self.encryption_key = self._get_or_create_encryption_key()
    
    # ============================================================================
    # ADVANCED AUTHENTICATION SECURITY
    # ============================================================================
    
    def validate_login_security(
        self, 
        email: str, 
        ip_address: str, 
        user_agent: str,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Comprehensive login security validation"""
        
        security_result = {
            "allowed": True,
            "security_level": SecurityLevel.LOW,
            "warnings": [],
            "requirements": [],
            "threat_indicators": []
        }
        
        # Check for brute force attempts
        brute_force_check = self._check_brute_force_protection(email, ip_address)
        if not brute_force_check["allowed"]:
            security_result["allowed"] = False
            security_result["security_level"] = SecurityLevel.CRITICAL
            security_result["threat_indicators"].append({
                "type": ThreatType.BRUTE_FORCE,
                "details": brute_force_check
            })
        
        # Geo-location analysis
        geo_analysis = self._analyze_geolocation(ip_address, email)
        if geo_analysis["suspicious"]:
            security_result["security_level"] = SecurityLevel.HIGH
            security_result["warnings"].append("Login from unusual location")
            security_result["requirements"].append("additional_verification")
        
        # Device fingerprinting
        device_analysis = self._analyze_device_fingerprint(user_agent, email)
        if device_analysis["new_device"]:
            security_result["security_level"] = SecurityLevel.MEDIUM
            security_result["warnings"].append("Login from new device")
            security_result["requirements"].append("device_verification")
        
        # Time-based analysis
        time_analysis = self._analyze_login_time_patterns(email)
        if time_analysis["unusual_time"]:
            security_result["warnings"].append("Login at unusual time")
        
        # Check for known threat indicators
        threat_check = self._check_threat_intelligence(ip_address, user_agent)
        if threat_check["threats_found"]:
            security_result["security_level"] = SecurityLevel.CRITICAL
            security_result["threat_indicators"].extend(threat_check["threats"])
        
        return security_result
    
    def _check_brute_force_protection(self, email: str, ip_address: str) -> Dict[str, Any]:
        """Check for brute force attack patterns"""
        
        current_time = datetime.now()
        
        # Check email-based attempts
        email_key = f"email:{email}"
        email_attempts = self._failed_attempts.get(email_key, [])
        email_attempts = [
            attempt for attempt in email_attempts 
            if current_time - attempt["timestamp"] < self.lockout_duration
        ]
        
        # Check IP-based attempts
        ip_key = f"ip:{ip_address}"
        ip_attempts = self._failed_attempts.get(ip_key, [])
        ip_attempts = [
            attempt for attempt in ip_attempts 
            if current_time - attempt["timestamp"] < self.lockout_duration
        ]
        
        if len(email_attempts) >= self.max_failed_attempts:
            return {
                "allowed": False,
                "reason": "Account temporarily locked due to multiple failed attempts",
                "lockout_until": email_attempts[0]["timestamp"] + self.lockout_duration,
                "attempt_count": len(email_attempts)
            }
        
        if len(ip_attempts) >= self.max_failed_attempts * 2:  # Higher threshold for IP
            return {
                "allowed": False,
                "reason": "IP address temporarily blocked",
                "lockout_until": ip_attempts[0]["timestamp"] + self.lockout_duration,
                "attempt_count": len(ip_attempts)
            }
        
        return {"allowed": True, "email_attempts": len(email_attempts), "ip_attempts": len(ip_attempts)}
    
    def record_failed_login_attempt(self, email: str, ip_address: str, reason: str):
        """Record a failed login attempt"""
        
        current_time = datetime.now()
        attempt_data = {
            "timestamp": current_time,
            "ip_address": ip_address,
            "reason": reason
        }
        
        # Record by email
        email_key = f"email:{email}"
        if email_key not in self._failed_attempts:
            self._failed_attempts[email_key] = []
        self._failed_attempts[email_key].append(attempt_data)
        
        # Record by IP
        ip_key = f"ip:{ip_address}"
        if ip_key not in self._failed_attempts:
            self._failed_attempts[ip_key] = []
        self._failed_attempts[ip_key].append(attempt_data)
        
        # Log security event
        self._log_security_event(
            event_type="failed_login",
            severity="medium",
            details={
                "email": email,
                "ip_address": ip_address,
                "reason": reason,
                "timestamp": current_time.isoformat()
            }
        )
    
    def clear_failed_attempts(self, email: str, ip_address: str):
        """Clear failed attempts after successful login"""
        
        email_key = f"email:{email}"
        ip_key = f"ip:{ip_address}"
        
        if email_key in self._failed_attempts:
            del self._failed_attempts[email_key]
        
        # Don't clear IP attempts to prevent rapid-fire attempts
    
    # ============================================================================
    # ADVANCED ACCESS CONTROL
    # ============================================================================
    
    def validate_api_access(
        self,
        user_id: int,
        endpoint: str,
        method: str,
        ip_address: str,
        api_key: Optional[str] = None,
        request_headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Comprehensive API access validation"""
        
        access_result = {
            "allowed": True,
            "security_level": SecurityLevel.LOW,
            "rate_limit": None,
            "audit_required": False,
            "additional_verification": False
        }
        
        # Get user security profile
        user_profile = self._get_user_security_profile(user_id)
        
        # Check endpoint security requirements
        endpoint_security = self._get_endpoint_security_requirements(endpoint, method)
        
        # IP whitelist/blacklist check
        ip_check = self._validate_ip_access(ip_address, user_profile, endpoint_security)
        if not ip_check["allowed"]:
            access_result["allowed"] = False
            access_result["security_level"] = SecurityLevel.HIGH
            return access_result
        
        # Time-based access control
        time_check = self._validate_time_access(user_profile, endpoint_security)
        if not time_check["allowed"]:
            access_result["allowed"] = False
            access_result["security_level"] = SecurityLevel.MEDIUM
            return access_result
        
        # Rate limiting
        rate_limit_check = self._check_rate_limits(user_id, endpoint, ip_address)
        access_result["rate_limit"] = rate_limit_check
        
        if rate_limit_check["exceeded"]:
            access_result["allowed"] = False
            access_result["security_level"] = SecurityLevel.MEDIUM
            return access_result
        
        # Sensitive operation detection
        if endpoint_security["sensitivity_level"] in ["high", "critical"]:
            access_result["audit_required"] = True
            access_result["security_level"] = SecurityLevel.HIGH
            
            if endpoint_security["sensitivity_level"] == "critical":
                access_result["additional_verification"] = True
                access_result["security_level"] = SecurityLevel.CRITICAL
        
        return access_result
    
    def _get_user_security_profile(self, user_id: int) -> Dict[str, Any]:
        """Get comprehensive user security profile"""
        
        cache_key = f"user_security_profile:{user_id}"
        if cache_key in self._security_cache:
            cached = self._security_cache[cache_key]
            if datetime.now() - cached["timestamp"] < timedelta(minutes=15):
                return cached["data"]
        
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return {}
        
        # Get user's recent activity patterns
        recent_activity = self._analyze_user_activity_patterns(user_id)
        
        profile = {
            "user_id": user_id,
            "role": user.role,
            "last_login": user.last_login_at,
            "account_created": user.created_at,
            "trusted_ips": getattr(user, 'trusted_ips', []),
            "allowed_time_ranges": getattr(user, 'allowed_time_ranges', []),
            "security_level": getattr(user, 'security_level', 'standard'),
            "two_factor_enabled": getattr(user, 'two_factor_enabled', False),
            "recent_activity": recent_activity
        }
        
        # Cache the profile
        self._security_cache[cache_key] = {
            "data": profile,
            "timestamp": datetime.now()
        }
        
        return profile
    
    def _get_endpoint_security_requirements(self, endpoint: str, method: str) -> Dict[str, Any]:
        """Get security requirements for specific endpoint"""
        
        # Define security requirements for different endpoint patterns
        security_rules = {
            # Critical operations
            r"/api/v1/admin/.*": {
                "sensitivity_level": "critical",
                "requires_audit": True,
                "allowed_methods": ["GET", "POST", "PUT", "DELETE"],
                "ip_restrictions": True,
                "time_restrictions": True
            },
            r"/api/v1/organizations/.*": {
                "sensitivity_level": "high",
                "requires_audit": True,
                "allowed_methods": ["GET", "POST", "PUT"],
                "ip_restrictions": False,
                "time_restrictions": False
            },
            r"/api/v1/finance/.*": {
                "sensitivity_level": "high",
                "requires_audit": True,
                "allowed_methods": ["GET", "POST", "PUT"],
                "ip_restrictions": False,
                "time_restrictions": True
            },
            r"/api/v1/users/.*": {
                "sensitivity_level": "medium",
                "requires_audit": True,
                "allowed_methods": ["GET", "POST", "PUT"],
                "ip_restrictions": False,
                "time_restrictions": False
            },
            # Payment operations
            r"/api/v1/external-integrations/payment/.*": {
                "sensitivity_level": "critical",
                "requires_audit": True,
                "allowed_methods": ["POST"],
                "ip_restrictions": True,
                "time_restrictions": False
            },
            # Default for other endpoints
            "default": {
                "sensitivity_level": "low",
                "requires_audit": False,
                "allowed_methods": ["GET", "POST", "PUT", "DELETE"],
                "ip_restrictions": False,
                "time_restrictions": False
            }
        }
        
        # Find matching rule
        for pattern, rules in security_rules.items():
            if pattern != "default" and re.match(pattern, endpoint):
                return rules
        
        return security_rules["default"]
    
    def _validate_ip_access(
        self, 
        ip_address: str, 
        user_profile: Dict[str, Any], 
        endpoint_security: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate IP-based access control"""
        
        # Check if IP restrictions are required
        if not endpoint_security.get("ip_restrictions", False):
            return {"allowed": True}
        
        # Check user's trusted IPs
        trusted_ips = user_profile.get("trusted_ips", [])
        if trusted_ips:
            for trusted_ip in trusted_ips:
                if self._ip_in_range(ip_address, trusted_ip):
                    return {"allowed": True, "reason": "trusted_ip"}
        
        # Check organization's allowed IP ranges
        organization_ips = self._get_organization_ip_ranges(user_profile.get("organization_id"))
        if organization_ips:
            for allowed_range in organization_ips:
                if self._ip_in_range(ip_address, allowed_range):
                    return {"allowed": True, "reason": "organization_range"}
        
        # Check global blacklist
        if self._is_ip_blacklisted(ip_address):
            return {"allowed": False, "reason": "blacklisted_ip"}
        
        # If IP restrictions are enabled but no ranges defined, allow but log
        self._log_security_event(
            event_type="ip_access_warning",
            severity="medium",
            details={
                "ip_address": ip_address,
                "user_id": user_profile.get("user_id"),
                "reason": "Access from non-whitelisted IP"
            }
        )
        
        return {"allowed": True, "reason": "no_restrictions_configured"}
    
    def _validate_time_access(
        self, 
        user_profile: Dict[str, Any], 
        endpoint_security: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate time-based access control"""
        
        if not endpoint_security.get("time_restrictions", False):
            return {"allowed": True}
        
        current_time = datetime.now().time()
        current_day = datetime.now().weekday()  # 0 = Monday
        
        # Check user's allowed time ranges
        allowed_ranges = user_profile.get("allowed_time_ranges", [])
        if allowed_ranges:
            for time_range in allowed_ranges:
                if self._is_time_in_range(current_time, current_day, time_range):
                    return {"allowed": True}
            
            return {"allowed": False, "reason": "outside_allowed_hours"}
        
        # Default business hours check for high-security endpoints
        if endpoint_security["sensitivity_level"] in ["high", "critical"]:
            business_hours = {
                "start_time": "09:00",
                "end_time": "18:00",
                "allowed_days": [0, 1, 2, 3, 4]  # Monday to Friday
            }
            
            if not self._is_time_in_range(current_time, current_day, business_hours):
                return {"allowed": False, "reason": "outside_business_hours"}
        
        return {"allowed": True}
    
    # ============================================================================
    # DATA ENCRYPTION AND PROTECTION
    # ============================================================================
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data using Fernet encryption"""
        
        f = Fernet(self.encryption_key)
        encrypted_data = f.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted_data).decode()
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        
        try:
            f = Fernet(self.encryption_key)
            decoded_data = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_data = f.decrypt(decoded_data)
            return decrypted_data.decode()
        except Exception as e:
            logger.error(f"Failed to decrypt data: {e}")
            raise ValueError("Failed to decrypt data")
    
    def hash_sensitive_data(self, data: str, salt: Optional[bytes] = None) -> Dict[str, str]:
        """Hash sensitive data with salt"""
        
        if salt is None:
            salt = secrets.token_bytes(32)
        
        # Use PBKDF2 for key derivation
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        
        key = kdf.derive(data.encode())
        hashed = base64.urlsafe_b64encode(key).decode()
        salt_b64 = base64.urlsafe_b64encode(salt).decode()
        
        return {
            "hash": hashed,
            "salt": salt_b64
        }
    
    def verify_hashed_data(self, data: str, stored_hash: str, stored_salt: str) -> bool:
        """Verify hashed data"""
        
        try:
            salt = base64.urlsafe_b64decode(stored_salt.encode())
            hash_result = self.hash_sensitive_data(data, salt)
            return hash_result["hash"] == stored_hash
        except Exception as e:
            logger.error(f"Failed to verify hash: {e}")
            return False
    
    # ============================================================================
    # AUDIT AND COMPLIANCE
    # ============================================================================
    
    def log_security_audit(
        self,
        user_id: Optional[int],
        action: str,
        resource_type: str,
        resource_id: Optional[int],
        ip_address: str,
        user_agent: str,
        additional_data: Optional[Dict[str, Any]] = None
    ):
        """Log security audit event"""
        
        audit_log = AuditLog(
            organization_id=None,  # Security logs are global
            table_name=resource_type,
            record_id=resource_id,
            action=action,
            user_id=user_id,
            changes=additional_data or {},
            ip_address=ip_address,
            user_agent=user_agent,
            timestamp=datetime.utcnow()
        )
        
        self.db.add(audit_log)
        self.db.commit()
        
        # Also log to security event system
        self._log_security_event(
            event_type="audit_action",
            severity="info",
            details={
                "user_id": user_id,
                "action": action,
                "resource_type": resource_type,
                "resource_id": resource_id,
                "ip_address": ip_address,
                "additional_data": additional_data
            }
        )
    
    def generate_security_report(
        self, 
        organization_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Generate comprehensive security report"""
        
        # Failed login attempts
        failed_logins = self.db.execute(text("""
            SELECT COUNT(*) as count, DATE(timestamp) as date
            FROM audit_logs 
            WHERE action = 'failed_login' 
            AND timestamp BETWEEN :start_date AND :end_date
            GROUP BY DATE(timestamp)
            ORDER BY date
        """), {
            "start_date": start_date,
            "end_date": end_date
        }).fetchall()
        
        # Suspicious activities
        suspicious_activities = self.db.execute(text("""
            SELECT action, COUNT(*) as count
            FROM audit_logs 
            WHERE action IN ('unauthorized_access', 'suspicious_activity', 'data_breach_attempt')
            AND timestamp BETWEEN :start_date AND :end_date
            GROUP BY action
        """), {
            "start_date": start_date,
            "end_date": end_date
        }).fetchall()
        
        # User access patterns
        user_access = self.db.execute(text("""
            SELECT user_id, COUNT(*) as access_count, 
                   COUNT(DISTINCT ip_address) as unique_ips
            FROM audit_logs 
            WHERE timestamp BETWEEN :start_date AND :end_date
            AND user_id IS NOT NULL
            GROUP BY user_id
            ORDER BY access_count DESC
            LIMIT 20
        """), {
            "start_date": start_date,
            "end_date": end_date
        }).fetchall()
        
        return {
            "report_period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "failed_login_trends": [
                {"date": row[1], "count": row[0]} for row in failed_logins
            ],
            "suspicious_activities": [
                {"activity": row[0], "count": row[1]} for row in suspicious_activities
            ],
            "top_users_by_activity": [
                {
                    "user_id": row[0],
                    "access_count": row[1],
                    "unique_ips": row[2]
                } for row in user_access
            ],
            "security_score": self._calculate_security_score(
                len(failed_logins), len(suspicious_activities)
            )
        }
    
    # ============================================================================
    # UTILITY METHODS
    # ============================================================================
    
    def _get_or_create_encryption_key(self) -> bytes:
        """Get or create encryption key"""
        
        # In production, use proper key management (AWS KMS, Azure Key Vault, etc.)
        if hasattr(settings, 'ENCRYPTION_KEY') and settings.ENCRYPTION_KEY:
            return settings.ENCRYPTION_KEY.encode()
        else:
            # Generate a new key (for development only)
            return Fernet.generate_key()
    
    def _log_security_event(self, event_type: str, severity: str, details: Dict[str, Any]):
        """Log security event to monitoring system"""
        
        # In production, integrate with SIEM or security monitoring platform
        logger.warning(f"Security Event - Type: {event_type}, Severity: {severity}, Details: {details}")
    
    def _ip_in_range(self, ip_address: str, ip_range: str) -> bool:
        """Check if IP address is in the specified range"""
        
        try:
            if "/" in ip_range:
                # CIDR notation
                network = ipaddress.ip_network(ip_range, strict=False)
                ip = ipaddress.ip_address(ip_address)
                return ip in network
            else:
                # Single IP
                return ip_address == ip_range
        except ValueError:
            return False
    
    def _is_time_in_range(self, current_time, current_day, time_range) -> bool:
        """Check if current time is within allowed range"""
        
        # Check day of week if specified
        if "allowed_days" in time_range:
            if current_day not in time_range["allowed_days"]:
                return False
        
        # Check time range
        start_time = datetime.strptime(time_range["start_time"], "%H:%M").time()
        end_time = datetime.strptime(time_range["end_time"], "%H:%M").time()
        
        if start_time <= end_time:
            return start_time <= current_time <= end_time
        else:
            # Overnight range (e.g., 22:00 to 06:00)
            return current_time >= start_time or current_time <= end_time
    
    def _analyze_geolocation(self, ip_address: str, email: str) -> Dict[str, Any]:
        """Analyze geolocation for suspicious activity"""
        
        # Placeholder implementation
        # In production, integrate with geolocation service
        return {
            "suspicious": False,
            "country": "Unknown",
            "city": "Unknown",
            "is_new_location": False
        }
    
    def _analyze_device_fingerprint(self, user_agent: str, email: str) -> Dict[str, Any]:
        """Analyze device fingerprint"""
        
        # Simplified device fingerprinting
        # In production, use more sophisticated fingerprinting
        device_hash = hashlib.sha256(user_agent.encode()).hexdigest()
        
        return {
            "new_device": True,  # Placeholder
            "device_hash": device_hash,
            "trusted_device": False
        }
    
    def _analyze_login_time_patterns(self, email: str) -> Dict[str, Any]:
        """Analyze login time patterns for anomalies"""
        
        # Placeholder implementation
        return {
            "unusual_time": False,
            "typical_hours": ["09:00", "18:00"],
            "confidence": 0.85
        }
    
    def _check_threat_intelligence(self, ip_address: str, user_agent: str) -> Dict[str, Any]:
        """Check against threat intelligence feeds"""
        
        # Placeholder implementation
        # In production, integrate with threat intelligence services
        return {
            "threats_found": False,
            "threats": []
        }
    
    def _analyze_user_activity_patterns(self, user_id: int) -> Dict[str, Any]:
        """Analyze user activity patterns"""
        
        # Placeholder implementation
        return {
            "average_daily_requests": 150,
            "peak_hours": ["10:00", "14:00", "16:00"],
            "typical_endpoints": ["/api/v1/customers", "/api/v1/products"],
            "anomaly_score": 0.1
        }
    
    def _check_rate_limits(self, user_id: int, endpoint: str, ip_address: str) -> Dict[str, Any]:
        """Check rate limits for user and endpoint"""
        
        # Placeholder implementation
        return {
            "exceeded": False,
            "remaining": 950,
            "reset_time": datetime.now() + timedelta(hours=1),
            "limit_type": "user_hourly"
        }
    
    def _get_organization_ip_ranges(self, organization_id: int) -> List[str]:
        """Get allowed IP ranges for organization"""
        
        # Placeholder implementation
        return []
    
    def _is_ip_blacklisted(self, ip_address: str) -> bool:
        """Check if IP is in global blacklist"""
        
        # Placeholder implementation
        return False
    
    def _calculate_security_score(self, failed_logins: int, suspicious_activities: int) -> float:
        """Calculate overall security score"""
        
        base_score = 100.0
        
        # Deduct points for security issues
        score = base_score - (failed_logins * 0.5) - (suspicious_activities * 2.0)
        
        return max(0.0, min(100.0, score))