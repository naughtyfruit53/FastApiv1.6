# Feature Access Mapping - FastApiV1.5

## Overview

This document serves as the **source of truth** for all implemented features in the FastApiV1.5 repository, mapping backend API routes to frontend components, required roles (RBAC), current access paths, and mega menu exposure status. This mapping is essential for the upcoming mega menu overhaul and must be maintained whenever new features are added.

## Feature Categories

### 🔐 Authentication & User Management

| Feature | API Route(s) | Frontend Component/Page | Required Role(s) | Current Access Path | Mega Menu Exposed | Notes |
|---------|-------------|------------------------|------------------|-------------------|------------------|-------|
| **User Login** | `POST /api/v1/auth/login`<br>`POST /api/v1/auth/login/email` | `LoginForm.tsx`<br>`/login.tsx` | Public | Direct URL `/login` | ❌ | Entry point, no menu needed |
| **OTP Authentication** | `POST /api/v1/otp/*` | `OTPLogin.tsx` | Public | Via Login Form | ❌ | Part of login flow |
| **Password Reset** | `POST /api/v1/password/reset`<br>`POST /api/v1/reset/*` | `ForgotPasswordModal.tsx`<br>`ResetDialog.tsx` | Public | Via Login Form | ❌ | Password recovery flow |
| **Master Authentication** | `POST /api/v1/master-auth/*` | Not directly exposed | App Super Admin | Backend only | ❌ | System-level auth |
| **Admin Setup** | `POST /api/v1/admin-setup/*` | Not exposed | App Super Admin | Backend only | ❌ | Initial system setup |
| **User Profile Management** | `GET/PUT /api/v1/user/*` | `UserProfile.tsx`<br>`/Profile.tsx` | All authenticated | User menu dropdown | ❌ | Accessible via account icon |
| **App User Management** | `GET/POST/PUT/DELETE /api/v1/app-users/*` | `AddUserDialog.tsx` | App Super Admin | Settings page | ❌ | **RECOMMENDATION**: Should be in admin menu |

### 🏢 Platform & Organization Management

| Feature | API Route(s) | Frontend Component/Page | Required Role(s) | Current Access Path | Mega Menu Exposed | Notes |
|---------|-------------|------------------------|------------------|-------------------|------------------|-------|
| **Platform Statistics** | `GET /api/v1/platform/*` | `AppSuperAdminDashboard.tsx` | App Super Admin | `/dashboard` | ❌ | Dashboard available for app admins |
| **Organization Management** | `GET/POST/PUT/DELETE /api/v1/organizations/*` | `/admin/manage-organizations.tsx`<br>`/admin/organizations/*` | App Super Admin | `/admin/manage-organizations` | ❌ | Admin area for org management |
| **Organization License Creation** | `POST /api/v1/organizations/*/license` | `/admin/license-management.tsx`<br>`CreateOrganizationLicenseModal.tsx` | App Super Admin (app-level only, no org_id) | License Management button in mega menu | ✅ | Restricted to app-level admins, hidden from org accounts |
| **Organization Members** | `GET /api/v1/organizations/*/members` | `OrganizationMembersDialog.tsx` | Org Super Admin | Settings page | ❌ | **RECOMMENDATION**: Add to settings submenu |
| **App User Management** | `GET/POST/PUT/DELETE /api/v1/app-users/*` | `/admin/app-user-management.tsx` | App Super Admin | `/admin/app-user-management` | ❌ | Available in admin area |

### 👥 Business Entities Management

| Feature | API Route(s) | Frontend Component/Page | Required Role(s) | Current Access Path | Mega Menu Exposed | Notes |
|---------|-------------|------------------------|------------------|-------------------|------------------|-------|
| **User Management** | `GET/POST/PUT/DELETE /api/v1/users/*` | `/settings/user-management.tsx`<br>`/settings/add-user.tsx`<br>`AddUserDialog.tsx` | Org Super Admin | Settings → User Management | ❌ | Properly moved to settings area |
| **Company Details** | `GET/PUT /api/v1/companies/*` | `CompanyDetailsModal.tsx`<br>`CompanySetupGuard.tsx` | Org Admin+ | Masters menu → Company Details | ✅ | Well integrated |
| **Company Branding** | `GET/PUT /api/v1/company/branding/*` | `CompanyLogoUpload.tsx` | Org Admin+ | Company details page | ❌ | Embedded in company details |
| **Vendor Management** | `GET/POST/PUT/DELETE /api/v1/vendors/*` | `AddVendorModal.tsx`<br>`/masters/vendors` | Org User+ | Masters menu → Vendors | ✅ | Well integrated |
| **Customer Management** | `GET/POST/PUT/DELETE /api/v1/customers/*` | `AddCustomerModal.tsx`<br>`/masters/customers` | Org User+ | Masters menu → Customers | ✅ | Well integrated |
| **Product Management** | `GET/POST/PUT/DELETE /api/v1/products/*` | `AddProductModal.tsx`<br>`ProductDropdown.tsx`<br>`/masters/products` | Org User+ | Masters menu → Products | ✅ | Well integrated |

### 📋 Voucher System

| Feature | API Route(s) | Frontend Component/Page | Required Role(s) | Current Access Path | Mega Menu Exposed | Notes |
|---------|-------------|------------------------|------------------|-------------------|------------------|-------|
| **Sales Vouchers** | `GET/POST/PUT/DELETE /api/v1/sales-vouchers/*` | `/vouchers/Sales-Vouchers/sales-voucher` | Org User+ | Vouchers menu → Sales Vouchers | ✅ | Complete implementation |
| **Sales Orders** | `GET/POST/PUT/DELETE /api/v1/sales-orders/*` | `/vouchers/Pre-Sales-Voucher/sales-order` | Org User+ | Vouchers menu → Pre Sales Vouchers | ✅ | Complete implementation |
| **Delivery Challans** | `GET/POST/PUT/DELETE /api/v1/delivery-challans/*` | `/vouchers/Sales-Vouchers/delivery-challan` | Org User+ | Vouchers menu → Sales Vouchers | ✅ | Complete implementation |
| **Sales Returns** | `GET/POST/PUT/DELETE /api/v1/sales-returns/*` | `/vouchers/Sales-Vouchers/sales-return` | Org User+ | Vouchers menu → Sales Vouchers | ✅ | Complete implementation |
| **Purchase Orders** | `GET/POST/PUT/DELETE /api/v1/purchase-orders/*` | `/vouchers/Purchase-Vouchers/purchase-order` | Org User+ | Vouchers menu → Purchase Vouchers | ✅ | Complete implementation |
| **Goods Receipt Notes** | `GET/POST/PUT/DELETE /api/v1/goods-receipt-notes/*` | `/vouchers/Purchase-Vouchers/grn` | Org User+ | Vouchers menu → Purchase Vouchers | ✅ | Complete implementation |
| **Purchase Vouchers** | `GET/POST/PUT/DELETE /api/v1/purchase-vouchers/*` | `/vouchers/Purchase-Vouchers/purchase-voucher` | Org User+ | Vouchers menu → Purchase Vouchers | ✅ | Complete implementation |
| **Purchase Returns** | `GET/POST/PUT/DELETE /api/v1/purchase-returns/*` | `/vouchers/Purchase-Vouchers/purchase-return` | Org User+ | Vouchers menu → Purchase Vouchers | ✅ | Complete implementation |
| **Proforma Invoices** | `GET/POST/PUT/DELETE /api/v1/proforma-invoices/*` | `/vouchers/Pre-Sales-Voucher/proforma-invoice` | Org User+ | Vouchers menu → Pre Sales Vouchers | ✅ | Complete implementation |
| **Quotations** | `GET/POST/PUT/DELETE /api/v1/quotations/*` | `/vouchers/Pre-Sales-Voucher/quotation` | Org User+ | Vouchers menu → Pre Sales Vouchers | ✅ | Complete implementation |
| **Payment Vouchers** | `GET/POST/PUT/DELETE /api/v1/payment-vouchers/*` | `/vouchers/Financial-Vouchers/payment-voucher` | Org User+ | Vouchers menu → Financial Vouchers | ✅ | Complete implementation |
| **Receipt Vouchers** | `GET/POST/PUT/DELETE /api/v1/receipt-vouchers/*` | `/vouchers/Financial-Vouchers/receipt-voucher` | Org User+ | Vouchers menu → Financial Vouchers | ✅ | Complete implementation |
| **Contra Vouchers** | `GET/POST/PUT/DELETE /api/v1/contra-vouchers/*` | `/vouchers/Financial-Vouchers/contra-voucher` | Org User+ | Vouchers menu → Financial Vouchers | ✅ | Complete implementation |
| **Journal Vouchers** | `GET/POST/PUT/DELETE /api/v1/journal-vouchers/*` | `/vouchers/Financial-Vouchers/journal-voucher` | Org User+ | Vouchers menu → Financial Vouchers | ✅ | Complete implementation |
| **Credit Notes** | `GET/POST/PUT/DELETE /api/v1/credit-notes/*` | `/vouchers/Financial-Vouchers/credit-note` | Org User+ | Vouchers menu → Financial Vouchers | ✅ | Complete implementation |
| **Debit Notes** | `GET/POST/PUT/DELETE /api/v1/debit-notes/*` | `/vouchers/Financial-Vouchers/debit-note` | Org User+ | Vouchers menu → Financial Vouchers | ✅ | Complete implementation |
| **Inter-Department Vouchers** | `GET/POST/PUT/DELETE /api/v1/inter-department-vouchers/*` | `/vouchers/inter-department-voucher` | Org User+ | Vouchers menu → Inter Department | ✅ | Complete implementation |

### 📦 Inventory & Stock Management

| Feature | API Route(s) | Frontend Component/Page | Required Role(s) | Current Access Path | Mega Menu Exposed | Notes |
|---------|-------------|------------------------|------------------|-------------------|------------------|-------|
| **Current Stock View** | `GET /api/v1/stock/*` | `StockDisplay.tsx`<br>`/inventory/stock` | Org User+ | Inventory menu → Current Stock | ✅ | Well integrated |
| **Stock Movements** | `GET /api/v1/stock/movements/*` | `/inventory/movements` | Org User+ | Inventory menu → Stock Movements | ✅ | Well integrated |
| **Stock Bulk Import** | `POST /api/v1/stock/bulk-import` | `StockBulkImport.tsx` | Org Admin+ | Not exposed | ❌ | **ACTION NEEDED**: Add to inventory menu |
| **Low Stock Report** | `GET /api/v1/stock/low-stock` | `/inventory/low-stock` | Org User+ | Inventory menu → Low Stock Report | ✅ | Well integrated |
| **Inventory Management** | `GET/POST/PUT/DELETE /api/v1/inventory/*` | `/inventory/*` pages | Org User+ | Inventory menu → various | ✅ | Comprehensive coverage |
| **Warehouse Locations** | `GET/POST/PUT/DELETE /api/v1/inventory/locations/*` | `/inventory/locations` | Org Admin+ | Inventory menu → Locations | ✅ | Well integrated |
| **Bin Management** | `GET/POST/PUT/DELETE /api/v1/inventory/bins/*` | `/inventory/bins` | Org Admin+ | Inventory menu → Bin Management | ✅ | Well integrated |

### 🏭 Manufacturing & BOM

| Feature | API Route(s) | Frontend Component/Page | Required Role(s) | Current Access Path | Mega Menu Exposed | Notes |
|---------|-------------|------------------------|------------------|-------------------|------------------|-------|
| **Bill of Materials** | `GET/POST/PUT/DELETE /api/v1/bom/*` | `/masters?tab=bom` | Org User+ | Masters menu → BOM | ✅ | Available in masters |
| **Manufacturing Orders** | `GET/POST/PUT/DELETE /api/v1/manufacturing/*` | `/vouchers/Manufacturing-Vouchers/*` | Org User+ | Vouchers menu → Manufacturing | ✅ | Part of voucher system |
| **Production Orders** | `GET/POST /api/v1/manufacturing/production-orders/*` | `/vouchers/Manufacturing-Vouchers/production-order` | Org User+ | Vouchers menu → Manufacturing | ✅ | Well integrated |
| **Material Requisitions** | `GET/POST /api/v1/manufacturing/material-requisitions/*` | `/vouchers/Manufacturing-Vouchers/material-requisition` | Org User+ | Vouchers menu → Manufacturing | ✅ | Well integrated |
| **Work Orders** | `GET/POST /api/v1/manufacturing/work-orders/*` | `/vouchers/Manufacturing-Vouchers/work-order` | Org User+ | Vouchers menu → Manufacturing | ✅ | Well integrated |

### 📊 Reports & Analytics

| Feature | API Route(s) | Frontend Component/Page | Required Role(s) | Current Access Path | Mega Menu Exposed | Notes |
|---------|-------------|------------------------|------------------|-------------------|------------------|-------|
| **Financial Reports** | `GET /api/v1/reports/*` | `/reports/*` pages | Org User+ | Reports menu → Financial Reports | ✅ | Comprehensive reporting |
| **Ledger Reports** | `GET /api/v1/reports/ledgers/*` | `/reports/ledgers` | Org User+ | Reports menu → Ledgers | ✅ | Well integrated |
| **Trial Balance** | `GET /api/v1/reports/trial-balance` | `/reports/trial-balance` | Org User+ | Reports menu → Trial Balance | ✅ | Well integrated |
| **Profit & Loss** | `GET /api/v1/reports/profit-loss` | `/reports/profit-loss` | Org User+ | Reports menu → P&L | ✅ | Well integrated |
| **Balance Sheet** | `GET /api/v1/reports/balance-sheet` | `/reports/balance-sheet` | Org User+ | Reports menu → Balance Sheet | ✅ | Well integrated |
| **Stock Reports** | `GET /api/v1/reports/stock/*` | `/reports/stock` | Org User+ | Reports menu → Stock Report | ✅ | Well integrated |
| **Customer Analytics** | `GET /api/v1/analytics/*` | `CustomerAnalytics.tsx`<br>`CustomerAnalyticsModal.tsx` | Org Manager+ | Not directly exposed | ❌ | **ACTION NEEDED**: Add to reports or dedicated analytics menu |

### 🔔 Notifications & Communication

| Feature | API Route(s) | Frontend Component/Page | Required Role(s) | Current Access Path | Mega Menu Exposed | Notes |
|---------|-------------|------------------------|------------------|-------------------|------------------|-------|
| **Notification System** | `GET/POST /api/v1/notifications/*` | `NotificationBell.tsx`<br>`NotificationDashboard.tsx` | Org User+ | Header notification bell | ❌ | Always visible in header |
| **Notification Settings** | `GET/PUT /api/v1/notifications/settings/*` | `NotificationSettingsModal.tsx` | Org User+ | Via notification bell | ❌ | Accessible through notifications |
| **Notification Templates** | `GET/POST/PUT /api/v1/notifications/templates/*` | `NotificationTemplates.tsx` | Org Admin+ | Not exposed | ❌ | **ACTION NEEDED**: Add to admin/settings area |
| **Send Notifications** | `POST /api/v1/notifications/send` | `SendNotification.tsx` | Org Admin+ | Not exposed | ❌ | **ACTION NEEDED**: Add to admin area |

### 🛠️ Service CRM & Support

| Feature | API Route(s) | Frontend Component/Page | Required Role(s) | Current Access Path | Mega Menu Exposed | Notes |
|---------|-------------|------------------------|------------------|-------------------|------------------|-------|
| **RBAC Management** | `GET/POST/PUT/DELETE /api/v1/rbac/*` | `RoleManagement/*` components | Service Admin | Not exposed | ❌ | **ACTION NEEDED**: Add to admin/settings |
| **SLA Management** | `GET/POST/PUT/DELETE /api/v1/sla/*` | `SLAStatus.tsx`<br>`/sla/*` pages | Service Manager+ | Direct URL `/sla` | ❌ | **RECOMMENDATION**: Add to service menu |
| **Dispatch Management** | `GET/POST/PUT/DELETE /api/v1/dispatch/*` | `DispatchManagement/*` components | Service User+ | Not exposed | ❌ | **ACTION NEEDED**: Add to service operations menu |
| **Service Analytics Dashboard** | `GET /api/v1/service-analytics/organizations/*/analytics/dashboard` | `ServiceAnalyticsDashboard` | Service Manager+ | Not exposed | ❌ | **ACTION NEEDED**: Add to analytics/reports menu |
| **Job Completion Analytics** | `GET /api/v1/service-analytics/organizations/*/analytics/job-completion` | `JobCompletionChart` | Service User+ | Not exposed | ❌ | **ACTION NEEDED**: Add to service analytics section |
| **Technician Performance** | `GET /api/v1/service-analytics/organizations/*/analytics/technician-performance` | `TechnicianPerformanceChart` | Service Manager+ | Not exposed | ❌ | **ACTION NEEDED**: Add to service analytics section |
| **Customer Satisfaction Analytics** | `GET /api/v1/service-analytics/organizations/*/analytics/customer-satisfaction` | `CustomerSatisfactionChart` | Service User+ | Not exposed | ❌ | **ACTION NEEDED**: Add to service analytics section |
| **Job Volume Analytics** | `GET /api/v1/service-analytics/organizations/*/analytics/job-volume` | `JobVolumeChart` | Service User+ | Not exposed | ❌ | **ACTION NEEDED**: Add to service analytics section |
| **SLA Compliance Analytics** | `GET /api/v1/service-analytics/organizations/*/analytics/sla-compliance` | `SLAComplianceChart` | Service Manager+ | Not exposed | ❌ | **ACTION NEEDED**: Add to service analytics section |
| **Feedback Workflow** | `GET/POST/PUT /api/v1/feedback/*` | `FeedbackWorkflow/*` components | Service User+ | Not exposed | ❌ | **ACTION NEEDED**: Add to service operations menu |

### ⚙️ Settings & Configuration

| Feature | API Route(s) | Frontend Component/Page | Required Role(s) | Current Access Path | Mega Menu Exposed | Notes |
|---------|-------------|------------------------|------------------|-------------------|------------------|-------|
| **General Settings** | `GET/PUT /api/v1/settings/*` | `/settings/Settings.tsx`<br>`/settings.tsx` | Org Admin+ | Settings menu | ✅ | Well integrated |
| **Voucher Settings** | `GET/PUT /api/v1/voucher-settings/*` | `/settings/voucher-settings.tsx` | Org Admin+ | Settings menu → Voucher Settings | ✅ | Organization-level voucher configuration |
| **Data Management** | `GET/PUT /api/v1/settings/data/*` | `/settings/DataManagement.tsx` | God Super Admin (naughtyfruit53@gmail.com) | Settings → Data Management | ✅ | Restricted to god superadmin only |
| **Factory Reset** | `POST /api/v1/settings/factory-reset` | `/settings/FactoryReset.tsx` | God Super Admin (naughtyfruit53@gmail.com) | Settings → Factory Reset | ✅ | Restricted to god superadmin only |
| **Pincode Services** | `GET /api/v1/pincode/*` | Embedded in forms | Org User+ | Within address forms | ❌ | Utility service, no UI needed |
| **PDF Extraction** | `POST /api/v1/pdf-extraction/*` | `ProductFileUpload.tsx` | Org User+ | Within product forms | ❌ | Embedded feature |
| **Company Audit Logs** | `GET /api/v1/audit/*` | Not exposed | Org Super Admin | Not accessible via UI | ❌ | **ACTION NEEDED**: Add to admin/audit section |
| **Excel Import/Export** | `GET/POST /api/v1/*/excel/*` | `ExcelImportExport.tsx`<br>`ExcelUploadComponent.tsx` | Org User+ | Within relevant pages | ❌ | Embedded in various forms |

### 🎮 Demo & Training

| Feature | API Route(s) | Frontend Component/Page | Required Role(s) | Current Access Path | Mega Menu Exposed | Notes |
|---------|-------------|------------------------|------------------|-------------------|------------------|-------|
| **Demo Mode** | Various demo endpoints | `/demo.tsx` | App Super Admin | Demo button in mega menu | ✅ | Available for app admins |
| **Notification Demo** | Demo endpoints | `/notification-demo.tsx` | Development | Direct URL | ❌ | Development feature demo |
| **UI Testing Pages** | N/A | `/ui-test.tsx`<br>`/floating-labels-test.tsx` | Development | Direct URLs | ❌ | Development tools |

### 📊 Dashboard Components

| Feature | API Route(s) | Frontend Component/Page | Required Role(s) | Current Access Path | Mega Menu Exposed | Notes |
|---------|-------------|------------------------|------------------|-------------------|------------------|-------|
| **App Super Admin Dashboard** | `GET /api/v1/platform/*` | `AppSuperAdminDashboard.tsx`<br>`/dashboard/index.tsx` | App Super Admin | `/dashboard` | ❌ | Platform-level metrics and overview |
| **Organization Dashboard** | Various org endpoints | `OrgDashboard.tsx`<br>`/dashboard/index.tsx` | Org User+ | `/dashboard` | ❌ | Business metrics and KPIs |
| **Alerts Feed** | `GET /api/v1/notifications/*` | `AlertsFeed.tsx` | Org User+ | Dashboard component | ❌ | Embedded in dashboard |
| **Balance Display** | `GET /api/v1/reports/balance/*` | `BalanceDisplay.tsx` | Org User+ | Dashboard component | ❌ | Financial summary widget |

## Summary of Issues & Recommendations

### ❌ Features Not Exposed in UI (Action Required)

1. **Service Analytics Suite** - Complete service analytics dashboard with job completion, technician performance, customer satisfaction, job volume, and SLA compliance charts
2. **Customer Analytics** - Business intelligence and customer insights should be accessible via Reports or dedicated Analytics menu
3. **Dispatch Management** - Service dispatch orders and installation job scheduling needs dedicated Service menu
4. **RBAC Management** - Service role and permission management interface needed in admin area
5. **Company Audit Logs** - Organization super admins need access to audit trail data
6. **Notification Management** - Admin features for notification templates and sending need proper access
7. **Stock Bulk Import** - Should be accessible in Inventory menu for efficient stock management
8. **Feedback Workflow** - Service closure and customer feedback system needs UI exposure

### 🔧 Recommended Menu Structure Improvements

#### For App Super Admins:
- **Dashboard** - Platform statistics, organization overview, system health
- **Organizations** - Organization management, licensing, and monitoring  
- **Users** - App-level user management across all organizations
- **Demo** - Training and demonstration environment
- **Settings** - System-wide configuration and preferences

#### For Organization Users:
- **Dashboard** - Business overview, KPIs, alerts, and balance summary
- **Masters** - All business entity management (current structure is good)
- **Vouchers** - All transaction types (current structure is comprehensive)
- **Inventory** - Stock and warehouse management (add bulk import feature)
- **Reports** - Financial and operational reports (current structure is good)
- **Analytics** - Customer insights and business intelligence (new)
- **Service** - Service CRM features (if organization uses service module)
  - Service Dashboard
  - Dispatch Management  
  - SLA Monitoring
  - Service Analytics
  - Feedback Management
- **Settings** - Organization configuration, user management, data management

#### For Service CRM Users (if applicable):
- **Service Dashboard** - Service metrics, job overview, performance KPIs
- **Dispatch** - Job dispatch, installation scheduling, order management
- **SLA** - Service level agreement monitoring and compliance tracking
- **Analytics** - Comprehensive service analytics suite
  - Job Completion Analytics
  - Technician Performance
  - Customer Satisfaction
  - Job Volume Analysis
  - SLA Compliance Reports
- **Feedback** - Customer feedback collection and service closure workflow
- **Admin** - RBAC management and service configuration (for service admins)

## Maintenance Guidelines

### When Adding New Features:

1. **Update this mapping** - Add new feature with all required details
2. **Determine RBAC requirements** - Define which roles can access the feature
3. **Plan UI integration** - Decide on menu placement and access path
4. **Update MegaMenu.tsx** - Add new menu items if needed
5. **Test role-based access** - Ensure proper permission enforcement
6. **Update documentation** - Reflect changes in user guides

### Regular Review Process:

1. **Monthly audit** - Review this mapping for accuracy
2. **Feature accessibility check** - Ensure all features are properly exposed
3. **User feedback integration** - Update based on usability feedback
4. **Role permission review** - Verify RBAC assignments are appropriate

---

**Last Updated**: December 2024  
**Next Review**: Monthly  
**Maintained By**: Development Team

> This document is the authoritative source for feature access mapping and must be updated with every feature addition or modification.