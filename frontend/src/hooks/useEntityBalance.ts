// frontend/src/hooks/useEntityBalance.ts
// Hook for fetching and displaying vendor/customer balance
import { useState, useEffect } from 'react';
import { getEntityBalance } from '../services/ledgerService';

interface UseEntityBalanceResult {
  balance: number;
  loading: boolean;
  error: string | null;
}

export const useEntityBalance = (
  entityType: 'vendor' | 'customer' | null,
  entityId: number | null
): UseEntityBalanceResult => {
  const [balance, setBalance] = useState<number>(0);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchBalance = async () => {
      if (!entityType || !entityId) {
        setBalance(0);
        setLoading(false);
        setError(null);
        return;
      }

      setLoading(true);
      setError(null);

      try {
        const fetchedBalance = await getEntityBalance(entityType, String(entityId));
        setBalance(fetchedBalance);
      } catch (err: any) {
        console.error('Error fetching entity balance:', err);
        setError(err.message || 'Failed to fetch balance');
        setBalance(0);
      } finally {
        setLoading(false);
      }
    };

    fetchBalance();
  }, [entityType, entityId]);

  return { balance, loading, error };
};

// Format balance for display (up to 8 digits as specified)
export const formatBalance = (balance: number): string => {
  const absBalance = Math.abs(balance);
  if (absBalance > 99999999) {
    // More than 8 digits, show in crores
    return `₹${(balance / 10000000).toFixed(2)}Cr`;
  }
  return `₹${balance.toLocaleString('en-IN', { maximumFractionDigits: 2 })}`;
};

// Get balance display text without Dr/Cr indicator
export const getBalanceDisplayText = (balance: number): string => {
  if (balance === 0) return '₹0';
  return formatBalance(Math.abs(balance));
};

// Get color for balance: red for payable (negative), green for receivable (positive)
export const getBalanceColor = (balance: number): string => {
  if (balance === 0) return 'black';
  return balance > 0 ? 'green' : 'red';
};