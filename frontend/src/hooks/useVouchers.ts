// frontend/src/hooks/useVouchers.ts
import { useQuery } from "@tanstack/react-query";
import { voucherService } from "../services/vouchersService";

export const usePurchaseVouchers = (id?: number): any => {
  return useQuery({
    queryKey: ["purchaseVoucher", id],
    queryFn: () => voucherService.getPurchaseVoucherById(id!),
    enabled: !!id,
  });
};

export const usePurchaseOrders = (id?: number): any => {
  return useQuery({
    queryKey: ["purchaseOrder", id],
    queryFn: async () => {
      const data = await voucherService.getPurchaseOrderById(id!);
      console.log('[usePurchaseOrders] Fetched purchase order:', data);
      if (data.items && Array.isArray(data.items)) {
        data.items.forEach((item: any, index: number) => {
          if (!item.product_id || !item.quantity || !item.unit) {
            console.warn(`[usePurchaseOrders] Item ${index} is missing required fields:`, item);
          }
        });
      } else {
        console.warn('[usePurchaseOrders] No valid items in purchase order:', data);
      }
      return data;
    },
    enabled: !!id,
  });
};

export const useGrns = (id?: number): any => {
  return useQuery({
    queryKey: ["grn", id],
    queryFn: () => voucherService.getGrnById(id!),
    enabled: !!id,
  });
};

export const useRejectionIns = (id?: number): any => {
  return useQuery({
    queryKey: ["rejectionIn", id],
    queryFn: () => voucherService.getRejectionInById(id!),
    enabled: !!id,
  });
};

export const useReceiptVouchers = (id?: number): any => {
  return useQuery({
    queryKey: ["receiptVoucher", id],
    queryFn: () => voucherService.getReceiptVoucherById(id!),
    enabled: !!id,
  });
};