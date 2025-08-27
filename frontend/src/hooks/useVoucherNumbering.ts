// Voucher numbering utilities and hooks
import { useQuery } from '@tanstack/react-query';
import { useEffect } from 'react';
import api from '../lib/api';

interface UseVoucherNumberingProps {
  apiEndpoint: string;
  mode: 'create' | 'edit' | 'view';
  setValue: (name: string, value: any) => void;
  voucherData?: any;
}

export const useVoucherNumbering = ({ 
  apiEndpoint, 
  mode, 
  setValue, 
  voucherData 
}: UseVoucherNumberingProps) => {
  // Fetch next voucher number for create mode
  const { data: nextVoucherNumber, refetch: refetchNextNumber } = useQuery({
    queryKey: [`next${apiEndpoint}Number`],
    queryFn: () => api.get(`/${apiEndpoint}/next-number`).then(res => res.data),
    enabled: mode === 'create',
  });

  // Auto-set voucher number based on mode
  useEffect(() => {
    if (mode === 'create' && nextVoucherNumber) {
      setValue('voucher_number', nextVoucherNumber);
    } else if (voucherData && voucherData.voucher_number) {
      setValue('voucher_number', voucherData.voucher_number);
    }
  }, [mode, nextVoucherNumber, voucherData, setValue]);

  // Return refetch function for post-save increment
  const refreshVoucherNumber = async () => {
    if (mode === 'create') {
      const { data: newNextNumber } = await refetchNextNumber();
      setValue('voucher_number', newNextNumber);
      return newNextNumber;
    }
  };

  return {
    nextVoucherNumber,
    refreshVoucherNumber
  };
};

// Get API endpoint from voucher config
export const getVoucherApiEndpoint = (voucherType: string): string => {
  const endpointMap: Record<string, string> = {
    'quotation': 'quotations',
    'proforma-invoice': 'proforma-invoices',
    'sales-order': 'sales-orders',
    'sales-voucher': 'sales-vouchers',
    'delivery-challan': 'delivery-challans',
    'sales-return': 'sales-returns',
    'purchase-order': 'purchase-orders',
    'grn': 'goods-receipt-notes',
    'purchase-voucher': 'purchase-vouchers',
    'purchase-return': 'purchase-returns',
    'payment-voucher': 'payment-vouchers',
    'receipt-voucher': 'receipt-vouchers',
    'journal-voucher': 'journal-vouchers',
    'contra-voucher': 'contra-vouchers',
    'credit-note': 'credit-notes',
    'debit-note': 'debit-notes',
    'non-sales-credit-note': 'non-sales-credit-notes'
  };
  
  return endpointMap[voucherType] || voucherType;
};