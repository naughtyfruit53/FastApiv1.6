# ADR-001: Multi-Tenant Service CRM Architecture

## Status
Proposed

## Context

The TRITIQ ERP system currently supports multi-tenant financial and inventory management. We need to extend this platform to support service-oriented businesses with customer relationship management (CRM) capabilities, appointment scheduling, and technician management while maintaining the existing multi-tenant architecture.

### Current Architecture Strengths
- Well-established multi-tenancy with organization-based data isolation
- Robust user management with role-based access control
- Existing customer and vendor master data management
- Comprehensive voucher system for financial transactions
- Proven scalability with PostgreSQL and FastAPI

### Business Requirements
- Support service companies (HVAC, electrical, plumbing, etc.)
- Enable customer self-service appointment booking
- Manage technician workforce and scheduling
- Track service delivery and customer satisfaction
- Integrate service billing with existing financial system
- Maintain strict data isolation between organizations

## Decision

We will extend the existing multi-tenant architecture to include Service CRM capabilities by:

1. **Architectural Extension Pattern**: Build Service CRM as additional modules within the existing multi-tenant framework rather than a separate system
2. **Data Model Integration**: Extend existing Customer and Organization models rather than creating parallel structures
3. **API Consistency**: Follow established REST patterns and authentication mechanisms
4. **Database Strategy**: Add new tables while leveraging existing infrastructure
5. **UI Integration**: Extend the current Next.js frontend with new service management interfaces

### Key Architectural Decisions

#### 1. Multi-Tenancy Approach
- **Decision**: Extend existing organization-based isolation
- **Rationale**: Maintains consistency, leverages proven patterns, reduces complexity
- **Implementation**: All new service tables include `organization_id` foreign keys

#### 2. Customer Data Strategy
- **Decision**: Enhance existing Customer model rather than create ServiceCustomer
- **Rationale**: Avoids data duplication, maintains referential integrity
- **Implementation**: Add related tables (customer_preferences, customer_contacts, service_history)

#### 3. Service Catalog Design
- **Decision**: Two-tier service hierarchy (Categories → Items)
- **Rationale**: Flexible organization, supports various service business models
- **Implementation**: service_categories and service_items tables with organization scoping

#### 4. Technician Management
- **Decision**: Link technicians to existing User model with specialized profile
- **Rationale**: Leverages existing authentication, role management, and organization association
- **Implementation**: Technician table references User table, inherits organization context

#### 5. Appointment System
- **Decision**: Centralized appointment table linking customers, services, and technicians
- **Rationale**: Single source of truth, supports complex scheduling scenarios
- **Implementation**: Rich appointment model with status tracking and execution linking

## Consequences

### Positive
- **Consistency**: Service CRM feels native to existing ERP system
- **Data Integrity**: Leverages existing referential integrity and constraints
- **Security**: Inherits proven multi-tenant security model
- **Development Speed**: Developers familiar with existing patterns
- **User Experience**: Unified interface across ERP and CRM functions
- **Scalability**: Built on proven PostgreSQL multi-tenant foundation

### Negative
- **Complexity**: Existing tables become more complex with additional relationships
- **Migration Risk**: Changes to core customer model affect existing functionality
- **Database Size**: Additional tables and relationships increase database complexity
- **API Surface**: Larger API surface area to maintain and secure

### Risks and Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Core model changes break existing functionality | High | Low | Comprehensive testing, feature flags, gradual rollout |
| Database performance degradation | Medium | Medium | Proper indexing, query optimization, monitoring |
| UI complexity overwhelms users | Medium | Medium | Progressive disclosure, role-based UI, user testing |
| Security vulnerabilities in new modules | High | Low | Security review, penetration testing, audit trails |

## Implementation Guidelines

### Database Design Principles
1. **Foreign Key Consistency**: All service tables reference organization_id
2. **Soft Deletes**: Use is_active flags rather than hard deletes
3. **Audit Trails**: Include created_at, updated_at, created_by fields
4. **Performance**: Strategic indexes on frequently queried fields
5. **Constraints**: Unique constraints within organization scope

### API Design Principles
1. **Organization Scoping**: All endpoints include organization context
2. **Consistent Patterns**: Follow existing CRUD patterns
3. **Error Handling**: Use established error response formats
4. **Authentication**: Integrate with existing JWT authentication
5. **Rate Limiting**: Apply appropriate limits for customer-facing endpoints

### Security Principles
1. **Least Privilege**: Users see only their organization's service data
2. **Role-Based Access**: Different access levels for service managers, technicians, customers
3. **Data Validation**: Strict input validation for all service-related data
4. **Audit Logging**: Track all service-related operations for compliance

## Alternatives Considered

### 1. Separate Service CRM System
- **Pros**: Clean separation, independent scaling, technology choice freedom
- **Cons**: Data synchronization complexity, user experience fragmentation, increased infrastructure
- **Rejected**: Would create data silos and poor user experience

### 2. Microservices Architecture
- **Pros**: Independent deployment, technology diversity, team autonomy
- **Cons**: Distributed data management, increased operational complexity, transaction management
- **Rejected**: Premature optimization for current scale and team size

### 3. Third-Party Integration
- **Pros**: Proven functionality, faster implementation, reduced development
- **Cons**: Data integration complexity, vendor lock-in, customization limitations
- **Rejected**: Doesn't meet multi-tenant requirements and integration needs

## Review and Updates

This ADR should be reviewed:
- Before Phase 1 implementation begins
- After pilot organization testing
- If significant performance or security issues arise
- Annually as part of architecture review process

## Related ADRs
- ADR-002: Database Schema Design for Service Management
- ADR-003: API Design Patterns for Service Endpoints
- ADR-006: Authentication and Authorization for Service Module