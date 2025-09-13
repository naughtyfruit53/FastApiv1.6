// src/hooks/useVoucherDiscounts.ts
// Hook for managing discount logic (toggles, types, dialogs).
import { useState, useEffect } from 'react';

export const useVoucherDiscounts = () => {
  const [lineDiscountEnabled, setLineDiscountEnabled] = useState(false);
  const [lineDiscountType, setLineDiscountType] = useState<'percentage' | 'amount' | null>(null);
  const [totalDiscountEnabled, setTotalDiscountEnabled] = useState(false);
  const [totalDiscountType, setTotalDiscountType] = useState<'percentage' | 'amount' | null>(null);
  const [discountDialogOpen, setDiscountDialogOpen] = useState(false);
  const [discountDialogFor, setDiscountDialogFor] = useState<'line' | 'total' | null>(null);

  // Load saved types from localStorage on mount
  useEffect(() => {
    const savedLineType = localStorage.getItem('voucherLineDiscountType');
    if (savedLineType) {
      setLineDiscountType(savedLineType as 'percentage' | 'amount');
      setLineDiscountEnabled(true);
    }
    const savedTotalType = localStorage.getItem('voucherTotalDiscountType');
    if (savedTotalType) {
      setTotalDiscountType(savedTotalType as 'percentage' | 'amount');
      setTotalDiscountEnabled(true);
    }
  }, []);

  // Save types to localStorage when changed
  useEffect(() => {
    if (lineDiscountType) {
      localStorage.setItem('voucherLineDiscountType', lineDiscountType);
    }
  }, [lineDiscountType]);

  useEffect(() => {
    if (totalDiscountType) {
      localStorage.setItem('voucherTotalDiscountType', totalDiscountType);
    }
  }, [totalDiscountType]);

  const handleToggleLineDiscount = (checked: boolean) => {
    if (checked) {
      if (!lineDiscountType) {
        setDiscountDialogFor('line');
        setDiscountDialogOpen(true);
        return;
      }
      setLineDiscountEnabled(true);
    } else {
      setLineDiscountEnabled(false);
      localStorage.removeItem('voucherLineDiscountType');
      setLineDiscountType(null);
    }
  };

  const handleToggleTotalDiscount = (checked: boolean) => {
    if (checked) {
      if (!totalDiscountType) {
        setDiscountDialogFor('total');
        setDiscountDialogOpen(true);
        return;
      }
      setTotalDiscountEnabled(true);
    } else {
      setTotalDiscountEnabled(false);
      localStorage.removeItem('voucherTotalDiscountType');
      setTotalDiscountType(null);
    }
  };

  const handleDiscountTypeSelect = (type: 'percentage' | 'amount') => {
    if (discountDialogFor === 'line') {
      setLineDiscountType(type);
      setLineDiscountEnabled(true);
    } else if (discountDialogFor === 'total') {
      setTotalDiscountType(type);
      setTotalDiscountEnabled(true);
    }
    setDiscountDialogOpen(false);
    setDiscountDialogFor(null);
  };

  const handleDiscountDialogClose = () => {
    setDiscountDialogOpen(false);
    setDiscountDialogFor(null);
    // Uncheck if dialog canceled without selection
    if (discountDialogFor === 'line') {
      setLineDiscountEnabled(false);
    } else if (discountDialogFor === 'total') {
      setTotalDiscountEnabled(false);
    }
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