// src/utils/nameRefUtils.ts

import { useQuery } from '@tanstack/react-query';
import api from '../lib/api';
import { getVendors, getCustomers } from '../services/masterService';
import { useEntityOptions } from '../hooks/useEntity';
import { EntityType } from '../types/entity.types';

/**
 * Legacy hook for name options - now uses Entity abstraction
 * @deprecated Use useEntityOptions from useEntity hook instead
 */
export const useNameOptions = () => {
  const { options } = useEntityOptions(['Vendor', 'Customer']);
  
  // Convert to legacy format for backward compatibility
  return options.map(option => ({
    ...option.originalData,
    type: option.type
  }));
};

/**
 * Enhanced reference options with Entity support
 */
export const useReferenceOptions = (
  selectedEntityId: number | null, 
  selectedEntityType: EntityType | null
) => {
  const { data: unpaidVouchers } = useQuery({
    queryKey: ['unpaid-vouchers', selectedEntityId, selectedEntityType],
    queryFn: () => {
      if (!selectedEntityId || !selectedEntityType) return [];
      
      // Map entity types to voucher endpoints
      const endpoint = selectedEntityType === 'Vendor' ? '/purchase-vouchers' : 
                     selectedEntityType === 'Customer' ? '/sales-vouchers' : null;
      
      if (!endpoint) return [];
      
      const params = selectedEntityType === 'Vendor' 
        ? { vendor_id: selectedEntityId }
        : { customer_id: selectedEntityId };
      
      return api.get(endpoint, { params }).then(res => res.data);
    },
    enabled: !!selectedEntityId && !!selectedEntityType,
  });

  return [
    ...(unpaidVouchers || []).map(v => v.voucher_number),
    'Advance',
    'On Account'
  ];
};