// frontend/src/hooks/useVoucherDateConflict.ts

import { useState, useEffect } from 'react';
import api from '../lib/api';

interface ConflictInfo {
  has_conflict: boolean;
  later_voucher_count: number;
  suggested_date: string;
  period: string;
}

/**
 * Hook to check for voucher date conflicts
 * @param voucherType - The voucher API endpoint (e.g., 'purchase-orders', 'sales-vouchers')
 * @param selectedDate - The selected voucher date
 * @returns Conflict information and loading state
 */
export const useVoucherDateConflict = (
  voucherType: string,
  selectedDate: Date | string | null
) => {
  const [conflictInfo, setConflictInfo] = useState<ConflictInfo | null>(null);
  const [isChecking, setIsChecking] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!selectedDate || !voucherType) {
      setConflictInfo(null);
      return;
    }

    const checkConflict = async () => {
      setIsChecking(true);
      setError(null);
      
      try {
        const dateString = selectedDate instanceof Date 
          ? selectedDate.toISOString()
          : selectedDate;
          
        const response = await api.get(
          `/api/v1/${voucherType}/check-backdated-conflict`,
          {
            params: {
              voucher_date: dateString
            }
          }
        );
        
        setConflictInfo(response.data);
      } catch (err: any) {
        console.error('Error checking voucher date conflict:', err);
        setError(err.response?.data?.detail || 'Failed to check for conflicts');
        setConflictInfo(null);
      } finally {
        setIsChecking(false);
      }
    };

    // Debounce the API call to avoid too many requests
    const debounceTimer = setTimeout(checkConflict, 500);
    
    return () => {
      clearTimeout(debounceTimer);
    };
  }, [selectedDate, voucherType]);

  return { 
    conflictInfo, 
    isChecking, 
    error,
    hasConflict: conflictInfo?.has_conflict || false
  };
};

/**
 * Hook to get next voucher number based on selected date
 * @param voucherType - The voucher API endpoint
 * @param selectedDate - The selected voucher date
 * @returns Next voucher number and loading state
 */
export const useVoucherNumberForDate = (
  voucherType: string,
  selectedDate: Date | string | null
) => {
  const [voucherNumber, setVoucherNumber] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!selectedDate || !voucherType) {
      return;
    }

    const fetchVoucherNumber = async () => {
      setIsLoading(true);
      setError(null);
      
      try {
        const dateString = selectedDate instanceof Date 
          ? selectedDate.toISOString()
          : selectedDate;
          
        const response = await api.get(
          `/api/v1/${voucherType}/next-number`,
          {
            params: {
              voucher_date: dateString
            }
          }
        );
        
        setVoucherNumber(response.data);
      } catch (err: any) {
        console.error('Error fetching voucher number:', err);
        setError(err.response?.data?.detail || 'Failed to fetch voucher number');
      } finally {
        setIsLoading(false);
      }
    };

    // Debounce the API call
    const debounceTimer = setTimeout(fetchVoucherNumber, 500);
    
    return () => {
      clearTimeout(debounceTimer);
    };
  }, [selectedDate, voucherType]);

  return { voucherNumber, isLoading, error };
};

export default useVoucherDateConflict;
