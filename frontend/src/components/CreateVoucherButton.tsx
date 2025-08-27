'use client';

import React from 'react';
import { Button } from '@mui/material';
import { Add } from '@mui/icons-material';
import { useRouter } from 'next/navigation';

interface CreateVoucherButtonProps {
  voucherType: string; // 'purchase', 'sales', 'financial', 'internal'
  visible?: boolean; // Control visibility based on mode (view/edit)
  variant?: 'contained' | 'outlined' | 'text';
  size?: 'small' | 'medium' | 'large';
}

const CreateVoucherButton: React.FC<CreateVoucherButtonProps> = ({
  voucherType,
  visible = true,
  variant = 'contained',
  size = 'medium',
}) => {
  const router = useRouter();

  if (!visible) {
    return null;
  }

  const handleCreateVoucher = () => {
    // Navigate to new voucher creation page based on type
    const routeMap: Record<string, string> = {
      purchase: '/vouchers/Purchase-Vouchers/purchase-voucher',
      sales: '/vouchers/Sales-Vouchers/sales-voucher',
      financial: '/vouchers/financial', // TODO: Implement financial vouchers
      internal: '/vouchers/internal', // TODO: Implement internal vouchers
    };

    const route = routeMap[voucherType.toLowerCase()];
    if (route) {
      router.push(route);
    } else {
      console.warn(`No route defined for voucher type: ${voucherType}`);
    }
  };

  const getButtonText = () => {
    const typeMap: Record<string, string> = {
      purchase: 'Purchase Voucher',
      sales: 'Sales Voucher',
      financial: 'Financial Voucher',
      internal: 'Internal Voucher',
    };

    return `Create ${typeMap[voucherType.toLowerCase()] || 'Voucher'}`;
  };

  return (
    <Button
      variant={variant}
      size={size}
      startIcon={<Add />}
      onClick={handleCreateVoucher}
      sx={{
        backgroundColor: variant === 'contained' ? '#FFD700' : 'transparent',
        color: variant === 'contained' ? '#000' : '#FFD700',
        borderColor: variant === 'outlined' ? '#FFD700' : undefined,
        '&:hover': {
          backgroundColor: variant === 'contained' ? '#FFC107' : 'rgba(255, 215, 0, 0.1)',
          borderColor: variant === 'outlined' ? '#FFC107' : undefined,
        },
        fontWeight: 'bold',
      }}
    >
      {getButtonText()}
    </Button>
  );
};

export default CreateVoucherButton;