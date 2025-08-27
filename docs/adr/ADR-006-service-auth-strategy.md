# ADR-006: Authentication and Authorization for Service Module

## Status
Proposed

## Context

The Service CRM integration introduces new user types and access patterns that extend beyond the existing ERP user management system. We need to design authentication and authorization mechanisms that support:

- **Multi-Role Access**: Technicians, customers, service managers, dispatchers
- **Customer Self-Service**: External customer access to booking and history
- **Mobile Workforce**: Secure mobile app authentication with offline capabilities
- **API Integration**: Third-party integrations and webhook access
- **Granular Permissions**: Service-specific permissions within existing role framework

### Current Authentication System
- **JWT Tokens**: HS256 signed tokens with user and organization context
- **Role-Based Access**: Super admin, org admin, admin, standard user roles
- **Multi-Tenant**: Organization-scoped authentication and data access
- **Session Management**: Token expiration and refresh mechanisms

### New Requirements
- **Customer Authentication**: External customer access without full ERP access
- **Technician Mobile**: Secure mobile authentication with extended session times
- **Service Permissions**: Granular permissions for service operations
- **API Keys**: Third-party integration authentication
- **Offline Authentication**: Mobile app operation when disconnected

## Decision

We will extend the existing JWT authentication system with **role-based service permissions** and **multi-audience token support** while maintaining backward compatibility with the current ERP authentication.

### Authentication Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Authentication Gateway                   │
├─────────────────────────────────────────────────────────────┤
│  Token Types: Standard JWT | Customer JWT | API Key        │
├─────────────────────────────────────────────────────────────┤
│              Role-Based Permission Matrix                   │
├─────────────────────────────────────────────────────────────┤
│  Service Permissions: Catalog | Scheduling | Execution     │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
   ┌────▼────┐         ┌─────▼─────┐         ┌─────▼─────┐
   │   ERP   │         │  Service  │         │ Customer  │
   │  Users  │         │   CRM     │         │  Portal   │
   │         │         │  Mobile   │         │           │
   └─────────┘         └───────────┘         └───────────┘
```

## Implementation Details

### Extended User Roles and Permissions

```python
# Enhanced role definitions
class ServiceRole(str, Enum):
    # Existing ERP roles
    SUPER_ADMIN = "super_admin"
    ORG_ADMIN = "org_admin" 
    ADMIN = "admin"
    STANDARD_USER = "standard_user"
    
    # New service-specific roles
    SERVICE_MANAGER = "service_manager"      # Full service management
    DISPATCHER = "dispatcher"               # Scheduling and assignment
    TECHNICIAN = "technician"              # Field service execution
    CUSTOMER_SERVICE = "customer_service"   # Customer interaction
    CUSTOMER = "customer"                  # External customer access

# Service permission matrix
SERVICE_PERMISSIONS = {
    "super_admin": ["*"],  # All permissions
    "org_admin": ["*"],    # All org permissions
    "service_manager": [
        "service_catalog.*",
        "technician.*", 
        "appointment.*",
        "customer_service.*",
        "reports.*"
    ],
    "dispatcher": [
        "appointment.read",
        "appointment.create", 
        "appointment.update",
        "technician.read",
        "customer.read"
    ],
    "technician": [
        "appointment.read_assigned",
        "appointment.update_assigned",
        "service_execution.*",
        "customer.read_assigned"
    ],
    "customer_service": [
        "appointment.read",
        "appointment.create",
        "customer.read",
        "customer.update",
        "service_catalog.read"
    ],
    "customer": [
        "appointment.read_own",
        "appointment.create_own",
        "appointment.update_own",
        "service_catalog.read",
        "service_history.read_own"
    ]
}
```

### JWT Token Structure

```python
# Enhanced JWT payload for service operations
class ServiceJWTPayload(BaseModel):
    # Standard fields
    sub: str  # User ID
    email: str
    organization_id: Optional[int]
    role: ServiceRole
    
    # Service-specific fields
    customer_id: Optional[int]  # For customer tokens
    technician_id: Optional[int]  # For technician tokens
    service_permissions: List[str]
    audience: str  # "erp", "service", "customer", "mobile"
    
    # Token metadata
    iat: int  # Issued at
    exp: int  # Expires at
    refresh_until: int  # Refresh token validity

# Token generation for different user types
class ServiceTokenGenerator:
    def generate_erp_user_token(self, user: User) -> str:
        """Standard ERP user token with service permissions"""
        payload = ServiceJWTPayload(
            sub=str(user.id),
            email=user.email,
            organization_id=user.organization_id,
            role=user.role,
            service_permissions=SERVICE_PERMISSIONS.get(user.role, []),
            audience="service",
            iat=int(time.time()),
            exp=int(time.time()) + 3600,  # 1 hour
            refresh_until=int(time.time()) + 86400  # 24 hours
        )
        return jwt.encode(payload.dict(), self.secret_key, algorithm="HS256")
    
    def generate_customer_token(self, customer: Customer) -> str:
        """Customer portal access token"""
        payload = ServiceJWTPayload(
            sub=f"customer_{customer.id}",
            email=customer.email,
            organization_id=customer.organization_id,
            customer_id=customer.id,
            role=ServiceRole.CUSTOMER,
            service_permissions=SERVICE_PERMISSIONS["customer"],
            audience="customer",
            iat=int(time.time()),
            exp=int(time.time()) + 7200,  # 2 hours
            refresh_until=int(time.time()) + 86400  # 24 hours
        )
        return jwt.encode(payload.dict(), self.secret_key, algorithm="HS256")
    
    def generate_technician_mobile_token(self, technician: Technician) -> str:
        """Extended session token for mobile technician app"""
        payload = ServiceJWTPayload(
            sub=str(technician.user.id),
            email=technician.user.email,
            organization_id=technician.organization_id,
            technician_id=technician.id,
            role=ServiceRole.TECHNICIAN,
            service_permissions=SERVICE_PERMISSIONS["technician"],
            audience="mobile",
            iat=int(time.time()),
            exp=int(time.time()) + 28800,  # 8 hours
            refresh_until=int(time.time()) + 604800  # 7 days
        )
        return jwt.encode(payload.dict(), self.secret_key, algorithm="HS256")
```

### Authorization Middleware

```python
from functools import wraps
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer

security = HTTPBearer()

class ServiceAuthValidator:
    def __init__(self):
        self.secret_key = settings.SECRET_KEY
    
    def validate_token(self, token: str) -> ServiceJWTPayload:
        """Validate and decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            return ServiceJWTPayload(**payload)
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")
    
    def check_permission(self, payload: ServiceJWTPayload, required_permission: str) -> bool:
        """Check if user has required permission"""
        if "*" in payload.service_permissions:
            return True
        
        # Check exact permission
        if required_permission in payload.service_permissions:
            return True
        
        # Check wildcard permissions
        permission_parts = required_permission.split(".")
        for perm in payload.service_permissions:
            if perm.endswith(".*"):
                perm_prefix = perm[:-2]
                if required_permission.startswith(perm_prefix):
                    return True
        
        return False

# Authorization decorators
def require_service_permission(permission: str):
    """Decorator to require specific service permission"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract token from request
            token = kwargs.get('token') or get_token_from_request()
            
            # Validate token and check permission
            auth_validator = ServiceAuthValidator()
            payload = auth_validator.validate_token(token)
            
            if not auth_validator.check_permission(payload, permission):
                raise HTTPException(
                    status_code=403, 
                    detail=f"Insufficient permissions: {permission} required"
                )
            
            # Add payload to request context
            kwargs['current_user'] = payload
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def require_technician_access():
    """Decorator for technician-only endpoints"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            token = get_token_from_request()
            auth_validator = ServiceAuthValidator()
            payload = auth_validator.validate_token(token)
            
            if payload.role != ServiceRole.TECHNICIAN:
                raise HTTPException(status_code=403, detail="Technician access required")
            
            if not payload.technician_id:
                raise HTTPException(status_code=403, detail="Invalid technician token")
            
            kwargs['technician_id'] = payload.technician_id
            kwargs['current_user'] = payload
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def require_customer_access():
    """Decorator for customer portal endpoints"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            token = get_token_from_request()
            auth_validator = ServiceAuthValidator()
            payload = auth_validator.validate_token(token)
            
            if payload.audience != "customer":
                raise HTTPException(status_code=403, detail="Customer access required")
            
            if not payload.customer_id:
                raise HTTPException(status_code=403, detail="Invalid customer token")
            
            kwargs['customer_id'] = payload.customer_id
            kwargs['current_user'] = payload
            return await func(*args, **kwargs)
        return wrapper
    return decorator
```

### API Key Authentication

```python
# API key model for third-party integrations
class APIKey(Base):
    __tablename__ = "api_keys"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"))
    
    name: Mapped[str] = mapped_column(String, nullable=False)
    key_hash: Mapped[str] = mapped_column(String, nullable=False, index=True)
    permissions: Mapped[List[str]] = mapped_column(JSON, nullable=False)
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_used: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))

class APIKeyManager:
    def generate_api_key(self, organization_id: int, name: str, permissions: List[str]) -> tuple[str, APIKey]:
        """Generate new API key"""
        raw_key = secrets.token_urlsafe(32)
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        
        api_key = APIKey(
            organization_id=organization_id,
            name=name,
            key_hash=key_hash,
            permissions=permissions
        )
        
        return f"tritiq_{raw_key}", api_key
    
    def validate_api_key(self, api_key: str) -> Optional[APIKey]:
        """Validate API key and return key record"""
        if not api_key.startswith("tritiq_"):
            return None
        
        raw_key = api_key[7:]  # Remove prefix
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        
        return session.query(APIKey).filter(
            APIKey.key_hash == key_hash,
            APIKey.is_active == True,
            or_(APIKey.expires_at.is_(None), APIKey.expires_at > datetime.utcnow())
        ).first()

# API key authentication decorator
def require_api_key(required_permissions: List[str] = None):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            api_key = request.headers.get("X-API-Key")
            if not api_key:
                raise HTTPException(status_code=401, detail="API key required")
            
            key_manager = APIKeyManager()
            api_key_record = key_manager.validate_api_key(api_key)
            
            if not api_key_record:
                raise HTTPException(status_code=401, detail="Invalid API key")
            
            # Check permissions
            if required_permissions:
                for perm in required_permissions:
                    if perm not in api_key_record.permissions and "*" not in api_key_record.permissions:
                        raise HTTPException(status_code=403, detail=f"Permission {perm} required")
            
            # Update last used timestamp
            api_key_record.last_used = datetime.utcnow()
            session.commit()
            
            kwargs['api_key'] = api_key_record
            return await func(*args, **kwargs)
        return wrapper
    return decorator
```

### Customer Authentication Flow

```python
# Customer registration and authentication
class CustomerAuthService:
    def register_customer(self, customer_data: CustomerRegistration) -> dict:
        """Register new customer for portal access"""
        # Check if customer exists
        existing_customer = session.query(Customer).filter(
            Customer.email == customer_data.email,
            Customer.organization_id == customer_data.organization_id
        ).first()
        
        if existing_customer:
            raise HTTPException(status_code=409, detail="Customer already exists")
        
        # Create customer record
        customer = Customer(
            organization_id=customer_data.organization_id,
            name=customer_data.name,
            email=customer_data.email,
            phone=customer_data.phone,
            address1=customer_data.address1,
            city=customer_data.city,
            state=customer_data.state,
            pin_code=customer_data.pin_code
        )
        
        # Create customer portal access
        portal_access = CustomerPortalAccess(
            customer=customer,
            password_hash=hash_password(customer_data.password),
            email_verified=False,
            is_active=True
        )
        
        session.add_all([customer, portal_access])
        session.commit()
        
        # Send verification email
        self.send_verification_email(customer)
        
        return {"message": "Customer registered successfully", "customer_id": customer.id}
    
    def authenticate_customer(self, email: str, password: str, organization_id: int) -> dict:
        """Authenticate customer for portal access"""
        portal_access = session.query(CustomerPortalAccess).join(Customer).filter(
            Customer.email == email,
            Customer.organization_id == organization_id,
            CustomerPortalAccess.is_active == True
        ).first()
        
        if not portal_access or not verify_password(password, portal_access.password_hash):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        if not portal_access.email_verified:
            raise HTTPException(status_code=401, detail="Email not verified")
        
        # Generate customer token
        token_generator = ServiceTokenGenerator()
        access_token = token_generator.generate_customer_token(portal_access.customer)
        refresh_token = token_generator.generate_refresh_token(portal_access.customer)
        
        # Update last login
        portal_access.last_login = datetime.utcnow()
        session.commit()
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "customer": CustomerSummary.from_orm(portal_access.customer)
        }
```

### Mobile Offline Authentication

```python
# Mobile app offline authentication support
class MobileAuthService:
    def generate_offline_auth_data(self, technician_id: int) -> dict:
        """Generate offline authentication data for mobile app"""
        technician = session.query(Technician).get(technician_id)
        
        # Generate long-lived offline token
        offline_payload = {
            "technician_id": technician_id,
            "organization_id": technician.organization_id,
            "role": "technician",
            "offline": True,
            "exp": int(time.time()) + 2592000,  # 30 days
            "permissions": SERVICE_PERMISSIONS["technician"]
        }
        
        offline_token = jwt.encode(offline_payload, settings.OFFLINE_SECRET_KEY)
        
        # Generate sync keys for secure data storage
        sync_key = secrets.token_bytes(32)
        encrypted_sync_key = self.encrypt_with_device_key(sync_key, technician.device_id)
        
        return {
            "offline_token": offline_token,
            "sync_key": base64.b64encode(encrypted_sync_key).decode(),
            "organization_id": technician.organization_id,
            "technician_profile": TechnicianProfile.from_orm(technician)
        }
    
    def validate_offline_token(self, token: str) -> dict:
        """Validate offline token for mobile app"""
        try:
            payload = jwt.decode(token, settings.OFFLINE_SECRET_KEY, algorithms=["HS256"])
            
            if not payload.get("offline"):
                raise HTTPException(status_code=401, detail="Invalid offline token")
            
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Offline token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid offline token")
```

## Security Considerations

### Token Security
- **Secret Key Rotation**: Regular rotation of JWT signing keys
- **Token Blacklisting**: Maintain blacklist for revoked tokens
- **Refresh Token Security**: Secure storage and automatic rotation
- **Rate Limiting**: Prevent brute force authentication attempts

### API Key Security
- **Hashed Storage**: API keys stored as SHA-256 hashes
- **Scope Limitation**: Granular permissions for each API key
- **Expiration**: Automatic expiration and renewal processes
- **Audit Logging**: Complete logging of API key usage

### Customer Data Protection
- **Email Verification**: Required for customer portal access
- **Password Security**: Strong password requirements and hashing
- **Data Isolation**: Customers can only access their own data
- **Session Management**: Automatic logout after inactivity

## Implementation Guidelines

### Authentication Flow Examples

```python
# Example API endpoint implementations
@router.post("/api/v1/organizations/{org_id}/appointments")
@require_service_permission("appointment.create")
async def create_appointment(
    org_id: int,
    appointment_data: AppointmentCreate,
    current_user: ServiceJWTPayload = Depends(get_current_user)
):
    """Create new service appointment"""
    # Implementation with organization scoping
    pass

@router.get("/api/v1/mobile/technician/{tech_id}/assignments")
@require_technician_access()
async def get_technician_assignments(
    tech_id: int,
    technician_id: int = None,  # From decorator
    current_user: ServiceJWTPayload = None  # From decorator
):
    """Get assignments for technician mobile app"""
    if tech_id != technician_id:
        raise HTTPException(status_code=403, detail="Access denied")
    # Implementation
    pass

@router.get("/api/v1/customer-portal/appointments")
@require_customer_access()
async def get_customer_appointments(
    customer_id: int = None,  # From decorator
    current_user: ServiceJWTPayload = None  # From decorator
):
    """Get customer's appointments"""
    # Implementation with customer scoping
    pass

@router.post("/webhook/appointment-booked")
@require_api_key(["webhook.write"])
async def appointment_webhook(
    webhook_data: dict,
    api_key: APIKey = None  # From decorator
):
    """Handle external appointment booking webhook"""
    # Implementation with API key context
    pass
```

## Consequences

### Positive
- **Flexibility**: Supports diverse user types and access patterns
- **Security**: Granular permissions and secure token management
- **Backward Compatibility**: Extends existing authentication without breaking changes
- **Scalability**: Supports high-volume mobile and customer portal usage
- **Integration**: Enables secure third-party API access

### Negative
- **Complexity**: Multiple authentication patterns increase system complexity
- **Token Management**: More token types to manage and secure
- **Performance**: Additional permission checks may impact response times
- **Documentation**: Extensive documentation needed for different auth patterns

### Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Token compromise | Short expiration times, refresh rotation, blacklisting |
| Permission escalation | Strict permission validation, audit logging |
| Customer data breach | Data isolation, encryption, access monitoring |
| API key misuse | Scope limitation, usage monitoring, automatic revocation |

## Monitoring and Alerting

```python
# Authentication metrics and monitoring
auth_attempts = Counter(
    "auth_attempts_total",
    "Authentication attempts",
    ["type", "status", "organization"]
)

token_generation = Counter(
    "tokens_generated_total", 
    "Tokens generated",
    ["type", "role", "audience"]
)

permission_checks = Histogram(
    "permission_check_duration_seconds",
    "Permission check duration",
    ["permission", "result"]
)

# Security alerts
class SecurityAlertManager:
    async def monitor_auth_anomalies(self):
        """Monitor for authentication anomalies"""
        # Failed login attempts
        # Unusual access patterns
        # Token usage anomalies
        pass
    
    async def alert_suspicious_activity(self, event: SecurityEvent):
        """Alert on suspicious authentication activity"""
        # Send alerts to security team
        # Log security events
        # Auto-block if necessary
        pass
```

## Testing Strategy

```python
# Authentication testing examples
class TestServiceAuthentication:
    async def test_technician_token_generation(self):
        """Test technician token contains correct permissions"""
        technician = create_test_technician()
        token = ServiceTokenGenerator().generate_technician_mobile_token(technician)
        
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        assert payload["role"] == "technician"
        assert "appointment.read_assigned" in payload["service_permissions"]
    
    async def test_customer_portal_access(self):
        """Test customer can only access own data"""
        customer = create_test_customer()
        token = ServiceTokenGenerator().generate_customer_token(customer)
        
        # Test accessing own appointments
        response = await client.get(
            "/api/v1/customer-portal/appointments",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        
        # Test accessing other customer's data (should fail)
        other_customer_id = create_other_customer().id
        response = await client.get(
            f"/api/v1/customer-portal/customers/{other_customer_id}/appointments",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 403
    
    async def test_api_key_permissions(self):
        """Test API key permission validation"""
        api_key = create_test_api_key(permissions=["appointment.read"])
        
        # Test allowed operation
        response = await client.get(
            "/api/v1/organizations/1/appointments",
            headers={"X-API-Key": api_key.key}
        )
        assert response.status_code == 200
        
        # Test forbidden operation
        response = await client.post(
            "/api/v1/organizations/1/appointments",
            headers={"X-API-Key": api_key.key}
        )
        assert response.status_code == 403
```

## Related ADRs
- ADR-001: Multi-Tenant Service CRM Architecture
- ADR-002: Database Schema Design for Service Management
- ADR-003: API Design Patterns for Service Endpoints
- ADR-004: Mobile Workforce Application Strategy
- ADR-008: Service Data Privacy and Compliance