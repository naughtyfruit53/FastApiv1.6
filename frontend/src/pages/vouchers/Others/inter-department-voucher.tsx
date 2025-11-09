// frontend/src/pages/vouchers/Others/inter-department-voucher.tsx
'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import VoucherLayout from '../../../components/VoucherLayout';
import VoucherDateConflictModal from '../../../components/VoucherDateConflictModal';
import api from '../../../utils/api';

import { ProtectedPage } from '../../../components/ProtectedPage';
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
  const router = useRouter();
  const { id, mode = 'create' } = router.query;
  const isEditMode = mode === 'edit';
  const [voucherData, setVoucherData] = useState<InterDepartmentVoucherData>(defaultVoucherData);
  const [loading, setLoading] = useState<boolean>(false);
  const [submitting, setSubmitting] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<boolean>(false);

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
  
  // State for voucher date conflict detection
  const [conflictInfo, setConflictInfo] = useState<any>(null);
  const [showConflictModal, setShowConflictModal] = useState(false);
  const [pendingDate, setPendingDate] = useState<string | null>(null);

  // Load voucher data if in edit or view mode
  useEffect(() => {
    if (id && (mode === 'edit' || mode === 'view')) {
      const fetchData = async () => {
        setLoading(true);
        try {
          const response = await api.get(`/vouchers/inter-department-vouchers/${id}`);
          setVoucherData(response.data);
        } catch (err: any) {
          setError(err.message || 'Error loading voucher data');
          console.error('Error fetching voucher data:', err);
        } finally {
          setLoading(false);
        }
      };
      fetchData();
    }
  }, [id, mode]);

  // Calculate total amount when items change
  useEffect(() => {
    const total = (voucherData?.items || []).reduce((sum, item) => sum + (item.amount || 0), 0);
    setVoucherData((prev) => ({ ...prev, total_amount: total }));
  }, [voucherData?.items]);

  // Fetch voucher number when date changes and check for conflicts
  useEffect(() => {
    const fetchVoucherNumber = async () => {
      const currentDate = voucherData?.date || '';
      if (currentDate && mode === 'create') {
        try {
          // Fetch new voucher number based on date
          const response = await api.get(
            `/vouchers/inter-department-vouchers/next-number`,
            { params: { voucher_date: currentDate } }
          );
          setVoucherData((prev) => ({ ...prev, voucher_number: response.data }));
          
          // Check for backdated conflicts
          const conflictResponse = await api.get(
            `/vouchers/inter-department-vouchers/check-backdated-conflict`,
            { params: { voucher_date: currentDate } }
          );
          
          if (conflictResponse.data.has_conflict) {
            setConflictInfo(conflictResponse.data);
            setShowConflictModal(true);
            setPendingDate(currentDate);
          }
        } catch (error) {
          console.error('Error fetching voucher number:', error);
        }
      }
    };
    
    fetchVoucherNumber();
  }, [voucherData?.date, mode]);

  const handleItemChange = (index: number, field: keyof InterDepartmentVoucherItem, value: any) => {
    const updatedItems = [...(voucherData?.items || [])];
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
    setVoucherData((prev) => ({ ...prev, items: [...(prev.items || []), newItem] }));
  };

  const removeItem = (index: number) => {
    const updatedItems = (voucherData?.items || []).filter((_, i) => i !== index);
    setVoucherData((prev) => ({ ...prev, items: updatedItems }));
  };

  const submitVoucher = async (data: InterDepartmentVoucherData) => {
    setSubmitting(true);
    setError(null);
    setSuccess(false);
    try {
      let response;
      if (mode === 'create') {
        response = await api.post('/vouchers/inter-department-vouchers', data);
      } else if (mode === 'edit') {
        response = await api.put(`/vouchers/inter-department-vouchers/${id}`, data);
      }
      console.log('Voucher submitted successfully:', response?.data);
      setSuccess(true);
      // Optional: Redirect or reset after success
      setTimeout(() => {
        setSuccess(false);
        if (mode === 'create') {
          setVoucherData(defaultVoucherData);
        }
      }, 3000);
    } catch (err: any) {
      setError(err.message || 'Error submitting voucher');
      console.error('Error submitting voucher:', err);
    } finally {
      setSubmitting(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await submitVoucher(voucherData || defaultVoucherData);
  };

  const resetForm = () => {
    setVoucherData(defaultVoucherData);
    setError(null);
    setSuccess(false);
  };

  // Conflict modal handlers
  const handleChangeDateToSuggested = () => {
    if (conflictInfo?.suggested_date) {
      setVoucherData((prev) => ({ ...prev, date: conflictInfo.suggested_date.split('T')[0] }));
      setShowConflictModal(false);
      setPendingDate(null);
    }
  };

  const handleProceedAnyway = () => {
    setShowConflictModal(false);
  };

  const handleCancelConflict = () => {
    setShowConflictModal(false);
    if (pendingDate) {
      setVoucherData((prev) => ({ ...prev, date: '' }));
    }
    setPendingDate(null);
  };
  return (
    <ProtectedPage moduleKey="finance" action="write">
      <VoucherLayout
      title="Inter Department Voucher"
      voucherData={voucherData || defaultVoucherData}
      onSubmit={handleSubmit}
      loading={loading}
      submitting={submitting}
      error={error}
      success={success}
      onReset={resetForm}
      isEditMode={isEditMode}
      mode={mode as string}
      customFields={
        <>
          {/* From Department Field */}
          <select
            value={voucherData?.from_department || ''}
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
            value={voucherData?.to_department || ''}
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
            {departments.filter(dept => dept !== voucherData?.from_department).map((dept) => (
              <option key={dept} value={dept}>{dept}</option>
            ))}
          </select>
        </>
      }
      items={voucherData?.items || []}
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
      <VoucherDateConflictModal
        open={showConflictModal}
        onClose={handleCancelConflict}
        conflictInfo={conflictInfo}
        onChangeDateToSuggested={handleChangeDateToSuggested}
        onProceedAnyway={handleProceedAnyway}
        voucherType="Inter-Department Voucher"
      />
    </ProtectedPage>
  );
};
export default InterDepartmentVoucherPage;
