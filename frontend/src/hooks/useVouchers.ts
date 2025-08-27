// frontend/src/hooks/useVouchers.ts

import { useQuery } from '@tanstack/react-query';
import { voucherService } from '../services/vouchersService';

export const usePurchaseVouchers = (id?: number) => {
  return useQuery({
    queryKey: ['purchaseVoucher', id],
    queryFn: () => voucherService.getPurchaseVoucherById(id!),
    enabled: !!id
  });
};

export const usePurchaseOrders = (id?: number) => {
  return useQuery({
    queryKey: ['purchaseOrder', id],
    queryFn: () => voucherService.getPurchaseOrderById(id!),
    enabled: !!id
  });
};

export const useGrns = (id?: number) => {
  return useQuery({
    queryKey: ['grn', id],
    queryFn: () => voucherService.getGrnById(id!),
    enabled: !!id
  });
};

export const useRejectionIns = (id?: number) => {
  return useQuery({
    queryKey: ['rejectionIn', id],
    queryFn: () => voucherService.getRejectionInById(id!),
    enabled: !!id
  });
};

// Mutations can be added similarly if needed