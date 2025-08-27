# ADR-002: Database Schema Design for Service Management

## Status
Proposed

## Context

The Service CRM integration requires extending the existing PostgreSQL database schema to support service-oriented business operations. We need to design new tables and relationships that integrate seamlessly with the existing multi-tenant ERP database while supporting:

- Service catalog management (categories, items, pricing)
- Technician profiles and skill management  
- Appointment scheduling and execution tracking
- Customer service history and preferences
- Mobile workforce data access patterns

### Current Database Architecture
- **Multi-tenant**: All tables include `organization_id` for data isolation
- **Audit Trail**: Consistent `created_at`, `updated_at`, `created_by` patterns
- **Soft Deletes**: Uses `is_active` flags instead of hard deletes
- **Foreign Keys**: Comprehensive referential integrity
- **Indexing**: Strategic indexes for performance optimization

### Performance Requirements
- Support up to 1000 technicians per organization
- Handle 10,000+ appointments per month per organization
- Sub-200ms query response times for scheduling operations
- Efficient mobile app data synchronization

## Decision

We will implement a normalized database schema with the following key design decisions:

### 1. Service Catalog Structure

```sql
-- Two-tier hierarchy for service organization
service_categories (organization_id, name, description, is_active)
service_items (organization_id, category_id, name, description, duration_minutes, base_price)

-- Flexible pricing model supporting multiple tiers
service_pricing (service_id, tier_name, price, effective_from, effective_to)
```

**Rationale**: 
- Two-tier structure balances simplicity with flexibility
- Separate pricing table supports complex pricing strategies
- Organization scoping maintains multi-tenancy

### 2. Technician Management Schema

```sql
-- Technician profiles linked to existing User model
technicians (organization_id, user_id, employee_id, hire_date, status)

-- Skills management for service assignment
technician_skills (technician_id, skill_name, proficiency_level, certified_date)

-- Schedule management for availability tracking
technician_schedules (technician_id, day_of_week, start_time, end_time, is_available)
```

**Rationale**:
- Links to existing User model for authentication and role management
- JSON fields for complex data (certifications, equipment) reduce table proliferation
- Day-of-week schedule pattern supports recurring availability

### 3. Appointment and Service Execution

```sql
-- Central appointment management
appointments (organization_id, customer_id, service_id, technician_id, 
              appointment_date, start_time, end_time, status, address_json)

-- Service delivery tracking
service_executions (appointment_id, technician_id, started_at, completed_at,
                   work_performed, parts_used_json, photos_json)

-- Flexible note system
service_notes (execution_id, note_type, content, visibility, created_by)
```

**Rationale**:
- Single appointment table simplifies scheduling logic
- JSON fields for complex data (address, parts, photos) provide flexibility
- Separate execution tracking enables detailed work management

### 4. Enhanced Customer Data

```sql
-- Customer preferences for service delivery
customer_preferences (customer_id, preferred_technician_id, preferred_time_slots_json,
                     communication_method, special_instructions)

-- Multiple contact management
customer_contacts (customer_id, contact_type, name, phone, email, is_primary)

-- Service history aggregation
customer_service_history (customer_id, service_id, execution_id, service_date,
                         satisfaction_rating, total_amount, payment_status)
```

**Rationale**:
- Extends existing Customer model without modification
- JSON for flexible data structures (time slots, addresses)
- History table enables reporting and customer insights

### 5. Indexing Strategy

```sql
-- Performance-critical indexes
CREATE INDEX idx_appointments_org_date ON appointments(organization_id, appointment_date);
CREATE INDEX idx_appointments_technician_date ON appointments(technician_id, appointment_date);
CREATE INDEX idx_appointments_customer_status ON appointments(customer_id, status);
CREATE INDEX idx_service_executions_status_date ON service_executions(status, started_at);
CREATE INDEX idx_technician_skills_lookup ON technician_skills(technician_id, skill_name);
CREATE INDEX idx_customer_service_history_date ON customer_service_history(customer_id, service_date);

-- JSON field indexes for complex queries
CREATE INDEX idx_appointments_address_city ON appointments USING GIN ((address->'city'));
CREATE INDEX idx_service_pricing_effective ON service_pricing(service_id, effective_from, effective_to);
```

## Implementation Strategy

### Phase 1: Core Tables
1. **Service Catalog**: service_categories, service_items, service_pricing
2. **Technician Management**: technicians, technician_skills, technician_schedules
3. **Basic Appointments**: appointments table with essential fields

### Phase 2: Service Execution
1. **Service Delivery**: service_executions, service_notes
2. **Customer Extensions**: customer_preferences, customer_contacts
3. **History Tracking**: customer_service_history

### Phase 3: Optimization
1. **Performance Indexes**: Implement comprehensive indexing strategy
2. **Partitioning**: Consider table partitioning for high-volume organizations
3. **Archival**: Implement data archival for old service records

## Data Migration Considerations

### Existing Data Integration
- **Customer Enhancement**: Add default preferences for existing customers
- **User to Technician**: Create technician records for users with appropriate roles
- **Service Setup**: Provide templates for common service types

### Migration Scripts
```sql
-- Example: Create default customer preferences
INSERT INTO customer_preferences (customer_id, communication_method, created_at)
SELECT id, 'email', NOW() 
FROM customers 
WHERE organization_id = ?;

-- Example: Convert service users to technicians
INSERT INTO technicians (organization_id, user_id, status, created_at)
SELECT organization_id, id, 'active', NOW()
FROM users 
WHERE role IN ('technician', 'field_service') 
AND organization_id = ?;
```

### Rollback Strategy
- **Foreign Key Constraints**: Can be safely dropped if rollback needed
- **Table Cleanup**: New tables can be dropped without affecting existing data
- **Data Backup**: Full backup before migration with point-in-time recovery

## Performance Considerations

### Query Optimization Patterns

```sql
-- Efficient technician availability query
SELECT t.id, t.user_id, u.full_name
FROM technicians t
JOIN users u ON t.user_id = u.id
JOIN technician_schedules ts ON t.id = ts.technician_id
WHERE t.organization_id = ? 
  AND t.status = 'active'
  AND ts.day_of_week = EXTRACT(dow FROM ?)
  AND ts.is_available = true
  AND NOT EXISTS (
    SELECT 1 FROM appointments a 
    WHERE a.technician_id = t.id 
      AND a.appointment_date = ?
      AND a.status IN ('confirmed', 'in_progress')
  );

-- Service history with pagination
SELECT sh.*, s.name as service_name, c.name as customer_name
FROM customer_service_history sh
JOIN service_items s ON sh.service_id = s.id
JOIN customers c ON sh.customer_id = c.id
WHERE c.organization_id = ?
  AND sh.service_date >= ?
ORDER BY sh.service_date DESC
LIMIT ? OFFSET ?;
```

### Scaling Considerations
- **Partitioning**: Partition appointments by date for large organizations
- **Read Replicas**: Use read replicas for reporting and analytics
- **Caching**: Implement Redis caching for frequently accessed service catalog data
- **Connection Pooling**: Optimize connection pool size for mobile app access patterns

## Security and Compliance

### Data Protection
- **Encryption**: Sensitive customer data encrypted at rest
- **Access Control**: Row-level security for organization isolation
- **Audit Trails**: All service data changes logged with user context
- **Data Retention**: Automated archival of old service records

### Compliance Requirements
```sql
-- Example: Data retention policy implementation
CREATE OR REPLACE FUNCTION archive_old_service_data()
RETURNS void AS $$
BEGIN
  -- Archive service executions older than 7 years
  INSERT INTO service_executions_archive 
  SELECT * FROM service_executions 
  WHERE completed_at < NOW() - INTERVAL '7 years';
  
  DELETE FROM service_executions 
  WHERE completed_at < NOW() - INTERVAL '7 years';
END;
$$ LANGUAGE plpgsql;
```

## Monitoring and Maintenance

### Database Health Metrics
- **Table Growth**: Monitor appointment and execution table growth rates
- **Query Performance**: Track slow queries and optimize indexes
- **Disk Usage**: Monitor storage growth and plan capacity
- **Connection Usage**: Track connection pool utilization

### Maintenance Procedures
- **Index Maintenance**: Weekly REINDEX on heavily updated tables
- **Statistics Update**: Daily ANALYZE on appointment and execution tables
- **Backup Verification**: Daily backup validation and restore testing
- **Archive Cleanup**: Monthly archival of old service data

## Consequences

### Positive
- **Performance**: Optimized schema for service business query patterns
- **Scalability**: Designed to handle growth in appointments and service history
- **Flexibility**: JSON fields accommodate varying business requirements
- **Integration**: Seamless integration with existing ERP data structures
- **Compliance**: Built-in support for data retention and audit requirements

### Negative
- **Complexity**: Additional tables increase overall database complexity
- **Storage**: JSON fields may use more storage than normalized alternatives
- **Migration Risk**: Schema changes require careful testing and rollback planning
- **Query Complexity**: Some queries become more complex with additional joins

### Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Poor query performance | Comprehensive indexing strategy, query optimization |
| Data integrity issues | Foreign key constraints, validation triggers |
| Storage growth | Data archival policies, partitioning strategy |
| Migration failures | Comprehensive testing, rollback procedures |

## Alternatives Considered

### 1. Document Database (MongoDB)
- **Pros**: Flexible schema, JSON-native, horizontal scaling
- **Cons**: Loss of ACID guarantees, query complexity, team expertise
- **Rejected**: Inconsistent with existing PostgreSQL infrastructure

### 2. Denormalized Design
- **Pros**: Simpler queries, better read performance
- **Cons**: Data duplication, update complexity, storage overhead
- **Rejected**: Conflicts with existing normalized ERP schema patterns

### 3. Separate Service Database
- **Pros**: Independent scaling, technology choice freedom
- **Cons**: Cross-database queries, data synchronization complexity
- **Rejected**: Breaks multi-tenant data isolation model

## Review and Validation

### Before Implementation
- [ ] DBA team review for performance implications
- [ ] Security team review for compliance requirements
- [ ] Development team review for implementation complexity
- [ ] Business stakeholder validation of data model

### During Implementation
- [ ] Performance testing with realistic data volumes
- [ ] Migration testing on copy of production data
- [ ] Security penetration testing
- [ ] Load testing for mobile app access patterns

### Post-Implementation
- [ ] Monitor database performance metrics
- [ ] Validate data integrity and audit trails
- [ ] Review and optimize slow queries
- [ ] Plan for future scaling requirements

## Related ADRs
- ADR-001: Multi-Tenant Service CRM Architecture
- ADR-003: API Design Patterns for Service Endpoints
- ADR-008: Service Data Privacy and Compliance