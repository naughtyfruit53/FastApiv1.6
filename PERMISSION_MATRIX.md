# Permission Matrix - FastAPI v1.6

**Version**: 1.6  
**Last Updated**: October 29, 2025  
**Status**: Production Ready

---

## Overview

This document provides a comprehensive matrix of all permissions in the FastAPI v1.6 RBAC system, organized by module and role.

---

## Permission Format

Permissions follow the pattern: `{module}:{action}`

**Standard Actions**:
- `read` - View/list records
- `create` - Create new records
- `update` - Modify existing records
- `delete` - Remove records
- `export` - Export data (Excel, PDF, etc.)
- `import` - Import data

**Special Actions**:
- `manage` - Full management (create, read, update, delete)
- `approve` - Approve workflow items
- `configure` - Configure module settings

---

## Default Role Permissions

### Legend

- ✅ = Permission granted
- ❌ = Permission denied
- 🔒 = Super Admin only
- 🔄 = Configurable (can be granted/revoked)

---

## Core System Permissions

### User Management

| Permission | Super Admin | Admin | Manager | User |
|------------|-------------|-------|---------|------|
| `user:read` | ✅ | ✅ | 🔄 | ❌ |
| `user:create` | ✅ | ✅ | ❌ | ❌ |
| `user:update` | ✅ | ✅ | 🔄 | ❌ |
| `user:delete` | ✅ | ✅ | ❌ | ❌ |
| `user:manage_permissions` | ✅ | ✅ | ❌ | ❌ |
| `user:impersonate` | 🔒 | ❌ | ❌ | ❌ |

### Organization Management

| Permission | Super Admin | Admin | Manager | User |
|------------|-------------|-------|---------|------|
| `organization:read` | ✅ | ✅ | ✅ | ✅ |
| `organization:create` | 🔒 | ❌ | ❌ | ❌ |
| `organization:update` | ✅ | ✅ | ❌ | ❌ |
| `organization:delete` | 🔒 | ❌ | ❌ | ❌ |
| `organization:configure` | ✅ | ✅ | ❌ | ❌ |
| `organization:cross_access` | 🔒 | ❌ | ❌ | ❌ |

### Settings

| Permission | Super Admin | Admin | Manager | User |
|------------|-------------|-------|---------|------|
| `settings:read` | ✅ | ✅ | ✅ | ❌ |
| `settings:update` | ✅ | ✅ | ❌ | ❌ |
| `settings:manage_modules` | ✅ | ✅ | ❌ | ❌ |
| `settings:manage_integrations` | ✅ | ✅ | ❌ | ❌ |

---

## Business Module Permissions

### Manufacturing Module

| Permission | Super Admin | Admin | Manager | User |
|------------|-------------|-------|---------|------|
| `manufacturing:read` | ✅ | ✅ | ✅ | ✅ |
| `manufacturing:create` | ✅ | ✅ | ✅ | 🔄 |
| `manufacturing:update` | ✅ | ✅ | ✅ | 🔄 |
| `manufacturing:delete` | ✅ | ✅ | 🔄 | ❌ |
| `bom:read` | ✅ | ✅ | ✅ | ✅ |
| `bom:create` | ✅ | ✅ | ✅ | 🔄 |
| `bom:update` | ✅ | ✅ | ✅ | 🔄 |
| `bom:delete` | ✅ | ✅ | 🔄 | ❌ |
| `production_order:read` | ✅ | ✅ | ✅ | ✅ |
| `production_order:create` | ✅ | ✅ | ✅ | 🔄 |
| `production_order:update` | ✅ | ✅ | ✅ | 🔄 |
| `production_order:delete` | ✅ | ✅ | 🔄 | ❌ |
| `quality_control:read` | ✅ | ✅ | ✅ | ✅ |
| `quality_control:create` | ✅ | ✅ | ✅ | 🔄 |
| `quality_control:update` | ✅ | ✅ | ✅ | 🔄 |
| `quality_control:approve` | ✅ | ✅ | ✅ | ❌ |

### CRM Module

| Permission | Super Admin | Admin | Manager | User |
|------------|-------------|-------|---------|------|
| `crm:read` | ✅ | ✅ | ✅ | ✅ |
| `crm:create` | ✅ | ✅ | ✅ | ✅ |
| `crm:update` | ✅ | ✅ | ✅ | 🔄 |
| `crm:delete` | ✅ | ✅ | 🔄 | ❌ |
| `lead:read` | ✅ | ✅ | ✅ | ✅ |
| `lead:create` | ✅ | ✅ | ✅ | ✅ |
| `lead:update` | ✅ | ✅ | ✅ | ✅ |
| `lead:delete` | ✅ | ✅ | 🔄 | ❌ |
| `lead:convert` | ✅ | ✅ | ✅ | 🔄 |
| `opportunity:read` | ✅ | ✅ | ✅ | ✅ |
| `opportunity:create` | ✅ | ✅ | ✅ | ✅ |
| `opportunity:update` | ✅ | ✅ | ✅ | 🔄 |
| `opportunity:delete` | ✅ | ✅ | 🔄 | ❌ |
| `contact:read` | ✅ | ✅ | ✅ | ✅ |
| `contact:create` | ✅ | ✅ | ✅ | ✅ |
| `contact:update` | ✅ | ✅ | ✅ | 🔄 |
| `contact:delete` | ✅ | ✅ | 🔄 | ❌ |

### Finance Module

| Permission | Super Admin | Admin | Manager | User |
|------------|-------------|-------|---------|------|
| `finance:read` | ✅ | ✅ | ✅ | 🔄 |
| `finance:create` | ✅ | ✅ | ✅ | 🔄 |
| `finance:update` | ✅ | ✅ | ✅ | 🔄 |
| `finance:delete` | ✅ | ✅ | 🔄 | ❌ |
| `chart_of_accounts:read` | ✅ | ✅ | ✅ | ✅ |
| `chart_of_accounts:create` | ✅ | ✅ | ✅ | ❌ |
| `chart_of_accounts:update` | ✅ | ✅ | ✅ | ❌ |
| `chart_of_accounts:delete` | ✅ | ✅ | ❌ | ❌ |
| `voucher:read` | ✅ | ✅ | ✅ | 🔄 |
| `voucher:create` | ✅ | ✅ | ✅ | 🔄 |
| `voucher:update` | ✅ | ✅ | ✅ | 🔄 |
| `voucher:delete` | ✅ | ✅ | 🔄 | ❌ |
| `voucher:approve` | ✅ | ✅ | ✅ | ❌ |
| `invoice:read` | ✅ | ✅ | ✅ | ✅ |
| `invoice:create` | ✅ | ✅ | ✅ | ✅ |
| `invoice:update` | ✅ | ✅ | ✅ | 🔄 |
| `invoice:delete` | ✅ | ✅ | 🔄 | ❌ |

### Inventory Module

| Permission | Super Admin | Admin | Manager | User |
|------------|-------------|-------|---------|------|
| `inventory:read` | ✅ | ✅ | ✅ | ✅ |
| `inventory:create` | ✅ | ✅ | ✅ | 🔄 |
| `inventory:update` | ✅ | ✅ | ✅ | 🔄 |
| `inventory:delete` | ✅ | ✅ | 🔄 | ❌ |
| `product:read` | ✅ | ✅ | ✅ | ✅ |
| `product:create` | ✅ | ✅ | ✅ | 🔄 |
| `product:update` | ✅ | ✅ | ✅ | 🔄 |
| `product:delete` | ✅ | ✅ | 🔄 | ❌ |
| `stock:read` | ✅ | ✅ | ✅ | ✅ |
| `stock:create` | ✅ | ✅ | ✅ | 🔄 |
| `stock:update` | ✅ | ✅ | ✅ | 🔄 |
| `stock:adjust` | ✅ | ✅ | ✅ | ❌ |
| `warehouse:read` | ✅ | ✅ | ✅ | ✅ |
| `warehouse:create` | ✅ | ✅ | ✅ | ❌ |
| `warehouse:update` | ✅ | ✅ | ✅ | ❌ |
| `warehouse:delete` | ✅ | ✅ | ❌ | ❌ |

### HR Module

| Permission | Super Admin | Admin | Manager | User |
|------------|-------------|-------|---------|------|
| `hr:read` | ✅ | ✅ | ✅ | 🔄 |
| `hr:create` | ✅ | ✅ | ✅ | ❌ |
| `hr:update` | ✅ | ✅ | ✅ | ❌ |
| `hr:delete` | ✅ | ✅ | ❌ | ❌ |
| `employee:read` | ✅ | ✅ | ✅ | 🔄 |
| `employee:create` | ✅ | ✅ | ✅ | ❌ |
| `employee:update` | ✅ | ✅ | ✅ | ❌ |
| `employee:delete` | ✅ | ✅ | ❌ | ❌ |
| `attendance:read` | ✅ | ✅ | ✅ | ✅ |
| `attendance:create` | ✅ | ✅ | ✅ | ✅ |
| `attendance:update` | ✅ | ✅ | ✅ | 🔄 |
| `attendance:approve` | ✅ | ✅ | ✅ | ❌ |
| `payroll:read` | ✅ | ✅ | ✅ | 🔄 |
| `payroll:create` | ✅ | ✅ | ✅ | ❌ |
| `payroll:update` | ✅ | ✅ | ✅ | ❌ |
| `payroll:approve` | ✅ | ✅ | ❌ | ❌ |

---

## Advanced Modules

### Analytics & Reporting

| Permission | Super Admin | Admin | Manager | User |
|------------|-------------|-------|---------|------|
| `analytics:read` | ✅ | ✅ | ✅ | 🔄 |
| `analytics:create` | ✅ | ✅ | ✅ | 🔄 |
| `analytics:export` | ✅ | ✅ | ✅ | 🔄 |
| `reports:read` | ✅ | ✅ | ✅ | ✅ |
| `reports:create` | ✅ | ✅ | ✅ | 🔄 |
| `reports:export` | ✅ | ✅ | ✅ | 🔄 |
| `dashboard:read` | ✅ | ✅ | ✅ | ✅ |
| `dashboard:create` | ✅ | ✅ | ✅ | 🔄 |
| `dashboard:configure` | ✅ | ✅ | 🔄 | ❌ |

### AI & ML Features

| Permission | Super Admin | Admin | Manager | User |
|------------|-------------|-------|---------|------|
| `ai:read` | ✅ | ✅ | ✅ | ✅ |
| `ai:create` | ✅ | ✅ | ✅ | 🔄 |
| `ai:configure` | ✅ | ✅ | ❌ | ❌ |
| `ml:read` | ✅ | ✅ | ✅ | 🔄 |
| `ml:train` | ✅ | ✅ | ✅ | ❌ |
| `ml:deploy` | ✅ | ✅ | ❌ | ❌ |
| `forecasting:read` | ✅ | ✅ | ✅ | ✅ |
| `forecasting:create` | ✅ | ✅ | ✅ | 🔄 |

---

## Special Permissions

### System Administration

| Permission | Super Admin | Admin | Manager | User |
|------------|-------------|-------|---------|------|
| `system:read` | 🔒 | ❌ | ❌ | ❌ |
| `system:configure` | 🔒 | ❌ | ❌ | ❌ |
| `audit_log:read` | ✅ | ✅ | 🔄 | ❌ |
| `audit_log:export` | ✅ | ✅ | 🔄 | ❌ |

### Data Management

| Permission | Super Admin | Admin | Manager | User |
|------------|-------------|-------|---------|------|
| `data:export` | ✅ | ✅ | ✅ | 🔄 |
| `data:import` | ✅ | ✅ | ✅ | ❌ |
| `data:backup` | ✅ | ✅ | ❌ | ❌ |
| `data:restore` | 🔒 | ❌ | ❌ | ❌ |
| `data:reset` | 🔒 | ❌ | ❌ | ❌ |

### Integration & Migration

| Permission | Super Admin | Admin | Manager | User |
|------------|-------------|-------|---------|------|
| `integration:read` | ✅ | ✅ | ✅ | ❌ |
| `integration:configure` | ✅ | ✅ | ❌ | ❌ |
| `migration:read` | ✅ | ✅ | ❌ | ❌ |
| `migration:create` | ✅ | ✅ | ❌ | ❌ |
| `migration:execute` | ✅ | ✅ | ❌ | ❌ |

---

## Permission Combinations

### Common Role Configurations

#### Sales Representative
```
Permissions:
- crm:read, crm:create, crm:update
- lead:read, lead:create, lead:update, lead:convert
- opportunity:read, opportunity:create, opportunity:update
- contact:read, contact:create, contact:update
- invoice:read, invoice:create
- reports:read, reports:export
```

#### Accountant
```
Permissions:
- finance:read, finance:create, finance:update
- chart_of_accounts:read
- voucher:read, voucher:create, voucher:update
- invoice:read, invoice:create, invoice:update
- reports:read, reports:export
```

#### Production Manager
```
Permissions:
- manufacturing:read, manufacturing:create, manufacturing:update
- bom:read, bom:create, bom:update
- production_order:read, production_order:create, production_order:update
- quality_control:read, quality_control:approve
- inventory:read, inventory:update
- product:read
- reports:read, reports:export
```

#### Warehouse Keeper
```
Permissions:
- inventory:read, inventory:create, inventory:update
- product:read
- stock:read, stock:create, stock:update
- warehouse:read
```

#### HR Manager
```
Permissions:
- hr:read, hr:create, hr:update
- employee:read, employee:create, employee:update
- attendance:read, attendance:approve
- payroll:read, payroll:create, payroll:approve
- reports:read, reports:export
```

---

## Permission Inheritance

### Role Hierarchy

```
Super Admin
    └─> Full system access + cross-organization access
    
Admin (Organization)
    └─> Full organization access
        ├─> User management
        ├─> Module configuration
        └─> All module permissions
        
Manager
    └─> Module-specific management
        ├─> CRUD operations within modules
        ├─> Report generation
        └─> Limited configuration
        
User
    └─> Basic access
        ├─> Read permissions
        ├─> Limited create/update
        └─> Own data management
```

---

## Custom Permissions

Enterprise users can create custom permissions for specific business needs:

### Examples

**Custom Permission**: `invoice:approve_large`
- **Purpose**: Approve invoices over $10,000
- **Granted To**: Finance Director role
- **Implementation**: Custom middleware check

**Custom Permission**: `product:bulk_import`
- **Purpose**: Bulk import products via Excel
- **Granted To**: Data Import Specialist role
- **Implementation**: Special endpoint protection

**Custom Permission**: `report:schedule`
- **Purpose**: Schedule automated report generation
- **Granted To**: Report Administrators
- **Implementation**: Scheduled job configuration

---

## Permission Validation

### Validation Rules

1. **Module Licensing**: Permission requires active module license
2. **Role Assignment**: User must have role with permission
3. **Organization Scope**: Permission is valid only within user's organization
4. **Time-based**: Some permissions may have time restrictions
5. **Feature Flags**: Advanced permissions may require feature flags

### Validation Flow

```
Request → Authentication → Permission Check → Module License → Feature Flag → Action
           ↓                ↓                  ↓               ↓              ↓
           Valid JWT?       Has permission?    Module active?  Feature on?    Execute
```

---

## Appendix

### Permission Naming Conventions

- **Module Prefix**: Use module name (e.g., `crm:`, `finance:`)
- **Action Suffix**: Use standard actions (read, create, update, delete)
- **Specificity**: More specific permissions override general ones
- **Hierarchy**: Parent permissions include child permissions

### Permission Groups

Permissions can be grouped for easier management:

**Group**: `sales_team_basic`
- `crm:read`, `crm:create`, `crm:update`
- `lead:read`, `lead:create`, `lead:update`
- `contact:read`, `contact:create`

**Group**: `finance_team_full`
- `finance:read`, `finance:create`, `finance:update`
- `voucher:read`, `voucher:create`, `voucher:update`
- `invoice:read`, `invoice:create`, `invoice:update`
- `reports:read`, `reports:export`

---

**Document Version**: 1.0  
**Last Updated**: October 29, 2025  
**For Questions**: Check RBAC_COMPREHENSIVE_GUIDE.md or contact dev team
