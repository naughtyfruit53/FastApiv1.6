# Comprehensive RBAC System Extension Documentation

## Overview

This document describes the comprehensive Role-Based Access Control (RBAC) system extension implemented across all modules in the FastAPI v1.6 application.

## Architecture

### 1. Module Hierarchy

The system defines a hierarchical structure of modules and submodules:

```
Module (e.g., CRM, ERP, Manufacturing)
  └── Submodules (e.g., leads, opportunities, contacts)
      └── Permissions (e.g., create, read, update, delete)
```

### 2. Role Hierarchy

The system implements the following role hierarchy:

1. **Super Admin / Platform Admin**
   - Full system access across all organizations
   - Can create organizations and licenses

2. **Org Admin / Management**
   - Full access to all modules enabled for their organization
   - Can create managers and executives
   - No module restrictions

3. **Manager**
   - Access to assigned modules only
   - Can create and manage executives
   - Full access to assigned modules (all submodules and permissions)
   - Must have at least one module assigned

4. **Executive**
   - Access inherited from reporting manager
   - Restricted to specific submodules within manager's modules
   - Granular permissions per submodule (e.g., read-only on leads, create/read/update on opportunities)
   - Must report to a manager

## Modules and Submodules

### Core Business Modules

#### CRM (Customer Relationship Management)
- leads
- opportunities
- contacts
- accounts
- activities
- campaigns
- commission
- analytics
- settings
- import_export

#### ERP (Enterprise Resource Planning)
- general_ledger
- accounts_payable
- accounts_receivable
- journal_entries
- bank_reconciliation
- cost_centers
- chart_of_accounts
- gst_configuration
- tax_codes
- financial_statements
- kpis

#### HR (Human Resources)
- employees
- attendance
- leave_management
- performance
- recruitment
- training
- documents
- org_structure

#### Inventory
- products
- stock
- warehouses
- stock_transfers
- stock_adjustments
- stock_reports
- categories
- units
- brands

#### Service
- service_requests
- technicians
- appointments
- work_orders
- service_reports
- customer_feedback
- service_closure
- sla_management
- service_analytics

#### Analytics
- dashboards
- reports
- custom_reports
- data_visualization
- kpi_tracking
- forecasting
- export

#### Finance
- vouchers
- purchase_vouchers
- sales_vouchers
- payment_vouchers
- receipt_vouchers
- journal_vouchers
- contra_vouchers
- financial_modeling
- budgeting

### Extended Modules

#### Manufacturing
- production_planning
- work_orders
- bom (Bill of Materials)
- quality_control
- job_work
- material_requisition
- production_reports
- capacity_planning
- shop_floor

#### Procurement
- purchase_orders
- purchase_requisitions
- rfq (Request for Quotation)
- vendor_quotations
- vendor_evaluation
- grn (Goods Receipt Note)
- purchase_returns
- vendor_management

#### Project
- projects
- tasks
- milestones
- time_tracking
- resource_allocation
- project_reports
- gantt_charts
- collaboration

#### Asset
- asset_register
- asset_tracking
- depreciation
- maintenance
- allocation
- disposal
- asset_reports

#### Transport
- vehicles
- drivers
- routes
- trips
- fuel_management
- maintenance
- gps_tracking
- transport_reports

#### SEO
- keywords
- content_optimization
- backlinks
- site_audit
- rank_tracking
- competitor_analysis
- seo_reports

#### Marketing
- campaigns
- email_marketing
- social_media
- content_marketing
- marketing_automation
- lead_generation
- analytics
- roi_tracking

#### Payroll
- salary_structure
- payslips
- deductions
- bonuses
- tax_calculation
- statutory_compliance
- payroll_reports
- bank_transfer

#### Talent
- recruitment
- candidate_tracking
- interviews
- offer_management
- onboarding
- talent_pool
- recruitment_analytics

### Advanced Modules

#### Workflow
- workflow_templates
- approval_requests
- workflow_instances
- automation_rules
- workflow_analytics

#### Integration
- api_keys
- webhooks
- external_integrations
- data_sync
- tally_sync
- oauth_clients
- integration_logs

#### AI_Analytics
- ml_models
- predictions
- anomaly_detection
- recommendations
- automl
- model_explainability
- ai_reports

#### Streaming_Analytics
- real_time_dashboards
- event_streaming
- alerts
- monitoring
- streaming_reports

#### AB_Testing
- experiments
- variants
- metrics
- results_analysis
- ab_reports

#### Website_Agent
- chatbot_config
- conversations
- knowledge_base
- analytics
- customization

#### Email
- inbox
- compose
- templates
- accounts
- sync
- filters
- email_analytics

#### Calendar
- events
- meetings
- reminders
- calendar_sharing
- event_types

#### Task_Management
- tasks
- projects
- boards
- sprints
- time_logs
- task_reports

#### Order_Book
- sales_orders
- purchase_orders
- order_tracking
- fulfillment
- order_analytics

#### Exhibition
- exhibitions
- booths
- attendees
- leads
- exhibition_analytics

## Permissions

### Permission Structure

Each permission is defined as a tuple:
```python
(
    permission_name,    # e.g., "crm_leads_create"
    display_name,       # e.g., "Create Leads"
    description,        # e.g., "Create new leads in CRM"
    module,            # e.g., "crm_leads"
    action             # e.g., "create"
)
```

### Permission Actions

- **Basic CRUD**: create, read, update, delete
- **Advanced**: approve, reject, submit, review, publish, archive
- **Data Operations**: export, import, sync, backup, restore
- **Special**: admin, manage, view_all, edit_all
- **Communication**: send, compose, reply, forward
- **Conversion**: convert, transform
- **Closure**: close, finalize, reopen
- **Assignment**: assign, reassign

### Role-Based Permissions

1. **Admin**: All permissions (200+ permissions)
2. **Manager**: Most permissions except delete and admin (excluding CRM/Service which get full access)
3. **Support**: Read, create, update permissions (no delete, no admin)
4. **Viewer**: Read/view-only permissions

## User Creation Workflows

### Creating an Org Admin / Management User

```python
# During license creation or user creation
# Automatically grants full access to all organization modules

user_rbac_service.setup_user_rbac_by_role(
    user_id=user_id,
    role="org_admin"  # or "management"
)

# Result:
# - assigned_modules: All organization enabled modules
# - sub_module_permissions: None (full access)
# - reporting_manager_id: None
```

### Creating a Manager

```python
# Manager must have assigned modules
assigned_modules = {
    "CRM": True,
    "Manufacturing": True,
    "Procurement": True
}

user_rbac_service.setup_user_rbac_by_role(
    user_id=user_id,
    role="manager",
    assigned_modules=assigned_modules
)

# Result:
# - assigned_modules: Only specified modules
# - sub_module_permissions: None (full access to assigned modules)
# - reporting_manager_id: None
```

### Creating an Executive

```python
# Executive inherits from manager and has granular permissions
submodule_permissions = {
    "CRM": {
        "leads": ["read", "create", "update"],
        "opportunities": ["read"]
    },
    "Manufacturing": {
        "production_planning": ["read"],
        "quality_control": ["read", "update"]
    }
}

user_rbac_service.setup_user_rbac_by_role(
    user_id=user_id,
    role="executive",
    reporting_manager_id=manager_id,
    submodule_permissions=submodule_permissions
)

# Result:
# - assigned_modules: Inherited from manager
# - sub_module_permissions: As specified above
# - reporting_manager_id: manager_id
```

## API Endpoints

### Module Management

```
GET    /api/v1/organizations/{org_id}/modules
PUT    /api/v1/organizations/{org_id}/modules
```

### User Management with RBAC

```
POST   /api/v1/organizations/{org_id}/users
PUT    /api/v1/organizations/{org_id}/users/{user_id}
```

### RBAC Services

```python
from app.services.user_rbac_service import UserRBACService

# Initialize service
rbac_service = UserRBACService(db)

# Assign modules to user
await rbac_service.assign_modules_to_user(user_id, modules_dict)

# Assign submodule permissions to executive
await rbac_service.assign_submodule_permissions_to_executive(
    user_id, 
    submodule_permissions
)

# Setup user RBAC by role
await rbac_service.setup_user_rbac_by_role(
    user_id, 
    role,
    reporting_manager_id=None,
    assigned_modules=None,
    submodule_permissions=None
)

# Get user effective permissions
permissions = await rbac_service.get_user_effective_permissions(user_id)
```

## Database Schema

### Organization Model

```python
class Organization:
    enabled_modules: JSON = {
        "CRM": True,
        "ERP": True,
        # ... all 30+ modules
    }
```

### User Model

```python
class User:
    role: str  # org_admin, management, manager, executive
    
    # Module assignments (subset of org enabled_modules)
    assigned_modules: JSON = {
        "CRM": True,
        "Manufacturing": True,
        # ...
    }
    
    # Submodule permissions for executives
    # Format: {module: {submodule: [actions]}}
    sub_module_permissions: JSON = {
        "CRM": {
            "leads": ["read", "create", "update"],
            "opportunities": ["read"]
        }
    }
    
    # Reporting relationship
    reporting_manager_id: int
```

## Permission Checks

### Checking User Permissions

```python
from app.services.rbac import RBACService

rbac_service = RBACService(db)

# Check if user has a specific permission
has_permission = await rbac_service.user_has_permission(
    user_id, 
    "crm_leads_create"
)

# Get all user permissions
permissions = await rbac_service.get_user_permissions(user_id)
```

### Module/Submodule Access

```python
from app.services.user_rbac_service import UserRBACService

rbac_service = UserRBACService(db)

# Get effective permissions (includes modules, submodules, actions)
effective_perms = await rbac_service.get_user_effective_permissions(user_id)

# Returns:
# {
#     "user_id": 123,
#     "role": "executive",
#     "assigned_modules": {"CRM": True, ...},
#     "sub_module_permissions": {"CRM": {"leads": ["read", "create"]}},
#     "has_full_access": False,
#     "reporting_manager_id": 456,
#     "rbac_permissions": ["crm_leads_read", "crm_leads_create", ...]
# }
```

## Migration Path

### For Existing Organizations

1. Existing organizations will automatically have all modules enabled by default
2. Existing users retain their current access
3. User roles determine access:
   - Org admins: Full access to all modules
   - Managers: Need assigned_modules to be set
   - Executives: Need reporting_manager_id and sub_module_permissions

### Backward Compatibility

- All legacy module names maintained
- All legacy permissions maintained
- Existing API endpoints continue to work
- JSON fields are additive (no breaking changes)

## Best Practices

### Module Assignment

1. **Org Admin/Management**: Automatically gets all enabled modules
2. **Manager**: Explicitly assign only required modules
3. **Executive**: Inherit from manager, restrict to specific submodules

### Permission Design

1. Use granular submodule permissions for executives
2. Grant module-level access for managers
3. Review and adjust permissions based on business needs

### Security Considerations

1. Always validate module assignments against organization enabled_modules
2. Validate submodule permissions against manager's assigned_modules
3. Use role hierarchy to enforce access control
4. Regular permission audits recommended

## Testing

### Unit Tests

```bash
python -m pytest tests/test_comprehensive_rbac.py -v
```

### Manual Testing

1. Create organization with license
2. Verify org_admin has full access
3. Create manager with specific modules
4. Create executive under manager
5. Verify permission inheritance
6. Test module/submodule access

## Troubleshooting

### Common Issues

1. **Manager created without assigned_modules**
   - Error: "Managers must have at least one module assigned"
   - Solution: Specify assigned_modules during creation

2. **Executive created without reporting_manager_id**
   - Error: "Executives must have a reporting manager"
   - Solution: Specify reporting_manager_id during creation

3. **Invalid module in enabled_modules**
   - Error: "Invalid module: XYZ"
   - Solution: Use modules from get_all_modules()

4. **Submodule not in manager's modules**
   - Error: "Cannot assign sub-modules for X - manager doesn't have access"
   - Solution: Ensure manager has the parent module assigned

## Future Enhancements

1. Dynamic permission creation
2. Custom role definitions
3. Permission templates
4. Role cloning
5. Permission delegation
6. Time-based access control
7. IP-based access restrictions
8. Audit logging for permission changes

## References

- Module Registry: `app/core/modules_registry.py`
- RBAC Permissions: `app/services/rbac_permissions.py`
- User RBAC Service: `app/services/user_rbac_service.py`
- RBAC Service: `app/services/rbac.py`
- Tests: `tests/test_comprehensive_rbac.py`
