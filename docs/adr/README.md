# Architecture Decision Record (ADR) Index

This directory contains Architecture Decision Records for the TRITIQ ERP system and its Service CRM integration.

## What are ADRs?

Architecture Decision Records (ADRs) are lightweight documents that capture important architectural decisions made during development. They provide context about why decisions were made and help future developers understand the reasoning behind architectural choices.

## ADR Format

Each ADR follows this format:
- **Title**: Brief description of the decision
- **Status**: Proposed, Accepted, Deprecated, or Superseded
- **Context**: Background and problem being solved
- **Decision**: What was decided and why
- **Consequences**: Positive and negative outcomes

## Current ADRs

### Service CRM Integration
- [ADR-001: Multi-Tenant Service CRM Architecture](./ADR-001-multi-tenant-service-crm.md)
- [ADR-002: Database Schema Design for Service Management](./ADR-002-service-database-schema.md)
- [ADR-003: API Design Patterns for Service Endpoints](./ADR-003-service-api-patterns.md)
- [ADR-004: Mobile Workforce Application Strategy](./ADR-004-mobile-workforce-strategy.md)
- [ADR-005: Customer Portal Integration Approach](./ADR-005-customer-portal-integration.md)

### Infrastructure & Security
- [ADR-006: Authentication and Authorization for Service Module](./ADR-006-service-auth-strategy.md)
- [ADR-007: Notification and Communication System](./ADR-007-notification-system.md)
- [ADR-008: Service Data Privacy and Compliance](./ADR-008-service-data-privacy.md)

## Guidelines for New ADRs

1. **Numbering**: Use sequential numbering (ADR-001, ADR-002, etc.)
2. **Naming**: Use descriptive, kebab-case filenames
3. **Status**: Start with "Proposed", move to "Accepted" after approval
4. **Review**: All ADRs should be reviewed by the architecture team
5. **Updates**: If an ADR becomes outdated, mark it as "Superseded" and reference the new ADR

## Review Process

1. Create ADR with "Proposed" status
2. Submit for architecture team review
3. Incorporate feedback and revisions
4. Mark as "Accepted" once approved
5. Reference in implementation PRs