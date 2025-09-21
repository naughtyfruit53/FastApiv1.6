// CoASelector.tsx - Shared Chart of Accounts Selector Component

import React, { useState, useEffect, useMemo } from 'react';
import { Search, ChevronDown } from 'lucide-react';
import { getFeatureFlag } from '@/utils/config';

interface ChartAccount {
  id: number;
  account_code: string;
  account_name: string;
  account_type: string;
  display_name: string;
}

interface CoASelectorProps {
  value?: number;
  onChange: (accountId: number | null) => void;
  accountTypes?: string[];
  excludeInactive?: boolean;
  organizationScoped?: boolean;
  placeholder?: string;
  required?: boolean;
  disabled?: boolean;
  componentType?: string; // For payroll component type filtering
  className?: string;
  label?: string;
  error?: string;
}

const CoASelector: React.FC<CoASelectorProps> = ({
  value,
  onChange,
  accountTypes = [],
  excludeInactive = true,
  organizationScoped = true,
  placeholder = "Select chart account...",
  required = false,
  disabled = false,
  componentType,
  className = "",
  label,
  error
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [accounts, setAccounts] = useState<ChartAccount[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedAccount, setSelectedAccount] = useState<ChartAccount | null>(null);

  // Feature flag checks
  const coaRequiredStrict = getFeatureFlag('coaRequiredStrict');
  const payrollEnabled = getFeatureFlag('payrollEnabled');

  // Filter account types based on component type for payroll
  const effectiveAccountTypes = useMemo(() => {
    if (componentType && payrollEnabled) {
      switch (componentType) {
        case 'earning':
        case 'deduction':
          return ['expense'];
        case 'employer_contribution':
          return ['liability'];
        default:
          return accountTypes.length > 0 ? accountTypes : ['expense', 'liability'];
      }
    }
    return accountTypes;
  }, [accountTypes, componentType, payrollEnabled]);

  // Fetch accounts from API
  const fetchAccounts = async (search?: string) => {
    try {
      setLoading(true);
      
      const params = new URLSearchParams();
      if (search) params.append('search', search);
      if (effectiveAccountTypes.length > 0) {
        effectiveAccountTypes.forEach(type => params.append('account_types', type));
      }
      params.append('limit', '50');

      const response = await fetch(`/api/v1/chart-of-accounts/lookup?${params}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch accounts');
      }

      const data = await response.json();
      setAccounts(data.accounts || []);
    } catch (error) {
      console.error('Error fetching chart accounts:', error);
      setAccounts([]);
    } finally {
      setLoading(false);
    }
  };

  // Load accounts on mount and when filters change
  useEffect(() => {
    fetchAccounts();
  }, [effectiveAccountTypes]);

  // Handle search with debouncing
  useEffect(() => {
    const timer = setTimeout(() => {
      if (searchTerm || isOpen) {
        fetchAccounts(searchTerm);
      }
    }, 300);

    return () => clearTimeout(timer);
  }, [searchTerm, isOpen]);

  // Find selected account
  useEffect(() => {
    if (value && accounts.length > 0) {
      const account = accounts.find(acc => acc.id === value);
      setSelectedAccount(account || null);
    } else {
      setSelectedAccount(null);
    }
  }, [value, accounts]);

  const handleSelect = (account: ChartAccount) => {
    onChange(account.id);
    setSelectedAccount(account);
    setIsOpen(false);
    setSearchTerm('');
  };

  const handleClear = () => {
    onChange(null);
    setSelectedAccount(null);
    setSearchTerm('');
  };

  const filteredAccounts = useMemo(() => {
    if (!searchTerm) return accounts;
    return accounts.filter(account =>
      account.display_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      account.account_code.toLowerCase().includes(searchTerm.toLowerCase()) ||
      account.account_name.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }, [accounts, searchTerm]);

  // Don't render if payroll is disabled and this is a payroll component
  if (componentType && !payrollEnabled) {
    return null;
  }

  return (
    <div className={`relative ${className}`}>
      {label && (
        <label className="block text-sm font-medium text-gray-700 mb-1">
          {label}
          {(required || coaRequiredStrict) && <span className="text-red-500 ml-1">*</span>}
        </label>
      )}
      
      <div className="relative">
        <button
          type="button"
          onClick={() => !disabled && setIsOpen(!isOpen)}
          disabled={disabled}
          className={`
            w-full px-3 py-2 border rounded-md shadow-sm text-left
            ${disabled 
              ? 'bg-gray-100 cursor-not-allowed' 
              : 'bg-white hover:border-gray-400 focus:border-blue-500 focus:ring-1 focus:ring-blue-500'
            }
            ${error ? 'border-red-500' : 'border-gray-300'}
            ${selectedAccount ? 'text-gray-900' : 'text-gray-500'}
          `}
        >
          <div className="flex items-center justify-between">
            <span className="truncate">
              {selectedAccount 
                ? `${selectedAccount.account_code} - ${selectedAccount.account_name}`
                : placeholder
              }
            </span>
            <div className="flex items-center space-x-2">
              {selectedAccount && !disabled && (
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleClear();
                  }}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ×
                </button>
              )}
              <ChevronDown className={`w-4 h-4 text-gray-400 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
            </div>
          </div>
        </button>

        {isOpen && !disabled && (
          <div className="absolute z-50 w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg">
            <div className="p-2 border-b border-gray-200">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="text"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  placeholder="Search accounts..."
                  className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                  autoFocus
                />
              </div>
            </div>

            <div className="max-h-60 overflow-y-auto">
              {loading ? (
                <div className="p-3 text-center text-gray-500">Loading accounts...</div>
              ) : filteredAccounts.length > 0 ? (
                filteredAccounts.map((account) => (
                  <button
                    key={account.id}
                    type="button"
                    onClick={() => handleSelect(account)}
                    className={`
                      w-full px-3 py-2 text-left hover:bg-gray-50 focus:bg-gray-50
                      ${selectedAccount?.id === account.id ? 'bg-blue-50 text-blue-900' : 'text-gray-900'}
                    `}
                  >
                    <div className="flex flex-col">
                      <span className="font-medium">{account.account_code} - {account.account_name}</span>
                      <span className="text-xs text-gray-500 capitalize">{account.account_type}</span>
                    </div>
                  </button>
                ))
              ) : (
                <div className="p-3 text-center text-gray-500">
                  {searchTerm ? 'No accounts found matching your search' : 'No accounts available'}
                </div>
              )}
            </div>

            {effectiveAccountTypes.length > 0 && (
              <div className="p-2 border-t border-gray-200 text-xs text-gray-500">
                Showing: {effectiveAccountTypes.join(', ')} accounts
              </div>
            )}
          </div>
        )}
      </div>

      {error && (
        <p className="mt-1 text-sm text-red-600">{error}</p>
      )}

      {coaRequiredStrict && !selectedAccount && (
        <p className="mt-1 text-xs text-orange-600">
          Chart account selection is required for all transactions
        </p>
      )}
    </div>
  );
};

export default CoASelector;