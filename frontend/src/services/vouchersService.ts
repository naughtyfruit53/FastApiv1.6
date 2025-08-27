// src/services/vouchersService.ts
// frontend/src/services/vouchersService.ts

import api from '../lib/api';

export const voucherService = {
  // Generic Voucher Methods
  getVouchers: async (type: string, params?: any) => {
    const endpoint = `/${type}`;  // Remove extra 's' - use type as is (already plural)
    console.log(`[voucherService] Fetching vouchers from endpoint: ${endpoint}`);
    const response = await api.get(endpoint, { params });
    console.log(`[voucherService] Received data for ${type}:`, response.data);
    return response.data;
  },
  getVoucherById: async (type: string, id: number) => {
    const endpoint = `/${type}/${id}`;
    console.log(`[voucherService] Fetching voucher by ID from: ${endpoint}`);
    const response = await api.get(endpoint);
    return response.data;
  },
  createVoucher: async (type: string, data: any, sendEmail: boolean = false) => {
    const endpoint = `/${type}`;
    console.log(`[voucherService] Creating voucher at: ${endpoint}`);
    const response = await api.post(endpoint, data, { params: { send_email: sendEmail } });
    return response.data;
  },
  updateVoucher: async (type: string, id: number, data: any) => {
    const endpoint = `/${type}/${id}`;
    console.log(`[voucherService] Updating voucher at: ${endpoint}`);
    const response = await api.put(endpoint, data);
    return response.data;
  },
  getNextVoucherNumber: async (endpoint: string) => {
    console.log(`[voucherService] Fetching next number from: ${endpoint}`);
    const response = await api.get(endpoint);
    return response.data;
  },

  // Purchase Vouchers
  getPurchaseVoucherById: async (id: number) => {
    const response = await api.get(`/purchase-vouchers/${id}`);
    return response.data;
  },
  createPurchaseVoucher: async (data: any, sendEmail: boolean) => {
    const response = await api.post(`/purchase-vouchers`, data, { params: { send_email: sendEmail } });
    return response.data;
  },
  updatePurchaseVoucher: async (id: number, data: any) => {
    const response = await api.put(`/purchase-vouchers/${id}`, data);
    return response.data;
  },

  // Purchase Orders
  getPurchaseOrderById: async (id: number) => {
    const response = await api.get(`/purchase-orders/${id}`);
    return response.data;
  },
  createPurchaseOrder: async (data: any, sendEmail: boolean) => {
    const response = await api.post(`/purchase-orders`, data, { params: { send_email: sendEmail } });
    return response.data;
  },
  updatePurchaseOrder: async (id: number, data: any) => {
    const response = await api.put(`/purchase-orders/${id}`, data);
    return response.data;
  },

  // GRN
  getGrnById: async (id: number) => {
    const response = await api.get(`/goods-receipt-notes/${id}`);
    return response.data;
  },
  createGrn: async (data: any, sendEmail: boolean) => {
    const response = await api.post(`/goods-receipt-notes`, data, { params: { send_email: sendEmail } });
    return response.data;
  },
  updateGrn: async (id: number, data: any) => {
    const response = await api.put(`/goods-receipt-notes/${id}`, data);
    return response.data;
  },

  // Rejection In
  getRejectionInById: async (id: number) => {
    const response = await api.get(`/purchase-returns/${id}`);
    return response.data;
  },
  createRejectionIn: async (data: any, sendEmail: boolean) => {
    const response = await api.post(`/purchase-returns`, data, { params: { send_email: sendEmail } });
    return response.data;
  },
  updateRejectionIn: async (id: number, data: any) => {
    const response = await api.put(`/purchase-returns/${id}`, data);
    return response.data;
  },

  // Enhanced service methods for voucher actions
  getEmailRecipient: (voucher: any, voucherType: string) => {
    const type = voucherType.toLowerCase();
    if (type === 'purchase' && voucher.vendor) {
      return {
        name: voucher.vendor.name,
        email: voucher.vendor.email,
        type: 'vendor',
      };
    }
    if (type === 'sales' && voucher.customer) {
      return {
        name: voucher.customer.name,
        email: voucher.customer.email,
        type: 'customer',
      };
    }
    return null;
  },

  sendVoucherEmail: async (voucherType: string, id: number) => {
    try {
      const response = await api.post(`/${voucherType}s/${id}/send-email`);
      return response.data;
    } catch (error) {
      console.error('Error sending voucher email:', error);
      throw error;
    }
  },

  deleteVoucher: async (voucherType: string, id: number) => {
    try {
      const response = await api.delete(`/${voucherType}s/${id}`);
      return response.data;
    } catch (error) {
      console.error('Error deleting voucher:', error);
      throw error;
    }
  },

  getVoucherActions: (voucher: any, voucherType: string) => {
    const recipient = voucherService.getEmailRecipient(voucher, voucherType);
    
    return {
      canView: true,
      canEdit: true,
      canDelete: voucher.status !== 'approved' && voucher.status !== 'confirmed',
      canPrint: true,
      canEmail: Boolean(recipient?.email),
      emailRecipient: recipient,
    };
  },
};