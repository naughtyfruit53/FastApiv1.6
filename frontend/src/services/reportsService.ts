// frontend/src/services/reportsService.ts
import api from "../lib/api";

export interface SalesReportFilters {
  start_date?: string;
  end_date?: string;
  customer_id?: string;
  search?: string;
}

export interface PurchaseReportFilters {
  start_date?: string;
  end_date?: string;
  vendor_id?: string;
  search?: string;
}

export interface LedgerFilters {
  start_date?: string;
  end_date?: string;
  account_type?: string;
  account_id?: string;
  voucher_type?: string;
}

export const reportsService = {
  getDashboardStats: async () => {
    try {
      const response = await api.get("/reports/dashboard-stats");
      return response.data;
    } catch (error: any) {
      throw new Error(error.message || "Failed to fetch dashboard stats");
    }
  },

  getSalesReport: async (filters: SalesReportFilters) => {
    try {
      const response = await api.get("/reports/sales-report", {
        params: filters,
      });
      return response.data;
    } catch (error: any) {
      throw new Error(error.message || "Failed to fetch sales report");
    }
  },

  getPurchaseReport: async (filters: PurchaseReportFilters) => {
    try {
      const response = api.get("/reports/purchase-report", {
        params: filters,
      });
      return response.data;
    } catch (error: any) {
      throw new Error(error.message || "Failed to fetch purchase report");
    }
  },

  getInventoryReport: async (lowStockOnly: boolean) => {
    try {
      const response = await api.get("/reports/inventory-report", {
        params: { low_stock_only: lowStockOnly },
      });
      return response.data;
    } catch (error: any) {
      throw new Error(error.message || "Failed to fetch inventory report");
    }
  },

  getPendingOrders: async (orderType: string) => {
    try {
      const response = await api.get("/reports/pending-orders", {
        params: { order_type: orderType },
      });
      return response.data;
    } catch (error: any) {
      throw new Error(error.message || "Failed to fetch pending orders");
    }
  },

  getCompleteLedger: async (filters: LedgerFilters) => {
    try {
      const response = await api.get("/reports/complete-ledger", {
        params: filters,
      });
      return response.data;
    } catch (error: any) {
      throw new Error(error.message || "Failed to fetch complete ledger");
    }
  },

  getOutstandingLedger: async (filters: LedgerFilters) => {
    try {
      const response = await api.get("/reports/outstanding-ledger", {
        params: filters,
      });
      return response.data;
    } catch (error: any) {
      throw new Error(error.message || "Failed to fetch outstanding ledger");
    }
  },

  exportSalesReportExcel: async (filters: SalesReportFilters) => {
    try {
      const response = await api.get("/reports/sales-report/export/excel", {
        params: filters,
        responseType: "blob",
      });
      return response.data;
    } catch (error: any) {
      throw new Error(error.message || "Failed to export sales report");
    }
  },

  exportPurchaseReportExcel: async (filters: PurchaseReportFilters) => {
    try {
      const response = await api.get("/reports/purchase-report/export/excel", {
        params: filters,
        responseType: "blob",
      });
      return response.data;
    } catch (error: any) {
      throw new Error(error.message || "Failed to export purchase report");
    }
  },

  exportInventoryReportExcel: async (includeZeroStock: boolean) => {
    try {
      const response = await api.get("/reports/inventory-report/export/excel", {
        params: { include_zero_stock: includeZeroStock },
        responseType: "blob",
      });
      return response.data;
    } catch (error: any) {
      throw new Error(error.message || "Failed to export inventory report");
    }
  },

  exportPendingOrdersExcel: async (orderType: string) => {
    try {
      const response = await api.get("/reports/pending-orders/export/excel", {
        params: { order_type: orderType },
        responseType: "blob",
      });
      return response.data;
    } catch (error: any) {
      throw new Error(error.message || "Failed to export pending orders report");
    }
  },

  exportCompleteLedgerExcel: async (filters: LedgerFilters) => {
    try {
      const response = await api.get("/reports/complete-ledger/export/excel", {
        params: filters,
        responseType: "blob",
      });
      return response.data;
    } catch (error: any) {
      throw new Error(error.message || "Failed to export complete ledger");
    }
  },

  exportOutstandingLedgerExcel: async (filters: LedgerFilters) => {
    try {
      const response = await api.get("/reports/outstanding-ledger/export/excel", {
        params: filters,
        responseType: "blob",
      });
      return response.data;
    } catch (error: any) {
      throw new Error(error.message || "Failed to export outstanding ledger");
    }
  },
};

export default reportsService;