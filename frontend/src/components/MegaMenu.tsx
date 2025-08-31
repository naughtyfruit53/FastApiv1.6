'use client';

import React, { useState, useEffect } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Menu,
  MenuItem,
  Box,
  Paper,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  IconButton,
  Avatar,
  ListItemButton,
  Grid,
  Tooltip
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
  // New icons for CRM, Marketing, and Service Desk
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
  // New icons for Task Management, Calendar, and Mail
  Task,
  CalendarToday,
  EventNote,
  Alarm,
  AccessTime,
  CheckBox,
  PlayArrow,
  Inbox,
  Send,
  Drafts,
  Archive,
  Label,
  AttachFile
} from '@mui/icons-material';
import { useRouter } from 'next/navigation';
import CreateOrganizationLicenseModal from './CreateOrganizationLicenseModal';
import { isAppSuperAdmin, isOrgSuperAdmin, canManageUsers, canShowUserManagementInMegaMenu } from '../types/user.types';
import { useQuery, useQueryClient } from '@tanstack/react-query';
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
  const router = useRouter();
  const queryClient = useQueryClient();

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

  // Don't render if not visible
  if (!isVisible) {
    return null;
  }

  const handleMenuClick = (event: React.MouseEvent<HTMLElement>, menuName: string) => {
    setAnchorEl(event.currentTarget);
    setActiveMenu(menuName);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setActiveMenu(null);
  };

  const handleSubClick = (event: React.MouseEvent<HTMLElement>, category: any) => {
    setSubAnchorEl(event.currentTarget);
    setActiveSubCategory(category);
  };

  const handleSubClose = () => {
    setSubAnchorEl(null);
    setActiveSubCategory(null);
  };

  const handleUserMenuClick = (event: React.MouseEvent<HTMLElement>) => {
    setUserMenuAnchor(event.currentTarget);
  };

  const handleUserMenuClose = () => {
    setUserMenuAnchor(null);
  };

  const navigateTo = (path: string) => {
    router.push(path);
    handleMenuClose();
    handleSubClose();
  };

  const _handleCreateOrgLicense = () => {
    // For now, we'll use a state to control the modal
    // In a full implementation, this would be managed by parent component
    setCreateLicenseModalOpen(true);
    handleMenuClose();
  };

  const handleDemoMode = () => {
    // Navigate to demo page
    router.push('/demo');
    handleMenuClose();
  };

  // Check user roles using proper utility functions
  const isSuperAdmin = isAppSuperAdmin(user);
  const _isOrgAdmin = isOrgSuperAdmin(user);
  const _canManage = canManageUsers(user);
  const _canShowUserMgmtInMenu = canShowUserManagementInMegaMenu(user);

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

  // Enhanced logo navigation function
  const navigateToHome = () => {
    router.push('/dashboard');
    handleMenuClose();
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

  // Function to handle contact support (placeholder - open email or ticket)
  const handleContactSupport = () => {
    // In production, this could open a support ticket form or email client
    window.location.href = 'mailto:support@tritiq.com?subject=Module Activation Request&body=Please activate the Service CRM module for my organization.';
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
    // Finance & Accounting menu
    finance: {
      title: 'Finance & Accounting',
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
            { name: 'Trial Balance', path: '/reports/trial-balance', icon: <BarChart /> },
            { name: 'Profit & Loss', path: '/reports/profit-loss', icon: <TrendingUp /> },
            { name: 'Balance Sheet', path: '/reports/balance-sheet', icon: <Assessment /> },
            { name: 'Cash Flow', path: '/reports/cash-flow', icon: <AccountBalance /> }
          ]
        },
        {
          title: 'Analytics & KPIs',
          items: [
            { name: 'Finance Dashboard', path: '/finance-dashboard', icon: <Analytics /> },
            { name: 'Financial KPIs', path: '/financial-kpis', icon: <TrendingUp /> },
            { name: 'Expense Analysis', path: '/expense-analysis', icon: <BarChart /> },
            { name: 'Cash Flow Forecast', path: '/cash-flow-forecast', icon: <Assessment /> }
          ]
        }
      ]
    },
    // Combined Reports & Analytics menu
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
    crm: {
      title: 'CRM',
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
    // Enhanced Service Desk Module
    serviceDesk: {
      title: 'Service Desk',
      icon: <ServiceDeskIcon />,
      sections: [
        {
          title: 'Helpdesk & Ticketing',
          items: [
            { name: 'Service Desk Dashboard', path: '/service-desk', icon: <Dashboard /> },
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
    // Combined Workspace menu
    workspace: {
      title: 'Workspace',
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
        },
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

  const renderMegaMenu = () => {
    if (!activeMenu || !menuItems[activeMenu as keyof typeof menuItems]) {return null;}

    const menu = menuItems[activeMenu as keyof typeof menuItems];

    // Filter menu items based on user permissions
    const filterMenuItems = (section: any) => {
      return section.items.filter((item: any) => {
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

    const filteredSections = menu.sections.map(section => ({
      ...section,
      items: filterMenuItems(section)
    })).filter(section => section.items.length > 0);

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
            width: 600,
            maxHeight: 500,
            mt: 1,
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
        <Typography variant="h6" sx={{ mb: 2, color: 'primary.main' }}>
          {menu.title}
        </Typography>
        <Grid container spacing={2}>
          {filteredSections.map((section, index) => (
            <Grid
              key={index}
              size={{
                xs: 12,
                sm: 6,
                md: 4
              }}>
              <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 'bold', color: 'text.secondary' }}>
                {section.title}
              </Typography>
              <List dense>
                {section.items.map((item: any, itemIndex: number) => (
                  <ListItemButton
                    key={itemIndex}
                    onClick={(e) => item.subItems ? handleSubClick(e, item) : navigateTo(item.path)}
                    sx={{
                      borderRadius: 1,
                      mb: 0.5,
                      '&:hover': {
                        backgroundColor: 'primary.light',
                        color: 'primary.contrastText'
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
              {index < filteredSections.length - 1 && <Divider sx={{ mt: 1 }} />}
            </Grid>
          ))}
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
          {/* Enhanced Logo Section */}
          <Box 
            sx={{ 
              display: 'flex', 
              alignItems: 'center', 
              cursor: 'pointer',
              mr: 3,
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

          <Box sx={{ display: 'flex', alignItems: 'center', flexGrow: 1 }}>
            {/* Different menu structures based on user type */}
            {isSuperAdmin ? (
              <>
                {/* App Super Admins: Dashboard, Demo, Settings (with Admin submenu) */}
                <Button
                  color="inherit"
                  startIcon={<Dashboard />}
                  onClick={() => router.push('/dashboard')}
                  className="modern-menu-button"
                  sx={modernButtonStyle}
                >
                  Dashboard
                </Button>
                <Button
                  color="inherit"
                  startIcon={<DeveloperMode />}
                  onClick={handleDemoMode}
                  className="modern-menu-button"
                  sx={modernButtonStyle}
                >
                  Demo
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
              </>
            ) : (
              <>
                {/* Organization users: Master Data with direct navigation to individual pages */}
                
                {/* Master Data - Top level menu with direct navigation (no hub) */}
                <Button
                  color="inherit"
                  startIcon={<People />}
                  endIcon={<ExpandMore />}
                  onClick={(e) => handleMenuClick(e, 'masterData')}
                  sx={modernButtonStyle}
                >
                  Master Data
                </Button>
                
                {/* ERP Menu - Contains inventory and vouchers */}
                <Button
                  color="inherit"
                  startIcon={<Business />}
                  endIcon={<ExpandMore />}
                  onClick={(e) => handleMenuClick(e, 'erp')}
                  sx={modernButtonStyle}
                >
                  ERP
                </Button>

                {/* Finance & Accounting Menu */}
                <Button
                  color="inherit"
                  startIcon={<AccountBalance />}
                  endIcon={<ExpandMore />}
                  onClick={(e) => handleMenuClick(e, 'finance')}
                  sx={modernButtonStyle}
                >
                  Finance
                </Button>

                {/* Combined Reports & Analytics menu */}
                <Button
                  color="inherit"
                  startIcon={<Assessment />}
                  endIcon={<ExpandMore />}
                  onClick={(e) => handleMenuClick(e, 'reportsAnalytics')}
                  sx={modernButtonStyle}
                >
                  Reports & Analytics
                </Button>

                {/* CRM Menu - Contains both Sales CRM and Service CRM as sub-categories */}
                <Button
                  color="inherit"
                  startIcon={<Person />}
                  endIcon={<ExpandMore />}
                  onClick={(e) => handleMenuClick(e, 'crm')}
                  sx={modernButtonStyle}
                >
                  CRM
                </Button>

                {/* HR Management Menu */}
                <Button
                  color="inherit"
                  startIcon={<Groups />}
                  endIcon={<ExpandMore />}
                  onClick={(e) => handleMenuClick(e, 'hrManagement')}
                  sx={modernButtonStyle}
                >
                  HR Management
                </Button>

                {/* Marketing Menu */}
                <Button
                  color="inherit"
                  startIcon={<Campaign />}
                  endIcon={<ExpandMore />}
                  onClick={(e) => handleMenuClick(e, 'marketing')}
                  sx={modernButtonStyle}
                >
                  Marketing
                </Button>

                {/* Service Desk Menu */}
                <Button
                  color="inherit"
                  startIcon={<ServiceDeskIcon />}
                  endIcon={<ExpandMore />}
                  onClick={(e) => handleMenuClick(e, 'serviceDesk')}
                  sx={modernButtonStyle}
                >
                  Service Desk
                </Button>

                {/* Workspace Menu - Combined Tasks, Calendar, Mail */}
                <Button
                  color="inherit"
                  startIcon={<Task />}
                  endIcon={<ExpandMore />}
                  onClick={(e) => handleMenuClick(e, 'workspace')}
                  sx={modernButtonStyle}
                >
                  Workspace
                </Button>

                {/* Settings with Administration as submenu */}
                <Button
                  color="inherit"
                  startIcon={<Settings />}
                  endIcon={<ExpandMore />}
                  onClick={(e) => handleMenuClick(e, 'settings')}
                  sx={modernButtonStyle}
                >
                  Settings
                </Button>
              </>
            )}
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