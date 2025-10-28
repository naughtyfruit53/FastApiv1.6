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
// Removed import { PERMISSIONS } from '../types/rbac.types'; 

// Master Data - Restored as top-level menu with direct navigation
export const menuItems = {
  masterData: {
    title: 'Master Data',
    icon: <People />,
    sections: [
      {
        title: 'Business Entities',
        items: [
          { name: 'Vendors', path: '/masters/vendors', icon: <People />, permission: 'master_data.read', requireModule: 'master_data', requireSubmodule: { module: 'master_data', submodule: 'vendors' } },
          { name: 'Customers', path: '/masters/customers', icon: <Business />, permission: 'master_data.read', requireModule: 'master_data', requireSubmodule: { module: 'master_data', submodule: 'customers' } },
          { name: 'Employees', path: '/masters/employees', icon: <People />, permission: 'master_data.read', requireModule: 'master_data', requireSubmodule: { module: 'master_data', submodule: 'employees' } },
          { name: 'Company Details', path: '/masters/company-details', icon: <Business />, permission: 'master_data.read', requireModule: 'master_data', requireSubmodule: { module: 'master_data', submodule: 'company_details' } }
        ]
      },
      {
        title: 'Product & Inventory',
        items: [
          { name: 'Products', path: '/masters/products', icon: <Inventory />, permission: 'master_data.read', requireModule: 'master_data', requireSubmodule: { module: 'master_data', submodule: 'products' } },
          { name: 'Categories', path: '/masters/categories', icon: <Storage />, permission: 'master_data.read', requireModule: 'master_data', requireSubmodule: { module: 'master_data', submodule: 'categories' } },
          { name: 'Units', path: '/masters/units', icon: <Storage />, permission: 'master_data.read', requireModule: 'master_data', requireSubmodule: { module: 'master_data', submodule: 'units' } },
          { name: 'Bill of Materials (BOM)', path: '/masters/bom', icon: <Build />, permission: 'master_data.read', requireModule: 'master_data', requireSubmodule: { module: 'master_data', submodule: 'bom' } }
        ]
      },
      {
        title: 'Financial Configuration',
        items: [
          { name: 'Chart of Accounts', path: '/masters/chart-of-accounts', icon: <AccountBalance />, permission: 'master_data.read', requireModule: 'master_data', requireSubmodule: { module: 'master_data', submodule: 'chart_of_accounts' } },
          { name: 'Tax Codes', path: '/masters/tax-codes', icon: <Assessment />, permission: 'master_data.read', requireModule: 'master_data', requireSubmodule: { module: 'master_data', submodule: 'tax_codes' } },
          { name: 'Payment Terms', path: '/masters/payment-terms', icon: <Business />, permission: 'master_data.read', requireModule: 'master_data', requireSubmodule: { module: 'master_data', submodule: 'payment_terms' } },
          { name: 'Bank Account', path: '/bank-accounts', icon: <AccountBalance />, permission: 'master_data.read', requireModule: 'master_data', requireSubmodule: { module: 'master_data', submodule: 'bank_account' } }
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
          { name: 'Current Stock', path: '/inventory', icon: <Inventory />, permission: 'inventory.read', requireModule: 'inventory', requireSubmodule: { module: 'inventory', submodule: 'current_stock' } },
          { name: 'Stock Movements', path: '/inventory/movements', icon: <SwapHoriz />, permission: 'inventory.read', requireModule: 'inventory', requireSubmodule: { module: 'inventory', submodule: 'stock_movements' } },
          { name: 'Low Stock Report', path: '/inventory/low-stock', icon: <TrendingUp />, permission: 'inventory.read', requireModule: 'inventory', requireSubmodule: { module: 'inventory', submodule: 'low_stock_report' } },
          { name: 'Pending Orders', path: '/inventory/pending-orders', icon: <Schedule />, permission: 'inventory.read', requireModule: 'inventory', requireSubmodule: { module: 'inventory', submodule: 'pending_orders' } }
        ]
      },
      {
        title: 'Warehouse Management',
        items: [
          { name: 'Locations', path: '/inventory/locations', icon: <Storage />, permission: 'inventory.read', requireModule: 'inventory', requireSubmodule: { module: 'inventory', submodule: 'locations' } },
          { name: 'Bin Management', path: '/inventory/bins', icon: <Storage />, permission: 'inventory.read', requireModule: 'inventory', requireSubmodule: { module: 'inventory', submodule: 'bin_management' } },
          { name: 'Cycle Count', path: '/inventory/cycle-count', icon: <Assessment />, permission: 'inventory.read', requireModule: 'inventory', requireSubmodule: { module: 'inventory', submodule: 'cycle_count' } }
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
          { name: 'Order Book', path: '/order-book', icon: <Assignment />, permission: 'manufacturing.read', requireModule: 'manufacturing', requireSubmodule: { module: 'manufacturing', submodule: 'order_book' } },
          { name: 'Production Order', path: '/vouchers/Manufacturing-Vouchers/production-order', icon: <Build />, permission: 'manufacturing.read', requireModule: 'manufacturing', requireSubmodule: { module: 'manufacturing', submodule: 'production_order' } },
          { name: 'Work Order', path: '/vouchers/Manufacturing-Vouchers/work-order', icon: <Assessment />, permission: 'manufacturing.read', requireModule: 'manufacturing', requireSubmodule: { module: 'manufacturing', submodule: 'work_order' } },
          { name: 'Material Requisition', path: '/vouchers/Manufacturing-Vouchers/material-requisition', icon: <Storage />, permission: 'manufacturing.read', requireModule: 'manufacturing', requireSubmodule: { module: 'manufacturing', submodule: 'material_requisition' } },
          { name: 'Finished Good Receipt', path: '/vouchers/Manufacturing-Vouchers/finished-good-receipt', icon: <Inventory />, permission: 'manufacturing.read', requireModule: 'manufacturing', requireSubmodule: { module: 'manufacturing', submodule: 'finished_good_receipt' } },
          { name: 'Job Card', path: '/vouchers/Manufacturing-Vouchers/job-card', icon: <Assignment />, permission: 'manufacturing.read', requireModule: 'manufacturing', requireSubmodule: { module: 'manufacturing', submodule: 'job_card' } }
        ]
      },
      {
        title: 'Jobwork Management',
        items: [
          { name: 'Inward Jobwork', path: '/manufacturing/jobwork/inward', icon: <LocalShipping />, permission: 'manufacturing.read', requireModule: 'manufacturing', requireSubmodule: { module: 'manufacturing', submodule: 'inward_jobwork' } },
          { name: 'Outward Jobwork', path: '/manufacturing/jobwork/outward', icon: <SwapHoriz />, permission: 'manufacturing.read', requireModule: 'manufacturing', requireSubmodule: { module: 'manufacturing', submodule: 'outward_jobwork' } },
          { name: 'Jobwork Challan', path: '/manufacturing/jobwork/challan', icon: <ReceiptLong />, permission: 'manufacturing.read', requireModule: 'manufacturing', requireSubmodule: { module: 'manufacturing', submodule: 'jobwork_challan' } },
          { name: 'Jobwork Receipt', path: '/manufacturing/jobwork/receipt', icon: <Inventory />, permission: 'manufacturing.read', requireModule: 'manufacturing', requireSubmodule: { module: 'manufacturing', submodule: 'jobwork_receipt' } }
        ]
      },
      {
        title: 'Manufacturing Operations',
        items: [
          { name: 'Manufacturing Journal', path: '/vouchers/Manufacturing-Vouchers/manufacturing-journal', icon: <Build />, permission: 'manufacturing.read', requireModule: 'manufacturing', requireSubmodule: { module: 'manufacturing', submodule: 'manufacturing_journal' } },
          { name: 'Stock Journal', path: '/vouchers/Manufacturing-Vouchers/stock-journal', icon: <Storage />, permission: 'manufacturing.read', requireModule: 'manufacturing', requireSubmodule: { module: 'manufacturing', submodule: 'stock_journal' } },
          { name: 'Material Receipt', path: '/vouchers/Manufacturing-Vouchers/material-receipt', icon: <Inventory />, permission: 'manufacturing.read', requireModule: 'manufacturing', requireSubmodule: { module: 'manufacturing', submodule: 'material_receipt' } }
        ]
      },
      {
        title: 'Quality Control',
        items: [
          { name: 'Quality Inspection', path: '/manufacturing/quality/inspection', icon: <Assessment />, permission: 'manufacturing.read', requireModule: 'manufacturing', requireSubmodule: { module: 'manufacturing', submodule: 'quality_inspection' } },
          { name: 'Quality Reports', path: '/manufacturing/quality/reports', icon: <BarChart />, permission: 'manufacturing.read', requireModule: 'manufacturing', requireSubmodule: { module: 'manufacturing', submodule: 'quality_reports' } }
        ]
      },
      {
        title: 'Manufacturing Reports',
        items: [
          { name: 'Production Summary', path: '/manufacturing/reports/production-summary', icon: <Assessment />, permission: 'manufacturing.read', requireModule: 'manufacturing', requireSubmodule: { module: 'manufacturing', submodule: 'production_summary' } },
          { name: 'Material Consumption', path: '/manufacturing/reports/material-consumption', icon: <BarChart />, permission: 'manufacturing.read', requireModule: 'manufacturing', requireSubmodule: { module: 'manufacturing', submodule: 'material_consumption' } },
          { name: 'Manufacturing Efficiency', path: '/manufacturing/reports/efficiency', icon: <TrendingUp />, permission: 'manufacturing.read', requireModule: 'manufacturing', requireSubmodule: { module: 'manufacturing', submodule: 'manufacturing_efficiency' } }
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
          { name: 'Purchase Order', path: '/vouchers/Purchase-Vouchers/purchase-order', icon: <LocalShipping />, permission: 'vouchers.read', requireModule: 'vouchers', requireSubmodule: { module: 'vouchers', submodule: 'purchase_order' } },
          { name: 'GRN (Goods Received Note)', path: '/vouchers/Purchase-Vouchers/grn', icon: <Inventory />, permission: 'vouchers.read', requireModule: 'vouchers', requireSubmodule: { module: 'vouchers', submodule: 'grn' } },
          { name: 'Purchase Voucher', path: '/vouchers/Purchase-Vouchers/purchase-voucher', icon: <ShoppingCart />, permission: 'vouchers.read', requireModule: 'vouchers', requireSubmodule: { module: 'vouchers', submodule: 'purchase_voucher' } },
          { name: 'Purchase Return', path: '/vouchers/Purchase-Vouchers/purchase-return', icon: <SwapHoriz />, permission: 'vouchers.read', requireModule: 'vouchers', requireSubmodule: { module: 'vouchers', submodule: 'purchase_return' } }
        ]
      },
      {
        title: 'Pre-Sales Vouchers',
        items: [
          { name: 'Quotation', path: '/vouchers/Pre-Sales-Voucher/quotation', icon: <NoteAdd />, permission: 'vouchers.read', requireModule: 'vouchers', requireSubmodule: { module: 'vouchers', submodule: 'quotation' } },
          { name: 'Proforma Invoice', path: '/vouchers/Pre-Sales-Voucher/proforma-invoice', icon: <ReceiptLong />, permission: 'vouchers.read', requireModule: 'vouchers', requireSubmodule: { module: 'vouchers', submodule: 'proforma_invoice' } },
          { name: 'Sales Order', path: '/vouchers/Pre-Sales-Voucher/sales-order', icon: <Assessment />, permission: 'vouchers.read', requireModule: 'vouchers', requireSubmodule: { module: 'vouchers', submodule: 'sales_order' } }
        ]
      },
      {
        title: 'Sales Vouchers',
        items: [
          { name: 'Sales Voucher', path: '/vouchers/Sales-Vouchers/sales-voucher', icon: <TrendingUp />, permission: 'vouchers.read', requireModule: 'vouchers', requireSubmodule: { module: 'vouchers', submodule: 'sales_voucher' } },
          { name: 'Delivery Challan', path: '/vouchers/Sales-Vouchers/delivery-challan', icon: <LocalShipping />, permission: 'vouchers.read', requireModule: 'vouchers', requireSubmodule: { module: 'vouchers', submodule: 'delivery_challan' } },
          { name: 'Sales Return', path: '/vouchers/Sales-Vouchers/sales-return', icon: <SwapHoriz />, permission: 'vouchers.read', requireModule: 'vouchers', requireSubmodule: { module: 'vouchers', submodule: 'sales_return' } }
        ]
      },
      {
        title: 'Financial Vouchers',
        items: [
          { name: 'Payment Voucher', path: '/vouchers/Financial-Vouchers/payment-voucher', icon: <AccountBalance />, permission: 'vouchers.read', requireModule: 'vouchers', requireSubmodule: { module: 'vouchers', submodule: 'payment_voucher' } },
          { name: 'Receipt Voucher', path: '/vouchers/Financial-Vouchers/receipt-voucher', icon: <AccountBalance />, permission: 'vouchers.read', requireModule: 'vouchers', requireSubmodule: { module: 'vouchers', submodule: 'receipt_voucher' } },
          { name: 'Journal Voucher', path: '/vouchers/Financial-Vouchers/journal-voucher', icon: <AccountBalance />, permission: 'vouchers.read', requireModule: 'vouchers', requireSubmodule: { module: 'vouchers', submodule: 'journal_voucher' } },
          { name: 'Contra Voucher', path: '/vouchers/Financial-Vouchers/contra-voucher', icon: <AccountBalance />, permission: 'vouchers.read', requireModule: 'vouchers', requireSubmodule: { module: 'vouchers', submodule: 'contra_voucher' } },
          { name: 'Credit Note', path: '/vouchers/Financial-Vouchers/credit-note', icon: <AccountBalance />, permission: 'vouchers.read', requireModule: 'vouchers', requireSubmodule: { module: 'vouchers', submodule: 'credit_note' } },
          { name: 'Debit Note', path: '/vouchers/Financial-Vouchers/debit-note', icon: <AccountBalance />, permission: 'vouchers.read', requireModule: 'vouchers', requireSubmodule: { module: 'vouchers', submodule: 'debit_note' } },
          { name: 'Non-Sales Credit Note', path: '/vouchers/Financial-Vouchers/non-sales-credit-note', icon: <AccountBalance />, permission: 'vouchers.read', requireModule: 'vouchers', requireSubmodule: { module: 'vouchers', submodule: 'non_sales_credit_note' } }
        ]
      },
      {
        title: 'Other Vouchers',
        items: [
          { name: 'RFQ (Request for Quotation)', path: '/vouchers/Others/rfq', icon: <Assignment />, permission: 'vouchers.read', requireModule: 'vouchers', requireSubmodule: { module: 'vouchers', submodule: 'rfq' } },
          { name: 'Dispatch Details', path: '/vouchers/Others/dispatch-details', icon: <LocalShipping />, permission: 'vouchers.read', requireModule: 'vouchers', requireSubmodule: { module: 'vouchers', submodule: 'dispatch_details' } },
          { name: 'Inter Department Voucher', path: '/vouchers/Others/inter-department-voucher', icon: <SwapHoriz />, permission: 'vouchers.read', requireModule: 'vouchers', requireSubmodule: { module: 'vouchers', submodule: 'inter_department_voucher' } }
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
          { name: 'Vendor Bills', path: '/accounts-payable', icon: <Receipt />, permission: 'finance.read', requireModule: 'finance', requireSubmodule: { module: 'finance', submodule: 'vendor_bills' } },
          { name: 'Payment Vouchers', path: '/vouchers/Financial-Vouchers/payment-voucher', icon: <Payment />, permission: 'finance.read', requireModule: 'finance', requireSubmodule: { module: 'finance', submodule: 'payment_vouchers' } },
          { name: 'Vendor Aging', path: '/vendor-aging', icon: <Schedule />, permission: 'finance.read', requireModule: 'finance', requireSubmodule: { module: 'finance', submodule: 'vendor_aging' } }
        ]
      },
      {
        title: 'Accounts Receivable',
        items: [
          { name: 'Customer Invoices', path: '/accounts-receivable', icon: <ReceiptLong />, permission: 'finance.read', requireModule: 'finance', requireSubmodule: { module: 'finance', submodule: 'customer_invoices' } },
          { name: 'Receipt Vouchers', path: '/vouchers/Financial-Vouchers/receipt-voucher', icon: <MonetizationOn />, permission: 'finance.read', requireModule: 'finance', requireSubmodule: { module: 'finance', submodule: 'receipt_vouchers' } },
          { name: 'Customer Aging', path: '/customer-aging', icon: <Schedule />, permission: 'finance.read', requireModule: 'finance', requireSubmodule: { module: 'finance', submodule: 'customer_aging' } }
        ]
      },
      {
        title: 'Cost Management',
        items: [
          { name: 'Cost Centers', path: '/cost-centers', icon: <CorporateFare />, permission: 'finance.read', requireModule: 'finance', requireSubmodule: { module: 'finance', submodule: 'cost_centers' } },
          { name: 'Budget Management', path: '/budgets', icon: <TrendingUp />, permission: 'finance.read', requireModule: 'finance', requireSubmodule: { module: 'finance', submodule: 'budget_management' } },
          { name: 'Cost Analysis', path: '/cost-analysis', icon: <Analytics />, permission: 'finance.read', requireModule: 'finance', requireSubmodule: { module: 'finance', submodule: 'cost_analysis' } }
        ]
      },
      {
        title: 'Financial Reports',
        items: [
          { name: 'Cash Flow', path: '/reports/cash-flow', icon: <AccountBalance />, permission: 'finance.read', requireModule: 'finance', requireSubmodule: { module: 'finance', submodule: 'cash_flow' } },
          { name: 'Cash Flow Forecast', path: '/cash-flow-forecast', icon: <Assessment />, permission: 'finance.read', requireModule: 'finance', requireSubmodule: { module: 'finance', submodule: 'cash_flow_forecast' } },
          { name: 'Financial Reports Hub', path: '/financial-reports', icon: <Assessment />, permission: 'finance.read', requireModule: 'finance', requireSubmodule: { module: 'finance', submodule: 'financial_reports_hub' } }
        ]
      },
      {
        title: 'Analytics & KPIs',
        items: [
          { name: 'Finance Dashboard', path: '/finance-dashboard', icon: <Analytics />, permission: 'finance.read', requireModule: 'finance', requireSubmodule: { module: 'finance', submodule: 'finance_dashboard' } },
          { name: 'Financial KPIs', path: '/financial-kpis', icon: <TrendingUp />, permission: 'finance.read', requireModule: 'finance', requireSubmodule: { module: 'finance', submodule: 'financial_kpis' } },
          { name: 'Expense Analysis', path: '/expense-analysis', icon: <BarChart />, permission: 'finance.read', requireModule: 'finance', requireSubmodule: { module: 'finance', submodule: 'expense_analysis' } }
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
          { name: 'Chart of Accounts', path: '/masters/chart-of-accounts', icon: <AccountBalance />, permission: 'accounting.read', requireModule: 'accounting', requireSubmodule: { module: 'accounting', submodule: 'chart_of_accounts' } },
          { name: 'Account Groups', path: '/account-groups', icon: <Business />, permission: 'accounting.read', requireModule: 'accounting', requireSubmodule: { module: 'accounting', submodule: 'account_groups' } },
          { name: 'Opening Balances', path: '/opening-balances', icon: <TrendingUp />, permission: 'accounting.read', requireModule: 'accounting', requireSubmodule: { module: 'accounting', submodule: 'opening_balances' } }
        ]
      },
      {
        title: 'Transactions',
        items: [
          { name: 'General Ledger', path: '/general-ledger', icon: <ReceiptLong />, permission: 'accounting.read', requireModule: 'accounting', requireSubmodule: { module: 'accounting', submodule: 'general_ledger' } },
          { name: 'Journal Entries', path: '/vouchers/Financial-Vouchers/journal-voucher', icon: <NoteAdd />, permission: 'accounting.read', requireModule: 'accounting', requireSubmodule: { module: 'accounting', submodule: 'journal_entries' } },
          { name: 'Bank Reconciliation', path: '/bank-reconciliation', icon: <AccountBalance />, permission: 'accounting.read', requireModule: 'accounting', requireSubmodule: { module: 'accounting', submodule: 'bank_reconciliation' } }
        ]
      },
      {
        title: 'Financial Reports',
        items: [
          { name: 'Trial Balance', path: '/reports/trial-balance', icon: <BarChart />, permission: 'accounting.read', requireModule: 'accounting', requireSubmodule: { module: 'accounting', submodule: 'trial_balance' } },
          { name: 'Profit & Loss', path: '/reports/profit-loss', icon: <TrendingUp />, permission: 'accounting.read', requireModule: 'accounting', requireSubmodule: { module: 'accounting', submodule: 'profit_loss' } },
          { name: 'Balance Sheet', path: '/reports/balance-sheet', icon: <Assessment />, permission: 'accounting.read', requireModule: 'accounting', requireSubmodule: { module: 'accounting', submodule: 'balance_sheet' } },
          { name: 'Cash Flow', path: '/reports/cash-flow', icon: <AccountBalance />, permission: 'accounting.read', requireModule: 'accounting', requireSubmodule: { module: 'accounting', submodule: 'cash_flow' } }
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
          { name: 'Ledgers', path: '/reports/ledgers', icon: <AccountBalance />, permission: 'reports.read', requireModule: 'reports', requireSubmodule: { module: 'reports', submodule: 'ledgers' } },
          { name: 'Trial Balance', path: '/reports/trial-balance', icon: <BarChart />, permission: 'reports.read', requireModule: 'reports', requireSubmodule: { module: 'reports', submodule: 'trial_balance' } },
          { name: 'Profit & Loss', path: '/reports/profit-loss', icon: <TrendingUp />, permission: 'reports.read', requireModule: 'reports', requireSubmodule: { module: 'reports', submodule: 'profit_loss' } },
          { name: 'Balance Sheet', path: '/reports/balance-sheet', icon: <Assessment />, permission: 'reports.read', requireModule: 'reports', requireSubmodule: { module: 'reports', submodule: 'balance_sheet' } }
        ]
      },
      {
        title: 'Inventory Reports',
        items: [
          { name: 'Stock Report', path: '/reports/stock', icon: <Inventory />, permission: 'reports.read', requireModule: 'reports', requireSubmodule: { module: 'reports', submodule: 'stock_report' } },
          { name: 'Valuation Report', path: '/reports/valuation', icon: <BarChart />, permission: 'reports.read', requireModule: 'reports', requireSubmodule: { module: 'reports', submodule: 'valuation_report' } },
          { name: 'Movement Report', path: '/reports/movements', icon: <SwapHoriz />, permission: 'reports.read', requireModule: 'reports', requireSubmodule: { module: 'reports', submodule: 'movement_report' } }
        ]
      },
      {
        title: 'Business Reports',
        items: [
          { name: 'Sales Analysis', path: '/reports/sales-analysis', icon: <TrendingUp />, permission: 'reports.read', requireModule: 'reports', requireSubmodule: { module: 'reports', submodule: 'sales_analysis' } },
          { name: 'Purchase Analysis', path: '/reports/purchase-analysis', icon: <ShoppingCart />, permission: 'reports.read', requireModule: 'reports', requireSubmodule: { module: 'reports', submodule: 'purchase_analysis' } },
          { name: 'Vendor Analysis', path: '/reports/vendor-analysis', icon: <People />, permission: 'reports.read', requireModule: 'reports', requireSubmodule: { module: 'reports', submodule: 'vendor_analysis' } }
        ]
      },
      {
        title: 'Business Analytics',
        items: [
          { name: 'Customer Analytics', path: '/analytics/customer', icon: <TrendingUp />, permission: 'reports.read', requireModule: 'reports', requireSubmodule: { module: 'reports', submodule: 'customer_analytics' } },
          { name: 'Sales Analytics', path: '/analytics/sales', icon: <BarChart />, permission: 'reports.read', requireModule: 'reports', requireSubmodule: { module: 'reports', submodule: 'sales_analytics' } },
          { name: 'Purchase Analytics', path: '/analytics/purchase', icon: <ShoppingCart />, permission: 'reports.read', requireModule: 'reports', requireSubmodule: { module: 'reports', submodule: 'purchase_analytics' } }
        ]
      },
      {
        title: 'Advanced Analytics',
        items: [
          { name: 'Project Analytics', path: '/projects/analytics', icon: <Analytics />, permission: 'reports.read', requireModule: 'reports', requireSubmodule: { module: 'reports', submodule: 'project_analytics' } },
          { name: 'HR Analytics', path: '/hr/analytics', icon: <TrendingUp />, permission: 'reports.read', requireModule: 'reports', requireSubmodule: { module: 'reports', submodule: 'hr_analytics' } }
        ]
      },
      {
        title: 'Service Analytics',
        items: [
          { name: 'Service Dashboard', path: '/analytics/service', icon: <Dashboard />, permission: 'service.read', requireModule: 'reports', requireSubmodule: { module: 'reports', submodule: 'service_dashboard' } },
          { name: 'Job Completion', path: '/analytics/service/job-completion', icon: <Assignment />, permission: 'service.read', requireModule: 'reports', requireSubmodule: { module: 'reports', submodule: 'job_completion' } },
          { name: 'Technician Performance', path: '/analytics/service/technician-performance', icon: <Engineering />, permission: 'service.read', requireModule: 'reports', requireSubmodule: { module: 'reports', submodule: 'technician_performance' } },
          { name: 'Customer Satisfaction', path: '/analytics/service/customer-satisfaction', icon: <Feedback />, permission: 'service.read', requireModule: 'reports', requireSubmodule: { module: 'reports', submodule: 'customer_satisfaction' } },
          { name: 'SLA Compliance', path: '/analytics/service/sla-compliance', icon: <Timeline />, permission: 'service.read', requireModule: 'reports', requireSubmodule: { module: 'reports', submodule: 'sla_compliance' } }
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
          { name: 'AI Chatbot', path: '/ai-chatbot', icon: <SmartToy />, permission: 'ai_analytics.read', requireModule: 'ai_analytics', requireSubmodule: { module: 'ai_analytics', submodule: 'ai_chatbot' } },
          { name: 'AI Help & Guidance', path: '/ai/help', icon: <SupportAgent />, permission: 'ai_analytics.read', requireModule: 'ai_analytics', requireSubmodule: { module: 'ai_analytics', submodule: 'ai_help_guidance' } },
          { name: 'Business Advisor', path: '/ai/advisor', icon: <Analytics />, permission: 'ai_analytics.read', requireModule: 'ai_analytics', requireSubmodule: { module: 'ai_analytics', submodule: 'business_advisor' } }
        ]
      },
      {
        title: 'Advanced Analytics',
        items: [
          { name: 'Analytics Dashboard', path: '/analytics/advanced-analytics', icon: <Dashboard />, permission: 'ai_analytics.read', requireModule: 'ai_analytics', requireSubmodule: { module: 'ai_analytics', submodule: 'analytics_dashboard' } },
          { name: 'Predictive Analytics', path: '/ai-analytics', icon: <TrendingUp />, permission: 'ai_analytics.read', requireModule: 'ai_analytics', requireSubmodule: { module: 'ai_analytics', submodule: 'predictive_analytics' } },
          { name: 'Streaming Analytics', path: '/analytics/streaming-dashboard', icon: <Timeline />, permission: 'ai_analytics.read', requireModule: 'ai_analytics', requireSubmodule: { module: 'ai_analytics', submodule: 'streaming_analytics' } },
          { name: 'AutoML Platform', path: '/analytics/automl', icon: <Build />, permission: 'ai_analytics.read', requireModule: 'ai_analytics', requireSubmodule: { module: 'ai_analytics', submodule: 'automl_platform' } }
        ]
      },
      {
        title: 'AI Tools',
        items: [
          { name: 'A/B Testing', path: '/analytics/ab-testing', icon: <Poll />, permission: 'ai_analytics.read', requireModule: 'ai_analytics', requireSubmodule: { module: 'ai_analytics', submodule: 'ab_testing' } },
          { name: 'Model Explainability', path: '/ai/explainability', icon: <Assessment />, permission: 'ai_analytics.read', requireModule: 'ai_analytics', requireSubmodule: { module: 'ai_analytics', submodule: 'model_explainability' } },
          { name: 'Website Agent', path: '/service/website-agent', icon: <SmartToy />, permission: 'ai_analytics.read', requireModule: 'ai_analytics', requireSubmodule: { module: 'ai_analytics', submodule: 'website_agent' } }
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
          { name: 'Sales Dashboard', path: '/sales/dashboard', icon: <Dashboard />, permission: 'sales.read', requireModule: 'sales', requireSubmodule: { module: 'sales', submodule: 'sales_dashboard' } },
          { name: 'Lead Management', path: '/sales/leads', icon: <PersonAdd />, permission: 'sales.read', requireModule: 'sales', requireSubmodule: { module: 'sales', submodule: 'lead_management' } },
          { name: 'Opportunity Tracking', path: '/sales/opportunities', icon: <TrendingUp />, permission: 'sales.read', requireModule: 'sales', requireSubmodule: { module: 'sales', submodule: 'opportunity_tracking' } },
          { name: 'Sales Pipeline', path: '/sales/pipeline', icon: <Timeline />, permission: 'sales.read', requireModule: 'sales', requireSubmodule: { module: 'sales', submodule: 'sales_pipeline' } },
          { name: 'Exhibition Mode', path: '/exhibition-mode', icon: <Business />, permission: 'sales.read', requireModule: 'sales', requireSubmodule: { module: 'sales', submodule: 'exhibition_mode' } }
        ]
      },
      {
        title: 'Customer Management',
        items: [
          { name: 'Customer Database', path: '/sales/customers', icon: <People />, permission: 'sales.read', requireModule: 'sales', requireSubmodule: { module: 'sales', submodule: 'customer_database' } },
          { name: 'Contact Management', path: '/sales/contacts', icon: <ContactPhone />, permission: 'sales.read', requireModule: 'sales', requireSubmodule: { module: 'sales', submodule: 'contact_management' } },
          { name: 'Account Management', path: '/sales/accounts', icon: <Business />, permission: 'sales.read', requireModule: 'sales', requireSubmodule: { module: 'sales', submodule: 'account_management' } },
          { name: 'Customer Analytics', path: '/sales/customer-analytics', icon: <Analytics />, permission: 'sales.read', requireModule: 'sales', requireSubmodule: { module: 'sales', submodule: 'customer_analytics' } }
        ]
      },
      {
        title: 'Sales Operations',
        items: [
          { name: 'Quotations', path: '/vouchers/Pre-Sales-Voucher/quotation', icon: <NoteAdd />, permission: 'sales.read', requireModule: 'sales', requireSubmodule: { module: 'sales', submodule: 'quotations' } },
          { name: 'Sales Orders', path: '/vouchers/Pre-Sales-Voucher/sales-order', icon: <Receipt />, permission: 'sales.read', requireModule: 'sales', requireSubmodule: { module: 'sales', submodule: 'sales_orders' } },
          { name: 'Commission Tracking', path: '/sales/commissions', icon: <MonetizationOn />, permission: 'sales.read', requireModule: 'sales', requireSubmodule: { module: 'sales', submodule: 'commission_tracking' } },
          { name: 'Sales Reports', path: '/sales/reports', icon: <Assessment />, permission: 'sales.read', requireModule: 'sales', requireSubmodule: { module: 'sales', submodule: 'sales_reports' } }
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
          { name: 'Marketing Dashboard', path: '/marketing', icon: <Dashboard />, permission: 'marketing.read', requireModule: 'marketing', requireSubmodule: { module: 'marketing', submodule: 'marketing_dashboard' } },
          { name: 'Campaigns', path: '/marketing/campaigns', icon: <Campaign />, permission: 'marketing.read', requireModule: 'marketing', requireSubmodule: { module: 'marketing', submodule: 'campaigns' } },
          { name: 'Email Campaigns', path: '/marketing/campaigns/email', icon: <Email />, permission: 'marketing.read', requireModule: 'marketing', requireSubmodule: { module: 'marketing', submodule: 'email_campaigns' } },
          { name: 'SMS Campaigns', path: '/marketing/campaigns/sms', icon: <Sms />, permission: 'marketing.read', requireModule: 'marketing', requireSubmodule: { module: 'marketing', submodule: 'sms_campaigns' } },
          { name: 'Social Media', path: '/marketing/campaigns/social', icon: <Groups />, permission: 'marketing.read', requireModule: 'marketing', requireSubmodule: { module: 'marketing', submodule: 'social_media' } }
        ]
      },
      {
        title: 'Promotions & Offers',
        items: [
          { name: 'Promotions', path: '/marketing/promotions', icon: <LocalOffer />, permission: 'marketing.read', requireModule: 'marketing', requireSubmodule: { module: 'marketing', submodule: 'promotions' } },
          { name: 'Discount Codes', path: '/marketing/discount-codes', icon: <LocalOffer />, permission: 'marketing.read', requireModule: 'marketing', requireSubmodule: { module: 'marketing', submodule: 'discount_codes' } },
          { name: 'Promotion Analytics', path: '/marketing/promotion-analytics', icon: <Analytics />, permission: 'marketing.read', requireModule: 'marketing', requireSubmodule: { module: 'marketing', submodule: 'promotion_analytics' } }
        ]
      },
      {
        title: 'Customer Engagement',
        items: [
          { name: 'Marketing Lists', path: '/marketing/lists', icon: <ContactPhone />, permission: 'marketing.read', requireModule: 'marketing', requireSubmodule: { module: 'marketing', submodule: 'marketing_lists' } },
          { name: 'Segmentation', path: '/marketing/segmentation', icon: <Groups />, permission: 'marketing.read', requireModule: 'marketing', requireSubmodule: { module: 'marketing', submodule: 'segmentation' } },
          { name: 'Campaign Analytics', path: '/marketing/analytics', icon: <Assessment />, permission: 'marketing.read', requireModule: 'marketing', requireSubmodule: { module: 'marketing', submodule: 'campaign_analytics' } },
          { name: 'ROI Reports', path: '/marketing/reports/roi', icon: <MonetizationOn />, permission: 'marketing.read', requireModule: 'marketing', requireSubmodule: { module: 'marketing', submodule: 'roi_reports' } }
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
          { name: 'Helpdesk Dashboard', path: '/service-desk', icon: <Dashboard />, permission: 'service.read', requireModule: 'service', requireSubmodule: { module: 'service', submodule: 'helpdesk_dashboard' } },
          { name: 'Tickets', path: '/service-desk/tickets', icon: <Assignment />, permission: 'service.read', requireModule: 'service', requireSubmodule: { module: 'service', submodule: 'tickets' } },
          { name: 'SLA Management', path: '/service-desk/sla', icon: <Schedule />, permission: 'service.read', requireModule: 'service', requireSubmodule: { module: 'service', submodule: 'sla_management' } },
          { name: 'Escalations', path: '/service-desk/escalations', icon: <TrendingUp />, permission: 'service.read', requireModule: 'service', requireSubmodule: { module: 'service', submodule: 'escalations' } }
        ]
      },
      {
        title: 'Omnichannel Support',
        items: [
          { name: 'Chat Conversations', path: '/service-desk/chat', icon: <Chat />, permission: 'service.read', requireModule: 'service', requireSubmodule: { module: 'service', submodule: 'chat_conversations' } },
          { name: 'Chatbot Management', path: '/service-desk/chatbot', icon: <SmartToy />, permission: 'service.read', requireModule: 'service', requireSubmodule: { module: 'service', submodule: 'chatbot_management' } },
          { name: 'Channel Configuration', path: '/service-desk/channels', icon: <Settings />, permission: 'service.read', requireModule: 'service', requireSubmodule: { module: 'service', submodule: 'channel_configuration' } },
          { name: 'Knowledge Base', path: '/service-desk/knowledge', icon: <Storage />, permission: 'service.read', requireModule: 'service', requireSubmodule: { module: 'service', submodule: 'knowledge_base' } }
        ]
      },
      {
        title: 'Feedback & Surveys',
        items: [
          { name: 'Customer Surveys', path: '/service-desk/surveys', icon: <Poll />, permission: 'service.read', requireModule: 'service', requireSubmodule: { module: 'service', submodule: 'customer_surveys' } },
          { name: 'Survey Templates', path: '/service-desk/survey-templates', icon: <NoteAdd />, permission: 'service.read', requireModule: 'service', requireSubmodule: { module: 'service', submodule: 'survey_templates' } },
          { name: 'Feedback Analytics', path: '/service-desk/feedback-analytics', icon: <Analytics />, permission: 'service.read', requireModule: 'service', requireSubmodule: { module: 'service', submodule: 'feedback_analytics' } },
          { name: 'Satisfaction Reports', path: '/service-desk/satisfaction', icon: <Feedback />, permission: 'service.read', requireModule: 'service', requireSubmodule: { module: 'service', submodule: 'satisfaction_reports' } }
        ]
      },
      {
        title: 'Service CRM',
        items: [
          { name: 'Service CRM Dashboard', path: '/service/dashboard', icon: <Dashboard />, permission: 'service.read', requireModule: 'service', requireSubmodule: { module: 'service', submodule: 'service_crm_dashboard' } },
          { name: 'Dispatch Management', path: '/service/dispatch', icon: <LocalShipping />, permission: 'service.read', requireModule: 'service', requireSubmodule: { module: 'service', submodule: 'dispatch_management' } },
          { name: 'SLA Management', path: '/sla', icon: <Schedule />, permission: 'service.read', requireModule: 'service', requireSubmodule: { module: 'service', submodule: 'sla_management' } },
          { name: 'Feedback Workflow', path: '/service/feedback', icon: <Feedback />, permission: 'service.read', requireModule: 'service', requireSubmodule: { module: 'service', submodule: 'feedback_workflow' } },
          { name: 'Role & Permissions', path: '/service/permissions', icon: <Security />, permission: 'admin', requireModule: 'service', requireSubmodule: { module: 'service', submodule: 'role_permissions' } }
        ]
      },
      {
        title: 'Management',
        items: [
          { name: 'Technicians', path: '/service/technicians', icon: <Engineering />, permission: 'service.read', requireModule: 'service', requireSubmodule: { module: 'service', submodule: 'technicians' } },
          { name: 'Work Orders', path: '/service/work-orders', icon: <Assignment />, permission: 'service.read', requireModule: 'service', requireSubmodule: { module: 'service', submodule: 'work_orders' } },
          { name: 'Appointments', path: '/service/appointments', icon: <Schedule />, permission: 'service.read', requireModule: 'service', requireSubmodule: { module: 'service', submodule: 'appointments' } }
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
          { name: 'Employee Directory', path: '/hr/employees-directory', icon: <People />, permission: 'hr.read', requireModule: 'hr', requireSubmodule: { module: 'hr', submodule: 'employee_directory' } },
          { name: 'Employee Records', path: '/hr/employees', icon: <People />, permission: 'hr.read', requireModule: 'hr', requireSubmodule: { module: 'hr', submodule: 'employee_records' } },
          { name: 'Employee Onboarding', path: '/hr/onboarding', icon: <PersonAdd />, permission: 'hr.read', requireModule: 'hr', requireSubmodule: { module: 'hr', submodule: 'employee_onboarding' } },
          { name: 'Performance Management', path: '/hr/performance', icon: <Assessment />, permission: 'hr.read', requireModule: 'hr', requireSubmodule: { module: 'hr', submodule: 'performance_management' } },
          { name: 'Employee Records Archive', path: '/hr/records', icon: <Storage />, permission: 'hr.read', requireModule: 'hr', requireSubmodule: { module: 'hr', submodule: 'employee_records_archive' } }
        ]
      },
      {
        title: 'Payroll & Benefits',
        items: [
          { name: 'Payroll Management', path: '/hr/payroll', icon: <MonetizationOn />, permission: 'hr.read', requireModule: 'hr', requireSubmodule: { module: 'hr', submodule: 'payroll_management' } },
          { name: 'Salary Processing', path: '/hr/salary', icon: <Payment />, permission: 'hr.read', requireModule: 'hr', requireSubmodule: { module: 'hr', submodule: 'salary_processing' } },
          { name: 'Benefits Administration', path: '/hr/benefits', icon: <Security />, permission: 'hr.read', requireModule: 'hr', requireSubmodule: { module: 'hr', submodule: 'benefits_administration' } },
          { name: 'Tax Management', path: '/hr/tax', icon: <AccountBalance />, permission: 'hr.read', requireModule: 'hr', requireSubmodule: { module: 'hr', submodule: 'tax_management' } }
        ]
      },
      {
        title: 'Time & Attendance',
        items: [
          { name: 'Time Tracking', path: '/hr/timesheet', icon: <Schedule />, permission: 'hr.read', requireModule: 'hr', requireSubmodule: { module: 'hr', submodule: 'time_tracking' } },
          { name: 'Leave Management', path: '/hr/leave', icon: <Timeline />, permission: 'hr.read', requireModule: 'hr', requireSubmodule: { module: 'hr', submodule: 'leave_management' } },
          { name: 'Attendance Reports', path: '/hr/attendance', icon: <BarChart />, permission: 'hr.read', requireModule: 'hr', requireSubmodule: { module: 'hr', submodule: 'attendance_reports' } },
          { name: 'Shift Management', path: '/hr/shifts', icon: <Schedule />, permission: 'hr.read', requireModule: 'hr', requireSubmodule: { module: 'hr', submodule: 'shift_management' } }
        ]
      },
      {
        title: 'Recruitment',
        items: [
          { name: 'Job Postings', path: '/hr/jobs', icon: <AddBusiness />, permission: 'hr.read', requireModule: 'hr', requireSubmodule: { module: 'hr', submodule: 'job_postings' } },
          { name: 'Candidate Management', path: '/hr/candidates', icon: <Person />, permission: 'hr.read', requireModule: 'hr', requireSubmodule: { module: 'hr', submodule: 'candidate_management' } },
          { name: 'Interview Scheduling', path: '/hr/interviews', icon: <Schedule />, permission: 'hr.read', requireModule: 'hr', requireSubmodule: { module: 'hr', submodule: 'interview_scheduling' } },
          { name: 'Hiring Pipeline', path: '/hr/hiring', icon: <Timeline />, permission: 'hr.read', requireModule: 'hr', requireSubmodule: { module: 'hr', submodule: 'hiring_pipeline' } }
        ]
      },
      {
        title: 'HR Analytics',
        items: [
          { name: 'HR Analytics Dashboard', path: '/hr/analytics', icon: <Analytics />, permission: 'hr.read', requireModule: 'hr', requireSubmodule: { module: 'hr', submodule: 'hr_analytics_dashboard' } }
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
          { name: 'All Projects', path: '/projects', icon: <Assignment />, permission: 'projects.read', requireModule: 'projects', requireSubmodule: { module: 'projects', submodule: 'all_projects' } },
          { name: 'Project Planning', path: '/projects/planning', icon: <Timeline />, permission: 'projects.read', requireModule: 'projects', requireSubmodule: { module: 'projects', submodule: 'project_planning' } },
          { name: 'Resource Management', path: '/projects/resources', icon: <People />, permission: 'projects.read', requireModule: 'projects', requireSubmodule: { module: 'projects', submodule: 'resource_management' } },
          { name: 'Document Management', path: '/projects/documents', icon: <Storage />, permission: 'projects.read', requireModule: 'projects', requireSubmodule: { module: 'projects', submodule: 'document_management' } },
          { name: 'Create Project', path: '/projects/create', icon: <NoteAdd />, permission: 'projects.read', requireModule: 'projects', requireSubmodule: { module: 'projects', submodule: 'create_project' } }
        ]
      },
      {
        title: 'Analytics & Reporting',
        items: [
          { name: 'Project Analytics', path: '/projects/analytics', icon: <Analytics />, permission: 'projects.read', requireModule: 'projects', requireSubmodule: { module: 'projects', submodule: 'project_analytics' } },
          { name: 'Performance Reports', path: '/projects/reports', icon: <Assessment />, permission: 'projects.read', requireModule: 'projects', requireSubmodule: { module: 'projects', submodule: 'performance_reports' } },
          { name: 'Resource Utilization', path: '/projects/utilization', icon: <TrendingUp />, permission: 'projects.read', requireModule: 'projects', requireSubmodule: { module: 'projects', submodule: 'resource_utilization' } },
          { name: 'Budget Analysis', path: '/projects/budget', icon: <MonetizationOn />, permission: 'projects.read', requireModule: 'projects', requireSubmodule: { module: 'projects', submodule: 'budget_analysis' } }
        ]
      },
      {
        title: 'Collaboration',
        items: [
          { name: 'Team Dashboard', path: '/projects/team', icon: <Groups />, permission: 'projects.read', requireModule: 'projects', requireSubmodule: { module: 'projects', submodule: 'team_dashboard' } },
          { name: 'Time Tracking', path: '/projects/time', icon: <AccessTime />, permission: 'projects.read', requireModule: 'projects', requireSubmodule: { module: 'projects', submodule: 'time_tracking' } },
          { name: 'Team Documents', path: '/projects/documents', icon: <Storage />, permission: 'projects.read', requireModule: 'projects', requireSubmodule: { module: 'projects', submodule: 'team_documents' } },
          { name: 'Project Chat', path: '/projects/chat', icon: <Chat />, permission: 'projects.read', requireModule: 'projects', requireSubmodule: { module: 'projects', submodule: 'project_chat' } }
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
          { name: 'Task Dashboard', path: '/tasks/dashboard', icon: <Dashboard />, permission: 'tasks_calendar.read', requireModule: 'tasks_calendar', requireSubmodule: { module: 'tasks_calendar', submodule: 'task_dashboard' } },
          { name: 'My Tasks', path: '/tasks', icon: <Task />, permission: 'tasks_calendar.read', requireModule: 'tasks_calendar', requireSubmodule: { module: 'tasks_calendar', submodule: 'my_tasks' } },
          { name: 'Create Task', path: '/tasks/create', icon: <NoteAdd />, permission: 'tasks_calendar.read', requireModule: 'tasks_calendar', requireSubmodule: { module: 'tasks_calendar', submodule: 'create_task' } }
        ]
      },
      {
        title: 'Task Operations',
        items: [
          { name: 'Task Assignment', path: '/tasks/assignments', icon: <AssignmentTurnedIn />, permission: 'tasks_calendar.read', requireModule: 'tasks_calendar', requireSubmodule: { module: 'tasks_calendar', submodule: 'task_assignment' } },
          { name: 'Task Templates', path: '/tasks/templates', icon: <Storage />, permission: 'tasks_calendar.read', requireModule: 'tasks_calendar', requireSubmodule: { module: 'tasks_calendar', submodule: 'task_templates' } },
          { name: 'Task Reminders', path: '/tasks/reminders', icon: <Alarm />, permission: 'tasks_calendar.read', requireModule: 'tasks_calendar', requireSubmodule: { module: 'tasks_calendar', submodule: 'task_reminders' } },
          { name: 'Task Comments', path: '/tasks/comments', icon: <Chat />, permission: 'tasks_calendar.read', requireModule: 'tasks_calendar', requireSubmodule: { module: 'tasks_calendar', submodule: 'task_comments' } }
        ]
      },
      {
        title: 'Calendar Views',
        items: [
          { name: 'Calendar Dashboard', path: '/calendar/dashboard', icon: <Dashboard />, permission: 'tasks_calendar.read', requireModule: 'tasks_calendar', requireSubmodule: { module: 'tasks_calendar', submodule: 'calendar_dashboard' } },
          { name: 'Calendar View', path: '/calendar', icon: <CalendarToday />, permission: 'tasks_calendar.read', requireModule: 'tasks_calendar', requireSubmodule: { module: 'tasks_calendar', submodule: 'calendar_view' } },
          { name: 'My Events', path: '/calendar/events', icon: <EventNote />, permission: 'tasks_calendar.read', requireModule: 'tasks_calendar', requireSubmodule: { module: 'tasks_calendar', submodule: 'my_events' } },
          { name: 'Create Event', path: '/calendar/create', icon: <NoteAdd />, permission: 'tasks_calendar.read', requireModule: 'tasks_calendar', requireSubmodule: { module: 'tasks_calendar', submodule: 'create_event' } }
        ]
      },
      {
        title: 'Scheduling',
        items: [
          { name: 'Appointments', path: '/calendar/appointments', icon: <Schedule />, permission: 'tasks_calendar.read', requireModule: 'tasks_calendar', requireSubmodule: { module: 'tasks_calendar', submodule: 'appointments' } },
          { name: 'Meeting Rooms', path: '/calendar/meeting-rooms', icon: <Business />, permission: 'tasks_calendar.read', requireModule: 'tasks_calendar', requireSubmodule: { module: 'tasks_calendar', submodule: 'meeting_rooms' } },
          { name: 'Event Reminders', path: '/calendar/reminders', icon: <Alarm />, permission: 'tasks_calendar.read', requireModule: 'tasks_calendar', requireSubmodule: { module: 'tasks_calendar', submodule: 'event_reminders' } },
          { name: 'Recurring Events', path: '/calendar/recurring', icon: <Timeline />, permission: 'tasks_calendar.read', requireModule: 'tasks_calendar', requireSubmodule: { module: 'tasks_calendar', submodule: 'recurring_events' } }
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
          { name: 'Inbox', path: '/email', icon: <Email />, permission: 'email.read', requireModule: 'email', requireSubmodule: { module: 'email', submodule: 'inbox' } },
          { name: 'Compose', path: '/email?compose=true', icon: <NoteAdd />, permission: 'email.read', requireModule: 'email', requireSubmodule: { module: 'email', submodule: 'compose' } },
          { name: 'Account Settings', path: '/email/accounts', icon: <Settings />, permission: 'email.read', requireModule: 'email', requireSubmodule: { module: 'email', submodule: 'account_settings' } }
        ]
      },
      {
        title: 'Integration',
        items: [
          { name: 'OAuth Connections', path: '/email/oauth', icon: <Security />, permission: 'email.read', requireModule: 'email', requireSubmodule: { module: 'email', submodule: 'oauth_connections' } },
          { name: 'Sync Status', path: '/email/sync', icon: <CloudUpload />, permission: 'email.read', requireModule: 'email', requireSubmodule: { module: 'email', submodule: 'sync_status' } },
          { name: 'Templates', path: '/email/templates', icon: <Assignment />, permission: 'email.read', requireModule: 'email', requireSubmodule: { module: 'email', submodule: 'templates' } }
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
          { name: 'General Settings', path: '/settings/general-settings', icon: <Settings />, permission: 'settings.read', requireModule: 'settings', requireSubmodule: { module: 'settings', submodule: 'general_settings' } },
          { name: 'Company Profile', path: '/settings/company', icon: <Business />, permission: 'settings.read', requireModule: 'settings', requireSubmodule: { module: 'settings', submodule: 'company_profile' } },
          { name: 'Voucher Settings', path: '/settings/voucher-settings', icon: <ReceiptLong />, permission: 'settings.read', requireModule: 'settings', requireSubmodule: { module: 'settings', submodule: 'voucher_settings' } },
          { name: 'Data Management', path: '/settings/DataManagement', icon: <Storage />, godSuperAdminOnly: true, requireModule: 'settings', requireSubmodule: { module: 'settings', submodule: 'data_management' } },
          { name: 'Factory Reset', path: '/settings/FactoryReset', icon: <Build />, godSuperAdminOnly: true, requireModule: 'settings', requireSubmodule: { module: 'settings', submodule: 'factory_reset' } }
        ]
      },
      {
        title: 'Administration',
        items: [
          { name: 'App Users', path: '/admin/app-user-management', icon: <Groups />, superAdminOnly: true, requireModule: 'settings', requireSubmodule: { module: 'settings', submodule: 'app_users' } },
          { name: 'Organization Management', path: '/admin/manage-organizations', icon: <CorporateFare />, superAdminOnly: true, requireModule: 'settings', requireSubmodule: { module: 'settings', submodule: 'organization_management' } },
          { name: 'Organization List', path: '/admin/organizations', icon: <CorporateFare />, superAdminOnly: true, requireModule: 'settings', requireSubmodule: { module: 'settings', submodule: 'organization_list' } },
          { name: 'Create Organization', path: '/admin/organizations/create', icon: <AddBusiness />, superAdminOnly: true, requireModule: 'settings', requireSubmodule: { module: 'settings', submodule: 'create_organization' } },
          { name: 'License Management', path: '/admin/license-management', icon: <Security />, superAdminOnly: true, requireModule: 'settings', requireSubmodule: { module: 'settings', submodule: 'license_management' } },
          { name: 'Role Management', path: '/admin/rbac', icon: <SupervisorAccount />, permission: 'admin', requireModule: 'settings', requireSubmodule: { module: 'settings', submodule: 'role_management' } },
          { name: 'Service Settings', path: '/admin/service-settings', icon: <Settings />, permission: 'admin', requireModule: 'settings', requireSubmodule: { module: 'settings', submodule: 'service_settings' } },
          { name: 'Audit Logs', path: '/admin/audit-logs', icon: <History />, permission: 'admin', requireModule: 'settings', requireSubmodule: { module: 'settings', submodule: 'audit_logs' } },
          { name: 'Notification Management', path: '/admin/notifications', icon: <NotificationsActive />, permission: 'admin', requireModule: 'settings', requireSubmodule: { module: 'settings', submodule: 'notification_management' } },
          { name: 'User Management', path: '/settings/user-management', icon: <People />, permission: 'admin', requireModule: 'settings', requireSubmodule: { module: 'settings', submodule: 'user_management' } }
        ]
      },
      {
        title: 'System & Utilities',
        items: [
          { name: 'System Reports', path: '/reports', icon: <Assessment />, permission: 'settings.read', requireModule: 'settings', requireSubmodule: { module: 'settings', submodule: 'system_reports' } },
          { name: 'Migration Management', path: '/migration/management', icon: <SwapHoriz />, permission: 'settings.read', requireModule: 'settings', requireSubmodule: { module: 'settings', submodule: 'migration_management' } },
          { name: 'UI Testing', path: '/ui-test', icon: <DeveloperMode />, permission: 'settings.read', requireModule: 'settings', requireSubmodule: { module: 'settings', submodule: 'ui_testing' } },
          { name: 'Notification Demo', path: '/notification-demo', icon: <NotificationsActive />, permission: 'settings.read', requireModule: 'settings', requireSubmodule: { module: 'settings', submodule: 'notification_demo' } },
          { name: 'Transport Management', path: '/transport', icon: <LocalShipping />, permission: 'settings.read', requireModule: 'settings', requireSubmodule: { module: 'settings', submodule: 'transport_management' } },
          { name: 'Assets Management', path: '/assets', icon: <Storage />, permission: 'settings.read', requireModule: 'settings', requireSubmodule: { module: 'settings', submodule: 'assets_management' } },
          { name: 'Bank Accounts', path: '/bank-accounts', icon: <AccountBalance />, permission: 'settings.read', requireModule: 'settings', requireSubmodule: { module: 'settings', submodule: 'bank_accounts' } }
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
                { name: 'Demo', path: '/demo', icon: <DeveloperMode />, permission: 'admin', requireModule: 'administration', requireSubmodule: { module: 'administration', submodule: 'demo' } }
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