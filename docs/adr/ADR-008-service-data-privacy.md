# ADR-008: Service Data Privacy and Compliance

## Status
Proposed

## Context

The Service CRM integration introduces new types of personal and sensitive data that require comprehensive privacy protection and regulatory compliance. The system will handle:

- **Customer Personal Information**: Names, addresses, phone numbers, email addresses
- **Service History**: Detailed records of services performed at customer locations
- **Location Data**: GPS coordinates from technician mobile apps
- **Photos and Signatures**: Visual documentation from service execution
- **Communication Records**: Email, SMS, and call logs with customers
- **Payment Information**: Credit card and banking details for service payments

### Regulatory Requirements
- **GDPR**: European Union General Data Protection Regulation
- **CCPA**: California Consumer Privacy Act
- **SOC 2**: Security controls for service organizations
- **PCI DSS**: Payment card industry data security standards (if handling payments)
- **Industry-Specific**: HIPAA (healthcare), FERPA (education), or other vertical compliance

### Current System Security
- Multi-tenant data isolation at organization level
- JWT-based authentication with role-based access
- Encrypted database connections
- Basic audit logging for user actions
- HTTPS enforcement for all communications

## Decision

We will implement a **Privacy by Design** approach with comprehensive data protection controls, automated compliance tools, and transparent privacy management throughout the Service CRM system.

### Core Privacy Principles

1. **Data Minimization**: Collect only necessary data for service delivery
2. **Purpose Limitation**: Use data only for stated business purposes
3. **Storage Limitation**: Automatic data retention and deletion policies
4. **Transparency**: Clear privacy notices and consent management
5. **Security**: Encryption, access controls, and breach prevention
6. **Accountability**: Comprehensive audit trails and compliance reporting

## Implementation Framework

### Data Classification and Protection

```python
# Data classification system
class DataClassification(str, Enum):
    PUBLIC = "public"           # Non-sensitive business data
    INTERNAL = "internal"       # Internal business information
    CONFIDENTIAL = "confidential"  # Customer personal information
    RESTRICTED = "restricted"   # Highly sensitive data (payment, biometric)

# Data protection decorator
def protect_data(classification: DataClassification):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Apply appropriate protection based on classification
            if classification == DataClassification.RESTRICTED:
                await validate_restricted_access(func, args, kwargs)
            elif classification == DataClassification.CONFIDENTIAL:
                await validate_confidential_access(func, args, kwargs)
            
            # Log data access for audit trail
            await log_data_access(func, classification, args, kwargs)
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

# Example usage
@protect_data(DataClassification.CONFIDENTIAL)
async def get_customer_service_history(customer_id: int):
    """Get customer service history with privacy protection"""
    pass

@protect_data(DataClassification.RESTRICTED)
async def process_payment_information(payment_data: PaymentInfo):
    """Process payment with restricted data protection"""
    pass
```

### Encryption Strategy

```python
# Field-level encryption for sensitive data
class EncryptedField:
    def __init__(self, field_type, encryption_key_id: str):
        self.field_type = field_type
        self.encryption_key_id = encryption_key_id
    
    def encrypt(self, value: str) -> str:
        """Encrypt sensitive field data"""
        key = self.get_encryption_key(self.encryption_key_id)
        cipher = Fernet(key)
        return cipher.encrypt(value.encode()).decode()
    
    def decrypt(self, encrypted_value: str) -> str:
        """Decrypt sensitive field data"""
        key = self.get_encryption_key(self.encryption_key_id)
        cipher = Fernet(key)
        return cipher.decrypt(encrypted_value.encode()).decode()

# Enhanced customer model with encryption
class CustomerPrivacyModel(Base):
    __tablename__ = "customers"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"))
    
    # Encrypted personal information
    name_encrypted: Mapped[str] = mapped_column(String)  # Encrypted name
    email_encrypted: Mapped[str] = mapped_column(String)  # Encrypted email
    phone_encrypted: Mapped[str] = mapped_column(String)  # Encrypted phone
    address_encrypted: Mapped[str] = mapped_column(JSON)  # Encrypted address JSON
    
    # Non-encrypted business data
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Privacy metadata
    privacy_consent_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    data_retention_until: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    gdpr_consent: Mapped[bool] = mapped_column(Boolean, default=False)
    marketing_consent: Mapped[bool] = mapped_column(Boolean, default=False)
    
    @property
    def name(self) -> str:
        return self.decrypt_field(self.name_encrypted, "customer_name_key")
    
    @name.setter
    def name(self, value: str):
        self.name_encrypted = self.encrypt_field(value, "customer_name_key")
```

### Consent Management System

```python
# Consent management for customer data
class ConsentType(str, Enum):
    SERVICE_DELIVERY = "service_delivery"      # Core service functionality
    MARKETING = "marketing"                    # Marketing communications
    ANALYTICS = "analytics"                    # Usage analytics and insights
    THIRD_PARTY_SHARING = "third_party_sharing"  # Data sharing with partners

class CustomerConsent(Base):
    __tablename__ = "customer_consent"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"))
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"))
    
    consent_type: Mapped[ConsentType] = mapped_column(Enum(ConsentType))
    granted: Mapped[bool] = mapped_column(Boolean)
    granted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    withdrawn_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Consent metadata
    consent_source: Mapped[str] = mapped_column(String)  # "customer_portal", "phone", "paper"
    ip_address: Mapped[Optional[str]] = mapped_column(String)
    user_agent: Mapped[Optional[str]] = mapped_column(String)
    legal_basis: Mapped[str] = mapped_column(String)  # "consent", "legitimate_interest", "contract"

class ConsentManager:
    async def record_consent(
        self, 
        customer_id: int, 
        consent_type: ConsentType, 
        granted: bool,
        source: str,
        ip_address: str = None,
        user_agent: str = None
    ):
        """Record customer consent for data processing"""
        consent = CustomerConsent(
            customer_id=customer_id,
            consent_type=consent_type,
            granted=granted,
            granted_at=datetime.utcnow(),
            consent_source=source,
            ip_address=ip_address,
            user_agent=user_agent,
            legal_basis="consent" if granted else None
        )
        
        session.add(consent)
        await session.commit()
        
        # Trigger appropriate actions based on consent
        if consent_type == ConsentType.MARKETING and not granted:
            await self.remove_from_marketing_lists(customer_id)
    
    async def check_consent(self, customer_id: int, consent_type: ConsentType) -> bool:
        """Check if customer has granted specific consent"""
        latest_consent = session.query(CustomerConsent).filter(
            CustomerConsent.customer_id == customer_id,
            CustomerConsent.consent_type == consent_type
        ).order_by(CustomerConsent.granted_at.desc()).first()
        
        return latest_consent and latest_consent.granted and not latest_consent.withdrawn_at
```

### Data Retention and Deletion

```python
# Automated data retention and deletion system
class DataRetentionPolicy(Base):
    __tablename__ = "data_retention_policies"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"))
    
    data_type: Mapped[str] = mapped_column(String)  # "customer_data", "service_history", "photos"
    retention_period_days: Mapped[int] = mapped_column(Integer)
    auto_delete: Mapped[bool] = mapped_column(Boolean, default=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), onupdate=func.now())

class DataRetentionService:
    async def apply_retention_policies(self):
        """Apply data retention policies across all organizations"""
        policies = session.query(DataRetentionPolicy).filter(
            DataRetentionPolicy.auto_delete == True
        ).all()
        
        for policy in policies:
            cutoff_date = datetime.utcnow() - timedelta(days=policy.retention_period_days)
            
            if policy.data_type == "customer_data":
                await self.archive_customer_data(policy.organization_id, cutoff_date)
            elif policy.data_type == "service_history":
                await self.archive_service_history(policy.organization_id, cutoff_date)
            elif policy.data_type == "photos":
                await self.delete_old_photos(policy.organization_id, cutoff_date)
    
    async def process_deletion_request(self, customer_id: int, request_type: str):
        """Process customer data deletion request (GDPR Right to be Forgotten)"""
        customer = session.query(Customer).get(customer_id)
        
        if request_type == "complete_deletion":
            # Full deletion (where legally allowed)
            await self.delete_customer_completely(customer_id)
        elif request_type == "anonymization":
            # Anonymize data while preserving business records
            await self.anonymize_customer_data(customer_id)
        
        # Log the deletion for compliance audit
        await self.log_deletion_request(customer_id, request_type, "completed")

    async def anonymize_customer_data(self, customer_id: int):
        """Anonymize customer data while preserving service records"""
        customer = session.query(Customer).get(customer_id)
        
        # Replace personal data with anonymized versions
        customer.name_encrypted = self.encrypt_field("ANONYMIZED_USER", "customer_name_key")
        customer.email_encrypted = self.encrypt_field(f"anon_{customer_id}@example.com", "customer_email_key")
        customer.phone_encrypted = self.encrypt_field("000-000-0000", "customer_phone_key")
        
        # Update service records to remove personal details
        service_executions = session.query(ServiceExecution).join(Appointment).filter(
            Appointment.customer_id == customer_id
        ).all()
        
        for execution in service_executions:
            execution.customer_notes = "ANONYMIZED"
            execution.photos = []  # Remove photos containing personal data
        
        await session.commit()
```

### Privacy Impact Assessment

```python
# Privacy Impact Assessment for new features
class PrivacyImpactAssessment:
    def __init__(self, feature_name: str, data_types: List[str]):
        self.feature_name = feature_name
        self.data_types = data_types
        self.assessment_date = datetime.utcnow()
    
    def assess_privacy_risks(self) -> dict:
        """Assess privacy risks for new feature"""
        risks = {
            "data_collection": self.assess_data_collection_risks(),
            "data_processing": self.assess_data_processing_risks(),
            "data_sharing": self.assess_data_sharing_risks(),
            "data_security": self.assess_data_security_risks(),
            "individual_rights": self.assess_individual_rights_impact()
        }
        
        return {
            "feature": self.feature_name,
            "assessment_date": self.assessment_date,
            "overall_risk_level": self.calculate_overall_risk(risks),
            "risks": risks,
            "mitigation_measures": self.recommend_mitigations(risks)
        }
    
    def assess_data_collection_risks(self) -> dict:
        """Assess risks related to data collection"""
        high_risk_data = ["biometric", "location", "financial"]
        collected_high_risk = [dt for dt in self.data_types if dt in high_risk_data]
        
        return {
            "risk_level": "high" if collected_high_risk else "medium",
            "high_risk_data_types": collected_high_risk,
            "lawful_basis_required": True,
            "consent_required": len(collected_high_risk) > 0
        }
```

### Audit and Compliance Reporting

```python
# Comprehensive audit system for compliance
class PrivacyAuditLog(Base):
    __tablename__ = "privacy_audit_log"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"))
    
    event_type: Mapped[str] = mapped_column(String)  # "data_access", "consent_change", "deletion_request"
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    customer_id: Mapped[Optional[int]] = mapped_column(ForeignKey("customers.id"))
    
    event_description: Mapped[str] = mapped_column(Text)
    data_affected: Mapped[dict] = mapped_column(JSON)
    legal_basis: Mapped[Optional[str]] = mapped_column(String)
    
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    ip_address: Mapped[Optional[str]] = mapped_column(String)
    user_agent: Mapped[Optional[str]] = mapped_column(String)

class ComplianceReporter:
    async def generate_gdpr_report(self, organization_id: int, start_date: date, end_date: date) -> dict:
        """Generate GDPR compliance report"""
        return {
            "organization_id": organization_id,
            "reporting_period": {"start": start_date, "end": end_date},
            "data_processing_activities": await self.get_processing_activities(organization_id),
            "consent_statistics": await self.get_consent_statistics(organization_id, start_date, end_date),
            "data_subject_requests": await self.get_data_subject_requests(organization_id, start_date, end_date),
            "data_breaches": await self.get_data_breaches(organization_id, start_date, end_date),
            "privacy_violations": await self.get_privacy_violations(organization_id, start_date, end_date),
            "compliance_score": await self.calculate_compliance_score(organization_id)
        }
    
    async def generate_data_inventory(self, organization_id: int) -> dict:
        """Generate comprehensive data inventory for compliance"""
        return {
            "customer_data": await self.inventory_customer_data(organization_id),
            "service_data": await self.inventory_service_data(organization_id),
            "communication_data": await self.inventory_communication_data(organization_id),
            "technical_data": await self.inventory_technical_data(organization_id),
            "retention_schedules": await self.get_retention_schedules(organization_id),
            "data_flows": await self.map_data_flows(organization_id)
        }
```

### Breach Detection and Response

```python
# Data breach detection and response system
class BreachDetectionService:
    def __init__(self):
        self.anomaly_detectors = [
            UnusualAccessPatternDetector(),
            MassDataExportDetector(),
            UnauthorizedAccessDetector(),
            DataIntegrityBreachDetector()
        ]
    
    async def monitor_for_breaches(self):
        """Continuously monitor for potential data breaches"""
        for detector in self.anomaly_detectors:
            anomalies = await detector.detect_anomalies()
            
            for anomaly in anomalies:
                if anomaly.severity >= BreachSeverity.HIGH:
                    await self.initiate_breach_response(anomaly)
    
    async def initiate_breach_response(self, breach: DataBreach):
        """Initiate automated breach response procedures"""
        # 1. Immediate containment
        await self.contain_breach(breach)
        
        # 2. Assessment and investigation
        assessment = await self.assess_breach_impact(breach)
        
        # 3. Notification obligations
        if assessment.requires_authority_notification:
            await self.notify_data_protection_authority(breach, assessment)
        
        if assessment.requires_individual_notification:
            await self.notify_affected_individuals(breach, assessment)
        
        # 4. Documentation and reporting
        await self.document_breach_response(breach, assessment)

class DataBreach:
    def __init__(self, breach_type: str, affected_data: List[str], severity: BreachSeverity):
        self.id = str(uuid.uuid4())
        self.breach_type = breach_type
        self.affected_data = affected_data
        self.severity = severity
        self.detected_at = datetime.utcnow()
        self.contained_at = None
        self.notification_sent_at = None
```

## Privacy by Design Integration

### Customer Portal Privacy Controls

```python
# Customer portal with privacy controls
@router.get("/api/v1/customer-portal/privacy/data-export")
@require_customer_access()
async def export_customer_data(customer_id: int):
    """Allow customer to export their personal data (GDPR Article 20)"""
    consent_check = await ConsentManager().check_consent(
        customer_id, 
        ConsentType.SERVICE_DELIVERY
    )
    
    if not consent_check:
        raise HTTPException(status_code=403, detail="No consent for data processing")
    
    customer_data = await PrivacyService().export_customer_data(customer_id)
    
    # Log the data export for audit
    await PrivacyAuditLogger().log_event(
        event_type="data_export",
        customer_id=customer_id,
        description="Customer requested data export",
        legal_basis="data_subject_right"
    )
    
    return {"data": customer_data, "exported_at": datetime.utcnow()}

@router.post("/api/v1/customer-portal/privacy/deletion-request")
@require_customer_access()
async def request_data_deletion(customer_id: int, deletion_type: str):
    """Allow customer to request data deletion (GDPR Article 17)"""
    deletion_request = DataDeletionRequest(
        customer_id=customer_id,
        deletion_type=deletion_type,
        requested_at=datetime.utcnow(),
        status="pending"
    )
    
    # Queue for manual review if required
    if deletion_type == "complete_deletion":
        await DeletionReviewQueue().add_request(deletion_request)
    else:
        await DataRetentionService().process_deletion_request(
            customer_id, 
            deletion_type
        )
    
    return {"message": "Deletion request submitted", "request_id": deletion_request.id}
```

### API Privacy Controls

```python
# Privacy-aware API endpoints
@router.get("/api/v1/organizations/{org_id}/customers/{customer_id}/service-history")
@require_service_permission("customer.read")
@privacy_audit("customer_data_access")
async def get_customer_service_history(
    org_id: int, 
    customer_id: int,
    include_photos: bool = False,
    current_user: ServiceJWTPayload = None
):
    """Get customer service history with privacy controls"""
    # Check if user has consent to access customer data
    consent_valid = await ConsentManager().check_consent(
        customer_id,
        ConsentType.SERVICE_DELIVERY
    )
    
    if not consent_valid:
        raise HTTPException(
            status_code=403, 
            detail="Customer has not consented to data processing"
        )
    
    # Apply data minimization - only include photos if specifically requested
    service_history = await ServiceHistoryService().get_history(
        customer_id,
        include_photos=include_photos,
        include_personal_notes=current_user.role in ["service_manager", "admin"]
    )
    
    return service_history
```

## Consequences

### Positive
- **Regulatory Compliance**: Meets GDPR, CCPA, and other privacy regulations
- **Customer Trust**: Transparent privacy practices build customer confidence
- **Data Security**: Comprehensive protection against breaches and unauthorized access
- **Legal Protection**: Reduces legal risk and potential fines
- **Competitive Advantage**: Privacy as a differentiator in the market

### Negative
- **Development Complexity**: Additional complexity in data handling and storage
- **Performance Impact**: Encryption and audit logging may impact performance
- **Storage Overhead**: Encrypted data and audit trails require more storage
- **Operational Overhead**: Privacy management requires ongoing attention and resources

### Risks and Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Data breach | Low | Very High | Multi-layered security, monitoring, incident response |
| Regulatory non-compliance | Medium | High | Regular compliance audits, legal review, automated tools |
| Performance degradation | Medium | Medium | Optimized encryption, selective auditing, caching |
| User experience friction | Medium | Low | Streamlined consent flows, transparent privacy notices |

## Implementation Timeline

### Phase 1: Foundation (2 weeks)
- [ ] Data classification system implementation
- [ ] Basic encryption for sensitive fields
- [ ] Consent management system
- [ ] Privacy audit logging infrastructure

### Phase 2: Compliance Tools (2 weeks)
- [ ] Data retention and deletion automation
- [ ] Customer privacy portal features
- [ ] GDPR compliance reporting
- [ ] Breach detection system

### Phase 3: Advanced Privacy (1 week)
- [ ] Privacy impact assessment tools
- [ ] Advanced anomaly detection
- [ ] Automated compliance monitoring
- [ ] Privacy dashboard for administrators

## Monitoring and Validation

### Privacy Metrics
- **Consent Rates**: Percentage of customers providing various consents
- **Data Access Frequency**: How often personal data is accessed
- **Deletion Requests**: Volume and processing time of deletion requests
- **Breach Detection**: Time to detect and respond to potential breaches
- **Compliance Score**: Automated assessment of privacy compliance

### Regular Assessments
- **Monthly**: Privacy impact assessments for new features
- **Quarterly**: Compliance audit and gap analysis
- **Annually**: Comprehensive privacy program review
- **Ad-hoc**: Breach response exercises and tabletop simulations

## Related ADRs
- ADR-001: Multi-Tenant Service CRM Architecture
- ADR-002: Database Schema Design for Service Management
- ADR-006: Authentication and Authorization for Service Module