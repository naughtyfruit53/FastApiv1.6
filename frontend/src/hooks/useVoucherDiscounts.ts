// src/hooks/useVoucherDiscounts.ts
// Hook for managing discount logic (toggles, types, dialogs).
import { useState } from 'react';

export const useVoucherDiscounts = () => {
  const [lineDiscountEnabled, setLineDiscountEnabled] = useState(false);
  const [lineDiscountType, setLineDiscountType] = useState<'percentage' | 'amount'>('percentage');
  const [totalDiscountEnabled, setTotalDiscountEnabled] = useState(false);
  const [totalDiscountType, setTotalDiscountType] = useState<'percentage' | 'amount'>('percentage');
  const [discountDialogOpen, setDiscountDialogOpen] = useState(false);
  const [discountDialogFor, setDiscountDialogFor] = useState<'line' | 'total'>('line');

  const handleToggleLineDiscount = (checked: boolean) => {
    if (checked && !lineDiscountType) {
      setDiscountDialogFor('line');
      setDiscountDialogOpen(true);
    } else {
      setLineDiscountEnabled(checked);
      if (!checked) setLineDiscountType('percentage'); // Reset type
    }
  };

  const handleToggleTotalDiscount = (checked: boolean) => {
    if (checked && !totalDiscountType) {
      setDiscountDialogFor('total');
      setDiscountDialogOpen(true);
    } else {
      setTotalDiscountEnabled(checked);
      if (!checked) setTotalDiscountType('percentage'); // Reset type
    }
  };

  const handleDiscountTypeSelect = (type: 'percentage' | 'amount') => {
    if (discountDialogFor === 'line') {
      setLineDiscountType(type);
      setLineDiscountEnabled(true);
    } else {
      setTotalDiscountType(type);
      setTotalDiscountEnabled(true);
    }
    setDiscountDialogOpen(false);
  };

  const handleDiscountDialogClose = () => {
    setDiscountDialogOpen(false);
  };

  return {
    lineDiscountEnabled,
    lineDiscountType,
    totalDiscountEnabled,
    totalDiscountType,
    discountDialogOpen,
    discountDialogFor,
    handleToggleLineDiscount,
    handleToggleTotalDiscount,
    handleDiscountTypeSelect,
    handleDiscountDialogClose,
  };
};