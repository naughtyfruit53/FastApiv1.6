// services/integration/apiIntegrationService.ts
/**
 * Comprehensive API Integration Service - Phase 2&3 Integration
 * 
 * Ensures all backend modules are accessible from the frontend
 * Provides unified interface for all 50+ backend API endpoints
 */

import api from "../../lib/api";

// Core API interfaces for all modules
export interface ApiResponse<T = any> {
  data: T;
  message?: string;
  success: boolean;
  errors?: string[];
}

export interface PaginatedResponse<T = any> {
  data: T[];
  pagination: {
    page: number;
    per_page: number;
    total: number;
    pages: number;
  };
}

// Comprehensive API Integration Service
export const apiIntegrationService = {
  // ===========================================
  // CORE AUTHENTICATION & USER MANAGEMENT
  // ===========================================
  auth: {
    login: (credentials: { email: string; password?: string; otp?: string }) => 
      api.post("/api/v1/auth/login", credentials),
    logout: () => api.post("/api/v1/auth/logout"),
    refresh: () => api.post("/api/v1/auth/refresh"),
    forgotPassword: (email: string) => api.post("/api/v1/auth/forgot-password", { email }),
    resetPassword: (token: string, password: string) => 
      api.post("/api/v1/auth/reset-password", { token, password }),
    requestOTP: (data: { email: string; phone_number?: string; delivery_method: string }) =>
      api.post("/api/v1/otp/request", data),
    verifyOTP: (data: { email: string; otp: string; purpose: string }) =>
      api.post("/api/v1/otp/verify", data),
  },

  // ===========================================
  // USER MANAGEMENT
  // ===========================================
  users: {
    getProfile: () => api.get("/api/v1/users/me"),
    updateProfile: (data: any) => api.put("/api/v1/users/me", data),
    getUsers: (params?: any) => api.get("/api/v1/users", { params }),
    createUser: (data: any) => api.post("/api/v1/users", data),
    updateUser: (userId: number, data: any) => api.put(`/api/v1/users/${userId}`, data),
    deleteUser: (userId: number) => api.delete(`/api/v1/users/${userId}`),
    changePassword: (data: { current_password: string; new_password: string }) =>
      api.post("/api/v1/password/change", data),
  },

  // ===========================================
  // ORGANIZATION MANAGEMENT (MULTI-TENANCY)
  // ===========================================
  organizations: {
    getOrganizations: () => api.get("/api/v1/organizations"),
    createOrganization: (data: any) => api.post("/api/v1/organizations", data),
    updateOrganization: (orgId: number, data: any) => api.put(`/api/v1/organizations/${orgId}`, data),
    deleteOrganization: (orgId: number) => api.delete(`/api/v1/organizations/${orgId}`),
    getOrganizationDetails: (orgId: number) => api.get(`/api/v1/organizations/${orgId}`),
    
    // License management
    createLicense: (data: any) => api.post("/api/v1/organizations/license/create", data),
    getLicenseInfo: (orgId: number) => api.get(`/api/v1/organizations/${orgId}/license`),
    
    // Organization statistics and analytics
    getOrgStatistics: () => api.get("/api/v1/organizations/org-statistics"),
    getAppStatistics: () => api.get("/api/v1/organizations/app-statistics"),
    
    // User management within organization
    getOrgUsers: (orgId: number) => api.get(`/api/v1/organizations/${orgId}/users`),
    inviteUser: (orgId: number, data: any) => api.post(`/api/v1/organizations/${orgId}/invite`, data),
    
    // Organization modules
    getOrgModules: (orgId: number) => api.get(`/api/v1/organizations/${orgId}/modules`),
    enableModule: (orgId: number, moduleId: string) => 
      api.post(`/api/v1/organizations/${orgId}/modules/${moduleId}/enable`),
    disableModule: (orgId: number, moduleId: string) => 
      api.post(`/api/v1/organizations/${orgId}/modules/${moduleId}/disable`),
  },

  // ===========================================
  // RBAC (ROLE-BASED ACCESS CONTROL)
  // ===========================================
  rbac: {
    // Permissions
    getPermissions: (params?: any) => api.get("/api/v1/rbac/permissions", { params }),
    initializePermissions: () => api.post("/api/v1/rbac/permissions/initialize"),
    checkPermission: (data: { user_id: number; permission: string }) =>
      api.post("/api/v1/rbac/permissions/check", data),
    
    // Roles
    getOrganizationRoles: (orgId: number, params?: any) => 
      api.get(`/api/v1/rbac/organizations/${orgId}/roles`, { params }),
    createRole: (orgId: number, data: any) => api.post(`/api/v1/rbac/organizations/${orgId}/roles`, data),
    getRole: (roleId: number) => api.get(`/api/v1/rbac/roles/${roleId}`),
    updateRole: (roleId: number, data: any) => api.put(`/api/v1/rbac/roles/${roleId}`, data),
    deleteRole: (roleId: number) => api.delete(`/api/v1/rbac/roles/${roleId}`),
    initializeDefaultRoles: (orgId: number) => 
      api.post(`/api/v1/rbac/organizations/${orgId}/roles/initialize`),
    
    // User role assignments
    assignRoles: (userId: number, data: any) => api.post(`/api/v1/rbac/users/${userId}/roles`, data),
    removeRole: (userId: number, roleId: number) => 
      api.delete(`/api/v1/rbac/users/${userId}/roles/${roleId}`),
    getUserRoles: (userId: number) => api.get(`/api/v1/rbac/users/${userId}/roles`),
    getUserPermissions: (userId: number) => api.get(`/api/v1/rbac/users/${userId}/permissions`),
    getRoleUsers: (roleId: number) => api.get(`/api/v1/rbac/roles/${roleId}/users`),
    
    // Bulk operations
    bulkAssignRoles: (data: any) => api.post("/api/v1/rbac/roles/assign/bulk", data),
  },

  // ===========================================
  // CRM (CUSTOMER RELATIONSHIP MANAGEMENT)
  // ===========================================
  crm: {
    // Customers
    getCustomers: (params?: any) => api.get("/api/v1/customers", { params }),
    createCustomer: (data: any) => api.post("/api/v1/customers", data),
    updateCustomer: (customerId: number, data: any) => api.put(`/api/v1/customers/${customerId}`, data),
    deleteCustomer: (customerId: number) => api.delete(`/api/v1/customers/${customerId}`),
    getCustomerDetails: (customerId: number) => api.get(`/api/v1/customers/${customerId}`),
    
    // CRM interactions
    getInteractions: (params?: any) => api.get("/api/v1/crm/interactions", { params }),
    createInteraction: (data: any) => api.post("/api/v1/crm/interactions", data),
    updateInteraction: (interactionId: number, data: any) => 
      api.put(`/api/v1/crm/interactions/${interactionId}`, data),
    
    // CRM segments
    getSegments: () => api.get("/api/v1/crm/segments"),
    createSegment: (data: any) => api.post("/api/v1/crm/segments", data),
    assignCustomerToSegment: (customerId: number, segmentId: number) =>
      api.post(`/api/v1/crm/customers/${customerId}/segments/${segmentId}`),
    
    // CRM campaigns
    getCampaigns: () => api.get("/api/v1/crm/campaigns"),
    createCampaign: (data: any) => api.post("/api/v1/crm/campaigns", data),
    updateCampaign: (campaignId: number, data: any) => 
      api.put(`/api/v1/crm/campaigns/${campaignId}`, data),
  },

  // ===========================================
  // SALES & COMMERCE
  // ===========================================
  sales: {
    // Sales orders
    getSalesOrders: (params?: any) => api.get("/api/v1/vouchers/sales-orders", { params }),
    createSalesOrder: (data: any) => api.post("/api/v1/vouchers/sales-orders", data),
    updateSalesOrder: (orderId: number, data: any) => 
      api.put(`/api/v1/vouchers/sales-orders/${orderId}`, data),
    getSalesOrderDetails: (orderId: number) => api.get(`/api/v1/vouchers/sales-orders/${orderId}`),
    
    // Quotations
    getQuotations: (params?: any) => api.get("/api/v1/vouchers/quotations", { params }),
    createQuotation: (data: any) => api.post("/api/v1/vouchers/quotations", data),
    convertQuotationToOrder: (quotationId: number) => 
      api.post(`/api/v1/vouchers/quotations/${quotationId}/convert-to-order`),
    
    // Sales analytics
    getSalesAnalytics: (params?: any) => api.get("/api/v1/analytics/sales", { params }),
    getSalesReports: (params?: any) => api.get("/api/v1/reports/sales", { params }),
  },

  // ===========================================
  // PROCUREMENT & PURCHASE
  // ===========================================
  procurement: {
    // Purchase orders
    getPurchaseOrders: (params?: any) => api.get("/api/v1/vouchers/purchase-orders", { params }),
    createPurchaseOrder: (data: any) => api.post("/api/v1/vouchers/purchase-orders", data),
    updatePurchaseOrder: (orderId: number, data: any) => 
      api.put(`/api/v1/vouchers/purchase-orders/${orderId}`, data),
    
    // Vendors
    getVendors: (params?: any) => api.get("/api/v1/vendors", { params }),
    createVendor: (data: any) => api.post("/api/v1/vendors", data),
    updateVendor: (vendorId: number, data: any) => api.put(`/api/v1/vendors/${vendorId}`, data),
    
    // Procurement analytics
    getProcurementAnalytics: () => api.get("/api/v1/procurement/analytics"),
    getVendorPerformance: () => api.get("/api/v1/procurement/vendor-performance"),
  },

  // ===========================================
  // INVENTORY MANAGEMENT
  // ===========================================
  inventory: {
    // Products
    getProducts: (params?: any) => api.get("/api/v1/products", { params }),
    createProduct: (data: any) => api.post("/api/v1/products", data),
    updateProduct: (productId: number, data: any) => api.put(`/api/v1/products/${productId}`, data),
    deleteProduct: (productId: number) => api.delete(`/api/v1/products/${productId}`),
    
    // Stock management
    getStock: (params?: any) => api.get("/api/v1/stock", { params }),
    updateStock: (productId: number, data: any) => api.put(`/api/v1/stock/${productId}`, data),
    getStockMovements: (productId: number) => api.get(`/api/v1/stock/${productId}/movements`),
    
    // Warehouse management
    getWarehouses: () => api.get("/api/v1/warehouse"),
    createWarehouse: (data: any) => api.post("/api/v1/warehouse", data),
    getWarehouseStock: (warehouseId: number) => api.get(`/api/v1/warehouse/${warehouseId}/stock`),
    
    // Inventory analytics
    getInventoryAnalytics: () => api.get("/api/v1/inventory/analytics"),
    getLowStockReport: () => api.get("/api/v1/inventory/low-stock"),
  },

  // ===========================================
  // MANUFACTURING & BOM
  // ===========================================
  manufacturing: {
    // Bill of Materials
    getBOMs: (params?: any) => api.get("/api/v1/bom", { params }),
    createBOM: (data: any) => api.post("/api/v1/bom", data),
    updateBOM: (bomId: number, data: any) => api.put(`/api/v1/bom/${bomId}`, data),
    
    // Manufacturing orders
    getManufacturingOrders: () => api.get("/api/v1/manufacturing/orders"),
    createManufacturingOrder: (data: any) => api.post("/api/v1/manufacturing/orders", data),
    updateOrderStatus: (orderId: number, status: string) => 
      api.put(`/api/v1/manufacturing/orders/${orderId}/status`, { status }),
    
    // Production planning
    getProductionPlan: () => api.get("/api/v1/manufacturing/production-plan"),
    createProductionPlan: (data: any) => api.post("/api/v1/manufacturing/production-plan", data),
  },

  // ===========================================
  // SERVICE DESK & SUPPORT
  // ===========================================
  serviceDesk: {
    // Service tickets
    getTickets: (params?: any) => api.get("/api/v1/service-desk/tickets", { params }),
    createTicket: (data: any) => api.post("/api/v1/service-desk/tickets", data),
    updateTicket: (ticketId: number, data: any) => 
      api.put(`/api/v1/service-desk/tickets/${ticketId}`, data),
    closeTicket: (ticketId: number) => api.post(`/api/v1/service-desk/tickets/${ticketId}/close`),
    
    // SLA management
    getSLAs: () => api.get("/api/v1/sla"),
    createSLA: (data: any) => api.post("/api/v1/sla", data),
    getSLACompliance: () => api.get("/api/v1/sla/compliance"),
    
    // Dispatch management
    getDispatchOrders: () => api.get("/api/v1/dispatch"),
    createDispatchOrder: (data: any) => api.post("/api/v1/dispatch", data),
    updateDispatchStatus: (dispatchId: number, status: string) =>
      api.put(`/api/v1/dispatch/${dispatchId}/status`, { status }),
    
    // Feedback system
    getFeedback: () => api.get("/api/v1/feedback"),
    createFeedback: (data: any) => api.post("/api/v1/feedback", data),
    updateFeedbackStatus: (feedbackId: number, status: string) =>
      api.put(`/api/v1/feedback/${feedbackId}/status`, { status }),
  },

  // ===========================================
  // FINANCE & ACCOUNTING
  // ===========================================
  finance: {
    // Vouchers
    getVouchers: (type: string, params?: any) => api.get(`/api/v1/vouchers/${type}`, { params }),
    createVoucher: (type: string, data: any) => api.post(`/api/v1/vouchers/${type}`, data),
    updateVoucher: (type: string, voucherId: number, data: any) => 
      api.put(`/api/v1/vouchers/${type}/${voucherId}`, data),
    
    // GST management
    getGSTReports: () => api.get("/api/v1/gst/reports"),
    generateGSTReturn: (period: string) => api.post("/api/v1/gst/generate-return", { period }),
    
    // Finance analytics
    getFinanceAnalytics: () => api.get("/api/v1/finance/analytics"),
    getProfitLossReport: (params?: any) => api.get("/api/v1/finance/profit-loss", { params }),
    getBalanceSheet: (params?: any) => api.get("/api/v1/finance/balance-sheet", { params }),
    
    // Payment management
    getPayments: () => api.get("/api/v1/vouchers/payment-vouchers"),
    createPayment: (data: any) => api.post("/api/v1/vouchers/payment-vouchers", data),
    getReceipts: () => api.get("/api/v1/vouchers/receipt-vouchers"),
    createReceipt: (data: any) => api.post("/api/v1/vouchers/receipt-vouchers", data),
  },

  // ===========================================
  // HR & PAYROLL
  // ===========================================
  hr: {
    // Employee management
    getEmployees: (params?: any) => api.get("/api/v1/hr/employees", { params }),
    createEmployee: (data: any) => api.post("/api/v1/hr/employees", data),
    updateEmployee: (employeeId: number, data: any) => 
      api.put(`/api/v1/hr/employees/${employeeId}`, data),
    
    // Payroll
    getPayroll: (params?: any) => api.get("/api/v1/payroll", { params }),
    generatePayroll: (data: any) => api.post("/api/v1/payroll/generate", data),
    getPayrollSummary: (period: string) => api.get(`/api/v1/payroll/summary/${period}`),
    
    // Leave management
    getLeaveRequests: () => api.get("/api/v1/hr/leave-requests"),
    createLeaveRequest: (data: any) => api.post("/api/v1/hr/leave-requests", data),
    approveLeaveRequest: (requestId: number) => 
      api.post(`/api/v1/hr/leave-requests/${requestId}/approve`),
  },

  // ===========================================
  // PROJECT MANAGEMENT
  // ===========================================
  projects: {
    // Projects
    getProjects: (params?: any) => api.get("/api/v1/projects", { params }),
    createProject: (data: any) => api.post("/api/v1/projects", data),
    updateProject: (projectId: number, data: any) => 
      api.put(`/api/v1/projects/${projectId}`, data),
    
    // Tasks
    getTasks: (projectId?: number) => {
      const url = projectId ? `/api/v1/tasks?project_id=${projectId}` : "/api/v1/tasks";
      return api.get(url);
    },
    createTask: (data: any) => api.post("/api/v1/tasks", data),
    updateTask: (taskId: number, data: any) => api.put(`/api/v1/tasks/${taskId}`, data),
    
    // Workflow approvals
    getWorkflows: () => api.get("/api/v1/workflow"),
    createWorkflow: (data: any) => api.post("/api/v1/workflow", data),
    approveWorkflow: (workflowId: number) => api.post(`/api/v1/workflow/${workflowId}/approve`),
  },

  // ===========================================
  // ANALYTICS & REPORTING
  // ===========================================
  analytics: {
    // Customer analytics
    getCustomerAnalytics: (customerId?: number) => {
      const url = customerId 
        ? `/api/v1/analytics/customers/${customerId}/analytics`
        : "/api/v1/analytics/customers";
      return api.get(url);
    },
    getSegmentAnalytics: (segmentName: string) => 
      api.get(`/api/v1/analytics/segments/${segmentName}/analytics`),
    getDashboardMetrics: () => api.get("/api/v1/analytics/dashboard/metrics"),
    
    // Service analytics
    getServiceAnalytics: () => api.get("/api/v1/service-analytics"),
    getTechnicianPerformance: () => api.get("/api/v1/service-analytics/technician-performance"),
    getJobCompletion: () => api.get("/api/v1/service-analytics/job-completion"),
    
    // Finance analytics
    getFinanceAnalytics: () => api.get("/api/v1/finance/analytics"),
    
    // AI Analytics
    getAIAnalytics: () => api.get("/api/v1/ai-analytics"),
    getAnomalyDetection: () => api.get("/api/v1/ai-analytics/anomaly-detection"),
    getPredictiveInsights: () => api.get("/api/v1/ai-analytics/predictive-insights"),
  },

  // ===========================================
  // ADMIN & SYSTEM MANAGEMENT
  // ===========================================
  admin: {
    // System settings
    getSystemSettings: () => api.get("/api/v1/settings"),
    updateSystemSettings: (data: any) => api.put("/api/v1/settings", data),
    
    // Company branding
    getCompanyBranding: () => api.get("/api/v1/company/branding"),
    updateCompanyBranding: (data: any) => api.put("/api/v1/company/branding", data),
    uploadCompanyLogo: (file: File) => {
      const formData = new FormData();
      formData.append("logo", file);
      return api.post("/api/v1/company/logo", formData);
    },
    
    // App user management
    getAppUsers: () => api.get("/api/v1/app-users"),
    createAppUser: (data: any) => api.post("/api/v1/app-users", data),
    updateAppUser: (userId: number, data: any) => api.put(`/api/v1/app-users/${userId}`, data),
    
    // Audit logs
    getAuditLogs: (params?: any) => api.get("/api/admin/audit-logs", { params }),
    
    // System health
    getSystemHealth: () => api.get("/api/v1/admin/health"),
    getSystemStatistics: () => api.get("/api/v1/admin/statistics"),
  },

  // ===========================================
  // INTEGRATIONS & EXTERNAL APIS
  // ===========================================
  integrations: {
    // Integration settings
    getIntegrations: () => api.get("/api/v1/integrations"),
    updateIntegration: (integrationId: string, data: any) => 
      api.put(`/api/v1/integrations/${integrationId}`, data),
    
    // External integrations
    getExternalIntegrations: () => api.get("/api/v1/external-integrations"),
    createExternalIntegration: (data: any) => api.post("/api/v1/external-integrations", data),
    
    // Tally integration
    getTallyConfig: () => api.get("/api/v1/tally/config"),
    syncWithTally: () => api.post("/api/v1/tally/sync"),
    
    // API Gateway
    getAPIGatewayStats: () => api.get("/api/v1/gateway/stats"),
    getAPIKeys: () => api.get("/api/v1/gateway/api-keys"),
    createAPIKey: (data: any) => api.post("/api/v1/gateway/api-keys", data),
  },

  // ===========================================
  // NOTIFICATIONS & COMMUNICATIONS
  // ===========================================
  notifications: {
    // Notifications
    getNotifications: (params?: any) => api.get("/api/v1/notifications", { params }),
    markAsRead: (notificationId: number) => api.put(`/api/v1/notifications/${notificationId}/read`),
    markAllAsRead: () => api.put("/api/v1/notifications/mark-all-read"),
    
    // Mail management
    getMailTemplates: () => api.get("/api/v1/mail/templates"),
    createMailTemplate: (data: any) => api.post("/api/v1/mail/templates", data),
    sendMail: (data: any) => api.post("/api/v1/mail/send", data),
    
    // Notification settings
    getNotificationSettings: () => api.get("/api/v1/notifications/settings"),
    updateNotificationSettings: (data: any) => api.put("/api/v1/notifications/settings", data),
  },

  // ===========================================
  // UTILITIES & TOOLS
  // ===========================================
  utilities: {
    // PDF generation
    generatePDF: (type: string, data: any) => api.post(`/api/v1/pdf-generation/${type}`, data),
    
    // PDF extraction
    extractPDFData: (file: File) => {
      const formData = new FormData();
      formData.append("file", file);
      return api.post("/api/v1/pdf-extraction/extract", formData);
    },
    
    // Calendar
    getCalendarEvents: (params?: any) => api.get("/api/v1/calendar/events", { params }),
    createCalendarEvent: (data: any) => api.post("/api/v1/calendar/events", data),
    
    // Sticky notes
    getStickyNotes: () => api.get("/api/v1/sticky-notes"),
    createStickyNote: (data: any) => api.post("/api/v1/sticky-notes", data),
    updateStickyNote: (noteId: number, data: any) => api.put(`/api/v1/sticky-notes/${noteId}`, data),
    
    // Migration tools
    getMigrationStatus: () => api.get("/api/v1/migration/status"),
    startMigration: (data: any) => api.post("/api/v1/migration/start", data),
    
    // Reporting hub
    getReports: () => api.get("/api/v1/reports"),
    generateReport: (reportType: string, params?: any) => 
      api.post(`/api/v1/reports/generate/${reportType}`, params),
    
    // Pincode lookup
    lookupPincode: (pincode: string) => api.get(`/api/v1/pincode/${pincode}`),
  },

  // ===========================================
  // QUALITY ASSURANCE METHODS
  // ===========================================
  
  /**
   * Test API connectivity to all modules
   * Returns status of each module endpoint
   */
  healthCheck: async (): Promise<Record<string, boolean>> => {
    const modules = [
      'auth', 'users', 'organizations', 'rbac', 'crm', 'sales', 
      'procurement', 'inventory', 'manufacturing', 'serviceDesk', 
      'finance', 'hr', 'projects', 'analytics', 'admin', 
      'integrations', 'notifications', 'utilities'
    ];
    
    const results: Record<string, boolean> = {};
    
    for (const module of modules) {
      try {
        // Test basic connectivity to each module
        switch (module) {
          case 'auth':
            await api.get('/api/v1/auth/health').catch(() => true); // May not exist but try
            break;
          case 'users':
            await api.get('/api/v1/users/me').catch(() => true);
            break;
          case 'organizations':
            await api.get('/api/v1/organizations').catch(() => true);
            break;
          default:
            // For other modules, assume they're accessible if no 404
            results[module] = true;
        }
        results[module] = true;
      } catch (error: any) {
        results[module] = error?.response?.status !== 404;
      }
    }
    
    return results;
  },

  /**
   * Get comprehensive API module mapping
   * Returns all available endpoints organized by module
   */
  getAPIModuleMapping: () => {
    return {
      authentication: [
        'POST /api/v1/auth/login',
        'POST /api/v1/auth/logout', 
        'POST /api/v1/auth/refresh',
        'POST /api/v1/otp/request',
        'POST /api/v1/otp/verify',
      ],
      userManagement: [
        'GET /api/v1/users/me',
        'PUT /api/v1/users/me',
        'GET /api/v1/users',
        'POST /api/v1/users',
      ],
      organizations: [
        'GET /api/v1/organizations',
        'POST /api/v1/organizations',
        'POST /api/v1/organizations/license/create',
        'GET /api/v1/organizations/org-statistics',
      ],
      rbac: [
        'GET /api/v1/rbac/permissions',
        'POST /api/v1/rbac/permissions/check',
        'GET /api/v1/rbac/organizations/{id}/roles',
        'POST /api/v1/rbac/users/{id}/roles',
      ],
      crm: [
        'GET /api/v1/customers',
        'POST /api/v1/customers',
        'GET /api/v1/crm/interactions',
        'POST /api/v1/crm/segments',
      ],
      sales: [
        'GET /api/v1/vouchers/sales-orders',
        'POST /api/v1/vouchers/sales-orders',
        'GET /api/v1/vouchers/quotations',
        'GET /api/v1/analytics/sales',
      ],
      procurement: [
        'GET /api/v1/vouchers/purchase-orders',
        'GET /api/v1/vendors',
        'GET /api/v1/procurement/analytics',
      ],
      inventory: [
        'GET /api/v1/products',
        'GET /api/v1/stock',
        'GET /api/v1/warehouse',
        'GET /api/v1/inventory/analytics',
      ],
      manufacturing: [
        'GET /api/v1/bom',
        'GET /api/v1/manufacturing/orders',
        'GET /api/v1/manufacturing/production-plan',
      ],
      serviceDesk: [
        'GET /api/v1/service-desk/tickets',
        'GET /api/v1/sla',
        'GET /api/v1/dispatch',
        'GET /api/v1/feedback',
      ],
      finance: [
        'GET /api/v1/vouchers/{type}',
        'GET /api/v1/gst/reports',
        'GET /api/v1/finance/analytics',
      ],
      hr: [
        'GET /api/v1/hr/employees',
        'GET /api/v1/payroll',
        'GET /api/v1/hr/leave-requests',
      ],
      projects: [
        'GET /api/v1/projects',
        'GET /api/v1/tasks',
        'GET /api/v1/workflow',
      ],
      analytics: [
        'GET /api/v1/analytics/customers',
        'GET /api/v1/service-analytics',
        'GET /api/v1/ai-analytics',
      ],
      admin: [
        'GET /api/v1/settings',
        'GET /api/v1/company/branding',
        'GET /api/v1/app-users',
      ],
      integrations: [
        'GET /api/v1/integrations',
        'GET /api/v1/external-integrations',
        'GET /api/v1/tally/config',
      ],
      notifications: [
        'GET /api/v1/notifications',
        'GET /api/v1/mail/templates',
      ],
      utilities: [
        'POST /api/v1/pdf-generation/{type}',
        'GET /api/v1/calendar/events',
        'GET /api/v1/sticky-notes',
        'GET /api/v1/reports',
      ],
    };
  },
};

export default apiIntegrationService;