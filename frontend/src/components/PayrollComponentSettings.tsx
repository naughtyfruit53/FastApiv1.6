// PayrollComponentSettings.tsx - Payroll Component Configuration Page

import React, { useState, useEffect } from 'react';
import { Plus, Edit, Trash2, Save, X, AlertCircle } from 'lucide-react';
import CoASelector from '@/components/CoASelector';
import { getFeatureFlag } from '@/utils/config';

interface PayrollComponent {
  id: number;
  component_name: string;
  component_code: string;
  component_type: string;
  expense_account_id?: number;
  payable_account_id?: number;
  is_active: boolean;
  is_taxable: boolean;
  calculation_formula?: string;
  default_amount?: number;
  default_percentage?: number;
  expense_account?: {
    id: number;
    account_code: string;
    account_name: string;
    account_type: string;
  };
  payable_account?: {
    id: number;
    account_code: string;
    account_name: string;
    account_type: string;
  };
}

interface ComponentFormData {
  component_name: string;
  component_code: string;
  component_type: string;
  expense_account_id?: number;
  payable_account_id?: number;
  is_active: boolean;
  is_taxable: boolean;
  calculation_formula?: string;
  default_amount?: number;
  default_percentage?: number;
}

const PayrollComponentSettings: React.FC = () => {
  const [components, setComponents] = useState<PayrollComponent[]>([]);
  const [loading, setLoading] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [formData, setFormData] = useState<ComponentFormData>({
    component_name: '',
    component_code: '',
    component_type: 'earning',
    is_active: true,
    is_taxable: true
  });
  const [errors, setErrors] = useState<Record<string, string>>({});

  // Feature flags
  const payrollEnabled = getFeatureFlag('payrollEnabled');
  const coaRequiredStrict = getFeatureFlag('coaRequiredStrict');

  // Don't render if payroll is disabled
  if (!payrollEnabled) {
    return (
      <div className="p-6 bg-yellow-50 rounded-lg">
        <div className="flex items-center">
          <AlertCircle className="w-5 h-5 text-yellow-600 mr-2" />
          <p className="text-yellow-800">Payroll functionality is currently disabled.</p>
        </div>
      </div>
    );
  }

  useEffect(() => {
    fetchComponents();
  }, []);

  const fetchComponents = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/v1/payroll/components', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });

      if (!response.ok) throw new Error('Failed to fetch components');
      
      const data = await response.json();
      setComponents(data.components || []);
    } catch (error) {
      console.error('Error fetching components:', error);
    } finally {
      setLoading(false);
    }
  };

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.component_name.trim()) {
      newErrors.component_name = 'Component name is required';
    }

    if (!formData.component_code.trim()) {
      newErrors.component_code = 'Component code is required';
    }

    if (coaRequiredStrict) {
      if (!formData.expense_account_id) {
        newErrors.expense_account_id = 'Expense account is required';
      }
      if (formData.component_type !== 'earning' && !formData.payable_account_id) {
        newErrors.payable_account_id = 'Payable account is required for deductions and contributions';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) return;

    try {
      const url = editingId 
        ? `/api/v1/payroll/components/${editingId}`
        : '/api/v1/payroll/components';
      
      const method = editingId ? 'PUT' : 'POST';

      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify(formData)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to save component');
      }

      await fetchComponents();
      resetForm();
    } catch (error) {
      console.error('Error saving component:', error);
      // You could add a toast notification here
    }
  };

  const handleEdit = (component: PayrollComponent) => {
    setFormData({
      component_name: component.component_name,
      component_code: component.component_code,
      component_type: component.component_type,
      expense_account_id: component.expense_account_id,
      payable_account_id: component.payable_account_id,
      is_active: component.is_active,
      is_taxable: component.is_taxable,
      calculation_formula: component.calculation_formula,
      default_amount: component.default_amount,
      default_percentage: component.default_percentage
    });
    setEditingId(component.id);
    setShowForm(true);
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this component?')) return;

    try {
      const response = await fetch(`/api/v1/payroll/components/${id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });

      if (!response.ok) throw new Error('Failed to delete component');
      
      await fetchComponents();
    } catch (error) {
      console.error('Error deleting component:', error);
    }
  };

  const resetForm = () => {
    setFormData({
      component_name: '',
      component_code: '',
      component_type: 'earning',
      is_active: true,
      is_taxable: true
    });
    setEditingId(null);
    setShowForm(false);
    setErrors({});
  };

  const getComponentTypeColor = (type: string) => {
    switch (type) {
      case 'earning': return 'bg-green-100 text-green-800';
      case 'deduction': return 'bg-red-100 text-red-800';
      case 'employer_contribution': return 'bg-blue-100 text-blue-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Payroll Component Settings</h1>
          <p className="text-gray-600 mt-1">Configure payroll components and their chart account mappings</p>
        </div>
        <button
          onClick={() => setShowForm(true)}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 flex items-center gap-2"
        >
          <Plus className="w-4 h-4" />
          Add Component
        </button>
      </div>

      {showForm && (
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-semibold">
              {editingId ? 'Edit Component' : 'Add New Component'}
            </h2>
            <button onClick={resetForm} className="text-gray-400 hover:text-gray-600">
              <X className="w-5 h-5" />
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Component Name *
                </label>
                <input
                  type="text"
                  value={formData.component_name}
                  onChange={(e) => setFormData({...formData, component_name: e.target.value})}
                  className={`w-full px-3 py-2 border rounded-md ${errors.component_name ? 'border-red-500' : 'border-gray-300'}`}
                  placeholder="e.g., Basic Salary, HRA, Professional Tax"
                />
                {errors.component_name && <p className="text-red-500 text-xs mt-1">{errors.component_name}</p>}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Component Code *
                </label>
                <input
                  type="text"
                  value={formData.component_code}
                  onChange={(e) => setFormData({...formData, component_code: e.target.value.toUpperCase()})}
                  className={`w-full px-3 py-2 border rounded-md ${errors.component_code ? 'border-red-500' : 'border-gray-300'}`}
                  placeholder="e.g., BS, HRA, PT"
                />
                {errors.component_code && <p className="text-red-500 text-xs mt-1">{errors.component_code}</p>}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Component Type
                </label>
                <select
                  value={formData.component_type}
                  onChange={(e) => setFormData({...formData, component_type: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                >
                  <option value="earning">Earning</option>
                  <option value="deduction">Deduction</option>
                  <option value="employer_contribution">Employer Contribution</option>
                </select>
              </div>

              <div className="flex items-center space-x-4">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={formData.is_active}
                    onChange={(e) => setFormData({...formData, is_active: e.target.checked})}
                    className="mr-2"
                  />
                  Active
                </label>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={formData.is_taxable}
                    onChange={(e) => setFormData({...formData, is_taxable: e.target.checked})}
                    className="mr-2"
                  />
                  Taxable
                </label>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <CoASelector
                label="Expense Account"
                value={formData.expense_account_id}
                onChange={(accountId) => setFormData({...formData, expense_account_id: accountId || undefined})}
                accountTypes={['expense']}
                componentType={formData.component_type}
                placeholder="Select expense account..."
                required={coaRequiredStrict}
                error={errors.expense_account_id}
              />

              {formData.component_type !== 'earning' && (
                <CoASelector
                  label="Payable Account"
                  value={formData.payable_account_id}
                  onChange={(accountId) => setFormData({...formData, payable_account_id: accountId || undefined})}
                  accountTypes={['liability']}
                  componentType={formData.component_type}
                  placeholder="Select payable account..."
                  required={coaRequiredStrict && formData.component_type !== 'earning'}
                  error={errors.payable_account_id}
                />
              )}
            </div>

            <div className="flex justify-end space-x-2">
              <button
                type="button"
                onClick={resetForm}
                className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 flex items-center gap-2"
              >
                <Save className="w-4 h-4" />
                {editingId ? 'Update' : 'Create'}
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="bg-white border border-gray-200 rounded-lg">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Component</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Expense Account</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Payable Account</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {loading ? (
                <tr>
                  <td colSpan={6} className="px-6 py-4 text-center text-gray-500">Loading components...</td>
                </tr>
              ) : components.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-4 text-center text-gray-500">No components configured</td>
                </tr>
              ) : (
                components.map((component) => (
                  <tr key={component.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4">
                      <div>
                        <div className="text-sm font-medium text-gray-900">{component.component_name}</div>
                        <div className="text-sm text-gray-500">{component.component_code}</div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${getComponentTypeColor(component.component_type)}`}>
                        {component.component_type.replace('_', ' ')}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900">
                      {component.expense_account ? (
                        <div>
                          <div>{component.expense_account.account_code}</div>
                          <div className="text-gray-500">{component.expense_account.account_name}</div>
                        </div>
                      ) : (
                        <span className="text-gray-400">Not set</span>
                      )}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900">
                      {component.payable_account ? (
                        <div>
                          <div>{component.payable_account.account_code}</div>
                          <div className="text-gray-500">{component.payable_account.account_name}</div>
                        </div>
                      ) : (
                        <span className="text-gray-400">Not set</span>
                      )}
                    </td>
                    <td className="px-6 py-4">
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                        component.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                      }`}>
                        {component.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm font-medium space-x-2">
                      <button
                        onClick={() => handleEdit(component)}
                        className="text-blue-600 hover:text-blue-900"
                      >
                        <Edit className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleDelete(component.id)}
                        className="text-red-600 hover:text-red-900"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default PayrollComponentSettings;