// components/StockDisplay.tsx
// Component to display current stock quantity for selected products

import React from 'react';
import { Typography, Box } from '@mui/material';
import { useQuery } from '@tanstack/react-query';
import { getProductStock } from '../services/stockService';

interface StockDisplayProps {
  productId: number | null;
  disabled?: boolean;
  showLabel?: boolean; // New prop to control whether to show "Current Stock:" label
}

const StockDisplay: React.FC<StockDisplayProps> = ({ productId, disabled = false, showLabel = true }) => {
  const { data: stockData, isLoading, isError } = useQuery({
    queryKey: ['productStock', productId],
    queryFn: getProductStock,
    enabled: !disabled && !!productId,
    staleTime: 5 * 60 * 1000, // Cache for 5 minutes
    gcTime: 10 * 60 * 1000, // Keep in cache for 10 minutes
    refetchOnWindowFocus: false,
    retry: false, // Don't retry on permission errors
  });

  // Don't show anything if disabled, no product selected, loading, or error
  if (disabled || !productId || isLoading || isError || !stockData) {
    return null;
  }

  const stockQuantity = stockData.quantity || 0;
  const unit = stockData.unit || '';

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
        {showLabel ? `Current Stock: ${stockQuantity} ${unit}` : `${stockQuantity} ${unit}`}
      </Typography>
    </Box>
  );
};

export default StockDisplay;