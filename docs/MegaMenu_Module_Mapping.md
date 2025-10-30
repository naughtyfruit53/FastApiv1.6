# MegaMenu Module Mapping Guide

## Overview

This document provides a comprehensive mapping between organization-enabled modules and MegaMenu items. It explains which `enabled_modules` flags (and/or permissions) activate each MegaMenu section and sub-items.

## Purpose

- **For Administrators**: Understand which modules to enable for specific menu items to appear
- **For Developers**: Reference guide for menu configuration and module dependencies
- **For QA**: Test checklist to verify menu behavior when modules are toggled on/off

---

## Module-to-Menu Mapping

### 1. Master Data

**Enabled Module**: `master_data`

**Permission**: `master_data.view`

**Menu Items**:
- **Business Entities**
  - Vendors (`master_data` + `vendors` submodule)
  - Customers (`master_data` + `customers` submodule)
  - Employees (`master_data` + `employees` submodule)
  - Company Details (`master_data` + `company_details` submodule)

- **Product & Inventory**
  - Products (`master_data` + `products` submodule)
  - Categories (`master_data` + `categories` submodule)
  - Units (`master_data` + `units` submodule)
  - Bill of Materials (BOM) (`master_data` + `bom` submodule)

- **Financial Configuration**
  - Chart of Accounts (`master_data` + `chart_of_accounts` submodule)
  - Tax Codes (`master_data` + `tax_codes` submodule)
  - Payment Terms (`master_data` + `payment_terms` submodule)
  - Bank Account (`master_data` + `bank_account` submodule)

**Test**: When `master_data` is disabled, the entire Master Data top-level menu item should not appear.

---

### 2. Inventory

**Enabled Module**: `inventory`

**Permission**: `inventory.view`

**Menu Items**:
- **Stock Management**
  - Current Stock (`inventory` + `current_stock` submodule)
  - Stock Movements (`inventory` + `stock_movements` submodule)
  - Low Stock Report (`inventory` + `low_stock_report` submodule)
  - Pending Orders (`inventory` + `pending_orders` submodule)

- **Warehouse Management**
  - Locations (`inventory` + `locations` submodule)
  - Bin Management (`inventory` + `bin_management` submodule)
  - Cycle Count (`inventory` + `cycle_count` submodule)

**Test**: Toggle `inventory` module on/off and verify all inventory menu items appear/disappear accordingly.

---

### 3. Manufacturing

**Enabled Module**: `manufacturing`

**Permission**: `manufacturing.view`

**Menu Items**:
- **Production Management**
  - Order Book (`manufacturing` + `order_book` submodule)
  - Production Order (`manufacturing` + `production_order` submodule)
  - Work Order (`manufacturing` + `work_order` submodule)
  - Material Requisition (`manufacturing` + `material_requisition` submodule)
  - Finished Good Receipt (`manufacturing` + `finished_good_receipt` submodule)
  - Job Card (`manufacturing` + `job_card` submodule)

- **Jobwork Management**
  - Inward Jobwork (`manufacturing` + `inward_jobwork` submodule)
  - Outward Jobwork (`manufacturing` + `outward_jobwork` submodule)
  - Jobwork Challan (`manufacturing` + `jobwork_challan` submodule)
  - Jobwork Receipt (`manufacturing` + `jobwork_receipt` submodule)

- **Manufacturing Operations**
  - Manufacturing Journal (`manufacturing` + `manufacturing_journal` submodule)
  - Stock Journal (`manufacturing` + `stock_journal` submodule)
  - Material Receipt (`manufacturing` + `material_receipt` submodule)

- **Quality Control**
  - QC Checkpoints (`manufacturing` + `qc_checkpoints` submodule)
  - QC Reports (`manufacturing` + `qc_reports` submodule)

**Test**: Disable `manufacturing` module and confirm all manufacturing-related menu items are hidden.

---

### 4. Vouchers

**Enabled Module**: `vouchers`

**Permission**: `vouchers.view`

**Menu Items**:
- **Sales Vouchers**
  - Sales Order, Delivery Note, Sales Invoice, Credit Note, etc.
  - (`vouchers` + `sales_vouchers` submodule)

- **Purchase Vouchers**
  - Purchase Order, Goods Receipt Note (GRN), Purchase Invoice, Debit Note, etc.
  - (`vouchers` + `purchase_vouchers` submodule)

- **Inventory Vouchers**
  - Stock Transfer, Stock Adjustment, etc.
  - (`vouchers` + `inventory_vouchers` submodule)

- **Manufacturing Vouchers**
  - See Manufacturing section
  - (`vouchers` + `manufacturing_vouchers` submodule)

**Test**: Toggle `vouchers` module and verify voucher-related menu items respond accordingly.

---

### 5. Finance & Accounting

**Enabled Module**: `finance` and/or `accounting`

**Permission**: `finance.view`, `accounting.view`

**Menu Items**:
- **Financial Management**
  - Ledger Entries (`finance` module)
  - Payment Vouchers (`finance` module)
  - Receipt Vouchers (`finance` module)
  - Journal Vouchers (`accounting` module)
  - Bank Reconciliation (`finance` + `accounting` modules)

- **Financial Reports**
  - Balance Sheet (`accounting` module)
  - Profit & Loss (`accounting` module)
  - Cash Flow Statement (`accounting` module)
  - Trial Balance (`accounting` module)

**Test**: 
- Enable `finance` only: Financial management items appear
- Enable `accounting` only: Accounting-specific reports appear
- Enable both: All finance and accounting items appear

---

### 6. Reports & Analytics

**Enabled Module**: `reportsAnalytics`

**Permission**: `reportsAnalytics.view`

**Menu Items**:
- Operational Reports
- Sales Reports
- Inventory Reports
- Financial Reports
- Custom Reports

**Test**: Disable `reportsAnalytics` and verify reports menu section is hidden.

---

### 7. AI Analytics

**Enabled Module**: `aiAnalytics`

**Permission**: `aiAnalytics.view`

**Menu Items**:
- AI Dashboard
- Predictive Analytics
- Data Insights
- ML Models
- AutoML

**Test**: Toggle `aiAnalytics` module and confirm AI-related menu items appear/disappear.

---

### 8. Sales & CRM

**Enabled Module**: `sales` and/or `crm`

**Permission**: `sales.view`, `crm.view`

**Menu Items**:
- **Sales**
  - Quotations (`sales` module)
  - Sales Orders (`sales` module)
  - Invoices (`sales` module)
  - Customers (`sales` + `crm` modules)

- **CRM**
  - Leads (`crm` module)
  - Opportunities (`crm` module)
  - Contacts (`crm` module)
  - Activities (`crm` module)
  - Service Desk (`crm` + service permissions)

**Test**: 
- Enable `sales` only: Sales-related items appear
- Enable `crm` only: CRM-specific items appear
- Enable both: Full sales and CRM functionality

---

### 9. Marketing

**Enabled Module**: `marketing`

**Permission**: `marketing.view`

**Menu Items**:
- Campaigns
- Email Marketing
- Social Media
- Analytics
- Lead Generation

**Test**: Disable `marketing` module and verify marketing menu section is hidden.

---

### 10. Service Desk

**Enabled Module**: `service` (or `crm` with service permissions)

**Permission**: Service-specific permissions from RBAC

**Menu Items**:
- Service Dashboard
- Tickets
- Service Requests
- Knowledge Base
- SLA Management
- Service Analytics

**Test**: 
- For org_admin: Service items should appear if `service` module is enabled
- Verify RBAC service permissions control access to specific service features

---

### 11. Projects & Tasks

**Enabled Module**: `projects` and/or `tasks_calendar`

**Permission**: `projects.view`, `tasks_calendar.view`

**Menu Items**:
- **Projects**
  - Project List (`projects` module)
  - Task Board (`projects` + `tasks_calendar` modules)
  - Gantt Chart (`projects` module)
  - Project Reports (`projects` module)

- **Tasks & Calendar**
  - Tasks (`tasks_calendar` module)
  - Calendar View (`tasks_calendar` module)
  - Reminders (`tasks_calendar` module)

**Test**: Toggle each module independently and verify menu items respond correctly.

---

### 12. HR Management

**Enabled Module**: `hr` (or `hrManagement`)

**Permission**: `hr.view`, `hrManagement.view`

**Menu Items**:
- Employee Management
- Attendance
- Leave Management
- Payroll
- Performance Reviews
- HR Reports

**Test**: Disable `hr` module and confirm HR menu section disappears.

---

### 13. Email

**Enabled Module**: `email`

**Permission**: `email.view`

**Menu Items**:
- Inbox
- Compose
- Sent
- Drafts
- Settings

**Note**: Email is a direct-path menu item (doesn't expand into submenu)

**Test**: Toggle `email` module and verify Email menu item appears/disappears.

---

### 14. Settings & Administration

**Enabled Module**: Always visible to authorized users

**Permissions**: 
- `settings.view` (basic settings)
- `settings.manageUsers` (user management)
- `settings.manageRoles` (role management)
- `settings.manageOrganization` (org settings)
- `admin.*` (super admin functions)

**Menu Items**:
- Organization Settings (org_admin+)
- User Management (org_admin+)
- Role Management (org_admin+)
- Module Settings (org_admin+)
- System Settings (super_admin only)

**Test**: 
- As org_admin: Organization management items appear
- As super_admin: All admin and system items appear
- As regular user: Limited settings visible

---

## Module Enabling/Disabling Guidelines

### Backend: How to Enable/Disable Modules

1. **Via API** (requires `organization_module.update` permission):
   ```bash
   PUT /api/v1/organizations/{org_id}/modules
   {
     "enabled_modules": {
       "master_data": true,
       "inventory": true,
       "manufacturing": false,
       "vouchers": true,
       "finance": true,
       "accounting": true,
       "reportsAnalytics": true,
       "aiAnalytics": false,
       "sales": true,
       "crm": true,
       "marketing": false,
       "service": true,
       "projects": true,
       "tasks_calendar": true,
       "hr": true,
       "email": true
     }
   }
   ```

2. **Via Database**:
   ```sql
   UPDATE organizations 
   SET enabled_modules = '{"master_data": true, "inventory": true, ...}'::jsonb
   WHERE id = <org_id>;
   ```

3. **Default Modules**: Set in `app/core/modules_registry.py` via `get_default_enabled_modules()`

### Frontend: How Modules Affect Menu Display

1. **MegaMenu.tsx** checks:
   - `organizationData?.enabled_modules?.[module]` for org-level module status
   - `hasModuleAccess(module)` for user-level RBAC permissions
   - `isModuleEnabled(module)` for combined check

2. **Menu Item Filtering**:
   - Items with `requireModule` property are filtered based on module status
   - Items with `requireSubmodule` property check both module and submodule
   - Items with `permission` property check RBAC permissions

---

## Testing Checklist

Use this checklist to verify menu behavior:

### Test Scenario 1: org_admin User with All Modules Enabled

- [ ] Login as org_admin
- [ ] Verify all top-level menu items appear
- [ ] Click each top-level item and verify submenu expands
- [ ] Verify no permission errors in console

### Test Scenario 2: org_admin User with Selective Modules

- [ ] Disable `manufacturing` module
- [ ] Login as org_admin
- [ ] Verify Manufacturing menu item does NOT appear
- [ ] Verify other menu items still work correctly
- [ ] Re-enable `manufacturing` and verify it reappears

### Test Scenario 3: super_admin User

- [ ] Login as super_admin
- [ ] Verify ALL menu items appear regardless of org enabled_modules
- [ ] Verify Admin menu section is visible
- [ ] Verify ability to manage organization modules

### Test Scenario 4: Regular User

- [ ] Login as regular user
- [ ] Verify only permitted modules appear
- [ ] Verify submodules match assigned permissions
- [ ] Verify no unauthorized menu items

### Test Scenario 5: Empty/Undefined Modules Handling

- [ ] Set organization `enabled_modules` to `null` in database
- [ ] Login as org_admin
- [ ] Verify graceful fallback (no errors)
- [ ] Verify default modules are applied

### Test Scenario 6: RBAC Permissions Failure

- [ ] Simulate RBAC endpoint failure (e.g., network error)
- [ ] Login as user
- [ ] Verify safe fallback permissions are used
- [ ] Verify no blocking errors
- [ ] Verify `modules: []` in fallback response

---

## Troubleshooting

### Issue: Menu items not appearing for org_admin

**Possible Causes**:
1. Organization `enabled_modules` field is null or missing
   - **Fix**: Run backend seeding or manually set enabled_modules
2. RBAC permissions endpoint returning error
   - **Fix**: Check backend logs, ensure modules field in response
3. Frontend context not loading permissions
   - **Fix**: Check browser console for errors, verify AuthContext

### Issue: Menu expands but shows "No items available"

**Possible Causes**:
1. Module enabled but submodules not configured
   - **Fix**: Ensure submodule structure in menuConfig.tsx
2. User lacks specific submodule permissions
   - **Fix**: Assign appropriate service roles or permissions

### Issue: super_admin sees limited menu

**Possible Causes**:
1. `is_super_admin` flag not set correctly
   - **Fix**: Verify user.is_super_admin in database
2. Frontend not detecting super admin status
   - **Fix**: Check localStorage for IS_SUPER_ADMIN_KEY

---

## API Endpoints Reference

### Get Organization Modules
```
GET /api/v1/organizations/{org_id}/modules
Response: { "enabled_modules": { "master_data": true, ... } }
```

### Update Organization Modules
```
PUT /api/v1/organizations/{org_id}/modules
Body: { "enabled_modules": { "master_data": true, ... } }
Response: { "message": "Organization modules updated successfully", "enabled_modules": {...} }
```

### Get User Permissions
```
GET /api/v1/rbac/users/{user_id}/permissions
Response: {
  "user_id": 123,
  "permissions": ["master_data.view", ...],
  "service_roles": [...],
  "modules": ["master_data", "inventory", ...],
  "total_permissions": 50
}
```

---

## Module Hierarchy

```
Organization
└── enabled_modules (JSON field)
    ├── master_data: boolean
    ├── inventory: boolean
    ├── manufacturing: boolean
    ├── vouchers: boolean
    ├── finance: boolean
    ├── accounting: boolean
    ├── reportsAnalytics: boolean
    ├── aiAnalytics: boolean
    ├── sales: boolean
    ├── crm: boolean
    ├── marketing: boolean
    ├── service: boolean
    ├── projects: boolean
    ├── tasks_calendar: boolean
    ├── hr: boolean
    └── email: boolean

User
├── RBAC Service Roles
│   └── Permissions (module.action format)
└── Resolved Permissions
    ├── permissions: ["module.action", ...]
    ├── modules: ["module_name", ...]
    └── submodules: { "module": ["submodule"], ... }
```

---

## Summary

This guide provides a complete mapping of organization modules to MegaMenu items. Follow the test checklist to validate menu behavior when toggling modules, and use the troubleshooting section to resolve common issues.

**Key Points**:
- Modules are controlled at organization level via `enabled_modules`
- RBAC permissions provide fine-grained access control
- MegaMenu filters items based on both module status and permissions
- Super admins bypass module restrictions
- Safe fallbacks ensure no blocking errors when permissions fail
