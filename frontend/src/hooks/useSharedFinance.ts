// frontend/src/hooks/useSharedFinance.ts
import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';

export interface FinancialTransaction {
  id: string;
  type: 'Receipt' | 'Payment' | 'Journal' | 'Transfer';
  amount: number;
  formatted_amount: string;
  account: string;
  account_id?: number;
  status: 'Cleared' | 'Pending' | 'Failed' | 'Cancelled';
  date: string;
  reference?: string;
  description?: string;
  voucher_number?: string;
  created_by?: string;
  updated_at?: string;
}

export interface FinancialSummary {
  total_income: number;
  total_expenses: number;
  net_balance: number;
  monthly_trend: number;
  trend_direction: 'up' | 'down' | 'neutral';
  currency: string;
}

export interface AccountBalance {
  account_name: string;
  account_type: string;
  balance: number;
  formatted_balance: string;
  last_transaction_date?: string;
}

export interface FinancialKPI {
  name: string;
  value: number | string;
  formatted_value: string;
  trend?: {
    value: number;
    direction: 'up' | 'down' | 'neutral';
    period: string;
  };
  icon?: string;
  color?: 'primary' | 'success' | 'warning' | 'error' | 'info';
}

export interface FinanceState {
  transactions: FinancialTransaction[];
  summary: FinancialSummary | null;
  accountBalances: AccountBalance[];
  kpis: FinancialKPI[];
  loading: boolean;
  error: string | null;
  refreshing: boolean;
  pagination: {
    page: number;
    totalPages: number;
    totalRecords: number;
    pageSize: number;
  };
}

/**
 * Shared finance hook for both desktop and mobile interfaces
 * Provides unified business logic for financial data management
 */
export const useSharedFinance = () => {
  const { user } = useAuth();
  
  const [state, setState] = useState<FinanceState>({
    transactions: [],
    summary: null,
    accountBalances: [],
    kpis: [],
    loading: true,
    error: null,
    refreshing: false,
    pagination: {
      page: 1,
      totalPages: 1,
      totalRecords: 0,
      pageSize: 10,
    },
  });

  const [filters, setFilters] = useState({
    search: '',
    account: '',
    type: '',
    status: '',
    dateFrom: '',
    dateTo: '',
  });

  // TODO: Replace with real financial API endpoints
  const fetchFinancialSummary = useCallback(async () => {
    try {
      // TODO: Implement real API call to /api/finance/summary
      // const response = await api.get('/finance/summary');
      
      // Mock data for now - replace with real API
      const mockSummary: FinancialSummary = {
        total_income: 284750,
        total_expenses: 145230,
        net_balance: 139520,
        monthly_trend: 12.5,
        trend_direction: 'up',
        currency: 'INR',
      };

      setState(prev => ({ 
        ...prev, 
        summary: mockSummary,
        error: null 
      }));
    } catch (err) {
      setState(prev => ({ 
        ...prev, 
        error: err instanceof Error ? err.message : "Failed to fetch financial summary" 
      }));
    }
  }, []);

  const fetchTransactions = useCallback(async (page: number = 1, pageSize: number = 10) => {
    try {
      // TODO: Implement real API call to /api/finance/transactions
      // const response = await api.get('/finance/transactions', {
      //   params: { page, page_size: pageSize, ...filters }
      // });

      // Mock data for now - replace with real API
      const mockTransactions: FinancialTransaction[] = [
        {
          id: 'TXN-2024-001',
          type: 'Receipt',
          amount: 25400,
          formatted_amount: '₹25,400',
          account: 'Sales Account',
          status: 'Cleared',
          date: '2024-01-15',
          voucher_number: 'RV-001',
          reference: 'Payment from ABC Corp'
        },
        {
          id: 'TXN-2024-002',
          type: 'Payment',
          amount: 15000,
          formatted_amount: '₹15,000',
          account: 'Purchase Account',
          status: 'Pending',
          date: '2024-01-14',
          voucher_number: 'PV-002',
          reference: 'Payment to XYZ Supplier'
        },
        {
          id: 'TXN-2024-003',
          type: 'Journal',
          amount: 8750,
          formatted_amount: '₹8,750',
          account: 'Adjustment Account',
          status: 'Cleared',
          date: '2024-01-12',
          voucher_number: 'JV-003',
          reference: 'Month-end adjustment'
        },
      ];

      setState(prev => ({ 
        ...prev, 
        transactions: mockTransactions,
        pagination: {
          ...prev.pagination,
          page,
          pageSize,
          totalRecords: mockTransactions.length,
          totalPages: Math.ceil(mockTransactions.length / pageSize),
        },
        error: null 
      }));
    } catch (err) {
      setState(prev => ({ 
        ...prev, 
        error: err instanceof Error ? err.message : "Failed to fetch transactions" 
      }));
    }
  }, [filters]);

  const fetchAccountBalances = useCallback(async () => {
    try {
      // TODO: Implement real API call to /api/finance/accounts
      // const response = await api.get('/finance/accounts/balances');
      
      // Mock data for now - replace with real API
      const mockBalances: AccountBalance[] = [
        {
          account_name: 'Cash Account',
          account_type: 'Asset',
          balance: 45000,
          formatted_balance: '₹45,000',
          last_transaction_date: '2024-01-15'
        },
        {
          account_name: 'Bank Account',
          account_type: 'Asset',
          balance: 125000,
          formatted_balance: '₹1,25,000',
          last_transaction_date: '2024-01-14'
        },
        {
          account_name: 'Accounts Receivable',
          account_type: 'Asset',
          balance: 85000,
          formatted_balance: '₹85,000',
          last_transaction_date: '2024-01-13'
        },
      ];

      setState(prev => ({ 
        ...prev, 
        accountBalances: mockBalances,
        error: null 
      }));
    } catch (err) {
      setState(prev => ({ 
        ...prev, 
        error: err instanceof Error ? err.message : "Failed to fetch account balances" 
      }));
    }
  }, []);

  const calculateKPIs = useCallback(() => {
    if (!state.summary) return [];

    const kpis: FinancialKPI[] = [
      {
        name: 'Total Income',
        value: state.summary.total_income,
        formatted_value: `₹${state.summary.total_income.toLocaleString()}`,
        trend: {
          value: 8.5,
          direction: 'up',
          period: 'vs last month',
        },
        color: 'success',
      },
      {
        name: 'Total Expenses',
        value: state.summary.total_expenses,
        formatted_value: `₹${state.summary.total_expenses.toLocaleString()}`,
        trend: {
          value: 3.2,
          direction: 'up',
          period: 'vs last month',
        },
        color: 'error',
      },
      {
        name: 'Net Profit',
        value: state.summary.net_balance,
        formatted_value: `₹${state.summary.net_balance.toLocaleString()}`,
        trend: {
          value: state.summary.monthly_trend,
          direction: state.summary.trend_direction,
          period: 'vs last month',
        },
        color: 'primary',
      },
      {
        name: 'Profit Margin',
        value: state.summary.total_income > 0 
          ? ((state.summary.net_balance / state.summary.total_income) * 100).toFixed(1)
          : '0',
        formatted_value: state.summary.total_income > 0 
          ? `${((state.summary.net_balance / state.summary.total_income) * 100).toFixed(1)}%`
          : '0%',
        color: 'info',
      },
    ];

    return kpis;
  }, [state.summary]);

  const refresh = useCallback(async () => {
    setState(prev => ({ ...prev, refreshing: true, error: null }));
    
    try {
      await Promise.all([
        fetchFinancialSummary(),
        fetchTransactions(state.pagination.page, state.pagination.pageSize),
        fetchAccountBalances(),
      ]);
    } finally {
      setState(prev => ({ 
        ...prev, 
        refreshing: false, 
        loading: false 
      }));
    }
  }, [fetchFinancialSummary, fetchTransactions, fetchAccountBalances, state.pagination.page, state.pagination.pageSize]);

  const updateFilters = useCallback((newFilters: Partial<typeof filters>) => {
    setFilters(prev => ({ ...prev, ...newFilters }));
  }, []);

  const searchTransactions = useCallback((query: string) => {
    updateFilters({ search: query });
  }, [updateFilters]);

  const changePage = useCallback((page: number) => {
    fetchTransactions(page, state.pagination.pageSize);
  }, [fetchTransactions, state.pagination.pageSize]);

  // Initial data load
  useEffect(() => {
    if (user) {
      refresh();
    } else {
      setState(prev => ({ ...prev, loading: false }));
    }
  }, [user, refresh]);

  // Recalculate KPIs when summary changes
  useEffect(() => {
    const kpis = calculateKPIs();
    setState(prev => ({ ...prev, kpis }));
  }, [calculateKPIs]);

  // Refetch when filters change
  useEffect(() => {
    if (!state.loading) {
      fetchTransactions(1, state.pagination.pageSize);
    }
  }, [filters, fetchTransactions, state.loading, state.pagination.pageSize]);

  // Filter transactions based on current search
  const getFilteredTransactions = useCallback(() => {
    if (!filters.search) return state.transactions;
    
    return state.transactions.filter(transaction =>
      transaction.id.toLowerCase().includes(filters.search.toLowerCase()) ||
      transaction.account.toLowerCase().includes(filters.search.toLowerCase()) ||
      transaction.type.toLowerCase().includes(filters.search.toLowerCase()) ||
      (transaction.reference && transaction.reference.toLowerCase().includes(filters.search.toLowerCase()))
    );
  }, [state.transactions, filters.search]);

  return {
    ...state,
    filters,
    filteredTransactions: getFilteredTransactions(),
    refresh,
    updateFilters,
    searchTransactions,
    changePage,
    kpis: calculateKPIs(),
  };
};

export default useSharedFinance;