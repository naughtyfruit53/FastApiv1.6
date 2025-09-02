// frontend/src/pages/vouchers/Others/inter-department-voucher.tsx
'use client';

import React, { useState, useEffect } from 'react';
import { useVoucherPage } from '../../../hooks/useVoucherPage';
import VoucherLayout from '../../../components/VoucherLayout';

interface InterDepartmentVoucherItem {
  id?: number;
  product: string;
  quantity: number;
  rate: number;
  amount: number;
  description?: string;
}

interface InterDepartmentVoucherData {
  id?: number;
  voucher_number?: string;
  date: string;
  from_department: string;
  to_department: string;
  total_amount: number;
  status: string;
  notes?: string;
  items: InterDepartmentVoucherItem[];
}

const defaultVoucherData: InterDepartmentVoucherData = {
  date: new Date().toISOString().split('T')[0],
  from_department: '',
  to_department: '',
  total_amount: 0,
  status: 'draft',
  notes: '',
  items: []
};

const InterDepartmentVoucherPage: React.FC = () => {
  const {
    voucherData,
    setVoucherData,
    loading,
    submitting,
    error,
    success,
    submitVoucher,
    resetForm,
    isEditMode,
    mode
  } = useVoucherPage<InterDepartmentVoucherData>({
    voucherType: 'inter-department-vouchers',
    defaultData: defaultVoucherData
  });

  const [departments] = useState([
    'Finance',
    'HR',
    'IT',
    'Operations',
    'Sales',
    'Marketing',
    'Production',
    'Quality Control',
    'Warehouse',
    'Maintenance'
  ]);

  // Calculate total amount when items change
  useEffect(() => {
    const total = voucherData.items.reduce((sum, item) => sum + (item.amount || 0), 0);
    setVoucherData((prev) => ({ ...prev, total_amount: total }));
  }, [voucherData.items, setVoucherData]);

  const handleItemChange = (index: number, field: keyof InterDepartmentVoucherItem, value: any) => {
    const updatedItems = [...voucherData.items];
    updatedItems[index] = { ...updatedItems[index], [field]: value };
    
    // Auto-calculate amount when quantity or rate changes
    if (field === 'quantity' || field === 'rate') {
      const item = updatedItems[index];
      updatedItems[index].amount = (item.quantity || 0) * (item.rate || 0);
    }
    
    setVoucherData((prev) => ({ ...prev, items: updatedItems }));
  };

  const addItem = () => {
    const newItem: InterDepartmentVoucherItem = {
      product: '',
      quantity: 0,
      rate: 0,
      amount: 0,
      description: ''
    };
    setVoucherData((prev) => ({ ...prev, items: [...prev.items, newItem] }));
  };

  const removeItem = (index: number) => {
    const updatedItems = voucherData.items.filter((_, i) => i !== index);
    setVoucherData((prev) => ({ ...prev, items: updatedItems }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await submitVoucher(voucherData);
  };

  return (
    <VoucherLayout
      title="Inter Department Voucher"
      voucherData={voucherData}
      onSubmit={handleSubmit}
      loading={loading}
      submitting={submitting}
      error={error}
      success={success}
      onReset={resetForm}
      isEditMode={isEditMode}
      mode={mode}
      customFields={
        <>
          {/* From Department Field */}
          <select
            value={voucherData.from_department}
            onChange={(e) => setVoucherData((prev) => ({ ...prev, from_department: e.target.value }))}
            required
            style={{
              width: '100%',
              padding: '12px',
              border: '1px solid #ddd',
              borderRadius: '4px',
              fontSize: '16px'
            }}
          >
            <option value="">Select From Department</option>
            {departments.map((dept) => (
              <option key={dept} value={dept}>{dept}</option>
            ))}
          </select>

          {/* To Department Field */}
          <select
            value={voucherData.to_department}
            onChange={(e) => setVoucherData((prev) => ({ ...prev, to_department: e.target.value }))}
            required
            style={{
              width: '100%',
              padding: '12px',
              border: '1px solid #ddd',
              borderRadius: '4px',
              fontSize: '16px'
            }}
          >
            <option value="">Select To Department</option>
            {departments.filter(dept => dept !== voucherData.from_department).map((dept) => (
              <option key={dept} value={dept}>{dept}</option>
            ))}
          </select>
        </>
      }
      items={voucherData.items}
      onItemChange={handleItemChange}
      onAddItem={addItem}
      onRemoveItem={removeItem}
      itemColumns={[
        { key: 'product', label: 'Product/Item', type: 'text', required: true },
        { key: 'description', label: 'Description', type: 'text' },
        { key: 'quantity', label: 'Quantity', type: 'number', required: true },
        { key: 'rate', label: 'Rate', type: 'number', required: true },
        { key: 'amount', label: 'Amount', type: 'number', readOnly: true }
      ]}
    />
  );
};

export default InterDepartmentVoucherPage;