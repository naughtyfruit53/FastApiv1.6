// components/BalanceDisplay.tsx
// Component to display current balance for selected customers/vendors

import React from 'react';
import { Typography, Box } from '@mui/material';
import { useQuery } from '@tanstack/react-query';
import { getAccountBalance } from '../services/stockService';

interface BalanceDisplayProps {
  accountType: 'customer' | 'vendor' | null;
  accountId: number | null;
  disabled?: boolean;
}

const BalanceDisplay: React.FC<BalanceDisplayProps> = ({ 
  accountType, 
  accountId, 
  disabled = false 
}) => {
  const { data: balanceData, isLoading, isError } = useQuery({
    queryKey: ['accountBalance', accountType, accountId],
    queryFn: getAccountBalance,
    enabled: !disabled && !!accountType && !!accountId,
    staleTime: 5 * 60 * 1000, // Cache for 5 minutes
    gcTime: 10 * 60 * 1000, // Keep in cache for 10 minutes
    refetchOnWindowFocus: false,
    retry: false, // Don't retry on permission errors
  });

  // Don't show anything if disabled, no account selected, loading, or error
  if (disabled || !accountType || !accountId || isLoading || isError || !balanceData) {
    return null;
  }

  const outstandingAmount = balanceData.outstanding_amount || 0;
  const accountName = balanceData.account_name || '';
  
  // Format the balance with proper sign convention
  const formatBalance = (amount: number, type: string) => {
    const absAmount = Math.abs(amount);
    if (type === 'vendor') {
      // For vendors: negative amount means money payable TO vendor
      return amount < 0 
        ? `₹${absAmount.toLocaleString()} payable`
        : `₹${amount.toLocaleString()} advance`;
    } else {
      // For customers: positive amount means money receivable FROM customer
      return amount > 0 
        ? `₹${amount.toLocaleString()} receivable`
        : `₹${absAmount.toLocaleString()} advance`;
    }
  };

  return (
    <Box sx={{ mt: 0.5 }}>
      <Typography
        variant="caption"
        sx={{
          color: 'success.main',
          fontSize: '0.75rem',
          fontWeight: 500,
          display: 'block'
        }}
      >
        Current Balance: {formatBalance(outstandingAmount, accountType)}
      </Typography>
    </Box>
  );
};

export default BalanceDisplay;