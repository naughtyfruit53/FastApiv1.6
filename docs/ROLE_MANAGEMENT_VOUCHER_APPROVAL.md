# Organization Role Management and Voucher Approval Workflow

## Overview

This document describes the new organization role management system and voucher approval workflow implemented in Phase 1. This system replaces the previous simple role-based access control with a hierarchical, module-based permission system and configurable approval workflows.

## Role Hierarchy

### New Role Structure

The system introduces three primary role levels within organizations:

1. **Management** (Level 1)
   - Highest authority level
   - Full access to all enabled modules
   - Can approve Level 2 voucher approvals
   - Can create and manage other roles
   - Can configure approval workflows

2. **Manager** (Level 2) 
   - Middle management level
   - Full access to assigned modules
   - Can approve Level 1 voucher approvals from Executives
   - Reports to Management for Level 2 approvals

3. **Executive** (Level 3)
   - Operational level
   - Limited access to assigned modules
   - Must get approvals for vouchers based on organization settings
   - Reports to assigned Managers per module

### Legacy Role Migration

- **Org Super Admin**: Retained with ability to create additional Org Super Admins
- **Org Admin**: To be migrated to Management role (Phase 4)
- **Standard User**: To be migrated to Executive role (Phase 4)

## Module-Based Permissions

### Available Modules

- CRM (Customer Relationship Management)
- ERP (Enterprise Resource Planning) 
- HR (Human Resources)
- Inventory (Inventory Management)
- Service (Service Management)
- Analytics (Analytics and Reporting)
- Finance (Financial Management)
- Mail (Email Management)

### Access Levels

Each role can be assigned different access levels per module:

- **Full**: Complete CRUD operations and administrative functions
- **Limited**: Read and update operations, no deletion or admin functions
- **View Only**: Read-only access to module data

### Permission Assignment

Permissions are assigned at the role level and inherited by users. A user's effective permissions are the highest level across all their assigned roles.

## Voucher Approval Workflow

### Approval Models

Organizations can configure one of three approval models:

#### 1. No Approval
- Vouchers are processed directly by the user
- Suitable for high-trust environments or low-risk operations
- Optional auto-approval threshold can be set

#### 2. Level 1 Approval (Maker-Checker)
- Executive submits voucher → Manager approves → Processed
- Single approval layer for moderate oversight
- Manager approval is final

#### 3. Level 2 Approval (Maker-Checker-Approver)
- Executive submits voucher → Manager approves → Management approves → Processed
- Dual approval layer for high-security environments
- Management approval is final

### Approval Flow

```
[Executive] → [Manager] → [Management] → [Processed]
    |            |            |
    |            |            └─ Level 2 Approval
    |            └─ Level 1 Approval  
    └─ Voucher Submission
```

### Auto-Approval Features

- **Threshold-based**: Vouchers below configured amount can be auto-approved
- **Escalation timeout**: Automatic escalation after configured hours
- **Emergency override**: Super admins can override any approval state

## Database Schema

### Core Tables

#### organization_roles
- Defines role hierarchy within organizations
- Links to organization and creator
- Stores hierarchy level and metadata

#### role_module_assignments  
- Maps roles to specific modules with access levels
- Stores granular permissions per module
- Tracks assignment history

#### user_organization_roles
- Assigns users to organization roles
- Supports manager assignments per module
- Tracks assignment metadata

#### organization_approval_settings
- Stores approval workflow configuration per organization
- Defines approval model and settings
- Configures Level 2 approvers and thresholds

#### voucher_approvals
- Tracks individual voucher approval records
- Stores approval history and comments
- Links to approval settings and voucher data

### Relationships

```sql
Organization 1:M OrganizationRole
Organization 1:1 OrganizationApprovalSettings
Organization 1:M VoucherApproval

OrganizationRole 1:M RoleModuleAssignment
OrganizationRole 1:M UserOrganizationRole

User 1:M UserOrganizationRole
User 1:M VoucherApproval (as submitter/approver)

OrganizationApprovalSettings 1:M VoucherApproval
```

## API Services

### RoleManagementService

Provides business logic for role and permission management:

- **Role Management**: Create, update, deactivate roles
- **Module Assignment**: Assign modules to roles with access levels  
- **User Assignment**: Assign users to roles with manager mappings
- **Permission Checking**: Check user access to specific modules

Key Methods:
- `create_organization_role()`
- `assign_module_to_role()`
- `assign_user_to_role()`
- `user_has_module_access()`
- `get_user_module_permissions()`

### VoucherApprovalService  

Provides business logic for voucher approval workflow:

- **Settings Management**: Configure approval models and thresholds
- **Approval Processing**: Submit, approve, reject vouchers
- **Workflow Routing**: Route approvals based on organization settings
- **Status Tracking**: Track approval history and current state

Key Methods:
- `submit_voucher_for_approval()`
- `approve_voucher_level_1()`
- `approve_voucher_level_2()`
- `reject_voucher()`
- `get_pending_approvals_for_user()`

## Implementation Status

### Phase 1 (Current) ✅
- Database models and schemas
- Core business logic services
- Migration scripts
- Basic tests

### Phase 2 (Next)
- REST API endpoints
- Authentication and authorization
- Role management APIs
- Voucher approval APIs

### Phase 3 (Follow-up)
- Frontend components
- Settings interface
- Role management UI
- Approval workflow screens

### Phase 4 (Final)
- Data migration from legacy roles
- Comprehensive testing
- Performance optimization
- Documentation completion

## Configuration Examples

### Default Role Setup

```python
# Initialize default roles for organization
roles = initialize_default_roles(db, organization_id)

# Assign modules to Management role (full access to all)
assign_default_modules_to_role(
    db, management_role.id, organization_id,
    ["CRM", "ERP", "HR", "Finance"], "full"
)

# Assign modules to Manager role (selected modules)
assign_default_modules_to_role(
    db, manager_role.id, organization_id, 
    ["CRM", "ERP"], "full"
)

# Assign modules to Executive role (limited access)
assign_default_modules_to_role(
    db, executive_role.id, organization_id,
    ["CRM"], "limited"
)
```

### Approval Settings Configuration

```python
# Configure Level 2 approval workflow
approval_service.update_approval_settings(
    organization_id=1,
    approval_model=ApprovalModel.LEVEL_2,
    level_2_approvers={"user_ids": [admin_user_id]},
    auto_approve_threshold=1000.0,
    escalation_timeout_hours=48
)
```

### User Role Assignment

```python
# Assign user to Executive role with manager assignment
role_service.assign_user_to_role(
    UserOrganizationRoleCreate(
        organization_id=1,
        user_id=user_id,
        role_id=executive_role_id,
        manager_assignments={"CRM": manager_user_id}
    )
)
```

## Security Considerations

### Access Control
- All operations are scoped to organization boundaries
- Role assignments require appropriate permissions
- Module access is enforced at the service layer

### Audit Trail
- All role changes are tracked with user and timestamp
- Approval history is maintained for vouchers
- Database constraints prevent unauthorized modifications

### Data Integrity
- Foreign key constraints ensure referential integrity
- Unique constraints prevent duplicate assignments
- Soft deletes preserve historical data

## Migration Path

### From Legacy System
1. **Phase 4**: Map existing roles to new hierarchy
   - `org_admin` → `management` role
   - `standard_user` → `executive` role
   - Preserve existing module assignments

2. **Gradual Transition**: Support both systems during migration
   - New features use new role system
   - Legacy features continue with old roles
   - Progressive migration of functionality

3. **Data Cleanup**: Remove legacy role fields after migration
   - Archive old role data
   - Update all references to new system
   - Clean up unused tables/columns

## Best Practices

### Role Design
- Keep role hierarchy simple (3 levels maximum)
- Assign minimal required permissions
- Use descriptive role names and descriptions
- Regular review and cleanup of role assignments

### Approval Workflow
- Match approval levels to risk tolerance
- Set appropriate auto-approval thresholds
- Configure reasonable escalation timeouts
- Train users on approval processes

### Module Permissions
- Start with restrictive permissions
- Grant additional access as needed
- Regular audit of module assignments
- Document permission rationale

## Troubleshooting

### Common Issues
1. **Permission Denied**: Check user role assignments and module access
2. **Approval Stuck**: Verify approver availability and workflow settings
3. **Module Not Accessible**: Confirm organization has module enabled
4. **Role Assignment Failed**: Check organization boundaries and constraints

### Diagnostic Queries
```sql
-- Check user's effective permissions
SELECT ur.*, r.name, r.hierarchy_level, ma.module_name, ma.access_level
FROM user_organization_roles ur
JOIN organization_roles r ON ur.role_id = r.id  
JOIN role_module_assignments ma ON r.id = ma.role_id
WHERE ur.user_id = ? AND ur.is_active = true;

-- Check pending approvals for user
SELECT va.*, v.voucher_number, v.voucher_amount
FROM voucher_approvals va
WHERE va.current_approver_id = ? 
AND va.status IN ('pending', 'level_1_approved');
```

## Future Enhancements

### Planned Features
- **Temporal Permissions**: Time-limited role assignments
- **Conditional Approval**: Rules-based approval routing
- **Bulk Operations**: Mass role assignments and approvals
- **Advanced Analytics**: Permission usage and approval metrics
- **Mobile Support**: Mobile-optimized approval workflows

### Integration Points
- **External Systems**: API for third-party integrations
- **SSO Integration**: Single sign-on with role mapping
- **Audit Systems**: Integration with compliance tools
- **Notification Systems**: Real-time approval notifications