# Module Categories and Mapping

## Overview

This document provides a comprehensive categorization of all modules and submodules in the FastAPI v1.6 Business Suite. Each module is organized into distinct product categories to enable category-based entitlement activation and licensing.

## Product Categories

### 1. CRM (Customer Relationship Management)

**Description**: Complete customer relationship and sales management suite.

**Primary Modules**:
- **CRM** (`crm`)
  - keywords
  - contacts
  - leads
  - opportunities
  - customers
  - accounts
  - pipeline
  - reports
  - analytics

- **SALES** (`sales`)
  - customers
  - leads
  - opportunities
  - contacts
  - commissions
  - pipeline
  - reports
  - customer_analytics
  - dashboard
  - accounts

- **MARKETING** (`marketing`)
  - campaigns
  - email_marketing
  - social_media
  - content_marketing
  - marketing_automation
  - lead_generation
  - analytics
  - roi_tracking

- **SEO** (`seo`)
  - keywords
  - content_optimization
  - backlinks
  - site_audit
  - rank_tracking
  - competitor_analysis
  - seo_reports

**Use Cases**: Lead management, customer acquisition, sales pipeline tracking, marketing campaigns, SEO optimization

---

### 2. ERP (Enterprise Resource Planning)

**Description**: Core business operations including inventory, procurement, and order management.

**Primary Modules**:
- **ERP** (`erp`)
  - inventory
  - products
  - stock
  - warehouse
  - procurement
  - dispatch
  - tasks_calendar
  - appointments
  - meeting_rooms
  - event_reminders
  - recurring_events
  - vendors
  - customers

- **INVENTORY** (`inventory`)
  - stock
  - locations
  - bins
  - movements
  - cycle_count
  - low_stock
  - pending_orders

- **PROCUREMENT** (`procurement`)
  - purchase_orders
  - purchase_requisitions
  - rfq
  - vendor_quotations
  - vendor_evaluation
  - grn
  - purchase_returns
  - vendor_management

- **ORDER_BOOK** (`order_book`)
  - sales_orders
  - purchase_orders
  - tracking
  - fulfillment
  - analytics

- **MASTER_DATA** (`master_data`)
  - customers
  - vendors
  - products
  - bom
  - employees
  - chart_of_accounts
  - expense_accounts
  - payment_terms
  - tax_codes
  - units
  - company_details
  - multi_company

- **PRODUCT** (`product`)
  - categories
  - units
  - details
  - pricing
  - images

- **VOUCHERS** (`vouchers`)
  - sales_vouchers
  - purchase_vouchers
  - payment_vouchers
  - receipt_vouchers
  - journal_vouchers
  - contra_vouchers
  - debit_note
  - credit_note
  - delivery_challan
  - goods_receipt_note
  - quotation
  - proforma_invoice
  - purchase_order
  - sales_order
  - purchase_return
  - sales_return
  - inter_department_voucher

**Use Cases**: Inventory control, procurement operations, vendor management, order fulfillment, product catalog management

---

### 3. Manufacturing

**Description**: Complete manufacturing operations from planning to execution.

**Primary Modules**:
- **MANUFACTURING** (`manufacturing`)
  - production_planning
  - work_orders
  - bom (Bill of Materials)
  - quality_control
  - job_work
  - material_requisition
  - production_reports
  - capacity_planning
  - shop_floor
  - mrp (Material Requirements Planning)
  - job_cards
  - material_issue
  - material_receipt
  - quality
  - reports

- **BOM** (`bom`)
  - (Bill of Materials standalone features)

**Use Cases**: Production planning, shop floor management, quality control, material requirements planning, work order management

---

### 4. Finance & Accounting

**Description**: Comprehensive financial management and accounting operations.

**Primary Modules**:
- **FINANCE** (`finance`)
  - salary_structure
  - salary_components
  - payslips
  - deductions
  - bonuses
  - tax_calculation
  - statutory_compliance
  - payroll_reports
  - bank_transfer

- **ACCOUNTING** (`accounting`)
  - ledger
  - trial_balance
  - profit_loss
  - balance_sheet
  - cash_flow
  - customer_aging
  - vendor_aging

- **REPORTS_ANALYTICS** (`reports_analytics`)
  - balance_sheet
  - cash_flow
  - ledgers
  - profit_loss
  - trial_balance

- **PAYROLL** (`payroll`)
  - salary_structure
  - salary_components
  - payslips
  - deductions
  - bonuses
  - tax_calculation
  - statutory_compliance
  - payroll_reports
  - bank_transfer

**Use Cases**: General ledger, accounts payable/receivable, financial reporting, payroll processing, tax compliance

---

### 5. Service Management

**Description**: Service desk and customer support operations.

**Primary Modules**:
- **SERVICE** (`service`)
  - tickets
  - sla
  - service_desk
  - technicians
  - feedback
  - dispatch
  - service_analytics

**Use Cases**: Ticket management, SLA tracking, technician dispatch, customer feedback, service analytics

---

### 6. HR (Human Resources)

**Description**: Complete human resource management and talent acquisition.

**Primary Modules**:
- **HR** (`hr`)
  - salary
  - salary_structure
  - payslips
  - deductions
  - bonuses
  - tax_calculation
  - statutory_compliance
  - payroll_reports
  - bank_transfer

- **HR_MANAGEMENT** (`hr_management`)
  - employees_directory
  - employees
  - dashboard

- **TALENT** (`talent`)
  - recruitment
  - candidate_tracking
  - interviews
  - offer_management
  - onboarding
  - talent_pool
  - recruitment_analytics

**Use Cases**: Employee management, recruitment, payroll, performance tracking, talent acquisition

---

### 7. Analytics & Business Intelligence

**Description**: Advanced analytics and reporting capabilities.

**Primary Modules**:
- **ANALYTICS** (`analytics`)
  - customer
  - sales
  - purchase
  - service
  - financial
  - ab_testing
  - streaming_dashboard

- **STREAMING_ANALYTICS** (`streaming_analytics`)
  - (Real-time analytics features)

- **AB_TESTING** (`ab_testing`)
  - (A/B testing capabilities)

**Use Cases**: Business intelligence, data visualization, customer analytics, sales forecasting, performance metrics

---

### 8. AI & Machine Learning

**Description**: Artificial intelligence and machine learning capabilities.

**Primary Modules**:
- **AI_ANALYTICS** (`ai_analytics`)
  - ml_models
  - predictions
  - anomaly_detection
  - recommendations
  - automl
  - explainability
  - reports

- **WEBSITE_AGENT** (`website_agent`)
  - (AI-powered website interaction features)

**Use Cases**: Predictive analytics, automated insights, anomaly detection, intelligent recommendations, AutoML

---

### 9. Project Management

**Description**: Project planning, tracking, and collaboration tools.

**Primary Modules**:
- **PROJECT** (`project`)
  - projects
  - tasks
  - milestones
  - time_tracking
  - resource_allocation
  - project_reports
  - gantt_charts
  - collaboration

- **PROJECTS** (`projects`)
  - planning
  - documents
  - resources
  - analytics

- **TASK_MANAGEMENT** (`task_management`)
  - tasks
  - projects
  - boards
  - sprints
  - time_logs
  - reports

- **TASKS_CALENDAR** (`tasks_calendar`)
  - dashboard
  - create
  - assignments
  - events

**Use Cases**: Project planning, task assignment, time tracking, milestone management, resource allocation

---

### 10. Asset & Transport Management

**Description**: Asset tracking and transportation operations.

**Primary Modules**:
- **ASSET** (`asset`)
  - asset_register
  - asset_tracking
  - depreciation
  - maintenance
  - allocation
  - disposal
  - asset_reports

- **TRANSPORT** (`transport`)
  - vehicles
  - drivers
  - routes
  - trips
  - fuel_management
  - maintenance
  - gps_tracking
  - transport_reports

**Use Cases**: Asset lifecycle management, vehicle fleet management, route optimization, maintenance scheduling

---

### 11. Workflow & Automation

**Description**: Business process automation and workflow management.

**Primary Modules**:
- **WORKFLOW** (`workflow`)
  - templates
  - approval_requests
  - instances
  - automation_rules
  - analytics

**Use Cases**: Approval workflows, process automation, business rule engines, workflow monitoring

---

### 12. Integration & Platform

**Description**: System integrations and platform capabilities.

**Primary Modules**:
- **INTEGRATION** (`integration`)
  - api_keys
  - webhooks
  - external
  - data_sync
  - tally_sync
  - oauth_clients
  - logs

**Use Cases**: Third-party integrations, API management, data synchronization, OAuth authentication

---

### 13. Communication & Collaboration (Always-On)

**Description**: Essential communication tools available to all users.

**Primary Modules**:
- **EMAIL** (`email`) - *Always-On*
  - inbox
  - compose
  - templates
  - accounts
  - sync
  - filters
  - analytics

- **CALENDAR** (`calendar`)
  - events
  - meetings
  - reminders
  - sharing
  - event_types

**Use Cases**: Email communication, calendar scheduling, meeting coordination

---

### 14. Additional Features

**Description**: Specialized and emerging capabilities.

**Primary Modules**:
- **EXHIBITION** (`exhibition`)
  - events
  - booths
  - attendees
  - leads
  - analytics

- **CUSTOMER** (`customer`)
  - (Customer-specific features)

- **VENDOR** (`vendor`)
  - (Vendor-specific features)

- **VOUCHER** (`voucher`)
  - (Voucher-specific features)

- **STOCK** (`stock`)
  - (Stock-specific features)

**Use Cases**: Event management, specialized business operations

---

### 15. Administration & Settings (RBAC-Only)

**Description**: System administration and configuration - not billable, always available to admins.

**Primary Modules**:
- **SETTINGS** (`settings`) - *RBAC-Only*
  - general_settings
  - company
  - user_management
  - voucher_settings
  - data_management
  - factory_reset

- **ADMIN** (`admin`) - *RBAC-Only*
  - app_user_management
  - audit_logs
  - notifications
  - license_management
  - manage_organizations

- **ORGANIZATION** (`organization`) - *RBAC-Only*
  - create
  - users

**Use Cases**: System configuration, user administration, organization management, audit logging

---

## Category-to-Module Mapping Summary

```
CRM → [crm, sales, marketing, seo]
ERP → [erp, inventory, procurement, order_book, master_data, product, vouchers]
Manufacturing → [manufacturing, bom]
Finance & Accounting → [finance, accounting, reports_analytics, payroll]
Service → [service]
HR → [hr, hr_management, talent]
Analytics → [analytics, streaming_analytics, ab_testing]
AI → [ai_analytics, website_agent]
Project Management → [project, projects, task_management, tasks_calendar]
Asset & Transport → [asset, transport]
Workflow & Automation → [workflow]
Integration → [integration]
Communication → [email, calendar] (Always-On for email)
Additional Features → [exhibition, customer, vendor, voucher, stock]
Administration → [settings, admin, organization] (RBAC-Only, non-billable)
```

## Module Status Types

### Always-On Modules
Modules that are always accessible regardless of entitlements:
- **email**: Core communication tool available to all users

### RBAC-Only Modules
Modules controlled only by role-based permissions (not entitlements):
- **settings**: System configuration
- **admin**: Administration features
- **organization**: Organization management

### Entitlement-Controlled Modules
All other modules require explicit entitlement activation at the organization level.

## Future Growth Opportunities

### Identified Gaps for Future Modules:

1. **Document Management**
   - Document storage
   - Version control
   - Approval workflows
   - Electronic signatures

2. **E-Commerce**
   - Online storefront
   - Shopping cart
   - Payment gateway integration
   - Order fulfillment

3. **Quality Management**
   - Quality audits
   - Corrective actions
   - Supplier quality
   - Compliance tracking

4. **Field Service Management**
   - Mobile technician app
   - GPS tracking
   - Job scheduling
   - Parts inventory

5. **Learning Management**
   - Training courses
   - Certifications
   - Employee development
   - Knowledge base

6. **Business Intelligence**
   - Advanced dashboards
   - Predictive analytics
   - Data warehousing
   - Custom reports

7. **Compliance Management**
   - Regulatory tracking
   - Audit trails
   - Policy management
   - Risk assessment

8. **Contract Management**
   - Contract lifecycle
   - Renewals
   - Compliance tracking
   - E-signatures

## Implementation Notes

### Category-Based Activation
When an **App Super Admin** selects a category for an organization:
1. All modules in that category are instantly enabled
2. All submodules within those modules become available
3. The organization's `enabled_modules` is updated
4. Changes are immediately reflected in the UI
5. Entitlement cache is invalidated

**Important**: Category activation is performed by **App Super Admin** only, not Org Admin. This is a licensing/billing operation that controls what features an organization has access to.

### Module Dependencies
Some modules may have dependencies on others:
- **Manufacturing** requires **Inventory** and **Product**
- **Payroll** is part of both **Finance** and **HR** categories
- **Analytics** modules may depend on their respective operational modules

### Licensing Considerations
- Categories can be licensed as bundles
- Individual modules can be licensed separately for flexibility
- Always-On modules (Email) are included in all plans
- RBAC-Only modules (Settings, Admin) are non-billable

---

**Last Updated**: 2024-11-03
**Version**: 1.0.0
**Status**: Complete
