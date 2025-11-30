// frontend/src/hooks/useVoucherDateConflict.ts

import { useState, useCallback } from 'react';
import api from '../lib/api';

interface ConflictInfo {
  has_conflict: boolean;
  later_voucher_count: number;
  suggested_date: string;
  period: string;
}

interface ReindexResult {
  success: boolean;
  vouchers_reindexed: number;
  old_to_new_mapping: Record<string, string>;
  error?: string;
}

/**
 * Hook to check for voucher date conflicts at SAVE TIME (not on date entry)
 * Per requirement: Show warning at Save time when voucher date < latest existing voucher date
 * 
 * @param voucherType - The voucher API endpoint (e.g., 'purchase-orders', 'sales-vouchers')
 * @returns Conflict checking functions and state
 */
export const useVoucherDateConflict = (voucherType: string) => {
  const [conflictInfo, setConflictInfo] = useState<ConflictInfo | null>(null);
  const [isChecking, setIsChecking] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showConflictModal, setShowConflictModal] = useState(false);

  /**
   * Check for backdated voucher conflict - call this at SAVE time
   * Returns true if there's a conflict (caller should show modal)
   */
  const checkConflictAtSave = useCallback(async (
    selectedDate: Date | string | null
  ): Promise<boolean> => {
    if (!selectedDate || !voucherType) {
      setConflictInfo(null);
      return false;
    }

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
      
      if (response.data?.has_conflict) {
        setShowConflictModal(true);
        return true;
      }
      
      return false;
    } catch (err: any) {
      console.error('Error checking voucher date conflict:', err);
      setError(err.response?.data?.detail || 'Failed to check for conflicts');
      setConflictInfo(null);
      return false;
    } finally {
      setIsChecking(false);
    }
  }, [voucherType]);

  /**
   * Request voucher reindexing after user confirms backdated insert
   * This realigns voucher numbering to maintain chronological order
   */
  const requestReindexing = useCallback(async (
    newVoucherId: number,
    newVoucherDate: Date | string
  ): Promise<ReindexResult> => {
    try {
      const dateString = newVoucherDate instanceof Date 
        ? newVoucherDate.toISOString()
        : newVoucherDate;
        
      const response = await api.post(
        `/api/v1/${voucherType}/reindex`,
        {
          voucher_id: newVoucherId,
          voucher_date: dateString
        }
      );
      
      return response.data;
    } catch (err: any) {
      console.error('Error requesting voucher reindexing:', err);
      return {
        success: false,
        vouchers_reindexed: 0,
        old_to_new_mapping: {},
        error: err.response?.data?.detail || 'Failed to reindex vouchers'
      };
    }
  }, [voucherType]);

  const closeConflictModal = useCallback(() => {
    setShowConflictModal(false);
  }, []);

  const resetConflict = useCallback(() => {
    setConflictInfo(null);
    setShowConflictModal(false);
    setError(null);
  }, []);

  return { 
    conflictInfo, 
    isChecking, 
    error,
    showConflictModal,
    hasConflict: conflictInfo?.has_conflict || false,
    checkConflictAtSave,
    requestReindexing,
    closeConflictModal,
    resetConflict
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

  const fetchVoucherNumber = useCallback(async () => {
    if (!selectedDate || !voucherType) {
      return;
    }

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
  }, [selectedDate, voucherType]);

  return { voucherNumber, isLoading, error, fetchVoucherNumber };
};

export default useVoucherDateConflict;
