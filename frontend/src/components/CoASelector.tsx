// CoASelector.tsx - Shared Chart of Accounts Selector Component

import React, { useState, useEffect, useMemo } from 'react';
import { Search, ChevronDown, AlertTriangle, Info } from 'lucide-react';
import { getFeatureFlag, shouldEnforceCoA, shouldWarnAboutCoA, isLegacyModeAllowed, getEnforcementLevel } from '@/utils/config';

interface ChartAccount {
  id: number;
  account_code: string;
  account_name: string;
  account_type: string;
  display_name: string;
  is_active?: boolean;
  organization_id?: number;
  parent_id?: number;
  description?: string;
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
  departmentId?: number; // For department-specific defaults
  className?: string;
  label?: string;
  error?: string;
  // Phase 2 enhancements
  allowLegacyMode?: boolean; // Allow legacy account references
  showWarnings?: boolean; // Show CoA warnings
  enforcementOverride?: boolean; // Override enforcement settings
  defaultAccountId?: number; // Department/category-specific defaults
  onValidationChange?: (isValid: boolean, message?: string) => void;
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
  departmentId,
  className = "",
  label,
  error,
  // Phase 2 props
  allowLegacyMode = false,
  showWarnings = true,
  enforcementOverride = false,
  defaultAccountId,
  onValidationChange
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [accounts, setAccounts] = useState<ChartAccount[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedAccount, setSelectedAccount] = useState<ChartAccount | null>(null);
  const [validationMessage, setValidationMessage] = useState<string>('');
  const [isLegacyAccount, setIsLegacyAccount] = useState(false);

  // Enhanced feature flag checks (Phase 2)
  const coaRequiredStrict = shouldEnforceCoA() || enforcementOverride;
  const payrollEnabled = getFeatureFlag('payrollEnabled');
  const shouldShowWarnings = shouldWarnAboutCoA() && showWarnings;
  const legacyModeAllowed = (isLegacyModeAllowed() || allowLegacyMode) && !enforcementOverride;
  const enforcementLevel = getEnforcementLevel();

  // Enhanced account type filtering with department-specific logic
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

  // Enhanced validation logic
  const validateSelection = (account: ChartAccount | null) => {
    let isValid = true;
    let message = '';

    if (!account && (required || coaRequiredStrict)) {
      isValid = false;
      message = 'Chart account selection is required';
    } else if (account) {
      // Check if account is active
      if (account.is_active === false && excludeInactive) {
        isValid = false;
        message = 'Selected account is inactive';
      }
      
      // Check account type compatibility
      if (effectiveAccountTypes.length > 0 && !effectiveAccountTypes.includes(account.account_type.toLowerCase())) {
        isValid = false;
        message = `Account type must be one of: ${effectiveAccountTypes.join(', ')}`;
      }

      // Check for legacy account patterns (simplified check)
      const isLegacy = account.account_code?.startsWith('LEG_') || account.account_name?.includes('[Legacy]') || account.display_name?.includes('[Legacy]');
      setIsLegacyAccount(isLegacy);
      
      if (isLegacy && !legacyModeAllowed) {
        isValid = false;
        message = 'Legacy accounts are not allowed in current enforcement mode';
      } else if (isLegacy && shouldShowWarnings) {
        message = 'Warning: This is a legacy account. Consider migrating to a new account.';
      }
    }

    setValidationMessage(message);
    onValidationChange?.(isValid, message);
    return isValid;
  };

  // Fetch accounts from API with enhanced filtering
  const fetchAccounts = async (search?: string) => {
    try {
      setLoading(true);
      
      const params = new URLSearchParams();
      if (search) params.append('search', search);
      if (effectiveAccountTypes.length > 0) {
        effectiveAccountTypes.forEach(type => params.append('account_types', type));
      }
      if (excludeInactive) params.append('exclude_inactive', 'true');
      if (organizationScoped) params.append('organization_scoped', 'true');
      if (departmentId) params.append('department_id', departmentId.toString());
      
      // Phase 2: Enhanced filtering options
      if (!legacyModeAllowed) params.append('exclude_legacy', 'true');
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
  }, [effectiveAccountTypes, departmentId, legacyModeAllowed]);

  // Handle search with debouncing
  useEffect(() => {
    const timer = setTimeout(() => {
      if (searchTerm || isOpen) {
        fetchAccounts(searchTerm);
      }
    }, 300);

    return () => clearTimeout(timer);
  }, [searchTerm, isOpen]);

  // Find selected account and validate
  useEffect(() => {
    if (value && accounts.length > 0) {
      const account = accounts.find(acc => acc.id === value);
      setSelectedAccount(account || null);
      validateSelection(account || null);
    } else {
      setSelectedAccount(null);
      validateSelection(null);
    }
  }, [value, accounts]);

  // Apply default account if provided
  useEffect(() => {
    if (defaultAccountId && !value) {
      onChange(defaultAccountId);
    }
  }, [defaultAccountId, value, onChange]);

  const handleSelect = (account: ChartAccount) => {
    if (validateSelection(account)) {
      onChange(account.id);
      setSelectedAccount(account);
      setIsOpen(false);
      setSearchTerm('');
    }
  };

  const handleClear = () => {
    onChange(null);
    setSelectedAccount(null);
    setSearchTerm('');
    validateSelection(null);
  };

  const getWarningIcon = () => {
    if (enforcementLevel === 'enforce' && !selectedAccount) {
      return <AlertTriangle className="w-4 h-4 text-red-500" />;
    }
    if (shouldShowWarnings && (isLegacyAccount || validationMessage)) {
      return <Info className="w-4 h-4 text-yellow-500" />;
    }
    return null;
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
          {enforcementLevel === 'enforce' && <span className="ml-1 text-xs bg-red-100 text-red-700 px-1 rounded">ENFORCED</span>}
          {enforcementLevel === 'warn' && <span className="ml-1 text-xs bg-yellow-100 text-yellow-700 px-1 rounded">WARNING</span>}
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
            ${error || (enforcementLevel === 'enforce' && !selectedAccount) ? 'border-red-500' : 'border-gray-300'}
            ${selectedAccount ? 'text-gray-900' : 'text-gray-500'}
          `}
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center flex-1 min-w-0">
              <span className="truncate">
                {selectedAccount 
                  ? `${selectedAccount.account_code} - ${selectedAccount.account_name}${isLegacyAccount ? ' [Legacy]' : ''}`
                  : placeholder
                }
              </span>
              {getWarningIcon()}
            </div>
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
                filteredAccounts.map((account) => {
                  const isLegacy = account.account_code?.startsWith('LEG_') || account.account_name?.includes('[Legacy]') || account.display_name?.includes('[Legacy]');
                  return (
                    <button
                      key={account.id}
                      type="button"
                      onClick={() => handleSelect(account)}
                      className={`
                        w-full px-3 py-2 text-left hover:bg-gray-50 focus:bg-gray-50 flex items-center justify-between
                        ${selectedAccount?.id === account.id ? 'bg-blue-50 text-blue-900' : 'text-gray-900'}
                        ${!account.is_active ? 'opacity-50' : ''}
                        ${isLegacy ? 'bg-yellow-50' : ''}
                      `}
                    >
                      <div className="flex flex-col min-w-0 flex-1">
                        <span className="font-medium truncate">
                          {account.account_code} - {account.account_name}
                        </span>
                        <span className="text-xs text-gray-500 capitalize truncate">
                          {account.account_type}
                          {!account.is_active && ' (Inactive)'}
                          {isLegacy && ' (Legacy)'}
                        </span>
                      </div>
                      {isLegacy && <Info className="w-3 h-3 text-yellow-500 ml-2" />}
                    </button>
                  );
                })
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

      {/* Enhanced validation messages */}
      {(error || validationMessage) && (
        <div className={`mt-1 text-sm flex items-center ${
          error ? 'text-red-600' : 
          validationMessage.startsWith('Warning') ? 'text-yellow-600' : 'text-red-600'
        }`}>
          {getWarningIcon() && <span className="mr-1">{getWarningIcon()}</span>}
          {error || validationMessage}
        </div>
      )}

      {/* Enforcement level indicator */}
      {shouldShowWarnings && !error && !validationMessage && (
        <div className="mt-1 text-xs text-gray-500">
          {enforcementLevel === 'enforce' && 'Chart account selection is enforced'}
          {enforcementLevel === 'warn' && 'Chart account selection is recommended'}
          {enforcementLevel === 'observe' && 'Chart account selection is being monitored'}
        </div>
      )}
    </div>
  );
};

export default CoASelector;