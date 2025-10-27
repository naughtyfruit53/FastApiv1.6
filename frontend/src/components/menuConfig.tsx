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
import { SERVICE_PERMISSIONS } from '../types/rbac.types';

// Master Data - Restored as top-level menu with direct navigation
export const menuItems = {
  masterData: {
    title: 'Master Data',
    icon: <People />,
    sections: [
      {
        title: 'Business Entities',
        items: [
          { name: 'Vendors', path: '/masters/vendors', icon: <People /> },
          { name: 'Customers', path: '/masters/customers', icon: <Business /> },
          { name: 'Employees', path: '/masters/employees', icon: <People /> },
          { name: 'Company Details', path: '/masters/company-details', icon: <Business /> }
        ]
      },
      {
        title: 'Product & Inventory',
        items: [
          { name: 'Products', path: '/masters/products', icon: <Inventory /> },
          { name: 'Categories', path: '/masters/categories', icon: <Storage /> },
          { name: 'Units', path: '/masters/units', icon: <Storage /> },
          { name: 'Bill of Materials (BOM)', path: '/masters/bom', icon: <Build /> }
        ]
      },
      {
        title: 'Financial Configuration',
        items: [
          { name: 'Chart of Accounts', path: '/masters/chart-of-accounts', icon: <AccountBalance /> },
          { name: 'Tax Codes', path: '/masters/tax-codes', icon: <Assessment /> },
          { name: 'Payment Terms', path: '/masters/payment-terms', icon: <Business /> },
          { name: 'Bank Account', path: '/bank-accounts', icon: <AccountBalance /> }
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
          { name: 'Current Stock', path: '/inventory', icon: <Inventory /> },
          { name: 'Stock Movements', path: '/inventory/movements', icon: <SwapHoriz /> },
          { name: 'Low Stock Report', path: '/inventory/low-stock', icon: <TrendingUp /> },
          { name: 'Pending Orders', path: '/inventory/pending-orders', icon: <Schedule /> }
        ]
      },
      {
        title: 'Warehouse Management',
        items: [
          { name: 'Locations', path: '/inventory/locations', icon: <Storage /> },
          { name: 'Bin Management', path: '/inventory/bins', icon: <Storage /> },
          { name: 'Cycle Count', path: '/inventory/cycle-count', icon: <Assessment /> }
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
          { name: 'Order Book', path: '/order-book', icon: <Assignment /> },
          { name: 'Production Order', path: '/vouchers/Manufacturing-Vouchers/production-order', icon: <Build /> },
          { name: 'Work Order', path: '/vouchers/Manufacturing-Vouchers/work-order', icon: <Assessment /> },
          { name: 'Material Requisition', path: '/vouchers/Manufacturing-Vouchers/material-requisition', icon: <Storage /> },
          { name: 'Finished Good Receipt', path: '/vouchers/Manufacturing-Vouchers/finished-good-receipt', icon: <Inventory /> },
          { name: 'Job Card', path: '/vouchers/Manufacturing-Vouchers/job-card', icon: <Assignment /> }
        ]
      },
      {
        title: 'Jobwork Management',
        items: [
          { name: 'Inward Jobwork', path: '/manufacturing/jobwork/inward', icon: <LocalShipping /> },
          { name: 'Outward Jobwork', path: '/manufacturing/jobwork/outward', icon: <SwapHoriz /> },
          { name: 'Jobwork Challan', path: '/manufacturing/jobwork/challan', icon: <ReceiptLong /> },
          { name: 'Jobwork Receipt', path: '/manufacturing/jobwork/receipt', icon: <Inventory /> }
        ]
      },
      {
        title: 'Manufacturing Operations',
        items: [
          { name: 'Manufacturing Journal', path: '/vouchers/Manufacturing-Vouchers/manufacturing-journal', icon: <Build /> },
          { name: 'Stock Journal', path: '/vouchers/Manufacturing-Vouchers/stock-journal', icon: <Storage /> },
          { name: 'Material Receipt', path: '/vouchers/Manufacturing-Vouchers/material-receipt', icon: <Inventory /> }
        ]
      },
      {
        title: 'Quality Control',
        items: [
          { name: 'Quality Inspection', path: '/manufacturing/quality/inspection', icon: <Assessment /> },
          { name: 'Quality Reports', path: '/manufacturing/quality/reports', icon: <BarChart /> }
        ]
      },
      {
        title: 'Manufacturing Reports',
        items: [
          { name: 'Production Summary', path: '/manufacturing/reports/production-summary', icon: <Assessment /> },
          { name: 'Material Consumption', path: '/manufacturing/reports/material-consumption', icon: <BarChart /> },
          { name: 'Manufacturing Efficiency', path: '/manufacturing/reports/efficiency', icon: <TrendingUp /> }
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
          { name: 'Purchase Order', path: '/vouchers/Purchase-Vouchers/purchase-order', icon: <LocalShipping /> },
          { name: 'GRN (Goods Received Note)', path: '/vouchers/Purchase-Vouchers/grn', icon: <Inventory /> },
          { name: 'Purchase Voucher', path: '/vouchers/Purchase-Vouchers/purchase-voucher', icon: <ShoppingCart /> },
          { name: 'Purchase Return', path: '/vouchers/Purchase-Vouchers/purchase-return', icon: <SwapHoriz /> }
        ]
      },
      {
        title: 'Pre-Sales Vouchers',
        items: [
          { name: 'Quotation', path: '/vouchers/Pre-Sales-Voucher/quotation', icon: <NoteAdd /> },
          { name: 'Proforma Invoice', path: '/vouchers/Pre-Sales-Voucher/proforma-invoice', icon: <ReceiptLong /> },
          { name: 'Sales Order', path: '/vouchers/Pre-Sales-Voucher/sales-order', icon: <Assessment /> }
        ]
      },
      {
        title: 'Sales Vouchers',
        items: [
          { name: 'Sales Voucher', path: '/vouchers/Sales-Vouchers/sales-voucher', icon: <TrendingUp /> },
          { name: 'Delivery Challan', path: '/vouchers/Sales-Vouchers/delivery-challan', icon: <LocalShipping /> },
          { name: 'Sales Return', path: '/vouchers/Sales-Vouchers/sales-return', icon: <SwapHoriz /> }
        ]
      },
      {
        title: 'Financial Vouchers',
        items: [
          { name: 'Payment Voucher', path: '/vouchers/Financial-Vouchers/payment-voucher', icon: <AccountBalance /> },
          { name: 'Receipt Voucher', path: '/vouchers/Financial-Vouchers/receipt-voucher', icon: <AccountBalance /> },
          { name: 'Journal Voucher', path: '/vouchers/Financial-Vouchers/journal-voucher', icon: <AccountBalance /> },
          { name: 'Contra Voucher', path: '/vouchers/Financial-Vouchers/contra-voucher', icon: <AccountBalance /> },
          { name: 'Credit Note', path: '/vouchers/Financial-Vouchers/credit-note', icon: <AccountBalance /> },
          { name: 'Debit Note', path: '/vouchers/Financial-Vouchers/debit-note', icon: <AccountBalance /> },
          { name: 'Non-Sales Credit Note', path: '/vouchers/Financial-Vouchers/non-sales-credit-note', icon: <AccountBalance /> }
        ]
      },
      {
        title: 'Other Vouchers',
        items: [
          { name: 'RFQ (Request for Quotation)', path: '/vouchers/Others/rfq', icon: <Assignment /> },
          { name: 'Dispatch Details', path: '/vouchers/Others/dispatch-details', icon: <LocalShipping /> },
          { name: 'Inter Department Voucher', path: '/vouchers/Others/inter-department-voucher', icon: <SwapHoriz /> }
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
          { name: 'Vendor Bills', path: '/accounts-payable', icon: <Receipt /> },
          { name: 'Payment Vouchers', path: '/vouchers/Financial-Vouchers/payment-voucher', icon: <Payment /> },
          { name: 'Vendor Aging', path: '/vendor-aging', icon: <Schedule /> }
        ]
      },
      {
        title: 'Accounts Receivable',
        items: [
          { name: 'Customer Invoices', path: '/accounts-receivable', icon: <ReceiptLong /> },
          { name: 'Receipt Vouchers', path: '/vouchers/Financial-Vouchers/receipt-voucher', icon: <MonetizationOn /> },
          { name: 'Customer Aging', path: '/customer-aging', icon: <Schedule /> }
        ]
      },
      {
        title: 'Cost Management',
        items: [
          { name: 'Cost Centers', path: '/cost-centers', icon: <CorporateFare /> },
          { name: 'Budget Management', path: '/budgets', icon: <TrendingUp /> },
          { name: 'Cost Analysis', path: '/cost-analysis', icon: <Analytics /> }
        ]
      },
      {
        title: 'Financial Reports',
        items: [
          { name: 'Cash Flow', path: '/reports/cash-flow', icon: <AccountBalance /> },
          { name: 'Cash Flow Forecast', path: '/cash-flow-forecast', icon: <Assessment /> },
          { name: 'Financial Reports Hub', path: '/financial-reports', icon: <Assessment /> }
        ]
      },
      {
        title: 'Analytics & KPIs',
        items: [
          { name: 'Finance Dashboard', path: '/finance-dashboard', icon: <Analytics /> },
          { name: 'Financial KPIs', path: '/financial-kpis', icon: <TrendingUp /> },
          { name: 'Expense Analysis', path: '/expense-analysis', icon: <BarChart /> }
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
          { name: 'Chart of Accounts', path: '/masters/chart-of-accounts', icon: <AccountBalance /> },
          { name: 'Account Groups', path: '/account-groups', icon: <Business /> },
          { name: 'Opening Balances', path: '/opening-balances', icon: <TrendingUp /> }
        ]
      },
      {
        title: 'Transactions',
        items: [
          { name: 'General Ledger', path: '/general-ledger', icon: <ReceiptLong /> },
          { name: 'Journal Entries', path: '/vouchers/Financial-Vouchers/journal-voucher', icon: <NoteAdd /> },
          { name: 'Bank Reconciliation', path: '/bank-reconciliation', icon: <AccountBalance /> }
        ]
      },
      {
        title: 'Financial Reports',
        items: [
          { name: 'Trial Balance', path: '/reports/trial-balance', icon: <BarChart /> },
          { name: 'Profit & Loss', path: '/reports/profit-loss', icon: <TrendingUp /> },
          { name: 'Balance Sheet', path: '/reports/balance-sheet', icon: <Assessment /> },
          { name: 'Cash Flow', path: '/reports/cash-flow', icon: <AccountBalance /> }
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
          { name: 'Ledgers', path: '/reports/ledgers', icon: <AccountBalance /> },
          { name: 'Trial Balance', path: '/reports/trial-balance', icon: <BarChart /> },
          { name: 'Profit & Loss', path: '/reports/profit-loss', icon: <TrendingUp /> },
          { name: 'Balance Sheet', path: '/reports/balance-sheet', icon: <Assessment /> }
        ]
      },
      {
        title: 'Inventory Reports',
        items: [
          { name: 'Stock Report', path: '/reports/stock', icon: <Inventory /> },
          { name: 'Valuation Report', path: '/reports/valuation', icon: <BarChart /> },
          { name: 'Movement Report', path: '/reports/movements', icon: <SwapHoriz /> }
        ]
      },
      {
        title: 'Business Reports',
        items: [
          { name: 'Sales Analysis', path: '/reports/sales-analysis', icon: <TrendingUp /> },
          { name: 'Purchase Analysis', path: '/reports/purchase-analysis', icon: <ShoppingCart /> },
          { name: 'Vendor Analysis', path: '/reports/vendor-analysis', icon: <People /> }
        ]
      },
      {
        title: 'Business Analytics',
        items: [
          { name: 'Customer Analytics', path: '/analytics/customer', icon: <TrendingUp /> },
          { name: 'Sales Analytics', path: '/analytics/sales', icon: <BarChart /> },
          { name: 'Purchase Analytics', path: '/analytics/purchase', icon: <ShoppingCart /> }
        ]
      },
      {
        title: 'Advanced Analytics',
        items: [
          { name: 'Project Analytics', path: '/projects/analytics', icon: <Analytics /> },
          { name: 'HR Analytics', path: '/hr/analytics', icon: <TrendingUp /> }
        ]
      },
      {
        title: 'Service Analytics',
        items: [
          { name: 'Service Dashboard', path: '/analytics/service', icon: <Dashboard />, servicePermission: SERVICE_PERMISSIONS.SERVICE_REPORTS_READ },
          { name: 'Job Completion', path: '/analytics/service/job-completion', icon: <Assignment />, servicePermission: SERVICE_PERMISSIONS.SERVICE_REPORTS_READ },
          { name: 'Technician Performance', path: '/analytics/service/technician-performance', icon: <Engineering />, servicePermission: SERVICE_PERMISSIONS.SERVICE_REPORTS_READ },
          { name: 'Customer Satisfaction', path: '/analytics/service/customer-satisfaction', icon: <Feedback />, servicePermission: SERVICE_PERMISSIONS.SERVICE_REPORTS_READ },
          { name: 'SLA Compliance', path: '/analytics/service/sla-compliance', icon: <Timeline />, servicePermission: SERVICE_PERMISSIONS.SERVICE_REPORTS_READ }
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
          { name: 'AI Chatbot', path: '/ai-chatbot', icon: <SmartToy /> },
          { name: 'AI Help & Guidance', path: '/ai/help', icon: <SupportAgent /> },
          { name: 'Business Advisor', path: '/ai/advisor', icon: <Analytics /> }
        ]
      },
      {
        title: 'Advanced Analytics',
        items: [
          { name: 'Analytics Dashboard', path: '/analytics/advanced-analytics', icon: <Dashboard /> },
          { name: 'Predictive Analytics', path: '/ai-analytics', icon: <TrendingUp /> },
          { name: 'Streaming Analytics', path: '/analytics/streaming-dashboard', icon: <Timeline /> },
          { name: 'AutoML Platform', path: '/analytics/automl', icon: <Build /> }
        ]
      },
      {
        title: 'AI Tools',
        items: [
          { name: 'A/B Testing', path: '/analytics/ab-testing', icon: <Poll /> },
          { name: 'Model Explainability', path: '/ai/explainability', icon: <Assessment /> },
          { name: 'Website Agent', path: '/service/website-agent', icon: <SmartToy /> }
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
          { name: 'Sales Dashboard', path: '/sales/dashboard', icon: <Dashboard /> },
          { name: 'Lead Management', path: '/sales/leads', icon: <PersonAdd /> },
          { name: 'Opportunity Tracking', path: '/sales/opportunities', icon: <TrendingUp /> },
          { name: 'Sales Pipeline', path: '/sales/pipeline', icon: <Timeline /> },
          { name: 'Exhibition Mode', path: '/exhibition-mode', icon: <Business /> }
        ]
      },
      {
        title: 'Customer Management',
        items: [
          { name: 'Customer Database', path: '/sales/customers', icon: <People /> },
          { name: 'Contact Management', path: '/sales/contacts', icon: <ContactPhone /> },
          { name: 'Account Management', path: '/sales/accounts', icon: <Business /> },
          { name: 'Customer Analytics', path: '/sales/customer-analytics', icon: <Analytics /> }
        ]
      },
      {
        title: 'Sales Operations',
        items: [
          { name: 'Quotations', path: '/vouchers/Pre-Sales-Voucher/quotation', icon: <NoteAdd /> },
          { name: 'Sales Orders', path: '/vouchers/Pre-Sales-Voucher/sales-order', icon: <Receipt /> },
          { name: 'Commission Tracking', path: '/sales/commissions', icon: <MonetizationOn /> },
          { name: 'Sales Reports', path: '/sales/reports', icon: <Assessment /> }
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
          { name: 'Marketing Dashboard', path: '/marketing', icon: <Dashboard /> },
          { name: 'Campaigns', path: '/marketing/campaigns', icon: <Campaign /> },
          { name: 'Email Campaigns', path: '/marketing/campaigns/email', icon: <Email /> },
          { name: 'SMS Campaigns', path: '/marketing/campaigns/sms', icon: <Sms /> },
          { name: 'Social Media', path: '/marketing/campaigns/social', icon: <Groups /> }
        ]
      },
      {
        title: 'Promotions & Offers',
        items: [
          { name: 'Promotions', path: '/marketing/promotions', icon: <LocalOffer /> },
          { name: 'Discount Codes', path: '/marketing/discount-codes', icon: <LocalOffer /> },
          { name: 'Promotion Analytics', path: '/marketing/promotion-analytics', icon: <Analytics /> }
        ]
      },
      {
        title: 'Customer Engagement',
        items: [
          { name: 'Marketing Lists', path: '/marketing/lists', icon: <ContactPhone /> },
          { name: 'Segmentation', path: '/marketing/segmentation', icon: <Groups /> },
          { name: 'Campaign Analytics', path: '/marketing/analytics', icon: <Assessment /> },
          { name: 'ROI Reports', path: '/marketing/reports/roi', icon: <MonetizationOn /> }
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
          { name: 'Helpdesk Dashboard', path: '/service-desk', icon: <Dashboard /> },
          { name: 'Tickets', path: '/service-desk/tickets', icon: <Assignment /> },
          { name: 'SLA Management', path: '/service-desk/sla', icon: <Schedule /> },
          { name: 'Escalations', path: '/service-desk/escalations', icon: <TrendingUp /> }
        ]
      },
      {
        title: 'Omnichannel Support',
        items: [
          { name: 'Chat Conversations', path: '/service-desk/chat', icon: <Chat /> },
          { name: 'Chatbot Management', path: '/service-desk/chatbot', icon: <SmartToy /> },
          { name: 'Channel Configuration', path: '/service-desk/channels', icon: <Settings /> },
          { name: 'Knowledge Base', path: '/service-desk/knowledge', icon: <Storage /> }
        ]
      },
      {
        title: 'Feedback & Surveys',
        items: [
          { name: 'Customer Surveys', path: '/service-desk/surveys', icon: <Poll /> },
          { name: 'Survey Templates', path: '/service-desk/survey-templates', icon: <NoteAdd /> },
          { name: 'Feedback Analytics', path: '/service-desk/feedback-analytics', icon: <Analytics /> },
          { name: 'Satisfaction Reports', path: '/service-desk/satisfaction', icon: <Feedback /> }
        ]
      },
      {
        title: 'Service CRM',
        items: [
          { name: 'Service CRM Dashboard', path: '/service/dashboard', icon: <Dashboard />, servicePermission: SERVICE_PERMISSIONS.SERVICE_READ },
          { name: 'Dispatch Management', path: '/service/dispatch', icon: <LocalShipping />, servicePermission: SERVICE_PERMISSIONS.WORK_ORDER_READ },
          { name: 'SLA Management', path: '/sla', icon: <Schedule />, servicePermission: SERVICE_PERMISSIONS.SERVICE_READ },
          { name: 'Feedback Workflow', path: '/service/feedback', icon: <Feedback />, servicePermission: SERVICE_PERMISSIONS.SERVICE_READ },
          { name: 'Role & Permissions', path: '/service/permissions', icon: <Security />, role: 'org_admin' }
        ]
      },
      {
        title: 'Management',
        items: [
          { name: 'Technicians', path: '/service/technicians', icon: <Engineering />, servicePermission: SERVICE_PERMISSIONS.TECHNICIAN_READ },
          { name: 'Work Orders', path: '/service/work-orders', icon: <Assignment />, servicePermission: SERVICE_PERMISSIONS.WORK_ORDER_READ },
          { name: 'Appointments', path: '/service/appointments', icon: <Schedule />, servicePermission: SERVICE_PERMISSIONS.APPOINTMENT_READ }
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
          { name: 'Employee Directory', path: '/hr/employees-directory', icon: <People /> },
          { name: 'Employee Records', path: '/hr/employees', icon: <People /> },
          { name: 'Employee Onboarding', path: '/hr/onboarding', icon: <PersonAdd /> },
          { name: 'Performance Management', path: '/hr/performance', icon: <Assessment /> },
          { name: 'Employee Records Archive', path: '/hr/records', icon: <Storage /> }
        ]
      },
      {
        title: 'Payroll & Benefits',
        items: [
          { name: 'Payroll Management', path: '/hr/payroll', icon: <MonetizationOn /> },
          { name: 'Salary Processing', path: '/hr/salary', icon: <Payment /> },
          { name: 'Benefits Administration', path: '/hr/benefits', icon: <Security /> },
          { name: 'Tax Management', path: '/hr/tax', icon: <AccountBalance /> }
        ]
      },
      {
        title: 'Time & Attendance',
        items: [
          { name: 'Time Tracking', path: '/hr/timesheet', icon: <Schedule /> },
          { name: 'Leave Management', path: '/hr/leave', icon: <Timeline /> },
          { name: 'Attendance Reports', path: '/hr/attendance', icon: <BarChart /> },
          { name: 'Shift Management', path: '/hr/shifts', icon: <Schedule /> }
        ]
      },
      {
        title: 'Recruitment',
        items: [
          { name: 'Job Postings', path: '/hr/jobs', icon: <AddBusiness /> },
          { name: 'Candidate Management', path: '/hr/candidates', icon: <Person /> },
          { name: 'Interview Scheduling', path: '/hr/interviews', icon: <Schedule /> },
          { name: 'Hiring Pipeline', path: '/hr/hiring', icon: <Timeline /> }
        ]
      },
      {
        title: 'HR Analytics',
        items: [
          { name: 'HR Analytics Dashboard', path: '/hr/analytics', icon: <Analytics /> }
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
          { name: 'All Projects', path: '/projects', icon: <Assignment /> },
          { name: 'Project Planning', path: '/projects/planning', icon: <Timeline /> },
          { name: 'Resource Management', path: '/projects/resources', icon: <People /> },
          { name: 'Document Management', path: '/projects/documents', icon: <Storage /> },
          { name: 'Create Project', path: '/projects/create', icon: <NoteAdd /> }
        ]
      },
      {
        title: 'Analytics & Reporting',
        items: [
          { name: 'Project Analytics', path: '/projects/analytics', icon: <Analytics /> },
          { name: 'Performance Reports', path: '/projects/reports', icon: <Assessment /> },
          { name: 'Resource Utilization', path: '/projects/utilization', icon: <TrendingUp /> },
          { name: 'Budget Analysis', path: '/projects/budget', icon: <MonetizationOn /> }
        ]
      },
      {
        title: 'Collaboration',
        items: [
          { name: 'Team Dashboard', path: '/projects/team', icon: <Groups /> },
          { name: 'Time Tracking', path: '/projects/time', icon: <AccessTime /> },
          { name: 'Team Documents', path: '/projects/documents', icon: <Storage /> },
          { name: 'Project Chat', path: '/projects/chat', icon: <Chat /> }
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
          { name: 'Task Dashboard', path: '/tasks/dashboard', icon: <Dashboard /> },
          { name: 'My Tasks', path: '/tasks', icon: <Task /> },
          { name: 'Create Task', path: '/tasks/create', icon: <NoteAdd /> }
        ]
      },
      {
        title: 'Task Operations',
        items: [
          { name: 'Task Assignment', path: '/tasks/assignments', icon: <AssignmentTurnedIn /> },
          { name: 'Task Templates', path: '/tasks/templates', icon: <Storage /> },
          { name: 'Task Reminders', path: '/tasks/reminders', icon: <Alarm /> },
          { name: 'Task Comments', path: '/tasks/comments', icon: <Chat /> }
        ]
      },
      {
        title: 'Calendar Views',
        items: [
          { name: 'Calendar Dashboard', path: '/calendar/dashboard', icon: <Dashboard /> },
          { name: 'Calendar View', path: '/calendar', icon: <CalendarToday /> },
          { name: 'My Events', path: '/calendar/events', icon: <EventNote /> },
          { name: 'Create Event', path: '/calendar/create', icon: <NoteAdd /> }
        ]
      },
      {
        title: 'Scheduling',
        items: [
          { name: 'Appointments', path: '/calendar/appointments', icon: <Schedule /> },
          { name: 'Meeting Rooms', path: '/calendar/meeting-rooms', icon: <Business /> },
          { name: 'Event Reminders', path: '/calendar/reminders', icon: <Alarm /> },
          { name: 'Recurring Events', path: '/calendar/recurring', icon: <Timeline /> }
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
          { name: 'Inbox', path: '/email', icon: <Email /> },
          { name: 'Compose', path: '/email?compose=true', icon: <NoteAdd /> },
          { name: 'Account Settings', path: '/email/accounts', icon: <Settings /> }
        ]
      },
      {
        title: 'Integration',
        items: [
          { name: 'OAuth Connections', path: '/email/oauth', icon: <Security /> },
          { name: 'Sync Status', path: '/email/sync', icon: <CloudUpload /> },
          { name: 'Templates', path: '/email/templates', icon: <Assignment /> }
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
          { name: 'General Settings', path: '/settings/general-settings', icon: <Settings /> },
          { name: 'Company Profile', path: '/settings/company', icon: <Business /> },
          { name: 'Voucher Settings', path: '/settings/voucher-settings', icon: <ReceiptLong /> },
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
          { name: 'Role Management', path: '/admin/rbac', icon: <SupervisorAccount />, servicePermission: SERVICE_PERMISSIONS.CRM_ADMIN },
          { name: 'Service Settings', path: '/admin/service-settings', icon: <Settings />, servicePermission: SERVICE_PERMISSIONS.CRM_SETTINGS },
          { name: 'Audit Logs', path: '/admin/audit-logs', icon: <History />, role: 'org_admin' },
          { name: 'Notification Management', path: '/admin/notifications', icon: <NotificationsActive />, role: 'org_admin' },
          { name: 'User Management', path: '/settings/user-management', icon: <People />, role: 'org_admin' }
        ]
      },
      {
        title: 'System & Utilities',
        items: [
          { name: 'System Reports', path: '/reports', icon: <Assessment /> },
          { name: 'Migration Management', path: '/migration/management', icon: <SwapHoriz /> },
          { name: 'UI Testing', path: '/ui-test', icon: <DeveloperMode /> },
          { name: 'Notification Demo', path: '/notification-demo', icon: <NotificationsActive /> },
          { name: 'Transport Management', path: '/transport', icon: <LocalShipping /> },
          { name: 'Assets Management', path: '/assets', icon: <Storage /> },
          { name: 'Bank Accounts', path: '/bank-accounts', icon: <AccountBalance /> }
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