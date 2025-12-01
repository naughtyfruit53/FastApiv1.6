# TritIQ BOS - Complete Feature Guide

> **Comprehensive Feature Matrix for TritIQ Business Operating System**
> 
> This document provides a complete inventory of all features, modules, submodules, routes, services, and components available in the TritIQ BOS platform.

---

## Table of Contents

1. [Master Data Module](#1-master-data-module)
2. [Inventory Module](#2-inventory-module)
3. [Manufacturing Module](#3-manufacturing-module)
4. [Vouchers Module](#4-vouchers-module)
5. [Finance Module](#5-finance-module)
6. [Accounting Module](#6-accounting-module)
7. [Reports & Analytics Module](#7-reports--analytics-module)
8. [AI & Analytics Module](#8-ai--analytics-module)
9. [Sales Module (CRM)](#9-sales-module-crm)
10. [Marketing Module](#10-marketing-module)
11. [Service Module](#11-service-module)
12. [HR Management Module](#12-hr-management-module)
13. [Projects Module](#13-projects-module)
14. [Tasks & Calendar Module](#14-tasks--calendar-module)
15. [Email Module](#15-email-module)
16. [Settings & Administration](#16-settings--administration)
17. [Platform Administration](#17-platform-administration)
18. [Integration & External Services](#18-integration--external-services)
19. [Internal Utilities & Services](#19-internal-utilities--services)
20. [Mobile Features](#20-mobile-features)

---

## 1. Master Data Module

### Business Entities
| Feature | Route/Path | Backend API | Components |
|---------|------------|-------------|------------|
| Vendors | `/masters/vendors` | `/api/v1/vendors` | `AddVendorModal.tsx`, `VendorAutocomplete.tsx` |
| Customers | `/masters/customers` | `/api/v1/customers` | `AddCustomerModal.tsx`, `CustomerAutocomplete.tsx` |
| Employees | `/masters/employees` | `/api/v1/hr/*` | `AddEmployeeModal.tsx` |
| Company Details | `/masters/company-details` | `/api/v1/companies` | `CompanyDetailsModal.tsx` |

### Product & Inventory
| Feature | Route/Path | Backend API | Components |
|---------|------------|-------------|------------|
| Products | `/masters/products` | `/api/v1/products` | `AddProductModal.tsx`, `ProductAutocomplete.tsx`, `ProductDropdown.tsx` |
| Categories | `/masters/categories` | `/api/v1/admin_categories` | Category Management |
| Units | `/masters/units` | `/api/v1/master_data` | Unit Management |
| Bill of Materials (BOM) | `/masters/bom` | `/api/v1/bom` | `AddBOMModal.tsx`, `BOMConsumptionModal.tsx` |

### Financial Configuration
| Feature | Route/Path | Backend API | Components |
|---------|------------|-------------|------------|
| Chart of Accounts | `/masters/chart-of-accounts`, `/chart-of-accounts` | `/api/v1/chart_of_accounts` | `CoASelector.tsx`, `AddEditAccountModal.tsx` |
| Tax Codes | `/masters/tax-codes` | `/api/v1/gst` | GST Configuration |
| Payment Terms | `/masters/payment-terms` | `/api/v1/master_data` | Payment Terms Management |
| Bank Accounts | `/bank-accounts` | `/api/v1/accounts` | `BankAccountModal.tsx` |

### Backend Services
- `master_service.py` - Core master data operations
- `customer_analytics_service.py` - Customer analytics

---

## 2. Inventory Module

### Stock Management
| Feature | Route/Path | Backend API | Components |
|---------|------------|-------------|------------|
| Current Stock | `/inventory` | `/api/v1/stock`, `/api/v1/inventory` | `StockDisplay.tsx`, `StockBulkImport.tsx` |
| Stock Movements | `/inventory/movements` | `/api/v1/stock` | Stock Movement Reports |
| Low Stock Report | `/inventory/low-stock` | `/api/v1/inventory` | Low Stock Alerts |
| Pending Orders | `/inventory/pending-orders` | `/api/v1/order_book` | Pending Orders View |

### Warehouse Management
| Feature | Route/Path | Backend API | Components |
|---------|------------|-------------|------------|
| Locations | `/inventory/locations` | `/api/v1/warehouse` | Location Management |
| Bin Management | `/inventory/bins` | `/api/v1/warehouse` | Bin Configuration |
| Cycle Count | `/inventory/cycle-count` | `/api/v1/inventory` | Cycle Count Operations |

### Backend Services
- `inventory_service.py` - Inventory operations
- `stockService.ts` - Frontend stock service

---

## 3. Manufacturing Module

### Production Management
| Feature | Route/Path | Backend API | Components |
|---------|------------|-------------|------------|
| Order Book | `/order-book` | `/api/v1/order_book` | Order Book Dashboard |
| Production Order | `/vouchers/Manufacturing-Vouchers/production-order` | `/api/v1/manufacturing/manufacturing_orders` | Production Order Forms |
| Work Order | `/vouchers/Manufacturing-Vouchers/work-order` | `/api/v1/manufacturing/manufacturing_orders` | Work Order Management |
| Material Requisition | `/vouchers/Manufacturing-Vouchers/material-requisition` | `/api/v1/manufacturing/material_issue` | Material Requisition Forms |
| Finished Good Receipt | `/vouchers/Manufacturing-Vouchers/finished-good-receipt` | `/api/v1/manufacturing/fg_receipts` | FG Receipt Management |
| Job Card | `/vouchers/Manufacturing-Vouchers/job-card` | `/api/v1/manufacturing/job_cards` | `JobworkModal.tsx` |

### Jobwork Management
| Feature | Route/Path | Backend API | Components |
|---------|------------|-------------|------------|
| Inward Jobwork | `/manufacturing/jobwork/inward` | `/api/v1/manufacturing/*` | Inward Jobwork Forms |
| Outward Jobwork | `/manufacturing/jobwork/outward` | `/api/v1/manufacturing/*` | Outward Jobwork Forms |
| Jobwork Challan | `/manufacturing/jobwork/challan` | `/api/v1/manufacturing/*` | Challan Management |
| Jobwork Receipt | `/manufacturing/jobwork/receipt` | `/api/v1/manufacturing/*` | Receipt Management |

### Manufacturing Operations
| Feature | Route/Path | Backend API | Components |
|---------|------------|-------------|------------|
| Manufacturing Journal | `/vouchers/Manufacturing-Vouchers/manufacturing-journal` | `/api/v1/manufacturing/manufacturing_journals` | Journal Entry |
| Stock Journal | `/vouchers/Manufacturing-Vouchers/stock-journal` | `/api/v1/manufacturing/stock_journals` | Stock Adjustments |
| Material Receipt | `/vouchers/Manufacturing-Vouchers/material-receipt` | `/api/v1/manufacturing/material_receipt` | Material Receipt Forms |
| Production Entry | `/vouchers/Manufacturing-Vouchers/production-entry` | `/api/v1/manufacturing/production_entries` | Production Tracking |
| Inventory Adjustment | `/vouchers/Manufacturing-Vouchers/inventory-adjustment` | `/api/v1/manufacturing/inventory_adjustment` | Inventory Corrections |
| Maintenance | `/vouchers/Manufacturing-Vouchers/maintenance` | `/api/v1/manufacturing/maintenance` | Equipment Maintenance |

### Quality Control
| Feature | Route/Path | Backend API | Components |
|---------|------------|-------------|------------|
| Quality Inspection | `/manufacturing/quality/inspection` | `/api/v1/manufacturing/quality_control` | Quality Inspection Forms |
| Quality Reports | `/manufacturing/quality/reports` | `/api/v1/manufacturing/quality_control` | QC Reports |
| Inspection Plans | `/manufacturing/quality/inspection-plans` | `/api/v1/manufacturing/quality_control` | Inspection Plan Setup |
| Non-Conformance | `/manufacturing/quality/non-conformance` | `/api/v1/manufacturing/quality_control` | NCR Management |
| Acceptance | `/manufacturing/quality/acceptance` | `/api/v1/manufacturing/quality_control` | Acceptance Criteria |
| QC Voucher | `/vouchers/Manufacturing-Vouchers/quality-control` | `/api/v1/manufacturing/quality_control` | QC Documentation |

### Manufacturing Reports
| Feature | Route/Path | Backend API | Components |
|---------|------------|-------------|------------|
| Production Summary | `/manufacturing/reports/production-summary` | `/api/v1/manufacturing/analytics` | Production Analytics |
| Material Consumption | `/manufacturing/reports/material-consumption` | `/api/v1/manufacturing/analytics` | Material Usage Reports |
| Manufacturing Efficiency | `/manufacturing/reports/efficiency` | `/api/v1/manufacturing/analytics` | Efficiency Metrics |
| Department Allocations | `/manufacturing/department-allocations` | `/api/v1/manufacturing/*` | Allocation Management |

### Manufacturing Backend APIs
| API Endpoint | Description |
|--------------|-------------|
| `/api/v1/manufacturing/bom` | Bill of Materials operations |
| `/api/v1/manufacturing/mrp` | Material Requirements Planning |
| `/api/v1/manufacturing/production_planning` | Production planning service |
| `/api/v1/manufacturing/shop_floor` | Shop floor operations |
| `/api/v1/manufacturing/analytics` | Manufacturing analytics |

### Backend Services
- `mrp_service.py` - MRP calculations
- `production_planning_service.py` - Production scheduling
- `ManufacturingShortageAlert.tsx` - Stock shortage alerts

---

## 4. Vouchers Module

### Purchase Vouchers
| Feature | Route/Path | Backend API | Components |
|---------|------------|-------------|------------|
| Purchase Order | `/vouchers/Purchase-Vouchers/purchase-order` | `/api/v1/vouchers/purchase_order` | `VoucherLayout.tsx`, `VoucherItemTable.tsx` |
| GRN (Goods Received Note) | `/vouchers/Purchase-Vouchers/grn` | `/api/v1/vouchers/goods_receipt_note` | GRN Forms with QC Integration |
| Purchase Voucher | `/vouchers/Purchase-Vouchers/purchase-voucher` | `/api/v1/vouchers/purchase_voucher` | Purchase Invoice |
| Purchase Return | `/vouchers/Purchase-Vouchers/purchase-return` | `/api/v1/vouchers/purchase_return` | Return Processing |

### Pre-Sales Vouchers
| Feature | Route/Path | Backend API | Components |
|---------|------------|-------------|------------|
| Quotation | `/vouchers/Pre-Sales-Voucher/quotation` | `/api/v1/vouchers/quotation` | Quote Generation |
| Proforma Invoice | `/vouchers/Pre-Sales-Voucher/proforma-invoice` | `/api/v1/vouchers/proforma_invoice` | Proforma Management |
| Sales Order | `/vouchers/Pre-Sales-Voucher/sales-order` | `/api/v1/vouchers/sales_order` | Order Entry |

### Sales Vouchers
| Feature | Route/Path | Backend API | Components |
|---------|------------|-------------|------------|
| Sales Voucher | `/vouchers/Sales-Vouchers/sales-voucher` | `/api/v1/vouchers/sales_voucher` | Tax Invoice |
| Delivery Challan | `/vouchers/Sales-Vouchers/delivery-challan` | `/api/v1/vouchers/delivery_challan` | Delivery Documentation |
| Sales Return | `/vouchers/Sales-Vouchers/sales-return` | `/api/v1/vouchers/sales_return` | Return Processing |

### Financial Vouchers
| Feature | Route/Path | Backend API | Components |
|---------|------------|-------------|------------|
| Payment Voucher | `/vouchers/Financial-Vouchers/payment-voucher` | `/api/v1/vouchers/payment_voucher` | Payment Processing |
| Receipt Voucher | `/vouchers/Financial-Vouchers/receipt-voucher` | `/api/v1/vouchers/receipt_voucher` | Receipt Recording |
| Journal Voucher | `/vouchers/Financial-Vouchers/journal-voucher` | `/api/v1/vouchers/journal_voucher` | Journal Entries |
| Contra Voucher | `/vouchers/Financial-Vouchers/contra-voucher` | `/api/v1/vouchers/contra_voucher` | Bank/Cash Transfers |
| Credit Note | `/vouchers/Financial-Vouchers/credit-note` | `/api/v1/vouchers/credit_note` | Credit Adjustments |
| Debit Note | `/vouchers/Financial-Vouchers/debit-note` | `/api/v1/vouchers/debit_note` | Debit Adjustments |
| Non-Sales Credit Note | `/vouchers/Financial-Vouchers/non-sales-credit-note` | `/api/v1/vouchers/non_sales_credit_note` | Non-Sales Credits |

### Other Vouchers
| Feature | Route/Path | Backend API | Components |
|---------|------------|-------------|------------|
| RFQ (Request for Quotation) | `/vouchers/Others/rfq` | `/api/v1/procurement` | RFQ Management |
| Dispatch Details | `/vouchers/Others/dispatch-details` | `/api/v1/dispatch` | `DispatchManagement/` components |
| Inter Department Voucher | `/vouchers/Others/inter-department-voucher` | `/api/v1/vouchers/inter_department_voucher` | Inter-Dept Transfers |

### Voucher Components
- `VoucherLayout.tsx` - Common voucher layout
- `VoucherItemTable.tsx` - Line items table
- `VoucherFormTotals.tsx` - Total calculations
- `VoucherHeaderActions.tsx` - Header action buttons
- `VoucherContextMenu.tsx` - Right-click actions
- `VoucherPDFButton.tsx` - PDF generation
- `VoucherPageWithPDF.tsx` - PDF preview
- `VoucherListModal.tsx` - Voucher selection
- `VoucherReferenceDropdown.tsx` - Reference linking
- `VoucherDateConflictModal.tsx` - Date conflict resolution
- `CreateVoucherButton.tsx` - Quick create button
- `AdditionalCharges.tsx` - Additional charges management
- `InwardMaterialQCModal.tsx` - QC integration for GRN

### Backend Services
- `voucher_service.py` - Core voucher operations
- `vouchersService.ts` - Frontend voucher service

---

## 5. Finance Module

### Accounts Payable
| Feature | Route/Path | Backend API | Components |
|---------|------------|-------------|------------|
| Vendor Bills | `/accounts-payable` | `/api/v1/accounts` | AP Dashboard |
| Payment Vouchers | `/vouchers/Financial-Vouchers/payment-voucher` | `/api/v1/vouchers/payment_voucher` | Payment Processing |
| Vendor Aging | `/vendor-aging` | `/api/v1/reports` | Aging Reports |

### Accounts Receivable
| Feature | Route/Path | Backend API | Components |
|---------|------------|-------------|------------|
| Customer Invoices | `/accounts-receivable` | `/api/v1/accounts` | AR Dashboard |
| Receipt Vouchers | `/vouchers/Financial-Vouchers/receipt-voucher` | `/api/v1/vouchers/receipt_voucher` | Receipt Processing |
| Customer Aging | `/customer-aging` | `/api/v1/reports` | Aging Reports |

### Cost Management
| Feature | Route/Path | Backend API | Components |
|---------|------------|-------------|------------|
| Cost Centers | `/cost-centers` | `/api/v1/expense_account` | Cost Center Setup |
| Budget Management | `/budgets`, `/budget-management` | `/api/v1/finance_analytics` | Budget Tracking |
| Cost Analysis | `/cost-analysis` | `/api/v1/finance_analytics` | Cost Analytics |

### Financial Reports
| Feature | Route/Path | Backend API | Components |
|---------|------------|-------------|------------|
| Cash Flow | `/reports/cash-flow` | `/api/v1/reports` | Cash Flow Statement |
| Cash Flow Forecast | `/cash-flow-forecast` | `/api/v1/forecasting` | Forecasting Dashboard |
| Financial Reports Hub | `/financial-reports` | `/api/v1/finance_analytics` | Report Center |

### Analytics & KPIs
| Feature | Route/Path | Backend API | Components |
|---------|------------|-------------|------------|
| Finance Dashboard | `/finance-dashboard` | `/api/v1/finance_analytics` | Financial Overview |
| Financial KPIs | `/financial-kpis` | `/api/v1/finance_analytics` | KPI Metrics |
| Expense Analysis | `/expense-analysis` | `/api/v1/expense_account` | Expense Breakdown |

---

## 6. Accounting Module

### Chart of Accounts
| Feature | Route/Path | Backend API | Components |
|---------|------------|-------------|------------|
| Chart of Accounts | `/masters/chart-of-accounts` | `/api/v1/chart_of_accounts` | Account Tree |
| Account Groups | `/account-groups` | `/api/v1/accounts` | Group Management |
| Opening Balances | `/opening-balances` | `/api/v1/accounts` | Balance Entry |

### Transactions
| Feature | Route/Path | Backend API | Components |
|---------|------------|-------------|------------|
| General Ledger | `/general-ledger` | `/api/v1/ledger` | Ledger View |
| Journal Entries | `/vouchers/Financial-Vouchers/journal-voucher` | `/api/v1/vouchers/journal_voucher` | Manual Journals |
| Bank Reconciliation | `/bank-reconciliation` | `/api/v1/accounts` | Reconciliation Tool |

### Financial Reports
| Feature | Route/Path | Backend API | Components |
|---------|------------|-------------|------------|
| Trial Balance | `/reports/trial-balance` | `/api/v1/reports` | Trial Balance |
| Profit & Loss | `/reports/profit-loss` | `/api/v1/reports` | P&L Statement |
| Balance Sheet | `/reports/balance-sheet` | `/api/v1/reports` | Balance Sheet |
| Ledgers | `/reports/ledgers` | `/api/v1/ledger` | Account Ledgers |

### Backend Services
- `ledger_service.py` - Ledger operations
- `ledgerService.ts` - Frontend ledger service

---

## 7. Reports & Analytics Module

### Financial Reports
| Feature | Route/Path | Backend API | Components |
|---------|------------|-------------|------------|
| Ledgers | `/reports/ledgers` | `/api/v1/ledger` | Ledger Reports |
| Trial Balance | `/reports/trial-balance` | `/api/v1/reports` | Balance Reports |
| Profit & Loss | `/reports/profit-loss` | `/api/v1/reports` | Income Statement |
| Balance Sheet | `/reports/balance-sheet` | `/api/v1/reports` | Position Statement |

### Inventory Reports
| Feature | Route/Path | Backend API | Components |
|---------|------------|-------------|------------|
| Stock Report | `/reports/stock` | `/api/v1/reports` | Stock Reports |
| Valuation Report | `/reports/valuation` | `/api/v1/reports` | Inventory Valuation |
| Movement Report | `/reports/movements` | `/api/v1/reports` | Stock Movements |

### Business Reports
| Feature | Route/Path | Backend API | Components |
|---------|------------|-------------|------------|
| Sales Analysis | `/reports/sales-analysis` | `/api/v1/reports` | Sales Analytics |
| Purchase Analysis | `/reports/purchase-analysis` | `/api/v1/reports` | Purchase Analytics |
| Vendor Analysis | `/reports/vendor-analysis` | `/api/v1/reports` | Vendor Performance |

### Business Analytics
| Feature | Route/Path | Backend API | Components |
|---------|------------|-------------|------------|
| Customer Analytics | `/reports/customer-analytics` | `/api/v1/customer_analytics` | `CustomerAnalytics.tsx`, `CustomerAnalyticsModal.tsx` |
| Sales Analytics | `/reports/sales-analytics`, `/analytics/sales` | `/api/v1/reports` | Sales Insights |
| Purchase Analytics | `/reports/purchase-analytics`, `/analytics/purchase` | `/api/v1/reports` | Purchase Insights |
| Customer Analytics Page | `/analytics/customer` | `/api/v1/customer_analytics` | Customer Insights |

### Service Analytics
| Feature | Route/Path | Backend API | Components |
|---------|------------|-------------|------------|
| Service Dashboard | `/analytics/service` | `/api/v1/service_analytics` | `ServiceAnalytics/` components |
| Job Completion | `/analytics/service/job-completion` | `/api/v1/service_analytics` | Job Analytics |
| Technician Performance | `/analytics/service/technician-performance` | `/api/v1/service_analytics` | Performance Metrics |
| Customer Satisfaction | `/analytics/service/customer-satisfaction` | `/api/v1/service_analytics` | CSAT Analytics |
| SLA Compliance | `/analytics/service/sla-compliance` | `/api/v1/sla` | SLA Reports |

### Management Reports
| Feature | Route/Path | Backend API | Components |
|---------|------------|-------------|------------|
| System Reports | `/reports` | `/api/v1/reports` | Report Hub |
| Management Dashboard | `/management/dashboard` | `/api/v1/management_reports` | Executive View |
| Reporting Hub | `/reporting-hub` | `/api/v1/reporting_hub` | Centralized Reports |

### Backend Services
- `reportsService.ts` - Frontend reports service
- `service_analytics_service.py` - Service analytics

---

## 8. AI & Analytics Module

### AI Assistant
| Feature | Route/Path | Backend API | Components |
|---------|------------|-------------|------------|
| AI Chatbot | `/ai-chatbot` | `/api/v1/chatbot`, `/api/v1/ai` | `ChatbotWidget.tsx`, `ChatbotNavigator.tsx` |
| AI Help & Guidance | `/ai/help` | `/api/v1/ai` | AI Help Page |
| Business Advisor | `/ai/advisor` | `/api/v1/ai_analytics` | AI Advisory |

### Advanced Analytics
| Feature | Route/Path | Backend API | Components |
|---------|------------|-------------|------------|
| Analytics Dashboard | `/analytics/advanced-analytics` | `/api/v1/ai_analytics` | Advanced Dashboard |
| Predictive Analytics | `/ai-analytics` | `/api/v1/ai_analytics` | `PredictiveDashboard.tsx`, `LiveAnalyticsDashboard.tsx` |
| Streaming Analytics | `/analytics/streaming-dashboard` | `/api/v1/streaming_analytics` | Real-time Analytics |
| AutoML Platform | `/analytics/automl` | `/api/v1/automl` | ML Model Building |

### AI Tools
| Feature | Route/Path | Backend API | Components |
|---------|------------|-------------|------------|
| A/B Testing | `/analytics/ab-testing` | `/api/v1/ab_testing` | Experiment Management |
| Model Explainability | `/ai/explainability` | `/api/v1/explainability` | `ExplainabilityDashboard.tsx` |
| Website Agent | `/service/website-agent` | `/api/v1/website_agent` | `WebsiteAgentWizard.tsx` |

### AI Backend APIs
| API Endpoint | Description |
|--------------|-------------|
| `/api/v1/ai` | Core AI operations |
| `/api/v1/ai_agents` | AI agent management |
| `/api/v1/ai_analytics` | AI-powered analytics |
| `/api/v1/ml_algorithms` | ML algorithm execution |
| `/api/v1/ml_analytics` | ML model analytics |

### Backend Services
- `ai_service.py` - Core AI service
- `ai_agents_service.py` - AI agents management
- `ai_analytics_service.py` - AI analytics
- `automl_service.py` - AutoML functionality
- `ml_algorithms_service.py` - ML algorithms
- `ml_analytics_service.py` - ML analytics
- `explainability_service.py` - Model explanations
- `forecasting_service.py` - Prediction models
- `streaming_analytics_service.py` - Real-time analytics
- `ab_testing_service.py` - A/B testing
- `advanced_analytics_service.py` - Advanced analytics

---

## 9. Sales Module (CRM)

### Sales CRM
| Feature | Route/Path | Backend API | Components |
|---------|------------|-------------|------------|
| Sales Dashboard | `/sales/dashboard` | `/api/v1/crm` | CRM Dashboard |
| Lead Management | `/sales/leads` | `/api/v1/crm` | `AddLeadModal.tsx`, `LeadsImportExportDropdown.tsx` |
| Opportunity Tracking | `/sales/opportunities` | `/api/v1/crm` | `AddOpportunityModal.tsx` |
| Sales Pipeline | `/sales/pipeline` | `/api/v1/crm` | Pipeline View |
| Exhibition Mode | `/exhibition-mode` | `/api/v1/exhibition` | Exhibition Lead Capture |

### Customer Management
| Feature | Route/Path | Backend API | Components |
|---------|------------|-------------|------------|
| Customer Database | `/sales/customers` | `/api/v1/customers` | Customer List |
| Contact Management | `/sales/contacts` | `/api/v1/contacts` | `AddContactModal.tsx` |
| Account Management | `/sales/accounts` | `/api/v1/accounts` | Account View |
| Customer Analytics | `/sales/customer-analytics` | `/api/v1/customer_analytics` | Customer Insights |

### Sales Operations
| Feature | Route/Path | Backend API | Components |
|---------|------------|-------------|------------|
| Quotations | `/vouchers/Pre-Sales-Voucher/quotation` | `/api/v1/vouchers/quotation` | Quote Management |
| Sales Orders | `/vouchers/Pre-Sales-Voucher/sales-order` | `/api/v1/vouchers/sales_order` | Order Entry |
| Commission Tracking | `/sales/commissions` | `/api/v1/crm` | `AddCommissionModal.tsx` |
| Sales Reports | `/sales/reports` | `/api/v1/reports` | Sales Reporting |

### CRM Page
| Feature | Route/Path | Backend API | Components |
|---------|------------|-------------|------------|
| CRM Hub | `/crm` | `/api/v1/crm` | CRM Overview |

### Backend Services
- `crmService.ts` - Frontend CRM service
- `exhibition_service.py` - Exhibition mode
- `customer_analytics_service.py` - Customer analytics

---

## 10. Marketing Module

### Campaign Management
| Feature | Route/Path | Backend API | Components |
|---------|------------|-------------|------------|
| Marketing Dashboard | `/marketing` | `/api/v1/marketing` | Marketing Overview |
| Campaigns | `/marketing/campaigns` | `/api/v1/marketing` | Campaign Management |
| Email Campaigns | `/marketing/campaigns/email` | `/api/v1/mail` | Email Marketing |
| SMS Campaigns | `/marketing/campaigns/sms` | `/api/v1/marketing` | SMS Marketing |
| Social Media | `/marketing/campaigns/social` | `/api/v1/marketing` | Social Marketing |

### Promotions & Offers
| Feature | Route/Path | Backend API | Components |
|---------|------------|-------------|------------|
| Promotions | `/marketing/promotions` | `/api/v1/marketing` | Promotion Setup |
| Discount Codes | `/marketing/discount-codes` | `/api/v1/marketing` | Discount Management |
| Promotion Analytics | `/marketing/promotion-analytics` | `/api/v1/marketing` | Promo Performance |

### Customer Engagement
| Feature | Route/Path | Backend API | Components |
|---------|------------|-------------|------------|
| Marketing Lists | `/marketing/lists` | `/api/v1/marketing` | List Management |
| Segmentation | `/marketing/segmentation` | `/api/v1/marketing` | Customer Segments |
| Campaign Analytics | `/marketing/analytics` | `/api/v1/marketing` | Campaign Performance |
| ROI Reports | `/marketing/reports/roi` | `/api/v1/marketing` | ROI Analysis |

### Backend Services
- `marketingService.ts` - Frontend marketing service

---

## 11. Service Module

### Helpdesk & Ticketing
| Feature | Route/Path | Backend API | Components |
|---------|------------|-------------|------------|
| Helpdesk Dashboard | `/service-desk` | `/api/v1/service_desk` | Service Desk Overview |
| Tickets | `/service-desk/tickets` | `/api/v1/service_desk` | `CreateTicketModal.tsx` |
| SLA Management | `/service-desk/sla`, `/sla` | `/api/v1/sla` | `SLAStatus.tsx` |
| Escalations | `/service-desk/escalations` | `/api/v1/service_desk` | Escalation Rules |
| Chat | `/service-desk/chat` | `/api/v1/service_desk` | Live Chat |

### Service CRM
| Feature | Route/Path | Backend API | Components |
|---------|------------|-------------|------------|
| Service CRM Dashboard | `/service/dashboard` | `/api/v1/service_desk` | Service Overview |
| Dispatch Management | `/service/dispatch` | `/api/v1/dispatch` | `DispatchManagement/` |
| Feedback Workflow | `/service/feedback` | `/api/v1/feedback` | `FeedbackWorkflow/` |
| Service Permissions | `/service/permissions` | `/api/v1/rbac` | `ServiceRoleGate.tsx` |
| Technicians | `/service/technicians` | `/api/v1/service_desk` | Technician Management |
| Website Agent | `/service/website-agent` | `/api/v1/website_agent` | `WebsiteAgentWizard.tsx` |

### Backend Services
- `service_desk_service.py` - Service desk operations
- `dispatch_service.py` - Dispatch management
- `feedback_service.py` - Feedback collection
- `sla.py` - SLA calculations
- `serviceDeskService.ts` - Frontend service
- `slaService.ts` - Frontend SLA service
- `service_analytics_service.py` - Service analytics

---

## 12. HR Management Module

### Employee Management
| Feature | Route/Path | Backend API | Components |
|---------|------------|-------------|------------|
| Employee Directory | `/hr/employees-directory` | `/api/v1/hr/hr_core` | Employee List |
| Employee Records | `/hr/employees` | `/api/v1/hr/hr_core` | Employee Details |
| Employee Onboarding | `/hr/onboarding` | `/api/v1/hr/hr_core` | Onboarding Workflow |
| Self-Service | `/hr/self-service` | `/api/v1/hr/hr_core` | Employee Self-Service |

### Performance Management
| Feature | Route/Path | Backend API | Components |
|---------|------------|-------------|------------|
| Performance Dashboard | `/hr/performance` | `/api/v1/hr/hr_performance` | Performance Overview |
| Goals & OKRs | `/hr/goals` | `/api/v1/hr/hr_performance` | Goal Setting |
| Review Cycles | `/hr/review-cycles` | `/api/v1/hr/hr_performance` | Review Management |
| 360 Feedback | `/hr/feedback` | `/api/v1/hr/hr_performance` | Multi-rater Feedback |

### Payroll & Benefits
| Feature | Route/Path | Backend API | Components |
|---------|------------|-------------|------------|
| Payroll Management | `/hr/payroll` | `/api/v1/payroll` | Payroll Processing |
| Salary Processing | `/hr/salary` | `/api/v1/payroll` | Salary Calculations |
| Benefits Administration | `/hr/benefits` | `/api/v1/payroll` | Benefits Management |
| Tax Management | `/hr/tax` | `/api/v1/payroll` | Tax Calculations |
| Payroll Components | N/A | `/api/v1/payroll_components`, `/api/v1/payroll_components_advanced` | `PayrollComponentSettings.tsx` |
| Payroll GL Integration | N/A | `/api/v1/payroll_gl` | GL Posting |
| Payroll Migration | N/A | `/api/v1/payroll_migration` | Data Migration |
| Payroll Monitoring | N/A | `/api/v1/payroll_monitoring` | Monitoring Dashboard |

### Time & Attendance
| Feature | Route/Path | Backend API | Components |
|---------|------------|-------------|------------|
| Time Tracking | `/hr/timesheet` | `/api/v1/hr/hr_attendance` | Timesheet Entry |
| Leave Management | `/hr/leave` | `/api/v1/hr/hr_leave` | Leave Applications |
| Attendance Reports | `/hr/attendance` | `/api/v1/hr/hr_attendance` | Attendance Reports |
| Shift Management | `/hr/shifts` | `/api/v1/hr/hr_attendance` | Shift Scheduling |

### Recruitment
| Feature | Route/Path | Backend API | Components |
|---------|------------|-------------|------------|
| Job Postings | `/hr/jobs` | `/api/v1/hr/hr_recruitment` | Job Management |
| Candidate Pipeline | `/hr/candidates` | `/api/v1/hr/hr_recruitment` | Applicant Tracking |
| Interview Scheduling | `/hr/interviews` | `/api/v1/hr/hr_recruitment` | Interview Management |
| Job Offers | `/hr/offers` | `/api/v1/hr/hr_recruitment` | Offer Letters |
| Hiring Pipeline | `/hr/hiring` | `/api/v1/hr/hr_recruitment` | Hiring Workflow |

### Compliance & Policies
| Feature | Route/Path | Backend API | Components |
|---------|------------|-------------|------------|
| Policy Documents | `/hr/policies` | `/api/v1/hr/hr_compliance` | Policy Management |
| Training Programs | `/hr/training` | `/api/v1/hr/hr_compliance` | Training Management |
| Compliance Dashboard | `/hr/compliance-dashboard` | `/api/v1/hr/hr_compliance` | Compliance Overview |

### HR Analytics
| Feature | Route/Path | Backend API | Components |
|---------|------------|-------------|------------|
| HR Analytics Dashboard | `/hr/analytics` | `/api/v1/hr/hr_advanced` | HR Metrics |
| Workforce Analytics | `/hr/workforce-analytics` | `/api/v1/hr/hr_advanced` | Workforce Insights |
| Audit Exports | `/hr/compliance-exports` | `/api/v1/hr/hr_exports` | Export Functions |

### Backend Services
- `hrService.ts` - Frontend HR service

---

## 13. Projects Module

### Project Management
| Feature | Route/Path | Backend API | Components |
|---------|------------|-------------|------------|
| All Projects | `/projects` | `/api/v1/project_management` | Project List |
| Project Planning | `/projects/planning` | `/api/v1/project_management` | Project Planning |
| Resource Management | `/projects/resources` | `/api/v1/project_management` | Resource Allocation |
| Document Management | `/projects/documents` | `/api/v1/project_management` | Project Documents |

### Analytics & Reporting
| Feature | Route/Path | Backend API | Components |
|---------|------------|-------------|------------|
| Project Analytics | `/projects/analytics` | `/api/v1/project_management` | Project Metrics |

---

## 14. Tasks & Calendar Module

### Tasks
| Feature | Route/Path | Backend API | Components |
|---------|------------|-------------|------------|
| Task Dashboard | `/tasks/dashboard` | `/api/v1/tasks` | Task Overview |
| My Tasks | `/tasks` | `/api/v1/tasks` | Task List |
| Create Task | `/tasks/create` | `/api/v1/tasks` | Task Creation |
| Task Assignments | `/tasks/assignments` | `/api/v1/tasks` | Assignment Management |

### Calendar
| Feature | Route/Path | Backend API | Components |
|---------|------------|-------------|------------|
| Calendar Dashboard | `/calendar/dashboard` | `/api/v1/calendar` | Calendar Overview |
| Calendar View | `/calendar` | `/api/v1/calendar` | Full Calendar |
| My Events | `/calendar/events` | `/api/v1/calendar` | Event List |
| Create Event | `/calendar/create` | `/api/v1/calendar` | Event Creation |

### Backend Services
- `calendar_sync_service.py` - Calendar synchronization

---

## 15. Email Module

### Email Management
| Feature | Route/Path | Backend API | Components |
|---------|------------|-------------|------------|
| Inbox | `/email` | `/api/v1/email` | `email/Inbox.tsx` |
| Compose | `/email?compose=true` | `/api/v1/email` | `email/Composer.tsx` |
| Thread View | `/email/thread/[id]` | `/api/v1/email` | `email/ThreadView.tsx` |
| Email Dashboard | `/email/dashboard` | `/api/v1/email` | Email Overview |

### Email Settings
| Feature | Route/Path | Backend API | Components |
|---------|------------|-------------|------------|
| Account Settings | `/email/accounts` | `/api/v1/email` | Account Configuration |
| OAuth Connections | `/email/oauth` | `/api/v1/oauth` | OAuth Setup |
| Sync Status | `/email/sync` | `/api/v1/email` | Sync Monitoring |
| Email Templates | `/email/templates` | `/api/v1/voucher_email_templates` | Template Management |

### Email Components
- `EmailAttachmentDisplay.tsx` - Attachment handling
- `email/` page components

### Backend Services
- `email_sync_service.py` - Email synchronization
- `email_sync_worker.py` - Background sync
- `email_api_sync_service.py` - API-based sync
- `email_search_service.py` - Email search
- `email_ai_service.py` - AI email features
- `email_templates.py` - Email templates
- `system_email_service.py` - System emails
- `user_email_service.py` - User email operations
- `emailService.ts` - Frontend email service

---

## 16. Settings & Administration

### Organization Settings
| Feature | Route/Path | Backend API | Components |
|---------|------------|-------------|------------|
| General Settings | `/settings/general-settings` | `/api/v1/settings` | `OrganizationSettings.tsx` |
| Company Profile | `/settings/company` | `/api/v1/companies` | Company Configuration |
| Voucher Settings | `/settings/voucher-settings` | `/api/v1/voucher_format_templates` | Voucher Customization |
| Data Management | `/settings/DataManagement` | `/api/v1/reset` | Data Operations |
| Factory Reset | `/settings/FactoryReset` | `/api/v1/reset` | `FactoryReset.tsx`, `ResetDialog.tsx` |

### User Management
| Feature | Route/Path | Backend API | Components |
|---------|------------|-------------|------------|
| User Management | `/settings/user-management` | `/api/v1/org_user_management` | User Admin |
| User Permissions | `/settings/user-permissions/[userId]` | `/api/v1/rbac` | Permission Editor |
| Role Management | `/admin/rbac`, `/RoleManagement/RoleManagement` | `/api/v1/rbac` | `RoleManagement/` |
| App Users | `/admin/app-user-management` | `/api/v1/app_users` | App User Admin |

### Administration
| Feature | Route/Path | Backend API | Components |
|---------|------------|-------------|------------|
| Admin Dashboard | `/admin` | `/api/v1/admin` | Admin Overview |
| Audit Logs | `/admin/audit-logs` | `/api/v1/audit_log` | `AuditLogViewer.tsx` |
| Notification Management | `/admin/notifications` | `/api/v1/notifications` | Notification Admin |
| Service Settings | `/admin/service-settings` | `/api/v1/settings` | Service Config |
| Admin Users | `/admin/users` | `/api/v1/admin` | Admin User Management |

### System Utilities
| Feature | Route/Path | Backend API | Components |
|---------|------------|-------------|------------|
| System Reports | `/reports` | `/api/v1/reports` | Report Hub |
| Migration Management | `/migration/management` | `/api/v1/migration` | `MigrationWizard.tsx` |
| UI Testing | `/ui-test` | N/A | UI Test Page |
| Notification Demo | `/notification-demo` | `/api/v1/notifications` | Notification Testing |
| Transport Management | `/transport` | `/api/v1/transport` | Transport Config |
| Assets Management | `/assets` | `/api/v1/assets` | Asset Tracking |

### Backend Services
- `rbac.py`, `rbac_enhanced.py`, `rbac_permissions.py` - RBAC services
- `user_rbac_service.py` - User RBAC
- `role_management_service.py` - Role management
- `role_hierarchy_service.py` - Role hierarchy
- `reset_service.py`, `org_reset_service.py` - Reset operations
- `migration_service.py` - Data migration
- `notification_service.py`, `enhanced_notification_service.py` - Notifications
- `adminService.ts`, `rbacService.ts` - Frontend services

---

## 17. Platform Administration

### Organization Management
| Feature | Route/Path | Backend API | Components |
|---------|------------|-------------|------------|
| Manage Organizations | `/admin/manage-organizations` | `/api/v1/organizations/*` | Org Management |
| Organization List | `/admin/organizations` | `/api/v1/organizations/routes` | `OrganizatonList.tsx` |
| Create Organization | `/admin/organizations/create` | `/api/v1/organizations/routes` | `OrganizationForm.tsx` |
| Organization Details | `/admin/organizations/[id]` | `/api/v1/organizations/routes` | Org Detail View |
| License Management | `/admin/license-management` | `/api/v1/organizations/license_routes` | `CreateOrganizationLicenseModal.tsx` |

### Platform APIs
| API Endpoint | Description |
|--------------|-------------|
| `/api/v1/organizations/routes` | Core organization CRUD |
| `/api/v1/organizations/user_routes` | Organization user management |
| `/api/v1/organizations/module_routes` | Module enablement |
| `/api/v1/organizations/settings_routes` | Organization settings |
| `/api/v1/organizations/license_routes` | License management |
| `/api/v1/organizations/invitation_routes` | User invitations |
| `/api/v1/platform` | Platform administration |
| `/api/v1/entitlements` | Entitlement management |
| `/api/v1/admin_entitlements` | Admin entitlements |

### Backend Services
- `organization_service.py` - Organization operations
- `org_cache_service.py` - Organization caching
- `org_role_service.py` - Organization roles
- `entitlement_service.py` - Entitlements
- `organizationService.ts` - Frontend org service
- `entitlementsApi.ts` - Entitlements API

---

## 18. Integration & External Services

### Integrations Dashboard
| Feature | Route/Path | Backend API | Components |
|---------|------------|-------------|------------|
| Integration Dashboard | `/integrations` | `/api/v1/integration` | `IntegrationDashboard.tsx` |
| Integration Settings | N/A | `/api/v1/integration_settings` | Settings Management |
| Plugins | `/plugins` | `/api/v1/plugin` | Plugin Management |

### External Integrations
| Feature | Backend API | Description |
|---------|-------------|-------------|
| Tally Integration | `/api/v1/tally` | Tally ERP sync |
| AfterShip Integration | `/api/v1/external_integrations` | Shipping tracking |
| WhatsApp Integration | `whatsapp_service.py` | WhatsApp messaging |
| OAuth Providers | `/api/v1/oauth` | OAuth authentication |
| Pincode Lookup | `/api/v1/pincode` | Address validation |

### Backend Services
- `integration_service.py` - Integration hub
- `external_integrations_service.py` - External APIs
- `tally_service.py` - Tally integration
- `oauth_service.py` - OAuth handling
- `whatsapp_service.py` - WhatsApp
- `tallyService.ts`, `integrationService.ts` - Frontend services
- `integration/` service directory

---

## 19. Internal Utilities & Services

### Authentication & Security
| Feature | Backend API | Components |
|---------|-------------|------------|
| Authentication | `/api/v1/auth`, `/api/v1/login` | `AuthProvider.tsx`, `LoginForm.tsx`, `UnifiedLoginForm.tsx` |
| OTP Login | `/api/v1/otp` | `OTPLogin.tsx` |
| OAuth Login | `/api/v1/oauth` | `OAuthLoginButton.tsx` |
| Biometric Login | N/A | `BiometricLoginButton.tsx` |
| Password Reset | `/api/v1/password` | `ForgotPasswordModal.tsx`, `PasswordChangeModal.tsx` |
| Master Auth | `/api/v1/master_auth` | Master authentication |

### Document Services
| Feature | Backend API | Components |
|---------|-------------|------------|
| PDF Generation | `/api/v1/pdf_generation` | PDF creation |
| PDF Extraction | `/api/v1/pdf_extraction` | `PDFSystemStatus.tsx` |
| Excel Import/Export | `excel_service.py` | `ExcelImportExport.tsx`, `ExcelUploadComponent.tsx`, `BulkImportExportProgressBar.tsx` |

### User Interface Components
| Component | Description |
|-----------|-------------|
| `MegaMenu.tsx` | Main navigation menu |
| `MobileNav.tsx` | Mobile navigation drawer |
| `AppLayout.tsx` | Main application layout |
| `DashboardLayout.tsx` | Dashboard layout |
| `DashboardWidget.tsx` | Widget components |
| `ModernLoading.tsx` | Loading states |
| `ModernChart.tsx` | Chart components |
| `MetricCard.tsx` | Metric display |
| `ErrorBoundary.tsx` | Error handling |
| `ProtectedPage.tsx` | Route protection |
| `RoleGate.tsx` | Role-based access |
| `SortableTable.tsx` | Data tables |
| `SearchableDropdown.tsx` | Search dropdowns |
| `EntitySelector.tsx` | Entity selection |
| `BalanceDisplay.tsx` | Balance formatting |

### Onboarding & Help
| Feature | Components |
|---------|------------|
| Demo Mode | `DemoModeDialog.tsx`, `DemoOnboarding.tsx` |
| Interactive Tutorial | `InteractiveTutorial.tsx` |
| Onboarding Tour | `OnboardingTour.tsx` |
| Role Onboarding | `RoleOnboarding.tsx` |
| First Login Setup | `FirstLoginSetupWrapper.tsx` |
| Company Setup Guard | `CompanySetupGuard.tsx` |
| Module Selection | `ModuleSelectionModal.tsx` |
| Help Page | `/help` |

### Notifications
| Feature | Backend API | Components |
|---------|-------------|------------|
| Notification Bell | `/api/v1/notifications` | `NotificationBell.tsx` |
| Notification Dashboard | `/api/v1/notifications` | `NotificationDashboard.tsx` |
| Notification Settings | `/api/v1/notifications` | `NotificationSettings.tsx`, `NotificationSettingsModal.tsx` |
| Notification Templates | `/api/v1/notifications` | `NotificationTemplates.tsx` |
| Notification Logs | `/api/v1/notifications` | `NotificationLogs.tsx` |
| Send Notification | `/api/v1/notifications` | `SendNotification.tsx` |

### Progressive Web App
| Feature | Components |
|---------|------------|
| PWA Install | `PWAInstallPrompt.tsx` |
| Update Prompt | `UpdatePrompt.tsx` |
| Offline Indicator | `OfflineIndicator.tsx` |

### Organization Management Components
| Component | Description |
|-----------|-------------|
| `OrganizationSwitcher.tsx` | Multi-org switching |
| `OrganizationMembersDialog.tsx` | Member management |
| `CreateOrganizationLicenseModal.tsx` | License creation |
| `AddUserDialog.tsx` | User addition |
| `AdminUserForm.tsx` | Admin user form |
| `SuspendDialog.tsx` | User suspension |

### Workflow & Approvals
| Feature | Backend API | Description |
|---------|-------------|-------------|
| Workflow Approval | `/api/v1/workflow_approval` | Approval workflows |
| Role Delegation | `/api/v1/role_delegation` | Permission delegation |

### Backend Core Services
| Service | Description |
|---------|-------------|
| `user_service.py` | User operations |
| `demo_user_service.py` | Demo user handling |
| `otp_service.py` | OTP generation |
| `ocr_service.py` | OCR processing |
| `localization_service.py` | i18n support |
| `seo_service.py` | SEO optimization |
| `performance_optimizer.py` | Performance tuning |
| `security_services.py`, `security_enhancements.py` | Security features |
| `permission_enforcement.py` | Permission checking |
| `automation_workflow_engine.py` | Workflow automation |
| `dependencies.py` | Service dependencies |

---

## 20. Mobile Features

### Mobile Pages
| Feature | Route/Path | Description |
|---------|------------|-------------|
| Mobile Dashboard | `/mobile/dashboard` | Mobile dashboard view |
| Mobile Sales | `/mobile/sales` | Sales on mobile |
| Mobile Finance | `/mobile/finance` | Finance on mobile |
| Mobile CRM | `/mobile/crm` | CRM on mobile |
| Mobile Inventory | `/mobile/inventory` | Inventory on mobile |
| Mobile HR | `/mobile/hr` | HR on mobile |
| Mobile Service | `/mobile/service` | Service on mobile |
| Mobile Reports | `/mobile/reports` | Reports on mobile |
| Mobile Marketing | `/mobile/marketing` | Marketing on mobile |
| Mobile Projects | `/mobile/projects` | Projects on mobile |
| Mobile Settings | `/mobile/settings` | Settings on mobile |
| Mobile Admin | `/mobile/admin` | Admin on mobile |
| Mobile AI Chatbot | `/mobile/ai-chatbot` | AI Chatbot on mobile |
| Mobile Integrations | `/mobile/integrations` | Integrations on mobile |
| Mobile Plugins | `/mobile/plugins` | Plugins on mobile |
| Mobile Login | `/mobile/login` | Mobile login |

### Mobile Components
| Component | Description |
|-----------|-------------|
| `MobileLayout.tsx` | Mobile app layout |
| `MobileNavigation.tsx` | Mobile navigation |
| `MobileNav.tsx` | Mobile nav drawer |
| `MobileBottomNav.tsx` | Bottom tab navigation |
| `MobileDrawerNavigation.tsx` | Enhanced drawer nav |
| `MobileDashboardLayout.tsx` | Dashboard layout |
| `MobileFormLayout.tsx` | Form layout |
| `MobileHeader.tsx` | Mobile header |
| `MobileCard.tsx` | Card component |
| `MobileButton.tsx` | Button component |
| `MobileTable.tsx` | Table component |
| `MobileModal.tsx` | Modal component |
| `MobileBottomSheet.tsx` | Bottom sheet |
| `MobileActionSheet.tsx` | Action sheet |
| `MobileDrawer.tsx` | Drawer component |
| `MobileSearchBar.tsx` | Search component |
| `MobileGlobalSearch.tsx` | Global search |
| `MobileContextualMenu.tsx` | Context menu |
| `MobileContextualActions.tsx` | Contextual actions |
| `MobilePullToRefresh.tsx` | Pull to refresh |
| `SwipeableCard.tsx` | Swipeable cards |
| `KeyboardNavigation.tsx` | Keyboard nav support |
| `NavigationBreadcrumbs.tsx` | Breadcrumb nav |

### Mobile Detection
| Hook/Utility | Description |
|--------------|-------------|
| `useMobileDetection.ts` | Device detection hook |
| `MobileDetectionDemo.tsx` | Detection demo |

---

## API Health & Monitoring

| Endpoint | Description |
|----------|-------------|
| `/api/v1/health` | Health check endpoint |
| `/api/v1/debug` | Debug endpoints (dev) |

---

## Summary Statistics

| Category | Count |
|----------|-------|
| Frontend Pages | 223+ |
| Backend API Files | 155+ |
| Backend Services | 70+ |
| Frontend Components | 150+ |
| Mobile Components | 25+ |
| Mobile Pages | 16 |

---

## Version Information

- **Document Version**: 1.0
- **Last Updated**: December 2024
- **Platform Version**: TritIQ BOS v1.6

---

*This feature guide is auto-generated based on comprehensive code analysis and may be updated as new features are added to the platform.*
