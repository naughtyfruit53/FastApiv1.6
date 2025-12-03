// frontend/src/services/authService.ts
import api from "../lib/api"; // Use the api client
import { ACCESS_TOKEN_KEY, REFRESH_TOKEN_KEY, USER_ROLE_KEY, IS_SUPER_ADMIN_KEY } from "../constants/auth";

// Simple in-memory cache for current user (TTL 1 minute)
let currentUserCache: { data: any; timestamp: number } | null = null;
const USER_CACHE_TTL = 60 * 1000; // 1 minute

export const authService = {
  login: async (username: string, password: string): Promise<any> => {
    try {
      console.log("[AuthService] Starting login process for:", username);
      const formData = new FormData();
      formData.append("username", username);
      formData.append("password", password);
      const response = await api.post("/auth/login", formData, {
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
      });
      console.log("[AuthService] Login API response received:", {
        hasToken: !!response.data.access_token,
        hasRefresh: !!response.data.refresh_token,
        organizationId: response.data.organization_id,
        userRole: response.data.user_role,
        mustChangePassword: response.data.must_change_password,
      });
      // Store token FIRST
      localStorage.setItem(ACCESS_TOKEN_KEY, response.data.access_token);
      // Store refresh token if provided
      if (response.data.refresh_token) {
        localStorage.setItem(REFRESH_TOKEN_KEY, response.data.refresh_token);
        console.log("[AuthService] Stored refresh token");
      }
      // Store authentication context data (NOT organization_id - that stays in memory)
      if (response.data.user_role) {
        localStorage.setItem(USER_ROLE_KEY, response.data.user_role);
        console.log("[AuthService] Stored user_role:", response.data.user_role);
      }
      localStorage.setItem(
        IS_SUPER_ADMIN_KEY,
        response.data.user?.is_super_admin ? "true" : "false",
      );
      console.log(
        "[AuthService] Stored is_super_admin:",
        response.data.user?.is_super_admin,
      );
      console.log(
        "[AuthService] Organization context managed by backend session only",
      );
      console.log("[AuthService] Login complete - auth context established");
      return response.data;
    } catch (error: any) {
      console.error("[AuthService] Login failed:", error);
      throw new Error(error.userMessage || "Login failed");
    }
  },
  loginWithEmail: async (email: string, password: string): Promise<any> => {
    try {
      console.log("[AuthService] Starting email login process for:", email);
      const formData = new FormData();
      formData.append("username", email);
      formData.append("password", password);
      const response = await api.post("/auth/login", formData, {
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
      });
      console.log("[AuthService] Email login API response received:", {
        hasToken: !!response.data.access_token,
        hasRefresh: !!response.data.refresh_token,
        organizationId: response.data.organization_id,
        userRole: response.data.user_role,
        mustChangePassword: response.data.must_change_password,
      });
      // Store token FIRST
      localStorage.setItem(ACCESS_TOKEN_KEY, response.data.access_token);
      // Store ALL authentication context data immediately after token
      // Store refresh token if provided
      if (response.data.refresh_token) {
        localStorage.setItem(REFRESH_TOKEN_KEY, response.data.refresh_token);
        console.log("[AuthService] Stored refresh token");
      }
      if (response.data.user_role) {
        localStorage.setItem(USER_ROLE_KEY, response.data.user_role);
        console.log("[AuthService] Stored user_role:", response.data.user_role);
      }
      localStorage.setItem(
        IS_SUPER_ADMIN_KEY,
        response.data.user?.is_super_admin ? "true" : "false",
      );
      console.log(
        "[AuthService] Stored is_super_admin:",
        response.data.user?.is_super_admin,
      );
      console.log(
        "[AuthService] Organization context managed by backend session only",
      );
      console.log(
        "[AuthService] Email login complete - all context established",
      );
      return response.data;
    } catch (error: any) {
      console.error("[AuthService] Email login failed:", error);
      throw new Error(error.userMessage || "Email login failed");
    }
  },
  // NOTE: This method should only be called by AuthProvider for:
  // 1. Initial user fetch on app mount
  // 2. Manual user refresh operations
  // DO NOT call this directly from components - use useAuth() hook instead
  getCurrentUser: async (): Promise<any> => {
    try {
      console.log("[AuthService] Fetching current user data");
      // Check cache
      if (currentUserCache && Date.now() - currentUserCache.timestamp < USER_CACHE_TTL) {
        console.log("[AuthService] Returning cached user data");
        return currentUserCache.data;
      }
      const response = await api.get("/users/me");
      console.log("[AuthService] User data received from /users/me:", {
        id: response.data.id,
        email: response.data.email,
        role: response.data.role,
        is_super_admin: response.data.is_super_admin,
        organization_id: response.data.organization_id,
        must_change_password: response.data.must_change_password,
      });
      // Organization context is managed by backend session only
      console.log(
        "[AuthService] Organization context from backend session:",
        response.data.organization_id,
      );
      // Store role information
      if (response.data.role) {
        localStorage.setItem(USER_ROLE_KEY, response.data.role);
        console.log(
          "[AuthService] Updated user_role in localStorage:",
          response.data.role,
        );
      }
      localStorage.setItem(
        IS_SUPER_ADMIN_KEY,
        response.data.is_super_admin ? "true" : "false",
      );
      console.log(
        "[AuthService] Updated is_super_admin in localStorage:",
        response.data.is_super_admin,
      );
      console.log(
        "[AuthService] getCurrentUser complete - all localStorage updated",
      );
      // Cache the result
      currentUserCache = {
        data: response.data,
        timestamp: Date.now(),
      };
      return response.data;
    } catch (error: any) {
      console.error("[AuthService] Failed to fetch current user:", error);
      throw new Error(error.userMessage || "Failed to fetch user information");
    }
  },
  logout: () => {
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
    localStorage.removeItem(USER_ROLE_KEY);
    localStorage.removeItem(IS_SUPER_ADMIN_KEY);
    window.location.href = "/";
  },
  requestOTP: async (
    email: string,
    phone: string,
    deliveryMethod: string = "auto",
    purpose: string = "login",
  ): Promise<any> => {
    try {
      const requestData: any = { email, purpose };
      if (phone) {
        requestData.phone_number = phone;
      }
      if (deliveryMethod) {
        requestData.delivery_method = deliveryMethod;
      }
      const response = await api.post("/auth/otp/request", requestData);
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to send OTP");
    }
  },
  verifyOTP: async (
    email: string,
    otp: string,
    purpose: string = "login",
  ): Promise<any> => {
    try {
      const response = await api.post("/auth/otp/verify", {
        email,
        otp,
        purpose,
      });
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "OTP verification failed");
    }
  },
  refreshToken: async (): Promise<any> => {
    try {
      console.log("[AuthService] Attempting to refresh token");
      const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY);
      if (!refreshToken) {
        console.error("[AuthService] No refresh token available");
        // Instead of throw, return null and let caller handle
        return null;
      }
      const response = await api.post("/auth/refresh-token", {
        refresh_token: refreshToken,
      });
      console.log("[AuthService] Token refresh successful");
      // Update stored tokens
      if (response.data.access_token) {
        localStorage.setItem(ACCESS_TOKEN_KEY, response.data.access_token);
      }
      if (response.data.refresh_token) {
        localStorage.setItem(REFRESH_TOKEN_KEY, response.data.refresh_token);
      }
      return response.data;
    } catch (error: any) {
      console.error("[AuthService] Token refresh failed:", error);
      // Instead of clear, return null
      return null;
    }
  },
  isTokenValid: () => {
    const token = localStorage.getItem(ACCESS_TOKEN_KEY);
    if (!token) {
      return false;
    }
    try {
      const payload = JSON.parse(atob(token.split(".")[1]));
      const expiry = payload.exp * 1000; // Convert to milliseconds
      const now = Date.now();
      // Check if token expires in next 5 minutes
      return expiry > now + 5 * 60 * 1000;
    } catch (error) {
      console.error("[AuthService] Failed to parse token:", error);
      return false;
    }
  },
  setupAdminAccount: async (): Promise<any> => {
    try {
      const response = await api.post("/auth/admin/setup");
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Admin setup failed");
    }
  },
};
export const voucherService = {
  // Generic function for CRUD
  getVouchers: async (type: string, params?: any) => {
    try {
      const response = await api.get(`/${type}/`, { params });
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || `Failed to fetch ${type}`);
    }
  },
  createVoucher: async (type: string, data: any, sendEmail = false) => {
    try {
      const response = await api.post(`/${type}/`, data, {
        params: { send_email: sendEmail },
      });
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || `Failed to create ${type}`);
    }
  },
  getVoucherById: async (type: string, voucherId: number) => {
    try {
      const response = await api.get(`/${type}/${voucherId}`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || `Failed to fetch ${type}`);
    }
  },
  updateVoucher: async (type: string, voucherId: number, data: any) => {
    try {
      const response = await api.put(`/${type}/${voucherId}`, data);
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || `Failed to update ${type}`);
    }
  },
  deleteVoucher: async (type: string, voucherId: number) => {
    try {
      const response = await api.delete(`/${type}/${voucherId}`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || `Failed to delete ${type}`);
    }
  },
  sendVoucherEmail: async (
    voucherType: string,
    voucherId: number,
    customEmail?: string,
  ) => {
    let params = "";
    if (customEmail) {
      params = `?custom_email=${customEmail}`;
    }
    try {
      const response = await api.post(
        `/${voucherType}/${voucherId}/send-email${params}`,
      );
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to send email");
    }
  },
  getSalesVouchers: async (params?: any) => {
    return voucherService.getVouchers("sales-vouchers", params);
  },
  // Purchase Order specific methods
  getPurchaseOrders: async (params?: any) => {
    return voucherService.getVouchers("purchase-orders", params);
  },
  getPurchaseOrderById: async (id: number) => {
    return voucherService.getVoucherById("purchase-orders", id);
  },
  createPurchaseOrder: async (data: any, sendEmail = false) => {
    return voucherService.createVoucher("purchase-orders", data, sendEmail);
  },
  updatePurchaseOrder: async (id: number, data: any) => {
    return voucherService.updateVoucher("purchase-orders", id, data);
  },
  // GRN specific methods
  getGrns: async (params?: any) => {
    return voucherService.getVouchers("goods-receipt-notes", params);
  },
  getGrnById: async (id: number) => {
    return voucherService.getVoucherById("goods-receipt-notes", id);
  },
  createGrn: async (data: any, sendEmail = false) => {
    return voucherService.createVoucher("goods-receipt-notes", data, sendEmail);
  },
  updateGrn: async (id: number, data: any) => {
    return voucherService.updateVoucher("goods-receipt-notes", id, data);
  },
  // Access to master data for vouchers
  getVendors: async (params?: any) => {
    return masterDataService.getVendors(params);
  },
  getProducts: async (params?: any) => {
    return masterDataService.getProducts(params);
  },
  getCustomers: async (params?: any) => {
    return masterDataService.getCustomers(params);
  },
};
export const masterDataService = {
  getVendors: async ({ signal, params = {} } = {}) => {
    try {
      const response = await api.get("/vendors", { params, signal });
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to fetch vendors");
    }
  },
  createVendor: async (data: any) => {
    try {
      const response = await api.post("/vendors", data); // No trailing /
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to create vendor");
    }
  },
  updateVendor: async (id: number, data: any) => {
    try {
      const response = await api.put(`/vendors/${id}`, data);
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to update vendor");
    }
  },
  deleteVendor: async (id: number) => {
    try {
      const response = await api.delete(`/vendors/${id}`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to delete vendor");
    }
  },
  getCustomers: async ({ signal, params = {} } = {}) => {
    try {
      // Organization context is derived from backend session, no need to add manually
      const response = await api.get("/customers", { params, signal });
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to fetch customers");
    }
  },
  createCustomer: async (data: any) => {
    try {
      const response = await api.post("/customers", data); // No trailing /
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to create customer");
    }
  },
  updateCustomer: async (id: number, data: any) => {
    try {
      const response = await api.put(`/customers/${id}`, data);
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to update customer");
    }
  },
  deleteCustomer: async (id: number) => {
    try {
      const response = await api.delete(`/customers/${id}`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to delete customer");
    }
  },
  getProducts: async ({ signal } = {}) => {
    try {
      // Organization context is derived from backend session, no need to add manually
      const response = await api.get("/products", { signal });
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to fetch products");
    }
  },
  createProduct: async (data: any) => {
    try {
      const response = await api.post("/products", data); // No trailing /
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to create product");
    }
  },
  updateProduct: async (id: number, data: any) => {
    try {
      const response = await api.put(`/products/${id}`, data);
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to update product");
    }
  },
  deleteProduct: async (id: number) => {
    try {
      const response = await api.delete(`/products/${id}`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to delete product");
    }
  },
  getStock: async ({ signal, params = {} } = {}) => {
    try {
      // Organization context is derived from backend session, no need to add manually
      const response = await api.get("/stock", { params, signal });
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to fetch stock data");
    }
  },
  getLowStock: async ({ signal } = {}) => {
    try {
      // Organization context is derived from backend session, no need to add manually
      const response = await api.get("/stock/low-stock", { signal });
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to fetch low stock data");
    }
  },
  updateStock: async (productId: number, data: any) => {
    try {
      const response = await api.put(`/stock/product/product/${productId}`, data);
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to update stock");
    }
  },
  adjustStock: async (
    productId: number,
    quantityChange: number,
    reason: string,
  ) => {
    try {
      const response = await api.post(`/stock/adjust/${productId}`, null, {
        params: { quantity_change: quantityChange, reason },
      });
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to adjust stock");
    }
  },
  bulkImportStock: async (file: File, mode: string = "replace") => {
    try {
      // Ensure user is authenticated before attempting import
      const token = localStorage.getItem(ACCESS_TOKEN_KEY);
      if (!token) {
        throw new Error(
          "Authentication required. Please log in before importing inventory.",
        );
      }
      const formData = new FormData();
      formData.append("file", file);
      /**
       * @deprecated Use React user context instead - organization context is derived from backend session
       * Organization context is automatically managed by the backend via JWT token
       */
      const params = { mode };
      console.log("Bulk import params:", params);
      const response = await api.post("/stock/bulk", formData, {
        params,
        headers: {
          "Content-Type": undefined,
        },
        transformRequest: (data) => data,
      });
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to bulk import stock");
    }
  },
  downloadStockTemplate: async () => {
    try {
      const response = await api.get("/stock/template/excel", {
        responseType: "blob",
      });
      const blob = new Blob([response.data], {
        type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
      });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = "stock_template.xlsx";
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to download stock template");
    }
  },
  exportStock: async (params?: any) => {
    try {
      /**
       * @deprecated Use React user context instead - organization context is derived from backend session
       * Organization context is automatically managed by the backend via JWT token
       */
      const response = await api.get("/stock/export/excel", {
        params,
        responseType: "blob",
      });
      const blob = new Blob([response.data], {
        type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
      });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = "stock_export.xlsx";
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to export stock");
    }
  },
};
export const companyService = {
  getCurrentCompany: async () => {
    const token = localStorage.getItem(ACCESS_TOKEN_KEY);
    if (!token) {
      console.log(
        "[CompanyService] Skipping company fetch - no token available",
      );
      return null;
    }
    try {
      /**
       * @deprecated Use React user context instead - organization context is derived from backend session
       * Organization context is automatically managed by the backend via JWT token
       */
      const response = await api.get("/companies/current");
      console.log("[CompanyService] Company data received:", response.data);
      return response.data;
    } catch (error: any) {
      if (error.status === 404 || error.isCompanySetupRequired) {
        console.log(
          "[CompanyService] Company setup required (404 or company missing)",
        );
        return null;
      }
      console.error("[CompanyService] Error fetching company:", error);
      return null; // Instead of throw, return null on error to avoid throwing
    }
  },
  isCompanySetupRequired: async () => {
    try {
      const company = await companyService.getCurrentCompany();
      return company === null;
    } catch (error: any) {
      // If we get an error other than 404, assume company setup is required
      return true;
    }
  },
  createCompany: async (data: any) => {
    try {
      const response = await api.post("/companies/", data);
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to create company");
    }
  },
  updateCompany: async (id: number, data: any) => {
    try {
      const response = await api.put(`/companies/${id}`, data);
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to update company");
    }
  },
  uploadLogo: async (companyId: number, file: File) => {
    try {
      const formData = new FormData();
      formData.append("file", file);
      const response = await api.post(
        `/companies/${companyId}/logo`,
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        },
      );
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to upload logo");
    }
  },
  deleteLogo: async (companyId: number) => {
    try {
      const response = await api.delete(`/companies/${companyId}/logo`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to delete logo");
    }
  },
  getLogoUrl: (companyId: number) => {
    return `/api/v1/companies/${companyId}/logo`;
  },
  // Multi-company management methods
  getCompanies: async () => {
    try {
      const response = await api.get("/companies/");
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to fetch companies");
    }
  },
  getOrganizationInfo: async () => {
    try {
      const response = await api.get("/organizations/current");
      return response.data;
    } catch (error: any) {
      throw new Error(
        error.userMessage || "Failed to fetch organization info",
      );
    }
  },
  getCompanyUsers: async (companyId: number) => {
    try {
      const response = await api.get(`/companies/${companyId}/users`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to fetch company users");
    }
  },
  assignUserToCompany: async (
    companyId: number,
    data: { user_id: number; company_id: number; is_company_admin: boolean },
  ) => {
    try {
      const response = await api.post(`/companies/${companyId}/users`, data);
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to assign user to company");
    }
  },
  updateUserCompanyAssignment: async (
    companyId: number,
    userId: number,
    updates: any,
  ) => {
    try {
      const response = await api.put(
        `/companies/${companyId}/users/${userId}`,
        updates,
      );
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to update user assignment");
    }
  },
  removeUserFromCompany: async (companyId: number, userId: number) => {
    try {
      const response = await api.delete(
        `/companies/${companyId}/users/${userId}`,
      );
      return response.data;
    } catch (error: any) {
      throw new Error(
        error.userMessage || "Failed to remove user from company",
      );
    }
  },
};
export const reportsService = {
  getDashboardStats: async () => {
    try {
      const response = await api.get("/reports/dashboard-stats");
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to get dashboard stats");
    }
  },
  getSalesReport: async (params?: any) => {
    try {
      const response = await api.get("/reports/sales-report", { params });
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to get sales report");
    }
  },
  getPurchaseReport: async (params?: any) => {
    try {
      const response = await api.get("/reports/purchase-report", { params });
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to get purchase report");
    }
  },
  getInventoryReport: async (lowStockOnly = false) => {
    try {
      const response = await api.get("/reports/inventory-report", {
        params: { low_stock_only: lowStockOnly },
      });
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to get inventory report");
    }
  },
  getPendingOrders: async (orderType = "all") => {
    try {
      const response = await api.get("/reports/pending-orders", {
        params: { order_type: orderType },
      });
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to get pending orders");
    }
  },
  getCompleteLedger: async (params?: any) => {
    try {
      const response = await api.get("/reports/complete-ledger", { params });
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to get complete ledger");
    }
  },
  getOutstandingLedger: async (params?: any) => {
    try {
      const response = await api.get("/reports/outstanding-ledger", { params });
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to get outstanding ledger");
    }
  },
  // Export functions
  exportSalesReportExcel: async (params?: any) => {
    try {
      const response = await api.get("/reports/sales-report/export/excel", {
        params,
        responseType: "blob",
      });
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to export sales report");
    }
  },
  exportPurchaseReportExcel: async (params?: any) => {
    try {
      const response = await api.get("/reports/purchase-report/export/excel", {
        params,
        responseType: "blob",
      });
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to export purchase report");
    }
  },
  exportInventoryReportExcel: async (params?: any) => {
    try {
      const response = await api.get("/reports/inventory-report/export/excel", {
        params,
        responseType: "blob",
      });
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to export inventory report");
    }
  },
  exportPendingOrdersExcel: async (params?: any) => {
    try {
      const response = await api.get("/reports/pending-orders/export/excel", {
        params,
        responseType: "blob",
      });
      return response.data;
    } catch (error: any) {
      throw new Error(
        error.userMessage || "Failed to export pending orders report",
      );
    }
  },
  exportCompleteLedgerExcel: async (params?: any) => {
    try {
      const response = await api.get("/reports/complete-ledger/export/excel", {
        params,
        responseType: "blob",
      });
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to export complete ledger");
    }
  },
  exportOutstandingLedgerExcel: async (params?: any) => {
    try {
      const response = await api.get(
        "/reports/outstanding-ledger/export/excel",
        {
          params,
          responseType: "blob",
        },
      );
      return response.data;
    } catch (error: any) {
      throw new Error(
        error.userMessage || "Failed to export outstanding ledger",
      );
    }
  },
};
export const organizationService = {
  createLicense: async (data: any) => {
    try {
      const response = await api.post("/organizations/license/create", data);
      return response.data;
    } catch (error: any) {
      throw new Error(
        error.userMessage || "Failed to create organization license",
      );
    }
  },
  getCurrentOrganization: async () => {
    try {
      const response = await api.get("/organizations/current");
      return response.data;
    } catch (error: any) {
      throw new Error(
        error.userMessage || "Failed to get current organization",
      );
    }
  },
  updateOrganization: async (data: any) => {
    try {
      const response = await api.put("/organizations/current", data);
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to update organization");
    }
  },
  // Admin-only endpoints
  getAllOrganizations: async () => {
    try {
      const response = await api.get("/organizations/");
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to get organizations");
    }
  },
  getOrganization: async (id: number) => {
    try {
      const response = await api.get(`/organizations/${id}`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to get organization");
    }
  },
  updateOrganizationById: async (id: number, data: any) => {
    try {
      const response = await api.put(`/organizations/${id}`, data);
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to update organization");
    }
  },
};
export const passwordService = {
  changePassword: async (
    currentPassword: string | null,
    newPassword: string,
    confirmPassword?: string,
  ) => {
    try {
      const payload: {
        new_password: string;
        current_password?: string;
        confirm_password?: string;
      } = {
        new_password: newPassword,
      };
      if (currentPassword) {
        payload.current_password = currentPassword;
      }
      if (confirmPassword) {
        payload.confirm_password = confirmPassword;
      }
      const response = await api.post("/password/change", payload);
      // Handle new token if provided in response (password change returns new JWT)
      if (response.data.access_token) {
        console.log(
          "[PasswordService] New token received after password change, updating storage",
        );
        localStorage.setItem(ACCESS_TOKEN_KEY, response.data.access_token);
      }
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to change password");
    }
  },
  forgotPassword: async (email: string) => {
    try {
      const response = await api.post("/password/forgot", { email });
      return response.data;
    } catch (error: any) {
      throw new Error(
        error.userMessage || "Failed to send password reset email",
      );
    }
  },
  resetPassword: async (email: string, otp: string, newPassword: string) => {
    try {
      const response = await api.post("/password/reset", {
        email,
        otp,
        new_password: newPassword,
      });
      // Handle new token if provided in response (password reset returns new JWT)
      if (response.data.access_token) {
        console.log(
          "[PasswordService] New token received after password reset, updating storage",
        );
        localStorage.setItem(ACCESS_TOKEN_KEY, response.data.access_token);
      }
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to reset password");
    }
  },
  adminResetPassword: async (userEmail: string) => {
    try {
      const response = await api.post("/password/admin-reset", { user_email: userEmail });
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to initiate admin password reset");
    }
  }
};
export const userService = {
  // Organization user management (for org admins)
  getOrganizationUsers: async (params?: any) => {
    try {
      const response = await api.get("/users/", { params });
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to get organization users");
    }
  },
  createUser: async (data: any) => {
    try {
      const response = await api.post("/users/", data);
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to create user");
    }
  },
  updateUser: async (id: number, data: any) => {
    try {
      const response = await api.put(`/users/${id}`, data);
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to update user");
    }
  },
  deleteUser: async (id: number) => {
    try {
      const response = await api.delete(`/users/${id}`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to delete user");
    }
  },
  resetUserPassword: async (userId: number) => {
    try {
      const response = await api.post(`/auth/reset/${userId}/password`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to reset user password");
    }
  },
  toggleUserStatus: async (userId: number, isActive: boolean) => {
    try {
      const response = await api.put(`/users/${userId}`, {
        is_active: isActive,
      });
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to update user status");
    }
  },
};
