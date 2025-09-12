// services/integration/__tests__/apiIntegrationService.test.ts
/**
 * Comprehensive test suite for API Integration Service
 * Tests all backend module endpoints and integration functionality
 */

import { jest } from '@jest/globals';
import apiIntegrationService from '../apiIntegrationService';
import api from '../../../lib/api';

// Mock the api module
jest.mock('../../../lib/api');
const mockApi = api as jest.Mocked<typeof api>;

describe('apiIntegrationService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    
    // Default successful response
    mockApi.get.mockResolvedValue({ data: { success: true } });
    mockApi.post.mockResolvedValue({ data: { success: true } });
    mockApi.put.mockResolvedValue({ data: { success: true } });
    mockApi.delete.mockResolvedValue({ data: { success: true } });
  });

  describe('Authentication Module', () => {
    it('should handle login with credentials', async () => {
      const credentials = { email: 'test@example.com', password: 'password123' };
      
      await apiIntegrationService.auth.login(credentials);
      
      expect(mockApi.post).toHaveBeenCalledWith('/api/v1/auth/login', credentials);
    });

    it('should handle OTP login flow', async () => {
      const otpRequest = { 
        email: 'test@example.com', 
        phone_number: '+1234567890',
        delivery_method: 'sms' 
      };
      
      await apiIntegrationService.auth.requestOTP(otpRequest);
      
      expect(mockApi.post).toHaveBeenCalledWith('/api/v1/otp/request', otpRequest);
    });

    it('should handle OTP verification', async () => {
      const otpVerification = { 
        email: 'test@example.com', 
        otp: '123456',
        purpose: 'login' 
      };
      
      await apiIntegrationService.auth.verifyOTP(otpVerification);
      
      expect(mockApi.post).toHaveBeenCalledWith('/api/v1/otp/verify', otpVerification);
    });

    it('should handle logout', async () => {
      await apiIntegrationService.auth.logout();
      
      expect(mockApi.post).toHaveBeenCalledWith('/api/v1/auth/logout');
    });

    it('should handle password reset', async () => {
      await apiIntegrationService.auth.forgotPassword('test@example.com');
      
      expect(mockApi.post).toHaveBeenCalledWith('/api/v1/auth/forgot-password', { 
        email: 'test@example.com' 
      });
    });
  });

  describe('Organization Management (Multi-tenancy)', () => {
    it('should get organizations list', async () => {
      await apiIntegrationService.organizations.getOrganizations();
      
      expect(mockApi.get).toHaveBeenCalledWith('/api/v1/organizations');
    });

    it('should create new organization', async () => {
      const orgData = { name: 'Test Org', subdomain: 'test' };
      
      await apiIntegrationService.organizations.createOrganization(orgData);
      
      expect(mockApi.post).toHaveBeenCalledWith('/api/v1/organizations', orgData);
    });

    it('should create organization license', async () => {
      const licenseData = { plan: 'enterprise', users: 100 };
      
      await apiIntegrationService.organizations.createLicense(licenseData);
      
      expect(mockApi.post).toHaveBeenCalledWith('/api/v1/organizations/license/create', licenseData);
    });

    it('should get organization statistics', async () => {
      await apiIntegrationService.organizations.getOrgStatistics();
      
      expect(mockApi.get).toHaveBeenCalledWith('/api/v1/organizations/org-statistics');
    });

    it('should manage organization modules', async () => {
      const orgId = 123;
      const moduleId = 'crm';
      
      await apiIntegrationService.organizations.getOrgModules(orgId);
      expect(mockApi.get).toHaveBeenCalledWith(`/api/v1/organizations/${orgId}/modules`);

      await apiIntegrationService.organizations.enableModule(orgId, moduleId);
      expect(mockApi.post).toHaveBeenCalledWith(`/api/v1/organizations/${orgId}/modules/${moduleId}/enable`);

      await apiIntegrationService.organizations.disableModule(orgId, moduleId);
      expect(mockApi.post).toHaveBeenCalledWith(`/api/v1/organizations/${orgId}/modules/${moduleId}/disable`);
    });
  });

  describe('RBAC Module', () => {
    it('should manage permissions', async () => {
      const params = { module: 'crm', action: 'view' };
      
      await apiIntegrationService.rbac.getPermissions(params);
      expect(mockApi.get).toHaveBeenCalledWith('/api/v1/rbac/permissions', { params });

      await apiIntegrationService.rbac.initializePermissions();
      expect(mockApi.post).toHaveBeenCalledWith('/api/v1/rbac/permissions/initialize');
    });

    it('should manage roles', async () => {
      const orgId = 123;
      const roleData = { name: 'Manager', description: 'Manager role' };
      
      await apiIntegrationService.rbac.getOrganizationRoles(orgId);
      expect(mockApi.get).toHaveBeenCalledWith(`/api/v1/rbac/organizations/${orgId}/roles`, { params: undefined });

      await apiIntegrationService.rbac.createRole(orgId, roleData);
      expect(mockApi.post).toHaveBeenCalledWith(`/api/v1/rbac/organizations/${orgId}/roles`, roleData);
    });

    it('should manage user role assignments', async () => {
      const userId = 456;
      const roleId = 789;
      const assignmentData = { role_ids: [roleId] };
      
      await apiIntegrationService.rbac.assignRoles(userId, assignmentData);
      expect(mockApi.post).toHaveBeenCalledWith(`/api/v1/rbac/users/${userId}/roles`, assignmentData);

      await apiIntegrationService.rbac.removeRole(userId, roleId);
      expect(mockApi.delete).toHaveBeenCalledWith(`/api/v1/rbac/users/${userId}/roles/${roleId}`);

      await apiIntegrationService.rbac.getUserRoles(userId);
      expect(mockApi.get).toHaveBeenCalledWith(`/api/v1/rbac/users/${userId}/roles`);
    });

    it('should handle permission checks', async () => {
      const permissionCheck = { user_id: 123, permission: 'crm_view' };
      
      await apiIntegrationService.rbac.checkPermission(permissionCheck);
      
      expect(mockApi.post).toHaveBeenCalledWith('/api/v1/rbac/permissions/check', permissionCheck);
    });
  });

  describe('CRM Module', () => {
    it('should manage customers', async () => {
      const customerData = { name: 'Test Customer', email: 'customer@test.com' };
      const customerId = 123;
      
      await apiIntegrationService.crm.getCustomers();
      expect(mockApi.get).toHaveBeenCalledWith('/api/v1/customers', { params: undefined });

      await apiIntegrationService.crm.createCustomer(customerData);
      expect(mockApi.post).toHaveBeenCalledWith('/api/v1/customers', customerData);

      await apiIntegrationService.crm.updateCustomer(customerId, customerData);
      expect(mockApi.put).toHaveBeenCalledWith(`/api/v1/customers/${customerId}`, customerData);

      await apiIntegrationService.crm.getCustomerDetails(customerId);
      expect(mockApi.get).toHaveBeenCalledWith(`/api/v1/customers/${customerId}`);
    });

    it('should manage CRM interactions', async () => {
      const interactionData = { type: 'call', subject: 'Follow-up call' };
      
      await apiIntegrationService.crm.getInteractions();
      expect(mockApi.get).toHaveBeenCalledWith('/api/v1/crm/interactions', { params: undefined });

      await apiIntegrationService.crm.createInteraction(interactionData);
      expect(mockApi.post).toHaveBeenCalledWith('/api/v1/crm/interactions', interactionData);
    });

    it('should manage CRM segments', async () => {
      const segmentData = { name: 'Premium Customers', criteria: {} };
      
      await apiIntegrationService.crm.getSegments();
      expect(mockApi.get).toHaveBeenCalledWith('/api/v1/crm/segments');

      await apiIntegrationService.crm.createSegment(segmentData);
      expect(mockApi.post).toHaveBeenCalledWith('/api/v1/crm/segments', segmentData);
    });
  });

  describe('Sales Module', () => {
    it('should manage sales orders', async () => {
      const orderData = { customer_id: 123, items: [] };
      const orderId = 456;
      
      await apiIntegrationService.sales.getSalesOrders();
      expect(mockApi.get).toHaveBeenCalledWith('/api/v1/vouchers/sales-orders', { params: undefined });

      await apiIntegrationService.sales.createSalesOrder(orderData);
      expect(mockApi.post).toHaveBeenCalledWith('/api/v1/vouchers/sales-orders', orderData);

      await apiIntegrationService.sales.updateSalesOrder(orderId, orderData);
      expect(mockApi.put).toHaveBeenCalledWith(`/api/v1/vouchers/sales-orders/${orderId}`, orderData);
    });

    it('should manage quotations', async () => {
      const quotationData = { customer_id: 123, items: [] };
      const quotationId = 789;
      
      await apiIntegrationService.sales.getQuotations();
      expect(mockApi.get).toHaveBeenCalledWith('/api/v1/vouchers/quotations', { params: undefined });

      await apiIntegrationService.sales.createQuotation(quotationData);
      expect(mockApi.post).toHaveBeenCalledWith('/api/v1/vouchers/quotations', quotationData);

      await apiIntegrationService.sales.convertQuotationToOrder(quotationId);
      expect(mockApi.post).toHaveBeenCalledWith(`/api/v1/vouchers/quotations/${quotationId}/convert-to-order`);
    });

    it('should get sales analytics', async () => {
      await apiIntegrationService.sales.getSalesAnalytics();
      expect(mockApi.get).toHaveBeenCalledWith('/api/v1/analytics/sales', { params: undefined });

      await apiIntegrationService.sales.getSalesReports();
      expect(mockApi.get).toHaveBeenCalledWith('/api/v1/reports/sales', { params: undefined });
    });
  });

  describe('Inventory Module', () => {
    it('should manage products', async () => {
      const productData = { name: 'Test Product', sku: 'TEST001' };
      const productId = 123;
      
      await apiIntegrationService.inventory.getProducts();
      expect(mockApi.get).toHaveBeenCalledWith('/api/v1/products', { params: undefined });

      await apiIntegrationService.inventory.createProduct(productData);
      expect(mockApi.post).toHaveBeenCalledWith('/api/v1/products', productData);

      await apiIntegrationService.inventory.updateProduct(productId, productData);
      expect(mockApi.put).toHaveBeenCalledWith(`/api/v1/products/${productId}`, productData);
    });

    it('should manage stock', async () => {
      const stockData = { quantity: 100 };
      const productId = 123;
      
      await apiIntegrationService.inventory.getStock();
      expect(mockApi.get).toHaveBeenCalledWith('/api/v1/stock', { params: undefined });

      await apiIntegrationService.inventory.updateStock(productId, stockData);
      expect(mockApi.put).toHaveBeenCalledWith(`/api/v1/stock/${productId}`, stockData);

      await apiIntegrationService.inventory.getStockMovements(productId);
      expect(mockApi.get).toHaveBeenCalledWith(`/api/v1/stock/${productId}/movements`);
    });

    it('should manage warehouses', async () => {
      const warehouseData = { name: 'Main Warehouse', location: 'New York' };
      const warehouseId = 456;
      
      await apiIntegrationService.inventory.getWarehouses();
      expect(mockApi.get).toHaveBeenCalledWith('/api/v1/warehouse');

      await apiIntegrationService.inventory.createWarehouse(warehouseData);
      expect(mockApi.post).toHaveBeenCalledWith('/api/v1/warehouse', warehouseData);

      await apiIntegrationService.inventory.getWarehouseStock(warehouseId);
      expect(mockApi.get).toHaveBeenCalledWith(`/api/v1/warehouse/${warehouseId}/stock`);
    });
  });

  describe('Service Desk Module', () => {
    it('should manage service tickets', async () => {
      const ticketData = { title: 'System Issue', priority: 'high' };
      const ticketId = 123;
      
      await apiIntegrationService.serviceDesk.getTickets();
      expect(mockApi.get).toHaveBeenCalledWith('/api/v1/service-desk/tickets', { params: undefined });

      await apiIntegrationService.serviceDesk.createTicket(ticketData);
      expect(mockApi.post).toHaveBeenCalledWith('/api/v1/service-desk/tickets', ticketData);

      await apiIntegrationService.serviceDesk.updateTicket(ticketId, ticketData);
      expect(mockApi.put).toHaveBeenCalledWith(`/api/v1/service-desk/tickets/${ticketId}`, ticketData);

      await apiIntegrationService.serviceDesk.closeTicket(ticketId);
      expect(mockApi.post).toHaveBeenCalledWith(`/api/v1/service-desk/tickets/${ticketId}/close`);
    });

    it('should manage SLA', async () => {
      const slaData = { name: 'Standard SLA', response_time: 4 };
      
      await apiIntegrationService.serviceDesk.getSLAs();
      expect(mockApi.get).toHaveBeenCalledWith('/api/v1/sla');

      await apiIntegrationService.serviceDesk.createSLA(slaData);
      expect(mockApi.post).toHaveBeenCalledWith('/api/v1/sla', slaData);

      await apiIntegrationService.serviceDesk.getSLACompliance();
      expect(mockApi.get).toHaveBeenCalledWith('/api/v1/sla/compliance');
    });

    it('should manage dispatch orders', async () => {
      const dispatchData = { ticket_id: 123, technician_id: 456 };
      const dispatchId = 789;
      
      await apiIntegrationService.serviceDesk.getDispatchOrders();
      expect(mockApi.get).toHaveBeenCalledWith('/api/v1/dispatch');

      await apiIntegrationService.serviceDesk.createDispatchOrder(dispatchData);
      expect(mockApi.post).toHaveBeenCalledWith('/api/v1/dispatch', dispatchData);

      await apiIntegrationService.serviceDesk.updateDispatchStatus(dispatchId, 'completed');
      expect(mockApi.put).toHaveBeenCalledWith(`/api/v1/dispatch/${dispatchId}/status`, { status: 'completed' });
    });
  });

  describe('Analytics Module', () => {
    it('should get customer analytics', async () => {
      const customerId = 123;
      
      await apiIntegrationService.analytics.getCustomerAnalytics();
      expect(mockApi.get).toHaveBeenCalledWith('/api/v1/analytics/customers');

      await apiIntegrationService.analytics.getCustomerAnalytics(customerId);
      expect(mockApi.get).toHaveBeenCalledWith(`/api/v1/analytics/customers/${customerId}/analytics`);
    });

    it('should get service analytics', async () => {
      await apiIntegrationService.analytics.getServiceAnalytics();
      expect(mockApi.get).toHaveBeenCalledWith('/api/v1/service-analytics');

      await apiIntegrationService.analytics.getTechnicianPerformance();
      expect(mockApi.get).toHaveBeenCalledWith('/api/v1/service-analytics/technician-performance');

      await apiIntegrationService.analytics.getJobCompletion();
      expect(mockApi.get).toHaveBeenCalledWith('/api/v1/service-analytics/job-completion');
    });

    it('should get AI analytics', async () => {
      await apiIntegrationService.analytics.getAIAnalytics();
      expect(mockApi.get).toHaveBeenCalledWith('/api/v1/ai-analytics');

      await apiIntegrationService.analytics.getAnomalyDetection();
      expect(mockApi.get).toHaveBeenCalledWith('/api/v1/ai-analytics/anomaly-detection');

      await apiIntegrationService.analytics.getPredictiveInsights();
      expect(mockApi.get).toHaveBeenCalledWith('/api/v1/ai-analytics/predictive-insights');
    });
  });

  describe('Admin Module', () => {
    it('should manage system settings', async () => {
      const settingsData = { theme: 'dark', notifications: true };
      
      await apiIntegrationService.admin.getSystemSettings();
      expect(mockApi.get).toHaveBeenCalledWith('/api/v1/settings');

      await apiIntegrationService.admin.updateSystemSettings(settingsData);
      expect(mockApi.put).toHaveBeenCalledWith('/api/v1/settings', settingsData);
    });

    it('should manage company branding', async () => {
      const brandingData = { primary_color: '#007acc', logo_url: 'https://example.com/logo.png' };
      
      await apiIntegrationService.admin.getCompanyBranding();
      expect(mockApi.get).toHaveBeenCalledWith('/api/v1/company/branding');

      await apiIntegrationService.admin.updateCompanyBranding(brandingData);
      expect(mockApi.put).toHaveBeenCalledWith('/api/v1/company/branding', brandingData);
    });

    it('should handle logo upload', async () => {
      const file = new File(['logo'], 'logo.png', { type: 'image/png' });
      
      await apiIntegrationService.admin.uploadCompanyLogo(file);
      
      expect(mockApi.post).toHaveBeenCalledWith('/api/v1/company/logo', expect.any(FormData));
    });

    it('should manage app users', async () => {
      const userData = { email: 'admin@app.com', role: 'app_admin' };
      const userId = 123;
      
      await apiIntegrationService.admin.getAppUsers();
      expect(mockApi.get).toHaveBeenCalledWith('/api/v1/app-users');

      await apiIntegrationService.admin.createAppUser(userData);
      expect(mockApi.post).toHaveBeenCalledWith('/api/v1/app-users', userData);

      await apiIntegrationService.admin.updateAppUser(userId, userData);
      expect(mockApi.put).toHaveBeenCalledWith(`/api/v1/app-users/${userId}`, userData);
    });
  });

  describe('Health Check and Quality Assurance', () => {
    it('should perform health check for all modules', async () => {
      // Mock successful API calls for health check
      mockApi.get.mockResolvedValue({ data: { status: 'ok' } });
      
      const healthStatus = await apiIntegrationService.healthCheck();
      
      expect(healthStatus).toBeInstanceOf(Object);
      expect(Object.keys(healthStatus)).toContain('auth');
      expect(Object.keys(healthStatus)).toContain('users');
      expect(Object.keys(healthStatus)).toContain('organizations');
      expect(Object.keys(healthStatus)).toContain('rbac');
    });

    it('should handle health check failures gracefully', async () => {
      // Mock API failures
      mockApi.get.mockRejectedValue(new Error('Service unavailable'));
      
      const healthStatus = await apiIntegrationService.healthCheck();
      
      expect(healthStatus).toBeInstanceOf(Object);
      // Should handle failures and return status for each module
    });

    it('should provide API module mapping', () => {
      const moduleMapping = apiIntegrationService.getAPIModuleMapping();
      
      expect(moduleMapping).toBeInstanceOf(Object);
      expect(moduleMapping).toHaveProperty('authentication');
      expect(moduleMapping).toHaveProperty('userManagement');
      expect(moduleMapping).toHaveProperty('organizations');
      expect(moduleMapping).toHaveProperty('rbac');
      expect(moduleMapping).toHaveProperty('crm');
      expect(moduleMapping).toHaveProperty('sales');
      expect(moduleMapping).toHaveProperty('inventory');
      expect(moduleMapping).toHaveProperty('analytics');
      
      // Check that authentication endpoints are properly mapped
      expect(moduleMapping.authentication).toContain('POST /api/v1/auth/login');
      expect(moduleMapping.authentication).toContain('POST /api/v1/otp/request');
      
      // Check RBAC endpoints
      expect(moduleMapping.rbac).toContain('GET /api/v1/rbac/permissions');
      expect(moduleMapping.rbac).toContain('POST /api/v1/rbac/users/{id}/roles');
    });
  });

  describe('Error Handling', () => {
    it('should handle API errors gracefully', async () => {
      const apiError = new Error('API Error');
      mockApi.get.mockRejectedValue(apiError);
      
      await expect(apiIntegrationService.users.getProfile()).rejects.toThrow('API Error');
    });

    it('should handle network errors', async () => {
      const networkError = new Error('Network Error');
      mockApi.post.mockRejectedValue(networkError);
      
      await expect(apiIntegrationService.auth.login({ email: 'test@test.com', password: 'test' }))
        .rejects.toThrow('Network Error');
    });

    it('should handle timeout errors', async () => {
      const timeoutError = new Error('Timeout');
      mockApi.get.mockRejectedValue(timeoutError);
      
      await expect(apiIntegrationService.analytics.getDashboardMetrics()).rejects.toThrow('Timeout');
    });
  });

  describe('Module Coverage Verification', () => {
    it('should cover all major backend modules', () => {
      const moduleMapping = apiIntegrationService.getAPIModuleMapping();
      const expectedModules = [
        'authentication',
        'userManagement', 
        'organizations',
        'rbac',
        'crm',
        'sales',
        'procurement',
        'inventory',
        'manufacturing',
        'serviceDesk',
        'finance',
        'hr',
        'projects',
        'analytics',
        'admin',
        'integrations',
        'notifications',
        'utilities'
      ];
      
      expectedModules.forEach(module => {
        expect(moduleMapping).toHaveProperty(module);
        expect(Array.isArray(moduleMapping[module])).toBe(true);
        expect(moduleMapping[module].length).toBeGreaterThan(0);
      });
    });

    it('should verify all service methods exist', () => {
      // Verify auth module methods
      expect(apiIntegrationService.auth.login).toBeDefined();
      expect(apiIntegrationService.auth.logout).toBeDefined();
      expect(apiIntegrationService.auth.requestOTP).toBeDefined();
      
      // Verify RBAC module methods
      expect(apiIntegrationService.rbac.getPermissions).toBeDefined();
      expect(apiIntegrationService.rbac.createRole).toBeDefined();
      expect(apiIntegrationService.rbac.assignRoles).toBeDefined();
      
      // Verify CRM module methods
      expect(apiIntegrationService.crm.getCustomers).toBeDefined();
      expect(apiIntegrationService.crm.createCustomer).toBeDefined();
      expect(apiIntegrationService.crm.getInteractions).toBeDefined();
      
      // Verify analytics module methods
      expect(apiIntegrationService.analytics.getCustomerAnalytics).toBeDefined();
      expect(apiIntegrationService.analytics.getServiceAnalytics).toBeDefined();
      expect(apiIntegrationService.analytics.getAIAnalytics).toBeDefined();
    });
  });
});