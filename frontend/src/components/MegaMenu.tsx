declare function handleUserMenuClose(...args: any[]): any;
declare function handleSubClose(...args: any[]): any;
declare function handleMenuClose(...args: any[]): any;
'use client';
import React, { useState, useEffect, useRef } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Menu,
  MenuItem,
  Box,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  IconButton,
  ListItemButton,
  Grid,
  Tooltip,
  InputBase
} from '@mui/material';
import {
  Dashboard,
  Receipt,
  Inventory,
  People,
  Business,
  Assessment,
  Settings,
  AccountCircle,
  ExpandMore,
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
  AdminPanelSettings,
  NotificationsActive,
  History,
  CloudUpload,
  SupportAgent,
  Assignment,
  Timeline,
  Groups,
  CorporateFare,
  ChevronRight,
  LockOutlined,
  Person,
  ContactPhone,
  PersonAdd,
  AssignmentTurnedIn,
  MonetizationOn,
  Campaign,
  LocalOffer,
  Email,
  Sms,
  Chat,
  SmartToy,
  Poll,
  SupportAgent as ServiceDeskIcon,
  Task,
  CalendarToday,
  EventNote,
  Alarm,
  AccessTime,
  CheckBox,
  Inbox,
  Send,
  Drafts,
  Menu as MenuIcon,
  Search as SearchIcon
} from '@mui/icons-material';
import { useRouter } from 'next/navigation';
import CreateOrganizationLicenseModal from './CreateOrganizationLicenseModal';
import { isAppSuperAdmin, isOrgSuperAdmin, canManageUsers, canShowUserManagementInMegaMenu } from '../types/user.types';
import { useQuery } from '@tanstack/react-query';
import { companyService } from '../services/authService';
import { rbacService, SERVICE_PERMISSIONS } from '../services/rbacService';
import { organizationService } from '../services/organizationService';
interface MegaMenuProps {
  user?: any;
  onLogout: () => void;
  isVisible?: boolean;
}
const MegaMenu: React.FC<MegaMenuProps> = ({ user, onLogout, isVisible = true }) => {
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [userMenuAnchor, setUserMenuAnchor] = useState<null | HTMLElement>(null);
  const [activeMenu, setActiveMenu] = useState<string | null>(null);
  const [subAnchorEl, setSubAnchorEl] = useState<null | HTMLElement>(null);
  const [activeSubCategory, setActiveSubCategory] = useState<any>(null);
  const [createLicenseModalOpen, setCreateLicenseModalOpen] = useState(false);
  const [selectedSection, setSelectedSection] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [filteredMenuItems, setFilteredMenuItems] = useState<any[]>([]);
  const searchRef = useRef<HTMLDivElement>(null);
  const router = useRouter();
  // Common button style for enhanced UI/UX
  const modernButtonStyle = {
    mx: 1,
    transition: 'all 0.2s ease-in-out',
    borderRadius: 2,
    '&:hover': {
      transform: 'translateY(-2px)',
      backgroundColor: 'rgba(59, 130, 246, 0.1)',
      boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
    },
    '&:focus': {
      outline: '2px solid',
      outlineColor: 'primary.main',
      outlineOffset: '2px',
    },
    '&:active': {
      transform: 'translateY(0) scale(0.98)',
    }
  };
  // Query for company data to show logo
  const { data: companyData } = useQuery({
    queryKey: ['company'],
    queryFn: companyService.getCurrentCompany,
    enabled: !isAppSuperAdmin(user), // Only fetch for organization users
    retry: false,
    staleTime: 0, // 5 minutes
  });
  // Query for current organization (to get enabled_modules)
  const { data: organizationData } = useQuery({
    queryKey: ['currentOrganization'],
    queryFn: organizationService.getCurrentOrganization,
    enabled: !isAppSuperAdmin(user), // Only for organization users
    retry: false,
    staleTime: 0,
    refetchOnWindowFocus: true, // Refetch when window regains focus
    refetchInterval: 10000, // Auto-refetch every 10 seconds for testing
    onSuccess: (data) => {
      console.log('Organization data fetched:', {
        enabled_modules: data.enabled_modules,
        timestamp: new Date().toISOString()
      });
    },
    onError: (error) => {
      console.error('Failed to fetch organization data:', error);
    }
  });
  // Query for current user's service permissions
  const { data: userPermissions = [] } = useQuery({
    queryKey: ['userServicePermissions'],
    queryFn: rbacService.getCurrentUserPermissions,
    enabled: !!user && !isAppSuperAdmin(user), // Only fetch for organization users
    retry: false,
    staleTime: 0, // 5 minutes
    onSuccess: (data) => {
      console.log('User permissions fetched:', data);
    }
  });
  // Add keyboard event listener for Escape key
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        if (anchorEl) {
          handleMenuClose();
        }
        if (userMenuAnchor) {
          handleUserMenuClose();
        }
        if (subAnchorEl) {
          handleSubClose();
        }
      }
    };
    document.addEventListener('keydown', handleKeyDown);
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [anchorEl, userMenuAnchor, subAnchorEl]);
  // Click outside to close search results
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
        setSearchQuery('');
        setFilteredMenuItems([]);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [searchRef]);
  // Don't render if not visible
  if (!isVisible) {
    return null;
  }
  const handleMenuClick = (event: React.MouseEvent<HTMLElement>, menuName: string) => {
    setAnchorEl(event.currentTarget);
    setActiveMenu(menuName);
    setSelectedSection(null);
  };
  const handleSubClick = (event: React.MouseEvent<HTMLElement>, category: any) => {
    setSubAnchorEl(event.currentTarget);
    setActiveSubCategory(category);
  };
  const handleUserMenuClick = (event: React.MouseEvent<HTMLElement>) => {
    setUserMenuAnchor(event.currentTarget);
  };
  const navigateTo = (path: string) => {
    router.push(path);
    handleMenuClose();
    handleSubClose();
  };
  // Enhanced logo navigation function
  const navigateToHome = () => {
    router.push('/dashboard');
    handleMenuClose();
  };
  // Check user roles using proper utility functions
  const isSuperAdmin = isAppSuperAdmin(user);
  // Service permission helper functions
  const hasServicePermission = (permission: string): boolean => {
    return userPermissions.includes(permission);
  };
  const hasAnyServicePermission = (permissions: string[]): boolean => {
    return permissions.some(permission => userPermissions.includes(permission));
  };
  const canAccessServiceFeatures = (): boolean => {
    const hasAccess = hasAnyServicePermission([
      SERVICE_PERMISSIONS.SERVICE_READ,
      SERVICE_PERMISSIONS.APPOINTMENT_READ,
      SERVICE_PERMISSIONS.TECHNICIAN_READ,
      SERVICE_PERMISSIONS.WORK_ORDER_READ
    ]);
    console.log('Permission check - canAccessService:', hasAccess, {
      userPermissions,
      timestamp: new Date().toISOString()
    });
    return hasAccess;
  };
  const canAccessServiceAnalytics = (): boolean => {
    return hasServicePermission(SERVICE_PERMISSIONS.SERVICE_REPORTS_READ);
  };
  const canManageServiceRoles = (): boolean => {
    return hasServicePermission(SERVICE_PERMISSIONS.CRM_ADMIN) || isOrgSuperAdmin(user);
  };
  // Helper to check if a module is enabled for the organization
  const isModuleEnabled = (module: string): boolean => {
    if (isSuperAdmin) {return true;} // Super admins see all
    const enabled = organizationData?.enabled_modules?.[module] ?? false;
    console.log(`Module check - ${module}:`, enabled, {
      allModules: organizationData?.enabled_modules,
      timestamp: new Date().toISOString()
    });
    return enabled;
  };
  const handleDemoMode = () => {
    // Navigate to demo page
    router.push('/demo');
    handleMenuClose();
  };
  const handleContactSupport = () => {
    // In production, this could open a support ticket form or email client
    window.location.href = 'mailto:support@tritiq.com?subject=Module Activation Request&body=Please activate the Service CRM module for my organization.';
  };
  const handleSubClose = () => {
    setSubAnchorEl(null);
    setActiveSubCategory(null);
  };
  const handleUserMenuClose = () => {
    setUserMenuAnchor(null);
  };
  const handleMenuClose = () => {
    setAnchorEl(null);
    setActiveMenu(null);
    setSelectedSection(null);
  };
  const _handleCreateOrgLicense = () => {
    // For now, we'll use a state to control the modal
    // In a full implementation, this would be managed by parent component
    setCreateLicenseModalOpen(true);
    handleMenuClose();
  };
  const menuItems = {
    // Master Data - Restored as top-level menu with direct navigation
    masterData: {
      title: 'Master Data',
      icon: <People />,
      sections: [
        {
          title: 'Business Entities',
          items: [
            { name: 'Vendors', path: 'masters/vendors', icon: <People /> },
            { name: 'Customers', path: 'masters/customers', icon: <Business /> },
            { name: 'Employees', path: 'masters/employees', icon: <People /> },
            { name: 'Company Details', path: 'masters/company-details', icon: <Business /> }
          ]
        },
        {
          title: 'Product & Inventory',
          items: [
            { name: 'Products', path: 'masters/products', icon: <Inventory /> },
            { name: 'Categories', path: '/categories', icon: <Storage /> },
            { name: 'Units', path: '/units', icon: <Storage /> },
            { name: 'Bill of Materials (BOM)', path: '/bom', icon: <Build /> }
          ]
        },
        {
          title: 'Financial Configuration',
          items: [
            { name: 'Chart of Accounts', path: '/chart-of-accounts', icon: <AccountBalance /> },
            { name: 'Tax Codes', path: '/tax-codes', icon: <Assessment /> },
            { name: 'Payment Terms', path: '/payment-terms', icon: <Business /> }
          ]
        }
      ]
    },
    // ERP menu now contains inventory and vouchers only
    erp: {
      title: 'ERP',
      icon: <Business />,
      sections: [
        {
          title: 'Inventory',
          items: [
            { name: 'Current Stock', path: '/inventory/stock', icon: <Inventory /> },
            { name: 'Stock Movements', path: '/inventory/movements', icon: <SwapHoriz /> },
            { name: 'Low Stock Report', path: '/inventory/low-stock', icon: <TrendingUp /> },
            { name: 'Stock Bulk Import', path: '/inventory/bulk-import', icon: <CloudUpload />, role: 'org_admin' },
            { name: 'Locations', path: '/inventory/locations', icon: <Storage /> },
            { name: 'Bin Management', path: '/inventory/bins', icon: <Storage /> },
            { name: 'Cycle Count', path: '/inventory/cycle-count', icon: <Assessment /> }
          ]
        },
        {
          title: 'Vouchers',
          items: [
            {
              name: 'Purchase Vouchers',
              subItems: [
                { name: 'Purchase Order', path: '/vouchers/Purchase-Vouchers/purchase-order', icon: <LocalShipping /> },
                { name: 'GRN (Goods Received Note)', path: '/vouchers/Purchase-Vouchers/grn', icon: <Inventory /> },
                { name: 'Purchase Voucher', path: '/vouchers/Purchase-Vouchers/purchase-voucher', icon: <ShoppingCart /> },
                { name: 'Purchase Return', path: '/vouchers/Purchase-Vouchers/purchase-return', icon: <SwapHoriz /> }
              ]
            },
            {
              name: 'Pre-Sales Vouchers',
              subItems: [
                { name: 'Quotation', path: '/vouchers/Pre-Sales-Voucher/quotation', icon: <NoteAdd /> },
                { name: 'Proforma Invoice', path: '/vouchers/Pre-Sales-Voucher/proforma-invoice', icon: <ReceiptLong /> },
                { name: 'Sales Order', path: '/vouchers/Pre-Sales-Voucher/sales-order', icon: <Assessment /> }
              ]
            },
            {
              name: 'Sales Vouchers',
              subItems: [
                { name: 'Sales Voucher', path: '/vouchers/Sales-Vouchers/sales-voucher', icon: <TrendingUp /> },
                { name: 'Delivery Challan', path: '/vouchers/Sales-Vouchers/delivery-challan', icon: <LocalShipping /> },
                { name: 'Sales Return', path: '/vouchers/Sales-Vouchers/sales-return', icon: <SwapHoriz /> }
              ]
            },
            {
              name: 'Financial Vouchers',
              subItems: [
                { name: 'Payment Voucher', path: '/vouchers/Financial-Vouchers/payment-voucher', icon: <AccountBalance /> },
                { name: 'Receipt Voucher', path: '/vouchers/Financial-Vouchers/receipt-voucher', icon: <AccountBalance /> },
                { name: 'Journal Voucher', path: '/vouchers/Financial-Vouchers/journal-voucher', icon: <AccountBalance /> },
                { name: 'Contra Voucher', path: '/vouchers/Financial-Vouchers/contra-voucher', icon: <AccountBalance /> },
                { name: 'Credit Note', path: '/vouchers/Financial-Vouchers/credit-note', icon: <AccountBalance /> },
                { name: 'Debit Note', path: '/vouchers/Financial-Vouchers/debit-note', icon: <AccountBalance /> },
                { name: 'Non-Sales Credit Note', path: '/vouchers/Financial-Vouchers/non-sales-credit-note', icon: <AccountBalance /> },
                { name: 'Inter Department Voucher', path: '/vouchers/inter-department-voucher', icon: <SwapHoriz /> }
              ]
            },
            {
              name: 'Manufacturing Vouchers',
              subItems: [
                { name: 'Production Order', path: '/vouchers/Manufacturing-Vouchers/production-order', icon: <Build /> },
                { name: 'Material Requisition', path: '/vouchers/Manufacturing-Vouchers/material-requisition', icon: <Storage /> },
                { name: 'Work Order', path: '/vouchers/Manufacturing-Vouchers/work-order', icon: <Assessment /> },
                { name: 'Finished Goods Receipt', path: '/vouchers/Manufacturing-Vouchers/finished-goods-receipt', icon: <Inventory /> }
              ]
            },
            {
              name: 'Others',
              subItems: [
                { name: 'RFQ (Request for Quotation)', path: '/vouchers/Others/rfq', icon: <Assignment /> },
                { name: 'Dispatch Details', path: '/vouchers/Others/dispatch-details', icon: <LocalShipping /> }
              ]
            }
          ]
        }
      ]
    },
    // Finance menu (split from Finance & Accounting)
    finance: {
      title: 'Finance',
      icon: <AccountBalance />,
      sections: [
        {
          title: 'Accounts Payable',
          items: [
            { name: 'Vendor Bills', path: '/accounts-payable', icon: <Receipt /> },
            { name: 'Payment Vouchers', path: '/payment-vouchers', icon: <Payment /> },
            { name: 'Vendor Aging', path: '/vendor-aging', icon: <Schedule /> }
          ]
        },
        {
          title: 'Accounts Receivable',
          items: [
            { name: 'Customer Invoices', path: '/accounts-receivable', icon: <ReceiptLong /> },
            { name: 'Receipt Vouchers', path: '/receipt-vouchers', icon: <MonetizationOn /> },
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
            { name: 'Cash Flow Forecast', path: '/cash-flow-forecast', icon: <Assessment /> }
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
    // Accounting menu (split from Finance & Accounting)
    accounting: {
      title: 'Accounting',
      icon: <AccountBalance />,
      sections: [
        {
          title: 'Chart of Accounts',
          items: [
            { name: 'Chart of Accounts', path: '/chart-of-accounts', icon: <AccountBalance /> },
            { name: 'Account Groups', path: '/account-groups', icon: <Business /> },
            { name: 'Opening Balances', path: '/opening-balances', icon: <TrendingUp /> }
          ]
        },
        {
          title: 'Transactions',
          items: [
            { name: 'General Ledger', path: '/general-ledger', icon: <ReceiptLong /> },
            { name: 'Journal Entries', path: '/journal-entries', icon: <NoteAdd /> },
            { name: 'Bank Reconciliation', path: '/bank-reconciliation', icon: <AccountBalance /> }
          ]
        },
        {
          title: 'Financial Reports',
          items: [
            { name: 'Trial Balance', path: '/reports/trial-balance', icon: <BarChart /> },
            { name: 'Profit & Loss', path: '/reports/profit-loss', icon: <TrendingUp /> },
            { name: 'Balance Sheet', path: '/reports/balance-sheet', icon: <Assessment /> }
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
            { name: 'Sales Pipeline', path: '/sales/pipeline', icon: <Timeline /> }
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
            { name: 'Service Dashboard', path: '/service-desk', icon: <Dashboard /> },
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
            { name: 'Service Dashboard', path: '/service/dashboard', icon: <Dashboard />, servicePermission: SERVICE_PERMISSIONS.SERVICE_READ },
            { name: 'Dispatch Management', path: '/service/dispatch', icon: <LocalShipping />, servicePermission: SERVICE_PERMISSIONS.WORK_ORDER_READ },
            { name: 'SLA Management', path: '/sla', icon: <Schedule />, servicePermission: SERVICE_PERMISSIONS.SERVICE_READ },
            { name: 'Feedback Workflow', path: '/service/feedback', icon: <Feedback />, servicePermission: SERVICE_PERMISSIONS.CUSTOMER_SERVICE_READ }
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
            { name: 'Employee Onboarding', path: '/hr/onboarding', icon: <PersonAdd /> },
            { name: 'Performance Management', path: '/hr/performance', icon: <Assessment /> },
            { name: 'Employee Records', path: '/hr/records', icon: <Storage /> }
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
        }
      ]
    },
    // Tasks & Calendar menu (split from Workspace)
    tasksCalendar: {
      title: 'Tasks & Calendar',
      icon: <Task />,
      sections: [
        {
          title: 'Tasks',
          items: [
            { name: 'Task Dashboard', path: '/tasks/dashboard', icon: <Dashboard /> },
            { name: 'My Tasks', path: '/tasks', icon: <Task /> },
            { name: 'Task Projects', path: '/tasks/projects', icon: <Assignment /> },
            { name: 'Create Task', path: '/tasks/create', icon: <NoteAdd /> }
          ]
        },
        {
          title: 'Time Management',
          items: [
            { name: 'Time Tracking', path: '/tasks/time-logs', icon: <AccessTime /> },
            { name: 'Task Reports', path: '/tasks/reports', icon: <Assessment /> },
            { name: 'Team Performance', path: '/tasks/team-performance', icon: <Groups /> },
            { name: 'Project Analytics', path: '/tasks/project-analytics', icon: <Analytics /> }
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
    // Email menu (split from Workspace)
    email: {
      title: 'Email',
      icon: <Email />,
      sections: [
        {
          title: 'Email Management',
          items: [
            { name: 'Mail Dashboard', path: '/mail/dashboard', icon: <Dashboard /> },
            { name: 'Inbox', path: '/mail/inbox', icon: <Inbox /> },
            { name: 'Sent Items', path: '/mail/sent', icon: <Send /> },
            { name: 'Drafts', path: '/mail/drafts', icon: <Drafts /> }
          ]
        },
        {
          title: 'Mail Operations',
          items: [
            { name: 'Compose Mail', path: '/mail/compose', icon: <NoteAdd /> },
            { name: 'Email Accounts', path: '/mail/accounts', icon: <AccountCircle /> },
            { name: 'Email Templates', path: '/mail/templates', icon: <Storage /> },
            { name: 'Email Rules', path: '/mail/rules', icon: <Settings /> }
          ]
        },
        {
          title: 'Integration & Sync',
          items: [
            { name: 'Email Sync', path: '/mail/sync', icon: <CloudUpload /> },
            { name: 'Task Linking', path: '/mail/task-linking', icon: <Task /> },
            { name: 'Calendar Linking', path: '/mail/calendar-linking', icon: <CalendarToday /> },
            { name: 'Email Analytics', path: '/mail/analytics', icon: <Analytics /> }
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
            { name: 'General Settings', path: '/settings', icon: <Settings /> },
            { name: 'Company Profile', path: '/settings/company', icon: <Business /> },
            { name: 'User Management', path: '/settings/users', icon: <People /> }
          ]
        },
        {
          title: 'Administration',
          items: [
            { name: 'App Users', path: '/admin/app-user-management', icon: <Groups />, superAdminOnly: true },
            { name: 'Organization Management', path: '/admin/manage-organizations', icon: <CorporateFare />, superAdminOnly: true },
            { name: 'License Management', path: '/admin/license-management', icon: <Security />, superAdminOnly: true },
            { name: 'Role Management', path: '/admin/rbac', icon: <SupervisorAccount />, servicePermission: SERVICE_PERMISSIONS.CRM_ADMIN },
            { name: 'Service Settings', path: '/admin/service-settings', icon: <Settings />, servicePermission: SERVICE_PERMISSIONS.CRM_SETTINGS },
            { name: 'Audit Logs', path: '/admin/audit-logs', icon: <History />, role: 'org_admin' },
            { name: 'Notification Management', path: '/admin/notifications', icon: <NotificationsActive />, role: 'org_admin' }
          ]
        }
      ]
    }
  };
  // Create main menu sections dynamically
  const mainMenuSections = isSuperAdmin
    ? [
        {
          title: 'Administration',
          subSections: [
            {
              title: 'Administration',
              items: [
                { name: 'Dashboard', path: '/dashboard', icon: <Dashboard /> },
                { name: 'Demo', path: '/demo', icon: <DeveloperMode /> }
              ]
            }
          ]
        }
      ]
    : [
        { title: 'Master Data', subSections: menuItems.masterData.sections },
        { title: 'ERP', subSections: menuItems.erp.sections },
        { title: 'Finance', subSections: menuItems.finance.sections },
        { title: 'Accounting', subSections: menuItems.accounting.sections },
        { title: 'Reports & Analytics', subSections: menuItems.reportsAnalytics.sections },
        { title: 'Sales', subSections: menuItems.sales.sections },
        { title: 'Marketing', subSections: menuItems.marketing.sections },
        { title: 'Service', subSections: menuItems.service.sections },
        { title: 'HR Management', subSections: menuItems.hrManagement.sections },
        { title: 'Tasks & Calendar', subSections: menuItems.tasksCalendar.sections },
        { title: 'Email', subSections: menuItems.email.sections }
      ];
  menuItems.menu = {
    title: 'Menu',
    icon: <MenuIcon />,
    sections: mainMenuSections
  };
  const flattenMenuItems = (menu: any) => {
    let items = [];
    menu.sections.forEach(section => {
      section.subSections.forEach(subSection => {
        subSection.items.forEach(item => {
          if (item.subItems) {
            item.subItems.forEach(subItem => items.push(subItem));
          } else {
            items.push(item);
          }
        });
      });
    });
    return items;
  };
  const handleSearch = (query: string) => {
    setSearchQuery(query);
    if (query.length >= 2) {
      const allItems = flattenMenuItems(menuItems.menu);
      const filtered = allItems.filter(item => item.name.toLowerCase().includes(query.toLowerCase()));
      setFilteredMenuItems(filtered);
    } else {
      setFilteredMenuItems([]);
    }
  };
  const renderMegaMenu = () => {
    if (!activeMenu || !menuItems[activeMenu as keyof typeof menuItems]) {return null;}
    const menu = menuItems[activeMenu as keyof typeof menuItems];
    // Filter menu items based on user permissions
    const filterMenuItems = (subSection: any) => {
      return subSection.items.filter((item: any) => {
        // Check role-based permissions
        if (item.role && !canManageUsers(user)) {
          return false;
        }
        // Check super admin only items
        if (item.superAdminOnly && !isSuperAdmin) {
          return false;
        }
        // Check service permissions
        if (item.servicePermission && !hasServicePermission(item.servicePermission)) {
          return false;
        }
        return true;
      });
    };
    const normalizedSections = menu.sections.map(section => {
      if (!section.subSections) {
        return {
          ...section,
          subSections: [{
            title: '',
            items: section.items || []
          }]
        };
      }
      return section;
    });
    const filteredSections = normalizedSections.map(section => ({
      ...section,
      subSections: section.subSections.map((subSection: any) => ({
        ...subSection,
        items: filterMenuItems(subSection)
      })).filter((subSection: any) => subSection.items.length > 0)
    })).filter(section => section.subSections.length > 0);
    if (filteredSections.length === 0) {
      console.log(`No items in submenu for ${activeMenu} - permissions may be missing`);
      return null;
    }
    return (
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
        PaperProps={{
          sx: {
            width: selectedSection ? 'calc(100vw - 40px)' : 'auto',
            maxWidth: selectedSection ? 'calc(100vw - 40px)' : 'auto',
            maxHeight: 'calc(100vh - 100px)',
            overflowY: 'hidden',
            mt: 0,
            borderRadius: 2,
            boxShadow: '0 10px 40px rgba(0, 0, 0, 0.15)',
            border: '1px solid',
            borderColor: 'divider',
            left: '20px !important',
            right: 'auto',
            '& .MuiMenuItem-root': {
              borderRadius: 1,
              margin: '2px 8px',
              transition: 'all 0.2s ease-in-out',
              '&:hover': {
                backgroundColor: 'primary.50',
                transform: 'translateX(4px)',
              }
            }
          }
        }}
        MenuListProps={{
          sx: {
            padding: 1
          }
        }}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'left' }}
        transformOrigin={{ vertical: 'top', horizontal: 'left' }}
        disableAutoFocusItem
      >
        <Grid container>
          <Grid item xs={3}>
            <List>
              {filteredSections.map((section, index) => (
                <ListItemButton
                  key={index}
                  selected={selectedSection === section.title}
                  onClick={() => setSelectedSection(section.title)}
                  sx={{
                    backgroundColor: selectedSection === section.title ? 'primary.light' : 'transparent',
                    color: selectedSection === section.title ? 'primary.contrastText' : 'text.primary',
                    '&:hover': {
                      backgroundColor: 'primary.main',
                      color: 'primary.contrastText',
                    }
                  }}
                >
                  <ListItemText primary={section.title} />
                  <ChevronRight />
                </ListItemButton>
              ))}
            </List>
          </Grid>
          <Grid item xs={9} sx={{ pl: 2 }}>
            {selectedSection && (
              <Grid container spacing={2}>
                {filteredSections.find(s => s.title === selectedSection)?.subSections.map((subSection: any, subIndex: number) => (
                  <Grid item xs={12} sm={6} md={4} key={subIndex}>
                    {subSection.title && (
                      <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 'bold', color: 'secondary.main' }}>
                        {subSection.title}
                      </Typography>
                    )}
                    <List dense>
                      {subSection.items.map((item: any, itemIndex: number) => (
                        <ListItemButton
                          key={itemIndex}
                          onClick={(e) => item.subItems ? handleSubClick(e, item) : navigateTo(item.path)}
                          sx={{
                            borderRadius: 1,
                            mb: 0.5,
                            '&:hover': {
                              backgroundColor: 'secondary.light',
                              color: 'secondary.contrastText'
                            }
                          }}
                        >
                          <ListItemIcon sx={{ minWidth: 36 }}>
                            {item.icon}
                          </ListItemIcon>
                          <ListItemText primary={item.name} />
                          {item.subItems && <ChevronRight />}
                        </ListItemButton>
                      ))}
                    </List>
                  </Grid>
                ))}
              </Grid>
            )}
          </Grid>
        </Grid>
      </Menu>
    );
  };
  const renderSubMenu = () => {
    if (!activeSubCategory) {return null;}
    return (
      <Menu
        anchorEl={subAnchorEl}
        open={Boolean(subAnchorEl)}
        onClose={handleSubClose}
        anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
        transformOrigin={{ vertical: 'top', horizontal: 'left' }}
        PaperProps={{
          sx: {
            ml: 1,
            borderRadius: 2,
            boxShadow: '0 10px 40px rgba(0, 0, 0, 0.15)',
            border: '1px solid',
            borderColor: 'divider',
            '& .MuiMenuItem-root': {
              borderRadius: 1,
              margin: '2px 8px',
              transition: 'all 0.2s ease-in-out',
              '&:hover': {
                backgroundColor: 'primary.50',
                transform: 'translateX(4px)',
              }
            }
          }
        }}
        MenuListProps={{
          sx: {
            padding: 1
          }
        }}
      >
        <Typography variant="subtitle2" sx={{ px: 2, py: 1, fontWeight: 'bold' }}>
          {activeSubCategory.name}
        </Typography>
        <Divider />
        <List dense>
          {activeSubCategory.subItems.map((subItem: any, subIndex: number) => (
            <ListItemButton
              key={subIndex}
              onClick={() => navigateTo(subItem.path)}
              sx={{
                px: 3,
                py: 1,
                minWidth: 200,
                '&:hover': {
                  backgroundColor: 'primary.light',
                  color: 'primary.contrastText'
                }
              }}
            >
              <ListItemIcon sx={{ minWidth: 36 }}>
                {subItem.icon}
              </ListItemIcon>
              <ListItemText primary={subItem.name} />
            </ListItemButton>
          ))}
        </List>
      </Menu>
    );
  };
  const renderSearchResults = () => {
    if (filteredMenuItems.length === 0) {return null;}
    return (
      <Menu
        open={filteredMenuItems.length > 0}
        onClose={() => setSearchQuery('')}
        anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
        transformOrigin={{ vertical: 'top', horizontal: 'right' }}
        PaperProps={{
          sx: {
            width: 300,
            maxHeight: 400,
          }
        }}
      >
        {filteredMenuItems.map((item, index) => (
          <MenuItem key={index} onClick={() => navigateTo(item.path)}>
            {item.name}
          </MenuItem>
        ))}
      </Menu>
    );
  };
  return (
    <>
      <AppBar
        position="static"
        className="modern-nav"
        sx={{
          backgroundColor: 'var(--bg-surface)',
          color: 'var(--text-primary)',
          boxShadow: 'var(--shadow-sm)',
          borderBottom: '1px solid var(--border-primary)'
        }}
      >
        <Toolbar>
          {/* Menu and Settings on the left */}
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <Button
              color="inherit"
              startIcon={<MenuIcon />}
              endIcon={<ExpandMore />}
              onClick={(e) => handleMenuClick(e, 'menu')}
              className="modern-menu-button"
              sx={modernButtonStyle}
            >
              Menu
            </Button>
            <Button
              color="inherit"
              startIcon={<Settings />}
              endIcon={<ExpandMore />}
              onClick={(e) => handleMenuClick(e, 'settings')}
              className="modern-menu-button"
              sx={modernButtonStyle}
            >
              Settings
            </Button>
          </Box>
          {/* Enhanced Logo Section in the center */}
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              cursor: 'pointer',
              flexGrow: 1,
              justifyContent: 'center',
              '&:hover': {
                backgroundColor: 'rgba(255, 255, 255, 0.1)',
                borderRadius: 1
              },
              p: 1,
              borderRadius: 1,
              transition: 'background-color 0.2s'
            }}
            onClick={navigateToHome}
          >
            <Box
              component="img"
              src="/Tritiq.png"
              alt="TritiQ"
              sx={{
                width: 40,
                height: 40,
                mr: 1,
                objectFit: 'contain'
              }}
            />
            <Typography variant="h6" component="div" sx={{ fontWeight: 'bold' }}>
              {companyData?.name || 'ERP'}
            </Typography>
          </Box>
          {/* Search bar on the right */}
          <Box sx={{ display: 'flex', alignItems: 'center', position: 'relative', ml: 2 }} ref={searchRef}>
            <InputBase
              placeholder="Search…"
              value={searchQuery}
              onChange={(e) => handleSearch(e.target.value)}
              startAdornment={<SearchIcon />}
              sx={{
                color: 'inherit',
                ml: 1,
                '& .MuiInputBase-input': {
                  padding: '8px 8px 8px 0',
                  transition: 'width 0.3s',
                  width: searchQuery ? '200px' : '100px',
                },
              }}
            />
            {renderSearchResults()}
          </Box>
          <IconButton
            color="inherit"
            onClick={handleUserMenuClick}
            sx={{ ml: 2 }}
          >
            <AccountCircle />
          </IconButton>
        </Toolbar>
      </AppBar>
      {renderMegaMenu()}
      {renderSubMenu()}
      <Menu
        anchorEl={userMenuAnchor}
        open={Boolean(userMenuAnchor)}
        onClose={handleUserMenuClose}
        PaperProps={{
          sx: {
            borderRadius: 2,
            boxShadow: '0 10px 40px rgba(0, 0, 0, 0.15)',
            border: '1px solid',
            borderColor: 'divider',
            minWidth: 200,
            '& .MuiMenuItem-root': {
              borderRadius: 1,
              margin: '2px 8px',
              transition: 'all 0.2s ease-in-out',
              '&:hover': {
                backgroundColor: 'primary.50',
                transform: 'translateX(4px)',
              }
            }
          }
        }}
        MenuListProps={{
          sx: {
            padding: 1
          }
        }}
      >
        <MenuItem onClick={handleUserMenuClose}>
          <Typography variant="body2">
            {user?.full_name || user?.email || 'User'}
          </Typography>
        </MenuItem>
        <MenuItem onClick={handleUserMenuClose}>
          <Typography variant="body2" color="textSecondary">
            Role: {user?.role || 'Standard User'}
          </Typography>
        </MenuItem>
        <Divider />
        <MenuItem onClick={() => router.push('/profile')}>
          Profile Settings
        </MenuItem>
        <MenuItem onClick={onLogout}>
          Logout
        </MenuItem>
      </Menu>
      {/* Organization License Creation Modal */}
      <CreateOrganizationLicenseModal
        open={createLicenseModalOpen}
        onClose={() => setCreateLicenseModalOpen(false)}
        onSuccess={(result) => {
          console.log('License created:', result);
          // You might want to show a success notification here
        }}
      />
    </>
  );
};
export default MegaMenu;