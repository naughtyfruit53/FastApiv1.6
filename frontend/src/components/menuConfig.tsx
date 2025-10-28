// frontend/src/components/menuConfig.tsx
import {
  Dashboard,
  Receipt,
  Inventory,
  People,
  Business,
  Assessment,
  Settings,
  ShoppingCart,
  LocalShipping,
  AccountBalance,
  SwapHoriz,
  TrendingUp,
  BarChart,
  Security,
  Storage,
  Build,
  ReceiptLong,
  NoteAdd,
  AddBusiness,
  DeveloperMode,
  Analytics,
  SupervisorAccount,
  Engineering,
  Schedule,
  Payment,
  Feedback,
  NotificationsActive,
  History,
  CloudUpload,
  SupportAgent,
  Assignment,
  Timeline,
  Groups,
  CorporateFare,
  Person,
  ContactPhone,
  PersonAdd,
  AssignmentTurnedIn,
  MonetizationOn,
  Campaign,
  LocalOffer,
  Sms,
  Email,
  Chat,
  SmartToy,
  Poll,
  Task,
  CalendarToday,
  EventNote,
  Alarm,
  AccessTime,
  Menu as MenuIcon
} from '@mui/icons-material';
import { PERMISSIONS } from '../types/rbac.types';

// Master Data - Restored as top-level menu with direct navigation
export const menuItems = {
  masterData: {
    title: 'Master Data',
    icon: <People />,
    sections: [
      {
        title: 'Business Entities',
        items: [
          { name: 'Vendors', path: '/masters/vendors', icon: <People />, permission: PERMISSIONS.MASTER_DATA_READ },
          { name: 'Customers', path: '/masters/customers', icon: <Business />, permission: PERMISSIONS.MASTER_DATA_READ },
          { name: 'Employees', path: '/masters/employees', icon: <People />, permission: PERMISSIONS.MASTER_DATA_READ },
          { name: 'Company Details', path: '/masters/company-details', icon: <Business />, permission: PERMISSIONS.MASTER_DATA_READ }
        ]
      },
      {
        title: 'Product & Inventory',
        items: [
          { name: 'Products', path: '/masters/products', icon: <Inventory />, permission: PERMISSIONS.MASTER_DATA_READ },
          { name: 'Categories', path: '/masters/categories', icon: <Storage />, permission: PERMISSIONS.MASTER_DATA_READ },
          { name: 'Units', path: '/masters/units', icon: <Storage />, permission: PERMISSIONS.MASTER_DATA_READ },
          { name: 'Bill of Materials (BOM)', path: '/masters/bom', icon: <Build />, permission: PERMISSIONS.MASTER_DATA_READ }
        ]
      },
      {
        title: 'Financial Configuration',
        items: [
          { name: 'Chart of Accounts', path: '/masters/chart-of-accounts', icon: <AccountBalance />, permission: PERMISSIONS.MASTER_DATA_READ },
          { name: 'Tax Codes', path: '/masters/tax-codes', icon: <Assessment />, permission: PERMISSIONS.MASTER_DATA_READ },
          { name: 'Payment Terms', path: '/masters/payment-terms', icon: <Business />, permission: PERMISSIONS.MASTER_DATA_READ },
          { name: 'Bank Account', path: '/bank-accounts', icon: <AccountBalance />, permission: PERMISSIONS.MASTER_DATA_READ }
        ]
      }
    ]
  },
  // Inventory menu - separated from ERP
  inventory: {
    title: 'Inventory',
    icon: <Inventory />,
    sections: [
      {
        title: 'Stock Management',
        items: [
          { name: 'Current Stock', path: '/inventory', icon: <Inventory />, permission: PERMISSIONS.INVENTORY_READ },
          { name: 'Stock Movements', path: '/inventory/movements', icon: <SwapHoriz />, permission: PERMISSIONS.INVENTORY_READ },
          { name: 'Low Stock Report', path: '/inventory/low-stock', icon: <TrendingUp />, permission: PERMISSIONS.INVENTORY_READ },
          { name: 'Pending Orders', path: '/inventory/pending-orders', icon: <Schedule />, permission: PERMISSIONS.INVENTORY_READ }
        ]
      },
      {
        title: 'Warehouse Management',
        items: [
          { name: 'Locations', path: '/inventory/locations', icon: <Storage />, permission: PERMISSIONS.INVENTORY_READ },
          { name: 'Bin Management', path: '/inventory/bins', icon: <Storage />, permission: PERMISSIONS.INVENTORY_READ },
          { name: 'Cycle Count', path: '/inventory/cycle-count', icon: <Assessment />, permission: PERMISSIONS.INVENTORY_READ }
        ]
      }
    ]
  },
  // Manufacturing menu - comprehensive manufacturing module
  manufacturing: {
    title: 'Manufacturing',
    icon: <Engineering />,
    sections: [
      {
        title: 'Production Management',
        items: [
          { name: 'Order Book', path: '/order-book', icon: <Assignment />, permission: PERMISSIONS.MANUFACTURING_READ },
          { name: 'Production Order', path: '/vouchers/Manufacturing-Vouchers/production-order', icon: <Build />, permission: PERMISSIONS.MANUFACTURING_READ },
          { name: 'Work Order', path: '/vouchers/Manufacturing-Vouchers/work-order', icon: <Assessment />, permission: PERMISSIONS.MANUFACTURING_READ },
          { name: 'Material Requisition', path: '/vouchers/Manufacturing-Vouchers/material-requisition', icon: <Storage />, permission: PERMISSIONS.MANUFACTURING_READ },
          { name: 'Finished Good Receipt', path: '/vouchers/Manufacturing-Vouchers/finished-good-receipt', icon: <Inventory />, permission: PERMISSIONS.MANUFACTURING_READ },
          { name: 'Job Card', path: '/vouchers/Manufacturing-Vouchers/job-card', icon: <Assignment />, permission: PERMISSIONS.MANUFACTURING_READ }
        ]
      },
      {
        title: 'Jobwork Management',
        items: [
          { name: 'Inward Jobwork', path: '/manufacturing/jobwork/inward', icon: <LocalShipping />, permission: PERMISSIONS.MANUFACTURING_READ },
          { name: 'Outward Jobwork', path: '/manufacturing/jobwork/outward', icon: <SwapHoriz />, permission: PERMISSIONS.MANUFACTURING_READ },
          { name: 'Jobwork Challan', path: '/manufacturing/jobwork/challan', icon: <ReceiptLong />, permission: PERMISSIONS.MANUFACTURING_READ },
          { name: 'Jobwork Receipt', path: '/manufacturing/jobwork/receipt', icon: <Inventory />, permission: PERMISSIONS.MANUFACTURING_READ }
        ]
      },
      {
        title: 'Manufacturing Operations',
        items: [
          { name: 'Manufacturing Journal', path: '/vouchers/Manufacturing-Vouchers/manufacturing-journal', icon: <Build />, permission: PERMISSIONS.MANUFACTURING_READ },
          { name: 'Stock Journal', path: '/vouchers/Manufacturing-Vouchers/stock-journal', icon: <Storage />, permission: PERMISSIONS.MANUFACTURING_READ },
          { name: 'Material Receipt', path: '/vouchers/Manufacturing-Vouchers/material-receipt', icon: <Inventory />, permission: PERMISSIONS.MANUFACTURING_READ }
        ]
      },
      {
        title: 'Quality Control',
        items: [
          { name: 'Quality Inspection', path: '/manufacturing/quality/inspection', icon: <Assessment />, permission: PERMISSIONS.MANUFACTURING_READ },
          { name: 'Quality Reports', path: '/manufacturing/quality/reports', icon: <BarChart />, permission: PERMISSIONS.MANUFACTURING_READ }
        ]
      },
      {
        title: 'Manufacturing Reports',
        items: [
          { name: 'Production Summary', path: '/manufacturing/reports/production-summary', icon: <Assessment />, permission: PERMISSIONS.MANUFACTURING_READ },
          { name: 'Material Consumption', path: '/manufacturing/reports/material-consumption', icon: <BarChart />, permission: PERMISSIONS.MANUFACTURING_READ },
          { name: 'Manufacturing Efficiency', path: '/manufacturing/reports/efficiency', icon: <TrendingUp />, permission: PERMISSIONS.MANUFACTURING_READ }
        ]
      }
    ]
  },
  // Vouchers menu - separated from ERP
  vouchers: {
    title: 'Vouchers',
    icon: <ReceiptLong />,
    sections: [
      {
        title: 'Purchase Vouchers',
        items: [
          { name: 'Purchase Order', path: '/vouchers/Purchase-Vouchers/purchase-order', icon: <LocalShipping />, permission: PERMISSIONS.VOUCHERS_READ },
          { name: 'GRN (Goods Received Note)', path: '/vouchers/Purchase-Vouchers/grn', icon: <Inventory />, permission: PERMISSIONS.VOUCHERS_READ },
          { name: 'Purchase Voucher', path: '/vouchers/Purchase-Vouchers/purchase-voucher', icon: <ShoppingCart />, permission: PERMISSIONS.VOUCHERS_READ },
          { name: 'Purchase Return', path: '/vouchers/Purchase-Vouchers/purchase-return', icon: <SwapHoriz />, permission: PERMISSIONS.VOUCHERS_READ }
        ]
      },
      {
        title: 'Pre-Sales Vouchers',
        items: [
          { name: 'Quotation', path: '/vouchers/Pre-Sales-Voucher/quotation', icon: <NoteAdd />, permission: PERMISSIONS.VOUCHERS_READ },
          { name: 'Proforma Invoice', path: '/vouchers/Pre-Sales-Voucher/proforma-invoice', icon: <ReceiptLong />, permission: PERMISSIONS.VOUCHERS_READ },
          { name: 'Sales Order', path: '/vouchers/Pre-Sales-Voucher/sales-order', icon: <Assessment />, permission: PERMISSIONS.VOUCHERS_READ }
        ]
      },
      {
        title: 'Sales Vouchers',
        items: [
          { name: 'Sales Voucher', path: '/vouchers/Sales-Vouchers/sales-voucher', icon: <TrendingUp />, permission: PERMISSIONS.VOUCHERS_READ },
          { name: 'Delivery Challan', path: '/vouchers/Sales-Vouchers/delivery-challan', icon: <LocalShipping />, permission: PERMISSIONS.VOUCHERS_READ },
          { name: 'Sales Return', path: '/vouchers/Sales-Vouchers/sales-return', icon: <SwapHoriz />, permission: PERMISSIONS.VOUCHERS_READ }
        ]
      },
      {
        title: 'Financial Vouchers',
        items: [
          { name: 'Payment Voucher', path: '/vouchers/Financial-Vouchers/payment-voucher', icon: <AccountBalance />, permission: PERMISSIONS.VOUCHERS_READ },
          { name: 'Receipt Voucher', path: '/vouchers/Financial-Vouchers/receipt-voucher', icon: <AccountBalance />, permission: PERMISSIONS.VOUCHERS_READ },
          { name: 'Journal Voucher', path: '/vouchers/Financial-Vouchers/journal-voucher', icon: <AccountBalance />, permission: PERMISSIONS.VOUCHERS_READ },
          { name: 'Contra Voucher', path: '/vouchers/Financial-Vouchers/contra-voucher', icon: <AccountBalance />, permission: PERMISSIONS.VOUCHERS_READ },
          { name: 'Credit Note', path: '/vouchers/Financial-Vouchers/credit-note', icon: <AccountBalance />, permission: PERMISSIONS.VOUCHERS_READ },
          { name: 'Debit Note', path: '/vouchers/Financial-Vouchers/debit-note', icon: <AccountBalance />, permission: PERMISSIONS.VOUCHERS_READ },
          { name: 'Non-Sales Credit Note', path: '/vouchers/Financial-Vouchers/non-sales-credit-note', icon: <AccountBalance />, permission: PERMISSIONS.VOUCHERS_READ }
        ]
      },
      {
        title: 'Other Vouchers',
        items: [
          { name: 'RFQ (Request for Quotation)', path: '/vouchers/Others/rfq', icon: <Assignment />, permission: PERMISSIONS.VOUCHERS_READ },
          { name: 'Dispatch Details', path: '/vouchers/Others/dispatch-details', icon: <LocalShipping />, permission: PERMISSIONS.VOUCHERS_READ },
          { name: 'Inter Department Voucher', path: '/vouchers/Others/inter-department-voucher', icon: <SwapHoriz />, permission: PERMISSIONS.VOUCHERS_READ }
        ]
      }
    ]
  },
  // Finance menu (will be merged with Accounting)
  finance: {
    title: 'Finance',
    icon: <AccountBalance />,
    sections: [
      {
        title: 'Accounts Payable',
        items: [
          { name: 'Vendor Bills', path: '/accounts-payable', icon: <Receipt />, permission: PERMISSIONS.FINANCE_READ },
          { name: 'Payment Vouchers', path: '/vouchers/Financial-Vouchers/payment-voucher', icon: <Payment />, permission: PERMISSIONS.FINANCE_READ },
          { name: 'Vendor Aging', path: '/vendor-aging', icon: <Schedule />, permission: PERMISSIONS.FINANCE_READ }
        ]
      },
      {
        title: 'Accounts Receivable',
        items: [
          { name: 'Customer Invoices', path: '/accounts-receivable', icon: <ReceiptLong />, permission: PERMISSIONS.FINANCE_READ },
          { name: 'Receipt Vouchers', path: '/vouchers/Financial-Vouchers/receipt-voucher', icon: <MonetizationOn />, permission: PERMISSIONS.FINANCE_READ },
          { name: 'Customer Aging', path: '/customer-aging', icon: <Schedule />, permission: PERMISSIONS.FINANCE_READ }
        ]
      },
      {
        title: 'Cost Management',
        items: [
          { name: 'Cost Centers', path: '/cost-centers', icon: <CorporateFare />, permission: PERMISSIONS.FINANCE_READ },
          { name: 'Budget Management', path: '/budgets', icon: <TrendingUp />, permission: PERMISSIONS.FINANCE_READ },
          { name: 'Cost Analysis', path: '/cost-analysis', icon: <Analytics />, permission: PERMISSIONS.FINANCE_READ }
        ]
      },
      {
        title: 'Financial Reports',
        items: [
          { name: 'Cash Flow', path: '/reports/cash-flow', icon: <AccountBalance />, permission: PERMISSIONS.FINANCE_READ },
          { name: 'Cash Flow Forecast', path: '/cash-flow-forecast', icon: <Assessment />, permission: PERMISSIONS.FINANCE_READ },
          { name: 'Financial Reports Hub', path: '/financial-reports', icon: <Assessment />, permission: PERMISSIONS.FINANCE_READ }
        ]
      },
      {
        title: 'Analytics & KPIs',
        items: [
          { name: 'Finance Dashboard', path: '/finance-dashboard', icon: <Analytics />, permission: PERMISSIONS.FINANCE_READ },
          { name: 'Financial KPIs', path: '/financial-kpis', icon: <TrendingUp />, permission: PERMISSIONS.FINANCE_READ },
          { name: 'Expense Analysis', path: '/expense-analysis', icon: <BarChart />, permission: PERMISSIONS.FINANCE_READ }
        ]
      }
    ]
  },
  // Accounting menu (will be merged with Finance)
  accounting: {
    title: 'Accounting',
    icon: <AccountBalance />,
    sections: [
      {
        title: 'Chart of Accounts',
        items: [
          { name: 'Chart of Accounts', path: '/masters/chart-of-accounts', icon: <AccountBalance />, permission: PERMISSIONS.ACCOUNTING_READ },
          { name: 'Account Groups', path: '/account-groups', icon: <Business />, permission: PERMISSIONS.ACCOUNTING_READ },
          { name: 'Opening Balances', path: '/opening-balances', icon: <TrendingUp />, permission: PERMISSIONS.ACCOUNTING_READ }
        ]
      },
      {
        title: 'Transactions',
        items: [
          { name: 'General Ledger', path: '/general-ledger', icon: <ReceiptLong />, permission: PERMISSIONS.ACCOUNTING_READ },
          { name: 'Journal Entries', path: '/vouchers/Financial-Vouchers/journal-voucher', icon: <NoteAdd />, permission: PERMISSIONS.ACCOUNTING_READ },
          { name: 'Bank Reconciliation', path: '/bank-reconciliation', icon: <AccountBalance />, permission: PERMISSIONS.ACCOUNTING_READ }
        ]
      },
      {
        title: 'Financial Reports',
        items: [
          { name: 'Trial Balance', path: '/reports/trial-balance', icon: <BarChart />, permission: PERMISSIONS.ACCOUNTING_READ },
          { name: 'Profit & Loss', path: '/reports/profit-loss', icon: <TrendingUp />, permission: PERMISSIONS.ACCOUNTING_READ },
          { name: 'Balance Sheet', path: '/reports/balance-sheet', icon: <Assessment />, permission: PERMISSIONS.ACCOUNTING_READ },
          { name: 'Cash Flow', path: '/reports/cash-flow', icon: <AccountBalance />, permission: PERMISSIONS.ACCOUNTING_READ }
        ]
      }
    ]
  },
  // Reports & Analytics menu
  reportsAnalytics: {
    title: 'Reports & Analytics',
    icon: <Assessment />,
    sections: [
      {
        title: 'Financial Reports',
        items: [
          { name: 'Ledgers', path: '/reports/ledgers', icon: <AccountBalance />, permission: PERMISSIONS.REPORTS_READ },
          { name: 'Trial Balance', path: '/reports/trial-balance', icon: <BarChart />, permission: PERMISSIONS.REPORTS_READ },
          { name: 'Profit & Loss', path: '/reports/profit-loss', icon: <TrendingUp />, permission: PERMISSIONS.REPORTS_READ },
          { name: 'Balance Sheet', path: '/reports/balance-sheet', icon: <Assessment />, permission: PERMISSIONS.REPORTS_READ }
        ]
      },
      {
        title: 'Inventory Reports',
        items: [
          { name: 'Stock Report', path: '/reports/stock', icon: <Inventory />, permission: PERMISSIONS.REPORTS_READ },
          { name: 'Valuation Report', path: '/reports/valuation', icon: <BarChart />, permission: PERMISSIONS.REPORTS_READ },
          { name: 'Movement Report', path: '/reports/movements', icon: <SwapHoriz />, permission: PERMISSIONS.REPORTS_READ }
        ]
      },
      {
        title: 'Business Reports',
        items: [
          { name: 'Sales Analysis', path: '/reports/sales-analysis', icon: <TrendingUp />, permission: PERMISSIONS.REPORTS_READ },
          { name: 'Purchase Analysis', path: '/reports/purchase-analysis', icon: <ShoppingCart />, permission: PERMISSIONS.REPORTS_READ },
          { name: 'Vendor Analysis', path: '/reports/vendor-analysis', icon: <People />, permission: PERMISSIONS.REPORTS_READ }
        ]
      },
      {
        title: 'Business Analytics',
        items: [
          { name: 'Customer Analytics', path: '/analytics/customer', icon: <TrendingUp />, permission: PERMISSIONS.REPORTS_READ },
          { name: 'Sales Analytics', path: '/analytics/sales', icon: <BarChart />, permission: PERMISSIONS.REPORTS_READ },
          { name: 'Purchase Analytics', path: '/analytics/purchase', icon: <ShoppingCart />, permission: PERMISSIONS.REPORTS_READ }
        ]
      },
      {
        title: 'Advanced Analytics',
        items: [
          { name: 'Project Analytics', path: '/projects/analytics', icon: <Analytics />, permission: PERMISSIONS.REPORTS_READ },
          { name: 'HR Analytics', path: '/hr/analytics', icon: <TrendingUp />, permission: PERMISSIONS.REPORTS_READ }
        ]
      },
      {
        title: 'Service Analytics',
        items: [
          { name: 'Service Dashboard', path: '/analytics/service', icon: <Dashboard />, permission: PERMISSIONS.SERVICE_READ },
          { name: 'Job Completion', path: '/analytics/service/job-completion', icon: <Assignment />, permission: PERMISSIONS.SERVICE_READ },
          { name: 'Technician Performance', path: '/analytics/service/technician-performance', icon: <Engineering />, permission: PERMISSIONS.SERVICE_READ },
          { name: 'Customer Satisfaction', path: '/analytics/service/customer-satisfaction', icon: <Feedback />, permission: PERMISSIONS.SERVICE_READ },
          { name: 'SLA Compliance', path: '/analytics/service/sla-compliance', icon: <Timeline />, permission: PERMISSIONS.SERVICE_READ }
        ]
      }
    ]
  },
  // AI & Analytics Module
  aiAnalytics: {
    title: 'AI & Analytics',
    icon: <SmartToy />,
    sections: [
      {
        title: 'AI Assistant',
        items: [
          { name: 'AI Chatbot', path: '/ai-chatbot', icon: <SmartToy />, permission: PERMISSIONS.AI_ANALYTICS_READ },
          { name: 'AI Help & Guidance', path: '/ai/help', icon: <SupportAgent />, permission: PERMISSIONS.AI_ANALYTICS_READ },
          { name: 'Business Advisor', path: '/ai/advisor', icon: <Analytics />, permission: PERMISSIONS.AI_ANALYTICS_READ }
        ]
      },
      {
        title: 'Advanced Analytics',
        items: [
          { name: 'Analytics Dashboard', path: '/analytics/advanced-analytics', icon: <Dashboard />, permission: PERMISSIONS.AI_ANALYTICS_READ },
          { name: 'Predictive Analytics', path: '/ai-analytics', icon: <TrendingUp />, permission: PERMISSIONS.AI_ANALYTICS_READ },
          { name: 'Streaming Analytics', path: '/analytics/streaming-dashboard', icon: <Timeline />, permission: PERMISSIONS.AI_ANALYTICS_READ },
          { name: 'AutoML Platform', path: '/analytics/automl', icon: <Build />, permission: PERMISSIONS.AI_ANALYTICS_READ }
        ]
      },
      {
        title: 'AI Tools',
        items: [
          { name: 'A/B Testing', path: '/analytics/ab-testing', icon: <Poll />, permission: PERMISSIONS.AI_ANALYTICS_READ },
          { name: 'Model Explainability', path: '/ai/explainability', icon: <Assessment />, permission: PERMISSIONS.AI_ANALYTICS_READ },
          { name: 'Website Agent', path: '/service/website-agent', icon: <SmartToy />, permission: PERMISSIONS.AI_ANALYTICS_READ }
        ]
      }
    ]
  },
  // Sales menu (renamed from CRM, with service options removed)
  sales: {
    title: 'Sales',
    icon: <Person />,
    sections: [
      {
        title: 'Sales CRM',
        items: [
          { name: 'Sales Dashboard', path: '/sales/dashboard', icon: <Dashboard />, permission: PERMISSIONS.SALES_READ },
          { name: 'Lead Management', path: '/sales/leads', icon: <PersonAdd />, permission: PERMISSIONS.SALES_READ },
          { name: 'Opportunity Tracking', path: '/sales/opportunities', icon: <TrendingUp />, permission: PERMISSIONS.SALES_READ },
          { name: 'Sales Pipeline', path: '/sales/pipeline', icon: <Timeline />, permission: PERMISSIONS.SALES_READ },
          { name: 'Exhibition Mode', path: '/exhibition-mode', icon: <Business />, permission: PERMISSIONS.SALES_READ }
        ]
      },
      {
        title: 'Customer Management',
        items: [
          { name: 'Customer Database', path: '/sales/customers', icon: <People />, permission: PERMISSIONS.SALES_READ },
          { name: 'Contact Management', path: '/sales/contacts', icon: <ContactPhone />, permission: PERMISSIONS.SALES_READ },
          { name: 'Account Management', path: '/sales/accounts', icon: <Business />, permission: PERMISSIONS.SALES_READ },
          { name: 'Customer Analytics', path: '/sales/customer-analytics', icon: <Analytics />, permission: PERMISSIONS.SALES_READ }
        ]
      },
      {
        title: 'Sales Operations',
        items: [
          { name: 'Quotations', path: '/vouchers/Pre-Sales-Voucher/quotation', icon: <NoteAdd />, permission: PERMISSIONS.SALES_READ },
          { name: 'Sales Orders', path: '/vouchers/Pre-Sales-Voucher/sales-order', icon: <Receipt />, permission: PERMISSIONS.SALES_READ },
          { name: 'Commission Tracking', path: '/sales/commissions', icon: <MonetizationOn />, permission: PERMISSIONS.SALES_READ },
          { name: 'Sales Reports', path: '/sales/reports', icon: <Assessment />, permission: PERMISSIONS.SALES_READ }
        ]
      }
    ]
  },
  // Marketing Module
  marketing: {
    title: 'Marketing',
    icon: <Campaign />,
    sections: [
      {
        title: 'Campaign Management',
        items: [
          { name: 'Marketing Dashboard', path: '/marketing', icon: <Dashboard />, permission: PERMISSIONS.MARKETING_READ },
          { name: 'Campaigns', path: '/marketing/campaigns', icon: <Campaign />, permission: PERMISSIONS.MARKETING_READ },
          { name: 'Email Campaigns', path: '/marketing/campaigns/email', icon: <Email />, permission: PERMISSIONS.MARKETING_READ },
          { name: 'SMS Campaigns', path: '/marketing/campaigns/sms', icon: <Sms />, permission: PERMISSIONS.MARKETING_READ },
          { name: 'Social Media', path: '/marketing/campaigns/social', icon: <Groups />, permission: PERMISSIONS.MARKETING_READ }
        ]
      },
      {
        title: 'Promotions & Offers',
        items: [
          { name: 'Promotions', path: '/marketing/promotions', icon: <LocalOffer />, permission: PERMISSIONS.MARKETING_READ },
          { name: 'Discount Codes', path: '/marketing/discount-codes', icon: <LocalOffer />, permission: PERMISSIONS.MARKETING_READ },
          { name: 'Promotion Analytics', path: '/marketing/promotion-analytics', icon: <Analytics />, permission: PERMISSIONS.MARKETING_READ }
        ]
      },
      {
        title: 'Customer Engagement',
        items: [
          { name: 'Marketing Lists', path: '/marketing/lists', icon: <ContactPhone />, permission: PERMISSIONS.MARKETING_READ },
          { name: 'Segmentation', path: '/marketing/segmentation', icon: <Groups />, permission: PERMISSIONS.MARKETING_READ },
          { name: 'Campaign Analytics', path: '/marketing/analytics', icon: <Assessment />, permission: PERMISSIONS.MARKETING_READ },
          { name: 'ROI Reports', path: '/marketing/reports/roi', icon: <MonetizationOn />, permission: PERMISSIONS.MARKETING_READ }
        ]
      }
    ]
  },
  // Service menu (renamed from Service Desk, with CRM service options added)
  service: {
    title: 'Service',
    icon: <SupportAgent />,
    sections: [
      {
        title: 'Helpdesk & Ticketing',
        items: [
          { name: 'Helpdesk Dashboard', path: '/service-desk', icon: <Dashboard />, permission: PERMISSIONS.SERVICE_READ },
          { name: 'Tickets', path: '/service-desk/tickets', icon: <Assignment />, permission: PERMISSIONS.SERVICE_READ },
          { name: 'SLA Management', path: '/service-desk/sla', icon: <Schedule />, permission: PERMISSIONS.SERVICE_READ },
          { name: 'Escalations', path: '/service-desk/escalations', icon: <TrendingUp />, permission: PERMISSIONS.SERVICE_READ }
        ]
      },
      {
        title: 'Omnichannel Support',
        items: [
          { name: 'Chat Conversations', path: '/service-desk/chat', icon: <Chat />, permission: PERMISSIONS.SERVICE_READ },
          { name: 'Chatbot Management', path: '/service-desk/chatbot', icon: <SmartToy />, permission: PERMISSIONS.SERVICE_READ },
          { name: 'Channel Configuration', path: '/service-desk/channels', icon: <Settings />, permission: PERMISSIONS.SERVICE_READ },
          { name: 'Knowledge Base', path: '/service-desk/knowledge', icon: <Storage />, permission: PERMISSIONS.SERVICE_READ }
        ]
      },
      {
        title: 'Feedback & Surveys',
        items: [
          { name: 'Customer Surveys', path: '/service-desk/surveys', icon: <Poll />, permission: PERMISSIONS.SERVICE_READ },
          { name: 'Survey Templates', path: '/service-desk/survey-templates', icon: <NoteAdd />, permission: PERMISSIONS.SERVICE_READ },
          { name: 'Feedback Analytics', path: '/service-desk/feedback-analytics', icon: <Analytics />, permission: PERMISSIONS.SERVICE_READ },
          { name: 'Satisfaction Reports', path: '/service-desk/satisfaction', icon: <Feedback />, permission: PERMISSIONS.SERVICE_READ }
        ]
      },
      {
        title: 'Service CRM',
        items: [
          { name: 'Service CRM Dashboard', path: '/service/dashboard', icon: <Dashboard />, permission: PERMISSIONS.SERVICE_READ },
          { name: 'Dispatch Management', path: '/service/dispatch', icon: <LocalShipping />, permission: PERMISSIONS.SERVICE_READ },
          { name: 'SLA Management', path: '/sla', icon: <Schedule />, permission: PERMISSIONS.SERVICE_READ },
          { name: 'Feedback Workflow', path: '/service/feedback', icon: <Feedback />, permission: PERMISSIONS.SERVICE_READ },
          { name: 'Role & Permissions', path: '/service/permissions', icon: <Security />, permission: PERMISSIONS.ADMIN }
        ]
      },
      {
        title: 'Management',
        items: [
          { name: 'Technicians', path: '/service/technicians', icon: <Engineering />, permission: PERMISSIONS.SERVICE_READ },
          { name: 'Work Orders', path: '/service/work-orders', icon: <Assignment />, permission: PERMISSIONS.SERVICE_READ },
          { name: 'Appointments', path: '/service/appointments', icon: <Schedule />, permission: PERMISSIONS.SERVICE_READ }
        ]
      }
    ]
  },
  hrManagement: {
    title: 'HR Management',
    icon: <Groups />,
    sections: [
      {
        title: 'Employee Management',
        items: [
          { name: 'Employee Directory', path: '/hr/employees-directory', icon: <People />, permission: PERMISSIONS.HR_READ },
          { name: 'Employee Records', path: '/hr/employees', icon: <People />, permission: PERMISSIONS.HR_READ },
          { name: 'Employee Onboarding', path: '/hr/onboarding', icon: <PersonAdd />, permission: PERMISSIONS.HR_READ },
          { name: 'Performance Management', path: '/hr/performance', icon: <Assessment />, permission: PERMISSIONS.HR_READ },
          { name: 'Employee Records Archive', path: '/hr/records', icon: <Storage />, permission: PERMISSIONS.HR_READ }
        ]
      },
      {
        title: 'Payroll & Benefits',
        items: [
          { name: 'Payroll Management', path: '/hr/payroll', icon: <MonetizationOn />, permission: PERMISSIONS.HR_READ },
          { name: 'Salary Processing', path: '/hr/salary', icon: <Payment />, permission: PERMISSIONS.HR_READ },
          { name: 'Benefits Administration', path: '/hr/benefits', icon: <Security />, permission: PERMISSIONS.HR_READ },
          { name: 'Tax Management', path: '/hr/tax', icon: <AccountBalance />, permission: PERMISSIONS.HR_READ }
        ]
      },
      {
        title: 'Time & Attendance',
        items: [
          { name: 'Time Tracking', path: '/hr/timesheet', icon: <Schedule />, permission: PERMISSIONS.HR_READ },
          { name: 'Leave Management', path: '/hr/leave', icon: <Timeline />, permission: PERMISSIONS.HR_READ },
          { name: 'Attendance Reports', path: '/hr/attendance', icon: <BarChart />, permission: PERMISSIONS.HR_READ },
          { name: 'Shift Management', path: '/hr/shifts', icon: <Schedule />, permission: PERMISSIONS.HR_READ }
        ]
      },
      {
        title: 'Recruitment',
        items: [
          { name: 'Job Postings', path: '/hr/jobs', icon: <AddBusiness />, permission: PERMISSIONS.HR_READ },
          { name: 'Candidate Management', path: '/hr/candidates', icon: <Person />, permission: PERMISSIONS.HR_READ },
          { name: 'Interview Scheduling', path: '/hr/interviews', icon: <Schedule />, permission: PERMISSIONS.HR_READ },
          { name: 'Hiring Pipeline', path: '/hr/hiring', icon: <Timeline />, permission: PERMISSIONS.HR_READ }
        ]
      },
      {
        title: 'HR Analytics',
        items: [
          { name: 'HR Analytics Dashboard', path: '/hr/analytics', icon: <Analytics />, permission: PERMISSIONS.HR_READ }
        ]
      }
    ]
  },
  // Projects & Tasks
  projects: {
    title: 'Projects',
    icon: <Assignment />,
    sections: [
      {
        title: 'Project Management',
        items: [
          { name: 'All Projects', path: '/projects', icon: <Assignment />, permission: PERMISSIONS.PROJECTS_READ },
          { name: 'Project Planning', path: '/projects/planning', icon: <Timeline />, permission: PERMISSIONS.PROJECTS_READ },
          { name: 'Resource Management', path: '/projects/resources', icon: <People />, permission: PERMISSIONS.PROJECTS_READ },
          { name: 'Document Management', path: '/projects/documents', icon: <Storage />, permission: PERMISSIONS.PROJECTS_READ },
          { name: 'Create Project', path: '/projects/create', icon: <NoteAdd />, permission: PERMISSIONS.PROJECTS_READ }
        ]
      },
      {
        title: 'Analytics & Reporting',
        items: [
          { name: 'Project Analytics', path: '/projects/analytics', icon: <Analytics />, permission: PERMISSIONS.PROJECTS_READ },
          { name: 'Performance Reports', path: '/projects/reports', icon: <Assessment />, permission: PERMISSIONS.PROJECTS_READ },
          { name: 'Resource Utilization', path: '/projects/utilization', icon: <TrendingUp />, permission: PERMISSIONS.PROJECTS_READ },
          { name: 'Budget Analysis', path: '/projects/budget', icon: <MonetizationOn />, permission: PERMISSIONS.PROJECTS_READ }
        ]
      },
      {
        title: 'Collaboration',
        items: [
          { name: 'Team Dashboard', path: '/projects/team', icon: <Groups />, permission: PERMISSIONS.PROJECTS_READ },
          { name: 'Time Tracking', path: '/projects/time', icon: <AccessTime />, permission: PERMISSIONS.PROJECTS_READ },
          { name: 'Team Documents', path: '/projects/documents', icon: <Storage />, permission: PERMISSIONS.PROJECTS_READ },
          { name: 'Project Chat', path: '/projects/chat', icon: <Chat />, permission: PERMISSIONS.PROJECTS_READ }
        ]
      }
    ]
  },
  tasksCalendar: {
    title: 'Tasks & Calendar',
    icon: <Task />,
    sections: [
      {
        title: 'Tasks',
        items: [
          { name: 'Task Dashboard', path: '/tasks/dashboard', icon: <Dashboard />, permission: PERMISSIONS.TASKS_CALENDAR_READ },
          { name: 'My Tasks', path: '/tasks', icon: <Task />, permission: PERMISSIONS.TASKS_CALENDAR_READ },
          { name: 'Create Task', path: '/tasks/create', icon: <NoteAdd />, permission: PERMISSIONS.TASKS_CALENDAR_READ }
        ]
      },
      {
        title: 'Task Operations',
        items: [
          { name: 'Task Assignment', path: '/tasks/assignments', icon: <AssignmentTurnedIn />, permission: PERMISSIONS.TASKS_CALENDAR_READ },
          { name: 'Task Templates', path: '/tasks/templates', icon: <Storage />, permission: PERMISSIONS.TASKS_CALENDAR_READ },
          { name: 'Task Reminders', path: '/tasks/reminders', icon: <Alarm />, permission: PERMISSIONS.TASKS_CALENDAR_READ },
          { name: 'Task Comments', path: '/tasks/comments', icon: <Chat />, permission: PERMISSIONS.TASKS_CALENDAR_READ }
        ]
      },
      {
        title: 'Calendar Views',
        items: [
          { name: 'Calendar Dashboard', path: '/calendar/dashboard', icon: <Dashboard />, permission: PERMISSIONS.TASKS_CALENDAR_READ },
          { name: 'Calendar View', path: '/calendar', icon: <CalendarToday />, permission: PERMISSIONS.TASKS_CALENDAR_READ },
          { name: 'My Events', path: '/calendar/events', icon: <EventNote />, permission: PERMISSIONS.TASKS_CALENDAR_READ },
          { name: 'Create Event', path: '/calendar/create', icon: <NoteAdd />, permission: PERMISSIONS.TASKS_CALENDAR_READ }
        ]
      },
      {
        title: 'Scheduling',
        items: [
          { name: 'Appointments', path: '/calendar/appointments', icon: <Schedule />, permission: PERMISSIONS.TASKS_CALENDAR_READ },
          { name: 'Meeting Rooms', path: '/calendar/meeting-rooms', icon: <Business />, permission: PERMISSIONS.TASKS_CALENDAR_READ },
          { name: 'Event Reminders', path: '/calendar/reminders', icon: <Alarm />, permission: PERMISSIONS.TASKS_CALENDAR_READ },
          { name: 'Recurring Events', path: '/calendar/recurring', icon: <Timeline />, permission: PERMISSIONS.TASKS_CALENDAR_READ }
        ]
      }
    ]
  },
  // Email module - full email functionality
  email: {
    title: 'Email',
    icon: <Email />,
    sections: [
      {
        title: 'Email Management',
        items: [
          { name: 'Inbox', path: '/email', icon: <Email />, permission: PERMISSIONS.EMAIL_READ },
          { name: 'Compose', path: '/email?compose=true', icon: <NoteAdd />, permission: PERMISSIONS.EMAIL_READ },
          { name: 'Account Settings', path: '/email/accounts', icon: <Settings />, permission: PERMISSIONS.EMAIL_READ }
        ]
      },
      {
        title: 'Integration',
        items: [
          { name: 'OAuth Connections', path: '/email/oauth', icon: <Security />, permission: PERMISSIONS.EMAIL_READ },
          { name: 'Sync Status', path: '/email/sync', icon: <CloudUpload />, permission: PERMISSIONS.EMAIL_READ },
          { name: 'Templates', path: '/email/templates', icon: <Assignment />, permission: PERMISSIONS.EMAIL_READ }
        ]
      }
    ]
  },
  settings: {
    title: 'Settings',
    icon: <Settings />,
    sections: [
      {
        title: 'Organization Settings',
        items: [
          { name: 'General Settings', path: '/settings/general-settings', icon: <Settings />, permission: PERMISSIONS.SETTINGS_READ },
          { name: 'Company Profile', path: '/settings/company', icon: <Business />, permission: PERMISSIONS.SETTINGS_READ },
          { name: 'Voucher Settings', path: '/settings/voucher-settings', icon: <ReceiptLong />, permission: PERMISSIONS.SETTINGS_READ },
          { name: 'Data Management', path: '/settings/DataManagement', icon: <Storage />, godSuperAdminOnly: true },
          { name: 'Factory Reset', path: '/settings/FactoryReset', icon: <Build />, godSuperAdminOnly: true }
        ]
      },
      {
        title: 'Administration',
        items: [
          { name: 'App Users', path: '/admin/app-user-management', icon: <Groups />, superAdminOnly: true },
          { name: 'Organization Management', path: '/admin/manage-organizations', icon: <CorporateFare />, superAdminOnly: true },
          { name: 'Organization List', path: '/admin/organizations', icon: <CorporateFare />, superAdminOnly: true },
          { name: 'Create Organization', path: '/admin/organizations/create', icon: <AddBusiness />, superAdminOnly: true },
          { name: 'License Management', path: '/admin/license-management', icon: <Security />, superAdminOnly: true },
          { name: 'Role Management', path: '/admin/rbac', icon: <SupervisorAccount />, permission: PERMISSIONS.ADMIN },
          { name: 'Service Settings', path: '/admin/service-settings', icon: <Settings />, permission: PERMISSIONS.ADMIN },
          { name: 'Audit Logs', path: '/admin/audit-logs', icon: <History />, permission: PERMISSIONS.ADMIN },
          { name: 'Notification Management', path: '/admin/notifications', icon: <NotificationsActive />, permission: PERMISSIONS.ADMIN },
          { name: 'User Management', path: '/settings/user-management', icon: <People />, permission: PERMISSIONS.ADMIN }
        ]
      },
      {
        title: 'System & Utilities',
        items: [
          { name: 'System Reports', path: '/reports', icon: <Assessment />, permission: PERMISSIONS.SETTINGS_READ },
          { name: 'Migration Management', path: '/migration/management', icon: <SwapHoriz />, permission: PERMISSIONS.SETTINGS_READ },
          { name: 'UI Testing', path: '/ui-test', icon: <DeveloperMode />, permission: PERMISSIONS.SETTINGS_READ },
          { name: 'Notification Demo', path: '/notification-demo', icon: <NotificationsActive />, permission: PERMISSIONS.SETTINGS_READ },
          { name: 'Transport Management', path: '/transport', icon: <LocalShipping />, permission: PERMISSIONS.SETTINGS_READ },
          { name: 'Assets Management', path: '/assets', icon: <Storage />, permission: PERMISSIONS.SETTINGS_READ },
          { name: 'Bank Accounts', path: '/bank-accounts', icon: <AccountBalance />, permission: PERMISSIONS.SETTINGS_READ }
        ]
      }
    ]
  },
  menu: {
    title: 'Menu',
    icon: <MenuIcon />,
    sections: [] // Placeholder, will be set dynamically
  }
};

// Create main menu sections dynamically
export const mainMenuSections = (isSuperAdmin: boolean) => {
  // Debug logging
  console.log("menuConfig.tsx - Rendering menu for isSuperAdmin:", isSuperAdmin);
  return isSuperAdmin
    ? [
        {
          title: 'Administration',
          subSections: [
            {
              title: 'Administration',
              items: [
                { name: 'Demo', path: '/demo', icon: <DeveloperMode /> }
              ]
            }
          ]
        }
      ]
    : [
        // Note: Dashboard top-level removed by user request
        { title: 'Master Data', subSections: menuItems.masterData.sections },
        { title: 'Inventory', subSections: menuItems.inventory.sections },
        { title: 'Vouchers', subSections: menuItems.vouchers.sections },
        { title: 'Manufacturing', subSections: menuItems.manufacturing.sections },
        // Merge Finance & Accounting into single section
        { 
          title: 'Finance & Accounting', 
          subSections: [
            ...menuItems.finance.sections,
            ...menuItems.accounting.sections
          ]
        },
        { title: 'Reports & Analytics', subSections: menuItems.reportsAnalytics.sections },
        { title: 'AI & Analytics', subSections: menuItems.aiAnalytics.sections },
        { title: 'Sales', subSections: menuItems.sales.sections },
        { title: 'Marketing', subSections: menuItems.marketing.sections },
        { title: 'Service', subSections: menuItems.service.sections },
        { title: 'Projects', subSections: menuItems.projects.sections },
        { title: 'HR Management', subSections: menuItems.hrManagement.sections },
        { title: 'Tasks & Calendar', subSections: menuItems.tasksCalendar.sections }
        // Email and Settings moved to top-level menu
        // ERP removed and split into Inventory and Vouchers
      ];
};