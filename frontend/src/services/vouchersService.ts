// frontend/src/services/vouchersService.ts
import api from "../lib/api";

export const voucherService = {
  // Generic Voucher Methods
  getVouchers: async (
    type: string,
    params?: Record<string, any>,
  ): Promise<any> => {
    const endpoint = `/${type}`;
    const response = await api.get(endpoint, { params });
    return response.data;
  },
  getVoucherById: async (type: string, id: number): Promise<any> => {
    const endpoint = `/${type}/${id}`;
    const response = await api.get(endpoint);
    return response.data;
  },
  createVoucher: async (
    type: string,
    data: Record<string, any>,
    sendEmail: boolean = false,
  ): Promise<any> => {
    const endpoint = `/${type}`;
    const response = await api.post(endpoint, data, {
      params: { send_email: sendEmail },
    });
    return response.data;
  },
  updateVoucher: async (
    type: string,
    id: number,
    data: Record<string, any>,
  ): Promise<any> => {
    const endpoint = `/${type}/${id}`;
    const response = await api.patch(endpoint, data);
    return response.data;
  },
  createRevision: async (
    type: string,
    id: number,
    data: Record<string, any>,
  ): Promise<any> => {
    const endpoint = `/${type}/${id}/revision`;
    const response = await api.post(endpoint, data);
    return response.data;
  },
  getNextVoucherNumber: async (endpoint: string): Promise<any> => {
    const response = await api.get(endpoint);
    return response.data;
  },
  // Purchase Vouchers
  getPurchaseVoucherById: async (id: number): Promise<any> => {
    const response = await api.get(`/purchase-vouchers/${id}`);
    return response.data;
  },
  createPurchaseVoucher: async (
    data: Record<string, any>,
    sendEmail: boolean,
  ): Promise<any> => {
    const response = await api.post(`/purchase-vouchers`, data, {
      params: { send_email: sendEmail },
    });
    return response.data;
  },
  updatePurchaseVoucher: async (
    id: number,
    data: Record<string, any>,
  ): Promise<any> => {
    const response = await api.put(`/purchase-vouchers/${id}`, data);
    return response.data;
  },
  // Purchase Orders
  getPurchaseOrderById: async (id: number): Promise<any> => {
    const response = await api.get(`/purchase-orders/${id}`);
    return response.data;
  },
  createPurchaseOrder: async (
    data: Record<string, any>,
    sendEmail: boolean,
  ): Promise<any> => {
    const response = await api.post(`/purchase-orders`, data, {
      params: { send_email: sendEmail },
    });
    return response.data;
  },
  updatePurchaseOrder: async (
    id: number,
    data: Record<string, any>,
  ): Promise<any> => {
    const response = await api.put(`/purchase-orders/${id}`, data);
    return response.data;
  },
  // GRN
  getGrnById: async (id: number): Promise<any> => {
    const response = await api.get(`/goods-receipt-notes/${id}`);
    return response.data;
  },
  createGrn: async (
    data: Record<string, any>,
    sendEmail: boolean,
  ): Promise<any> => {
    const response = await api.post(`/goods-receipt-notes`, data, {
      params: { send_email: sendEmail },
    });
    return response.data;
  },
  updateGrn: async (id: number, data: Record<string, any>): Promise<any> => {
    const response = await api.put(`/goods-receipt-notes/${id}`, data);
    return response.data;
  },
  // Rejection In
  getRejectionInById: async (id: number): Promise<any> => {
    const response = await api.get(`/purchase-returns/${id}`);
    return response.data;
  },
  createRejectionIn: async (
    data: Record<string, any>,
    sendEmail: boolean,
  ): Promise<any> => {
    const response = await api.post(`/purchase-returns`, data, {
      params: { send_email: sendEmail },
    });
    return response.data;
  },
  updateRejectionIn: async (
    id: number,
    data: Record<string, any>,
  ): Promise<any> => {
    const response = await api.put(`/purchase-returns/${id}`, data);
    return response.data;
  },
  // Receipt Voucher
  getReceiptVoucherById: async (id: number): Promise<any> => {
    const response = await api.get(`/receipt-vouchers/${id}`);
    return response.data;
  },
  // Enhanced service methods for voucher actions
  getEmailRecipient: (
    voucher: Record<string, any>,
    voucherType: string,
  ): any => {
    const type = voucherType.toLowerCase();
    if (type === "purchase" && voucher.vendor) {
      return {
        name: voucher.vendor.name,
        email: voucher.vendor.email,
        type: "vendor",
      };
    }
    if (type === "sales" && voucher.customer) {
      return {
        name: voucher.customer.name,
        email: voucher.customer.email,
        type: "customer",
      };
    }
    return null;
  },
  sendVoucherEmail: async (voucherType: string, id: number): Promise<any> => {
    try {
      const response = await api.post(`/${voucherType}/${id}/send-email`);
      return response.data;
    } catch (error: any) {
      console.error("Error sending voucher email:", error);
      throw error;
    }
  },
  deleteVoucher: async (voucherType: string, id: number): Promise<any> => {
    try {
      const response = await api.delete(`/${voucherType}/${id}`);
      return response.data;
    } catch (error: any) {
      console.error("Error deleting voucher:", error);
      throw error;
    }
  },
  getVoucherActions: (
    voucher: Record<string, any>,
    voucherType: string,
  ): any => {
    const recipient = voucherService.getEmailRecipient(voucher, voucherType);
    return {
      canView: true,
      canEdit: true,
      canDelete:
        voucher.status !== "approved" && voucher.status !== "confirmed",
      canPrint: true,
      canEmail: Boolean(recipient?.email),
      emailRecipient: recipient,
      canRevise: true,
    };
  },
  // New method to check if tracking details exist for a voucher
  getHasTracking: async (type: string, id: number): Promise<boolean> => {
    try {
      const response = await api.get(`/${type}/${id}/tracking`);
      // Check if tracking details are present and non-empty
      return !!response.data && !!response.data.tracking_number && response.data.tracking_number.trim() !== '';
    } catch (error) {
      return false;
    }
  },
};
